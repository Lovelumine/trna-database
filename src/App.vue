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
        <!-- 条件渲染 NavBar，当路径不为 '/audio' 时显示 -->
        <nav-bar v-if="!isAudioRoute && !isAdminRoute && !isAIYingyingRoute" />
        <router-view />
        <footer-comp v-if="!isAdminRoute && !isAIYingyingRoute" />
        <bot-component v-if="!isAIYingyingRoute && !isAdminRoute" />
      </div>
    </transition>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed } from 'vue';
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
    const normalizedPath = computed(() => String(route.path || '').toLowerCase());
    const isAIYingyingRoute = computed(() =>
      route.name === 'AIYingying' || normalizedPath.value === '/aiyingying'
    );
    const isAdminRoute = computed(() => normalizedPath.value.startsWith('/admin'));
    const isAudioRoute = computed(() => normalizedPath.value.includes('/audio'));

    onMounted(() => {
      // 强制加载动画至少显示两秒
      setTimeout(() => {
        loading.value = false;
      }, 500);
    });

    return { loading, isAIYingyingRoute, isAudioRoute, isAdminRoute };
  }
});
</script>
