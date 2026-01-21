import { ref } from 'vue';
import { marked } from 'marked';

export function useChat(apiKey: string) {
  apiKey = (apiKey || '').trim();

  const isChatOpen = ref(false);
  const messages = ref<Array<{ id: number; text: string; sender: string; image?: string }>>([
    { id: 1, text: '我是学习助手荧荧，您可以就视频中的内容对我进行提问！', sender: 'bot' }
  ]);

  const newMessage = ref('');
  const newImage = ref<File | null>(null);
  const imagePreview = ref('');

  // ✅ 必须带前导斜杠，确保可被 dev/prod 代理命中
  const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';
  let applicationId = '';
  let chatId = '';

  // —— 日志与打码（便于排查 401/404）——
  const mask = (s?: string) => (s ? s.replace(/.(?=.{4})/g, '*') : '');
  const log = (...args: any[]) => console.log('[useChat]', ...args);

  const authHeaders = () => ({
    // ✅ 统一标准头名与 Bearer 前缀
    Authorization: `Bearer ${apiKey}`,
    Accept: 'application/json',
  });

  const toggleChat = () => { isChatOpen.value = !isChatOpen.value; };

  // 1) 获取应用信息：GET /chat/api/application/profile
  const fetchApplicationProfile = async () => {
    try {
      const url = `${apiBaseURL}/application/profile`;
      log('GET', url, 'Authorization(m):', mask(apiKey));
      const resp = await fetch(url, { method: 'GET', headers: authHeaders() });
      const txt = await resp.text();
      if (!resp.ok) {
        console.error('Profile failed:', resp.status, txt);
        throw new Error(`profile ${resp.status}`);
      }
      const data = JSON.parse(txt);
      applicationId = data?.data?.id || '';
      if (!applicationId) throw new Error('No applicationId in response');
      log('applicationId:', applicationId);
    } catch (e) {
      console.error('Error fetching application profile:', e);
      throw e;
    }
  };

  // 2) 打开会话：优先 /open?application_id=...，404/400 时兜底 /open
  const openChatSession = async () => {
    if (!applicationId) throw new Error('applicationId is empty');
    try {
      let url = `${apiBaseURL}/open?application_id=${encodeURIComponent(applicationId)}&ts=${Date.now()}`;
      log('GET', url);
      let resp = await fetch(url, { method: 'GET', headers: authHeaders(), cache: 'no-store' });

      if (!resp.ok && (resp.status === 400 || resp.status === 404)) {
        // 兜底：不带 application_id
        url = `${apiBaseURL}/open?ts=${Date.now()}`;
        log('GET (fallback)', url);
        resp = await fetch(url, { method: 'GET', headers: authHeaders(), cache: 'no-store' });
      }

      const txt = await resp.text();
      if (!resp.ok) {
        console.error('Open chat failed:', resp.status, txt);
        throw new Error(`open ${resp.status}`);
      }
      const data = JSON.parse(txt);
      chatId = data?.data || '';
      if (!chatId) throw new Error('No chatId in response');
      log('chatId:', chatId);
    } catch (e) {
      console.error('Error opening chat session:', e);
      throw e;
    }
  };

  // 3) 发送消息（保留你的签名）：POST /chat/api/chat_message/{chat_id}
  const sendMessage = async (userMessage: string, messageWithContext: string) => {
    if (!messageWithContext.trim() && !newImage.value) return;

    // 确保鉴权/会话已就绪
    if (!applicationId) await fetchApplicationProfile();
    if (!chatId)        await openChatSession();

    const imageBase64 = newImage.value ? await toBase64(newImage.value) : null;

    // 先显示用户消息
    messages.value.push({
      id: Date.now(),
      sender: 'user',
      text: userMessage,
      image: imageBase64 ? `data:image/jpeg;base64,${imageBase64}` : undefined
    });

    newMessage.value = '';
    newImage.value = null;
    imagePreview.value = '';

    try {
      const url = `${apiBaseURL}/chat_message/${encodeURIComponent(chatId)}`;
      log('POST', url);

      const resp = await fetch(url, {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageWithContext, // 仍然发送你拼好的上下文
          re_chat: false,
          stream: true
        })
      });

      // 非 2xx 且没有流，先把错误体打出来
      if (!resp.ok && !resp.body) {
        const errTxt = await resp.text();
        console.error('Send failed:', resp.status, errTxt);
        messages.value.push({ id: Date.now(), text: `请求失败：${resp.status} ${errTxt}`, sender: 'bot' });
        return;
      }

      const reader = resp.body!.getReader();
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
      log('stream ended');
    } catch (e: any) {
      console.error('Error communicating with API:', e?.message || e);
      messages.value.push({ id: Date.now(), text: 'Sorry, I could not process your request.', sender: 'bot' });
    }
  };

  const toBase64 = (file: File) =>
    new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          // 这里只需要 Base64 主体；上面 sendMessage 会拼 dataURL
          const comma = reader.result.indexOf(',');
          resolve(comma >= 0 ? reader.result.slice(comma + 1) : reader.result);
        } else reject(new Error('FileReader result is not a string'));
      };
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
    log('apiBaseURL:', apiBaseURL, 'Authorization(m):', mask(apiKey));
    try {
      await fetchApplicationProfile();
      await openChatSession();
    } catch (e) {
      // 初始化失败时，控制台已有详细错误
    }
  };

  const resetChat = async (newApiKey: string) => {
    apiKey = (newApiKey || '').trim();
    messages.value = [{ id: 1, text: '我是学习助手荧荧，您可以就视频中的内容对我进行提问！', sender: 'bot' }];
    applicationId = '';
    chatId = '';
    await initializeChat();
  };

  initializeChat();

  return {
    isChatOpen, messages, newMessage, newImage, imagePreview,
    toggleChat, sendMessage, triggerImageUpload, previewImage, resetChat
  };
}
