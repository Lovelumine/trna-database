const INTERNAL_TOOL_PATTERNS = [
  // XML-like tool protocols used by several model providers. Keep this broad
  // enough to catch both complete calls and the common function_call variant.
  /<\s*\/?\s*(?:function(?:_call)?|parameter|tool_call|tool)(?:\s*=|\s*>|\s+)|<\|\s*(?:tool_call|function_call)[^>]*\|>/i,
  /(?:query_db|database_query)\s*\(/i,
  // JSON/OpenAI-style tool calls. A JSON object containing these keys is
  // protocol data, not user-facing prose.
  /(?:^|[{,]\s*)["']?(?:tool_calls?|function_call|arguments)["']?\s*:/im,
  /(?:^|[{,]\s*)["']?function["']?\s*:\s*\{/im,
  /["']?name["']?\s*:\s*["'](?:query_db|database_query|execute_sql|run_sql)["']/i,
  // SQLAlchemy includes raw statements in this form when an exception leaks.
  /\[\s*SQL\s*:\s*[\s\S]{0,8000}/i,
  // Direct SQL statements emitted outside a tool wrapper. Requiring SELECT to
  // contain FROM avoids matching ordinary UI phrases such as “Select column”.
  /(?:^|[\n\r;])\s*(?:SELECT\s+(?=[^;]{0,2500}\bFROM\b)[^;]{1,2500}\bFROM\s+[`"'\w.]|INSERT\s+INTO\s+[`"'\w.]|UPDATE\s+[`"'\w.]+\s+SET\s+|DELETE\s+FROM\s+[`"'\w.])/im,
  /(?:^|[\n\r;])\s*WITH\s+(?:RECURSIVE\s+)?[A-Za-z_]\w*\s+AS\s*\([\s\S]{0,2500}?\)\s*(?:SELECT|INSERT|UPDATE|DELETE)\b/im,
  /(?:^|[\n\r;])\s*PRAGMA\s+(?:[A-Za-z_]\w*\.)?[A-Za-z_]\w*/im,
  /(?:^|[\n\r;])\s*EXPLAIN\s+(?:QUERY\s+PLAN\s+)?(?:SELECT|INSERT|UPDATE|DELETE|WITH)\b/im
];

export const containsInternalToolMarkup = (value: unknown) => {
  const text = String(value || '');
  return INTERNAL_TOOL_PATTERNS.some(pattern => pattern.test(text));
};

export const blockedAssistantMessage = (value: unknown) => {
  const text = String(value || '');
  if (!containsInternalToolMarkup(text)) return text;
  if (/[\u4e00-\u9fff]/.test(text)) {
    return '这条历史回答包含不应展示的内部调用信息，已被安全隐藏。请重新发送问题。';
  }
  return 'This saved response contained an internal tool instruction and was safely hidden. Please retry the question.';
};

/**
 * Sanitize a single assistant-controlled field before it is rendered or
 * retained. Metadata should normally pass an empty fallback so a contaminated
 * trace is omitted instead of replacing useful answer text.
 */
export const sanitizeAssistantText = (value: unknown, fallback = '') => {
  const text = String(value || '');
  return containsInternalToolMarkup(text) ? fallback : text;
};

export const sanitizeAssistantResponse = (main: unknown, evidence: unknown) => {
  const mainText = String(main || '');
  const evidenceText = String(evidence || '');
  if (containsInternalToolMarkup(mainText)) {
    return { main: blockedAssistantMessage(mainText), evidence: '' };
  }
  if (containsInternalToolMarkup(evidenceText)) {
    return { main: mainText, evidence: '' };
  }
  // This also catches a protocol marker split exactly across the two fields.
  if (containsInternalToolMarkup(`${mainText}\n${evidenceText}`)) {
    return { main: blockedAssistantMessage(`${mainText}\n${evidenceText}`), evidence: '' };
  }
  return { main: mainText, evidence: evidenceText };
};

/** Drop contaminated structured evidence records rather than exposing a raw
 * tool payload through a title, snippet, link, or other nested source field. */
export const sanitizeAssistantSources = (value: unknown): Record<string, unknown>[] => {
  if (!Array.isArray(value)) return [];
  return value.filter((source): source is Record<string, unknown> => {
    if (!source || typeof source !== 'object' || Array.isArray(source)) return false;
    try {
      return !containsInternalToolMarkup(JSON.stringify(source));
    } catch {
      return false;
    }
  });
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
    if ('sources' in next) next.sources = sanitizeAssistantSources(next.sources);
    if ('evidenceSources' in next) next.evidenceSources = sanitizeAssistantSources(next.evidenceSources);
    return next;
  });
};
