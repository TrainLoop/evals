import React, { useState } from 'react';
import { useLocation } from '@docusaurus/router';

interface DownloadMarkdownButtonProps {
  size?: 'small' | 'normal';
  variant?: 'primary' | 'secondary' | 'outline';
  filename?: string;
  githubUrl?: string;
  iconOnly?: boolean;
  action?: 'download' | 'copy';
}

const DownloadMarkdownButton: React.FC<DownloadMarkdownButtonProps> = ({ 
  size = 'small',
  variant = 'outline',
  filename,
  githubUrl,
  iconOnly = false,
  action = 'download'
}) => {
  const location = useLocation();
  const [isDownloading, setIsDownloading] = useState(false);
  const [isCopying, setIsCopying] = useState(false);
  
  const isLoading = action === 'download' ? isDownloading : isCopying;
  
  // Auto-detect current page info
  const getPageInfo = () => {
    const pathname = location.pathname;
    
    // Default filename based on current page
    const pageTitle = pathname === '/' 
      ? 'intro'
      : pathname.split('/').pop() || 'page';
    const defaultFilename = `${pageTitle}.md`;
    
    // Auto-construct GitHub URL based on current path
    let githubPath = '';
    
    if (pathname === '/') {
      githubPath = 'docs/docs/intro.md';
    } else if (pathname.startsWith('/cli/')) {
      githubPath = `docs/cli/${pathname.replace('/cli/', '')}.mdx`;
    } else if (pathname.startsWith('/ui/')) {
      githubPath = `docs/ui/${pathname.replace('/ui/', '')}.mdx`;  
    } else {
      // Main docs
      const cleanPath = pathname.replace(/^\//, '').replace(/\/$/, '');
      githubPath = `docs/docs/${cleanPath}.md`;
    }
    
    const defaultGithubUrl = `https://raw.githubusercontent.com/TrainLoop/evals/main/${githubPath}`;
    
    return {
      filename: filename || defaultFilename,
      githubUrl: githubUrl || defaultGithubUrl
    };
  };
  
  const { filename: finalFilename, githubUrl: finalGithubUrl } = getPageInfo();

  const fetchCleanMarkdown = async (): Promise<string> => {
    const response = await fetch(finalGithubUrl);
    if (!response.ok) {
      throw new Error('Failed to fetch markdown');
    }
    const text = await response.text();
    
    // Remove front matter and imports for cleaner output
    const withoutFrontMatter = text.replace(/^---\n[\s\S]*?\n---\n/, '');
    const withoutImports = withoutFrontMatter.replace(/^import.*;\n/gm, '');
    return withoutImports.trim();
  };

  const downloadMarkdown = async () => {
    setIsDownloading(true);
    try {
      const cleanMarkdown = await fetchCleanMarkdown();
      
      const blob = new Blob([cleanMarkdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = finalFilename;
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download markdown file. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const copyMarkdown = async () => {
    setIsCopying(true);
    try {
      const cleanMarkdown = await fetchCleanMarkdown();
      await navigator.clipboard.writeText(cleanMarkdown);
      
      // Brief success feedback without alert
      setTimeout(() => setIsCopying(false), 1000);
    } catch (error) {
      console.error('Copy failed:', error);
      alert('Failed to copy markdown to clipboard. Please try again.');
      setIsCopying(false);
    }
  };

  const handleClick = () => {
    if (action === 'download') {
      downloadMarkdown();
    } else {
      copyMarkdown();
    }
  };

  const getButtonContent = () => {
    if (isLoading) return '⏳';
    
    if (iconOnly) {
      return action === 'download' ? '📥' : '📋';
    }
    
    const icon = action === 'download' ? '📥' : '📋';
    const text = action === 'download' 
      ? (size === 'small' ? '.md' : 'Download .md')
      : (size === 'small' ? 'Copy' : 'Copy .md');
    
    return `${icon} ${text}`;
  };

  const getTooltip = () => {
    if (action === 'download') {
      return 'Download Markdown for this page';
    } else {
      return 'Copy Markdown for this page';
    }
  };

  const buttonClass = iconOnly 
    ? 'breadcrumb-markdown-button'
    : `button ${variant === 'primary' ? 'button--primary' : variant === 'secondary' ? 'button--secondary' : 'button--outline button--secondary'} ${size === 'small' ? 'button--sm' : ''}`;

  return (
    <button 
      className={buttonClass}
      onClick={handleClick}
      disabled={isLoading}
      title={getTooltip()}
      style={{ 
        fontSize: size === 'small' ? '0.8em' : undefined,
        minWidth: size === 'small' ? 'auto' : undefined 
      }}
    >
      {getButtonContent()}
    </button>
  );
};

export default DownloadMarkdownButton;