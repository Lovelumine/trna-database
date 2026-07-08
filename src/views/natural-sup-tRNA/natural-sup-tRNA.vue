<template>
    <div class="site--main">
      <h2>Natural sup-tRNA</h2>
      <div class="table-section" id="nonsense-sup-trna">
        <naturalsuptRNA1 />
      </div>
  
      <div class="table-section" id="frameshift-sup-trna">
        <FrameshiftsuptRNA />
      </div>

    </div>
  </template>
  
  <script>
  import naturalsuptRNA1 from './natural-sup-tRNA-1.vue';
  import FrameshiftsuptRNA from './Frameshift sup-tRNA.vue';
  
  export default {
    name: 'naturalsuptRNA',
    components: {
      naturalsuptRNA1,
      FrameshiftsuptRNA,
    },
  };
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }

  @media (max-width: 640px) {
    .site--main {
      padding-top: 12px;
    }

    .site--main > h2 {
      margin: 0 0 18px;
      font-size: clamp(1.45rem, 6.8vw, 1.7rem);
      line-height: 1.25;
    }

    .table-section {
      margin-bottom: 36px;
    }

    .table-section :deep(.site--main) {
      padding-top: 0;
    }

    .table-section :deep(.site--main > h2) {
      margin-bottom: 16px;
      font-size: clamp(1.45rem, 7vw, 1.75rem);
      line-height: 1.25;
    }
  }
  </style>
  
