<template>
  <div class="site--main">
    <h2>Construction of sup-tRNA</h2>
    <!-- 顶部行包含尺寸调整、搜索框和列选择 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box" style="margin-bottom: 10px">
        <TableSearchBar
          v-model="searchText"
          v-model:column="searchColumn"
          :columns="allColumns"
        />
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
      <s-table
        :columns="displayedColumns"
        :data-source="rows"
        :row-key="rowKey"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
        :loading="loading"
        @update:pagination="handlePaginationUpdate"
        @change="handleSorterChange"
      >
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
            <p><b>Species:</b> <em>{{ record.Species }}</em></p>
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
import { ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useServerTable } from '../../utils/useServerTable';
import { allColumns } from './Constructioncolumns';
import { highlightMutation } from '../../utils/highlightMutation.js';
import TableSearchBar from '@/components/TableSearchBar.vue';

import en from '@shene/table/dist/locale/en'
const locale = ref(en)

export default defineComponent({
  name: 'Construction-of-sup-tRNA',
  components: {
    ElImage,
    ElSelect,
    ElOption,
    TableSearchBar
  },
  setup() {
    const TABLE_NAME = 'construction_sup_trna';
    const {
      rows,
      loading,
      searchText,
      searchColumn,
      tableSize,
      pagination,
      loadPage,
      handlePaginationUpdate,
      handleSorterChange,
      watchSearch
    } = useServerTable(TABLE_NAME);

    const selectedColumns = ref<string[]>([
      'Species',
      'Anticodon before mutation',
      'Anticodon after mutation',
      'Stop codon for readthrough',
      'Mutational position of sup-tRNA'
    ]);

    watchSearch();

    onMounted(async () => {
      await loadPage();
    });

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    const rowKey = (r: any, idx: number) =>
      r?.key ?? r?.['RNA central ID of tRNA'] ?? `${r?.Species ?? ''}-${r?.['Anticodon after mutation'] ?? ''}-${idx}`;

    return {
      allColumns,
      columns: displayedColumns,
      rows,
      tableSize,
      loading,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      displayedColumns,
      pagination,
      handlePaginationUpdate,
      handleSorterChange,
      rowKey,
      highlightMutation
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
