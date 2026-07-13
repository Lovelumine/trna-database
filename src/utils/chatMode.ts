export type ChatMode = 'fast' | 'deep';

export const CHAT_MODE_STORAGE_KEY = 'ai_chat_mode';
const LEGACY_THINKING_STORAGE_KEY = 'ai_thinking_enabled';
const LEGACY_EFFORT_STORAGE_KEY = 'ai_reasoning_effort';

export const readChatMode = (): ChatMode => {
  const stored = localStorage.getItem(CHAT_MODE_STORAGE_KEY);
  if (stored === 'fast' || stored === 'deep') return stored;

  const legacyThinking = localStorage.getItem(LEGACY_THINKING_STORAGE_KEY);
  const legacyEffort = localStorage.getItem(LEGACY_EFFORT_STORAGE_KEY);
  if (legacyThinking === '1') return 'deep';
  if (legacyThinking === '0') return 'fast';
  return legacyEffort === 'max' ? 'deep' : 'fast';
};

export const persistChatMode = (mode: ChatMode) => {
  localStorage.setItem(CHAT_MODE_STORAGE_KEY, mode);
  // Legacy values are read once above, then retired so the UI has one source of truth.
  localStorage.removeItem(LEGACY_THINKING_STORAGE_KEY);
  localStorage.removeItem(LEGACY_EFFORT_STORAGE_KEY);
};

export const chatModeRequestOptions = (mode: ChatMode) => ({
  deepReview: mode === 'deep',
  thinkingEnabled: mode === 'deep'
});
