<template>
  <div class="chat-container">
    <div class="chat-box" ref="chatBox">
      <div
        class="message"
        v-for="(message, index) in messages"
        :key="index"
        :class="{ 'message-right': message.sender === 'user' }"
      >
        <div class="avatar">
          <img :src="message.sender === 'user' ? userAvatar : botAvatar" alt="avatar" />
        </div>
        <div class="content">
          <div class="name">{{ message.sender === 'user' ? 'You' : 'YingYing' }}</div>
          <div class="text" v-html="renderMarkdown(message.text)"></div>
        </div>
      </div>
    </div>
    <div class="input-area">
      <textarea
        v-model="userMessage"
        @keyup.enter.exact.prevent="sendMessage"
        @keyup.enter.shift="userMessage += '\n'"  
        placeholder="Send your messages, Shift+Enter line break"
      ></textarea>
      <div class="input-icons">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import { useChat } from './useChat';
import { marked } from 'marked';
import axios from 'axios';
import SrtParser from 'srt-parser-2';

const apiKey = 'application-cbeb6f30b865f5c392edf44131f82fed'; // Replace with your actual API key
const { messages, sendMessage: sendChatMessage } = useChat(apiKey);

const botAvatar = 'src/views/audio/AiAssistant/默认头像.jpg';
const userAvatar = 'https://framerusercontent.com/images/JnbQ2qAMPu3VRXkbzDhwoMnHpk.png';

const chatBox = ref<HTMLElement | null>(null);

// 字幕数据
const subtitles = ref<Array<{ startTime: number; text: string }>>([]);
const videoElement = ref<HTMLVideoElement | null>(null);

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};

// 加载并解析 .srt 文件
const loadSubtitles = async (srtPath: string) => {
  try {
    const response = await axios.get(srtPath);
    const parser = new SrtParser();
    const parsedSubtitles = parser.fromSrt(response.data);
    subtitles.value = parsedSubtitles.map((subtitle) => ({
      startTime: parseTime(subtitle.startTime),
      text: subtitle.text,
    }));
  } catch (error) {
    console.error('Failed to load subtitles:', error);
  }
};

// 解析时间字符串为秒数
const parseTime = (timeString: string): number => {
  const [hours, minutes, seconds] = timeString.split(':');
  const [secs, ms] = seconds.split(',').map(Number);
  return (
    Number(hours) * 3600 +
    Number(minutes) * 60 +
    secs +
    ms / 1000
  );
};

// 获取最近的三条字幕
const getRecentSubtitles = (currentTime: number) => {
  const recentSubtitles = subtitles.value
    .filter(sub => sub.startTime <= currentTime)
    .slice(-3)
    .map(sub => sub.text);
  return recentSubtitles.join('\n');
};

const userMessage = ref('');

const sendMessage = async () => {
  if (userMessage.value.trim() && videoElement.value) {
    const currentTime = videoElement.value.currentTime;
    const timeString = `${Math.floor(currentTime / 60)}:${Math.floor(currentTime % 60)
      .toString()
      .padStart(2, '0')}`;
    
    const recentSubtitles = getRecentSubtitles(currentTime);

    // 仅将播放时间和字幕发送给AI，但不显示给用户
    const messageWithContext = `播放时间: ${timeString}\n最近的字幕:\n${recentSubtitles}\n\n${userMessage.value}`;

    // 发送消息给AI，并立即显示用户的原始消息
    await sendChatMessage(userMessage.value, messageWithContext);

    userMessage.value = ''; // 清空输入框
    scrollToBottom();
  }
};

const renderMarkdown = (text: string) => {
  return marked(text);
};

// 组件挂载后加载字幕
onMounted(() => {
  const srtPath = '/src/views/audio/audio/双序列比对工具的介绍.srt';
  loadSubtitles(srtPath);
  videoElement.value = document.querySelector('video');
});

watch(messages, scrollToBottom, { deep: true, immediate: true });
</script>

<style scoped>
/* 样式代码保持不变 */
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
  background-color: #fff;
  border-radius: 0px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: calc(100vh - 96px - 40px);
  overflow-y: auto;
  scroll-behavior: smooth;
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
  background-color: #e6f7ff;
  padding: 10px 15px;
  border-radius: 8px;
  max-width: 120%;
}

.message-right .content {
  background-color: #bae7ff;
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

.input-area textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: none;
  height: 40px;
  width: calc(100% - 90px);
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
