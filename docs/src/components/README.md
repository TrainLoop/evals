# Universal Markdown Download Component

This component allows users to download or copy the raw markdown source of any documentation page.

## Available Component

### `<DownloadMarkdownButton />`
A flexible button that can download or copy markdown, appearing automatically in breadcrumbs.

**Props:**
- `action?: 'download' | 'copy'` (default: 'download')
- `iconOnly?: boolean` (default: false) 
- `size?: 'small' | 'normal'` (default: 'small')
- `variant?: 'primary' | 'secondary' | 'outline'` (default: 'outline') 
- `filename?: string` (auto-detected from page URL)
- `githubUrl?: string` (auto-constructed from page path)

## Usage

The component is available globally in all MDX files:

```jsx
// Breadcrumb usage (automatic)
<DownloadMarkdownButton iconOnly={true} action="download" />
<DownloadMarkdownButton iconOnly={true} action="copy" />

// Manual usage
<DownloadMarkdownButton action="download" />
<DownloadMarkdownButton action="copy" />

// Custom filename
<DownloadMarkdownButton filename="custom-name.md" />
```

## Features

- **Auto-detection**: Automatically detects current page and constructs appropriate GitHub raw URL
- **Clean output**: Removes front matter and import statements from downloaded markdown
- **Universal**: Works on any docs page (`/docs/`, `/cli/`, `/ui/`) 
- **Breadcrumb integration**: Small button automatically appears in breadcrumbs of every page
- **Responsive**: Adapts styling based on size and variant props

## Implementation

- `DownloadMarkdownButton` is automatically added to breadcrumbs via theme override
- Both components available globally via `MDXComponents.tsx` theme override
- Auto-constructs GitHub raw URLs based on Docusaurus routing conventions