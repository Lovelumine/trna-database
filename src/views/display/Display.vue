<template>
    <div class="site--main">
      <h1>Display tRNA</h1>
      <p>Currently displaying tRNA: {{ tRNAName }}</p>
      <FornaVisualizer class="forna-visualizer" />
      <TrnaScanUpload />
    </div>

  </template>
  
  <script setup>
  import { toRefs } from 'vue';
  import { useRoute } from 'vue-router';
  import FornaVisualizer from '@/components/FornaVisualizer.vue'; 
  import TrnaScanUpload from '@/utils/TrnaScanUpload';
  
  const route = useRoute();
  const { tRNAName } = toRefs(route.params);
  </script>

  