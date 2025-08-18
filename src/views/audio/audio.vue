<template>
  <div class="site--main">
    <h1>{{ title }}</h1>

    <div class="content-container">
      <div class="video-area">
        <!-- 用 src 作为 key，切换视频强制 remount -->
        <VideoPlayer
          :key="options.src"
          :videoOptions="options"
          :poster="currentPoster"
          :subtitles="currentSubtitles"
        />
      </div>

      <div class="sidebar">
        <VideoList :videoList="videoList" @selectVideo="handleSelectVideo" />
      </div>
    </div>

    <!-- 用字幕地址作为 key，保证刷新 -->
    <AiAssistant
      :key="currentSubtitles"
      :subtitles="currentSubtitles"
      class="ai-assistant-fullwidth"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import VideoPlayer from './VideoPlayer.vue';
import VideoList from './VideoList.vue';
import AiAssistant from './AiAssistant/AiAssistant.vue';
import { videoList as initialVideoList } from './VideoResources';

interface Video {
  title: string;
  src: string;
  poster: string;
  subtitles: string;
}

const videoList = ref<Video[]>(initialVideoList);

// ✅ 兜底：列表为空也不崩；若找不到该标题，回退到 0
const hasList = videoList.value.length > 0;
const defaultIndex = hasList
  ? Math.max(0, videoList.value.findIndex(v => v.title === '从细胞到餐桌'))
  : 0;

const title = ref(hasList ? videoList.value[defaultIndex].title : '');

// 🚩 和 VideoPlayer.vue 的类型保持一致：若子组件是 `ligthOff`，这里也写 `ligthOff`
const options = reactive({
  width: '800px',
  height: '450px',
  color: '#409eff',
  title: hasList ? videoList.value[defaultIndex].title : '',
  src: hasList ? videoList.value[defaultIndex].src : '',
  muted: false,
  webFullScreen: false,
  speedRate: ['0.75', '1.0', '1.25', '1.5', '2.0'],
  autoPlay: false,
  loop: false,
  mirror: false,
  // ⬇️ 如果你的 VideoPlayer.vue 接口是 ligthOff，就用这一行：
  ligthOff: false,
  // ⬇️ 如果你已把子组件接口改为 lightOff，就改成：
  // lightOff: false,
  volume: 0.3,
  control: true,
  controlBtns: ['audioTrack', 'quality', 'speedRate', 'volume', 'setting', 'pip', 'pageFullScreen', 'fullScreen'],
});

const currentPoster = ref(hasList ? videoList.value[defaultIndex].poster : '');
const currentSubtitles = ref(hasList ? videoList.value[defaultIndex].subtitles : '');

const handleSelectVideo = (video: Video) => {
  options.src = video.src;
  options.title = video.title;
  currentPoster.value = video.poster;
  currentSubtitles.value = video.subtitles;
  title.value = video.title;
};
</script>

<style scoped>
.site--main { padding: 20px; }
.content-container { display: flex; }
.video-area { flex: 1; }
.sidebar {
  margin-left: 20px;
  width: 300px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.ai-assistant-fullwidth {
  padding: 20px;
  background-color: #f0f4f8;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
</style>
