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
                <span :class="cellClass(i, record.alignment)">{{ ch }}</span>
              </template>
            </div>
            <div class="align-row">
              <template
                v-for="(ch, i) in parseAlignment(record.alignment).queryChars"
                :key="i"
              >
                <span :class="cellClass(i, record.alignment)">{{ ch }}</span>
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
                  <td class="key-cell">{{ cleanString(entry[0]) }}</td>
                  <td class="val-cell">
                    <!-- 图片显示 -->
                    <template v-if="cleanString(entry[0]) === 'pictureid'">
                      <button @click="showLightbox(cleanString(entry[1]))">
                        View Image
                      </button>
                    </template>
                    <!-- Species 名称斜体 -->
                    <template v-else-if="/specie/i.test(cleanString(entry[0]))">
                      <i>{{ cleanString(entry[1]) }}</i>
                    </template>
                    <!-- 其他情况清洗显示 -->
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
import { pagination } from '../../utils/table';
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

// 国际化 & 分页
const locale = ref(en);
watch(() => props.results.length, len => {
  pagination.value.total = len;
});

// 列定义
const columns = [
  { title: 'Database', dataIndex: 'file', key: 'file', width: 120 },
  { title: 'Row', dataIndex: 'row', key: 'row', width: 60 },
  { title: 'Column', dataIndex: 'column', key: 'column', width: 150 },
  { title: 'Score', dataIndex: 'score', key: 'score', width: 80, sorter: (a, b) => a.score - b.score }
] as STableColumnsType<any>;

// 排除的字段名列表
const excludeKeys = [
  'js_origin_tRNA',
  'js_sup_tRNA',
  'Unnamed: 17',
  'incidenceRate',
  'PMID of references'
  // 可继续添加其它要排除的字段
];

// 文件名到数据库名的映射
const fileToDbMap: Record<string, string> = {
  'Coding Variation in Cancer.csv': 'Cancer',
  'Coding Variation in Genetic Disease.csv': 'Genetic Disease',
  'Nonsense Sup-RNA.csv': 'Nonsense Suppressors',
  'Frameshift sup-tRNA.csv': 'Frameshift sup-tRNA',
  'Engineered Sup-tRNA.csv': 'Engineered Sup-tRNA',
  'Function and Modification.csv': 'Function & Modification',
  'aaRS Recognition.csv': 'aaRS Recognition'
};
function mapFileToDb(file: string): string {
  const clean = file.replace(/^\ufeff/, '');
  return fileToDbMap[clean] || clean;
}

// 清理字符串，去除 BOM 和特殊字符
function cleanString(x: unknown): string {
  if (typeof x !== 'string') return String(x);
  return x.replace(/^\ufeff/, '').replace(/ï»¿/g, '');
}

// 过滤空值和排除字段
function filterRow(key: unknown, val: unknown): boolean {
  const k = cleanString(key);
  if (excludeKeys.includes(k)) return false;
  const v = val == null ? '' : cleanString(val);
  return v.trim().length > 0;
}

// 解析 alignment，提取 target/query 行和匹配符
function parseAlignment(text: string) {
  const real = text.replace(/\\n/g, '\n');
  const parts = real.split('\n');
  const targetLine = parts[0].replace(/^target\s*/, '');
  const matchLine = parts[1] || '';
  const queryLine = (parts[2] || '').replace(/^query\s*/, '');
  return {
    targetChars: Array.from(targetLine),
    matchLine,
    queryChars: Array.from(queryLine)
  };
}

// 根据 index 判断 cell 类型
function cellClass(idx: number, text: string) {
  const { targetChars, matchLine, queryChars } = parseAlignment(text);
  if (matchLine[idx] === '|') return 'match';
  if (targetChars[idx] === '-') return 'insertion';
  if (queryChars[idx] === '-') return 'deletion';
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
</style>
