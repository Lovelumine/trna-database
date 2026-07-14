export const CHAT_GREETING =
  'Hi — I’m YingYing, the ENSURE research assistant. Ask me about records, publications, or suppressor tRNA.';

export function isChatGreeting(text: unknown): boolean {
  const normalized = String(text || '').trim().toLowerCase();
  return normalized.startsWith('hello, i am your virtual assistant') ||
    normalized.includes('how can i assist you today') ||
    normalized.startsWith('hi — i’m yingying, the ensure research assistant') ||
    normalized.startsWith("hi — i'm yingying, the ensure research assistant");
}
