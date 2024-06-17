<template>
    <div class="site--main">
      <h2>tRNA Therapeutics</h2>
  
      <div class="table-section">
        <tRNAtherapeutics1 />
      </div>
  
    </div>
  </template>
  
  <script>
  import tRNAtherapeutics1 from './tRNAtherapeutics-1.vue';
  
  export default {
    name: 'tRNAtherapeutics',
    components: {
        tRNAtherapeutics1,
    },
  };
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }
  </style>
  