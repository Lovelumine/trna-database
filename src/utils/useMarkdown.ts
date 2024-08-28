// src/utils/useMarkdown.ts
import { marked } from 'marked';

export function useMarkdown() {
  const renderMarkdown = async (markdownText: string): Promise<string> => {
    // 检查输入是否为空或未定义
    if (!markdownText) {
      console.warn('renderMarkdown: Received empty or undefined input.');
      return ''; // 返回空字符串，避免 marked() 报错
    }
    return marked(markdownText);
  };

  return { renderMarkdown };
}
