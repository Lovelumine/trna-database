<template>
  <div class="video-player-wrapper">
    <video
      ref="videoPlayerRef"
      class="native-video"
      :src="videoOptions.src"
      :poster="poster"
      :title="videoOptions.title"
      :muted="videoOptions.muted"
      :autoplay="videoOptions.autoPlay"
      :loop="videoOptions.loop"
      :controls="videoOptions.control"
      preload="metadata"
      playsinline
    >
      <track
        v-if="nativeTrackSrc"
        :src="nativeTrackSrc"
        kind="subtitles"
        srclang="zh"
        label="Chinese"
        default
      />
      Your browser does not support HTML5 video.
    </video>
  </div>
</template>

<script setup lang="ts">
import { computed, PropType, provide, ref, watch, nextTick } from 'vue';

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

const videoPlayerRef = ref<HTMLVideoElement | null>(null);
const nativeTrackSrc = computed(() =>
  String(props.subtitles || '').replace(/\.srt(?=($|[?#]))/i, '.vtt')
);

watch(
  () => [props.videoOptions.src, props.videoOptions.volume] as const,
  async () => {
    await nextTick();
    if (videoPlayerRef.value) {
      videoPlayerRef.value.volume = Math.min(1, Math.max(0, props.videoOptions.volume));
    }
  },
  { immediate: true }
);

// 将播放器引用提供给其他组件
provide('videoPlayer', videoPlayerRef);
</script>

<style scoped>
.video-player-wrapper {
  width: 100%;
  min-width: 0;
  padding: 12px;
  border: 1px solid var(--app-border-light);
  border-radius: 8px;
  background-color: var(--app-surface-2);
}

.native-video {
  display: block;
  width: 100% !important;
  height: auto !important;
  aspect-ratio: 16 / 9;
  object-fit: contain;
  overflow: hidden;
  border-radius: 4px;
  background: #07090d;
}

@media (max-width: 640px) {
  .video-player-wrapper {
    padding: 6px;
  }
}
</style>
