<template>
    <div class="site--main">
      <h2>Natural Sup-tRNA</h2>
        <div class="table-section">
        <naturalsuptRNA1 />
      </div>
      </div>
  </template>
  
  <script>
  import naturalsuptRNA1 from './natural-sup-tRNA-1.vue';
  
  export default {
    name: 'naturalsuptRNA',
    components: {
      naturalsuptRNA1,
    },
  };
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }
  </style>
  