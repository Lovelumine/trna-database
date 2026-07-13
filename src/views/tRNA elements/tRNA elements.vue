<template>
    <div class="site--main">
      <h2>tRNA Elements</h2>


      <h2>tRNA Binding Site of Recognition</h2>
      <div class="center-align">
        <ConceptMap />
      </div>
      <LazyMount class="table-section" id="aars-recognition" placeholder-height="520px" reserve-space>
        <TrnaElements2 />
      </LazyMount>
      <LazyMount class="table-section" id="eftu" placeholder-height="520px" reserve-space>
        <TrnaElements3 />
      </LazyMount>
      <LazyMount class="table-section" id="ribosome-interaction" placeholder-height="520px" reserve-space>
        <TrnaRibosomeInteractionSites />
      </LazyMount>
      <LazyMount class="table-section" id="function-modification" placeholder-height="520px" reserve-space>
        <TrnaElements1 />
      </LazyMount>

    </div>
  </template>

  <script setup>
  import { defineAsyncComponent } from 'vue';
  import LazyMount from '@/components/LazyMount.vue';
  import ConceptMap from '../../components/ConceptMap.vue'

  const TrnaElements1 = defineAsyncComponent(() => import('./function and modification.vue'));
  const TrnaElements2 = defineAsyncComponent(() => import('./aaRS recognition.vue'));
  const TrnaElements3 = defineAsyncComponent(() => import('./EFTU.vue'));
  const TrnaRibosomeInteractionSites = defineAsyncComponent(() => import('./tRNA-ribosome Interaction Sites.vue'));
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }

  .center-align {
  display: flex;
  justify-content: center;
  align-items: center;
  height: min(620px, 55vw);
  min-height: 420px;
  width: 100%;
  min-width: 0;
  overflow: clip;
}

@media (max-width: 640px) {
  .site--main {
    box-sizing: border-box;
    padding: 20px;
    overflow-x: hidden;
  }

  .site--main :deep(h2) {
    margin: 0 0 22px;
    font-size: clamp(1.45rem, 7vw, 1.75rem);
    line-height: 1.3;
  }

  .table-section {
    margin-bottom: 48px;
  }

  .center-align {
    height: auto;
    min-height: 300px;
    align-items: flex-start;
  }
}
  </style>
  
