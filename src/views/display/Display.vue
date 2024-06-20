<template>
    <div class="site--main">
      <h1>Display tRNA</h1>
      <p>Currently displaying tRNA: {{ tRNAName }}</p>
      <FornaVisualizer class="forna-visualizer" />
    </div>
  </template>
  
  <script setup>
  import { toRefs } from 'vue';
  import { useRoute } from 'vue-router';
  import FornaVisualizer from '@/components/FornaVisualizer.vue'; 
  
  const route = useRoute();
  const { tRNAName } = toRefs(route.params);
  </script>

  