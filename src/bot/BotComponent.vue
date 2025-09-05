<template>
  <div id="bot-container" ref="element">
    <div id="bot-icon" @click="toggleChat" @mousedown="startDrag">
      <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" alt="Bot Icon" @dragstart.prevent />
    </div>

    <div id="chat-box" v-if="isChatOpen">
      <div id="chat-header" @mousedown="startDrag">
        <span>Smart Web Navigator</span>
        <button @click="toggleChat" class="close-button">
          <el-icon><close /></el-icon>
        </button>
      </div>

      <div id="chat-content" ref="chatContent">
        <div
          v-for="message in renderedMessages"
          :key="message.id"
          :class="['message-container', message.sender]"
        >
          <!-- 头像 -->
          <img
            v-if="message.sender === 'bot'"
            src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png"
            class="avatar"
            alt=""
          />
          <img
            v-if="message.sender === 'user'"
            src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png"
            class="avatar"
            alt=""
          />

          <!-- 气泡 -->
          <div class="message">
            <span v-if="message.text" v-html="message.text"></span>
            <img v-if="message.image" :src="message.image" class="message-image" />
          </div>
        </div>

        <!-- 省略号 Loading -->
        <div v-if="loading" class="message-container bot">
          <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" class="avatar" alt="" />
          <div class="message"><span>...</span></div>
        </div>
      </div>

      <div id="chat-input-container">
        <!-- 示例问题 -->
        <div id="example-questions" v-if="showExampleQuestions">
          <div id="question-slider" ref="slider">
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
            placeholder="Type a message..."
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
import { defineComponent, ref, watch, nextTick, onMounted } from 'vue';
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
    const slider = ref<HTMLDivElement | null>(null);

    const showExampleQuestions = ref(true);

    onMounted(() => {
      const hasSentMessage = localStorage.getItem('hasSentMessage');
      if (hasSentMessage === 'true') showExampleQuestions.value = false;
    });

    watch(
      messages,
      async (newVal) => {
        const rendered = await Promise.all(
          newVal.map(async (m: any) => {
            if (m.text) m.text = await renderMarkdown(m.text);
            return m;
          })
        );
        renderedMessages.value = rendered;

        await nextTick();
        if (chatContent.value) {
          chatContent.value.scrollTop = chatContent.value.scrollHeight;
        }
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
      element, startDrag, isChatOpen, messages,
      newMessage, newImage, imagePreview, toggleChat, sendMessage,
      triggerImageUpload, previewImage, renderedMessages, chatContent,
      loading, fillExample, showExampleQuestions, slider
    };
  }
});
</script>

<style scoped>
/* ——示例问题，保持原样—— */
#example-questions {
  width: 100%;
  overflow-x: auto;
  white-space: nowrap;
  margin-bottom: 10px;
  padding: 8px;
}
#question-slider {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 5px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
#question-slider::-webkit-scrollbar { display: none; }
#question-slider button {
  flex: 0 0 auto;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(135deg, #007bff, #0056b3);
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all .3s ease;
  white-space: nowrap;
}
#question-slider button:hover {
  background: linear-gradient(135deg, #0056b3, #003f7f);
  transform: scale(1.05);
}

/* ——消息行：不改变窗口大小，仅优化间距/圆角与头像裁切—— */
#chat-content { overflow-y: auto; }

/* 头像与气泡的间距从 8px 缩小为 6px */
.message-container {
  display: flex;
  align-items: flex-start; /* 顶对齐 */
  gap: 0px;                /* 关键：缩小间距 */
  margin: 10px 8px;
}

/* 用户头像在右侧 */
.message-container.user { flex-direction: row-reverse; }

/* 头像固定方形，居中裁切，不拉伸 */
.avatar {
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  border-radius: 50%;
  object-fit: cover;
  object-position: center;
  display: block;
}

/* 气泡圆角从 14px 调为 10px */
.message {
  max-width: 85%;
  padding: 3px 6px;
  border-radius: 1px;     /* 关键：减小圆角 */
  line-height: 1.3;
  word-break: break-word;
  background: #f5f7fb;
  color: #1f2328;
}
.message-container.user .message {
  background: #1e80ff;
  color: #fff;
}

/* 图片消息 */
.message-image {
  display: block;
  max-width: 260px;
  border-radius: 8px;
  margin-top: 6px;
}

/* ——输入区，保持原样—— */
#input-area {
  display: flex;
  gap: 8px;
  align-items: center;
  width: 100%;
}
#chat-input {
  flex-grow: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 20px;
  outline: none;
}
#send-button {
  background-color: #007bff;
  color: #fff;
  padding: 10px 16px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all .3s ease;
}
#send-button:hover { background-color: #0056b3; }
</style>
