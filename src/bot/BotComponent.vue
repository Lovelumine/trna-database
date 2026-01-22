<template>
  <div id="bot-container" ref="element" v-if="!isAiPage">
    <div id="bot-icon" @click="toggleChat" @mousedown="startDrag">
      <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" alt="Bot Icon" @dragstart.prevent />
    </div>

    <div id="chat-box" v-if="chat.isChatOpen">
      <div id="chat-header" ref="headerRef" @mousedown="startDrag">
        <div class="header-left">
          <span class="chat-header-title">AI Web Navigator</span>
          <div class="header-select-group">
            <button
              class="header-icon-button"
              type="button"
              @mousedown.stop
              @click.stop="toggleSessionSelect"
              aria-label="Switch conversation"
              title="Switch conversation"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M4 6h16a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H7l-4 3v-3H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z"></path>
              </svg>
            </button>
            <div
              v-if="showSessionSelect"
              class="header-menu"
              role="listbox"
              aria-label="Switch conversation"
            >
              <button
                v-for="session in sessionOptions"
                :key="session.id"
                class="header-menu-item"
                type="button"
                role="option"
                :aria-selected="session.id === activeSessionId"
                :data-active="session.id === activeSessionId"
                @click.stop="selectSession(session.id)"
              >
                {{ session.title }}
              </button>
            </div>
          </div>
          <div class="header-select-group">
            <button
              class="header-icon-button"
              type="button"
              @mousedown.stop
              @click.stop="toggleModelSelect"
              aria-label="Select model"
              title="Select model"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 2a5 5 0 0 1 5 5v2h2a2 2 0 0 1 2 2v4a7 7 0 1 1-14 0V7a5 5 0 0 1 5-5zm3 7V7a3 3 0 1 0-6 0v2h6z"></path>
              </svg>
            </button>
            <div
              v-if="showModelSelect"
              class="header-menu"
              role="listbox"
              aria-label="Select model"
            >
              <button
                v-for="model in modelOptions"
                :key="model"
                class="header-menu-item"
                type="button"
                role="option"
                :aria-selected="model === selectedModel"
                :data-active="model === selectedModel"
                @click.stop="selectModel(model)"
              >
                {{ model }}
              </button>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <button
            @click="openFullscreen"
            @mousedown.stop
            class="header-button"
            aria-label="Open fullscreen"
            title="Open fullscreen"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M7 14H5v5h5v-2H7v-3zm0-4h2V7h3V5H7v5zm10 0h2V5h-5v2h3v3zm0 4h-2v3h-3v2h5v-5z"></path>
            </svg>
          </button>
          <button
            @click="toggleChat"
            @mousedown.stop
            class="close-button"
            aria-label="Close chat"
          >
            <el-icon><close /></el-icon>
          </button>
        </div>
      </div>

      <!-- AI 英文提示 -->
      <div id="ai-tip" role="note" aria-live="polite">
        <span class="ai-tip-text">
          <span class="ai-tip-icon" aria-hidden="true">!</span>
          {{ aiTip }}
        </span>
      </div>

      <div id="chat-content" ref="chatContent">
        <!-- 主消息流：证据块跟在每条 bot 消息后 -->
        <template v-for="(msg, i) in safeMessages" :key="(msg.id ?? 'msg') + '-' + i">
          <div :class="['message-container', msg.sender || 'bot']">
            <!-- 头像 -->
            <img
              v-if="(msg.sender || 'bot') === 'bot'"
              src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png"
              class="avatar"
              alt=""
            />
            <img
              v-else
              src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png"
              class="avatar"
              alt=""
            />
            <!-- 气泡 -->
            <div class="message">
              <span
                v-if="(msg.sender || 'bot') === 'bot' && !msg.text && !msg.textHtml"
                class="loading-dots"
              >...</span>
              <span v-else v-html="msg.textHtml || msg.text || ''"></span>
              <img v-if="msg.image" :src="msg.image" class="message-image" />
              <div class="message-actions">
                <button
                  class="message-action"
                  type="button"
                  @click="copyMessage(msg, i)"
                  :aria-label="'Copy message ' + (i + 1)"
                >
                  Copy
                </button>
                <button
                  v-if="(msg.sender || 'bot') === 'user' && isLatestUserMessage(msg)"
                  class="message-action"
                  type="button"
                  @click="editMessage(msg)"
                  aria-label="Edit message"
                >
                  Edit
                </button>
              </div>
              <span
                v-if="copiedId === (msg.id ?? i) && !msg.evidenceHtml"
                class="message-copied"
              >
                Copied
              </span>
            </div>
          </div>

          <!-- 证据块：仅 bot 且存在 evidenceHtml 时渲染；默认折叠，紧跟消息 -->
          <div
            v-if="(msg.sender || 'bot') === 'bot' && msg.evidenceHtml"
            class="evidence-card"
          >
            <details>
              <summary>
                <span>Search results (RAG)</span>
                <span class="rag-actions">
                  <button
                    class="message-action rag-action"
                    type="button"
                    @click.prevent.stop="copyMessage(msg, i)"
                    aria-label="Copy message"
                    title="Copy"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M8 8h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2zm-2 8H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1h-2V6H6v8z"></path>
                    </svg>
                  </button>
                  <button
                    v-if="isLatestBotMessage(msg)"
                    class="message-action rag-action"
                    type="button"
                    @click.prevent.stop="regenerateFromMessage(msg)"
                    aria-label="Regenerate response"
                    title="Regenerate"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M12 6V3L8 7l4 4V8c2.76 0 5 2.24 5 5 0 1.12-.37 2.16-1 3l1.46 1.46A6.96 6.96 0 0 0 19 13c0-3.87-3.13-7-7-7zm-5 5c0-1.12.37-2.16 1-3L6.54 6.54A6.96 6.96 0 0 0 5 11c0 3.87 3.13 7 7 7v3l4-4-4-4v3c-2.76 0-5-2.24-5-5z"></path>
                    </svg>
                  </button>
                  <span v-if="copiedId === (msg.id ?? i)" class="rag-copied-badge">Copied</span>
                </span>
              </summary>
              <div class="evidence-body" v-html="msg.evidenceHtml"></div>
            </details>
          </div>
        </template>

        <!-- Loading -->
        <div v-if="showLoading" class="message-container bot">
          <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" class="avatar" alt="" />
          <div class="message"><span>...</span></div>
        </div>
      </div>

      <div id="chat-input-container">
        <!-- 示例问题（父容器横向滚动） -->
        <div id="example-questions" v-if="showExampleQuestions" ref="exampleWrap">
          <div id="question-slider">
            <button @click="fillExample('What are the main features of ENSURE?')">What are the main features of ENSURE?</button>
            <button @click="fillExample('What is sup-tRNA?')">What is sup-tRNA?</button>
            <button @click="fillExample('How does RNA sequencing work?')">How does RNA sequencing work?</button>
            <button @click="fillExample('Explain the role of ncRNA.')">Explain the role of ncRNA.</button>
          </div>
        </div>

        <!-- 输入 -->
        <div id="input-area">
          <input
            id="chat-input"
            v-model="inputText"
            @keypress.enter="sendMessage"
            :placeholder="inputPlaceholder"
            ref="chatInput"
          />
          <button
            id="new-chat-button"
            type="button"
            @click="createNewSession"
            aria-label="New chat"
            title="New chat"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5v14m-7-7h14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>
            </svg>
          </button>
          <button @click="sendMessage" id="send-button">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>

        <input type="file" id="image-input" @change="previewImage" style="display: none;" />
        <div v-if="chatImagePreview" class="image-preview">
          <img :src="chatImagePreview" alt="Image Preview" class="image-preview-thumbnail" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, nextTick, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useDraggable } from './Draggable';
import { useChat } from '../utils/useChat';
import { useMarkdown } from '../utils/useMarkdown';
import { ElIcon } from 'element-plus';
import { Close } from '@element-plus/icons-vue';

export default defineComponent({
  name: 'BotComponent',
  components: { ElIcon, Close },
  setup() {
    const apiKey = import.meta.env.VITE_API_KEY;

    const { element, startDrag } = useDraggable();
    const activeSessionId = ref(
      localStorage.getItem('ai_chat_active_session') || 'floating-assistant'
    );
    const chat = ref(useChat(apiKey, { key: activeSessionId.value }));
    const sessionOptions = ref<Array<{ id: string; title: string }>>([]);
    const modelOptions = ['qwen3:32b', 'gemma3:27b'];
    const selectedModel = ref(
      localStorage.getItem('ai_chat_model') || 'qwen3:32b'
    );
    const showSessionSelect = ref(false);
    const showModelSelect = ref(false);
    const headerRef = ref<HTMLDivElement | null>(null);
    const draftSessionId = ref('');
    const toggleSessionSelect = () => {
      showSessionSelect.value = !showSessionSelect.value;
      if (showSessionSelect.value) showModelSelect.value = false;
    };
    const toggleModelSelect = () => {
      showModelSelect.value = !showModelSelect.value;
      if (showModelSelect.value) showSessionSelect.value = false;
    };
    const selectSession = (id: string) => {
      activeSessionId.value = id;
      showSessionSelect.value = false;
    };
    const selectModel = (model: string) => {
      selectedModel.value = model;
      showModelSelect.value = false;
    };
    const toggleChat = () => { setChatOpen(!getChatOpen()); };
    const previewImage = (event: Event) => chat.value.previewImage(event);
    const { renderMarkdown } = useMarkdown();
    const router = useRouter();
    const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';

    const loading = ref(false);
    const renderedMessages = ref<any[]>([]);
    const localMessages = ref<any[]>([]);
    const chatContent = ref<HTMLDivElement | null>(null);

    const showExampleQuestions = ref(true);
    const sessionsStorageKey = 'ai_chat_sessions';
    const activeSessionStorageKey = 'ai_chat_active_session';
    const chatMeta = ref<{ applicationId: string; chatId: string }>({
      applicationId: '',
      chatId: ''
    });

    const loadSessions = () => {
      let items: Array<{ id?: string; title?: string }> = [];
      try {
        const raw = localStorage.getItem(sessionsStorageKey);
        items = raw ? JSON.parse(raw) : [];
      } catch {
        items = [];
      }
      if (!Array.isArray(items)) items = [];
      if (!items.some(s => s?.id === 'floating-assistant')) {
        items.unshift({ id: 'floating-assistant', title: 'AI Web Navigator' });
      }
      if (draftSessionId.value && !items.some(s => s?.id === draftSessionId.value)) {
        items.unshift({ id: draftSessionId.value, title: 'New chat' });
      }
      sessionOptions.value = items
        .filter(s => s?.id)
        .map(s => ({
          id: String(s.id),
          title: (s.title || 'New chat').toString()
        }));
      if (!sessionOptions.value.length) {
        sessionOptions.value = [{ id: 'floating-assistant', title: 'AI Web Navigator' }];
      }
      if (!sessionOptions.value.some(s => s.id === activeSessionId.value)) {
        activeSessionId.value = sessionOptions.value[0].id;
      }
    };

    const chatMetaKey = () => `ai_chat_meta_${activeSessionId.value}`;
    const loadChatMeta = () => {
      try {
        const raw = localStorage.getItem(chatMetaKey());
        const parsed = raw ? JSON.parse(raw) : null;
        if (parsed && typeof parsed === 'object') {
          chatMeta.value = {
            applicationId: String(parsed.applicationId || ''),
            chatId: String(parsed.chatId || '')
          };
          return;
        }
      } catch {
        // ignore malformed cache
      }
      chatMeta.value = { applicationId: '', chatId: '' };
    };
    const saveChatMeta = () => {
      localStorage.setItem(chatMetaKey(), JSON.stringify(chatMeta.value));
    };

    const authHeaders = () => ({
      Authorization: `Bearer ${apiKey}`,
      accept: 'application/json'
    });
    const fetchApplicationProfile = async () => {
      const url = `${apiBaseURL}/application/profile`;
      const response = await fetch(url, { method: 'GET', headers: authHeaders() });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      chatMeta.value.applicationId = data?.data?.id || '';
      saveChatMeta();
    };
    const openChatSession = async () => {
      const url = `${apiBaseURL}/open?application_id=${encodeURIComponent(chatMeta.value.applicationId)}&ts=${Date.now()}`;
      let response = await fetch(url, { method: 'GET', headers: authHeaders(), cache: 'no-store' });
      if (!response.ok && (response.status === 400 || response.status === 404)) {
        const url2 = `${apiBaseURL}/open?ts=${Date.now()}`;
        response = await fetch(url2, { method: 'GET', headers: authHeaders(), cache: 'no-store' });
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      chatMeta.value.chatId = data?.data || '';
      saveChatMeta();
    };
    const ensureChatReady = async () => {
      if (!chatMeta.value.applicationId) {
        await fetchApplicationProfile();
      }
      if (!chatMeta.value.chatId) {
        await openChatSession();
      }
    };
    const clearImageState = () => {
      const rawPreview: any = chat.value.imagePreview;
      if (rawPreview && typeof rawPreview === 'object' && 'value' in rawPreview) {
        rawPreview.value = '';
      } else {
        chat.value.imagePreview = '';
      }
      const rawNewImage: any = chat.value.newImage;
      if (rawNewImage && typeof rawNewImage === 'object' && 'value' in rawNewImage) {
        rawNewImage.value = null;
      } else {
        chat.value.newImage = null as any;
      }
    };

    const saveSessions = (items: Array<{ id: string; title?: string; updatedAt?: number; customTitle?: boolean }>) => {
      localStorage.setItem(sessionsStorageKey, JSON.stringify(items));
    };

    const createNewSession = () => {
      if (draftSessionId.value) {
        activeSessionId.value = draftSessionId.value;
        return;
      }
      const id = `chat_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      const next = {
        id,
        title: 'New chat',
        updatedAt: Date.now(),
        customTitle: false
      };
      draftSessionId.value = id;
      activeSessionId.value = id;
      loadSessions();
    };

    const hydrateMessages = () => {
      const key = `ai_chat_session_${activeSessionId.value}`;
      try {
        const raw = localStorage.getItem(key);
        const parsed = raw ? JSON.parse(raw) : null;
        if (Array.isArray(parsed?.messages)) {
          setMessagesValue(parsed.messages);
          return;
        }
      } catch {
        // ignore malformed cache
      }
      if (!getMessagesValue().length) {
        setMessagesValue([
          { id: 1, sender: 'bot', text: 'Hello, I am your virtual assistant YingYing. How can I assist you today?' }
        ]);
      }
    };

    const persistMessages = () => {
      const list = getMessagesValue();
      if (!Array.isArray(list)) return;
      const hasUser = list.some(m => m?.sender === 'user' && String(m?.text || '').trim());
      if (!hasUser) return;
      const payload = { messages: list, updatedAt: Date.now() };
      localStorage.setItem(`ai_chat_session_${activeSessionId.value}`, JSON.stringify(payload));
    };

    const aiTip = ref(
      'Note: AI-generated responses may be inaccurate. Please verify important information.'
    );
    const inputPlaceholder = computed(() => 'Type a message...');
    const copiedId = ref<number | null>(null);
    const chatInput = ref<HTMLInputElement | null>(null);
    const editingMessageId = ref<number | null>(null);
    const isAiPage = computed(() => {
      const path = router.currentRoute.value?.path || '';
      return path.toLowerCase().startsWith('/aiyingying');
    });

    /* -------- 示例问题横向滚动 -------- */
    const exampleWrap = ref<HTMLDivElement | null>(null);
    let cleanupFns: Array<() => void> = [];

    const enableSliderInteractions = async () => {
      await nextTick();
      const el = exampleWrap.value;
      if (!el) return;

      let isDown = false, startX = 0, startLeft = 0;
      const onDown = (e: MouseEvent | TouchEvent) => {
        isDown = true;
        startX = 'touches' in e ? e.touches[0].pageX : (e as MouseEvent).pageX;
        startLeft = el.scrollLeft;
      };
      const onMove = (e: MouseEvent | TouchEvent) => {
        if (!isDown) return;
        e.preventDefault();
        const x = 'touches' in e ? e.touches[0].pageX : (e as MouseEvent).pageX;
        el.scrollLeft = startLeft - (x - startX);
      };
      const onUp = () => { isDown = false; };

      el.addEventListener('mousedown', onDown);
      el.addEventListener('mousemove', onMove);
      el.addEventListener('mouseleave', onUp);
      el.addEventListener('mouseup', onUp);
      el.addEventListener('touchstart', onDown, { passive: true });
      el.addEventListener('touchmove', onMove as any, { passive: false });
      el.addEventListener('touchend', onUp);
      cleanupFns.push(() => {
        el.removeEventListener('mousedown', onDown);
        el.removeEventListener('mousemove', onMove);
        el.removeEventListener('mouseleave', onUp);
        el.removeEventListener('mouseup', onUp);
        el.removeEventListener('touchstart', onDown);
        el.removeEventListener('touchmove', onMove as any);
        el.removeEventListener('touchend', onUp);
      });

      const onWheel = (e: WheelEvent) => {
        if (Math.abs(e.deltaY) >= Math.abs(e.deltaX)) {
          el.scrollLeft += e.deltaY;
          e.preventDefault();
        }
      };
      el.addEventListener('wheel', onWheel, { passive: false });
      cleanupFns.push(() => el.removeEventListener('wheel', onWheel));
    };

    const rebindSlider = async () => {
      cleanupFns.forEach(fn => fn());
      cleanupFns = [];
      if (getChatOpen() && showExampleQuestions.value) {
        await enableSliderInteractions();
      }
    };

    const handleDocClick = (event: MouseEvent) => {
      const target = event.target as Node | null;
      if (!headerRef.value || !target) return;
      if (!headerRef.value.contains(target)) {
        showSessionSelect.value = false;
        showModelSelect.value = false;
      }
    };

    onMounted(async () => {
      loadSessions();
      hydrateMessages();
      loadChatMeta();
      const hasSentMessage = localStorage.getItem('hasSentMessage');
      if (hasSentMessage === 'true') showExampleQuestions.value = false;
      await rebindSlider();
      window.addEventListener('storage', loadSessions);
      window.addEventListener('click', handleDocClick);
    });
    onBeforeUnmount(() => cleanupFns.forEach(fn => fn()));
    onBeforeUnmount(() => window.removeEventListener('storage', loadSessions));
    onBeforeUnmount(() => window.removeEventListener('click', handleDocClick));
    const inputText = ref('');
    const setChatOpen = (next: boolean) => {
      const raw: any = chat.value.isChatOpen;
      if (raw && typeof raw === 'object' && 'value' in raw) {
        raw.value = next;
      } else {
        chat.value.isChatOpen = next as any;
      }
    };
    const getChatOpen = () => {
      const raw: any = chat.value.isChatOpen;
      return raw && typeof raw === 'object' && 'value' in raw ? !!raw.value : !!raw;
    };
    const getMessagesValue = () => localMessages.value;
    const setMessagesValue = (next: any[]) => {
      localMessages.value = Array.isArray(next) ? next : [];
    };
    const chatImagePreview = computed(() => {
      const raw: any = chat.value.imagePreview;
      return raw && typeof raw === 'object' && 'value' in raw ? raw.value : raw;
    });

    watch(activeSessionId, (nextId) => {
      localStorage.setItem(activeSessionStorageKey, nextId);
      setMessagesValue([]);
      loading.value = false;
      inputText.value = '';
      editingMessageId.value = null;
      const wasOpen = getChatOpen();
      chat.value = useChat(apiKey, { key: nextId });
      if (wasOpen) setChatOpen(true);
      hydrateMessages();
      loadChatMeta();
    });
    watch(selectedModel, (next) => {
      localStorage.setItem('ai_chat_model', next);
    }, { immediate: true });
    watch(
      () => getChatOpen(),
      () => { rebindSlider(); }
    );
    watch(showExampleQuestions, rebindSlider);

    /* -------- 切分 “Search result:” -------- */
    const splitSearchResult = (raw: string) => {
      if (typeof raw !== 'string') return { main: '', evidence: '' };
      const s = raw.replace(/\r\n/g, '\n');
      // 宽松匹配：支持 Markdown 修饰、复数、大小写、中文冒号
      const re = /(?:^|\n)\s*(?:[*_#>\-\d.\)\s]{0,6})?(?:Search\s*results?)\s*[:：]\s*/i;
      let m = re.exec(s);
      if (!m) {
        // 兜底：没有冒号也切
        const loose = /(?:^|\n)\s*(?:[*_#>\-\d.\)\s]{0,6})?(?:Search\s*results?)/i.exec(s);
        if (loose) {
          const after = s.slice(loose.index).replace(/^[^\n]*\n?/, '');
          return { main: s.slice(0, loose.index).trim(), evidence: after.trim() };
        }
        return { main: s, evidence: '' };
      }
      const main = s.slice(0, m.index).trim();
      const evidence = s.slice(m.index + m[0].length).trim();
      return { main, evidence };
    };

    /* -------- 渲染/派生 -------- */
    const safeMessages = computed<any[]>(() =>
      Array.isArray(renderedMessages.value)
        ? renderedMessages.value.filter(Boolean)
        : []
    );
    const messagesSnapshot = computed(() => localMessages.value);

    const showLoading = computed(() => {
      if (!loading.value) return false;
      const list = messagesSnapshot.value;
      const last = list[list.length - 1];
      return !last || last.sender !== 'bot';
    });

    const renderToken = ref(0);
    watch(
      messagesSnapshot,
      async (newVal) => {
        const token = ++renderToken.value;
        if (!Array.isArray(newVal)) { renderedMessages.value = []; return; }
        const rendered = await Promise.all(
          newVal.map(async (m: any) => {
            const msg: any = { ...m };
            msg.sender ??= msg.role ?? 'bot';

            // text 或 content 里做切分
            const rawText =
              typeof msg.text === 'string'
                ? msg.text
                : (typeof msg.content === 'string' ? msg.content : '');

            if (rawText) {
              const { main, evidence } = splitSearchResult(rawText);
              msg.text = main;
              msg.evidence = evidence;
            }

            if (msg.text) {
              msg.textHtml = await renderMarkdown(String(msg.text));
            } else {
              msg.textHtml = msg.textHtml || '';
            }
            if (msg.evidence) {
              msg.evidenceHtml = await renderMarkdown(String(msg.evidence));
            } else {
              msg.evidenceHtml = msg.evidenceHtml || '';
            }
            return msg;
          })
        );

        if (token !== renderToken.value) return;
        renderedMessages.value = rendered;

        await nextTick();
        if (chatContent.value) chatContent.value.scrollTop = chatContent.value.scrollHeight;
        persistMessages();
      },
      { deep: true, immediate: true }
    );

    /* -------- 发送 -------- */
    const sendMessage = async () => {
      const text = inputText.value.trim();
      if (!text) return;

      if (draftSessionId.value && activeSessionId.value === draftSessionId.value) {
        const hasUser = getMessagesValue().some(
          m => m?.sender === 'user' && String(m?.text || '').trim()
        );
        if (!hasUser) {
          let items: any[] = [];
          try {
            const raw = localStorage.getItem(sessionsStorageKey);
            items = raw ? JSON.parse(raw) : [];
          } catch {
            items = [];
          }
          if (!Array.isArray(items)) items = [];
          items = items.filter(s => s?.id && s.id !== draftSessionId.value);
          items.unshift({
            id: draftSessionId.value,
            title: 'New chat',
            updatedAt: Date.now(),
            customTitle: false
          });
          saveSessions(items);
          draftSessionId.value = '';
          loadSessions();
        }
      }

      if (editingMessageId.value) {
        const list = getMessagesValue();
        const index = list.findIndex(m => m.id === editingMessageId.value);
        if (index >= 0) {
          list[index].text = text;
          list.splice(index + 1);
          setMessagesValue(list);
        }
      }

      const imagePreview = chatImagePreview.value || '';
      inputText.value = '';
      if (!editingMessageId.value) {
        const messageId = Date.now() + Math.floor(Math.random() * 1000);
        const list = [...getMessagesValue()];
        list.push({
          id: messageId,
          sender: 'user',
          text,
          image: imagePreview || null
        });
        setMessagesValue(list);
      }

      loading.value = true;
      try {
        await ensureChatReady();
        if (!chatMeta.value.chatId) {
          throw new Error('Chat ID is not available.');
        }
        const botMessageId = Date.now() + Math.floor(Math.random() * 1000);
        const list = [...getMessagesValue()];
        list.push({ id: botMessageId, text: '', sender: 'bot' });
        setMessagesValue(list);

        const url = `${apiBaseURL}/chat_message/${encodeURIComponent(chatMeta.value.chatId)}`;
        const payload: Record<string, any> = {
          message: text,
          re_chat: false,
          stream: true
        };
        if (selectedModel.value) payload.model = selectedModel.value;

        const response = await fetch(url, {
          method: 'POST',
          headers: { ...authHeaders(), 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!response.body) throw new Error('ReadableStream not supported.');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
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
                const nextList = [...getMessagesValue()];
                const target = nextList.find(m => m.id === botMessageId);
                if (target) target.text = complete.trim();
                setMessagesValue(nextList);
              }
            } catch (err) {
              console.error('chunk parse error:', err, line);
            }
          }
        }
      } catch (err) {
        console.error(err);
        const list = [...getMessagesValue()];
        list.push({
          id: Date.now() + Math.floor(Math.random() * 1000),
          text: 'Sorry, I could not process your request.',
          sender: 'bot'
        });
        setMessagesValue(list);
      } finally {
        loading.value = false;
        inputText.value = '';
        clearImageState();
      }
      showExampleQuestions.value = false;
      localStorage.setItem('hasSentMessage', 'true');
      editingMessageId.value = null;
    };

    const fillExample = (example: string) => { inputText.value = example; };

    const openFullscreen = async () => {
      setChatOpen(false);
      const query = activeSessionId.value === 'floating-assistant'
        ? { shared: '1' }
        : { session: activeSessionId.value };
      await router.push({ path: '/AIYingying', query });
    };

    const writeClipboard = async (text: string) => {
      if (!text) return;
      try {
        await navigator.clipboard.writeText(text);
        return;
      } catch {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', 'true');
        textarea.style.position = 'absolute';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }
    };

    const copyMessage = async (msg: any, index: number) => {
      const main = typeof msg.text === 'string' ? msg.text : '';
      const evidence = typeof msg.evidence === 'string' ? msg.evidence : '';
      const text = evidence ? `${main}\n\nSearch results:\n${evidence}` : main;
      await writeClipboard(text);
      const id = (msg.id ?? index) as number;
      copiedId.value = id;
      window.setTimeout(() => {
        if (copiedId.value === id) copiedId.value = null;
      }, 1200);
    };

    const editMessage = (msg: any) => {
      if (!msg || typeof msg.text !== 'string') return;
      inputText.value = msg.text;
      editingMessageId.value = msg.id ?? null;
      nextTick(() => chatInput.value?.focus());
    };

    const isLatestUserMessage = (msg: any) => {
      const lastUser = [...messagesSnapshot.value].reverse().find(m => m.sender === 'user');
      if (!lastUser) return false;
      return msg?.id === lastUser.id;
    };

    const isLatestBotMessage = (msg: any) => {
      const lastBot = [...messagesSnapshot.value].reverse().find(m => (m.sender || 'bot') === 'bot');
      if (!lastBot) return false;
      return msg?.id === lastBot.id;
    };

    const regenerateFromMessage = async (msg: any) => {
      if (!isLatestBotMessage(msg)) return;
      const list = [...getMessagesValue()];
      const targetIndex = list.findIndex(m => m?.id === msg?.id);
      let userIndex = -1;
      if (targetIndex >= 0) {
        for (let i = targetIndex; i >= 0; i -= 1) {
          if (list[i]?.sender === 'user' && list[i]?.text) {
            userIndex = i;
            break;
          }
        }
      }
      if (userIndex < 0) {
        userIndex = list
          .map((m, idx) => ({ m, idx }))
          .filter(item => item.m?.sender === 'user')
          .map(item => item.idx)
          .pop() ?? -1;
      }
      if (userIndex < 0) return;
      const userMsg = list[userIndex];
      if (!userMsg?.text) return;
      setMessagesValue(list.slice(0, userIndex + 1));
      loading.value = true;
      await chat.value.sendMessage({
        skipUserPush: true,
        overrideText: userMsg.text,
        model: selectedModel.value
      });
      loading.value = false;
    };

    return {
      element, startDrag, chat,
      activeSessionId, sessionOptions, selectedModel, modelOptions,
      toggleChat, sendMessage, previewImage,
      renderedMessages, safeMessages, chatContent,
      loading, fillExample, showExampleQuestions, exampleWrap,
      aiTip, inputPlaceholder, inputText,
      chatImagePreview,
      copyMessage, copiedId, openFullscreen,
      createNewSession,
      editMessage, chatInput, isLatestUserMessage,
      isLatestBotMessage, regenerateFromMessage,
      isAiPage,
      showLoading,
      showSessionSelect,
      showModelSelect,
      toggleSessionSelect,
      toggleModelSelect,
      selectSession,
      selectModel,
      headerRef
    };
  }
});
</script>

<style>
/* ——AI 提示条—— */
#ai-tip{
  display:flex;
  align-items:center;
  gap:6px;
  font-size:10px;
  color:var(--app-text-muted);
  background:var(--app-surface-2);
  border-left:3px solid var(--app-accent);
  padding:4px 6px;
  margin:4px 10px 2px 10px;
  border-radius:6px;
  position: relative;
}
.ai-tip-text{
  line-height:1.2;
  display:flex;
  align-items:center;
  gap:6px;
}
.ai-tip-icon{
  width:16px;
  height:16px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border-radius:50%;
  font-size:11px;
  font-weight:700;
  background:#f59e0b;
  color:#fff;
  flex:0 0 auto;
}

/* ——消息区—— */
#chat-content{
  flex:1 1 auto;
  min-height:0;
  overflow-y:auto;
  padding:8px 10px 8px;
}
.message-container{ display:flex; align-items:flex-start; gap:8px; margin:8px 8px 4px; }
.message-container.user{ flex-direction:row-reverse; }
.avatar{ width:32px; height:32px; flex:0 0 32px; border-radius:50%; object-fit:cover; object-position:center; display:block; margin-top:2px; }
.message{
  flex:1 1 auto;
  max-width:none;
  padding:6px 34px 6px 8px;
  border-radius:10px;
  line-height:1.4;
  word-break:break-word;
  background:#f5f6fb;
  color:var(--app-text);
  border:1px solid #e2e6f0;
  position:relative;
}
.message-container.bot .message{
  background:#f5f6fb;
  border-color:#e2e6f0;
}
.message-container.user .message{
  background:#3e63d1;
  color:#fff;
  border-color:#3e63d1;
}
.message-image{
  display:block;
  max-width:100%;
  max-height:220px;
  height:auto;
  border-radius:8px;
  margin-top:6px;
}
.message-actions{
  position:absolute;
  top:6px;
  right:6px;
  display:flex;
  gap:6px;
  opacity:0;
  transition:opacity 0.2s ease;
}
.message-action{
  font-size:11px;
  padding:2px 6px;
  border-radius:10px;
  border:1px solid var(--app-border);
  background:var(--app-surface);
  color:var(--app-text-muted);
  cursor:pointer;
}
.message:hover .message-actions{ opacity:1; }
.message-copied{
  position:absolute;
  top:28px;
  right:6px;
  font-size:11px;
  color:var(--app-text-muted);
}
.loading-dots{
  display:block;
  min-height:42px;
  letter-spacing:2px;
  color:var(--app-text-muted);
}

.rag-actions{
  display:inline-flex;
  align-items:center;
  gap:6px;
  margin-left:auto;
}
.rag-action{
  width:22px;
  height:22px;
  padding:0;
  border-radius:50%;
  display:inline-flex;
  align-items:center;
  justify-content:center;
}
.rag-action svg{
  width:14px;
  height:14px;
  fill:currentColor;
}
.rag-copied-badge{
  font-size:10px;
  padding:2px 6px;
  border-radius:999px;
  border:1px solid var(--app-border);
  background:var(--app-surface);
  color:var(--app-text-muted);
}

@media (max-width: 600px) {
  .message-actions { opacity: 1; }
}

/* ——RAG 证据卡片（默认折叠 + 紧凑 + 高度限制）—— */
#chat-box .evidence-card {
  max-width: calc(100% - 40px);
  margin: 0 8px 6px 40px;     /* align with message content */
}
#chat-box .evidence-card details {
  background: transparent;
  border: none;
  padding: 0;
}
#chat-box .evidence-card summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  cursor: pointer;
  list-style: none;
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text-muted);
  line-height: 1.2;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 999px;
  padding: 4px 10px;
}
#chat-box .evidence-card summary::-webkit-details-marker { display: none; }
/* 折叠内容更紧凑并限制高度 */
#chat-box .evidence-body {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.35;
  max-height: 140px;            /* 👈 控制最大高度 */
  overflow: auto;
}
#chat-box .evidence-body :where(img){ max-width:100%; border-radius:6px;height: 150px; }

/* ——示例问题（父容器横向滚动）—— */
#chat-input-container{
  display:flex;
  flex-direction:column;
  gap:6px;
  align-items:stretch;
}
#example-questions{
  width:100%;
  overflow-x:auto;
  overflow-y:hidden;
  padding:4px 8px;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:none;
}
#example-questions::-webkit-scrollbar{ display:none; }

#question-slider{
  display:inline-flex;
  flex-wrap:nowrap;
  gap:8px;
  white-space:nowrap;
  min-width:max-content;
}

/* 更小更紧凑的按钮 */
#question-slider button{
  flex:0 0 auto;
  padding:6px 10px;
  font-size:12px;
  line-height:1;
  font-weight:500;
  color:#fff;
  background:linear-gradient(135deg,var(--app-accent),var(--app-accent-strong));
  border:1px solid var(--app-accent-strong);
  border-radius:16px;
  cursor:pointer;
  transition:all .2s ease;
  white-space:nowrap;
}
#question-slider button:hover{
  filter:brightness(0.95);
  transform:translateY(-1px);
}

/* ——输入区—— */
#input-area{ display:flex; gap:6px; align-items:center; width:100%; }
#chat-input{
  flex-grow:1;
  padding:6px 10px;
  font-size:13px;
  border:1px solid var(--app-border);
  border-radius:12px;
  outline:none;
  background:var(--app-surface-2);
  color:var(--app-text);
}
#chat-input::placeholder{ color:var(--app-text-faint); }
#chat-input:disabled{
  opacity:0.6;
  cursor:not-allowed;
}
#send-button{
  background:var(--app-accent);
  color:#fff;
  padding:6px 8px;
  border:1px solid var(--app-accent);
  border-radius:12px;
  cursor:pointer;
  transition:all .3s ease;
  min-width:30px;
  height:30px;
}
#new-chat-button{
  background:transparent;
  color:var(--app-text-muted);
  padding:0;
  border:1px solid var(--app-border);
  border-radius:50%;
  width:30px;
  height:30px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  cursor:pointer;
}
#new-chat-button svg{
  width:16px;
  height:16px;
  stroke:currentColor;
}
#send-button:hover{ filter:brightness(0.95); }
#send-button:disabled{
  opacity:0.6;
  cursor:not-allowed;
}

:root[data-theme="dark"] #chat-box,
html.dark #chat-box {
  background-color: #12151c;
  border-color: rgba(255, 255, 255, 0.08);
}

:root[data-theme="dark"] #chat-header,
html.dark #chat-header {
  background-color: #3f66d0;
}

:root[data-theme="dark"] #ai-tip,
html.dark #ai-tip {
  background: #1f2532;
  color: #cdd4df;
  border-left-color: #4c71d8;
}

:root[data-theme="dark"] .message-container.bot .message,
html.dark .message-container.bot .message {
  background: #1c2230;
  border-color: rgba(255, 255, 255, 0.12);
}

:root[data-theme="dark"] .message-container.user .message,
html.dark .message-container.user .message {
  background: #365bc4;
  border-color: #365bc4;
}

:root[data-theme="dark"] #chat-input,
html.dark #chat-input {
  background: #171c26;
  border-color: rgba(255, 255, 255, 0.14);
  color: #e0e6f0;
}

:root[data-theme="dark"] #chat-input::placeholder,
html.dark #chat-input::placeholder {
  color: #8a94a6;
}

:root[data-theme="dark"] #send-button,
html.dark #send-button {
  background: #3f66d0;
  border-color: #3f66d0;
}

:root[data-theme="dark"] #chat-content::-webkit-scrollbar,
html.dark #chat-content::-webkit-scrollbar {
  width: 10px;
}

:root[data-theme="dark"] #chat-content::-webkit-scrollbar-thumb,
html.dark #chat-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.22);
  border-radius: 8px;
}

:root[data-theme="dark"] #chat-content::-webkit-scrollbar-track,
html.dark #chat-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8px;
}

</style>
