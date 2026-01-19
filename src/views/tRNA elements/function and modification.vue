<template>
  <div class="site--main">
    <h2>Function of Modification</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
        <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
          <el-option :key="'all'" :label="'All columns'" :value="''" />
          <el-option
            v-for="column in allColumns"
            :key="column.key"
            :value="column.dataIndex"
          />
        </el-select>
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
        <el-select v-model="selectedColumns" multiple placeholder="Select columns to display" collapse-tags class="column-select">
          <el-option
            v-for="column in allColumns"
            :key="column.key"
            :label="column.title as string"
            :value="column.key"
          />
        </el-select>
      </div>
    </div>
    <!-- 表格组件 -->
    <s-table-provider :hover="true" :theme-color="'#00ACF5'" :locale="locale">
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
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'species'">
            <span class="latin-name">{{ record.species }}</span>
          </template>
        </template>

        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Modification Type:</b> {{ record.Modification_Type }}</p>
            <p><b>Modomics CODE:</b><span v-html="highlightModification(record['Modomics_CODE'])"></span></p>
            <p><b>Modification site:</b> {{ record.Modification_site }}</p>
            <p><b>tRNA TYPE:</b> {{ record.tRNA_TYPE }}</p>
            <p><b>Function of Modification:</b> {{ record.Function_of_Modification }}</p>
            <p><b>species:</b> <span class="latin-name">{{ record.species }}</span></p>
            <p><b>tissue or cell line:</b> {{ record.tissue_or_cell_line }}</p>
            <p><b>condition:</b> {{ record.condition}}</p>
            <p><b>Literature Source(PMID):</b><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID" target="_blank" class="tilt-hover">{{record.PMID}}</a></p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { STableProvider } from '@shene/table';
import { ElSelect, ElOption } from 'element-plus';
import { useServerTable } from '../../utils/useServerTable';
import { highlightModification } from '../../utils/highlightModification.js'
import { allColumns ,selectedColumns } from './FunctionAndModificationColumns';

import en from '@shene/table/dist/locale/en'
const locale = ref(en)

export default defineComponent({
  name: 'TrnaElements1',
  components: {
    ElSelect,
    ElOption
  },
  setup() {
    const TABLE_NAME = 'function_and_modification';
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

    // 稳定的 rowKey，避免展开/分页状态丢失
    const rowKey = (r: any, idx: number) => r?.key ?? r?.id ?? `${r?.tRNA_TYPE ?? ''}-${r?.Modification_site ?? ''}-${idx}`;

    watchSearch();

    onMounted(async () => {
      await loadPage();
      selectedColumns.value = [...selectedColumns.value];
    });

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    return {
      // 表格
      displayedColumns,
      rows,
      tableSize,
      loading,
      searchText,
      locale,
      selectedColumns,
      searchColumn,
      allColumns,
      highlightModification,
      // 分页
      pagination,
      handlePaginationUpdate,
      handleSorterChange,
      rowKey
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

.size-controls, .column-controls {
  display: flex;
  align-items: center;
}

.column-select {
  margin-left: 10px;
  width: 200px; /* 设置选择框的宽度 */
}

.bracket-links {
  color: #00ACF5;
  text-decoration: none;
}

.bracket-links:hover {
  text-decoration: underline;
}

.latin-name {
  font-style: italic;
  font-family: 'Times New Roman', Times, serif; /* 替换为你想要的字体 */
  font-size: 16px; /* 可选：调整字体大小 */
  color: #333; /* 可选：设置字体颜色 */
}
</style>
