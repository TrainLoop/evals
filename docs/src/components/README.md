# Universal Markdown Download Components

These components allow users to download the raw markdown source of any documentation page.

## Available Components

### `<DownloadMarkdownButton />`
A compact button that appears automatically in the breadcrumb area of every docs page.

**Props:**
- `size?: 'small' | 'normal'` (default: 'small')
- `variant?: 'primary' | 'secondary' | 'outline'` (default: 'outline') 
- `filename?: string` (auto-detected from page URL)
- `githubUrl?: string` (auto-constructed from page path)

### `<DownloadMarkdown />`
Full-featured download component with both download and copy functionality.

**Props:**
- `filename?: string` (auto-detected from page URL)
- `githubUrl?: string` (auto-constructed from page path)

## Usage

These components are available globally in all MDX files:

```jsx
// Automatic detection (recommended)
<DownloadMarkdownButton />
<DownloadMarkdown />

// Custom filename
<DownloadMarkdownButton filename="custom-name.md" />

// Custom GitHub URL
<DownloadMarkdown githubUrl="https://raw.githubusercontent.com/TrainLoop/evals/main/docs/specific-file.md" />
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