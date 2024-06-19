<template>
  <div class="site--main">
    <h2>PTC in Disease</h2>

    <div class="table-section">
      <PTCinGeneticDisease />
    </div>

    <div class="table-section">
      <PTCinCancer />
    </div>
  </div>
</template>

<script>
import PTCinGeneticDisease from './PTC-in-Genetic-Disease.vue';
import PTCinCancer from './PTC in Cancer.vue';

export default {
  name: 'CodingVariationDisease',
  components: {
    PTCinGeneticDisease,
    PTCinCancer,
  },
};
</script>

<style scoped>
.table-section {
  margin-bottom: 20px;
}
</style>
