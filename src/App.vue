<template>
  <div>
    <div v-if="loading" class="loading-spinner">
      <!-- 加载动画 -->
      <div class="spinner">
        <div class="centered">
          <div class="blob-1"></div>
          <div class="blob-2"></div>
        </div>
        <p>LOADING</p>
        <div class="progress-bar">
          <div class="progress" :style="{ width: `${progress}%` }"></div>
        </div>
      </div>
    </div>
    <div v-else>
      <nav-bar />
      <router-view />
      <footer-comp />
      <bot-component />
    </div>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted } from 'vue';
import NavBar from './components/NavBar.vue';
import FooterComp from './components/Footer.vue';
import BotComponent from './bot/BotComponent.vue';

export default defineComponent({
  components: {
    NavBar,
    FooterComp,
    BotComponent
  },
  setup() {
    const loading = ref(true);
    const progress = ref(0);

    onMounted(() => {
      const interval = setInterval(() => {
        progress.value += 5;
        if (progress.value >= 100) {
          clearInterval(interval);
        }
      }, 100);

      // 强制加载动画至少显示两秒
      setTimeout(() => {
        loading.value = false;
      }, 2000);
    });

    return { loading, progress };
  }
});
</script>


<style>
/* 添加加载动画的样式 */
.loading-spinner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #5c94c1;
  /* 背景颜色 */
  z-index: 9999;
  /* 确保加载动画覆盖其他内容 */
}

.spinner {
  width: 200px;
  /* 增加宽度 */
  height: 200px;
  /* 增加高度 */
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  left: 0;
  margin: auto;
  text-align: center;
}

.spinner p {
  color: #fff;
  margin-top: 10px;
  /* 增加顶部间距 */
  font-family: sans-serif;
  letter-spacing: 3px;
  font-size: 48px;
  /* 增加字体大小 */
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  overflow: hidden;
  margin-top: 20px;
}

.progress {
  width: 0;
  height: 100%;
  background-color: #fff;
  transition: width 0.1s ease-in-out;
  border-radius: 5px;
}

@keyframes motion {
  0% {
    transform: translateX(0) scale(1);
  }

  25% {
    transform: translateX(-100px) scale(0.3);
    /* 调整动画距离 */
  }

  50% {
    transform: translateX(0) scale(1);
  }

  75% {
    transform: translateX(100px) scale(0.3);
    /* 调整动画距离 */
  }

  100% {
    transform: translateX(0) scale(1);
  }
}

.centered {
  width: 400px;
  height: 400px;
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translate(-50%, -50%);

  filter: blur(10px) contrast(20);
}

.blob-1,
.blob-2 {
  width: 70px;
  height: 70px;
  position: absolute;
  background: #fff;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.blob-1 {
  left: 20%;
  animation: osc-l 2.5s ease infinite;
}

.blob-2 {
  left: 80%;
  animation: osc-r 2.5s ease infinite;
  background: #0ff;
}

@keyframes osc-l {
  0% {
    left: 20%;
  }

  50% {
    left: 50%;
  }

  100% {
    left: 20%;
  }
}

@keyframes osc-r {
  0% {
    left: 80%;
  }

  50% {
    left: 50%;
  }

  100% {
    left: 80%;
  }
}
</style>
