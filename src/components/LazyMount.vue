<template>
  <div ref="rootRef" class="lazy-mount" :style="rootStyle">
    <slot v-if="active" />
    <div v-else class="lazy-mount__placeholder" aria-hidden="true" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';

const props = withDefaults(
  defineProps<{
    placeholderHeight?: string;
    rootMargin?: string;
    reserveSpace?: boolean;
  }>(),
  {
    placeholderHeight: '420px',
    rootMargin: '120px 0px',
    reserveSpace: false
  }
);

const rootRef = ref<HTMLElement | null>(null);
const active = ref(false);
let observer: IntersectionObserver | null = null;

const rootStyle = computed(() => ({
  minHeight: props.reserveSpace || !active.value ? props.placeholderHeight : undefined
}));

const activate = () => {
  if (active.value) return;
  active.value = true;
  observer?.disconnect();
  observer = null;
};

onMounted(() => {
  const target = rootRef.value;
  if (!target) return;

  if (!('IntersectionObserver' in window)) {
    activate();
    return;
  }

  observer = new IntersectionObserver(
    (entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        activate();
      }
    },
    { rootMargin: props.rootMargin }
  );
  observer.observe(target);
});

onBeforeUnmount(() => {
  observer?.disconnect();
  observer = null;
});
</script>

<style scoped>
.lazy-mount {
  width: 100%;
}

.lazy-mount__placeholder {
  width: 100%;
  min-height: inherit;
}
</style>
