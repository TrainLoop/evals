import React from 'react';
import DocBreadcrumbs from '@theme-original/DocBreadcrumbs';
import type DocBreadcrumbsType from '@theme/DocBreadcrumbs';
import type {WrapperProps} from '@docusaurus/types';
import DownloadMarkdownButton from '@site/src/components/DownloadMarkdownButton';

type Props = WrapperProps<typeof DocBreadcrumbsType>;

export default function DocBreadcrumbsWrapper(props: Props): JSX.Element {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
      <DocBreadcrumbs {...props} />
      <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
        <DownloadMarkdownButton iconOnly={true} action="download" />
        <DownloadMarkdownButton iconOnly={true} action="copy" />
      </div>
    </div>
  );
}