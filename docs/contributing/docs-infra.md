# Documentation Infrastructure

The documentation site lives in the `docs/` directory and is built with
Docusaurus. Important pieces are:

- `sidebars.ts` &ndash; defines the sidebar. It currently autogenerates all pages
  from the `docs/docs` folder.
- `src/pages/index.tsx` and `src/components/HomepageFeatures/` &ndash; implement
  the landing page.
- `src/css/custom.css` &ndash; contains global styles. Customize admonitions here
  if you need to tweak callout appearance.
- Shared reference pages such as `development/local-development.md` and
  `reference/cli/overview.md` document configuration and environment variables.

Build the docs locally with:

```bash
npm run docs:dev   # hot reload
npm run docs:build # production build
```
