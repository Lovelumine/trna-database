const CHAT_STORAGE_PREFIX = 'ensure:chat:v2';
const LEGACY_CLAIMED_KEY = `${CHAT_STORAGE_PREFIX}:legacy_claimed`;
const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';

const LEGACY_FIXED_KEYS = new Set([
  'ai_chat_sessions',
  'ai_chat_active_session',
  'ai_note_ack_global'
]);
const LEGACY_DYNAMIC_KEY = /^ai_chat_(?:session|meta)_.+$/;

let activeNamespace = '';
let initialization: Promise<string> | null = null;
let memoryFallbackNamespace = '';

const createRandomId = () => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `${Date.now()}_${Math.random().toString(36).slice(2, 12)}`;
};

const normalizeNamespace = (value: unknown) => {
  const raw = String(value || '').trim();
  return raw ? encodeURIComponent(raw) : '';
};

const fallbackNamespace = () => {
  if (memoryFallbackNamespace) return memoryFallbackNamespace;
  // An offline namespace intentionally lasts only for this page. Persisting it
  // would let a later anonymous identity inherit records written while the
  // backend cookie service was unavailable.
  memoryFallbackNamespace = `fallback_${createRandomId()}`;
  return memoryFallbackNamespace;
};

const scopedKeyFor = (namespace: string, key: string) =>
  `${CHAT_STORAGE_PREFIX}:${namespace}:${key}`;

const migrateLegacyChatStorage = (namespace: string) => {
  try {
    if (localStorage.getItem(LEGACY_CLAIMED_KEY)) return;

    const legacyKeys: string[] = [];
    for (let index = 0; index < localStorage.length; index += 1) {
      const key = localStorage.key(index);
      if (!key) continue;
      if (LEGACY_FIXED_KEYS.has(key) || LEGACY_DYNAMIC_KEY.test(key)) {
        legacyKeys.push(key);
      }
    }

    for (const legacyKey of legacyKeys) {
      const value = localStorage.getItem(legacyKey);
      const targetKey = scopedKeyFor(namespace, legacyKey);
      if (value !== null && localStorage.getItem(targetKey) === null) {
        localStorage.setItem(targetKey, value);
      }
    }

    // Write the marker before removing the unscoped copies. If deletion is
    // interrupted, a future anonymous cookie still cannot claim them again.
    localStorage.setItem(LEGACY_CLAIMED_KEY, JSON.stringify({
      namespace,
      claimedAt: Date.now()
    }));
    for (const legacyKey of legacyKeys) {
      localStorage.removeItem(legacyKey);
    }
  } catch {
    // If copying failed before the marker, the migration remains retryable. If
    // cleanup failed after it, the marker still prevents a second identity claim.
  }
};

const fetchIdentityNamespace = async () => {
  const controller = new AbortController();
  const timeout = globalThis.setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(`${apiBaseURL.replace(/\/$/, '')}/identity`, {
      method: 'GET',
      headers: { accept: 'application/json' },
      credentials: 'same-origin',
      cache: 'no-store',
      signal: controller.signal
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    return normalizeNamespace(
      payload?.data?.storage_namespace ?? payload?.storage_namespace
    );
  } finally {
    globalThis.clearTimeout(timeout);
  }
};

const requestIdentityNamespace = async () => {
  const locks = typeof navigator !== 'undefined' ? (navigator as any).locks : null;
  if (locks?.request) {
    // This lock is shared by same-origin tabs. It prevents two first-load
    // requests from receiving different cookies while the browser keeps only
    // the cookie written last.
    return locks.request('ensure-chat-identity-v2', { mode: 'exclusive' }, fetchIdentityNamespace);
  }

  // Older browsers do not expose Web Locks. A confirming request makes the
  // returned namespace match the cookie that is present after the first call.
  await fetchIdentityNamespace();
  return fetchIdentityNamespace();
};

export const initializeChatIdentity = async () => {
  if (activeNamespace) return activeNamespace;
  if (initialization) return initialization;

  initialization = (async () => {
    let namespace = '';
    try {
      namespace = await requestIdentityNamespace();
    } catch {
      namespace = '';
    }

    if (namespace) {
      activeNamespace = namespace;
      migrateLegacyChatStorage(activeNamespace);
    } else {
      activeNamespace = fallbackNamespace();
      // Do not import global legacy records without a server-issued identity.
      // Offline records remain isolated in this page-only fallback namespace.
    }
    return activeNamespace;
  })();

  try {
    return await initialization;
  } finally {
    initialization = null;
  }
};

export const scopedChatStorageKey = (key: string) => {
  if (!activeNamespace) {
    throw new Error('Chat identity must be initialized before accessing chat storage.');
  }
  return scopedKeyFor(activeNamespace, key);
};

export const createChatSessionId = () => `chat_${createRandomId()}`;
