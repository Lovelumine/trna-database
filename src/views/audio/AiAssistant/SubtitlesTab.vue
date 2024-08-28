<template>
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
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue';
  import SrtParser from 'srt-parser-2';
  import axios from 'axios';
  
  const props = defineProps({
    subtitles: {
      type: String,
      required: true
    }
  });
  
  const subtitles = ref<{ startTime: number; text: string }[]>([]);
  const currentTime = ref(0);
  const expanded = ref(false);
  const visibleSubtitles = ref<{ startTime: number; text: string }[]>([]);
  
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
  
  const loadSubtitles = async () => {
    if (props.subtitles) {
      try {
        const response = await axios.get(props.subtitles);
        const parser = new SrtParser();
        const parsedSubtitles = parser.fromSrt(response.data);
  
        subtitles.value = parsedSubtitles.map((subtitle) => ({
          startTime: parseTime(subtitle.startTime),
          text: subtitle.text,
        }));
  
        setInterval(() => {
          const video = document.querySelector('video');
          if (video) {
            currentTime.value = video.currentTime;
          }
        }, 200);
      } catch (error) {
        console.error('Failed to load subtitles:', error);
      }
    }
  };
  
  onMounted(loadSubtitles);
  
  watch(() => props.subtitles, loadSubtitles);
  
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
  .subtitle-container {
    margin-top: 15px;
    padding: 12px;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .subtitle-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .subtitle-header button {
    padding: 8px 12px;
    background-color: #50c878;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.3s;
    font-size: 0.9em;
    font-weight: bold;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
  
  .subtitle-header button:hover {
    background-color: #409eff;
    transform: scale(1.05);
  }
  
  .subtitle-list {
    list-style: none;
    padding: 0;
    margin: 0;
    max-height: 150px;
  }
  
  .subtitle-item {
    padding: 8px;
    border-bottom: 1px solid #ddd;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.3s;
  }
  
  .subtitle-item:hover,
  .subtitle-item.current {
    background-color: #e0f0ff;
    color: #409eff;
    transform: scale(1.02);
  }
  
  .subtitle-expanded p {
    margin: 0;
    padding: 8px 0;
    line-height: 1.8;
    text-align: justify;
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
    padding: 0 12px;
    text-align: justify;
  }
  </style>
  