<template>
  <div>
    <div v-if="loading" class="loading-spinner">
      <!-- 加载动画 -->
      <div class="spinner">
        <div class="ball"></div>
        <p>LOADING</p>
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

    onMounted(() => {
      // 模拟延迟以显示加载动画，可以根据需要调整
      setTimeout(() => {
        loading.value = false;
      }, 1000);
    });

    return { loading };
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
  width: 100px;
  height: 50px;
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  left: 0;
  margin: auto;
  text-align: center;
}

.spinner .ball {
  width: 20px;
  height: 20px;
  background-color: #fff;
  border-radius: 50%;
  display: inline-block;
  animation: motion 3s ease-in-out infinite;
}

.spinner p {
  color: #fff;
  margin-top: 5px;
  font-family: sans-serif;
  letter-spacing: 3px;
  font-size: 10px;
}

@keyframes motion {
  0% {
    transform: translateX(0) scale(1);
  }
  25% {
    transform: translateX(-50px) scale(0.3);
  }
  50% {
    transform: translateX(0) scale(1);
  }
  75% {
    transform: translateX(50px) scale(0.3);
  }
  100% {
    transform: translateX(0) scale(1);
  }
}
</style>
