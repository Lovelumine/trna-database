<template>
  <div class="site--main">
    <h2>Function of Modification</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
    <TableToolbar
      v-model="searchText"
      v-model:column="searchColumn"
      v-model:size="tableSize"
      v-model:selected-columns="selectedColumns"
      :search-columns="allColumns"
      :display-columns="allColumns"
    />
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
        v-model:expandedRowKeys="expandedRowKeys"
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
import { useTableData } from '../../utils/useTableData';
import { highlightModification } from '../../utils/highlightModification.js'
import { allColumns ,selectedColumns } from './FunctionAndModificationColumns';
import TableToolbar from '@/components/TableToolbar.vue';

import en from '@shene/table/dist/locale/en'
const locale = ref(en)

export default defineComponent({
  name: 'TrnaElements1',
  components: {
    ElSelect,
    ElOption,
    TableToolbar
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
    } = useTableData(TABLE_NAME);

    // 稳定的 rowKey，避免展开/分页状态丢失
    const rowKey = (r: any, idx: number) => r?.id ?? r?.key ?? `${r?.tRNA_TYPE ?? ''}-${r?.Modification_site ?? ''}-${idx}`;

    const expandedRowKeys = ref<any[]>([]);

    const shouldAutoExpand = () => {
      if (typeof window === 'undefined') return false;
      const params = new URLSearchParams(window.location.search);
      const tableParam = params.get('table');
      if (tableParam && tableParam !== TABLE_NAME) return false;
      return params.get('expand') === '1';
    };

    const tryAutoExpand = () => {
      if (!shouldAutoExpand() || expandedRowKeys.value.length) return;
      if (!searchColumn.value || searchText.value === '') return;
      const target = rows.value.find(
        (row: any) => String(row?.[searchColumn.value]) === String(searchText.value)
      );
      if (target) {
        expandedRowKeys.value = [rowKey(target, 0)];
      }
    };

    watchSearch(() => {
      tryAutoExpand();
    });

    onMounted(async () => {
      await loadPage();
      selectedColumns.value = [...selectedColumns.value];
      tryAutoExpand();
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
      rowKey,
      expandedRowKeys
    };
  }
});
</script>

<style scoped>
.site--main {
  padding: 20px;
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
