import React, { useState } from 'react';
import { useLocation } from '@docusaurus/router';

interface DownloadMarkdownProps {
  filename?: string;
  githubUrl?: string;
}

const DownloadMarkdown: React.FC<DownloadMarkdownProps> = ({ 
  filename,
  githubUrl
}) => {
  const location = useLocation();
  
  // Auto-detect current page info
  const getPageInfo = () => {
    const pathname = location.pathname;
    
    // Default filename based on current page
    const defaultFilename = pathname === '/' 
      ? 'page.md'
      : `${pathname.split('/').pop() || 'page'}.md`;
    
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
  const [isDownloading, setIsDownloading] = useState(false);
  const [isCopying, setIsCopying] = useState(false);

  const fetchMarkdown = async (): Promise<string> => {
    try {
      const response = await fetch(finalGithubUrl);
      if (!response.ok) {
        throw new Error('Failed to fetch markdown');
      }
      const text = await response.text();
      
      // Remove front matter for cleaner output
      const withoutFrontMatter = text.replace(/^---\n[\s\S]*?\n---\n/, '');
      // Remove import statements
      const withoutImports = withoutFrontMatter.replace(/^import.*;\n/gm, '');
      
      return withoutImports.trim();
    } catch (error) {
      console.error('Error fetching markdown:', error);
      throw error;
    }
  };

  const downloadMarkdown = async () => {
    setIsDownloading(true);
    try {
      const markdown = await fetchMarkdown();
      
      const blob = new Blob([markdown], { type: 'text/markdown' });
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
      alert('Failed to download markdown file. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const copyMarkdown = async () => {
    setIsCopying(true);
    try {
      const markdown = await fetchMarkdown();
      
      await navigator.clipboard.writeText(markdown);
      
      // Show success feedback
      const originalText = 'Copy Markdown';
      setIsCopying(false);
      
      // Temporary success state
      setTimeout(() => {
        // Reset after showing success
      }, 2000);
      
    } catch (error) {
      alert('Failed to copy markdown to clipboard. Please try again.');
      setIsCopying(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', alignItems: 'center' }}>
      <button 
        className="button button--primary"
        onClick={downloadMarkdown}
        disabled={isDownloading}
        style={{ minWidth: '140px' }}
      >
        {isDownloading ? '⏳ Downloading...' : '📥 Download .md'}
      </button>
      <button 
        className="button button--secondary"
        onClick={copyMarkdown}
        disabled={isCopying}
        style={{ minWidth: '130px' }}
      >
        {isCopying ? '⏳ Copying...' : '📋 Copy Markdown'}
      </button>
      <small style={{ color: 'var(--ifm-color-content-secondary)', marginLeft: '10px' }}>
        Get the raw markdown to share with your LLM
      </small>
    </div>
  );
};

export default DownloadMarkdown;