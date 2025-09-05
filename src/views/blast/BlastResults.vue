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
          <!-- 图例 -->
          <div class="align-legend">
            <span class="legend-item"><i class="legend-dot match"></i>Match</span>
            <span class="legend-item"><i class="legend-dot mismatch"></i>Mismatch</span>
            <span class="legend-item"><i class="legend-dot insertion"></i>Insertion (相对 Target)</span>
            <span class="legend-item"><i class="legend-dot deletion"></i>Deletion (相对 Target)</span>
          </div>

          <!-- 对齐可视化 -->
          <div class="alignment">
            <!-- Target：数据库序列（被比对） -->
            <div class="align-row">
              <span class="seq-label target">Target</span>
              <template
                v-for="(ch, i) in parseAlignmentForView(record.alignment).targetChars"
                :key="'t-' + i"
              >
                <span
                  :class="cellClass(i, record.alignment)"
                  class="char-cell"
                >{{ ch }}</span>
              </template>
            </div>

            <!-- Query：查询序列（你的输入） -->
            <div class="align-row">
              <span class="seq-label query">Query</span>
              <template
                v-for="(ch, i) in parseAlignmentForView(record.alignment).queryChars"
                :key="'q-' + i"
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
  alignment: string;          // 三行文本：target 行、match 行（可有可无）、query 行
  row_data: Record<string, any>;
}

const props = defineProps<{
  results: ResultRow[];
  loading: boolean;
}>();

const locale = ref(en);
watch(
  () => props.results,
  (rows) => {
    const len = rows?.length ?? 0;
    pagination.total = len;
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

// 下划线变空格
function formatKey(key: string): string {
  return cleanString(key).replace(/_/g, ' ');
}

function filterRow(key: unknown, val: unknown): boolean {
  const k = cleanString(key);
  if (excludeKeys.includes(k)) return false;
  const v = val == null ? '' : cleanString(val);
  return v.trim().length > 0;
}

/* ------------------- 对齐解析与上色逻辑 ------------------- */

// 缓存已解析的 alignment，避免在 v-for 中重复计算
const alignCache = new Map<string, { tArr: string[]; qArr: string[]; len: number }>();

// 从一行（带前缀与索引）中提取末尾的纯序列（含 '-'、'#' 等）
function extractSeq(line: string): string {
  // 允许 ACGTU、IUPAC、'-'、'#'、以及空格（稍后会去掉空格）
  const m = line.match(/[ACGTUIRYSWKMBDHVN#P\-\s]+$/i);
  return (m?.[0] ?? '').replace(/\s+/g, ''); // 去空格，保留 '-' 作为 gap
}

// 解析 alignment 文本：仅取 target 与 query 的纯序列并对齐（包含 gap）
function parseAlignmentRaw(text: string) {
  if (alignCache.has(text)) return alignCache.get(text)!;

  const real = text.replace(/\\n/g, '\n').trim();
  const parts = real.split('\n');

  const targetSeq = extractSeq(parts[0] ?? ''); // 第一行：Target（数据库）
  const querySeq  = extractSeq(parts[2] ?? ''); // 第三行：Query（查询）

  // 一般 pairwise 对齐会保证长度一致（包含 '-')
  const len = Math.max(targetSeq.length, querySeq.length);
  const tArr: string[] = targetSeq.padEnd(len, ' ').split('');
  const qArr: string[] = querySeq.padEnd(len, ' ').split('');

  const res = { tArr, qArr, len };
  alignCache.set(text, res);
  return res;
}

// 提供给模板的视图层数据
function parseAlignmentForView(text: string) {
  const { tArr, qArr } = parseAlignmentRaw(text);
  return { targetChars: tArr, queryChars: qArr };
}

// 颜色判断：直接比较两个字符（含 gap）
function cellClass(idx: number, text: string) {
  const { tArr, qArr } = parseAlignmentRaw(text);
  const t = (tArr[idx] || ' ').toUpperCase();
  const q = (qArr[idx] || ' ').toUpperCase();

  // gap 判断（以 Target 为参考系）
  if (t === '-' && q !== '-') return 'insertion';
  if (q === '-' && t !== '-') return 'deletion';

  // 把 T 归一为 U（把 DNA/RNA 视作等价；不需要可删除这行）
  const norm = (c: string) => (c === 'T' ? 'U' : c);

  if (norm(t) === norm(q)) return 'match';
  return 'mismatch';
}
</script>

<style scoped>
.expanded-content {
  padding: 0.5rem 1rem;
  background: #fdfdfd;
}

/* 图例 */
.align-legend {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 12px;
  margin-bottom: 6px;
  color: #555;
}
.legend-item { display: inline-flex; align-items: center; gap: 6px; }
.legend-dot {
  display: inline-block;
  width: 10px; height: 10px; border-radius: 50%;
  background: currentColor;
}
.legend-dot.match    { color: #4caf50; }
.legend-dot.mismatch { color: #f44336; }
.legend-dot.insertion{ color: #ff9800; }
.legend-dot.deletion { color: #2196f3; }

/* 对齐区域 */
.alignment {
  margin-bottom: 0.6rem;
  font-family: monospace;
  white-space: nowrap;
}

.align-row {
  line-height: 1.2;
  display: flex;
  align-items: baseline;
}

/* 左侧行标签（固定宽度，便于对齐） */
.seq-label {
  display: inline-block;
  min-width: 10ch;      /* 可按需要调整 */
  margin-right: 8px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  color: #666;
}
.seq-label.target { font-weight: 600; }
.seq-label.query  { font-weight: 600; }

.char-cell {
  display: inline-block;
  width: 0.6em;
  text-align: center;
  margin: 0;
  padding: 0;
}

/* 颜色 */
.match    { color: #4caf50; }
.mismatch { color: #f44336; }
.insertion{ color: #ff9800; }
.deletion { color: #2196f3; }

/* row_data 表格 */
.row-data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
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
.val-cell { background: #fff; }
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