<template>
  <div class="site--main">
    <h2>Coding Variation Disease</h2>

    <div class="table-section">
      <CodingVariationDisease1 />
    </div>

    <div class="table-section">
      <CodingVariationinCancer />
    </div>
  </div>
</template>

<script>
import CodingVariationDisease1 from './Coding Variation Disease-1.vue';
import CodingVariationinCancer from './Coding variation in Cancer.vue';

export default {
  name: 'CodingVariationDisease',
  components: {
    CodingVariationDisease1,
    CodingVariationinCancer,
  },
};
</script>

<style scoped>
.table-section {
  margin-bottom: 20px;
}
</style>
