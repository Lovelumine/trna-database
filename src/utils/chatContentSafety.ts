const INTERNAL_TOOL_MARKUP = /<\s*\/?\s*(?:function|parameter|tool_call|tool)(?:\s*=|\s*>|\s+)|<\|\s*(?:tool_call|function_call)[^>]*\|>|(?:query_db|database_query)\s*\(|(?:^|[\n;])\s*(?:SELECT\s+(?=[^\n;]{0,400}(?:COUNT\s*\(|\bAS\b|,|\*))(?=[^\n;]{1,400}\bFROM\b)[^\n;]{1,400}?\s+FROM\s+[`"'\w.]|INSERT\s+INTO\s+[`"'\w.]|UPDATE\s+[`"'\w.]+\s+SET\s+|DELETE\s+FROM\s+[`"'\w.])/i;

export const containsInternalToolMarkup = (value: unknown) =>
  INTERNAL_TOOL_MARKUP.test(String(value || ''));

export const blockedAssistantMessage = (value: unknown) => {
  const text = String(value || '');
  if (!containsInternalToolMarkup(text)) return text;
  if (/[\u4e00-\u9fff]/.test(text)) {
    return '这条历史回答包含不应展示的内部调用信息，已被安全隐藏。请重新发送问题。';
  }
  return 'This saved response contained an internal tool instruction and was safely hidden. Please retry the question.';
};

export const sanitizeAssistantResponse = (main: unknown, evidence: unknown) => {
  const mainText = String(main || '');
  const evidenceText = String(evidence || '');
  const combined = `${mainText}\n${evidenceText}`;
  if (containsInternalToolMarkup(combined)) {
    return { main: blockedAssistantMessage(combined), evidence: '' };
  }
  return { main: mainText, evidence: evidenceText };
};

export const sanitizeStoredChatMessages = (value: unknown) => {
  if (!Array.isArray(value)) return [];
  return value.map(message => {
    if (!message || typeof message !== 'object') return message;
    const sender = String((message as any).sender || (message as any).role || 'bot').toLowerCase();
    if (sender === 'user' || sender === 'human') return message;
    const next = { ...(message as Record<string, unknown>) };
    const visibleFields = [
      next.text,
      next.content,
      next.textPlain,
      next.evidence,
      next.evidencePlain,
      next.textHtml,
      next.evidenceHtml
    ]
      .filter(field => typeof field === 'string')
      .map(field => String(field));
    // Cached rendered HTML is never trusted. The Vue components regenerate it
    // from the sanitized plain-text fields.
    delete next.textHtml;
    delete next.evidenceHtml;
    if (containsInternalToolMarkup(visibleFields.join('\n'))) {
      const replacement = blockedAssistantMessage(visibleFields.join('\n'));
      next.text = replacement;
      if ('content' in next) next.content = replacement;
      delete next.textPlain;
      delete next.evidence;
      delete next.evidencePlain;
    }
    return next;
  });
};
