import { initializeChatIdentity } from '@/utils/chatIdentity';

export async function fetchOpenAIResponse(prompt: string) {
  // Establish the anonymous visitor cookie before requesting a visitor-bound
  // chat id. This helper is also called outside VideoSummary, so the guard
  // belongs here rather than only in the component.
  await initializeChatIdentity();

  const openResponse = await fetch('/chat/api/open', {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin',
  });
  if (!openResponse.ok) throw new Error(`Unable to open AI session (${openResponse.status})`);

  const openPayload = await openResponse.json();
  const chatId = String(openPayload?.data || '');
  if (!chatId) throw new Error('AI session ID is missing');

  const response = await fetch(`/chat/api/chat_message/${encodeURIComponent(chatId)}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: prompt,
      stream: false,
      request_deep_review: false,
    }),
  });
  if (!response.ok) throw new Error(`AI analysis failed (${response.status})`);

  const eventStream = await response.text();
  let content = '';
  for (const line of eventStream.split(/\r?\n/)) {
    if (!line.startsWith('data:')) continue;
    const raw = line.slice(5).trim();
    if (!raw || raw === '[DONE]') continue;
    try {
      const event = JSON.parse(raw);
      if (event?.type === 'content' && typeof event.content === 'string') {
        content += event.content;
      }
    } catch {
      // Ignore non-JSON SSE status lines; content events are parsed above.
    }
  }
  if (!content.trim()) throw new Error('AI analysis returned no content');
  return content.trim();
}
