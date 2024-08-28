<template>
  <div class="video-list">
    <button @click="toggleVideoList" class="toggle-button">
      {{ isVideoListVisible ? '隐藏视频列表' : '显示视频列表' }}
    </button>
    <div v-if="isVideoListVisible" class="video-list-content">
      <h3>视频列表</h3>
      <ul>
        <li
          v-for="(video, index) in videoList"
          :key="index"
          @click="selectVideo(video)"
          :class="{ selected: video.src === selectedVideoSrc }"
        >
          {{ video.title }}
        </li>
      </ul>
    </div>

    <!-- 引入并使用 VideoSummary 组件 -->
    <VideoSummary
      v-if="selectedVideo"
      :subtitles="selectedVideo.subtitles"
      :title="selectedVideo.title"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, PropType } from 'vue';
import VideoSummary from './VideoSummary.vue';

// 定义 Video 类型
interface Video {
  title: string;
  src: string;
  poster: string;
  subtitles: string;
}

// 接收来自父组件的 props
const props = defineProps({
  videoList: {
    type: Array as PropType<Video[]>,
    required: true
  }
});

const selectedVideoSrc = ref(props.videoList[0].src);
const selectedVideo = ref<Video | null>(props.videoList[0]);

// 视频列表可见性状态
const isVideoListVisible = ref(true);

// 切换视频列表可见性
const toggleVideoList = () => {
  isVideoListVisible.value = !isVideoListVisible.value;
};

// 选择视频函数，触发事件通知父组件
const selectVideo = (video: Video) => {
  selectedVideoSrc.value = video.src;
  selectedVideo.value = video;
  emit('selectVideo', video);
};

// 向父组件发出事件
const emit = defineEmits(['selectVideo']);
</script>

<style scoped>
.video-list {
  width: 300px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  overflow: hidden;
}

.toggle-button {
  padding: 10px;
  margin-bottom: 0;
  background-color: #409eff;
  color: white;
  border: none;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  cursor: pointer;
  width: 100%;
  text-align: center;
  font-weight: bold;
  transition: background-color 0.3s;
}

.toggle-button:hover {
  background-color: #307fcf;
}

.video-list-content {
  padding: 15px;
  border-top: 1px solid #ddd;
}

.video-list h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 1.2em;
  border-bottom: 2px solid #409eff;
  padding-bottom: 5px;
}

.video-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.video-list li {
  cursor: pointer;
  padding: 10px;
  background-color: #f9f9f9;
  margin-bottom: 8px;
  border-radius: 8px;
  transition: background-color 0.3s, transform 0.3s;
  display: flex;
  align-items: center;
}

.video-list li:hover {
  background-color: #e0f0ff;
  transform: translateX(5px);
}

.video-list li.selected {
  background-color: #d0e9ff;
  font-weight: bold;
}

.video-list li::before {
  content: "▶";
  margin-right: 10px;
  color: #409eff;
  font-size: 1.2em;
}
</style>
