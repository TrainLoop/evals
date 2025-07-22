import React, { useState } from 'react';
import { useLocation } from '@docusaurus/router';

interface DownloadMarkdownButtonProps {
  size?: 'small' | 'normal';
  variant?: 'primary' | 'secondary' | 'outline';
  filename?: string;
  githubUrl?: string;
}

const DownloadMarkdownButton: React.FC<DownloadMarkdownButtonProps> = ({ 
  size = 'small',
  variant = 'outline',
  filename,
  githubUrl
}) => {
  const location = useLocation();
  const [isDownloading, setIsDownloading] = useState(false);
  
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

  const downloadMarkdown = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch(finalGithubUrl);
      if (!response.ok) {
        throw new Error('Failed to fetch markdown');
      }
      const text = await response.text();
      
      // Remove front matter and imports for cleaner output
      const withoutFrontMatter = text.replace(/^---\n[\s\S]*?\n---\n/, '');
      const withoutImports = withoutFrontMatter.replace(/^import.*;\n/gm, '');
      const cleanMarkdown = withoutImports.trim();
      
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

  const buttonClass = `button ${variant === 'primary' ? 'button--primary' : variant === 'secondary' ? 'button--secondary' : 'button--outline button--secondary'} ${size === 'small' ? 'button--sm' : ''}`;

  return (
    <button 
      className={buttonClass}
      onClick={downloadMarkdown}
      disabled={isDownloading}
      title="Download this page as Markdown"
      style={{ 
        fontSize: size === 'small' ? '0.8em' : undefined,
        minWidth: size === 'small' ? 'auto' : undefined 
      }}
    >
      {isDownloading ? '⏳' : '📥'} {size === 'small' ? '.md' : 'Download .md'}
    </button>
  );
};

export default DownloadMarkdownButton;