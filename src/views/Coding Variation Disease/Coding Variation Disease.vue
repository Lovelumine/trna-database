<template>
  <div class="site--main">
    <h2>Mutation-induced Disease</h2>

    <div class="table-section" id="coding-variation-disease">
      <CodingVariationDisease1 />
    </div>

    <div class="table-section" id="coding-variation-cancer">
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

@media (max-width: 640px) {
  .site--main {
    padding-top: 12px;
  }

  .site--main > h2 {
    margin: 0 0 18px;
    font-size: clamp(1.45rem, 6.8vw, 1.7rem);
    line-height: 1.25;
  }

  .table-section {
    margin-bottom: 36px;
  }

  .table-section :deep(.site--main) {
    padding-top: 0;
  }

  .table-section :deep(.site--main > h2) {
    margin-bottom: 16px;
    font-size: clamp(1.45rem, 7vw, 1.75rem);
    line-height: 1.25;
  }
}
</style>
