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
          :key="video.src || index"               
          @click="selectVideo(video)"
          :class="{ selected: video.src === selectedVideoSrc }"
        >
          {{ video.title }}
        </li>
      </ul>
    </div>

    <!-- 总结：使用 key 强制刷新；把语言也下传（可选） -->
    <VideoSummary
      v-if="selectedVideo"
      :key="(selectedVideo.subtitles || '') + '|' + (selectedVideo.title || '') + '|' + (language || '中文')"
      :subtitles="selectedVideo.subtitles"
      :title="selectedVideo.title"
      :language="language"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, PropType, watch } from 'vue';
import VideoSummary from './VideoSummary.vue';

interface Video {
  title: string;
  src: string;
  poster: string;
  subtitles: string;
}

/** 接收父组件传入的视频列表与（可选）语言 */
const props = defineProps({
  videoList: {
    type: Array as PropType<Video[]>,
    required: true
  },
  language: {
    type: String,
    default: '中文'
  }
});

/** emit 类型（可选但推荐，便于类型检查） */
const emit = defineEmits<{
  (e: 'selectVideo', video: Video): void
}>();

/** 安全初始化：列表为空时不报错 */
const hasList = props.videoList && props.videoList.length > 0;
const selectedVideoSrc = ref(hasList ? props.videoList[0].src : '');
const selectedVideo   = ref<Video | null>(hasList ? props.videoList[0] : null);

/** 视频列表可见性 */
const isVideoListVisible = ref(true);
const toggleVideoList = () => { isVideoListVisible.value = !isVideoListVisible.value; };

/** 选择视频 */
const selectVideo = (video: Video) => {
  selectedVideoSrc.value = video.src;
  selectedVideo.value = video;
  emit('selectVideo', video);
};

/** 当父组件替换 videoList 时，确保仍有选中项 */
watch(
  () => props.videoList,
  (newList) => {
    if (!newList || newList.length === 0) {
      selectedVideoSrc.value = '';
      selectedVideo.value = null;
      return;
    }
    // 如果当前选中的视频不在新列表里，回退到第一项
    const stillExists = newList.some(v => v.src === selectedVideoSrc.value);
    if (!stillExists) {
      selectedVideoSrc.value = newList[0].src;
      selectedVideo.value = newList[0];
      emit('selectVideo', newList[0]);
    }
  },
  { deep: true }
);

/** 暴露给模板使用（可选，因为 <script setup> 会自动暴露） */
const language = props.language;
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

.toggle-button:hover { background-color: #307fcf; }

.video-list-content { padding: 15px; border-top: 1px solid #ddd; }

.video-list h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 1.2em;
  border-bottom: 2px solid #409eff;
  padding-bottom: 5px;
}

.video-list ul { list-style: none; padding: 0; margin: 0; }

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

.video-list li:hover { background-color: #e0f0ff; transform: translateX(5px); }
.video-list li.selected { background-color: #d0e9ff; font-weight: bold; }

.video-list li::before {
  content: "▶";
  margin-right: 10px;
  color: #409eff;
  font-size: 1.2em;
}
</style>
