<template>
    <div class="site--main">
      <h2>tRNA elements</h2>
  
      <div class="table-section">
        <trna-elements-1 />
      </div>

      <div class="table-section">
        <trna-elements-2 />
      </div>
    </div>
  </template>
  
  <script>
  import TrnaElements1 from './function and modification.vue';
  import TrnaElements2 from './aaRS recognition.vue';
  
  export default {
    name: 'TrnaElements',
    components: {
      TrnaElements1,
      TrnaElements2
    },
  };
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }
  </style>
  