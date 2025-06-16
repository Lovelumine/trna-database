<template>
    <div class="site--main">
      <h2>tRNA elements</h2>


      <h2>tRNA Binding Site of Recognition</h2>
      <div class="center-align">
        <ConceptMap />
      </div>
      <div class="table-section">
        <trna-elements-2 />
      </div>
      <div class="table-section">
        <trna-elements-1 />
      </div>
    </div>
  </template>
  
  <script>
  import TrnaElements1 from './function and modification.vue';
  import TrnaElements2 from './aaRS recognition.vue';
  import ConceptMap from '../../components/ConceptMap.vue'
  
  export default {
    name: 'TrnaElements',
    components: {
      TrnaElements1,
      TrnaElements2,
      ConceptMap
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
}
  </style>
  