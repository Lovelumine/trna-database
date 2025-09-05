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
        <div v-for="message in renderedMessages" :key="message.id" :class="['message-container', message.sender]">
          <img v-if="message.sender === 'bot'"
               src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png"
               class="avatar" alt="" />
          <img v-if="message.sender === 'user'"
               src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png"
               class="avatar" alt="" />
          <div class="message">
            <span v-if="message.text" v-html="message.text"></span>
            <img v-if="message.image" :src="message.image" class="message-image" />
          </div>
        </div>

        <div v-if="loading" class="message-container bot">
          <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" class="avatar" alt="" />
          <div class="message"><span>...</span></div>
        </div>
      </div>

      <div id="chat-input-container">
        <!-- ✅ 让父容器成为滚动容器 -->
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
import { defineComponent, ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
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
      isChatOpen, messages, newMessage, newImage, imagePreview,
      toggleChat, sendMessage: sendChatMessage, triggerImageUpload, previewImage
    } = useChat(apiKey);
    const { renderMarkdown } = useMarkdown();

    const loading = ref(false);
    const renderedMessages = ref<any[]>([]);
    const chatContent = ref<HTMLDivElement | null>(null);

    const showExampleQuestions = ref(true);

    const aiTip = ref('Note: AI-generated responses may be inaccurate. Please verify important information.');
    const inputPlaceholder = ref('Type a message...');

    // 父容器（滚动容器）
    const exampleWrap = ref<HTMLDivElement | null>(null);
    let cleanupFns: Array<() => void> = [];

    // 绑定滚动/拖拽
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

      // 鼠标滚轮 -> 横向
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

    // 渲染消息
    watch(
      messages,
      async (newVal) => {
        const rendered = await Promise.all(newVal.map(async (m: any) => {
          if (m.text) m.text = await renderMarkdown(m.text);
          return m;
        }));
        renderedMessages.value = rendered;
        await nextTick();
        chatContent.value && (chatContent.value.scrollTop = chatContent.value.scrollHeight);
      },
      { deep: true, immediate: true }
    );

    const sendMessage = async () => {
      if (!newMessage.value.trim()) return;
      loading.value = true;
      await sendChatMessage();
      loading.value = false;
      showExampleQuestions.value = false;
      localStorage.setItem('hasSentMessage', 'true');
    };

    const fillExample = (example: string) => { newMessage.value = example; };

    return {
      element, startDrag, isChatOpen, messages, newMessage, newImage, imagePreview,
      toggleChat, sendMessage, triggerImageUpload, previewImage,
      renderedMessages, chatContent, loading, fillExample, showExampleQuestions,
      aiTip, inputPlaceholder, exampleWrap
    };
  }
});
</script>

<style scoped>
/* ——示例问题（父容器滚动）—— */
#example-questions{
  width: 100%;
  overflow-x: auto;           /* 父容器负责滚动 */
  overflow-y: hidden;
  margin-bottom: 10px;
  padding: 6px 8px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
#example-questions::-webkit-scrollbar{ display:none; }

/* 子容器不收缩，确保内容能超过父容器宽度 */
#question-slider{
  display: inline-flex;
  flex-wrap: nowrap;
  gap: 8px;
  white-space: nowrap;
  min-width: max-content;     /* 关键：不要收缩为父宽 */
}

/* 更小更紧凑的按钮 */
#question-slider button{
  flex: 0 0 auto;
  padding: 6px 10px;
  font-size: 12px;            /* 已调小 */
  line-height: 1;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(135deg,#007bff,#0056b3);
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all .2s ease;
  white-space: nowrap;
}
#question-slider button:hover{
  background: linear-gradient(135deg,#0056b3,#003f7f);
  transform: translateY(-1px);
}

/* ——AI 提示条—— */
#ai-tip{
  display:flex; align-items:center; gap:6px;
  font-size:12px; color:#6b7280; background:#f9fafb;
  border-left:3px solid #e5e7eb; padding:6px 10px;
  margin:8px 10px 6px 10px; border-radius:6px;
}
.ai-tip-icon{ line-height:1; }
.ai-tip-text{ line-height:1.3; }

/* ——消息区、输入区（保持原样）—— */
#chat-content{ overflow-y:auto; }
.message-container{ display:flex; align-items:flex-start; gap:0; margin:10px 8px; }
.message-container.user{ flex-direction:row-reverse; }
.avatar{ width:36px; height:36px; flex:0 0 36px; border-radius:50%; object-fit:cover; object-position:center; display:block; }
.message{ max-width:85%; padding:3px 6px; border-radius:1px; line-height:1.3; word-break:break-word; background:#f5f7fb; color:#1f2328; }
.message-container.user .message{ background:#1e80ff; color:#fff; }
.message-image{ display:block; max-width:260px; border-radius:8px; margin-top:6px; }

#input-area{ display:flex; gap:8px; align-items:center; width:100%; }
#chat-input{ flex-grow:1; padding:10px; font-size:16px; border:1px solid #ccc; border-radius:20px; outline:none; }
#send-button{ background:#007bff; color:#fff; padding:10px 16px; border:none; border-radius:20px; cursor:pointer; transition:all .3s ease; }
#send-button:hover{ background:#0056b3; }
</style>
