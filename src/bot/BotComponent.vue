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
  <div v-for="message in renderedMessages" :key="message.id" :class="['message-container', message.sender]">
    <img v-if="message.sender === 'bot'" src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" class="avatar" />
    <img v-if="message.sender === 'user'" src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png" class="avatar" />
    <div class="message">
      <span v-if="message.text" v-html="message.text"></span>
      <img v-if="message.image" :src="message.image" class="message-image" />
    </div>
  </div>

  <!-- 添加省略号 -->
  <div v-if="loading" class="message-container bot">
    <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" class="avatar" />
    <div class="message">
      <span>...</span>
    </div>
  </div>
</div>

      <div id="chat-input-container">
        <!-- 示例问题（支持水平滚动条，不换行），用户发送消息后隐藏 -->
        <div id="example-questions" v-if="showExampleQuestions">
          <div id="question-slider" ref="slider">
            <button @click="fillExample('What are the main features of ENSURE?')">What are the main features of ENSURE?</button>
            <button @click="fillExample('What is sup-tRNA?')">What is sup-tRNA?</button>
            <button @click="fillExample('How does RNA sequencing work?')">How does RNA sequencing work?</button>
            <button @click="fillExample('Explain the role of ncRNA.')">Explain the role of ncRNA.</button>
          </div>
        </div>

        <!-- 输入框和发送按钮在第二行 -->
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
  components: {
    ElIcon,
    Close
  },
  setup() {
    const apiKey = import.meta.env.VITE_API_KEY;

    const { element, startDrag } = useDraggable();
    const { isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage: sendChatMessage, triggerImageUpload, previewImage } = useChat(apiKey);
    const { renderMarkdown } = useMarkdown();

    const loading = ref(false);
    const renderedMessages = ref([]);
    const chatContent = ref<HTMLDivElement | null>(null);
    const slider = ref<HTMLDivElement | null>(null);

    // 是否显示示例问题（基于 localStorage）
    const showExampleQuestions = ref(true);

    onMounted(() => {
      const hasSentMessage = localStorage.getItem('hasSentMessage');
      if (hasSentMessage === 'true') {
        showExampleQuestions.value = false;
      }
    });

    watch(messages, async (newVal) => {
      const rendered = await Promise.all(newVal.map(async message => {
        if (message.text) {
          message.text = await renderMarkdown(message.text);
        }
        return message;
      }));
      renderedMessages.value = rendered;

      // 在渲染完成后将消息框滚动到底部
      await nextTick(); // 等待 DOM 更新
      if (chatContent.value) {
        chatContent.value.scrollTop = chatContent.value.scrollHeight;
      }
    }, { deep: true, immediate: true });

    const sendMessage = async () => {
      if (!newMessage.value.trim()) return;

      loading.value = true;  // 开始显示省略号

      // 发送消息
      await sendChatMessage();
      loading.value = false;

      // 用户发送过消息后隐藏示例问题，并存入 localStorage
      showExampleQuestions.value = false;
      localStorage.setItem('hasSentMessage', 'true');
    };

    const fillExample = (example: string) => {
      newMessage.value = example;
    };

    return { element, startDrag, isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage, triggerImageUpload, previewImage, renderedMessages, chatContent, loading, fillExample, showExampleQuestions, slider };
  }
});
</script>

<style scoped>
/* 示例问题：水平滚动条 */
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

#question-slider::-webkit-scrollbar {
  display: none;
}

#question-slider button {
  flex: 0 0 auto;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  background: linear-gradient(135deg, #007bff, #0056b3);
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

#question-slider button:hover {
  background: linear-gradient(135deg, #0056b3, #003f7f);
  transform: scale(1.05);
}

/* 输入框和发送按钮 */
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
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

#send-button:hover {
  background-color: #0056b3;
}
</style>