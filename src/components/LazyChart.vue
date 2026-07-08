<template>
  <div ref="rootRef" :class="['lazy-chart', rootClass]" :style="rootStyle">
    <component
      :is="chartComponent"
      v-if="chartComponent"
      v-bind="chartAttrs"
      :option="option"
      :autoresize="autoresize"
      class="lazy-chart__canvas"
    />
    <div v-else class="lazy-chart__placeholder" aria-hidden="true" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, useAttrs } from 'vue';

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    option: unknown;
    autoresize?: boolean | Record<string, unknown>;
  }>(),
  {
    autoresize: false
  }
);

const attrs = useAttrs();
const rootRef = ref<HTMLElement | null>(null);
const chartComponent = shallowRef<unknown>(null);
let animationFrame: number | null = null;
let listening = false;

let chartLoader: Promise<unknown> | null = null;

const loadChart = async () => {
  if (chartComponent.value) return;
  chartLoader ??= import('@/utils/registerCharts').then((module) => module.VChart);
  chartComponent.value = await chartLoader;
};

const rootClass = computed(() => attrs.class);
const rootStyle = computed(() => attrs.style);
const chartAttrs = computed(() => {
  const { class: _class, style: _style, ...rest } = attrs;
  return rest;
});

const isVisibleEnough = () => {
  const target = rootRef.value;
  if (!target || target.offsetParent === null) return false;

  const rect = target.getBoundingClientRect();
  if (rect.height < 200) return false;

  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
  const visibleHeight = Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0);
  return visibleHeight >= Math.min(180, rect.height * 0.5);
};

const cleanupListeners = () => {
  if (!listening) return;
  window.removeEventListener('scroll', scheduleVisibilityCheck);
  window.removeEventListener('resize', scheduleVisibilityCheck);
  listening = false;
};

const checkVisibility = () => {
  if (chartComponent.value) {
    cleanupListeners();
    return;
  }
  if (!isVisibleEnough()) return;
  cleanupListeners();
  void loadChart();
};

function scheduleVisibilityCheck() {
  if (animationFrame !== null) return;
  animationFrame = window.requestAnimationFrame(() => {
    animationFrame = null;
    checkVisibility();
  });
}

onMounted(() => {
  listening = true;
  window.addEventListener('scroll', scheduleVisibilityCheck, { passive: true });
  window.addEventListener('resize', scheduleVisibilityCheck);
  if (window.scrollY > 0) {
    scheduleVisibilityCheck();
  }
});

onBeforeUnmount(() => {
  cleanupListeners();
  if (animationFrame !== null) {
    window.cancelAnimationFrame(animationFrame);
    animationFrame = null;
  }
});
</script>

<style scoped>
.lazy-chart {
  position: relative;
  width: 100%;
  min-height: 260px;
}

.lazy-chart__canvas,
.lazy-chart__placeholder {
  width: 100%;
  height: 100%;
  min-height: inherit;
}

.lazy-chart__placeholder {
  background: transparent;
}
</style>
