<template>
  <div class="ai-assistant">
    <h3>智慧工作台</h3>

    <div class="navbar">
      <button :class="{ active: currentTab === 'subtitles' }" @click="currentTab = 'subtitles'">智能字幕</button>
      <button :class="{ active: currentTab === 'chat' }" @click="currentTab = 'chat'">实时提问</button>
    </div>

    <div v-if="currentTab === 'subtitles'">
      <SubtitlesTab :subtitles="subtitlesPath" />
    </div>

    <div v-if="currentTab === 'chat'">
      <ChatTab />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SubtitlesTab from './SubtitlesTab.vue';
import ChatTab from './ChatTab.vue';

const currentTab = ref('subtitles');  // 控制当前显示的功能
const subtitlesPath = ref('/src/views/audio/audio/双序列比对工具的介绍.srt');
</script>

<style scoped>
.ai-assistant {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f4f8;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  font-size: 0.9em;
  font-family: 'Arial', sans-serif;
}

h3 {
  font-size: 1.3em;
  color: #409eff;
  margin-bottom: 15px;
  text-align: center;
  font-family: 'Arial', sans-serif;
}

.navbar {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.navbar button {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
  font-size: 1em;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.navbar button.active {
  background-color: #307fcf;
  transform: scale(1.05);
}

.navbar button:hover {
  background-color: #307fcf;
  transform: scale(1.1);
}
</style>
