// src/utils/useMarkdown.ts
import { marked } from 'marked';

export function useMarkdown() {
  const renderMarkdown = async (markdownText: string): Promise<string> => {
    return marked(markdownText);
  };

  return { renderMarkdown };
}
