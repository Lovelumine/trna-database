<template>
  <div class="site--main">
    <h2>Elongation Factor Recognition site</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box">
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
import { useServerTable } from '../../utils/useServerTable';
import { allColumns ,selectedColumns} from './EFTUcolumns';
import TableSearchBar from '@/components/TableSearchBar.vue';

import en from '@shene/table/dist/locale/en'
const locale = ref(en)

export default defineComponent({
  name: 'TrnaElements1',
  components: {
    ElSelect,
    ElOption,
    TableSearchBar
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
    } = useServerTable(TABLE_NAME);

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
