<template>
  <div>
    <transition name="fade" mode="out-in">
      <div v-if="loading" key="loading" class="loading-spinner">
        <!-- 加载动画 -->
        <div class="spinner">
          <div class="loader">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
      </div>
      <div v-else key="content">
        <nav-bar />
        <router-view />
        <footer-comp />
        <bot-component v-if="!isAIYingyingRoute" />
      </div>
    </transition>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
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
    const route = useRoute();
    const loading = ref(true);
    const isAIYingyingRoute = ref(route.path === '/AIYingying');


    onMounted(() => {
      // 强制加载动画至少显示两秒
      setTimeout(() => {
        loading.value = false;
      }, 500);
    });

    watch(
      () => route.path,
      (newPath) => {
        isAIYingyingRoute.value = newPath === '/AIYingying';
      }
    );

    return { loading, isAIYingyingRoute  };
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
  background-color: #5c94c1; /* 背景颜色 */
  z-index: 9999; /* 确保加载动画覆盖其他内容 */
}

.spinner {
  text-align: center;
}

.loader {
  position: relative;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.dot {
  width: 24px;
  height: 24px;
  background: #3ac;
  border-radius: 100%;
  display: inline-block;
  animation: slide 1s infinite;
}

.dot:nth-child(1) {
  animation-delay: 0.1s;
  background: #32aacc;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
  background: #64aacc;
}

.dot:nth-child(3) {
  animation-delay: 0.3s;
  background: #96aacc;
}

.dot:nth-child(4) {
  animation-delay: 0.4s;
  background: #c8aacc;
}

.dot:nth-child(5) {
  animation-delay: 0.5s;
  background: #faaacc;
}

@-moz-keyframes slide {
  0% {
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(2);
  }
  100% {
    transform: scale(1);
  }
}

@-webkit-keyframes slide {
  0% {
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(2);
  }
  100% {
    transform: scale(1);
  }
}

@-o-keyframes slide {
  0% {
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(2);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes slide {
  0% {
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(2);
  }
  100% {
    transform: scale(1);
  }
}

/* 添加过渡效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */ {
  opacity: 0;
}
</style>
