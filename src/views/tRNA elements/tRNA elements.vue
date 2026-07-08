<template>
    <div class="site--main">
      <h2>tRNA Elements</h2>


      <h2>tRNA Binding Site of Recognition</h2>
      <div class="center-align">
        <ConceptMap />
      </div>
      <div class="table-section" id="aars-recognition">
        <trna-elements-2 />
      </div>
                  <div class="table-section" id="eftu">
        <trna-elements-3 />
      </div>
          <div class="table-section" id="ribosome-interaction">
      <trna-ribosome-interaction-sites />
    </div>
      <div class="table-section" id="function-modification">
        <trna-elements-1 />
      </div>

    </div>
  </template>
  
  <script>
  import TrnaElements1 from './function and modification.vue';
  import TrnaElements2 from './aaRS recognition.vue';
  import TrnaElements3 from './EFTU.vue';
  import TrnaRibosomeInteractionSites from './tRNA-ribosome Interaction Sites.vue';
  import ConceptMap from '../../components/ConceptMap.vue'
  
  export default {
    name: 'TrnaElements',
    components: {
      TrnaElements1,
      TrnaElements2,
      TrnaElements3,
      ConceptMap,
      TrnaRibosomeInteractionSites
    },
  };
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }

  .center-align {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px; /* 设置高度占据整个视口，使其垂直居中 */
  width: 100%;
  min-width: 0;
  overflow: hidden;
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
  
