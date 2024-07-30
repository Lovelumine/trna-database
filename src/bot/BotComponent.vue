<template>
  <div id="bot-container" ref="element" @mousedown="startDrag">
    <div id="bot-icon" @click="toggleChat">
      <img src="/bot-image.png" alt="Bot Icon" @dragstart.prevent />
    </div>
    <div id="chat-box" v-if="isChatOpen">
      <div id="chat-header">
        <span>Smart Web Navigator</span>
        <button @click="toggleChat" class="close-button">
          <el-icon><close /></el-icon>
        </button>
      </div>
      <div id="chat-content">
        <div v-for="message in renderedMessages" :key="message.id" :class="['message-container', message.sender]">
          <img v-if="message.sender === 'bot'" src="/bot-image.png" alt="Bot Avatar" class="avatar"/>
          <img v-if="message.sender === 'user'" src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png" alt="User Avatar" class="avatar"/>
          <div class="message">
            <span v-if="message.text" v-html="message.text"></span>
            <!-- 显示消息文本并解析 Markdown -->
            <img v-if="message.image" :src="message.image" alt="Message Image" class="message-image"/>
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
        <!-- 隐藏的文件输入，用于选择图片 -->
        <button @click="triggerImageUpload" id="image-button">
          <i class="fas fa-camera"></i>
        </button>
        <!-- 图片上传按钮，点击时触发图片选择 -->
        <button @click="sendMessage" id="send-button">
          <i class="fas fa-paper-plane"></i>
        </button>
        <!-- 发送按钮，点击时发送消息，按钮文字为 "Send" -->
        <div v-if="imagePreview" class="image-preview">
          <img :src="imagePreview" alt="Image Preview" class="image-preview-thumbnail"/>
          <!-- 图片选择成功后显示的缩略图 -->
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import { useDraggable } from './Draggable';
import { useChat } from './useChat';
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
    const { element, startDrag } = useDraggable();
    const { isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage, triggerImageUpload, previewImage } = useChat();
    const { renderMarkdown } = useMarkdown();

    // 用于存储渲染后的消息
    const renderedMessages = ref([]);

    // 监听消息列表的变化并更新渲染后的消息
    watch(messages, async (newVal) => {
      const rendered = await Promise.all(newVal.map(async message => {
        if (message.text) {
          message.text = await renderMarkdown(message.text);
        }
        return message;
      }));
      renderedMessages.value = rendered;
    }, { deep: true, immediate: true });

    return { element, startDrag, isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage, triggerImageUpload, previewImage, renderedMessages };
  }
});
</script>