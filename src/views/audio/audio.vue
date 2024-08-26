<template>
  <div class="site--main">
    <!-- 标题 -->
    <h1>{{ title }}</h1>

    <div class="content-container">
      <!-- 视频播放区域 -->
      <div class="video-area">
        <VideoPlayer :videoOptions="options" :poster="currentPoster" />
      </div>

      <!-- 右侧的列表 -->
      <div class="sidebar">
        <VideoList :videoList="videoList" @selectVideo="handleSelectVideo" />
      </div>
    </div>

    <!-- AI Assistant 在视频下方 -->
    <AiAssistant class="ai-assistant-fullwidth" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import VideoPlayer from './VideoPlayer.vue';
import VideoList from './VideoList.vue';
import AiAssistant from './AiAssistant.vue';
import { videoList as initialVideoList } from './VideoResources';

// 当前视频标题
const title = ref('蛋白质的合成');

// 视频列表
const videoList = ref(initialVideoList);

// 当前播放视频的配置
const options = reactive({
  width: '800px',
  height: '450px',
  color: "#409eff",
  title: videoList.value[0].title,
  src: videoList.value[0].src,
  muted: false,
  webFullScreen: false,
  speedRate: ["0.75", "1.0", "1.25", "1.5", "2.0"],
  autoPlay: false,
  loop: false,
  mirror: false,
  ligthOff: false,
  volume: 0.3,
  control: true,
  controlBtns: ['audioTrack', 'quality', 'speedRate', 'volume', 'setting', 'pip', 'pageFullScreen', 'fullScreen']
});

// 当前视频的海报
const currentPoster = ref(videoList.value[0].poster);

// 处理选择视频的事件
const handleSelectVideo = (video) => {
  options.src = video.src;
  options.title = video.title;
  currentPoster.value = video.poster;
  title.value = `蛋白质的合成 - ${video.title}`;
}
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.content-container {
  display: flex;
}

.video-area {
  flex: 1;
}

.sidebar {
  margin-left: 20px;
  width: 300px;
  max-height: calc(100vh - 100px); /* 减去可能的其他空间 */
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.ai-assistant-fullwidth {
  padding: 20px;
  background-color: #f0f4f8;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

</style>
