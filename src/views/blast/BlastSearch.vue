<template>
  <div class="search-service">
    <h2>BLAST Search</h2>
    <p class="page-intro">Compare a modified tRNA sequence with selected ENSURE datasets.</p>

    <div class="controls">
      <div class="left-controls">
        <div class="section-heading">
          <span class="step">1</span>
          <div><h3>Query and scoring</h3><p>Enter a sequence and adjust alignment penalties.</p></div>
        </div>
        <div class="control-group">
          <label for="blast-query">Query sequence</label>
          <textarea
            id="blast-query"
            v-model="querySeq"
            class="query-input"
            :disabled="loading"
          />
        </div>

        <div class="sliders">
          <div class="slider-control">
            <label><span>Match</span><output>{{ match }}</output></label>
            <input
              type="range" min="0" max="5" step="0.1"
              v-model.number="match" :disabled="loading"
            />
          </div>
          <div class="slider-control">
            <label><span>Mismatch</span><output>{{ mismatch }}</output></label>
            <input
              type="range" min="-5" max="0" step="0.1"
              v-model.number="mismatch" :disabled="loading"
            />
          </div>
          <div class="slider-control">
            <label><span>Gap open</span><output>{{ gapOpen }}</output></label>
            <input
              type="range" min="-5" max="0" step="0.1"
              v-model.number="gapOpen" :disabled="loading"
            />
          </div>
          <div class="slider-control">
            <label><span>Gap extend</span><output>{{ gapExtend }}</output></label>
            <input
              type="range" min="-5" max="0" step="0.1"
              v-model.number="gapExtend" :disabled="loading"
            />
          </div>
        </div>

        <div class="control-group inline">
          <label for="result-count">Maximum results</label>
          <input
            id="result-count"
            type="number" v-model.number="numResults"
            min="1" max="50"
            class="number-input"
            :disabled="loading"
          />
        </div>
      </div>

      <div class="right-controls">
        <div class="section-heading">
          <span class="step">2</span>
          <div><h3>Target databases</h3><p>Select one or more datasets to search.</p></div>
        </div>
        <div class="db-pills">
          <button
            v-for="db in databases"
            :key="db.name"
            :class="['pill', { active: selectedDbs.includes(db.name), disabled: loading }]"
            :aria-pressed="selectedDbs.includes(db.name)"
            @click="!loading && toggleDb(db.name)"
          >
            <span class="pill-check" aria-hidden="true">{{ selectedDbs.includes(db.name) ? '✓' : '' }}</span>
            <span>{{ db.name }}</span>
          </button>
        </div>
      </div>

      <div class="button-wrapper">
        <button class="reset-button" @click="resetDefaults" :disabled="loading">Reset parameters</button>
        <button
          class="run-button"
          :class="{ loading: loading, done: progress === 100 }"
          @click="runSearch"
          :disabled="loading || !selectedDbs.length"
        >{{ loading ? 'Searching…' : 'Run search' }}</button>
        <div v-if="loading || progress===100" class="progress-bar">
          <div class="progress" :style="{ width: progress+'%' }"></div>
        </div>
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
  'Coding Variation in Disease',
  'Nonsense Sup-RNA',
  'Frameshift sup-tRNA',
  'Engineered sup-tRNA',
  'Function of Modification',
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
  { name: 'Coding Variation in Cancer', table: 'coding_variation_cancer' },
  { name: 'Coding Variation in Disease', table: 'coding_variation_genetic_disease' },
  { name: 'Nonsense Sup-RNA', table: 'nonsense_sup_rna' },
  { name: 'Frameshift sup-tRNA', table: 'frameshift_sup_trna' },
  { name: 'Engineered sup-tRNA', table: 'Engineered_sup_tRNA' },
  { name: 'Function of Modification', table: 'function_and_modification' },
  { name: 'aaRS Recognition', table: 'aars_recognition' },
];
const selectedDbs = ref(databases.map(d=>d.name));
const toggleDb = (n: string) => {
  const i = selectedDbs.value.indexOf(n);
  i<0 ? selectedDbs.value.push(n) : selectedDbs.value.splice(i,1);
};
const tableNames = computed(() =>
  databases.filter(d => selectedDbs.value.includes(d.name)).map(d => d.table)
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
      tables:    tableNames.value,
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
  width: min(1180px, calc(100% - 48px));
  margin: 2.5rem auto;
  color: var(--app-text);
  min-width: 0;
}

h2 {
  margin: 0 0 0.35rem;
  color: var(--app-text);
}

.page-intro {
  margin: 0 0 2rem;
  color: var(--app-text-muted);
  font-size: 0.98rem;
}

.controls {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.85fr);
  border-top: 1px solid var(--app-border);
  border-bottom: 1px solid var(--app-border);
}

.left-controls,
.right-controls {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.6rem 1.75rem 1.75rem 0;
  min-width: 0;
}

.right-controls {
  padding: 1.6rem 0 1.75rem 1.75rem;
  border-left: 1px solid var(--app-border);
}

.section-heading {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.section-heading h3 {
  margin: 0 0 0.2rem;
  font: inherit;
  font-weight: 700;
  color: var(--app-text);
}

.section-heading p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 0.85rem;
}

.step {
  display: inline-grid;
  place-items: center;
  width: 1.7rem;
  height: 1.7rem;
  flex: 0 0 1.7rem;
  border-radius: 50%;
  color: var(--app-accent);
  background: color-mix(in srgb, var(--app-accent) 12%, transparent);
  font-weight: 700;
  font-size: 0.82rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.control-group > label,
.inline > label {
  color: var(--app-text);
  font-size: 0.86rem;
  font-weight: 650;
}

.inline {
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
}

.query-input {
  width: 100%;
  min-height: 128px;
  box-sizing: border-box;
  padding: 0.85rem 1rem;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  resize: vertical;
  background: var(--app-surface-2);
  color: var(--app-text);
  font: 0.92rem/1.55 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  letter-spacing: 0.015em;
  outline: none;
}

.query-input:focus,
.number-input:focus {
  border-color: var(--app-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--app-accent) 14%, transparent);
}

.sliders {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.15rem 1.5rem;
}

.slider-control { min-width: 0; }

.slider-control label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.55rem;
  color: var(--app-text-muted);
  font-size: 0.84rem;
}

.slider-control output {
  min-width: 2.6rem;
  padding: 0.12rem 0.4rem;
  border-radius: 5px;
  text-align: center;
  color: var(--app-text);
  background: var(--app-surface-2);
  font-variant-numeric: tabular-nums;
}

.slider-control input {
  width: 100%;
  margin: 0;
  appearance: none;
  height: 4px;
  border-radius: 999px;
  background: var(--app-border);
  outline: none;
}

.slider-control input::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--app-accent);
  border: 3px solid var(--app-surface);
  box-shadow: 0 0 0 1px var(--app-accent);
}

.slider-control input::-moz-range-thumb {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--app-accent);
  border: 3px solid var(--app-surface);
}

.db-pills {
  display: grid;
  gap: 0.45rem;
}

.pill {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  width: 100%;
  min-height: 38px;
  padding: 0.45rem 0.6rem;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: var(--app-text-muted);
  text-align: left;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
  font-size: 0.86rem;
}

.pill:hover { background: var(--app-surface-2); color: var(--app-text); }

.pill.active {
  background: color-mix(in srgb, var(--app-accent) 10%, transparent);
  color: var(--app-text);
}

.pill-check {
  display: inline-grid;
  place-items: center;
  width: 17px;
  height: 17px;
  flex: 0 0 17px;
  border: 1px solid var(--app-border);
  border-radius: 4px;
  color: #fff;
  font-size: 11px;
  line-height: 1;
}

.pill.active .pill-check {
  border-color: var(--app-accent);
  background: var(--app-accent);
}

.pill.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.number-input {
  width: 4.5rem;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--app-border);
  border-radius: 7px;
  background: var(--app-surface-2);
  color: var(--app-text);
  outline: none;
}

.button-wrapper {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.7rem;
  position: relative;
  padding: 1rem 0;
  border-top: 1px solid var(--app-border);
}

.run-button {
  min-width: 150px;
  padding: 0.68rem 1.4rem;
  background: var(--app-accent);
  color: #fff;
  border: 1px solid var(--app-accent);
  border-radius: 7px;
  cursor: pointer;
  font-weight: 650;
}

.run-button:hover:not(:disabled) { filter: brightness(1.07); }
.run-button:disabled { opacity: 0.55; cursor: not-allowed; }

.reset-button {
  padding: 0.68rem 1rem;
  border: 1px solid var(--app-border);
  border-radius: 7px;
  background: transparent;
  color: var(--app-text-muted);
  cursor: pointer;
}

.reset-button:hover:not(:disabled) { color: var(--app-text); background: var(--app-surface-2); }

.progress-bar {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 3px;
  background: var(--app-border);
  overflow: hidden;
}

.progress {
  height: 100%;
  background: var(--app-accent);
  transition: width 0.2s;
}

.error {
  margin: 1rem 0;
  color: var(--app-danger, #dc2626);
  padding-left: 0.8rem;
  border-left: 3px solid currentColor;
}

.results-table {
  margin-top: 1.5rem;
}
.alignment {
  margin: 0;
  font-family: monospace;
  white-space: pre-wrap;
}

.reset-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 860px) {
  .search-service {
    margin: 1rem auto;
  }

  .controls {
    grid-template-columns: minmax(0, 1fr);
  }

  .left-controls,
  .right-controls {
    padding: 1.25rem 0;
  }

  .right-controls { border-left: 0; border-top: 1px solid var(--app-border); }

  .db-pills { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .search-service {
    width: calc(100% - 32px);
    margin: 1rem auto;
    padding-bottom: 64px;
  }

  .page-intro { margin-bottom: 1.25rem; }

  .query-input {
    min-height: 110px;
  }

  .sliders {
    grid-template-columns: minmax(0, 1fr);
    gap: 0.85rem;
  }

  .inline {
    justify-content: space-between;
  }

  .db-pills {
    grid-template-columns: minmax(0, 1fr);
  }

  .button-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .run-button {
    width: 100%;
  }
}
</style>
