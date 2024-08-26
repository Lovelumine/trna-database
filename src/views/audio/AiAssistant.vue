<template>
    <div class="ai-assistant">
      <h3>AI Assistant</h3>
      
      <div class="subtitle-container">
        <div class="subtitle-header">
          <h3>智能字幕</h3>
          <button @click="toggleExpand">{{ expanded ? '切换为字幕视图' : '切换为文章视图' }}</button>
        </div>
        <ul v-if="!expanded" class="subtitle-list">
          <li
            v-for="(subtitle, index) in visibleSubtitles"
            :key="index"
            @click="seekTo(subtitle.startTime)"
            :class="{ current: isCurrentSubtitle(subtitle.startTime) }"
            class="subtitle-item"
          >
            {{ subtitle.text }}
          </li>
        </ul>
        <div v-else class="subtitle-expanded">
          <p>
            <span
              v-for="(subtitle, index) in subtitles"
              :key="index"
              @click="seekTo(subtitle.startTime)"
              class="subtitle-sentence"
              :class="{ current: isCurrentSubtitle(subtitle.startTime) }"
            >
              {{ subtitle.text }}。
            </span>
          </p>
        </div>
      </div>
      
      <div class="chat-container">
        <div class="chat-history">
          <div v-for="(msg, index) in chatHistory" :key="index" class="chat-message">
            <p class="user-message"><strong>User:</strong> {{ msg.user }}</p>
            <p class="ai-message"><strong>AI:</strong> {{ msg.ai }}</p>
          </div>
        </div>
        <div class="input-container">
          <textarea v-model="inputText" placeholder="Ask me something..."></textarea>
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue';
  import SrtParser from 'srt-parser-2';
  import axios from 'axios';
  
  const inputText = ref('');
  const chatHistory = ref<{ user: string; ai: string }[]>([]);
  const subtitles = ref<{ startTime: number; text: string }[]>([]);
  const currentTime = ref(0);
  const expanded = ref(false);
  
  const visibleSubtitles = ref<{ startTime: number; text: string }[]>([]);
  
  const sendMessage = () => {
    if (inputText.value.trim()) {
      const aiResponse = `Response to: ${inputText.value}`; // 简单模拟AI的回复
      chatHistory.value.push({ user: inputText.value, ai: aiResponse });
      inputText.value = '';
    }
  };
  
  const seekTo = (time: number) => {
    const video = document.querySelector('video');
    if (video && !isNaN(time)) {
      video.currentTime = time;
      video.play();
    } else {
      console.error('Invalid time or video element not found.');
    }
  };
  
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
  
  const toggleExpand = () => {
    expanded.value = !expanded.value;
  };
  
  const isCurrentSubtitle = (time: number) => {
    return time <= currentTime.value && currentTime.value < time + 2;
  };
  
  onMounted(async () => {
    try {
      const response = await axios.get('/src/views/audio/audio/氨酰-tRNA的合成.srt');
      const parser = new SrtParser();
      const parsedSubtitles = parser.fromSrt(response.data);
  
      subtitles.value = parsedSubtitles.map((subtitle) => ({
        startTime: parseTime(subtitle.startTime),
        text: subtitle.text,
      }));
  
      // 每秒更新一次当前时间，来确定显示哪些字幕
      setInterval(() => {
        const video = document.querySelector('video');
        if (video) {
          currentTime.value = video.currentTime;
        }
      }, 500);
    } catch (error) {
      console.error('Failed to load subtitles:', error);
    }
  });
  
  // 根据当前播放时间更新可见字幕
  watch(currentTime, (newTime) => {
    const currentIndex = subtitles.value.findIndex(
      (subtitle) => subtitle.startTime > newTime
    );
  
    visibleSubtitles.value = subtitles.value.slice(
      Math.max(0, currentIndex - 1),
      currentIndex + 2
    );
  });
  </script>
  
  <style scoped>
  .ai-assistant {
    margin-top: 20px;
    padding: 15px;
    background-color: #f0f4f8;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    font-size: 0.9em; /* 字体缩小一点 */
  }
  
  h3 {
    font-size: 1.3em;
    color: #409eff;
    margin-bottom: 15px;
    text-align: center;
  }
  
  .chat-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .chat-history {
    max-height: 300px;
    overflow-y: auto;
    padding: 8px;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
  }
  
  .chat-message {
    margin-bottom: 8px;
    padding: 8px;
    border-radius: 8px;
    background-color: #e6f7ff;
    transition: background-color 0.3s;
  }
  
  .user-message {
    color: #333;
    margin-bottom: 4px;
  }
  
  .ai-message {
    color: #007bff;
  }
  
  .input-container {
    display: flex;
    gap: 8px;
  }
  
  textarea {
    flex: 1;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #ccc;
    resize: none;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
  }
  
  textarea:focus {
    border-color: #409eff;
    outline: none;
  }
  
  button {
    padding: 8px 16px;
    background-color: #409eff;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  button:hover {
    background-color: #307fcf;
  }
  
  /* 智能字幕样式 */
  .subtitle-container {
    margin-top: 15px;
    padding: 8px;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .subtitle-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  
  .subtitle-list {
    list-style: none;
    padding: 0;
    margin: 0;
    max-height: 150px;
    overflow-y: auto;
  }
  
  .subtitle-item {
    padding: 6px;
    border-bottom: 1px solid #ddd;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .subtitle-item:hover,
  .subtitle-item.current {
    background-color: #e0f0ff;
    color: #409eff;
  }
  
  .subtitle-expanded p {
    margin: 0;
    padding: 6px 0;
    line-height: 1.6; /* 行高调整，使段落更紧凑 */
    text-align: justify; /* 使段落对齐 */
  }
  
  .subtitle-sentence {
    cursor: pointer;
    transition: color 0.3s;
  }
  
  .subtitle-sentence:hover,
  .subtitle-sentence.current {
    color: #409eff;
  }
  
  .subtitle-expanded {
    padding: 0 10px;
    text-align: justify;
  }
  
  .subtitle-expanded p::after {
    content: "";
  }
  </style>
  