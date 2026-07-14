<template>
  <div id="bot-container" ref="element" v-if="!isAiPage">
    <button
      id="bot-icon"
      v-show="!chat.isChatOpen"
      type="button"
      aria-label="Open ENSURE Assistant"
      title="Open ENSURE Assistant"
      @click="toggleChat"
      @mousedown="startDrag"
    >
      <img src="/bot-image.png" alt="Bot Icon" @dragstart.prevent />
    </button>

    <div id="chat-box" v-if="chat.isChatOpen">
      <div id="chat-header" ref="headerRef" @mousedown="startDrag">
        <div class="header-left">
          <div class="chat-header-heading">
            <span class="chat-header-title">ENSURE Assistant</span>
            <span class="chat-header-status">
              <span class="chat-header-status-dot" aria-hidden="true"></span>
              Grounded in ENSURE
            </span>
          </div>
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
              @mousedown.stop
            >
              <button
                class="header-menu-item header-menu-item--new"
                type="button"
                :disabled="loading"
                @click.stop="createNewSession"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 5v14m-7-7h14"></path>
                </svg>
                New conversation
              </button>
              <span class="header-menu-divider" aria-hidden="true"></span>
              <button
                v-for="session in sessionOptions"
                :key="session.id"
                class="header-menu-item"
                type="button"
                role="option"
                :disabled="loading"
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
                <path d="M4 7h10m4 0h2m-6-3v6M4 17h2m4 0h10m-12-3v6"></path>
              </svg>
            </button>
            <div
              v-if="showModelSelect"
              class="header-menu"
              role="listbox"
              aria-label="Select model"
              @mousedown.stop
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
            title="Close"
          >
            <svg class="close-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18"></path>
            </svg>
          </button>
        </div>
      </div>

      <details id="ai-tip">
        <summary>
          <span class="ai-tip-icon" aria-hidden="true">i</span>
          <span>AI answers may be inaccurate</span>
          <span class="ai-tip-more">Details</span>
        </summary>
        <p>{{ aiTip }}</p>
      </details>

      <div id="chat-content" ref="chatContent">
        <!-- 主消息流：证据块跟在每条 bot 消息后 -->
        <template v-for="(msg, i) in safeMessages" :key="(msg.id ?? 'msg') + '-' + i">
          <div
            :class="[
              'message-container',
              msg.sender || 'bot',
              { 'is-greeting': (msg.sender || 'bot') === 'bot' && isGreeting(msg.text || msg.textPlain || '') }
            ]"
          >
            <!-- 头像 -->
            <img
              v-if="(msg.sender || 'bot') === 'bot'"
              src="/bot-image.png"
              class="avatar"
              alt=""
            />
            <!-- 气泡 -->
            <div class="message">
              <span v-html="msg.textHtml || msg.text || ''" @click="handleEvidenceClick"></span>
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
            v-if="(msg.sender || 'bot') === 'bot' && (msg.evidenceHtml || msg.evidenceSources?.length)"
            class="evidence-card"
          >
            <details>
              <summary>
                <span>Evidence &amp; sources</span>
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
              <div v-if="msg.evidenceHtml" class="evidence-body" v-html="msg.evidenceHtml"></div>
              <div v-if="msg.evidenceSources?.length" class="evidence-source-list">
                <article
                  v-for="source in msg.evidenceSources"
                  :id="sourceTargetId(msg, source)"
                  :key="source.ref"
                  class="evidence-source"
                >
                  <div class="evidence-source-heading">
                    <span class="evidence-source-ref">[{{ source.ref }}]</span>
                    <strong>{{ source.title }}</strong>
                  </div>
                  <div v-if="source.table || source.ensureId || source.pmid || source.doi" class="evidence-source-meta">
                    <span v-if="source.table">Table: {{ source.table }}</span>
                    <span v-if="source.ensureId">ENSURE_ID: {{ source.ensureId }}</span>
                    <span v-if="source.pmid">PMID: {{ source.pmid }}</span>
                    <span v-if="source.doi">DOI: {{ source.doi }}</span>
                  </div>
                  <p v-if="source.snippet">{{ source.snippet }}</p>
                  <div v-if="source.links?.length" class="evidence-source-links">
                    <a
                      v-for="link in source.links"
                      :key="link.href"
                      :href="link.href"
                      :target="link.external ? '_blank' : undefined"
                      :rel="link.external ? 'noopener noreferrer' : undefined"
                    >{{ link.label }}</a>
                  </div>
                </article>
              </div>
            </details>
          </div>
        </template>

        <!-- Loading -->
        <div v-if="showLoading" class="message-container bot">
          <img src="/bot-image.png" class="avatar" alt="" />
          <div class="message message--loading">
            <div class="loading-card">
              <div class="loading-badge">Processing</div>
              <div class="loading-status">{{ progressStatus || 'Working on your answer' }}</div>
              <p v-if="progressDetail" class="loading-detail">{{ progressDetail }}</p>
              <div v-if="visibleProgressJudges.length" class="loading-tools loading-tools--judge">
                <div class="loading-tools-title">Judge review</div>
                <div
                  v-for="item in visibleProgressJudges"
                  :key="item.id"
                  class="loading-tool-item"
                >
                  <span class="loading-tool-name">{{ item.verdict || 'judge' }}</span>
                  <span class="loading-tool-summary">{{ item.summary }}</span>
                </div>
              </div>
              <div v-if="progressDraftPreview" class="loading-tools loading-tools--draft">
                <div class="loading-tools-title">{{ progressDraftPreview.label }}</div>
                <div class="loading-tool-item loading-tool-item--draft">
                  <span class="loading-tool-summary loading-tool-summary--draft">{{ progressDraftPreview.content }}</span>
                </div>
              </div>
              <div v-if="visibleProgressTools.length" class="loading-tools">
                <div class="loading-tools-title">Tool activity</div>
                <div
                  v-for="item in visibleProgressTools"
                  :key="item.id"
                  class="loading-tool-item"
                >
                  <span class="loading-tool-name">{{ item.tool }}</span>
                  <span class="loading-tool-summary">{{ item.summary }}</span>
                </div>
              </div>
              <div v-else class="loading-pulse" aria-hidden="true">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <div id="example-questions" v-if="showExampleQuestions">
          <p class="example-questions-label">Try asking</p>
          <div id="question-slider">
            <button @click="fillExample('What are the main features of ENSURE?')">Explore ENSURE features</button>
            <button @click="fillExample('What is suppressor tRNA?')">What is suppressor tRNA?</button>
            <button @click="fillExample('How can I find evidence by PMID in ENSURE?')">Find evidence by PMID</button>
            <button @click="fillExample('Compare natural and engineered suppressor tRNA.')">Compare sup-tRNA types</button>
          </div>
        </div>
      </div>

      <div id="chat-input-container">
        <div class="composer-toolbar">
          <div class="answer-mode-switch" role="group" aria-label="Answer mode">
            <button
              v-for="mode in answerModes"
              :key="mode.value"
              class="answer-mode-option"
              :class="{ active: chatMode === mode.value }"
              type="button"
              :disabled="loading"
              @click="chatMode = mode.value"
            >{{ mode.label }}</button>
          </div>
        </div>
        <div id="input-area">
          <input
            id="chat-input"
            v-model="inputText"
            @keypress.enter="sendMessage"
            :placeholder="inputPlaceholder"
            ref="chatInput"
          />
          <button
            @click="handlePrimaryAction"
            id="send-button"
            :class="{ 'is-generating': loading }"
            :aria-label="loading ? 'Stop generating' : 'Send message'"
            :title="loading ? 'Stop generating' : 'Send message'"
          >
            <svg v-if="loading" viewBox="0 0 24 24" aria-hidden="true">
              <rect x="5.5" y="5.5" width="13" height="13" rx="3.4" fill="currentColor"></rect>
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 12h12.5" fill="none" stroke="currentColor" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"></path>
              <path d="M12 5.5 18.5 12 12 18.5" fill="none" stroke="currentColor" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"></path>
            </svg>
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
import { fetchChatModelConfig, resolveChatModelSelection } from '@/utils/chatConfig';
import { chatModeRequestOptions, persistChatMode, readChatMode, type ChatMode } from '@/utils/chatMode';
import { CHAT_GREETING, isChatGreeting } from '@/utils/chatGreeting';
import {
  evidenceLinks,
  evidenceTargetId,
  handleEvidenceReferenceClick,
  linkEvidenceCitations,
  normalizeEvidenceSources
} from '@/utils/chatEvidence';

export default defineComponent({
  name: 'BotComponent',
  setup() {
    const apiKey = '';

    const { element, startDrag } = useDraggable();
    const activeSessionId = ref(
      localStorage.getItem('ai_chat_active_session') || 'floating-assistant'
    );
    const chat = ref(useChat(apiKey, { key: activeSessionId.value }));
    const sessionOptions = ref<Array<{ id: string; title: string }>>([]);
    const modelOptions = ref<string[]>([]);
    const answerModes: Array<{ value: ChatMode; label: string }> = [
      { value: 'fast', label: 'Fast answer' },
      { value: 'deep', label: 'Deep research' }
    ];
    const chatMode = ref<ChatMode>(readChatMode());
    const selectedModel = ref('');
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
      if (loading.value) return;
      activeSessionId.value = id;
      showSessionSelect.value = false;
    };
    const selectModel = (model: string) => {
      selectedModel.value = model;
      showModelSelect.value = false;
    };
    const toggleChat = () => {
      const next = !getChatOpen();
      if (!next) {
        showSessionSelect.value = false;
        showModelSelect.value = false;
      }
      setChatOpen(next);
    };
    const previewImage = (event: Event) => chat.value.previewImage(event);
    const { renderMarkdown } = useMarkdown();
    const router = useRouter();
    const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';

    const renderedMessages = ref<any[]>([]);
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
        items.unshift({ id: 'floating-assistant', title: 'ENSURE Assistant' });
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
        sessionOptions.value = [{ id: 'floating-assistant', title: 'ENSURE Assistant' }];
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

    const authHeaders = () => ({ accept: 'application/json' });
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
      if (loading.value) return;
      showSessionSelect.value = false;
      showModelSelect.value = false;
      showExampleQuestions.value = true;
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
        if (Array.isArray(parsed?.messages)) setMessagesValue(parsed.messages);
      } catch {
        // ignore malformed cache
      }
      if (!getMessagesValue().length) {
        setMessagesValue([
          { id: 1, sender: 'bot', text: CHAT_GREETING }
        ]);
      }
      showExampleQuestions.value = !getMessagesValue().some(
        message => message?.sender === 'user' && String(message?.text || '').trim()
      );
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
      'Verify important claims against the linked ENSURE records and primary literature.'
    );
    const inputPlaceholder = computed(() => 'Type a message...');
    const copiedId = ref<number | null>(null);
    const chatInput = ref<HTMLInputElement | null>(null);
    const editingMessageId = ref<number | null>(null);
    const loading = computed(() => {
      const raw: any = chat.value.isStreaming;
      return raw && typeof raw === 'object' && 'value' in raw ? !!raw.value : !!raw;
    });
    const progressStatus = computed(() => {
      const raw: any = chat.value.progressStatus;
      if (raw && typeof raw === 'object' && 'value' in raw) {
        return String(raw.value || '');
      }
      return typeof raw === 'string' ? raw : '';
    });
    const progressDetail = computed(() => {
      const raw: any = chat.value.progressDetail;
      if (raw && typeof raw === 'object' && 'value' in raw) {
        return String(raw.value || '');
      }
      return typeof raw === 'string' ? raw : '';
    });
    const progressToolTrace = computed(() => {
      const raw: any = chat.value.progressToolTrace;
      if (raw && typeof raw === 'object' && 'value' in raw && Array.isArray(raw.value)) {
        return raw.value;
      }
      return Array.isArray(raw) ? raw : [];
    });
    const progressJudgeTrace = computed(() => {
      const raw: any = chat.value.progressJudgeTrace;
      if (raw && typeof raw === 'object' && 'value' in raw && Array.isArray(raw.value)) {
        return raw.value;
      }
      return Array.isArray(raw) ? raw : [];
    });
    const progressDraftPreview = computed(() => {
      const raw: any = chat.value.progressDraftPreview;
      if (raw && typeof raw === 'object' && 'value' in raw) {
        return raw.value || null;
      }
      return raw || null;
    });
    const isAiPage = computed(() => {
      const path = router.currentRoute.value?.path || '';
      return path.toLowerCase().startsWith('/aiyingying');
    });

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
      const chatConfig = await fetchChatModelConfig();
      const selection = resolveChatModelSelection(chatConfig);
      modelOptions.value = selection.modelOptions;
      selectedModel.value = selection.activeModel;
      if (selection.activeModel) {
        localStorage.setItem('ai_chat_model', selection.activeModel);
      } else {
        localStorage.removeItem('ai_chat_model');
      }
      window.addEventListener('storage', loadSessions);
      window.addEventListener('click', handleDocClick);
    });
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
    const getMessagesValue = () => {
      const raw: any = chat.value.messages;
      if (raw && typeof raw === 'object' && 'value' in raw && Array.isArray(raw.value)) {
        return raw.value;
      }
      return Array.isArray(raw) ? raw : [];
    };
    const setMessagesValue = (next: any[]) => {
      const raw: any = chat.value.messages;
      if (raw && typeof raw === 'object' && 'value' in raw) {
        raw.value = Array.isArray(next) ? next : [];
        return;
      }
      (chat.value as any).messages = Array.isArray(next) ? next : [];
    };
    const chatImagePreview = computed(() => {
      const raw: any = chat.value.imagePreview;
      return raw && typeof raw === 'object' && 'value' in raw ? raw.value : raw;
    });

    watch(activeSessionId, (nextId) => {
      localStorage.setItem(activeSessionStorageKey, nextId);
      setMessagesValue([]);
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
    watch(chatMode, persistChatMode, { immediate: true });
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

    const isGreeting = (text: string) => isChatGreeting(text);

    const buildHistoryPayload = (sourceMessages: any[], options: { excludeMessageId?: number | null } = {}) => {
      return (sourceMessages || [])
        .filter((message) => {
          if (!message) return false;
          if (options.excludeMessageId && message.id === options.excludeMessageId) return false;
          return message.sender === 'user' || message.sender === 'bot' || message.sender === 'assistant';
        })
        .map((message) => {
          const raw =
            typeof message?.textPlain === 'string' && message.textPlain.trim()
              ? message.textPlain
              : (typeof message?.text === 'string' ? splitSearchResult(message.text).main : '');
          const content = String(raw || '').trim();
          const role = message?.sender === 'user' ? 'user' : 'assistant';
          return { role, content };
        })
        .filter((item) => item.content && !(item.role === 'assistant' && isGreeting(item.content)))
        .slice(-14)
        .map((item) => ({
          role: item.role as 'user' | 'assistant',
          content: item.content.slice(0, 2400)
        }));
    };

    /* -------- 渲染/派生 -------- */
    const safeMessages = computed<any[]>(() =>
      Array.isArray(renderedMessages.value)
        ? renderedMessages.value.filter((msg: any) => {
            if (!msg) return false;
            const sender = msg.sender ?? msg.role ?? 'bot';
            const hasContent = Boolean(
              msg.text || msg.textHtml || msg.content || msg.image || msg.evidenceHtml
            );
            return !(loading.value && sender === 'bot' && !hasContent);
          })
        : []
    );
    const messagesSnapshot = computed(() => getMessagesValue());

    const showLoading = computed(() => {
      if (!loading.value) return false;
      const list = messagesSnapshot.value;
      const last = list[list.length - 1];
      if (!last) return true;
      const sender = last.sender ?? last.role ?? 'bot';
      const hasContent = Boolean(last.text || last.textHtml || last.content || last.image);
      return sender !== 'bot' || !hasContent;
    });
    const visibleProgressTools = computed(() => progressToolTrace.value.slice(-3));
    const visibleProgressJudges = computed(() => progressJudgeTrace.value.slice(-3));

    const renderToken = ref(0);
    watch(
      messagesSnapshot,
      async (newVal) => {
        const token = ++renderToken.value;
        if (!Array.isArray(newVal)) { renderedMessages.value = []; return; }
        const rendered = await Promise.all(
          newVal.map(async (m: any, index: number) => {
            const msg: any = { ...m };
            msg.sender ??= msg.role ?? 'bot';
            const messageId = msg.id ?? index;
            const sources = normalizeEvidenceSources(msg.sources);

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
              msg.textHtml = await renderMarkdown(linkEvidenceCitations(String(msg.text), messageId, sources));
            } else {
              msg.textHtml = msg.textHtml || '';
            }
            if (msg.evidence) {
              msg.evidenceHtml = await renderMarkdown(String(msg.evidence));
            } else {
              msg.evidenceHtml = msg.evidenceHtml || '';
            }
            msg.evidenceSources = sources.map(source => ({
              ...source,
              links: evidenceLinks(source)
            }));
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
      if (loading.value) return;
      const text = inputText.value.trim();
      if (!text) return;
      const sourceMessages = [...getMessagesValue()];
      let historySource = sourceMessages;

      if (draftSessionId.value && activeSessionId.value === draftSessionId.value) {
        const hasUser = sourceMessages.some(
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
        const list = [...getMessagesValue()];
        const index = list.findIndex(m => m.id === editingMessageId.value);
        if (index >= 0) {
          historySource = sourceMessages.slice(0, index);
          list[index].text = text;
          list.splice(index + 1);
          setMessagesValue(list);
        }
      }

      inputText.value = '';
      const result = await chat.value.sendMessage({
        skipUserPush: !!editingMessageId.value,
        overrideText: text,
        model: selectedModel.value,
        history: buildHistoryPayload(historySource, { excludeMessageId: editingMessageId.value }),
        ...chatModeRequestOptions(chatMode.value)
      });
      showExampleQuestions.value = false;
      if (!result?.aborted) {
        editingMessageId.value = null;
      }
      clearImageState();
    };

    const stopGenerating = () => {
      if (!loading.value) return;
      chat.value.stopMessage();
      editingMessageId.value = null;
    };

    const handlePrimaryAction = () => {
      if (loading.value) {
        stopGenerating();
        return;
      }
      void sendMessage();
    };

    const fillExample = (example: string) => { inputText.value = example; };
    const handleEvidenceClick = (event: MouseEvent) => handleEvidenceReferenceClick(event);
    const sourceTargetId = (message: any, source: any) =>
      evidenceTargetId(message?.id ?? 'message', source?.ref ?? '1');

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
      const historySource = list.slice(0, userIndex);
      setMessagesValue(list.slice(0, userIndex + 1));
      const result = await chat.value.sendMessage({
        skipUserPush: true,
        overrideText: userMsg.text,
        model: selectedModel.value,
        history: buildHistoryPayload(historySource),
        ...chatModeRequestOptions(chatMode.value)
      });
      if (!result?.aborted) {
        editingMessageId.value = null;
      }
    };

    return {
      element, startDrag, chat,
      activeSessionId, sessionOptions, selectedModel, modelOptions,
      answerModes, chatMode,
      toggleChat, sendMessage, previewImage,
      renderedMessages, safeMessages, chatContent,
      loading, fillExample, showExampleQuestions,
      aiTip, inputPlaceholder, inputText,
      progressStatus, progressDetail, progressDraftPreview, visibleProgressTools, visibleProgressJudges,
      chatImagePreview,
      copyMessage, copiedId, openFullscreen,
      createNewSession,
      editMessage, chatInput, isLatestUserMessage,
      isLatestBotMessage, regenerateFromMessage,
      handleEvidenceClick, sourceTargetId,
      handlePrimaryAction, stopGenerating,
      isAiPage,
      showLoading,
      showSessionSelect,
      showModelSelect,
      toggleSessionSelect,
      toggleModelSelect,
      selectSession,
      selectModel,
      headerRef,
      isGreeting
    };
  }
});
</script>

<style scoped>
#chat-box #ai-tip {
  flex: 0 0 auto;
  margin: 7px 12px 0;
  color: var(--app-text-muted);
  font-size: 11px;
}

#chat-box #ai-tip summary {
  display: flex;
  align-items: center;
  gap: 7px;
  min-height: 25px;
  padding: 2px 1px;
  cursor: pointer;
  list-style: none;
}

#chat-box #ai-tip summary::-webkit-details-marker {
  display: none;
}

#chat-box #ai-tip summary:hover {
  color: var(--app-text);
}

#chat-box .ai-tip-icon {
  display: inline-flex;
  flex: 0 0 15px;
  align-items: center;
  justify-content: center;
  width: 15px;
  height: 15px;
  color: var(--app-text-faint);
  font-size: 10px;
  font-weight: 800;
  border: 1px solid var(--app-border);
  border-radius: 50%;
}

#chat-box .ai-tip-more {
  margin-left: auto;
  color: var(--app-text-faint);
  font-size: 10px;
  font-weight: 650;
}

#chat-box #ai-tip[open] .ai-tip-more {
  color: var(--app-accent-strong);
}

#chat-box #ai-tip p {
  margin: 0 0 3px 22px;
  padding: 1px 0 7px;
  color: var(--app-text-faint);
  font-size: 10px;
  line-height: 1.45;
  border-bottom: 1px solid var(--app-border-light);
}

#chat-box #chat-content {
  flex: 1 1 auto;
  min-height: 0;
  padding: 9px 12px 12px;
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-color: color-mix(in srgb, var(--app-text) 22%, transparent) transparent;
  scrollbar-width: thin;
}

#chat-box #chat-content::-webkit-scrollbar {
  width: 7px;
}

#chat-box #chat-content::-webkit-scrollbar-track {
  background: transparent;
}

#chat-box #chat-content::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--app-text) 20%, transparent);
  border: 2px solid transparent;
  border-radius: 999px;
  background-clip: padding-box;
}

#chat-box .message-container {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 7px 0;
}

#chat-box .message-container.user {
  justify-content: flex-end;
}

#chat-box .avatar {
  display: block;
  flex: 0 0 28px;
  width: 28px;
  height: 28px;
  margin-top: 1px;
  object-fit: cover;
  object-position: center;
  border: 1px solid var(--app-border-light);
  border-radius: 50%;
}

#chat-box .message {
  position: relative;
  min-width: 0;
  color: var(--app-text);
  font-size: 13px;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

#chat-box .message-container.bot .message {
  flex: 1 1 auto;
  padding: 2px 30px 2px 0;
  background: transparent;
  border: 0;
  border-radius: 0;
}

#chat-box .message-container.user .message {
  flex: 0 1 84%;
  max-width: 84%;
  padding: 8px 30px 8px 10px;
  background: color-mix(in srgb, var(--app-accent) 8%, var(--app-surface-2));
  border: 1px solid color-mix(in srgb, var(--app-accent) 18%, var(--app-border));
  border-radius: 12px 12px 4px;
}

#chat-box .message-container.is-greeting {
  margin-top: 10px;
}

#chat-box .message-container.is-greeting .message {
  padding-top: 0;
  color: var(--app-text);
  font-size: 14px;
  line-height: 1.55;
}

#chat-box .message :deep(p) {
  margin: 0 0 0.65em;
}

#chat-box .message :deep(p:last-child) {
  margin-bottom: 0;
}

#chat-box .message :deep(a) {
  color: var(--app-accent-strong);
  font-weight: 700;
  text-decoration: none;
}

#chat-box .message :deep(ul),
#chat-box .message :deep(ol) {
  margin: 0.45em 0;
  padding-left: 1.35em;
}

#chat-box .message-image {
  display: block;
  width: auto;
  max-width: 100%;
  height: auto;
  max-height: 210px;
  margin-top: 7px;
  border: 1px solid var(--app-border-light);
  border-radius: 8px;
}

#chat-box .message-actions {
  position: absolute;
  top: 1px;
  right: 1px;
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 140ms ease;
}

#chat-box .message:hover .message-actions,
#chat-box .message:focus-within .message-actions {
  opacity: 1;
}

#chat-box .message-action {
  appearance: none;
  min-height: 22px;
  margin: 0;
  padding: 2px 6px;
  color: var(--app-text-faint);
  font-size: 10px;
  font-weight: 650;
  cursor: pointer;
  background: var(--app-surface);
  border: 0;
  border-radius: 6px;
}

#chat-box .message-action:hover {
  color: var(--app-text);
  background: var(--app-surface-2);
  border-color: transparent;
}

#chat-box .message-copied {
  position: absolute;
  top: 25px;
  right: 2px;
  color: var(--app-text-faint);
  font-size: 10px;
}

#chat-box .message--loading {
  padding: 9px 10px;
  background: var(--app-surface-2) !important;
  border: 1px solid var(--app-border-light) !important;
  border-radius: 10px !important;
}

#chat-box .loading-card {
  display: grid;
  gap: 7px;
}

#chat-box .loading-badge {
  width: max-content;
  padding: 3px 7px;
  color: var(--app-accent-strong);
  font-size: 9px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: color-mix(in srgb, var(--app-accent) 11%, transparent);
  border-radius: 999px;
}

#chat-box .loading-status {
  color: var(--app-text);
  font-size: 12px;
  font-weight: 700;
}

#chat-box .loading-detail {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 11px;
  line-height: 1.45;
}

#chat-box .loading-tools {
  display: grid;
  gap: 5px;
}

#chat-box .loading-tools-title {
  color: var(--app-text-faint);
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

#chat-box .loading-tool-item {
  display: grid;
  gap: 3px;
  padding: 6px 7px;
  background: color-mix(in srgb, var(--app-text) 4%, transparent);
  border: 1px solid var(--app-border-light);
  border-radius: 8px;
}

#chat-box .loading-tool-name {
  color: var(--app-text);
  font-size: 10px;
  font-weight: 700;
}

#chat-box .loading-tool-summary {
  color: var(--app-text-muted);
  font-size: 10px;
  line-height: 1.4;
}

#chat-box .loading-tool-item--draft {
  max-height: 9rem;
  overflow: auto;
}

#chat-box .loading-tool-summary--draft {
  white-space: pre-wrap;
}

#chat-box .loading-pulse {
  display: flex;
  align-items: center;
  gap: 5px;
  min-height: 12px;
}

#chat-box .loading-pulse span {
  width: 6px;
  height: 6px;
  background: var(--app-accent);
  border-radius: 50%;
  opacity: 0.28;
  animation: botPulse 1.1s ease-in-out infinite;
}

#chat-box .loading-pulse span:nth-child(2) {
  animation-delay: 0.16s;
}

#chat-box .loading-pulse span:nth-child(3) {
  animation-delay: 0.32s;
}

@keyframes botPulse {
  0%,
  80%,
  100% {
    opacity: 0.28;
    transform: translateY(0);
  }

  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

#chat-box .evidence-card {
  max-width: calc(100% - 36px);
  margin: 0 0 7px 36px;
}

#chat-box .evidence-card details {
  padding: 0;
  background: transparent;
  border: 0;
}

#chat-box .evidence-card summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 7px;
  min-height: 28px;
  padding: 4px 8px;
  color: var(--app-text-muted);
  font-size: 11px;
  font-weight: 650;
  line-height: 1.25;
  cursor: pointer;
  list-style: none;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border-light);
  border-radius: 8px;
}

#chat-box .evidence-card summary::-webkit-details-marker {
  display: none;
}

#chat-box .rag-actions {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: auto;
}

#chat-box .rag-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  padding: 0;
}

#chat-box .rag-action svg {
  width: 13px;
  height: 13px;
  fill: currentColor;
}

#chat-box .rag-copied-badge {
  padding: 2px 5px;
  color: var(--app-text-faint);
  font-size: 9px;
  background: var(--app-surface);
  border-radius: 999px;
}

#chat-box .evidence-body {
  max-height: 140px;
  margin-top: 5px;
  overflow: auto;
  color: var(--app-text-muted);
  font-size: 11px;
  line-height: 1.4;
}

#chat-box .evidence-body :deep(img) {
  max-width: 100%;
  height: auto;
  max-height: 150px;
  border-radius: 7px;
}

#chat-box .evidence-source-list {
  display: grid;
  gap: 6px;
  margin-top: 6px;
}

#chat-box .evidence-source {
  padding: 8px 9px;
  color: var(--app-text);
  scroll-margin: 12px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border-light);
  border-radius: 8px;
}

#chat-box .evidence-source:target {
  border-color: var(--app-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--app-accent) 20%, transparent);
}

#chat-box .evidence-source-heading {
  display: flex;
  align-items: baseline;
  gap: 5px;
  font-size: 11px;
  line-height: 1.35;
}

#chat-box .evidence-source-ref {
  color: var(--app-accent-strong);
  font-weight: 800;
}

#chat-box .evidence-source-meta,
#chat-box .evidence-source-links {
  display: flex;
  flex-wrap: wrap;
  gap: 3px 7px;
  margin-top: 4px;
  color: var(--app-text-faint);
  font-size: 9px;
}

#chat-box .evidence-source p {
  margin: 4px 0 0;
  color: var(--app-text-muted);
  font-size: 10px;
  line-height: 1.4;
}

#chat-box .evidence-source-links a {
  color: var(--app-accent-strong);
  font-weight: 700;
  text-decoration: none;
}

#chat-box #example-questions {
  margin: 15px 0 7px 36px;
}

#chat-box .example-questions-label {
  margin: 0 0 7px;
  color: var(--app-text-faint);
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

#chat-box #question-slider {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
  width: 100%;
}

#chat-box #question-slider button {
  appearance: none;
  min-width: 0;
  min-height: 40px;
  margin: 0;
  padding: 7px 8px;
  color: var(--app-text-muted);
  font-size: 11px;
  font-weight: 600;
  line-height: 1.3;
  text-align: left;
  white-space: normal;
  cursor: pointer;
  background: transparent;
  border: 1px solid var(--app-border);
  border-radius: 9px;
  transition: color 130ms ease, border-color 130ms ease, background-color 130ms ease;
}

#chat-box #question-slider button:hover {
  color: var(--app-accent-strong);
  background: color-mix(in srgb, var(--app-accent) 6%, transparent);
  border-color: color-mix(in srgb, var(--app-accent) 40%, var(--app-border));
}

#chat-box #chat-input-container {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  gap: 7px;
  align-items: stretch;
  padding: 8px 12px 11px;
  background: var(--app-surface);
  border-top: 1px solid var(--app-border-light);
}

#chat-box .composer-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 25px;
}

#chat-box .answer-mode-switch {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

#chat-box .answer-mode-option {
  appearance: none;
  min-height: 25px;
  margin: 0;
  padding: 0 8px;
  color: var(--app-text-faint);
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 7px;
}

#chat-box .answer-mode-option:hover {
  color: var(--app-text);
  background: var(--app-surface-2);
  border-color: transparent;
}

#chat-box .answer-mode-option.active {
  color: var(--app-accent-strong);
  background: color-mix(in srgb, var(--app-accent) 12%, transparent);
}

#chat-box .answer-mode-option:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

#chat-box #input-area {
  display: flex;
  align-items: center;
  width: 100%;
  min-width: 0;
  height: 42px;
  padding: 4px 4px 4px 11px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  transition: border-color 140ms ease, box-shadow 140ms ease;
}

#chat-box #input-area:focus-within {
  border-color: color-mix(in srgb, var(--app-accent) 64%, var(--app-border));
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--app-accent) 12%, transparent);
}

#chat-box #chat-input {
  flex: 1 1 auto;
  width: 100%;
  min-width: 0;
  height: 100%;
  margin: 0;
  padding: 0 9px 0 0;
  color: var(--app-text);
  font: inherit;
  font-size: 13px;
  outline: 0;
  background: transparent;
  border: 0;
  border-radius: 0;
}

#chat-box #chat-input::placeholder {
  color: var(--app-text-faint);
}

#chat-box #chat-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

#chat-box #send-button {
  appearance: none;
  display: inline-flex;
  flex: 0 0 33px;
  align-items: center;
  justify-content: center;
  width: 33px;
  height: 33px;
  margin: 0;
  padding: 0;
  color: #fff;
  cursor: pointer;
  background: #315fce;
  border: 0;
  border-radius: 9px;
  transition: background-color 130ms ease, transform 130ms ease;
}

#chat-box #send-button:hover {
  background: #274fae;
  border-color: transparent;
  transform: translateY(-1px);
}

#chat-box #send-button.is-generating {
  background: #a84b0f;
}

#chat-box #send-button svg {
  display: block;
  width: 16px;
  height: 16px;
}

#chat-box .image-preview {
  display: flex;
  align-items: center;
}

#chat-box .image-preview-thumbnail {
  width: auto;
  max-width: 52px;
  height: auto;
  max-height: 52px;
  border: 1px solid var(--app-border);
  border-radius: 7px;
}

@media (hover: none), (pointer: coarse) {
  #chat-box .message-actions {
    opacity: 1;
  }
}

@media (max-width: 430px) {
  #chat-box #question-slider {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  #chat-box .loading-pulse span {
    animation: none;
  }

  #chat-box .message-actions,
  #chat-box #send-button,
  #chat-box #question-slider button {
    transition: none;
  }
}
</style>
