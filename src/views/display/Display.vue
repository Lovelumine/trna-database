<template>
  <div class="site--main">
    <h1>Display tRNA</h1>
    <p>Currently displaying tRNA: {{ tRNAName }}</p>
    <FornaVisualizer class="forna-visualizer" />

    <!-- 这里是新的上传组件 -->
    <div>
      <h2>Upload tRNA Sequence</h2>
      <input type="text" v-model="sequence" placeholder="Enter tRNA sequence" />
      <button @click="uploadSequence">Analyze</button>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, toRefs } from 'vue';
import { useRoute } from 'vue-router';
import FornaVisualizer from '@/components/FornaVisualizer.vue';
import axios from 'axios';

const route = useRoute();
const { tRNAName } = toRefs(route.params);
const sequence = ref('');
const result = ref('');

const uploadSequence = async () => {
  try {
    const response = await axios.post('/scan', { sequence: sequence.value });
    result.value = response.data;
  } catch (error) {
    console.error('Error uploading sequence:', error);
    result.value = '上传失败，请重试。';
  }
};
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.forna-visualizer {
  margin-top: 20px;
}

input[type="text"] {
  width: 100%;
  padding: 8px;
  margin-top: 10px;
  margin-bottom: 10px;
}

button {
  padding: 8px 16px;
  cursor: pointer;
}

pre {
  background: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
}
</style>
