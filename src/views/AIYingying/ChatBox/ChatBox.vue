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
              <div class="text" v-html="message.textHtml" @click="handleEvidenceClick"></div>
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
            v-if="message.sender !== 'user' && (message.evidenceHtml || message.evidenceSources?.length)"
            class="evidence-card"
          >
            <details>
              <summary>
                <span>Evidence &amp; sources</span>
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
              <div v-if="message.evidenceHtml" class="evidence-body" v-html="message.evidenceHtml"></div>
              <div v-if="message.evidenceSources?.length" class="evidence-source-list">
                <article
                  v-for="source in message.evidenceSources"
                  :id="sourceTargetId(message, source)"
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
          <div class="answer-mode-switch" role="group" aria-label="Answer mode">
            <button
              v-for="mode in answerModes"
              :key="mode.value"
              class="answer-mode-option"
              :class="{ active: chatMode === mode.value }"
              type="button"
              :disabled="!noteAcknowledged || loading"
              @click="chatMode = mode.value"
            >{{ mode.label }}</button>
          </div>
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
import { defineComponent, ref, watch, nextTick, onMounted, computed } from 'vue';
import { useChat } from '../../../utils/useChat';
import { useMarkdown } from '../../../utils/useMarkdown';
import { ElDialog } from 'element-plus';
import { fetchChatModelConfig, resolveChatModelSelection } from '@/utils/chatConfig';
import { chatModeRequestOptions, persistChatMode, readChatMode, type ChatMode } from '@/utils/chatMode';
import { isChatGreeting } from '@/utils/chatGreeting';
import {
  evidenceLinks,
  evidenceTargetId,
  handleEvidenceReferenceClick,
  linkEvidenceCitations,
  normalizeEvidenceSources
} from '@/utils/chatEvidence';
import 'element-plus/dist/index.css';

const COMPOSER_MIN_HEIGHT = 44;
const COMPOSER_MAX_HEIGHT = 180;

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
    const modelOptions = ref<string[]>([]);
    const answerModes: Array<{ value: ChatMode; label: string }> = [
      { value: 'fast', label: 'Fast answer' },
      { value: 'deep', label: 'Deep research' }
    ];
    const chatMode = ref<ChatMode>(readChatMode());
    const selectedModel = ref('');
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
    watch(chatMode, persistChatMode, { immediate: true });

    const botAvatar = 'https://framerusercontent.com/images/p0mVMX1aJictMR1RM9fE1PrTrRQ.png';
    const userAvatar = 'https://framerusercontent.com/images/JnbQ2qAMPu3VRXkbzDhwoMnHpk.png';

    const { renderMarkdown } = useMarkdown();
    const renderedMessages = ref<any[]>([]);

    const scrollToBottom = async () => {
      await nextTick();
      if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
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
      const config = await fetchChatModelConfig();
      const selection = resolveChatModelSelection(config);
      modelOptions.value = selection.modelOptions;
      selectedModel.value = selection.activeModel;
      if (selection.activeModel) {
        localStorage.setItem('ai_chat_model', selection.activeModel);
      } else {
        localStorage.removeItem('ai_chat_model');
      }
      nextTick(resizeComposer);
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
          newVal.map(async (m: any, index: number) => {
            const msg = { ...m };
            msg.sender = msg.sender || msg.role || 'bot';
            const messageId = msg.id ?? index;
            const sources = normalizeEvidenceSources(msg.sources);

            const raw =
              typeof msg.text === 'string'
                ? msg.text
                : (typeof msg.content === 'string' ? msg.content : '');

            if (raw) {
              const { main, evidence } = splitSearchResult(raw);
              msg.textHtml = await renderMarkdown(linkEvidenceCitations(main || '', messageId, sources));
              msg.evidenceHtml = evidence ? await renderMarkdown(evidence) : '';
              msg.textPlain = main || '';
              msg.evidencePlain = evidence || '';
            } else {
              msg.textHtml = '';
              msg.evidenceHtml = '';
              msg.textPlain = '';
              msg.evidencePlain = '';
            }
            msg.evidenceSources = sources.map(source => ({
              ...source,
              links: evidenceLinks(source)
            }));
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
        ...chatModeRequestOptions(chatMode.value)
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
    const handleEvidenceClick = (event: MouseEvent) => handleEvidenceReferenceClick(event);
    const sourceTargetId = (message: any, source: any) =>
      evidenceTargetId(message?.id ?? 'message', source?.ref ?? '1');
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

    const isGreeting = (text: string) => isChatGreeting(text);

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
            'Content-Type': 'application/json'
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
        ...chatModeRequestOptions(chatMode.value)
      });
    };

    return {
      newMessage,
      renderedMessages,
      sendMessage,
      handlePrimaryAction,
      selectedModel,
      modelOptions,
      answerModes,
      chatMode,
      progressStatus,
      progressDetail,
      progressDraftPreview,
      visibleProgressJudges,
      visibleProgressTools,
      handleEvidenceClick,
      sourceTargetId,
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

.evidence-source-list {
  display: grid;
  gap: 10px;
  margin-top: 10px;
}

.evidence-source {
  padding: 13px 15px;
  border: 1px solid var(--ai-border);
  border-radius: 14px;
  background: var(--ai-card-muted);
  color: var(--ai-text);
  scroll-margin: 24px;
}

.evidence-source:target {
  border-color: var(--ai-accent);
  box-shadow: 0 0 0 3px var(--ai-accent-soft);
}

.evidence-source-heading {
  display: flex;
  align-items: baseline;
  gap: 8px;
  line-height: 1.4;
}

.evidence-source-ref {
  color: var(--ai-accent);
  font-weight: 800;
}

.evidence-source-meta,
.evidence-source-links {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
  margin-top: 8px;
  color: var(--ai-muted);
  font-size: 12px;
}

.evidence-source p {
  margin: 8px 0 0;
  color: var(--ai-muted);
  font-size: 13px;
  line-height: 1.5;
}

.evidence-source-links a {
  color: var(--ai-accent);
  font-weight: 700;
  text-decoration: none;
}

.evidence-source-links a:hover { text-decoration: underline; }

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

.answer-mode-switch {
  display: inline-grid;
  grid-template-columns: repeat(2, max-content);
  align-items: center;
  gap: 3px;
  min-height: 46px;
  padding: 4px;
  border-radius: 14px;
  border: 1px solid var(--ai-border);
  background: var(--ai-card-muted);
  flex-shrink: 0;
}

.answer-mode-option {
  min-height: 36px;
  padding: 0 11px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--ai-muted);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
}

.answer-mode-option.active {
  color: #fff;
  background: var(--ai-accent);
  box-shadow: 0 4px 12px rgba(34, 78, 191, 0.2);
}

.answer-mode-option:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  .answer-mode-switch {
    flex: 1 1 auto;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    min-width: 0;
  }
  .answer-mode-option {
    padding: 0 7px;
    font-size: 11px;
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
