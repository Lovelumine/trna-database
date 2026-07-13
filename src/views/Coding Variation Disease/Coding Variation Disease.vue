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
    padding: 8px 16px 28px;
  }

  .site--main > h2 {
    margin: 8px 0 20px;
    font-size: clamp(1.65rem, 7vw, 2rem);
    line-height: 1.16;
  }

  .table-section {
    margin-bottom: 36px;
    min-width: 0;
  }

  .table-section :deep(.site--main) {
    padding: 0;
  }

  .table-section :deep(.site--main > h2) {
    margin: 0 0 22px;
    font-size: clamp(1.5rem, 6.5vw, 1.8rem);
    line-height: 1.15;
  }
}
</style>
