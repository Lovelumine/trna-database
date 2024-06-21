<template>
  <div class="site--main">
    <h1>Display tRNA</h1>
    <p>Currently displaying tRNA: {{ tRNAName }}</p>
    <TranStructure
      :initialName="tRNAName"
      :initialStructure="structure"
      :initialSequence="sequence"
      :initialModifiedSequence="modifiedSequence"
    />
  </div>
</template>

<script setup>
import { toRefs } from 'vue';
import { useRoute } from 'vue-router';
import TranStructure from '@/components/TranStructure.vue';

const route = useRoute();
const { tRNAName } = toRefs(route.params);

// 模拟数据
const structure = "(((((((..((((........)))).(((((.......))))).....(((((.......)))))))))))).";
const sequence = "GGGGGATTAGCTCAAATGGTAGAGCGCTCGCTTAGCATGCGAGAGGTAGCGGGATCGATGCCCGCATCCTCCA";
const modifiedSequence = "-;G;G;G;G;G;A;U;U;A;m2G;C;U;C;A;A;A;D;-;G;G;D;-;-;A;G;A;G;C;m2,2G;C;U;C;G;C;Um;U;I;G;C;m1I;Y;Gm;C;G;A;G;A;G;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;-;m7G;U;A;G;C;G;G;G;A;Y;C;G;m1A;U;G;C;C;C;G;C;A;U;C;C;U;C;C;A;C;C;A";
</script>

<style scoped>
.site--main {
  padding: 20px;
}
</style>
