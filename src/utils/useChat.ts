import { ref, type Ref } from 'vue';

type ChatMessage = {
  id: number;
  text: string;
  sender: string;
  image?: string | null;
};

type ChatToolTrace = {
  id: number;
  tool: string;
  summary: string;
};

type ChatJudgeTrace = {
  id: number;
  verdict: string;
  summary: string;
  coverageScore?: number | null;
  missingAspects?: string[];
  nextTools?: string[];
};

type ChatDraftPreview = {
  label: string;
  content: string;
};

type ChatHistoryMessage = {
  role: 'user' | 'assistant';
  content: string;
};

type ChatSession = {
  apiKey: string;
  isChatOpen: Ref<boolean>;
  messages: Ref<ChatMessage[]>;
  newMessage: Ref<string>;
  newImage: Ref<File | null>;
  imagePreview: Ref<string>;
  isStreaming: Ref<boolean>;
  applicationId: string;
  chatId: string;
  initialized: boolean;
  initializing: Promise<void> | null;
  streamAbortController: AbortController | null;
  progressStatus: Ref<string>;
  progressDetail: Ref<string>;
  progressToolTrace: Ref<ChatToolTrace[]>;
  progressJudgeTrace: Ref<ChatJudgeTrace[]>;
  progressDraftPreview: Ref<ChatDraftPreview | null>;
};

type SendOptions = {
  skipUserPush?: boolean;
  overrideText?: string;
  model?: string;
  history?: ChatHistoryMessage[];
  deepReview?: boolean;
};

const defaultGreeting = 'Hello, I am your virtual assistant YingYing. How can I assist you today?';
const sessions = new Map<string, ChatSession>();
const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';
const mask = (s?: string) => (s ? s.replace(/.(?=.{4})/g, '*') : '');

const logAuth = (session: ChatSession, where: string, url: string, method: string) => {
  console.log(`[useChat] ${method} ${url}`);
  console.log(`[useChat] ${where} Authorization(m): ${mask(session.apiKey)}`);
  // @ts-ignore
  if (import.meta.env?.VITE_DEBUG_LOG_FULL_AUTH === '1') {
    console.warn('[useChat] Authorization(FULL,DEBUG): Bearer ' + session.apiKey);
  }
};

const authHeaders = (session: ChatSession) => ({
  Authorization: `Bearer ${session.apiKey}`,
  accept: 'application/json'
});

const composeBotMessageText = (main: string, evidence: string) => {
  const mainText = String(main || '').trim();
  const evidenceText = String(evidence || '').trim();
  return evidenceText ? `${mainText}\n\nSearch results:\n${evidenceText}`.trim() : mainText;
};

const getSession = (key: string, apiKey: string): ChatSession => {
  const existing = sessions.get(key);
  if (existing) return existing;
  const session: ChatSession = {
    apiKey,
    isChatOpen: ref(false),
    messages: ref<ChatMessage[]>([{ id: 1, text: defaultGreeting, sender: 'bot' }]),
    newMessage: ref(''),
    newImage: ref<File | null>(null),
    imagePreview: ref(''),
    isStreaming: ref(false),
    applicationId: '',
    chatId: '',
    initialized: false,
    initializing: null,
    streamAbortController: null,
    progressStatus: ref(''),
    progressDetail: ref(''),
    progressToolTrace: ref<ChatToolTrace[]>([]),
    progressJudgeTrace: ref<ChatJudgeTrace[]>([]),
    progressDraftPreview: ref<ChatDraftPreview | null>(null)
  };
  sessions.set(key, session);
  return session;
};

const fetchApplicationProfile = async (session: ChatSession, signal?: AbortSignal) => {
  try {
    const url = `${apiBaseURL}/application/profile`;
    logAuth(session, 'profile', url, 'GET');

    const response = await fetch(url, { method: 'GET', headers: authHeaders(session), signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    session.applicationId = data?.data?.id || '';
    console.log('[useChat] applicationId:', session.applicationId);
  } catch (e) {
    console.error('Error fetching application profile:', e);
  }
};

const openChatSession = async (session: ChatSession, signal?: AbortSignal) => {
  try {
    const url = `${apiBaseURL}/open?application_id=${encodeURIComponent(session.applicationId)}&ts=${Date.now()}`;
    logAuth(session, 'open', url, 'GET');

    let response = await fetch(url, {
      method: 'GET',
      headers: authHeaders(session),
      cache: 'no-store',
      signal
    });
    if (!response.ok && (response.status === 400 || response.status === 404)) {
      const fallbackUrl = `${apiBaseURL}/open?ts=${Date.now()}`;
      logAuth(session, 'open(fallback)', fallbackUrl, 'GET');
      response = await fetch(fallbackUrl, {
        method: 'GET',
        headers: authHeaders(session),
        cache: 'no-store',
        signal
      });
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    session.chatId = data?.data || '';
    console.log('[useChat] chatId:', session.chatId);
  } catch (e) {
    console.error('Error opening chat session:', e);
  }
};

const initializeChatSession = async (session: ChatSession, signal?: AbortSignal) => {
  if (session.chatId) {
    session.initialized = true;
    return;
  }
  if (session.initializing) {
    return session.initializing;
  }
  console.log('[useChat] apiBaseURL:', apiBaseURL);
  session.initializing = (async () => {
    try {
      if (!session.applicationId) {
        await fetchApplicationProfile(session, signal);
      }
      if (!session.chatId) {
        await openChatSession(session, signal);
      }
      session.initialized = Boolean(session.chatId);
    } finally {
      session.initializing = null;
    }
  })();
  return session.initializing;
};

type UseChatOptions = {
  key?: string;
};

export const warmChatSession = async (apiKey: string, key: string) => {
  const session = getSession(key, apiKey);
  session.apiKey = apiKey;
  await initializeChatSession(session);
};

export function useChat(apiKey: string, options: UseChatOptions = {}) {
  const key = options.key || 'default';
  const session = getSession(key, apiKey);
  session.apiKey = apiKey;

  const toggleChat = () => { session.isChatOpen.value = !session.isChatOpen.value; };
  const stopMessage = () => {
    session.streamAbortController?.abort();
  };

  const ensureReady = async (signal?: AbortSignal) => {
    await initializeChatSession(session, signal);
  };

  // 3) 发送消息（POST /chat/api/chat_message/{chat_id}）
  const sendMessage = async (options: SendOptions = {}) => {
    if (session.isStreaming.value) return { aborted: false };
    const overrideText = options.overrideText ?? '';
    const pendingText = overrideText ? overrideText : session.newMessage.value;
    if (!pendingText.trim() && !session.newImage.value) return;

    const textContent = pendingText.trim();
    const imageBase64 = session.newImage.value ? await toBase64(session.newImage.value) : null;
    let userMessageId: number | null = null;

    if (!options.skipUserPush) {
      userMessageId = Date.now();
      session.messages.value.push({
        id: userMessageId,
        sender: 'user',
        text: textContent,
        image: imageBase64
      });
    }
    session.newMessage.value = '';
    session.newImage.value = null;
    session.imagePreview.value = '';
    session.progressStatus.value = 'Preparing request';
    session.progressDetail.value = 'Opening the chat session and getting the response pipeline ready.';
    session.progressToolTrace.value = [];
    session.progressJudgeTrace.value = [];
    session.progressDraftPreview.value = null;

    const controller = new AbortController();
    session.streamAbortController = controller;
    session.isStreaming.value = true;

    let botMessageId: number | null = null;
    let complete = '';
    let evidence = '';

    try {
      await ensureReady(controller.signal);
      if (!session.chatId) {
        console.error('Chat ID is not available. Unable to send message.');
        session.messages.value.push({
          id: Date.now(),
          text: 'Sorry, I could not process your request.',
          sender: 'bot'
        });
        return { aborted: false };
      }

      const url = `${apiBaseURL}/chat_message/${encodeURIComponent(session.chatId)}`;
      logAuth(session, 'sendMessage', url, 'POST');

      const payload: Record<string, any> = {
        message: textContent,
        re_chat: false,
        stream: true
      };
      if (options.model) payload.model = options.model;
      if (Array.isArray(options.history) && options.history.length) {
        payload.history = options.history;
      }
      if (typeof options.deepReview === 'boolean') {
        payload.deep_review = options.deepReview;
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: { ...authHeaders(session), 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      if (!response.body) throw new Error('ReadableStream not supported.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      botMessageId = Date.now();

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6);
          if (jsonStr === '[DONE]') continue;
          try {
            const parsed = JSON.parse(jsonStr);
            const eventType = String(parsed?.type || 'content');
            if (eventType === 'status') {
              session.progressStatus.value = String(parsed?.status || 'Working on your answer');
              session.progressDetail.value = String(parsed?.detail || '');
              continue;
            }
            if (eventType === 'tool') {
              const tool = String(parsed?.tool || 'tool');
              const summary = String(parsed?.summary || '');
              session.progressToolTrace.value = [
                ...session.progressToolTrace.value,
                { id: Date.now() + session.progressToolTrace.value.length, tool, summary }
              ];
              continue;
            }
            if (eventType === 'judge') {
              const summary = String(parsed?.summary || '').trim();
              const verdict = String(parsed?.verdict || '').trim();
              const coverageRaw = parsed?.coverage_score;
              const coverageScore = typeof coverageRaw === 'number' ? coverageRaw : Number.isFinite(Number(coverageRaw)) ? Number(coverageRaw) : null;
              const missingAspects = Array.isArray(parsed?.missing_aspects)
                ? parsed.missing_aspects.map((item: unknown) => String(item || '').trim()).filter(Boolean)
                : [];
              const nextTools = Array.isArray(parsed?.next_tools)
                ? parsed.next_tools.map((item: unknown) => String(item || '').trim()).filter(Boolean)
                : [];
              session.progressJudgeTrace.value = [
                ...session.progressJudgeTrace.value,
                {
                  id: Date.now() + session.progressJudgeTrace.value.length,
                  verdict,
                  summary,
                  coverageScore,
                  missingAspects,
                  nextTools
                }
              ];
              if (summary) {
                session.progressDetail.value = summary;
              }
              continue;
            }
            if (eventType === 'draft_preview') {
              const label = String(parsed?.label || 'Draft answer preview').trim();
              const content = String(parsed?.content || '').trim();
              session.progressDraftPreview.value = content ? { label, content } : null;
              continue;
            }
            if (eventType === 'evidence') {
              evidence = String(parsed?.content || '').trim();
              const effectiveId = botMessageId ?? Date.now();
              if (botMessageId === null) botMessageId = effectiveId;
              const hasBotMessage = session.messages.value.some(v => v.id === botMessageId);
              if (!hasBotMessage) {
                session.messages.value.push({ id: effectiveId, text: '', sender: 'bot' });
              }
              const m = session.messages.value.find(v => v.id === botMessageId);
              if (m) m.text = composeBotMessageText(complete, evidence);
              continue;
            }
            const content = parsed?.content ?? '';
            if (content) {
              complete += content;
              const effectiveId = botMessageId ?? Date.now();
              if (botMessageId === null) botMessageId = effectiveId;
              const hasBotMessage = session.messages.value.some(v => v.id === botMessageId);
              if (!hasBotMessage) {
                session.messages.value.push({ id: effectiveId, text: '', sender: 'bot' });
              }
              const m = session.messages.value.find(v => v.id === botMessageId);
              if (m) m.text = composeBotMessageText(complete, evidence);
            }
          } catch (err) {
            console.error('chunk parse error:', err, line);
          }
        }
      }
      console.log('[useChat] stream ended');
      return { aborted: false };
    } catch (e: any) {
      if (e?.name === 'AbortError') {
        if (botMessageId === null && userMessageId !== null) {
          session.messages.value = session.messages.value.filter(v => v.id !== userMessageId);
        }
        if (botMessageId !== null && !complete.trim()) {
          session.messages.value = session.messages.value.filter(v => v.id !== botMessageId);
        }
        return { aborted: true };
      }
      console.error('Error communicating with API:', e?.message || e);
      session.messages.value.push({ id: Date.now(), text: 'Sorry, I could not process your request.', sender: 'bot' });
      return { aborted: false };
    } finally {
      session.isStreaming.value = false;
      session.streamAbortController = null;
    }
  };

  const toBase64 = (file: File) =>
    new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => (typeof reader.result === 'string' ? resolve(reader.result) : reject(new Error('FileReader result is not a string')));
      reader.onerror = reject;
    });

  const triggerImageUpload = () => { document.getElementById('image-input')?.click(); };
  const previewImage = (event: Event) => {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    if (!file) return;
    session.newImage.value = file;
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => { if (typeof reader.result === 'string') session.imagePreview.value = reader.result; };
  };

  const resetChat = async (newApiKey: string) => {
    stopMessage();
    session.apiKey = newApiKey;
    session.applicationId = '';
    session.chatId = '';
    session.initialized = false;
    session.initializing = null;
    session.isStreaming.value = false;
    session.streamAbortController = null;
    session.progressStatus.value = '';
    session.progressDetail.value = '';
    session.progressToolTrace.value = [];
    session.progressJudgeTrace.value = [];
    session.progressDraftPreview.value = null;
    session.messages.value = [];
    console.log('[useChat] resetChat with new apiKey(m):', mask(session.apiKey));
    await initializeChatSession(session);
    session.messages.value.push({ id: 1, text: defaultGreeting, sender: 'bot' });
  };

  void initializeChatSession(session);

  return {
    isChatOpen: session.isChatOpen,
    messages: session.messages,
    newMessage: session.newMessage,
    newImage: session.newImage,
    imagePreview: session.imagePreview,
    isStreaming: session.isStreaming,
    progressStatus: session.progressStatus,
    progressDetail: session.progressDetail,
    progressToolTrace: session.progressToolTrace,
    progressJudgeTrace: session.progressJudgeTrace,
    progressDraftPreview: session.progressDraftPreview,
    toggleChat,
    sendMessage,
    stopMessage,
    triggerImageUpload,
    previewImage,
    resetChat
  };
}
