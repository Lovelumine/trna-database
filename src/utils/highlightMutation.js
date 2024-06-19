// highlightMutation.js

export const highlightMutation = (sequence) => {
    if (!sequence) return sequence;
  
    let highlightedSequence = '';
    let lastIndex = 0;
  
    const regex = /(\\\\\\[A-Z])|(\\\\[A-Z])|(\\[A-Z])/g;
    let match;
  
    while ((match = regex.exec(sequence)) !== null) {
      const [fullMatch] = match;
      const index = match.index;
  
      // 添加非突变部分
      if (index > lastIndex) {
        highlightedSequence += sequence.slice(lastIndex, index);
      }
  
      // 添加突变部分
      if (fullMatch.startsWith("\\\\\\")) { // 删除
        const base = fullMatch[3];
        highlightedSequence += `<span style="text-decoration: line-through; color: black;" title="Deleted ${base}">${base}</span>`;
      } else if (fullMatch.startsWith("\\\\")) { // 增添
        const base = fullMatch[2];
        highlightedSequence += `<span style="color: green;" title="Added ${base}">${base}</span>`;
      } else if (fullMatch.startsWith("\\")) { // 替换
        const base = fullMatch[1];
        highlightedSequence += `<span style="color: red;" title="Replaced with ${base}">${base}</span>`;
      }
  
      lastIndex = index + fullMatch.length;
    }
  
    // 添加剩余部分
    if (lastIndex < sequence.length) {
      highlightedSequence += sequence.slice(lastIndex);
    }
  
    return highlightedSequence;
  };
  