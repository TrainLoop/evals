// index.ts - Pulumi program (Fargate + EFS, mount path env)
// ------------------------------------------------------------
//   1. Route 53 A‑alias for <subdomain>.<domain> → ALB.
//   2. Private S3 bucket (SDK access only).
//   3. EFS file system shared by tasks.
//   4. Next.js on **Fargate** with EFS mounted and `TRAINLOOP_DATA_FOLDER` env‑var.
//   5. ALB with HTTPS (ACM cert) + HTTP→HTTPS redirect.
//   6. Target‑tracking auto‑scaling.
// ------------------------------------------------------------

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

//---------------------------------------------------------------------
// Config & helpers
//---------------------------------------------------------------------
const cfg = new pulumi.Config();
const prefix = cfg.get("resource-prefix") ?? "trainloop-evals";
const hostedZoneDomain = cfg.require("hostedZoneDomain");
const subdomain = cfg.require("subdomain");
const appImage = cfg.require("appImage");
const appVersion = cfg.get("appVersion") ?? "latest";
const trainloopDataFolder = cfg.get("efsMountPath") ?? "/mnt/efs";

const name = (id: string) => `${prefix}-${id}`;

const container_name = name("ui");

//---------------------------------------------------------------------
// 1. S3 bucket
//---------------------------------------------------------------------
const bucket = new aws.s3.Bucket(name("bucket"), {
    forceDestroy: true,
    tags: { Project: pulumi.getProject(), Stack: pulumi.getStack() },
});

//---------------------------------------------------------------------
// 2. IAM roles & least‑priv S3 policy
//---------------------------------------------------------------------
const taskRole = new aws.iam.Role(name("task-role"), {
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ecs-tasks.amazonaws.com" }),
});
const s3Pol = bucket.arn.apply(arn => JSON.stringify({
    Version: "2012-10-17",
    Statement: [{ Effect: "Allow", Action: ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"], Resource: [arn, `${arn}/*`] }],
}));
new aws.iam.RolePolicy(name("s3-policy"), { role: taskRole.id, policy: s3Pol });

const execRole = new aws.iam.Role(name("exec-role"), {
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({ Service: "ecs-tasks.amazonaws.com" }),
});
new aws.iam.RolePolicyAttachment(name("exec-policy"), {
    role: execRole.name,
    policyArn: "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
});

//---------------------------------------------------------------------
// 3. Public ALB (creates SG/VPC context) & default VPC
//---------------------------------------------------------------------
const alb = new awsx.lb.ApplicationLoadBalancer(name("alb"), {
    defaultTargetGroup: { port: 3000, protocol: "HTTP", targetType: "ip" },
    listeners: [],
});
const vpcId = alb.loadBalancer.vpcId;

//---------------------------------------------------------------------
// 4. EFS file system
//---------------------------------------------------------------------
const efsSg = new aws.ec2.SecurityGroup(name("efs-sg"), {
    vpcId,
    ingress: [{ protocol: "tcp", fromPort: 2049, toPort: 2049, securityGroups: [alb.loadBalancer.securityGroups[0]] }],
    egress: [{ protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }],
});
const fileSystem = new aws.efs.FileSystem(name("efs"), {
    encrypted: true,
    performanceMode: "generalPurpose",
    throughputMode: "bursting",
});
// Mount targets in each ALB subnet
alb.loadBalancer.subnets.apply(subs => subs.forEach((subnet, i) => {
    new aws.efs.MountTarget(name(`mt-${i}`), { fileSystemId: fileSystem.id, subnetId: subnet, securityGroups: [efsSg.id] });
}));

//---------------------------------------------------------------------
// 5. ECS cluster, task definition & service with EFS mount
//---------------------------------------------------------------------
const cluster = new aws.ecs.Cluster(name("cluster"));
const logs = new aws.cloudwatch.LogGroup(name("logs"), { retentionInDays: 7 });

const taskDef = new aws.ecs.TaskDefinition(name("task"), {
    family: name("app"),
    networkMode: "awsvpc",
    requiresCompatibilities: ["FARGATE"],
    cpu: "256", memory: "512",
    executionRoleArn: execRole.arn,
    taskRoleArn: taskRole.arn,
    volumes: [{
        name: "efs-vol",
        efsVolumeConfiguration: { fileSystemId: fileSystem.id, transitEncryption: "ENABLED" },
    }],
    containerDefinitions: pulumi.output([{
        name: container_name,
        image: `${appImage}:${appVersion}`,
        essential: true,
        portMappings: [{ containerPort: 3000 }],
        mountPoints: [{ sourceVolume: "efs-vol", containerPath: trainloopDataFolder }],
        environment: [
            { name: "NODE_ENV", value: "production" },
            { name: "TRAINLOOP_DATA_FOLDER", value: trainloopDataFolder },
        ],
        logConfiguration: {
            logDriver: "awslogs", options: {
                "awslogs-group": logs.name,
                "awslogs-region": aws.config.region,
                "awslogs-stream-prefix": "ecs",
            }
        },
    }]).apply(JSON.stringify),
});

const service = new aws.ecs.Service(name("service"), {
    cluster: cluster.id,
    launchType: "FARGATE",
    desiredCount: 1,
    taskDefinition: taskDef.arn,
    networkConfiguration: {
        assignPublicIp: true,
        subnets: alb.loadBalancer.subnets,
        securityGroups: [alb.loadBalancer.securityGroups[0]],
    },
    loadBalancers: [{ targetGroupArn: alb.defaultTargetGroup.arn, containerName: container_name, containerPort: 3000 }],
}, { dependsOn: logs });

//---------------------------------------------------------------------
// 6. Auto‑scaling (CPU 50 %)
//---------------------------------------------------------------------
const scalableTarget = new aws.appautoscaling.Target(name("asg-target"), {
    maxCapacity: 5, minCapacity: 1,
    resourceId: pulumi.interpolate`service/${cluster.name}/${service.name}`,
    scalableDimension: "ecs:service:DesiredCount",
    serviceNamespace: "ecs",
});
new aws.appautoscaling.Policy(name("asg-policy"), {
    policyType: "TargetTrackingScaling",
    resourceId: scalableTarget.resourceId,
    scalableDimension: scalableTarget.scalableDimension,
    serviceNamespace: scalableTarget.serviceNamespace,
    targetTrackingScalingPolicyConfiguration: {
        predefinedMetricSpecification: { predefinedMetricType: "ECSServiceAverageCPUUtilization" },
        targetValue: 50,
        scaleInCooldown: 60,
        scaleOutCooldown: 60,
    },
});

//---------------------------------------------------------------------
// 7. HTTPS listener + HTTP→HTTPS redirect
//---------------------------------------------------------------------
const zone = aws.route53.getZone({ name: hostedZoneDomain });
const cert = new aws.acm.Certificate(name("cert"), { domainName: `${subdomain}.${hostedZoneDomain}`, validationMethod: "DNS" });
const validationRecord = new aws.route53.Record(name("cert-validate"), {
    zoneId: zone.then(z => z.zoneId),
    name: cert.domainValidationOptions[0].resourceRecordName,
    type: cert.domainValidationOptions[0].resourceRecordType,
    records: [cert.domainValidationOptions[0].resourceRecordValue], ttl: 60,
});
const certValidation = new aws.acm.CertificateValidation(name("cert-val"), {
    certificateArn: cert.arn,
    validationRecordFqdns: [validationRecord.fqdn],
});
new aws.lb.Listener(name("https-listener"), {
    loadBalancerArn: alb.loadBalancer.arn,
    port: 443, protocol: "HTTPS", sslPolicy: "ELBSecurityPolicy-2016-08",
    certificateArn: certValidation.certificateArn,
    defaultActions: [{ type: "forward", targetGroupArn: alb.defaultTargetGroup.arn }],
}, { dependsOn: certValidation });

//---------------------------------------------------------------------
// 8. DNS A‑alias
//---------------------------------------------------------------------
const dnsRecord = new aws.route53.Record(name("dns"), {
    zoneId: zone.then(z => z.zoneId),
    name: `${subdomain}.${hostedZoneDomain}`,
    type: "A",
    aliases: [{ name: alb.loadBalancer.dnsName, zoneId: alb.loadBalancer.zoneId, evaluateTargetHealth: true }],
});

//---------------------------------------------------------------------
// 9. Outputs
//---------------------------------------------------------------------
export const bucketName = bucket.bucket;
export const efsId = fileSystem.id;
export const mountPathOut = trainloopDataFolder;
export const albHostname = alb.loadBalancer.dnsName;
export const serviceUrl = pulumi.interpolate`https://${dnsRecord.name}`;
