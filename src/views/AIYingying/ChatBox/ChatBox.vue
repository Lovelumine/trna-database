<template>
  <div class="chat-container">
    <div class="chat-box" ref="chatBox">
      <div
        class="message"
        v-for="(message, index) in renderedMessages"
        :key="index"
        :class="{ 'message-right': message.sender === 'user' }"
      >
        <div class="avatar">
          <img :src="message.sender === 'user' ? userAvatar : botAvatar" alt="avatar" />
        </div>
        <div class="bubble">
          <div class="message-body">
            <div class="content">
              <!-- 改：使用渲染后的 textHtml -->
              <div class="text" v-html="message.textHtml"></div>
            </div>
            <div class="chat-message-actions">
              <button
                class="chat-copy-button"
                type="button"
                @click="copyMessage(message, index)"
                :aria-label="'Copy message ' + (index + 1)"
                title="Copy"
                v-if="message.sender === 'user' || !message.evidenceHtml"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8 8h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2zm-2 8H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1h-2V6H6v8z"></path>
                </svg>
              </button>
              <button
                v-if="message.sender === 'user' && isLatestUserMessage(message)"
                class="chat-edit-button"
                type="button"
                @click="editMessage(message)"
                aria-label="Edit message"
                title="Edit"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M3 17.25V21h3.75L17.8 9.95l-3.75-3.75L3 17.25zm18-10.5a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75L21 6.75z"></path>
                </svg>
              </button>
              <span
                v-if="copiedId === (message.id ?? index) && (message.sender === 'user' || !message.evidenceHtml)"
                class="chat-copied-badge"
              >
                Copied
              </span>
            </div>
          </div>

          <!-- 新增：证据块，紧跟 bot 消息，默认折叠 -->
          <div
            v-if="message.sender !== 'user' && message.evidenceHtml"
            class="evidence-card"
          >
            <details>
              <summary>
                <span>Search results (RAG)</span>
                <span class="rag-actions">
                  <button
                    class="chat-copy-button rag-copy-button"
                    type="button"
                    @click.prevent.stop="copyMessage(message, index)"
                    aria-label="Copy message"
                    title="Copy"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M8 8h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2zm-2 8H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1h-2V6H6v8z"></path>
                    </svg>
                  </button>
                  <button
                    class="chat-copy-button rag-copy-button"
                    type="button"
                    @click.prevent.stop="regenerateFromMessage(message)"
                    aria-label="Regenerate response"
                    title="Regenerate"
                    v-if="isLatestBotMessage(message)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M12 6V3L8 7l4 4V8c2.76 0 5 2.24 5 5 0 1.12-.37 2.16-1 3l1.46 1.46A6.96 6.96 0 0 0 19 13c0-3.87-3.13-7-7-7zm-5 5c0-1.12.37-2.16 1-3L6.54 6.54A6.96 6.96 0 0 0 5 11c0 3.87 3.13 7 7 7v3l4-4-4-4v3c-2.76 0-5-2.24-5-5z"></path>
                    </svg>
                  </button>
                  <span
                    v-if="copiedId === (message.id ?? index)"
                    class="rag-copied-badge"
                  >
                    Copied
                  </span>
                </span>
              </summary>
              <div class="evidence-body" v-html="message.evidenceHtml"></div>
            </details>
          </div>
        </div>
      </div>

      <!-- 显示省略号 -->
      <div v-if="showLoading" class="message loading-message">
        <div class="avatar">
          <img :src="botAvatar" alt="avatar" />
        </div>
        <div class="bubble">
          <div class="content loading-card">
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
            <div v-else class="loading-pulse">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <transition name="consent-fade">
      <div v-if="noteModalVisible" class="consent-overlay" role="dialog" aria-modal="true" aria-labelledby="consent-title">
        <div class="consent-backdrop"></div>
        <div class="consent-card">
          <button
            v-if="noteAcknowledged"
            class="consent-close"
            type="button"
            aria-label="Close usage note"
            @click="$emit('close-note-modal')"
          >
            ×
          </button>
          <div class="consent-badge">{{ noteAcknowledged ? 'Usage note' : 'Before you start' }}</div>
          <h2 id="consent-title">Please review the ENSURE AI usage note.</h2>
          <p class="consent-copy">{{ noteText }}</p>
          <div class="consent-points">
            <div class="consent-point">AI answers can be incomplete, outdated, or scientifically inaccurate.</div>
            <div class="consent-point">Verify claims, citations, and experimental details before reuse.</div>
            <div class="consent-point">Once acknowledged, the input box and model selector will be unlocked.</div>
          </div>
          <div class="consent-actions">
            <button class="consent-primary" type="button" @click="$emit('acknowledge-note')">
              {{ noteAcknowledged ? 'I understand' : 'I understand and continue' }}
            </button>
            <button
              v-if="noteAcknowledged"
              class="consent-secondary"
              type="button"
              @click="$emit('close-note-modal')"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="sheet-fade">
      <div
        v-if="mobileModelPickerOpen"
        class="model-sheet-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="mobile-model-picker-title"
      >
        <button
          class="model-sheet-backdrop"
          type="button"
          aria-label="Close model picker"
          @click="closeMobileModelPicker"
        ></button>
        <div class="model-sheet">
          <div class="model-sheet-header">
            <div class="model-sheet-kicker">Mobile model picker</div>
            <h3 id="mobile-model-picker-title">Choose response model</h3>
            <p>The current model stays fixed until you change it again.</p>
          </div>
          <div class="model-sheet-options">
            <button
              v-for="model in modelOptions"
              :key="model"
              class="model-sheet-option"
              :class="{ active: model === selectedModel }"
              type="button"
              @click="chooseMobileModel(model)"
            >
              <span>{{ model }}</span>
              <span v-if="model === selectedModel" class="model-sheet-check">Selected</span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <div class="input-area" :class="{ blocked: !noteAcknowledged }">
      <button
        v-if="!noteAcknowledged"
        class="blocked-banner"
        type="button"
        @click="$emit('open-note-modal')"
      >
        Review the usage note to unlock AI chat
      </button>
      <div class="input-row">
        <textarea
          v-model="newMessage"
          @keydown.enter.exact.prevent="sendMessage"
          :placeholder="noteAcknowledged ? 'Send your messages, Shift+Enter line break' : 'Please acknowledge the note to start'"
          :disabled="!noteAcknowledged"
          ref="inputRef"
        ></textarea>
        <div class="input-icons">
          <label class="composer-toggle" :class="{ disabled: !noteAcknowledged || loading }">
            <input
              v-model="deepReviewEnabled"
              type="checkbox"
              :disabled="!noteAcknowledged || loading"
            />
            <span>Deep retrieval & review</span>
          </label>
          <div v-if="!isMobileViewport" class="composer-model-shell">
            <select
              v-model="selectedModel"
              class="composer-model-select"
              :disabled="!noteAcknowledged || loading"
              aria-label="Model selection"
            >
              <option v-for="model in modelOptions" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
            <span class="composer-model-caret" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M7 10.5 12 15l5-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </span>
          </div>
          <button
            v-else
            class="mobile-model-button"
            type="button"
            :disabled="!noteAcknowledged || loading"
            @click="openMobileModelPicker"
          >
            <span class="mobile-model-button-label">Model</span>
            <span class="mobile-model-button-value">{{ mobileModelLabel }}</span>
            <span class="mobile-model-button-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M7 10.5 12 15l5-4.5" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </span>
          </button>
          <button
            @click="handlePrimaryAction"
            class="icon-button send-button"
            :class="{ 'is-generating': loading }"
            :disabled="!noteAcknowledged"
            :aria-label="loading ? 'Stop generating' : 'Send message'"
            :title="loading ? 'Stop generating' : 'Send message'"
          >
            <svg v-if="loading" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <rect x="3.5" y="3.5" width="17" height="17" rx="4.2" fill="currentColor"></rect>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M3.5 12h13.5" fill="none" stroke="currentColor" stroke-width="2.9" stroke-linecap="round" stroke-linejoin="round"></path>
              <path d="M11.5 5.5L18 12l-6.5 6.5" fill="none" stroke="currentColor" stroke-width="2.9" stroke-linecap="round" stroke-linejoin="round"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <el-dialog :visible.sync="dialogVisible" title="提示">
      <p>当前回复尚未完成，请稍后再试。</p>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, nextTick, onMounted, computed, onBeforeUnmount } from 'vue';
import { useChat } from '../../../utils/useChat';
import { useMarkdown } from '../../../utils/useMarkdown';
import { ElDialog } from 'element-plus';
import { fetchChatModelConfig } from '@/utils/chatConfig';
import 'element-plus/dist/index.css';

const COMPOSER_MIN_HEIGHT = 44;
const COMPOSER_MAX_HEIGHT = 180;
const MOBILE_BREAKPOINT = 860;
const DEEP_REVIEW_STORAGE_KEY = 'ai_deep_review_enabled';

export default defineComponent({
  name: 'ChatBox',
  components: { ElDialog },
  emits: ['conversation-updated', 'acknowledge-note', 'close-note-modal', 'open-note-modal'],
  props: {
    conversationId: { type: String, required: true },
    apiKey: { type: String, required: true },
    noteAcknowledged: { type: Boolean, required: true },
    noteText: { type: String, required: true },
    noteModalVisible: { type: Boolean, required: true }
  },
  setup(props, { emit }) {
    const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';
    const modelOptions = ref<string[]>(['deepseek-chat', 'deepseek-reasoner', 'qwen3:32b', 'gemma3:27b']);
    const selectedModel = ref(localStorage.getItem('ai_chat_model') || 'deepseek-chat');
    watch(selectedModel, (next) => {
      localStorage.setItem('ai_chat_model', next);
    });
    const {
      messages,
      newMessage,
      sendMessage: sendChatMessage,
      stopMessage: stopChatMessage,
      resetChat,
      isStreaming,
      progressStatus,
      progressDetail,
      progressToolTrace,
      progressJudgeTrace,
      progressDraftPreview
    } = useChat(props.apiKey, {
      key: props.conversationId
    });
    const chatBox = ref<HTMLElement | null>(null);
    const dialogVisible = ref(false);
    const loading = isStreaming;
    const copiedId = ref<number | null>(null);
    const inputRef = ref<HTMLTextAreaElement | null>(null);
    const editingMessageId = ref<number | null>(null);
    const isHydrating = ref(true);
    const titleRequested = ref(false);
    const isMobileViewport = ref(false);
    const mobileModelPickerOpen = ref(false);
    const deepReviewEnabled = ref(localStorage.getItem(DEEP_REVIEW_STORAGE_KEY) === '1');

    const botAvatar = 'https://framerusercontent.com/images/p0mVMX1aJictMR1RM9fE1PrTrRQ.png';
    const userAvatar = 'https://framerusercontent.com/images/JnbQ2qAMPu3VRXkbzDhwoMnHpk.png';

    const { renderMarkdown } = useMarkdown();
    const renderedMessages = ref<any[]>([]);

    const scrollToBottom = async () => {
      await nextTick();
      if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
    };

    const syncViewport = () => {
      const next = window.innerWidth <= MOBILE_BREAKPOINT;
      isMobileViewport.value = next;
      if (!next) {
        mobileModelPickerOpen.value = false;
      }
    };

    const resizeComposer = () => {
      const composer = inputRef.value;
      if (!composer) return;
      composer.style.height = '0px';
      const nextHeight = Math.min(Math.max(composer.scrollHeight, COMPOSER_MIN_HEIGHT), COMPOSER_MAX_HEIGHT);
      composer.style.height = `${nextHeight}px`;
      composer.style.overflowY = composer.scrollHeight > COMPOSER_MAX_HEIGHT ? 'auto' : 'hidden';
    };

    onMounted(async () => {
      syncViewport();
      window.addEventListener('resize', syncViewport);
      const config = await fetchChatModelConfig();
      if (config && Array.isArray(config.model_options) && config.model_options.length) {
        modelOptions.value = config.model_options;
      }
      if (config && (!selectedModel.value || !modelOptions.value.includes(selectedModel.value))) {
        selectedModel.value = config.active_model || modelOptions.value[0] || '';
      }
      nextTick(resizeComposer);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', syncViewport);
    });

    watch(
      () => props.noteAcknowledged,
      (next) => {
        nextTick(() => {
          resizeComposer();
          if (next) inputRef.value?.focus();
        });
      }
    );

    watch(newMessage, () => {
      nextTick(resizeComposer);
    });

    watch(
      () => props.conversationId,
      () => {
        nextTick(resizeComposer);
      }
    );

    watch(deepReviewEnabled, (next) => {
      localStorage.setItem(DEEP_REVIEW_STORAGE_KEY, next ? '1' : '0');
    });

    // 抽取 Search result(s) 证据的工具函数（宽松匹配）
    const splitSearchResult = (raw: string) => {
      if (typeof raw !== 'string') return { main: '', evidence: '' };
      const s = raw.replace(/\r\n/g, '\n');
      // 支持 “Search result”/“Search results” + 中英文冒号 + 前置 Markdown 符号
      const re = /(?:^|\n)\s*(?:[*_#>\-\d.\)\s]{0,6})?(?:Search\s*results?)\s*[:：]\s*/i;
      let m = re.exec(s);
      if (!m) {
        // 兜底：无冒号时，遇到“Search result(s)”标题也切
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

    const buildHistoryPayload = (sourceMessages: any[], options: { excludeMessageId?: number | null } = {}) => {
      const items = (sourceMessages || [])
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
      return items;
    };

    watch(
      messages,
      async (newVal) => {
        const rendered = await Promise.all(
          newVal.map(async (m: any) => {
            const msg = { ...m };
            msg.sender = msg.sender || msg.role || 'bot';

            const raw =
              typeof msg.text === 'string'
                ? msg.text
                : (typeof msg.content === 'string' ? msg.content : '');

            if (raw) {
              const { main, evidence } = splitSearchResult(raw);
              msg.textHtml = await renderMarkdown(main || '');
              msg.evidenceHtml = evidence ? await renderMarkdown(evidence) : '';
              msg.textPlain = main || '';
              msg.evidencePlain = evidence || '';
            } else {
              msg.textHtml = '';
              msg.evidenceHtml = '';
              msg.textPlain = '';
              msg.evidencePlain = '';
            }
            return msg;
          })
        );
        renderedMessages.value = rendered;
        scrollToBottom();
      },
      { deep: true, immediate: true }
    );

    const sendMessage = async () => {
      if (loading.value) return;
      if (!props.noteAcknowledged) return;
      const text = newMessage.value.trim();
      if (!text) return;
      const sourceMessages = [...messages.value];
      let historySource = sourceMessages;

      if (editingMessageId.value) {
        const index = messages.value.findIndex(m => m.id === editingMessageId.value);
        if (index >= 0) {
          historySource = sourceMessages.slice(0, index);
          messages.value[index].text = text;
          messages.value.splice(index + 1);
        }
      }

      const result = await sendChatMessage({
        skipUserPush: !!editingMessageId.value,
        overrideText: text,
        model: getSelectedModel(),
        history: buildHistoryPayload(historySource),
        deepReview: deepReviewEnabled.value
      });
      if (!result?.aborted) {
        editingMessageId.value = null;
      }
    };

    const stopGenerating = () => {
      if (!loading.value) return;
      stopChatMessage();
      editingMessageId.value = null;
    };

    const handlePrimaryAction = () => {
      if (loading.value) {
        stopGenerating();
        return;
      }
      void sendMessage();
    };

    watch(
      () => props.apiKey,
      async (nextKey) => {
        if (!nextKey) return;
        await resetChat(nextKey);
      }
    );

    const storageKey = () => `ai_chat_session_${props.conversationId}`;
    const getSelectedModel = () => selectedModel.value;
    const mobileModelLabel = computed(() => {
      const text = selectedModel.value || 'Model';
      return text.length > 20 ? `${text.slice(0, 20)}...` : text;
    });
    const openMobileModelPicker = () => {
      if (!isMobileViewport.value || !props.noteAcknowledged || loading.value) return;
      mobileModelPickerOpen.value = true;
    };
    const closeMobileModelPicker = () => {
      mobileModelPickerOpen.value = false;
    };
    const chooseMobileModel = (model: string) => {
      selectedModel.value = model;
      closeMobileModelPicker();
    };
    const visibleProgressTools = computed(() => progressToolTrace.value.slice(-6));
    const visibleProgressJudges = computed(() => {
      const raw = Array.isArray(progressJudgeTrace.value) ? progressJudgeTrace.value : [];
      return raw.slice(-3);
    });

    const summarizeTitle = (text: string) => {
      const cleaned = String(text || '')
        .replace(/[#>*_`-]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
      if (!cleaned) return 'New chat';
      const hasCjk = /[\u4e00-\u9fff]/.test(cleaned);
      if (hasCjk) {
        const first = cleaned.split(/[。！？\n]/)[0] || cleaned;
        const compact = first.replace(/[，、:：;；]/g, ' ').trim();
        return compact.length > 14 ? `${compact.slice(0, 14)}...` : compact;
      }
      const words = cleaned.split(/\s+/);
      const short = words.slice(0, 6).join(' ');
      return words.length > 6 ? `${short}...` : short;
    };

    const isGreeting = (text: string) => {
      const normalized = String(text || '').trim().toLowerCase();
      return normalized.startsWith('hello, i am your virtual assistant') ||
        normalized.includes('how can i assist you today');
    };

    const buildTitle = (list: any[]) => {
      const firstBot = list.find(m =>
        m?.sender === 'bot' &&
        typeof m?.text === 'string' &&
        m.text.trim() &&
        !isGreeting(m.text)
      );
      const firstUser = list.find(m => m?.sender === 'user' && typeof m?.text === 'string' && m.text.trim());
      const source = firstBot?.text || firstUser?.text || 'New chat';
      return summarizeTitle(source);
    };

    const buildSummaryPayload = () => {
      const items = (renderedMessages.value || [])
        .map(m => ({
          role: m?.sender === 'user' ? 'user' : 'assistant',
          content: (m?.textPlain || m?.text || '').trim()
        }))
        .filter(m => m.content);
      const trimmed = items.slice(0, 8).map(m => ({
        role: m.role,
        content: m.content.slice(0, 800)
      }));
      return trimmed;
    };

    const requestTitleSummary = async () => {
      if (titleRequested.value) return;
      const payloadMessages = buildSummaryPayload();
      const hasAssistant = payloadMessages.some(
        m => m.role === 'assistant' && !isGreeting(m.content)
      );
      const hasUser = payloadMessages.some(m => m.role === 'user');
      if (!hasUser || !hasAssistant) return;
      titleRequested.value = true;
      try {
        const resp = await fetch(`${apiBaseURL}/title`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${props.apiKey}`
          },
          body: JSON.stringify({ messages: payloadMessages, model: getSelectedModel() })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const title = String(data?.title || '').trim();
        if (title) {
          emit('conversation-updated', {
            id: props.conversationId,
            title,
            updatedAt: Date.now(),
            source: 'ai'
          });
        }
      } catch {
        titleRequested.value = false;
      }
    };

    const showLoading = computed(() => {
      if (!loading.value) return false;
      const last = messages.value[messages.value.length - 1];
      return !last || last.sender !== 'bot';
    });

    const hydrateMessages = async () => {
      try {
        const hasUser = messages.value.some(
          m => m?.sender === 'user' && typeof m?.text === 'string' && m.text.trim()
        );
        if (hasUser) return;
        const raw = localStorage.getItem(storageKey());
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed?.messages) && parsed.messages.length) {
          messages.value = parsed.messages;
        }
      } catch {
        // ignore malformed cache
      } finally {
        await nextTick();
        isHydrating.value = false;
      }
    };

    const persistMessages = () => {
      if (isHydrating.value) return;
      const hasUser = messages.value.some(
        m => m?.sender === 'user' && typeof m?.text === 'string' && m.text.trim()
      );
      if (!hasUser) return;
      const updatedAt = Date.now();
      const payload = { messages: messages.value, updatedAt };
      localStorage.setItem(storageKey(), JSON.stringify(payload));
      emit('conversation-updated', {
        id: props.conversationId,
        title: buildTitle(messages.value),
        updatedAt,
        source: 'fallback'
      });
      requestTitleSummary();
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

    const copyMessage = async (message: any, index: number) => {
      const main = typeof message.textPlain === 'string' ? message.textPlain : '';
      const evidence = typeof message.evidencePlain === 'string' ? message.evidencePlain : '';
      const text = evidence ? `${main}\n\nSearch results:\n${evidence}` : main;
      await writeClipboard(text);
      const id = (message.id ?? index) as number;
      copiedId.value = id;
      window.setTimeout(() => {
        if (copiedId.value === id) copiedId.value = null;
      }, 1200);
    };

    onMounted(() => {
      hydrateMessages().then(() => {
        persistMessages();
      });
      nextTick(resizeComposer);
    });

    watch(
      messages,
      () => {
        persistMessages();
      },
      { deep: true }
    );

    const editMessage = (message: any) => {
      const text = typeof message?.textPlain === 'string' ? message.textPlain : message?.text || '';
      if (!text) return;
      newMessage.value = text;
      editingMessageId.value = message?.id ?? null;
      nextTick(() => {
        resizeComposer();
        inputRef.value?.focus();
      });
    };

    const isLatestUserMessage = (message: any) => {
      const lastUser = [...messages.value].reverse().find(m => m?.sender === 'user');
      if (!lastUser) return false;
      return message?.id === lastUser.id;
    };

    const isLatestBotMessage = (message: any) => {
      const lastBot = [...messages.value].reverse().find(m => m?.sender !== 'user');
      if (!lastBot) return false;
      return message?.id === lastBot.id;
    };

    const regenerateFromMessage = async (message: any) => {
      if (!isLatestBotMessage(message)) return;
      const list = [...messages.value];
      const targetIndex = list.findIndex(m => m?.id === message?.id);
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
      if (typeof userIndex !== 'number') return;
      const userMsg = list[userIndex];
      if (!userMsg?.text) return;
      const historySource = list.slice(0, userIndex);
      messages.value = list.slice(0, userIndex + 1);
      await sendChatMessage({
        skipUserPush: true,
        overrideText: userMsg.text,
        model: getSelectedModel(),
        history: buildHistoryPayload(historySource),
        deepReview: deepReviewEnabled.value
      });
    };

    return {
      newMessage,
      renderedMessages,
      sendMessage,
      handlePrimaryAction,
      selectedModel,
      modelOptions,
      isMobileViewport,
      mobileModelPickerOpen,
      mobileModelLabel,
      progressStatus,
      progressDetail,
      progressDraftPreview,
      deepReviewEnabled,
      visibleProgressJudges,
      visibleProgressTools,
      openMobileModelPicker,
      closeMobileModelPicker,
      chooseMobileModel,
      chatBox,
      dialogVisible,
      botAvatar,
      userAvatar,
      loading,
      copyMessage,
      copiedId,
      editMessage,
      isLatestUserMessage,
      inputRef,
      showLoading,
      stopGenerating,
      regenerateFromMessage,
      isLatestBotMessage
    };
  }
});
</script>

<style>
* { box-sizing: border-box; }

.chat-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: linear-gradient(180deg, var(--ai-panel), var(--ai-card-muted));
  border-radius: 0;
  overflow: hidden;
  border: none;
  box-shadow: none;
}

.chat-box {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 30px 16px;
  overflow-y: auto;
  scroll-behavior: smooth;
  user-select: text;
  background:
    radial-gradient(24rem 18rem at top right, var(--ai-accent-soft), transparent 68%),
    transparent;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0;
  max-width: min(84%, 64rem);
  gap: 12px;
  animation: bubbleUp 0.35s ease-out;
  background: transparent;
  border: none;
}

.message-right { flex-direction: row-reverse; align-self: flex-end; }

.avatar {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  padding: 2px;
  border-radius: 50%;
  background: var(--ai-accent-soft);
  border: 1px solid var(--ai-border-strong);
}

.avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  object-position: center;
}

.bubble {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  flex: 0 1 auto;
  max-width: calc(100% - 40px);
}

.message-right .bubble {
  align-items: flex-end;
}

.message-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  max-width: 100%;
}

.message-right .message-body {
  align-items: flex-end;
}

.content {
  background: var(--ai-card);
  padding: 15px 17px;
  border-radius: 20px 20px 20px 8px;
  width: 100%;
  max-width: 100%;
  color: var(--ai-text);
  border: 1px solid var(--ai-border);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-shadow: var(--ai-card-shadow);
}

.message-right .content {
  background: linear-gradient(180deg, var(--ai-user-start), var(--ai-user-end));
  color: var(--ai-user-text);
  border-color: transparent;
  align-items: flex-end;
  border-radius: 20px 20px 8px 20px;
  box-shadow: var(--ai-user-shadow);
}

.message .content img {
  max-width: 70% !important;
  height: auto !important;
  display: block !important;
  margin: 6px auto 0 !important;
}

img { max-width: 100% !important; }

.text {
  color: inherit;
  font-size: 15px;
  line-height: 1.72;
}

.chat-message-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  width: fit-content;
  max-width: 100%;
  justify-content: flex-start;
}

.message-right .chat-message-actions {
  justify-content: flex-end;
}

.message-right .evidence-card {
  align-self: flex-end;
}

.chat-copy-button,
.chat-edit-button {
  width: 30px;
  height: 30px;
  padding: 0;
  border-radius: 50%;
  border: 1px solid var(--ai-border);
  background: var(--ai-card-muted);
  color: var(--ai-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.message-right .chat-copy-button,
.message-right .chat-edit-button {
  border-color: var(--ai-user-action-border);
  background: var(--ai-user-action-bg);
  color: var(--ai-user-text);
}

.chat-copy-button svg,
.chat-edit-button svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
}

.chat-copied-badge {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid var(--ai-border);
  background: var(--ai-card-muted);
  color: var(--ai-muted);
}

.evidence-card {
  margin-top: 6px;
  align-self: flex-start;
  margin-left: 0;
}

.evidence-card details {
  background: transparent;
  border: none;
  padding: 0;
}

.evidence-card summary {
  cursor: pointer;
  list-style: none;
  font-size: 12px;
  font-weight: 700;
  color: var(--ai-muted);
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--ai-card-muted);
  border: 1px solid var(--ai-border);
  border-radius: 999px;
  padding: 6px 12px;
  width: fit-content;
  line-height: 1;
}

.evidence-card summary span {
  white-space: nowrap;
}

.evidence-card summary .rag-actions {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  margin-left: 6px;
}

.rag-copy-button {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.rag-copied-badge {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid var(--ai-border);
  background: var(--ai-card-muted);
  color: var(--ai-muted);
}

.evidence-card summary::-webkit-details-marker { display: none; }

.evidence-body {
  margin-top: 10px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--ai-card-muted);
  border: 1px solid var(--ai-border);
  font-size: 13px;
  line-height: 1.55;
  max-height: 360px;
  overflow: auto;
  color: var(--ai-text);
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 14px 14px;
  background: linear-gradient(180deg, var(--ai-panel), var(--ai-shell));
  border-top: 1px solid var(--ai-border);
  z-index: 2;
  width: 100%;
  transition: all 0.3s ease-in-out;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

.blocked-banner {
  min-height: 40px;
  width: fit-content;
  max-width: 100%;
  padding: 0 14px;
  border: 1px solid var(--ai-warning-border);
  border-radius: 999px;
  background: var(--ai-warning-soft);
  color: var(--ai-warning-text);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.input-row {
  display: flex;
  align-items: stretch;
  gap: 10px;
  width: 100%;
  padding: 6px;
  border-radius: 16px;
  background: var(--ai-card);
  border: 1px solid var(--ai-border);
  box-shadow: var(--ai-card-shadow);
}

.input-row:focus-within {
  border-color: var(--ai-border-strong);
  box-shadow: 0 0 0 3px var(--ai-accent-soft);
}

.composer-model-shell {
  position: relative;
  display: flex;
  align-items: center;
  height: 54px;
  min-width: 168px;
  flex-shrink: 0;
}

.composer-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 54px;
  padding: 0 12px;
  border-radius: 16px;
  border: 1px solid var(--ai-border);
  background: linear-gradient(180deg, var(--ai-card), var(--ai-card-muted));
  color: var(--ai-muted);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.composer-toggle input {
  width: 14px;
  height: 14px;
  accent-color: var(--ai-accent);
}

.composer-toggle.disabled {
  opacity: 0.6;
}

.composer-model-select {
  display: block;
  width: 100%;
  height: 54px;
  min-width: 0;
  padding: 0 42px 0 16px;
  border-radius: 16px;
  border: 1px solid var(--ai-border);
  background: linear-gradient(180deg, var(--ai-card), var(--ai-card-muted));
  color: var(--ai-text);
  font-size: 13px;
  font-weight: 600;
  appearance: none;
  box-shadow: none;
  line-height: 1;
  cursor: pointer;
}

.composer-model-select:focus {
  outline: none;
  border-color: var(--ai-border-strong);
}

.composer-model-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.composer-model-caret {
  position: absolute;
  right: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ai-muted);
  pointer-events: none;
}

.composer-model-caret svg {
  width: 16px;
  height: 16px;
}

.input-area textarea {
  flex: 1;
  padding: 10px 8px 10px 8px;
  border: none;
  resize: none;
  height: 44px;
  min-height: 44px;
  max-height: 180px;
  width: 100%;
  background: transparent;
  color: var(--ai-text);
  font-size: 14px;
  line-height: 1.5;
  overflow-y: hidden;
  display: block;
}

.input-area textarea:focus {
  outline: none;
}

.input-area textarea::placeholder { color: var(--ai-muted); }

.input-area textarea:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.input-icons {
  display: flex;
  align-items: stretch;
  gap: 8px;
  flex-shrink: 0;
}

.mobile-model-button {
  display: none;
}

.icon-button {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  border: none;
  background: transparent;
  color: var(--ai-muted);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-button:hover { transform: translateY(-1px); }
.send-button:active { animation: sendAnimation 0.3s ease-in-out; }

.icon-button svg {
  width: 24px;
  height: 24px;
  display: block;
}

.icon-button:hover {
  color: var(--ai-accent);
}

.send-button {
  width: 54px;
  height: 54px;
  background: linear-gradient(180deg, var(--ai-accent), var(--ai-accent-strong));
  color: #fff;
  box-shadow: 0 10px 22px rgba(34, 78, 191, 0.22);
}

.send-button svg {
  width: 30px;
  height: 30px;
}

.send-button:hover {
  color: #fff;
}

.send-button.is-generating {
  background: linear-gradient(180deg, #f59e0b, #d97706);
  box-shadow: 0 10px 22px rgba(217, 119, 6, 0.24);
}

.send-button.is-generating svg {
  width: 36px;
  height: 36px;
}

.icon-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.consent-overlay {
  position: absolute;
  inset: 0;
  z-index: 8;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.consent-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(2, 6, 23, 0.54);
  backdrop-filter: blur(10px);
}

.consent-card {
  position: relative;
  width: min(34rem, 100%);
  padding: 26px 24px 22px;
  border-radius: 26px;
  background: linear-gradient(180deg, var(--ai-card), var(--ai-card-muted));
  border: 1px solid var(--ai-border);
  box-shadow: 0 24px 54px rgba(2, 6, 23, 0.28);
}

.consent-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid var(--ai-border);
  background: var(--ai-card-muted);
  color: var(--ai-muted);
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
}

.consent-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--ai-accent-soft);
  color: var(--ai-accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.consent-card h2 {
  margin: 14px 0 10px;
  font-size: 26px;
  line-height: 1.15;
  color: var(--ai-text);
}

.consent-copy {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--ai-muted);
}

.consent-points {
  display: grid;
  gap: 10px;
  margin-top: 18px;
}

.consent-point {
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--ai-card-muted);
  border: 1px solid var(--ai-border);
  color: var(--ai-text);
  font-size: 13px;
  line-height: 1.55;
}

.consent-actions {
  display: flex;
  gap: 10px;
  margin-top: 22px;
}

.consent-primary,
.consent-secondary {
  min-height: 44px;
  padding: 0 16px;
  border-radius: 14px;
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.consent-primary {
  background: linear-gradient(180deg, var(--ai-accent), var(--ai-accent-strong));
  color: #fff;
  box-shadow: 0 14px 28px rgba(34, 78, 191, 0.22);
}

.consent-secondary {
  background: var(--ai-card-muted);
  color: var(--ai-text);
  border-color: var(--ai-border);
}

.chat-box::-webkit-scrollbar { width: 10px; }
.chat-box::-webkit-scrollbar-thumb { background-color: var(--ai-border-strong); border-radius: 999px; }
.chat-box::-webkit-scrollbar-track { background-color: transparent; }

@keyframes sendAnimation { 0%{transform:translateY(0);} 50%{transform:translateY(-5px);} 100%{transform:translateY(0);} }
@keyframes bubbleUp { from{ transform: translateY(16px); opacity:0; } to{ transform: translateY(0); opacity:1; } }
@keyframes loadingPulse { 0%, 80%, 100% { transform: scale(0.75); opacity: 0.25; } 40% { transform: scale(1); opacity: 1; } }

.consent-fade-enter-active,
.consent-fade-leave-active {
  transition: opacity 0.2s ease;
}

.consent-fade-enter-from,
.consent-fade-leave-to {
  opacity: 0;
}

.sheet-fade-enter-active,
.sheet-fade-leave-active {
  transition: opacity 0.2s ease;
}

.sheet-fade-enter-from,
.sheet-fade-leave-to {
  opacity: 0;
}

.loading-message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0;
  max-width: min(84%, 64rem);
  animation: bubbleUp 0.4s ease-out;
}

.loading-card {
  min-width: min(32rem, 100%);
  gap: 10px;
}

.loading-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  background: var(--ai-accent-soft);
  color: var(--ai-accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.loading-status {
  font-size: 16px;
  font-weight: 700;
  line-height: 1.35;
  color: var(--ai-text);
}

.loading-detail {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--ai-muted);
}

.loading-tools {
  display: grid;
  gap: 8px;
}

.loading-tools-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ai-muted);
}

.loading-tool-item {
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 14px;
  background: var(--ai-card-muted);
  border: 1px solid var(--ai-border);
}

.loading-tool-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--ai-accent-strong);
}

.loading-tool-summary {
  font-size: 12px;
  line-height: 1.5;
  color: var(--ai-muted);
  word-break: break-word;
}

.loading-tool-item--draft {
  max-height: 12rem;
  overflow: auto;
}

.loading-tool-summary--draft {
  white-space: pre-wrap;
}

.loading-pulse {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 18px;
}

.loading-pulse span {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--ai-accent);
  opacity: 0.25;
  animation: loadingPulse 1.1s ease-in-out infinite;
}

.loading-pulse span:nth-child(2) {
  animation-delay: 0.18s;
}

.loading-pulse span:nth-child(3) {
  animation-delay: 0.36s;
}

@media (max-width: 860px) {
  .chat-box {
    padding: 14px 14px 10px;
    gap: 14px;
  }

  .message,
  .loading-message {
    max-width: 100%;
    gap: 10px;
  }
  .loading-card {
    min-width: 0;
  }
  .loading-status {
    font-size: 15px;
  }

  .avatar { width: 30px; height: 30px; }
  .bubble { max-width: calc(100% - 36px); }
  .content {
    padding: 13px 14px;
  }
  .message-right .content {
    border-radius: 18px 18px 8px 18px;
  }
  .text {
    font-size: 14px;
    line-height: 1.65;
  }
  .input-area {
    padding: 10px 12px calc(12px + env(safe-area-inset-bottom));
  }
  .blocked-banner {
    width: 100%;
  }
  .input-row {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding: 10px;
    border-radius: 20px;
  }
  .input-area textarea {
    padding: 8px 2px;
    font-size: 16px;
  }
  .input-icons {
    width: 100%;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
  }
  .composer-toggle {
    min-height: 44px;
    padding: 0 10px;
    border-radius: 14px;
    font-size: 11px;
    flex: 1 1 auto;
  }
  .mobile-model-button {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    max-width: calc(100% - 62px);
    height: 44px;
    padding: 0 14px;
    border-radius: 14px;
    border: 1px solid var(--ai-border);
    background: linear-gradient(180deg, var(--ai-card), var(--ai-card-muted));
    color: var(--ai-text);
    flex: 0 1 auto;
    box-shadow: var(--ai-card-shadow);
  }
  .mobile-model-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .mobile-model-button-label {
    font-size: 11px;
    font-weight: 700;
    color: var(--ai-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    white-space: nowrap;
  }
  .mobile-model-button-value {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 14px;
    font-weight: 700;
  }
  .mobile-model-button-icon {
    width: 16px;
    height: 16px;
    color: var(--ai-muted);
    flex-shrink: 0;
  }
  .mobile-model-button-icon svg {
    width: 16px;
    height: 16px;
  }
  .icon-button,
  .send-button {
    width: 52px;
    height: 52px;
    border-radius: 15px;
  }
  .icon-button svg,
  .send-button svg {
    width: 24px;
    height: 24px;
  }
  .send-button.is-generating svg {
    width: 30px;
    height: 30px;
  }
  .model-sheet-overlay {
    position: absolute;
    inset: 0;
    z-index: 9;
    display: flex;
    align-items: flex-end;
  }
  .model-sheet-backdrop {
    position: absolute;
    inset: 0;
    border: none;
    background: rgba(15, 23, 42, 0.28);
    backdrop-filter: blur(5px);
  }
  .model-sheet {
    position: relative;
    width: 100%;
    padding: 14px 14px calc(18px + env(safe-area-inset-bottom));
    border-radius: 22px 22px 0 0;
    background: linear-gradient(180deg, var(--ai-card), var(--ai-card-muted));
    border-top: 1px solid var(--ai-border);
    box-shadow: 0 -20px 40px rgba(15, 23, 42, 0.16);
  }
  .model-sheet-header {
    padding: 4px 2px 12px;
  }
  .model-sheet-kicker {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ai-accent);
  }
  .model-sheet-header h3 {
    margin: 6px 0 4px;
    font-size: 18px;
    color: var(--ai-text);
  }
  .model-sheet-header p {
    margin: 0;
    font-size: 13px;
    line-height: 1.5;
    color: var(--ai-muted);
  }
  .model-sheet-options {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .model-sheet-option {
    min-height: 50px;
    padding: 0 14px;
    border-radius: 16px;
    border: 1px solid var(--ai-border);
    background: var(--ai-card);
    color: var(--ai-text);
    font-size: 14px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .model-sheet-option.active {
    border-color: var(--ai-border-strong);
    background: var(--ai-card-strong);
    color: var(--ai-accent-strong);
  }
  .model-sheet-check {
    font-size: 11px;
    font-weight: 700;
    color: var(--ai-accent);
    white-space: nowrap;
  }
  .evidence-card summary {
    width: 100%;
    justify-content: space-between;
  }
  .evidence-card summary .rag-actions {
    margin-left: 0;
  }
  .consent-overlay {
    padding: 16px;
  }
  .consent-card {
    padding: 22px 18px 18px;
    border-radius: 22px;
  }
  .consent-card h2 {
    font-size: 22px;
  }
  .consent-actions {
    flex-direction: column;
  }
}
</style>
