<template>
  <div class="video-player-wrapper">
    <videoPlay ref="videoPlayerRef" v-bind="videoOptions" :poster="poster">
      <!-- 动态加载字幕 -->
      <track
        v-if="subtitles"
        :src="subtitles"
        kind="subtitles"
        srclang="zh"
        label="Chinese"
        default
      />
    </videoPlay>
  </div>
</template>

<script setup lang="ts">
import { PropType, provide, ref } from 'vue';
import 'vue3-video-play/dist/style.css'; // 引入样式
import { videoPlay } from 'vue3-video-play'; // 引入组件

interface VideoOptions {
  width: string;
  height: string;
  color: string;
  title: string;
  src: string;
  muted: boolean;
  webFullScreen: boolean;
  speedRate: string[];
  autoPlay: boolean;
  loop: boolean;
  mirror: boolean;
  ligthOff: boolean;
  volume: number;
  control: boolean;
  controlBtns: string[];
}

// 接收来自父组件的 props
const props = defineProps({
  videoOptions: {
    type: Object as PropType<VideoOptions>,
    required: true
  },
  poster: {
    type: String,
    required: true
  },
  subtitles: {
    type: String,  // 接收字幕文件路径
    required: false
  }
});

const videoPlayerRef = ref(null);

// 将播放器引用提供给其他组件
provide('videoPlayer', videoPlayerRef);
</script>

<style scoped>
.video-player-wrapper {
  background-color: rgba(240, 240, 240, 0.8); /* 淡淡的背景颜色 */
  padding: 20px;
  border-radius: 10px;
}
</style>
