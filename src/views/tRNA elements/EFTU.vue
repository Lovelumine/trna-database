<template>
  <div class="site--main">
    <h2>Elongation Factor Recognition site</h2>
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
        :data-source="filteredDataSource"
        :row-key="record => record.key"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
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
import { defineComponent, ref, onMounted, computed,watch } from 'vue';
import { STableProvider } from '@shene/table';
import { ElSelect, ElOption } from 'element-plus';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import {highlightModification} from '../../utils/highlightModification.js'
import {pagination} from '../../utils/table'
import { allColumns ,selectedColumns} from './EFTUcolumns';

// 定义数据类型
type DataType = { [key: string]: string };
import en from '@shene/table/dist/locale/en'
const locale = ref(en)

export default defineComponent({
  name: 'TrnaElements1',
  components: {
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource,  searchColumn,loadData } = useTableData('https://minio.lumoxuan.cn/ensure/EF-Tu.csv');
    const tableSize = ref('default'); // 表格尺寸状态


    onMounted(async() => {
      await loadData();
      triggerColumnChange();
    });

    const triggerColumnChange = () => {
      // 模拟点击列选择控件以触发数据刷新
      selectedColumns.value = [...selectedColumns.value];
    };

    watch([tableSize, searchColumn, searchText, selectedColumns], async () => {
      await loadData();
    });



    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      locale,
      selectedColumns,
      displayedColumns,
      searchColumn, // 添加搜索列
      allColumns, // 列选择控件
      highlightModification,
      triggerColumnChange,
      pagination
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
