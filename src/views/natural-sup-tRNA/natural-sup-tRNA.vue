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
  </style>
  
