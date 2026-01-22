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
          <div class="content">
            <div class="text">...</div>
          </div>
        </div>
      </div>
    </div>

    <div class="input-area" :class="{ fullscreen: isFullscreen }">
      <div class="input-row">
        <textarea
          v-model="newMessage"
          @keyup.enter.exact.prevent="sendMessage"
          @keyup.enter.shift="newMessage += '\n'"
          :placeholder="noteAcknowledged ? 'Send your messages, Shift+Enter line break' : 'Please acknowledge the note to start'"
          :disabled="!noteAcknowledged"
          ref="inputRef"
        ></textarea>
        <select
          v-model="selectedModel"
          class="model-select"
          :disabled="!noteAcknowledged"
          aria-label="Model selection"
        >
          <option v-for="model in modelOptions" :key="model" :value="model">
            {{ model }}
          </option>
        </select>
        <div class="input-icons">
          <button @click="toggleFullscreen" class="icon-button">
            <svg
              v-if="!isFullscreen"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="24"
              height="24"
            >
              <path d="M7 14H5v5h5v-2H7v-3zm0-4h2V7h3V5H7v5zm10 0h2V5h-5v2h3v3zm0 4h-2v3h-3v2h5v-5z"></path>
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="24"
              height="24"
            >
              <path d="M16 12h2V7h-5v2h3v3zm-8 0H7v3H4v-5h2v3zm8-8h-3v2h3v3h2V4h-2zm-8 0H7v5h5V7H9V4z"></path>
            </svg>
          </button>
          <button @click="sendMessage" class="icon-button send-button" :disabled="!noteAcknowledged">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="24"
              height="24"
            >
              <path d="M2 21l21-9L2 3v7l15 2-15 2v7z"></path>
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
import 'element-plus/dist/index.css';

export default defineComponent({
  name: 'ChatBox',
  components: { ElDialog },
  emits: ['conversation-updated'],
  props: {
    conversationId: { type: String, required: true },
    apiKey: { type: String, required: true },
    noteAcknowledged: { type: Boolean, required: true }
  },
  setup(props, { emit }) {
    const apiBaseURL = import.meta.env.VITE_CHAT_API_BASE || '/chat/api';
    const modelOptions = ['qwen3:32b', 'gemma3:27b'];
    const selectedModel = ref(localStorage.getItem('ai_chat_model') || 'qwen3:32b');
    watch(selectedModel, (next) => {
      localStorage.setItem('ai_chat_model', next);
    });
    const { messages, newMessage, sendMessage: sendChatMessage, resetChat } = useChat(props.apiKey, {
      key: props.conversationId
    });
    const isFullscreen = ref(false);
    const chatBox = ref<HTMLElement | null>(null);
    const dialogVisible = ref(false);
    const loading = ref(false);
    const copiedId = ref<number | null>(null);
    const inputRef = ref<HTMLTextAreaElement | null>(null);
    const editingMessageId = ref<number | null>(null);
    const isHydrating = ref(true);
    const titleRequested = ref(false);

    const botAvatar = 'https://framerusercontent.com/images/p0mVMX1aJictMR1RM9fE1PrTrRQ.png';
    const userAvatar = 'https://framerusercontent.com/images/JnbQ2qAMPu3VRXkbzDhwoMnHpk.png';

    const { renderMarkdown } = useMarkdown();
    const renderedMessages = ref<any[]>([]);

    const scrollToBottom = async () => {
      await nextTick();
      if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
    };

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

    const toggleFullscreen = () => { isFullscreen.value = !isFullscreen.value; };

    const sendMessage = async () => {
      if (!props.noteAcknowledged) return;
      const text = newMessage.value.trim();
      if (!text) return;

      if (editingMessageId.value) {
        const index = messages.value.findIndex(m => m.id === editingMessageId.value);
        if (index >= 0) {
          messages.value[index].text = text;
          messages.value.splice(index + 1);
        }
      }

      loading.value = true;
      await sendChatMessage({
        skipUserPush: !!editingMessageId.value,
        overrideText: text,
        model: getSelectedModel()
      });
      loading.value = false;
      editingMessageId.value = null;
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
      nextTick(() => inputRef.value?.focus());
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
      messages.value = list.slice(0, userIndex + 1);
      loading.value = true;
      await sendChatMessage({
        skipUserPush: true,
        overrideText: userMsg.text,
        model: getSelectedModel()
      });
      loading.value = false;
    };

    return {
      newMessage,
      renderedMessages,
      sendMessage,
      isFullscreen,
      toggleFullscreen,
      selectedModel,
      modelOptions,
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
      regenerateFromMessage,
      isLatestBotMessage
    };
  }
});
</script>

<style>
* { box-sizing: border-box; }

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: var(--app-surface);
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
}

.chat-box {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  overflow-y: auto;
  scroll-behavior: smooth;
  user-select: text;
  background: transparent;
}


.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0;
  max-width: 70%;
  gap: 10px;
  animation: bubbleUp 0.4s ease-out;
  background: transparent;
  border: none;
}

.message-right { flex-direction: row-reverse; align-self: flex-end; }

.avatar { flex-shrink: 0; width: 32px; height: 32px; }

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
  gap: 6px;
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
  width: fit-content;
  max-width: 100%;
}

.message-right .message-body {
  align-items: flex-end;
}

.content {
  background-color: var(--app-surface);
  padding: 7px 12px;
  border-radius: 12px;
  width: 100%;
  max-width: 100%;
  color: var(--app-text);
  border: 1px solid var(--app-border);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.message-right .content {
  background-color: var(--app-accent);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.35);
  align-items: flex-end;
}

.message .content img {
  max-width: 70% !important;
  height: auto !important;
  display: block !important;
  margin: 6px auto 0 !important;
}

img { max-width: 100% !important; }

.text { color: inherit; }

.chat-message-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
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
  width: 26px;
  height: 26px;
  padding: 0;
  border-radius: 50%;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.message-right .chat-copy-button,
.message-right .chat-edit-button {
  border-color: rgba(255, 255, 255, 0.45);
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
}

.chat-copy-button svg,
.chat-edit-button svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
}

.chat-copied-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
}

.evidence-card {
  margin-top: 4px;
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
  font-size: 11px;
  font-weight: 600;
  color: var(--app-text-muted);
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 999px;
  padding: 4px 10px;
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
  width: 22px;
  height: 22px;
  border-radius: 50%;
}
.rag-copied-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
}
.evidence-card summary::-webkit-details-marker { display: none; }
.evidence-body {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.35;
  max-height: 360px;
  overflow: auto;
}

.input-area {
  display: flex;
  padding: 10px 12px;
  background-color: var(--app-surface);
  border-top: 1px solid var(--app-border);
  z-index: 1;
  width: 100%;
  transition: all 0.3s ease-in-out;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.model-select {
  height: 34px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid var(--app-border);
  background: var(--app-surface-2);
  color: var(--app-text);
  font-size: 12px;
}
.model-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-area.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
  width: 100%;
  background-color: var(--app-bg);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
  animation: zoomIn 0.3s ease-in-out;
}

.input-area textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  resize: none;
  height: 38px;
  width: 100%;
  background: var(--app-surface-2);
  color: var(--app-text);
}
.input-area textarea::placeholder { color: var(--app-text-faint); }
.input-area textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.input-area.fullscreen textarea {
  height: 80%;
  margin-right: 0;
  margin-bottom: 10px;
  width: 100%;
}

.input-icons { display: flex; gap: 10px; }
.icon-button { background: none; border: none; cursor: pointer; transition: transform 0.2s; }
.icon-button:hover { transform: scale(1.15); }
.send-button:active { animation: sendAnimation 0.3s ease-in-out; }
.icon-button svg { fill: var(--app-text-muted); width: 24px; height: 24px; }
.icon-button:hover svg { fill: var(--app-accent); }
.icon-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}


.chat-box::-webkit-scrollbar { width: 10px; }
.chat-box::-webkit-scrollbar-thumb { background-color: var(--app-border); border-radius: 5px; }
.chat-box::-webkit-scrollbar-track { background-color: var(--app-surface-2); border-radius: 5px; }

@keyframes zoomIn { from { transform: scale(0.9); } to { transform: scale(1); } }
@keyframes sendAnimation { 0%{transform:translateY(0);} 50%{transform:translateY(-5px);} 100%{transform:translateY(0);} }
@keyframes bubbleUp { from{ transform: translateY(16px); opacity:0; } to{ transform: translateY(0); opacity:1; } }

.loading-message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0;
  max-width: 72%;
  animation: bubbleUp 0.4s ease-out;
}

@media (max-width: 768px) {
  .chat-box { padding: 12px; }
  .message { max-width: 88%; }
  .avatar { width: 28px; height: 28px; }
  .bubble { max-width: calc(100% - 36px); }
  .input-area { padding: 8px 10px; }
}

:root[data-theme="dark"] .chat-container,
html.dark .chat-container {
  background: #141820;
}

:root[data-theme="dark"] .content,
html.dark .content {
  background: #171c26;
  border-color: rgba(255, 255, 255, 0.08);
}

:root[data-theme="dark"] .chat-message-actions .chat-copy-button,
:root[data-theme="dark"] .chat-message-actions .chat-edit-button,
html.dark .chat-message-actions .chat-copy-button,
html.dark .chat-message-actions .chat-edit-button {
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #d9dee7;
}

:root[data-theme="dark"] .chat-copied-badge,
html.dark .chat-copied-badge {
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #c8d0dc;
}
</style>
