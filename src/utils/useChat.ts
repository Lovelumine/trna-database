import { ref } from 'vue';

export function useChat(apiKey: string) {
  const isChatOpen = ref(false);
  const messages = ref<Array<{ id: number; text: string; sender: string; image?: string | null }>>([
    { id: 1, text: 'Hello, I am your virtual assistant YingYing. How can I assist you today?', sender: 'bot' }
  ]);

  const newMessage = ref('');
  const newImage = ref<File | null>(null);
  const imagePreview = ref('');

  // ✅ 必须带前导斜杠
  const apiBaseURL = '/chat/api';
  let applicationId = '';
  let chatId = '';

  // 日志与打码
  const mask = (s?: string) => (s ? s.replace(/.(?=.{4})/g, '*') : '');
  const logAuth = (where: string, url: string, method: string) => {
    console.log(`[useChat] ${method} ${url}`);
    console.log(`[useChat] ${where} Authorization(m): ${mask(apiKey)}`);
    // @ts-ignore
    if (import.meta.env?.VITE_DEBUG_LOG_FULL_AUTH === '1') {
      console.warn('[useChat] Authorization(FULL,DEBUG): Bearer ' + apiKey);
    }
  };
  const authHeaders = () => ({
    // ✅ 用标准头 + Bearer 前缀
    Authorization: `Bearer ${apiKey}`,
    accept: 'application/json'
  });

  const toggleChat = () => { isChatOpen.value = !isChatOpen.value; };

  // 1) 获取应用信息
  const fetchApplicationProfile = async () => {
    try {
      const url = `${apiBaseURL}/application/profile`;
      logAuth('profile', url, 'GET');

      const response = await fetch(url, { method: 'GET', headers: authHeaders() });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      applicationId = data?.data?.id || '';
      console.log('[useChat] applicationId:', applicationId);
    } catch (e) {
      console.error('Error fetching application profile:', e);
    }
  };

  // 2) 打开会话（按你的 Swagger：GET /chat/api/open）
  const openChatSession = async () => {
    try {
      // 可带 application_id，也可不带；先带上
      const url = `${apiBaseURL}/open?application_id=${encodeURIComponent(applicationId)}&ts=${Date.now()}`;
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
      chatId = data?.data || '';
      console.log('[useChat] chatId:', chatId);
    } catch (e) {
      console.error('Error opening chat session:', e);
    }
  };

  // 3) 发送消息（POST /chat/api/chat_message/{chat_id}）
  const sendMessage = async () => {
    if (!newMessage.value.trim() && !newImage.value) return;
    if (!chatId) {
      console.error('Chat ID is not available. Unable to send message.');
      return;
    }

    const textContent = newMessage.value.trim();
    const imageBase64 = newImage.value ? await toBase64(newImage.value) : null;

    messages.value.push({
      id: Date.now(),
      sender: 'user',
      text: textContent,
      image: imageBase64
    });
    newMessage.value = '';
    newImage.value = null;
    imagePreview.value = '';

    try {
      const url = `${apiBaseURL}/chat_message/${encodeURIComponent(chatId)}`;
      logAuth('sendMessage', url, 'POST');

      const response = await fetch(url, {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textContent,
          re_chat: false,
          stream: true
          // 若需要看图，这里把 imageBase64 一起传：image: imageBase64
        })
      });

      if (!response.body) throw new Error('ReadableStream not supported.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      const botMessageId = Date.now();
      messages.value.push({ id: botMessageId, text: '', sender: 'bot' });

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
              const m = messages.value.find(v => v.id === botMessageId);
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
      messages.value.push({ id: Date.now(), text: 'Sorry, I could not process your request.', sender: 'bot' });
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
    newImage.value = file;
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => { if (typeof reader.result === 'string') imagePreview.value = reader.result; };
  };

  const initializeChat = async () => {
    console.log('[useChat] apiBaseURL:', apiBaseURL);
    await fetchApplicationProfile();
    await openChatSession();
  };

  const resetChat = async (newApiKey: string) => {
    apiKey = newApiKey;
    messages.value = [];
    console.log('[useChat] resetChat with new apiKey(m):', mask(apiKey));
    await fetchApplicationProfile();
    await openChatSession();
    messages.value.push({ id: 1, text: 'Hello, I am your virtual assistant YingYing. How can I assist you today?', sender: 'bot' });
  };

  initializeChat();

  return { isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage, triggerImageUpload, previewImage, resetChat };
}
