<template>
    <div class="site--main">
      <h2>tRNA Elements</h2>
  
      <div class="table-section">
        <trna-elements-1 />
      </div>
    </div>
  </template>
  
  <script>
  import TrnaElements1 from './function and modification.vue';

  
  export default {
    name: 'TrnaElements',
    components: {
      TrnaElements1,

    },
  };
  </script>
  
  <style scoped>
  .table-section {
    margin-bottom: 20px;
  }
  </style>
  