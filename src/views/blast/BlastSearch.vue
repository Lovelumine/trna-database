<template>
  <div class="search-service">
    <h2>tRNA Search Service</h2>

    <div class="controls">
      <!-- 左侧：Query + 参数 -->
      <div class="left-controls">
        <div class="control-group">
          <label>Query Sequence:</label>
          <textarea
            v-model="querySeq"
            class="query-input"
            :disabled="loading"
          />
        </div>

        <div class="sliders">
          <div class="slider-control">
            <label>Match: {{ match }}</label>
            <input
              type="range" min="0" max="5" step="0.1"
              v-model.number="match" :disabled="loading"
            />
          </div>
          <div class="slider-control">
            <label>Mismatch: {{ mismatch }}</label>
            <input
              type="range" min="-5" max="0" step="0.1"
              v-model.number="mismatch" :disabled="loading"
            />
          </div>
          <div class="slider-control">
            <label>Gap Open: {{ gapOpen }}</label>
            <input
              type="range" min="-5" max="0" step="0.1"
              v-model.number="gapOpen" :disabled="loading"
            />
          </div>
          <div class="slider-control">
            <label>Gap Extend: {{ gapExtend }}</label>
            <input
              type="range" min="-5" max="0" step="0.1"
              v-model.number="gapExtend" :disabled="loading"
            />
          </div>
        </div>

        <div class="control-group inline">
          <label>Results Count:</label>
          <input
            type="number" v-model.number="numResults"
            min="1" max="50"
            class="number-input"
            :disabled="loading"
          />
          <!-- Reset 按钮 -->
          <button class="reset-button" @click="resetDefaults" :disabled="loading">
            Reset
          </button>
        </div>
      </div>

      <!-- 右侧：数据库 Pills -->
      <div class="right-controls">
        <label class="db-label">Databases:</label>
        <div class="db-pills">
          <button
            v-for="db in databases"
            :key="db.name"
            :class="['pill', { active: selectedDbs.includes(db.name), disabled: loading }]"
            @click="!loading && toggleDb(db.name)"
          >
            {{ db.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- 搜索按钮 + 进度 -->
    <div class="button-wrapper">
      <button
        class="run-button"
        :class="{ loading: loading, done: progress === 100 }"
        @click="runSearch"
        :disabled="loading"
      >{{ loading ? 'Searching…' : 'Run Search' }}</button>
      <div v-if="loading || progress===100" class="progress-bar">
        <div class="progress" :style="{ width: progress+'%' }"></div>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <!-- 子组件展示结果 -->
    <BlastResults
      :results="results"
      :loading="loading"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import axios from 'axios';
import BlastResults from './BlastResults.vue';

const SERVICE_URL = '/search';

const querySeq = ref(`GUCCCGCUGGUGUAAU#GADAGCAUACGAUCCUNCUAAGPUUGCGGUCCUGGTPCGAUCCCAGGGCGGGAUACCA`);
const loading  = ref(false);
const error    = ref<string|null>(null);
const results  = ref<any[]>([]);
const progress = ref(0);
let timer: number|null = null;

// 参数
const numResults = ref(5);
const match      = ref(2.0);
const mismatch   = ref(-0.5);
const gapOpen    = ref(-2.0);
const gapExtend  = ref(-1.0);
// 默认值常量
const DEFAULT_QUERY = `GUCCCGCUGGUGUAAU#GADAGCAUACGAUCCUNCUAAGPUUGCGGUCCUGGTPCGAUCCCAGGGCGGGAUACCA`;
const DEFAULT_NUM = 5;
const DEFAULT_MATCH = 2.0;
const DEFAULT_MISMATCH = -0.5;
const DEFAULT_GAP_OPEN = -2.0;
const DEFAULT_GAP_EXTEND = -1.0;
const DEFAULT_DBS = [
  'Coding Variation in Cancer',
  'Coding Variation in Genetic Disease',
  'Nonsense Sup-RNA',
  'Frameshift sup-tRNA',
  'Engineered Sup-tRNA',
  'Function and Modification',
  'aaRS Recognition'
];
function resetDefaults() {
  querySeq.value  = DEFAULT_QUERY;
  numResults.value = DEFAULT_NUM;
  match.value      = DEFAULT_MATCH;
  mismatch.value   = DEFAULT_MISMATCH;
  gapOpen.value    = DEFAULT_GAP_OPEN;
  gapExtend.value  = DEFAULT_GAP_EXTEND;
  selectedDbs.value = [...DEFAULT_DBS];
  progress.value   = 0;
  error.value      = null;
  results.value    = [];
}

// 数据库 Pills
const databases = [
  { name: 'Coding Variation in Cancer', url: 'https://minio.lumoxuan.cn/ensure/Coding Variation in Cancer.csv' },
  { name: 'Coding Variation in Genetic Disease', url: 'https://minio.lumoxuan.cn/ensure/Coding Variation in Genetic Disease.csv' },
  { name: 'Nonsense Sup-RNA', url: 'https://minio.lumoxuan.cn/ensure/Nonsense Sup-RNA.csv' },
  { name: 'Frameshift sup-tRNA', url: 'https://minio.lumoxuan.cn/ensure/Frameshift sup-tRNA.csv' },
  { name: 'Engineered Sup-tRNA', url: 'https://minio.lumoxuan.cn/ensure/Engineered Sup-tRNA.csv' },
  { name: 'Function and Modification', url: 'https://minio.lumoxuan.cn/ensure/Function and Modification.csv' },
  { name: 'aaRS Recognition', url: 'https://minio.lumoxuan.cn/ensure/aaRS%20Recognition.csv' },
];
const selectedDbs = ref(databases.map(d=>d.name));
const toggleDb = (n: string) => {
  const i = selectedDbs.value.indexOf(n);
  i<0 ? selectedDbs.value.push(n) : selectedDbs.value.splice(i,1);
};
const csvLinks = computed(() => 
  databases.filter(d=>selectedDbs.value.includes(d.name)).map(d=>d.url)
);

// 重置进度
watch(querySeq,()=>{
  if(!loading.value) progress.value=0;
});

async function runSearch(){
  loading.value=true; error.value=null; results.value=[]; progress.value=0;
  timer = window.setInterval(()=>{
    if(progress.value<90) progress.value += Math.random()*5;
  },200);

  try {
    const payload = {
      query_seq: querySeq.value,
      csv_paths: csvLinks.value,
      number:    numResults.value,
      match:     match.value,
      mismatch:  mismatch.value,
      gap_open:  gapOpen.value,
      gap_extend:gapExtend.value
    };
    const resp = await axios.post(SERVICE_URL,payload,{timeout:60000});
    results.value = resp.data;
    progress.value = 100;
  } catch(e:any){
    error.value = e.response?.data || e.message || 'Unknown error';
    progress.value=0;
  } finally {
    loading.value=false;
    if(timer){ clearInterval(timer); timer=null; }
  }
}
</script>

<style scoped>
.search-service {
  max-width: 900px;
  margin: 2rem auto;
  font-family: Arial, sans-serif;
  color: #333;
}
h2 {
  text-align: center;
  margin-bottom: 1rem;
}
.controls {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
  background: #fafafa;
  padding: 1rem;
  border-radius: 6px;
}
.left-controls,
.right-controls {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.control-group {
  display: flex;
  flex-direction: column;
}
.inline {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

/* Query 加高 */
.query-input {
  font-family: monospace;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  min-height: 100px;
  resize: vertical;
}

/* 滑块 */
.sliders {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.8rem;
}
.slider-control label {
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}
.slider-control input {
  width: 100%;
}

/* Pills */
.db-label {
  font-weight: bold;
}
.db-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.pill {
  padding: 0.3rem 0.7rem;
  border: 1px solid #ccc;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: 0.2s;
  font-size: 0.9rem;
}
.pill.active {
  background: #007acc;
  color: #fff;
  border-color: #007acc;
}
.pill.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 结果数输入 */
.number-input {
  width: 4rem;
  padding: 0.3rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* 按钮 + 进度 */
.button-wrapper {
  grid-column: 1 / -1;
  text-align: center;
  margin-top: 0.5rem;
}
.run-button {
  padding: 0.6rem 1.8rem;
  background: #007acc;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: 0.2s;
  min-width: 150px;
}
.run-button.loading {
  background: #f0ad4e;
}
.run-button.done {
  background: #5cb85c;
}
.run-button:disabled {
  cursor: not-allowed;
}
.progress-bar {
  margin-top: 0.4rem;
  width: 60%;
  height: 6px;
  background: #ddd;
  border-radius: 3px;
  margin-left: auto;
  margin-right: auto;
  overflow: hidden;
}
.progress {
  height: 100%;
  background: #f0ad4e;
  transition: width 0.2s;
}
.run-button.done + .progress-bar .progress {
  background: #5cb85c;
}

.error {
  margin: 1rem 0;
  color: #c00;
  text-align: center;
}

/* 结果表 */
.results-table {
  margin-top: 1.5rem;
}
.alignment {
  margin: 0;
  font-family: monospace;
  white-space: pre-wrap;
}

.inline .reset-button {
  margin-left: 0.5rem;
  padding: 0.3rem 0.6rem;
  background: #ccc;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}
.inline .reset-button:hover:not(:disabled) {
  background: #999;
}
.reset-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>