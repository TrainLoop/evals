# GitHub Pages Deployment Documentation

This document explains the GitHub Pages deployment setup for the TrainLoop Evals documentation site.

## Overview

The documentation site is built using Docusaurus and automatically deployed to GitHub Pages using GitHub Actions. The site is served from the custom domain `docs.trainloop.ai`.

## Deployment Architecture

### Components

1. **GitHub Actions Workflow** (`.github/workflows/deploy-docs.yml`)
   - Triggers on pushes to the `main` branch
   - Builds the Docusaurus site
   - Deploys to GitHub Pages

2. **Docusaurus Configuration** (`docusaurus.config.ts`)
   - Configured for GitHub Pages deployment
   - Set up with custom domain `docs.trainloop.ai`
   - Optimized for SEO and performance

3. **Custom Domain Configuration** (`static/CNAME`)
   - Configures GitHub Pages to serve from `docs.trainloop.ai`
   - Automatically copied to the build output

## Deployment Process

### Automatic Deployment

The deployment process is fully automated:

1. **Trigger**: Push to `main` branch
2. **Build**: GitHub Actions runs `npm run build`
3. **Deploy**: Built site is deployed to `gh-pages` branch
4. **Serve**: GitHub Pages serves the content from `gh-pages` branch

### Manual Deployment

If needed, you can also deploy manually:

```bash
# Build and deploy to GitHub Pages
npm run deploy

# Or build for production locally
npm run build:production

# Test the build locally
npm run test:build
```

## Configuration Details

### GitHub Actions Workflow

The workflow (`.github/workflows/deploy-docs.yml`) includes:

- **Node.js 18 setup** with npm caching
- **Dependency installation** using `npm ci`
- **Build optimization** with proper artifact handling
- **Deployment configuration** with proper permissions
- **Concurrency control** to prevent deployment conflicts

### Docusaurus Configuration

Key deployment settings in `docusaurus.config.ts`:

```typescript
{
  url: 'https://docs.trainloop.ai',
  baseUrl: '/',
  organizationName: 'TrainLoop',
  projectName: 'trainloop-evals',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,
}
```

### Custom Domain Setup

The custom domain `docs.trainloop.ai` is configured through:

1. **CNAME file** (`static/CNAME`) containing the domain
2. **DNS configuration** (managed separately) pointing to GitHub Pages
3. **SSL certificate** automatically provided by GitHub Pages

## Repository Setup Requirements

### GitHub Pages Configuration

In the repository settings:

1. **Pages Source**: Deploy from a branch
2. **Branch**: `gh-pages` (automatically created by the workflow)
3. **Custom Domain**: `docs.trainloop.ai` (configured via CNAME file)

### Required Permissions

The GitHub Actions workflow requires:

- **Contents**: read (to checkout code)
- **Pages**: write (to deploy to GitHub Pages)
- **ID Token**: write (for GitHub Pages deployment)

## Build Process

### Build Scripts

Available npm scripts:

- `npm run build` - Standard build
- `npm run build:production` - Production build with optimizations
- `npm run test:build` - Build and serve locally for testing
- `npm run deploy:gh-pages` - Deploy to GitHub Pages manually

### Build Output

The build process:

1. **Compiles** TypeScript and processes MDX files
2. **Optimizes** images and assets
3. **Generates** static HTML for all pages
4. **Creates** search index and sitemap
5. **Copies** static assets including CNAME file

## Performance Optimizations

### Caching Strategy

- **npm dependencies** cached in GitHub Actions
- **Build artifacts** efficiently uploaded
- **Static assets** served with proper cache headers

### Build Optimizations

- **Code splitting** for JavaScript bundles
- **Image optimization** for faster loading
- **CSS optimization** and minification
- **HTML minification** for smaller file sizes

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check for TypeScript errors: `npm run typecheck`
   - Verify dependencies: `npm ci`
   - Test build locally: `npm run build`

2. **Deployment Failures**
   - Check GitHub Actions logs
   - Verify repository permissions
   - Ensure `gh-pages` branch exists and is not protected

3. **Custom Domain Issues**
   - Verify DNS configuration
   - Check CNAME file content
   - Ensure SSL certificate is active

### Debug Commands

```bash
# Check build locally
npm run build && npm run serve

# Verify TypeScript
npm run typecheck

# Check for broken links
npm run build 2>&1 | grep -i "broken\|error"
```

## Monitoring

### Build Status

Monitor deployment status through:

- **GitHub Actions tab** in the repository
- **GitHub Pages settings** showing last deployment
- **Site availability** at `https://docs.trainloop.ai`

### Performance Monitoring

The site includes:

- **Google Analytics** integration (when configured)
- **Lighthouse scoring** through GitHub Actions
- **SEO optimization** with proper meta tags

## Security Considerations

### Content Security

- **No sensitive data** in the repository
- **Environment variables** for API keys (when needed)
- **HTTPS enforcement** through GitHub Pages

### Access Control

- **Branch protection** on `main` branch (recommended)
- **Required reviews** for documentation changes
- **Automated testing** before deployment

## Maintenance

### Regular Tasks

1. **Update dependencies** monthly
2. **Monitor build performance** and optimize as needed
3. **Review and update** documentation content
4. **Check for broken links** and fix them

### Dependency Updates

```bash
# Update all dependencies
npm update

# Check for outdated packages
npm outdated

# Update Docusaurus specifically
npm install @docusaurus/core@latest @docusaurus/preset-classic@latest
```

## Support

For issues with the deployment setup:

1. Check this documentation
2. Review GitHub Actions logs
3. Consult Docusaurus documentation
4. Create an issue in the repository

## Related Documentation

- [Docusaurus Deployment Guide](https://docusaurus.io/docs/deployment)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)