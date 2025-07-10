import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  icon: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Simplicity First',
    icon: '🚀',
    description: (
      <>
        One environment variable, one function call, one folder of JSON files.
        Get started with LLM evaluation in minutes, not hours.
      </>
    ),
  },
  {
    title: 'Vendor Independent',
    icon: '🔧',
    description: (
      <>
        Everything stored as newline-delimited JSON with no databases required.
        Works with any LLM provider and integrates with your existing infrastructure.
      </>
    ),
  },
  {
    title: 'Type-Safe & Extensible',
    icon: '⚡',
    description: (
      <>
        In-code tests with full TypeScript support. Composable system with
        helper generators that mimic <code>shadcn</code> patterns.
      </>
    ),
  },
];

function Feature({title, icon, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <span className={styles.featureIcon} role="img" aria-label={title}>
          {icon}
        </span>
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
