<template>
  <div class="site--main">
    <h2>Function and Modification</h2>
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
      >
      <template #bodyCell="{ text, column, record }">
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
import { defineComponent, ref, onMounted, computed,watch } from 'vue';
import { STableProvider } from '@shene/table';
import { ElSelect, ElOption } from 'element-plus';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import {highlightModification} from '../../utils/highlightModification.js'

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
    const { searchText, filteredDataSource,  searchColumn,loadData } = useTableData('https://minio.lumoxuan.cn/ensure/Function and Modification.csv');
    const tableSize = ref('default'); // 表格尺寸状态
    const selectedColumns = ref<string[]>([
      'Modification_Type',
      'Function_of_Modification',
      'tissue_or_cell_line',
      'PMID'
    ]);

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

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Modification Type', dataIndex: 'Modification_Type', width: 140, ellipsis: true, key: 'Modification_Type', resizable: true },
      { title: 'Modomics CODE', dataIndex: 'Modomics_CODE', width: 140, ellipsis: true, key: 'Modomics_CODE', resizable: true },
      { title: 'Modification site', dataIndex: 'Modification_site', width: 500, ellipsis: true, key: 'Modification_site', resizable: true },
      { title: 'tRNA TYPE', dataIndex: 'tRNA_TYPE', width: 500, ellipsis: true, key: 'tRNA_TYPE', resizable: true },
      { title: 'Function of Modification', dataIndex: 'Function_of_Modification', width: 560, ellipsis: true, key: 'Function_of_Modification', resizable: true },
      { title: 'species', dataIndex: 'species', width: 200, ellipsis: true, key: 'species', resizable: true, customRender: ({ text, record }) => (<span className="latin-name">{record.species}</span>)},
      { title: 'tissue or cell line', dataIndex: 'tissue_or_cell_line', width: 240, ellipsis: true, key: 'tissue_or_cell_line', resizable: true },
      { title: 'condition', dataIndex: 'condition', width: 200, ellipsis: true, key: 'condition', resizable: true },      
      {
        title: 'PMID', width: 112, ellipsis: true, key: 'PMID', dataIndex: 'PMID',
        customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID || '#'} target="_blank" class="bracket-links">{record.PMID}</a></div>),
        resizable: true
      }
    ];

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
      triggerColumnChange
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
