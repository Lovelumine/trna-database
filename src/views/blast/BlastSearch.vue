<template>
  <div class="search-service">
    <h2>tRNA Search Service</h2>
    <div class="form">
      <label>
        Query Sequence:
        <textarea v-model="querySeq" rows="4" />
      </label>
      <button @click="runSearch" :disabled="loading">
        {{ loading ? 'Searching…' : 'Run Search' }}
      </button>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <table v-if="results.length" class="results-table">
      <thead>
        <tr>
          <th>File</th>
          <th>Row</th>
          <th>Column</th>
          <th>Score</th>
          <th>Alignment</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, i) in results" :key="i">
          <td>{{ r.file }}</td>
          <td>{{ r.row }}</td>
          <td>{{ r.column }}</td>
          <td>{{ r.score.toFixed(1) }}</td>
          <td>
            <pre class="alignment">{{ r.alignment.replace(/\\n/g, '\n') }}</pre>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="no-results">
      No results yet.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

const SERVICE_URL = 'http://223.82.75.76:8000/search';

const querySeq = ref(`GUCCCGCUGGUGUAAU#GADAGCAUACGAUCCUNCUAAGPUUGCGGUCCUGGTPCGAUCCCAGGGCGGGAUACCA`);
const loading  = ref(false);
const error    = ref<string | null>(null);
const results  = ref<any[]>([]);

// 固定的 CSV 列表
const csvLinks = [
  'https://minio.lumoxuan.cn/ensure/Coding Variation in Cancer.csv',
  'https://minio.lumoxuan.cn/ensure/Coding Variation in Genetic Disease.csv',
  'https://minio.lumoxuan.cn/ensure/Nonsense Sup-RNA.csv',
  'https://minio.lumoxuan.cn/ensure/Frameshift sup-tRNA.csv',
  'https://minio.lumoxuan.cn/ensure/tRNAtherapeutics.csv',
  'https://minio.lumoxuan.cn/ensure/Function and Modification.csv',
  'https://minio.lumoxuan.cn/ensure/aaRS%20Recognition.csv'
];

async function runSearch() {
  loading.value = true;
  error.value   = null;
  results.value = [];

  try {
    const payload = {
      query_seq: querySeq.value,
      csv_paths: csvLinks,
      number:    5,
      match:     2.0,
      mismatch:  -0.5,
      gap_open:  -2.0,
      gap_extend:-1.0
    };
    const resp = await axios.post(SERVICE_URL, payload, { timeout: 60_000 });
    results.value = resp.data;
  } catch (e: any) {
    error.value = e.response?.data || e.message || 'Unknown error';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.search-service {
  max-width: 800px;
  margin: auto;
  font-family: sans-serif;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
textarea {
  width: 100%;
  font-family: monospace;
}
button {
  align-self: flex-start;
  padding: 6px 12px;
}
.error {
  color: #c00;
  margin-bottom: 16px;
}
.results-table {
  width: 100%;
  border-collapse: collapse;
}
.results-table th,
.results-table td {
  border: 1px solid #ddd;
  padding: 8px;
  vertical-align: top;
}
.alignment {
  margin: 0;
  font-family: monospace;
  white-space: pre-wrap;
}
.no-results {
  color: #666;
  font-style: italic;
}
</style>