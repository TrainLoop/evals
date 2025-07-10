import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', '330'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', 'e32'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', 'a51'),
            routes: [
              {
                path: '/category/cli-reference',
                component: ComponentCreator('/category/cli-reference', '0d4'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/category/development',
                component: ComponentCreator('/category/development', 'd36'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/category/explanation',
                component: ComponentCreator('/category/explanation', 'd11'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/category/getting-started',
                component: ComponentCreator('/category/getting-started', '794'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/category/guides',
                component: ComponentCreator('/category/guides', '0a5'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/category/reference',
                component: ComponentCreator('/category/reference', '51f'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development',
                component: ComponentCreator('/development', '1e0'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/architecture',
                component: ComponentCreator('/development/architecture', '394'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/building-from-source',
                component: ComponentCreator('/development/building-from-source', '1dc'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/code-style',
                component: ComponentCreator('/development/code-style', '8f2'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/contributing',
                component: ComponentCreator('/development/contributing', 'f8b'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/local-development',
                component: ComponentCreator('/development/local-development', '732'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/pull-request-process',
                component: ComponentCreator('/development/pull-request-process', '9d7'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/release-process',
                component: ComponentCreator('/development/release-process', '333'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/sdk-testing',
                component: ComponentCreator('/development/sdk-testing', '614'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/development/testing',
                component: ComponentCreator('/development/testing', '010'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/explanation',
                component: ComponentCreator('/explanation', '93c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/getting-started/installation',
                component: ComponentCreator('/getting-started/installation', '91c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/getting-started/quick-start',
                component: ComponentCreator('/getting-started/quick-start', 'a3a'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/guides',
                component: ComponentCreator('/guides', 'd8c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/intro',
                component: ComponentCreator('/intro', '4a2'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/reference',
                component: ComponentCreator('/reference', '67b'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/reference/benchmark-schema',
                component: ComponentCreator('/reference/benchmark-schema', 'b1c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/reference/cli/overview',
                component: ComponentCreator('/reference/cli/overview', '176'),
                exact: true,
                sidebar: "docsSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
