<template>
  <div class="site--main">
    <h2>Elongation Factor Recognition site</h2>
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
        :pagination="pagination"
        :loading="loading"
        @update:pagination="handlePaginationUpdate"
        @change="handleSorterChange"
      >
      <template #bodyCell="{ text, column, record }">
          <template v-if="column.key === 'species'">
            <span class="latin-name">{{ record.species }}</span>
          </template>
          </template>
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>tRNA families:</b> {{ record['tRNA families'] }}</p>
            <p v-if="record['Acceptor branch']"><b>Acceptor branch:</b> {{ record['Acceptor branch'] }}</p>
            <p v-if="record['Core region']"><b>Core region:</b> {{ record['Core region']}}</p>
            <p v-if="record['Anticodon branch']"><b>Anticodon branch:</b> {{ record['Anticodon branch'] }}</p>
            <p v-if="record['Modification elements']"><b>Modification elements:</b> {{ record['Modification elements'] }}</p>
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
import { allColumns ,selectedColumns} from './EFTUcolumns';
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
    const TABLE_NAME = 'ef_tu';
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

    // Stable rowKey
    const rowKey = (r: any, idx: number) =>
      r?.key ?? `${r?.species ?? ''}-${r?.['tRNA families'] ?? ''}-${idx}`;

    const triggerColumnChange = () => {
      // 模拟点击列选择控件以触发数据刷新
      selectedColumns.value = [...selectedColumns.value];
    };

    watchSearch();

    onMounted(async() => {
      await loadPage();
      triggerColumnChange();
    });

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    return {
      columns: displayedColumns,
      rows,
      tableSize,
      loading,
      searchText,
      locale,
      selectedColumns,
      displayedColumns,
      searchColumn, // 添加搜索列
      allColumns, // 列选择控件
      triggerColumnChange,
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

.bracket-links {
  color: var(--link-meta);
  text-decoration: none;
}

.bracket-links:hover {
  color: var(--link-meta-hover);
  text-decoration: underline;
}

.latin-name {
            font-style: italic;
            font-family: 'Times New Roman', Times, serif; /* 替换为你想要的字体 */
            font-size: 16px; /* 可选：调整字体大小 */
            color: #333; /* 可选：设置字体颜色 */
        }
</style>
