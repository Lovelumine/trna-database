// highlightModification.js

export const highlightModification = (sequence) => {
    if (!sequence) return sequence;
  
    let highlightedSequence = '';
    let lastIndex = 0;
  
    // 更新正则表达式，匹配 / 后的任意单个字符，包括符号
    const regex = /(\/[^\s])/g;
    let match;
  
    while ((match = regex.exec(sequence)) !== null) {
      const [fullMatch] = match;
      const index = match.index;
  
      // 添加非特殊修饰部分
      if (index > lastIndex) {
        highlightedSequence += sequence.slice(lastIndex, index);
      }
  
      // 添加特殊修饰部分
      if (fullMatch.startsWith('/')) { // 替换
        const base = fullMatch[1];
        highlightedSequence += `<span style="color: blue;">${base}</span>`;
      }
  
      lastIndex = index + fullMatch.length;
    }
  
    // 添加剩余部分
    if (lastIndex < sequence.length) {
      highlightedSequence += sequence.slice(lastIndex);
    }
  
    return highlightedSequence;
  };
  