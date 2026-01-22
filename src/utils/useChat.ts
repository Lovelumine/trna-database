import { ref, type Ref } from 'vue';

type ChatMessage = {
  id: number;
  text: string;
  sender: string;
  image?: string | null;
};

type ChatSession = {
  apiKey: string;
  isChatOpen: Ref<boolean>;
  messages: Ref<ChatMessage[]>;
  newMessage: Ref<string>;
  newImage: Ref<File | null>;
  imagePreview: Ref<string>;
  applicationId: string;
  chatId: string;
  initialized: boolean;
  initializing: Promise<void> | null;
};

type SendOptions = {
  skipUserPush?: boolean;
  overrideText?: string;
  model?: string;
};

const defaultGreeting = 'Hello, I am your virtual assistant YingYing. How can I assist you today?';
const sessions = new Map<string, ChatSession>();

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
    applicationId: '',
    chatId: '',
    initialized: false,
    initializing: null
  };
  sessions.set(key, session);
  return session;
};

type UseChatOptions = {
  key?: string;
};

export function useChat(apiKey: string, options: UseChatOptions = {}) {
  const key = options.key || 'default';
  const session = getSession(key, apiKey);
  session.apiKey = apiKey;

  // ✅ 必须带前导斜杠
  const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';

  // 日志与打码
  const mask = (s?: string) => (s ? s.replace(/.(?=.{4})/g, '*') : '');
  const logAuth = (where: string, url: string, method: string) => {
    console.log(`[useChat] ${method} ${url}`);
    console.log(`[useChat] ${where} Authorization(m): ${mask(session.apiKey)}`);
    // @ts-ignore
    if (import.meta.env?.VITE_DEBUG_LOG_FULL_AUTH === '1') {
      console.warn('[useChat] Authorization(FULL,DEBUG): Bearer ' + session.apiKey);
    }
  };
  const authHeaders = () => ({
    // ✅ 用标准头 + Bearer 前缀
    Authorization: `Bearer ${session.apiKey}`,
    accept: 'application/json'
  });

  const toggleChat = () => { session.isChatOpen.value = !session.isChatOpen.value; };

  // 1) 获取应用信息
  const fetchApplicationProfile = async () => {
    try {
      const url = `${apiBaseURL}/application/profile`;
      logAuth('profile', url, 'GET');

      const response = await fetch(url, { method: 'GET', headers: authHeaders() });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      session.applicationId = data?.data?.id || '';
      console.log('[useChat] applicationId:', session.applicationId);
    } catch (e) {
      console.error('Error fetching application profile:', e);
    }
  };

  // 2) 打开会话（按你的 Swagger：GET /chat/api/open）
  const openChatSession = async () => {
    try {
      // 可带 application_id，也可不带；先带上
      const url = `${apiBaseURL}/open?application_id=${encodeURIComponent(session.applicationId)}&ts=${Date.now()}`;
      logAuth('open', url, 'GET');

      let response = await fetch(url, { method: 'GET', headers: authHeaders(), cache: 'no-store' });
      // 兜底：如果带 application_id 不被接受，再试不带
      if (!response.ok && (response.status === 400 || response.status === 404)) {
        const url2 = `${apiBaseURL}/open?ts=${Date.now()}`;
        logAuth('open(fallback)', url2, 'GET');
        response = await fetch(url2, { method: 'GET', headers: authHeaders(), cache: 'no-store' });
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      session.chatId = data?.data || '';
      console.log('[useChat] chatId:', session.chatId);
    } catch (e) {
      console.error('Error opening chat session:', e);
    }
  };

  const ensureReady = async () => {
    if (session.chatId) return;
    if (session.initializing) {
      await session.initializing;
    }
    if (!session.applicationId) {
      await fetchApplicationProfile();
    }
    if (!session.chatId) {
      await openChatSession();
    }
  };

  // 3) 发送消息（POST /chat/api/chat_message/{chat_id}）
  const sendMessage = async (options: SendOptions = {}) => {
    const overrideText = options.overrideText ?? '';
    const pendingText = overrideText ? overrideText : session.newMessage.value;
    if (!pendingText.trim() && !session.newImage.value) return;
    await ensureReady();
    if (!session.chatId) {
      console.error('Chat ID is not available. Unable to send message.');
      session.messages.value.push({
        id: Date.now(),
        text: 'Sorry, I could not process your request.',
        sender: 'bot'
      });
      return;
    }

    const textContent = pendingText.trim();
    const imageBase64 = session.newImage.value ? await toBase64(session.newImage.value) : null;

    if (!options.skipUserPush) {
      session.messages.value.push({
        id: Date.now(),
        sender: 'user',
        text: textContent,
        image: imageBase64
      });
    }
    session.newMessage.value = '';
    session.newImage.value = null;
    session.imagePreview.value = '';

    try {
      const url = `${apiBaseURL}/chat_message/${encodeURIComponent(session.chatId)}`;
      logAuth('sendMessage', url, 'POST');

      const payload: Record<string, any> = {
        message: textContent,
        re_chat: false,
        stream: true
      };
      if (options.model) payload.model = options.model;

      const response = await fetch(url, {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.body) throw new Error('ReadableStream not supported.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      const botMessageId = Date.now();
      session.messages.value.push({ id: botMessageId, text: '', sender: 'bot' });

      let buffer = '';
      let complete = '';

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
            const content = parsed?.content ?? '';
            if (content) {
              complete += content;
              const m = session.messages.value.find(v => v.id === botMessageId);
              if (m) m.text = complete.trim();
            }
          } catch (err) {
            console.error('chunk parse error:', err, line);
          }
        }
      }
      console.log('[useChat] stream ended');
    } catch (e: any) {
      console.error('Error communicating with API:', e?.message || e);
      session.messages.value.push({ id: Date.now(), text: 'Sorry, I could not process your request.', sender: 'bot' });
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

  const initializeChat = async () => {
    if (session.initialized) return;
    if (session.initializing) return session.initializing;
    console.log('[useChat] apiBaseURL:', apiBaseURL);
    session.initializing = (async () => {
      await fetchApplicationProfile();
      await openChatSession();
      session.initialized = true;
      session.initializing = null;
    })();
    return session.initializing;
  };

  const resetChat = async (newApiKey: string) => {
    session.apiKey = newApiKey;
    session.applicationId = '';
    session.chatId = '';
    session.initialized = false;
    session.initializing = null;
    session.messages.value = [];
    console.log('[useChat] resetChat with new apiKey(m):', mask(session.apiKey));
    await fetchApplicationProfile();
    await openChatSession();
    session.initialized = true;
    session.initializing = null;
    session.messages.value.push({ id: 1, text: defaultGreeting, sender: 'bot' });
  };

  initializeChat();

  return {
    isChatOpen: session.isChatOpen,
    messages: session.messages,
    newMessage: session.newMessage,
    newImage: session.newImage,
    imagePreview: session.imagePreview,
    toggleChat,
    sendMessage,
    triggerImageUpload,
    previewImage,
    resetChat
  };
}
