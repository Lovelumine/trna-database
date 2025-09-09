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
        <div class="content">
          <div class="name">{{ message.sender === 'user' ? 'You' : 'YingYing' }}</div>
          <!-- 改：使用渲染后的 textHtml -->
          <div class="text" v-html="message.textHtml"></div>

          <!-- 新增：证据块，紧跟 bot 消息，默认折叠 -->
          <div
            v-if="message.sender !== 'user' && message.evidenceHtml"
            class="evidence-card"
          >
            <details>
              <summary>Search results (RAG)</summary>
              <div class="evidence-body" v-html="message.evidenceHtml"></div>
            </details>
          </div>
        </div>
      </div>

      <!-- 显示省略号 -->
      <div v-if="loading" class="message loading-message">
        <div class="avatar">
          <img :src="botAvatar" alt="avatar" />
        </div>
        <div class="content">
          <div class="name">YingYing</div>
          <div class="text">...</div>
        </div>
      </div>
    </div>

    <div class="input-area" :class="{ fullscreen: isFullscreen }">
      <textarea
        v-model="newMessage"
        @keyup.enter.exact.prevent="sendMessage"
        @keyup.enter.shift="newMessage += '\n'"
        placeholder="Send your messages, Shift+Enter line break"
      ></textarea>
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
        <button @click="sendMessage" class="icon-button send-button">
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

    <el-dialog :visible.sync="dialogVisible" title="提示">
      <p>当前回复尚未完成，请稍后再试。</p>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, nextTick } from 'vue';
import { useChat } from '../../../utils/useChat';
import { useMarkdown } from '../../../utils/useMarkdown';
import { ElDialog } from 'element-plus';
import 'element-plus/dist/index.css';

export default defineComponent({
  name: 'ChatBox',
  components: { ElDialog },
  props: {
    selectedMenuId: { type: Number, required: true },
    selectedSceneId: { type: Number, required: true }
  },
  setup(props) {
    const getApiKey = () => {
      if (props.selectedMenuId === 1 && props.selectedSceneId === 1) {
        return import.meta.env.VITE_API_KEY_11;
      }
      return import.meta.env.VITE_API_KEY_DEFAULT;
    };

    const apiKey = ref(getApiKey());
    const { messages, newMessage, sendMessage: sendChatMessage, resetChat } = useChat(apiKey.value);
    const isFullscreen = ref(false);
    const chatBox = ref<HTMLElement | null>(null);
    const dialogVisible = ref(false);
    const loading = ref(false);

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
            } else {
              msg.textHtml = '';
              msg.evidenceHtml = '';
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
      if (!newMessage.value.trim()) return;
      loading.value = true;
      await sendChatMessage();
      loading.value = false;
    };

    watch([() => props.selectedMenuId, () => props.selectedSceneId], async () => {
      apiKey.value = getApiKey();
      await resetChat(apiKey.value);
    });

    return {
      newMessage,
      renderedMessages,
      sendMessage,
      isFullscreen,
      toggleFullscreen,
      chatBox,
      dialogVisible,
      botAvatar,
      userAvatar,
      loading
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
}

.chat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  margin-top: 60px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: calc(100vh - 96px - 40px);
  overflow-y: auto;
  z-index: 2;
  scroll-behavior: smooth;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  max-width: 60%;
  animation: bubbleUp 0.5s ease-out;
}

.message-right { flex-direction: row-reverse; align-self: flex-end; }

.avatar { flex-shrink: 0; width: 40px; height: 40px; margin-right: 10px; }
.message-right .avatar { margin-right: 0; margin-left: 10px; }

.avatar img {
  width: 100%; height: 100%; border-radius: 50%; object-fit: cover; object-position: center;
}

.content { background-color: #e6f7ff; padding: 10px 15px; border-radius: 8px; max-width: 120%; }

/* General rule for all images */
/* 确保图片大小被正确限制 */
.message .content img {
  max-width: 50% !important;  /* 确保图像宽度不超过 70% */
  height: auto !important;    /* 保持图片的纵横比 */
  display: block !important;  /* 确保图片是块级元素 */
  margin: 0 auto !important; /* 将图片居中 */
}

img { max-width: 100% !important; }

.message-right .content { background-color: #bae7ff; }

.name { font-weight: bold; margin-bottom: 5px; }
.text { color: #333; }

/* 证据块：紧凑、默认折叠、限制高度 */
.evidence-card { margin-top: 6px; }
.evidence-card details {
  background: #fffdf4;
  border: 1px solid #f5e6b3;
  border-left: 3px solid #f59e0b;
  border-radius: 6px;
  padding: 4px 8px;
}
.evidence-card summary {
  cursor: pointer;
  list-style: none;
  font-size: 12px;
  font-weight: 600;
  color: #9a6b00;
}
.evidence-card summary::-webkit-details-marker { display: none; }
.evidence-body {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.35;
  max-height: 440px;   /* 控制高度，避免撑开窗口 */
  overflow: auto;
}

/* 输入区保持不变 */
.input-area {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #fff;
  z-index: 1;
  width: 100%;
  transition: all 0.3s ease-in-out;
}

.input-area.fullscreen {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  z-index: 1000; flex-direction: column; justify-content: center; padding: 20px;
  width: 100%; background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3); animation: zoomIn 0.3s ease-in-out;
}

.input-area textarea {
  flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px;
  resize: none; height: 40px; width: calc(100% - 90px);
}
.input-area.fullscreen textarea { height: 80%; margin-right: 0; margin-bottom: 10px; width: 100%; }

.input-icons { display: flex; gap: 10px; }
.icon-button { background: none; border: none; cursor: pointer; transition: transform 0.2s; }
.icon-button:hover { transform: scale(1.2); }
.send-button:active { animation: sendAnimation 0.3s ease-in-out; }
.icon-button svg { fill: #888; width: 24px; height: 24px; }
.icon-button:hover svg { fill: #4677ff; }

/* 自定义滚动条 */
.chat-box::-webkit-scrollbar { width: 10px; }
.chat-box::-webkit-scrollbar-thumb { background-color: #7a9bf4; border-radius: 5px; }
.chat-box::-webkit-scrollbar-track { background-color: #f0f0f5; border-radius: 5px; }

/* 动画 */
@keyframes zoomIn { from { transform: scale(0.9); } to { transform: scale(1); } }
@keyframes sendAnimation { 0%{transform:translateY(0);} 50%{transform:translateY(-5px);} 100%{transform:translateY(0);} }
@keyframes bubbleUp { from{ transform: translateY(20px); opacity:0; } to{ transform: translateY(0); opacity:1; } }

/* loading 样式保持 */
.loading-message {
  display: flex; align-items: flex-start; margin-bottom: 20px; max-width: 60%;
  animation: bubbleUp 0.5s ease-out;
}
</style>
