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
      <template #bodyCell="{ column, text }">
        <!-- 自定义 alignment 列 -->
        <div v-if="column.dataIndex === 'alignment'" class="alignment">
          <template v-for="(base, idx) in parseAlignment(text).queryChars" :key="idx">
            <span :class="{ match: parseAlignment(text).matchLine[idx] === '|' }">
              {{ base }}
            </span>
          </template>
        </div>
        <!-- file 列映射到数据库名 -->
        <span v-else-if="column.dataIndex === 'file'">
          {{ mapFileToDb(text as string) }}
        </span>
        <!-- 其他列 -->
        <span v-else>{{ text }}</span>
        
      </template>
              <template #expandedRowRender="{ record }">
Under development
        </template>
    </s-table>
    <div v-else-if="!loading" class="no-results">No results yet.</div>
  </s-table-provider>
</template>

<script setup lang="ts">
import { defineProps, ref, watch } from 'vue';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import en from '@shene/table/dist/locale/en';
import {pagination} from '../../utils/table'

interface ResultRow {
  file: string;
  row: number;
  column: string;
  score: number;
  alignment: string;
}

const props = defineProps<{
  results: ResultRow[];
  loading: boolean;
}>();

// 国际化 & 分页
const locale = ref(en);

// 列定义
const columns = [
  { title: 'Database',      dataIndex: 'file',      key: 'file',                resizable: true,  width: 120 },
  { title: 'Row',       dataIndex: 'row',       key: 'row',                 resizable: true,  width:  60 },
  { title: 'Column',    dataIndex: 'column',    key: 'column',               resizable: true, width: 150 },
  { title: 'Score',     dataIndex: 'score',     key: 'score',                resizable: true, width:  80,
    sorter: (a: ResultRow, b: ResultRow) => a.score - b.score
  },
  { title: 'Alignment', dataIndex: 'alignment', key: 'alignment', ellipsis: false }
] as STableColumnsType<ResultRow>;

// 当结果变更时更新分页 total
watch(() => props.results.length, len => {
  pagination.value.total = len;
});

// 文件名到数据库名的映射
const fileToDbMap: Record<string,string> = {
  'Coding Variation in Cancer.csv':           'Cancer',
  'Coding Variation in Genetic Disease.csv':  'Genetic Disease',
  'Nonsense Sup-RNA.csv':                     'Nonsense Suppressors',
  'Frameshift sup-tRNA.csv':                  'Frameshift sup-tRNA',
  'tRNAtherapeutics.csv':                     'Engineered Sup-tRNA',
  'Function and Modification.csv':            'Function & Modification',
  'aaRS Recognition.csv':                     'aaRS Recognition'
};
function mapFileToDb(fileName: string): string {
  const clean = fileName.replace(/^\ufeff/, '');
  return fileToDbMap[clean] || clean;
}

/**
 * 解析 alignment 文本，只提取中间的 matchLine 和 query 行
 * @param text 完整 alignment（含换行）
 */
function parseAlignment(text: string): { matchLine: string; queryChars: string[] } {
  // 将 JSON 中的 "\n" 转成真正换行
  const real = (text as string).replace(/\\n/g, '\n');
  const parts = real.split('\n');
  // parts[0] = "target ...."
  // parts[1] = "||||.."
  // parts[2] = "query  XXXXXXXXX"
  const matchLine = parts[1] || '';
  const queryLine = parts[2] || '';
  // 去掉前缀 "query  "
  const querySeq = queryLine.replace(/^query\s*/, '');
  return {
    matchLine,
    queryChars: Array.from(querySeq)
  };
}
</script>

<style scoped>
.alignment {
  font-family: monospace;
  white-space: nowrap;
  line-height: 1.4;
}
.alignment .match {
  color: #4CAF50;
  font-weight: bold;
}
.no-results {
  text-align: center;
  padding: 1rem;
  color: #666;
}
</style>