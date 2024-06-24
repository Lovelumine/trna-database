<template>
  <div class="site--main">
    <h2>Construction of sup-tRNA</h2>
    <!-- 顶部行包含尺寸调整、搜索框和列选择 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box" style="margin-bottom: 10px">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
      </div>
      <!-- 调整尺寸 -->
      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize">
          <el-radio-button value="small">Small Size</el-radio-button>
          <el-radio-button value="default">Default Size</el-radio-button>
          <el-radio-button value="large">Large Size</el-radio-button>
        </el-radio-group>
      </div>
      <!-- 选择显示列 -->
      <div class="column-controls" style="margin-bottom: 10px">
        <el-select v-model="selectedColumns" multiple placeholder="Select columns to display" collapse-tags
          class="column-select">
          <el-option v-for="column in allColumns" :key="column.key" :label="column.title as string"
            :value="column.key" />
        </el-select>
      </div>
    </div>
    <!-- 表格组件 -->
    <s-table-provider :hover="true" :locale="locale">
      <s-table :columns="displayedColumns" :data-source="filteredDataSource" :row-key="record => record.key"
        :stripe="true" :show-sorter-tooltip="true" :size="tableSize" :expand-row-by-click="true">
        <template #bodyCell="{ text, column, record }">
          <template v-if="column.key === 'Structure of sup-tRNA'">
            <el-image style="width: 100px; height: 100px" :src="text" :preview-src-list="[text]" fit="cover" />
          </template>
          <template v-else>
            <span>{{ text }}</span>
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Species:</b> {{ record.Species }}</p>
            <p><b>Anticodon before mutation:</b> {{ record['Anticodon before mutation'] }}</p>
            <p><b>Anticodon after mutation:</b> {{ record['Anticodon after mutation'] }}</p>
            <p><b>Stop codon for readthrough:</b> {{ record['Stop codon for readthrough'] }}</p>
            <p><b>Noncanonical charged amino acids:</b> {{ record['Noncanonical charged amino acids'] }}</p>
            <p><b>tRNA sequence before mutation:</b> {{ record['tRNA sequence before mutation'] }}</p>
            <p><b>tRNA sequence after mutation:</b> <span
                v-html="highlightMutation(record['tRNA sequence after mutation'])"></span></p>
            <p><b>Readthrough mechanism:</b> {{ record['Readthrough mechanism'] }}</p>
            <p><b>Mutational position of sup-tRNA:</b> {{ record['Mutational position of sup-tRNA'] }}</p>
            <p><b>PMID of references:</b> {{ record['PMID of references'] }}</p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';


type DataType = {
  [key: string]: string | string[];
  Species: string;
  'Anticodon before mutation': string;
  'Anticodon after mutation': string;
  'Stop codon for readthrough': string;
  'Noncanonical charged amino acids': string;
  'tRNA sequence before mutation': string;
  'tRNA sequence after mutation': string;
  'Structure of sup-tRNA': string;
  'Readthrough mechanism': string;
  'Mutational position of sup-tRNA': string;
  'PMID of references': string;
};

import en from '@shene/table/dist/locale/en'
const locale = ref(en)

export default defineComponent({
  name: 'Construction-of-sup-tRNA',
  components: {
    ElTooltip,
    ElImage,
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource, loadData } = useTableData('/data/Construction of sup-tRNA.csv');

    const tableSize = ref('default');
    const selectedColumns = ref<string[]>(['Species', 'Anticodon before mutation', 'Anticodon after mutation', 'Stop codon for readthrough', 'Mutational position of sup-tRNA']);

    onMounted(() => {
      loadData();
    });

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Species', dataIndex: 'Species', width: 150, ellipsis: true, key: 'Species', resizable: true },
      { title: 'Anticodon before mutation', dataIndex: 'Anticodon before mutation', width: 180, ellipsis: true, key: 'Anticodon before mutation', resizable: true },
      { title: 'Anticodon after mutation', dataIndex: 'Anticodon after mutation', width: 180, ellipsis: true, key: 'Anticodon after mutation', resizable: true },
      { title: 'Stop codon for readthrough', dataIndex: 'Stop codon for readthrough', width: 180, ellipsis: true, key: 'Stop codon for readthrough', resizable: true },
      { title: 'Noncanonical charged amino acids', dataIndex: 'Noncanonical charged amino acids', width: 150, ellipsis: true, key: 'Noncanonical charged amino acids', resizable: true },
      { title: 'tRNA sequence before mutation', dataIndex: 'tRNA sequence before mutation', width: 200, ellipsis: true, key: 'tRNA sequence before mutation', resizable: true },
      { title: 'tRNA sequence after mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      { title: 'Structure of sup-tRNA', dataIndex: 'Structure of sup-tRNA', width: 150, ellipsis: true, key: 'Structure of sup-tRNA', resizable: true },
      { title: 'Readthrough mechanism', dataIndex: 'Readthrough mechanism', width: 200, ellipsis: true, key: 'Readthrough mechanism', resizable: true },
      { title: 'Mutational position of sup-tRNA', dataIndex: 'Mutational position of sup-tRNA', width: 250, ellipsis: true, key: 'Mutational position of sup-tRNA', resizable: true },
      { title: 'PMID of references', dataIndex: 'PMID of references', width: 150, ellipsis: true, key: 'PMID of references', resizable: true }
    ];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    const highlightMutation = (sequence) => {
      if (!sequence) return sequence;

      let highlightedSequence = '';
      let lastIndex = 0;

      const regex = /(\\\\\\[A-Z])|(\\\\[A-Z])|(\\[A-Z])/g;
      let match;

      while ((match = regex.exec(sequence)) !== null) {
        const [fullMatch] = match;
        const index = match.index;

        // 添加非突变部分
        if (index > lastIndex) {
          highlightedSequence += sequence.slice(lastIndex, index);
        }

        // 添加突变部分
        if (fullMatch.startsWith("\\\\\\\\")) { // 删除
          const base = fullMatch[4];
          highlightedSequence += `<span style="text-decoration: line-through; color: black;" title="Deleted ${base}">${base}</span>`;
        } else if (fullMatch.startsWith("\\\\")) { // 增添
          const base = fullMatch[2];
          highlightedSequence += `<span style="color: green;" title="Added ${base}">${base}</span>`;
        } else if (fullMatch.startsWith("\\")) { // 替换
          const base = fullMatch[1];
          highlightedSequence += `<span style="color: red;" title="Replaced with ${base}">${base}</span>`;
        }

        lastIndex = index + fullMatch.length;
      }

      // 添加剩余部分
      if (lastIndex < sequence.length) {
        highlightedSequence += sequence.slice(lastIndex);
      }

      return highlightedSequence;
    };



    return {
      allColumns,
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      locale,
      selectedColumns,
      displayedColumns,
      highlightMutation // 返回highlightMutation方法
    };
  }
});
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  flex-grow: 1;
  margin-right: 10px;
}

.size-controls,
.column-controls {
  display: flex;
  align-items: center;
}

.column-select {
  margin-left: 10px;
  width: 200px;
}
</style>