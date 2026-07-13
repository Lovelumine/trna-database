<template>
  <div class="ai-assistant">
    <h3>智慧工作台</h3>

    <div class="navbar">
      <button :class="{ active: currentTab === 'subtitles' }" @click="currentTab = 'subtitles'">智能字幕</button>
      <button :class="{ active: currentTab === 'chat' }" @click="currentTab = 'chat'">实时提问</button>

      <select v-model="languageStyle" class="language-select">
        <option value="default">默认风格</option>
        <option value="formal">正式风格</option>
        <option value="casual">非正式风格</option>
        <option value="friendly">友好风格</option>
      </select>
    </div>

    <div v-if="currentTab === 'subtitles'">
      <!-- 用 props.subtitles，而不是 subtitlesPath -->
      <SubtitlesTab :subtitles="props.subtitles" />
    </div>

    <div v-if="currentTab === 'chat'">
      <ChatTab
  :languageStyle="languageStyle"
  :subtitles="props.subtitles" 
  :key="props.subtitles"       
/>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SubtitlesTab from './SubtitlesTab.vue';
import ChatTab from './ChatTab.vue';

const props = defineProps<{ subtitles: string }>();

const currentTab = ref<'subtitles' | 'chat'>('subtitles');
const languageStyle = ref<'default' | 'formal' | 'casual' | 'friendly'>('default');
</script>


<style scoped>
.ai-assistant {
  padding: 0;
  background-color: transparent;
  color: var(--app-text);
  font-size: 0.9em;
  font-family: 'Arial', sans-serif;
}

h3 {
  font-size: 1.3em;
  color: var(--app-accent);
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
  background-color: var(--app-accent);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
  font-size: 1em;
  font-weight: bold;
}

.navbar button.active {
  background-color: var(--app-accent-strong);
  transform: scale(1.05);
}

.navbar button:hover {
  background-color: var(--app-accent-strong);
  transform: scale(1.1);
}

/* 语言风格选择下拉菜单样式 */
.language-select {
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid var(--app-border);
  background-color: var(--app-surface-2);
  color: var(--app-text);
  cursor: pointer;
  transition: border-color 0.3s;
}

.language-select:hover {
  border-color: var(--app-accent);
}

@media (max-width: 640px) {
  .navbar {
    flex-wrap: wrap;
  }

  .navbar button,
  .language-select {
    min-height: 40px;
  }
}
</style>
