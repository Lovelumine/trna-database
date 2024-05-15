<template>
    <div class="site--main">
      <h2>tRNA Elements</h2>
  
      <div class="table-section">
        <trna-elements-1 />
      </div>
  
      <div class="table-section">
        <trna-elements-2 />
      </div>
  
      <div class="table-section">
        <trna-elements-3 />
      </div>
    </div>
  </template>
  
  <script>
  import TrnaElements1 from './tRNA-elements-1.vue';
  import TrnaElements2 from './tRNA-elements-2.vue';
  import TrnaElements3 from './tRNA-elements-3.vue';
  
  export default {
    name: 'TrnaElements',
    components: {
      TrnaElements1,
      TrnaElements2,
      TrnaElements3,
    },
  };
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }
  </style>
  