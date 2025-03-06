<template>
  <div id="bot-container" ref="element" >
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
          <img v-if="message.sender === 'bot'" src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" alt="Bot Avatar" class="avatar"/>
          <img v-if="message.sender === 'user'" src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png" alt="User Avatar" class="avatar"/>
          <div class="message">
            <span v-if="message.text" v-html="message.text"></span>
            <img v-if="message.image" :src="message.image" alt="Message Image" class="message-image"/>
          </div>
        </div>
        <!-- 显示省略号 -->
        <div v-if="loading" class="message-container bot">
          <img src="https://minio.lumoxuan.cn/ensure/bot/bot-image.png" alt="Bot Avatar" class="avatar"/>
          <div class="message">
            <span>...</span>
          </div>
        </div>
      </div>
      <div id="chat-input-container">
        <input
          id="chat-input"
          v-model="newMessage"
          @keypress.enter="sendMessage"
          placeholder="Type a message..."
        />
        <input type="file" id="image-input" @change="previewImage" style="display: none;" />
        <button @click="triggerImageUpload" id="image-button">
          <i class="fas fa-camera"></i>
        </button>
        <button @click="sendMessage" id="send-button">
          <i class="fas fa-paper-plane"></i>
        </button>
        <div v-if="imagePreview" class="image-preview">
          <img :src="imagePreview" alt="Image Preview" class="image-preview-thumbnail"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, nextTick } from 'vue';
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
    // 从 .env 文件中读取 API Key
    const apiKey = import.meta.env.VITE_API_KEY;

    const { element, startDrag } = useDraggable();
    const { isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage: sendChatMessage, triggerImageUpload, previewImage } = useChat(apiKey);
    const { renderMarkdown } = useMarkdown();

    const loading = ref(false);  // 用于管理省略号状态
    const renderedMessages = ref([]);
    const chatContent = ref<HTMLDivElement | null>(null);

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

      loading.value = false;  // 停止显示省略号
    };

    return { element, startDrag, isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage, triggerImageUpload, previewImage, renderedMessages, chatContent, loading };
  }
});
</script>