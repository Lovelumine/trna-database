<template>
  <div class="site--main">
    <h2>Coding variation Disease</h2>

    <div class="table-section">
      <coding-variation-disease-1 />
    </div>

    <div class="table-section">
      <coding-variation-disease-2 />
    </div>
  </div>
</template>

<script>
import CodingVariationDisease1 from './coding-variation-disease-1.vue';
import CodingVariationDisease2 from './coding-variation-disease-2.vue';

export default {
  name: 'CodingVariationDisease',
  components: {
    CodingVariationDisease1,
    CodingVariationDisease2,
  },
};
</script>

<style scoped>
.table-section {
  margin-bottom: 20px;
}
</style>
