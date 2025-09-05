<template>
  <div id="bot-container" ref="element">
    <div id="bot-icon" @click="toggleChat" @mousedown="startDrag">
      <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" alt="Bot Icon" @dragstart.prevent />
    </div>

    <div id="chat-box" v-if="isChatOpen">
      <div id="chat-header" @mousedown="startDrag">
        <span>AI Web Navigator</span>
        <button @click="toggleChat" class="close-button">
          <el-icon><close /></el-icon>
        </button>
      </div>

      <!-- AI 英文提示 -->
      <div id="ai-tip" role="note" aria-live="polite">
        <span class="ai-tip-icon" aria-hidden="true">ℹ️</span>
        <span class="ai-tip-text">{{ aiTip }}</span>
      </div>

      <div id="chat-content" ref="chatContent">
        <!-- 主消息流：证据块跟在每条 bot 消息后 -->
        <template v-for="(msg, i) in safeMessages" :key="msg.id ?? i">
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
              <span v-if="msg.textHtml" v-html="msg.textHtml"></span>
              <img v-if="msg.image" :src="msg.image" class="message-image" />
            </div>
          </div>

          <!-- 证据块：仅 bot 且存在 evidenceHtml 时渲染；默认折叠，紧跟消息 -->
          <div
            v-if="(msg.sender || 'bot') === 'bot' && msg.evidenceHtml"
            class="evidence-card"
          >
            <details>
              <summary>Search results (RAG)</summary>
              <div class="evidence-body" v-html="msg.evidenceHtml"></div>
            </details>
          </div>
        </template>

        <!-- Loading -->
        <div v-if="loading" class="message-container bot">
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
            v-model="newMessage"
            @keypress.enter="sendMessage"
            :placeholder="inputPlaceholder"
          />
          <button @click="sendMessage" id="send-button">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>

        <input type="file" id="image-input" @change="previewImage" style="display: none;" />
        <div v-if="imagePreview" class="image-preview">
          <img :src="imagePreview" alt="Image Preview" class="image-preview-thumbnail" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, nextTick, onMounted, onBeforeUnmount, computed } from 'vue';
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
    const {
      isChatOpen,
      messages,
      newMessage,
      newImage,
      imagePreview,
      toggleChat,
      sendMessage: sendChatMessage,
      triggerImageUpload,
      previewImage
    } = useChat(apiKey);
    const { renderMarkdown } = useMarkdown();

    const loading = ref(false);
    const renderedMessages = ref<any[]>([]);
    const chatContent = ref<HTMLDivElement | null>(null);

    const showExampleQuestions = ref(true);

    const aiTip = ref(
      'Note: AI-generated responses may be inaccurate. Please verify important information.'
    );
    const inputPlaceholder = ref('Type a message...');

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
      if (isChatOpen.value && showExampleQuestions.value) await enableSliderInteractions();
    };

    onMounted(async () => {
      const hasSentMessage = localStorage.getItem('hasSentMessage');
      if (hasSentMessage === 'true') showExampleQuestions.value = false;
      await rebindSlider();
    });
    onBeforeUnmount(() => cleanupFns.forEach(fn => fn()));
    watch([isChatOpen, showExampleQuestions], rebindSlider);

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

    watch(
      messages,
      async (newVal) => {
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

            if (msg.text) msg.textHtml = await renderMarkdown(String(msg.text));
            if (msg.evidence) msg.evidenceHtml = await renderMarkdown(String(msg.evidence));
            return msg;
          })
        );

        renderedMessages.value = rendered;

        await nextTick();
        if (chatContent.value) chatContent.value.scrollTop = chatContent.value.scrollHeight;
      },
      { deep: true, immediate: true }
    );

    /* -------- 发送 -------- */
    const sendMessage = async () => {
      if (!newMessage.value?.trim()) return;
      loading.value = true;
      await sendChatMessage();
      loading.value = false;
      showExampleQuestions.value = false;
      localStorage.setItem('hasSentMessage', 'true');
    };

    const fillExample = (example: string) => { newMessage.value = example; };

    return {
      element, startDrag, isChatOpen,
      messages, newMessage, newImage, imagePreview,
      toggleChat, sendMessage, triggerImageUpload, previewImage,
      renderedMessages, safeMessages, chatContent,
      loading, fillExample, showExampleQuestions, exampleWrap,
      aiTip, inputPlaceholder
    };
  }
});
</script>

<style scoped>
/* ——AI 提示条—— */
#ai-tip{
  display:flex; align-items:center; gap:6px;
  font-size:12px; color:#6b7280; background:#f9fafb;
  border-left:3px solid #e5e7eb; padding:6px 10px;
  margin:8px 10px 6px 10px; border-radius:6px;
}
.ai-tip-icon{ line-height:1; }
.ai-tip-text{ line-height:1.3; }

/* ——消息区—— */
#chat-content{ overflow-y:auto; }
.message-container{ display:flex; align-items:flex-start; gap:0; margin:10px 8px 6px; }
.message-container.user{ flex-direction:row-reverse; }
.avatar{ width:36px; height:36px; flex:0 0 36px; border-radius:50%; object-fit:cover; object-position:center; display:block; }
.message{ max-width:85%; padding:3px 6px; border-radius:1px; line-height:1.3; word-break:break-word; background:#f5f7fb; color:#1f2328; }
.message-container.user .message{ background:#1e80ff; color:#fff; }
.message-image{ display:block; max-width:260px; border-radius:8px; margin-top:6px; }

/* ——RAG 证据卡片（默认折叠 + 紧凑 + 高度限制）—— */
.evidence-card {
  max-width: 85%;
  margin: 2px 8px 8px 44px;     /* 紧跟 bot 气泡，留左侧头像位 */
}
.evidence-card details {
  background: #fffdf4;
  border: 1px solid #f5e6b3;
  border-left: 3px solid #f59e0b;
  border-radius: 8px;
  padding: 4px 8px;
}
.evidence-card summary {
  cursor: pointer;
  list-style: none;
  font-size: 12px;
  font-weight: 600;
  color: #9a6b00;
  line-height: 1.2;
}
.evidence-card summary::-webkit-details-marker { display: none; }
/* 折叠内容更紧凑并限制高度 */
.evidence-body {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.35;
  max-height: 140px;            /* 👈 控制最大高度 */
  overflow: auto;
}
.evidence-body :where(img){ max-width:100%; border-radius:6px; }

/* ——示例问题（父容器横向滚动）—— */
#example-questions{
  width:100%;
  overflow-x:auto;
  overflow-y:hidden;
  margin-bottom:10px;
  padding:6px 8px;
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
  background:linear-gradient(135deg,#007bff,#0056b3);
  border:none;
  border-radius:16px;
  cursor:pointer;
  transition:all .2s ease;
  white-space:nowrap;
}
#question-slider button:hover{
  background:linear-gradient(135deg,#0056b3,#003f7f);
  transform:translateY(-1px);
}

/* ——输入区—— */
#input-area{ display:flex; gap:8px; align-items:center; width:100%; }
#chat-input{ flex-grow:1; padding:10px; font-size:16px; border:1px solid #ccc; border-radius:20px; outline:none; }
#send-button{ background:#007bff; color:#fff; padding:10px 16px; border:none; border-radius:20px; cursor:pointer; transition:all .3s ease; }
#send-button:hover{ background:#0056b3; }
</style>
