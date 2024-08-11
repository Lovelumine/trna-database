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
          <div class="text" v-html="message.text"></div>
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
  components: {
    ElDialog,
  },
  props: {
    selectedMenuId: {
      type: Number,
      required: true
    },
    selectedSceneId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    let apiKey = import.meta.env.VITE_API_KEY_DEFAULT; 
    if (props.selectedMenuId === 1 && props.selectedSceneId === 1) {
      apiKey = import.meta.env.VITE_API_KEY_11;
    }

    const { messages, newMessage, sendMessage } = useChat(apiKey);
    const isFullscreen = ref(false);
    const chatBox = ref(null);
    const dialogVisible = ref(false);

    const botAvatar = 'https://framerusercontent.com/images/p0mVMX1aJictMR1RM9fE1PrTrRQ.png';
    const userAvatar = 'https://framerusercontent.com/images/JnbQ2qAMPu3VRXkbzDhwoMnHpk.png';

    const { renderMarkdown } = useMarkdown();
    const renderedMessages = ref([]);

    const scrollToBottom = async () => {
      await nextTick();
      if (chatBox.value) {
        chatBox.value.scrollTop = chatBox.value.scrollHeight;
      }
    };

    watch(messages, async (newVal) => {
      const rendered = await Promise.all(newVal.map(async message => {
        if (message.text) {
          message.text = await renderMarkdown(message.text);
        }
        return message;
      }));
      renderedMessages.value = rendered;
      scrollToBottom();
    }, { deep: true, immediate: true });

    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value;
    };

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
    };
  },
});
</script>


<style scoped>

* {
  box-sizing: border-box;
}


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
  scroll-behavior: smooth; /* 添加平滑滚动 */
}


.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  max-width: 60%;
  animation: bubbleUp 0.5s ease-out;
}

.message-right {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.message-right .avatar {
  margin-right: 0;
  margin-left: 10px;
}

.avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.content {
  background-color: #e6f7ff; /* 修改默认颜色 */
  padding: 10px 15px;
  border-radius: 8px;
  max-width: 120%;
}


img {
  max-width: 100% !important;
}

.message-right .content {
  background-color: #bae7ff; /* 修改默认颜色 */
}

.name {
  font-weight: bold;
  margin-bottom: 5px;
}

.text {
  color: #333;
}

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
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
  animation: zoomIn 0.3s ease-in-out;
}

.input-area textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: none;
  height: 40px;
  width: calc(100% - 90px); /* 留出图标按钮的空间 */
}

.input-area.fullscreen textarea {
  height: 80%;
  margin-right: 0;
  margin-bottom: 10px;
  width: 100%;
}

.input-icons {
  display: flex;
  gap: 10px;
}

.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  transition: transform 0.2s;
}

.icon-button:hover {
  transform: scale(1.2);
}

.send-button:active {
  animation: sendAnimation 0.3s ease-in-out;
}

.icon-button svg {
  fill: #888;
  width: 24px;
  height: 24px;
}

.icon-button:hover svg {
  fill: #4677ff;
}

/* 自定义滚动条 */
.chat-box::-webkit-scrollbar {
  width: 10px;
}

.chat-box::-webkit-scrollbar-thumb {
  background-color: #7a9bf4;
  border-radius: 5px;
}

.chat-box::-webkit-scrollbar-track {
  background-color: #f0f0f5;
  border-radius: 5px;
}

/* 动画效果 */
@keyframes zoomIn {
  from {
    transform: scale(0.9);
  }
  to {
    transform: scale(1);
  }
}

@keyframes sendAnimation {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
  100% {
    transform: translateY(0);
  }
}

@keyframes bubbleUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>