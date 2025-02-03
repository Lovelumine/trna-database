<template>
  <div class="ai-assistant">
    <h3>智慧工作台</h3>

    <!-- 顶部导航栏和语言风格选择 -->
    <div class="navbar">
      <button
        :class="{ active: currentTab === 'subtitles' }"
        @click="currentTab = 'subtitles'"
      >
        智能字幕
      </button>
      <button
        :class="{ active: currentTab === 'chat' }"
        @click="currentTab = 'chat'"
      >
        实时提问
      </button>
      
      <!-- 语言风格选择下拉菜单 -->
      <select v-model="languageStyle" class="language-select">
        <option value="default">默认风格</option>
        <option value="formal">正式风格</option>
        <option value="casual">非正式风格</option>
        <option value="friendly">友好风格</option>
      </select>
    </div>

    <div v-if="currentTab === 'subtitles'">
      <SubtitlesTab :subtitles="subtitlesPath" />
    </div>

    <div v-if="currentTab === 'chat'">
      <ChatTab :languageStyle="languageStyle" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SubtitlesTab from './SubtitlesTab.vue';
import ChatTab from './ChatTab.vue';

const currentTab = ref('subtitles');  // 控制当前显示的功能
const subtitlesPath = ref('/src/views/audio/audio/双序列比对工具的介绍.srt');

// 语言风格状态变量
const languageStyle = ref('default');
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
  align-items: center;
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

/* 语言风格选择下拉菜单样式 */
.language-select {
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid #ccc;
  background-color: #fff;
  cursor: pointer;
  transition: border-color 0.3s;
}

.language-select:hover {
  border-color: #409eff;
}
</style>