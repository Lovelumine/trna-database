<template>
  <s-table-provider :hover="true" :locale="locale">
    <s-table
      v-if="results.length"
      :columns="columns"
      :data-source="results"
      :row-key="r => r.file + '-' + r.row + '-' + r.column"
      :stripe="true"
      :pagination="pagination"
      size="default"
      :expand-row-by-click="true"
    >
      <!-- 主表格单元格渲染 -->
      <template #bodyCell="{ column, text }">
        <span v-if="column.dataIndex === 'file'">{{ mapFileToDb(text) }}</span>
        <span v-else-if="column.dataIndex === 'score'">{{ (text as number).toFixed(1) }}</span>
        <span v-else-if="column.dataIndex === 'column'">{{ cleanString(text) }}</span>
        <span v-else>{{ cleanString(text) }}</span>
      </template>

      <!-- 展开行渲染 -->
      <template #expandedRowRender="{ record }">
        <div class="expanded-content">
          <!-- 格式化 alignment -->
          <div class="alignment">
            <div class="align-row">
              <template
                v-for="(ch, i) in parseAlignment(record.alignment).targetChars"
                :key="i"
              >
                <span
                  :class="cellClass(i, record.alignment)"
                  class="char-cell"
                >{{ ch }}</span>
              </template>
            </div>
            <div class="align-row">
              <template
                v-for="(ch, i) in parseAlignment(record.alignment).queryChars"
                :key="i"
              >
                <span
                  :class="cellClass(i, record.alignment)"
                  class="char-cell"
                >{{ ch }}</span>
              </template>
            </div>
          </div>

          <!-- row_data 表格 -->
          <table class="row-data-table">
            <tbody>
              <template v-for="entry in Object.entries(record.row_data)" :key="entry[0]">
                <tr
                  v-if="filterRow(entry[0], entry[1])"
                  :class="{ highlighted: entry[0] === record.column }"
                >
                  <!-- 这里将下划线替换为空格 -->
                  <td class="key-cell">{{ formatKey(entry[0]) }}</td>
                  <td class="val-cell">
                    <template v-if="cleanString(entry[0]) === 'pairwise_alignment'">
                      <pre class="pairwise">{{ stripScore(cleanString(entry[1])) }}</pre>
                    </template>
                    <template v-else-if="cleanString(entry[0]) === 'pictureid'">
                      <button @click="showLightbox(cleanString(entry[1]))">
                        View Image
                      </button>
                    </template>
                    <template v-else-if="/specie/i.test(cleanString(entry[0]))">
                      <i>{{ cleanString(entry[1]) }}</i>
                    </template>
                    <template v-else>
                      {{ cleanString(entry[1]) }}
                    </template>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </template>
    </s-table>
    <div v-else-if="!loading" class="no-results">No results yet.</div>

    <!-- Lightbox 弹窗 -->
    <vue-easy-lightbox
      :visible="visible"
      :imgs="lightboxImgs"
      :index="0"
      @hide="visible = false"
      :key="lightboxKey"
    />
  </s-table-provider>
</template>

<script setup lang="ts">
import { defineProps, ref, watch } from 'vue';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import en from '@shene/table/dist/locale/en';
import { createPagination } from '../../utils/table';
const pagination = createPagination();
import VueEasyLightbox from 'vue-easy-lightbox';
import {
  visible,
  lightboxImgs,
  lightboxKey,
  showLightbox
} from './keycell';

interface ResultRow {
  file: string;
  row: number;
  column: string;
  score: number;
  alignment: string;
  row_data: Record<string, any>;
}

const props = defineProps<{
  results: ResultRow[];
  loading: boolean;
}>();

const locale = ref(en);
watch(
  () => props.results,                      // 监听数组本身，替换也能触发
  (rows) => {
    const len = rows?.length ?? 0;
    pagination.total = len;                 // ← 不要再写 .value
    // 数据变化时把页码拉回第一页，避免“当前页 > 最大页”
    pagination.current = 1;
  },
  { immediate: true }
);

const columns = [
  { title: 'Database', dataIndex: 'file', key: 'file', width: 120 },
  { title: 'Row', dataIndex: 'row', key: 'row', width: 60 },
  { title: 'Column', dataIndex: 'column', key: 'column', width: 150 },
  { title: 'Score', dataIndex: 'score', key: 'score', width: 80, sorter: (a, b) => a.score - b.score }
] as STableColumnsType<any>;

const excludeKeys = [
  'js_origin_tRNA',
  'js_sup_tRNA',
  'Unnamed: 17',
  'incidenceRate',
  'PMID of references'
];

const fileToDbMap: Record<string, string> = {
  'Coding Variation in Cancer.csv': 'Coding Variation in Cancer',
  'Coding Variation in Genetic Disease.csv': 'Coding Variation in Disease',
  'Nonsense Sup-RNA.csv': 'Nonsense Suppressors',
  'Frameshift sup-tRNA.csv': 'Frameshift sup-tRNA',
  'Engineered Sup-tRNA.csv': 'Engineered sup-tRNA',
  'Function of Modification.csv': 'Function & Modification',
  'aaRS Recognition.csv': 'aaRS Recognition'
};
function mapFileToDb(file: string): string {
  const clean = file.replace(/^\ufeff/, '');
  return fileToDbMap[clean] || clean;
}


// 去掉 pairwise_alignment 中的 Score= 行
function stripScore(text: string): string {
  return text
    .split('\n')
    .filter(line => !line.trim().startsWith('Score='))
    .join('\n');
}

function cleanString(x: unknown): string {
  if (typeof x !== 'string') return String(x);
  return x.replace(/^\ufeff/, '').replace(/ï»¿/g, '');
}

// 新增：替换下划线为普通空格
function formatKey(key: string): string {
  return cleanString(key).replace(/_/g, ' ');
}

function filterRow(key: unknown, val: unknown): boolean {
  const k = cleanString(key);
  if (excludeKeys.includes(k)) return false;
  const v = val == null ? '' : cleanString(val);
  return v.trim().length > 0;
}

function parseAlignment(text: string) {
  const real = text.replace(/\\n/g, '\n').trim();
  const parts = real.split('\n');

  const targetLine = (parts[0] || '')
    .replace(/^target(?:\s+target)?\s*/, 'target ')
    .replace(/target\s+/, 'target ');
  const matchLine = parts[1] || '';
  const queryLine = (parts[2] || '')
    .replace(/^query(?:\s+query)?\s*/, 'query  ')
    .replace(/query\s+/, 'query  ');

  const tArr = Array.from(targetLine);
  const qArr = Array.from(queryLine);
  const maxLen = Math.max(tArr.length, qArr.length);

  while (tArr.length < maxLen) tArr.push(' ');
  while (qArr.length < maxLen) qArr.push(' ');

  const mLine = matchLine.padEnd(maxLen, ' ');

  return {
    targetChars: tArr,
    matchLine: mLine,
    queryChars: qArr
  };
}

function cellClass(idx: number, text: string) {
  const { targetChars, matchLine, queryChars } = parseAlignment(text);
  if (matchLine[idx] === '|') return 'match';
  if (targetChars[idx] === '-')  return 'insertion';
  if (queryChars[idx] === '-')   return 'deletion';
  return 'mismatch';
}
</script>

<style scoped>
.expanded-content {
  padding: 0.5rem 1rem;
  background: #fdfdfd;
}
.alignment {
  margin-bottom: 0.6rem;
  font-family: monospace;
  white-space: nowrap;
}
.char-cell {
  display: inline-block;
  width: 0.6em;
  text-align: center;
  margin: 0;
  padding: 0;
}
.align-row {
  line-height: 1.2;
}
.match {
  color: #4caf50;
}
.mismatch {
  color: #f44336;
}
.insertion {
  color: #ff9800;
}
.deletion {
  color: #2196f3;
}
.row-data-table {
  width: 100%;
  border-collapse: collapse;
}
.row-data-table td {
  border: 1px solid #ddd;
  padding: 4px 8px;
  vertical-align: top;
}
.key-cell {
  width: 200px;
  font-weight: bold;
  background: #f5f5f5;
}
.highlighted .key-cell,
.highlighted .val-cell {
  background: #ffffcc;
}
.val-cell {
  background: #fff;
}
.no-results {
  text-align: center;
  padding: 1rem;
  color: #666;
}

/* pairwise_alignment 专用样式 */
.pairwise {
  font-family: monospace;
  white-space: pre;
  margin: 0;
  padding: 0.5em;
  background: #f9f9f9;
  border: 1px solid #ddd;
  overflow: auto;
}
</style>