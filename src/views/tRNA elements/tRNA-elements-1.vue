<template>
  <div class="site--main">
    <h2>tRNA Modify-function</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box" style="margin-bottom: 10px">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
      </div>
      <!-- 调整尺寸 -->
      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize">
          <el-radio-button label="small">Small Size</el-radio-button>
          <el-radio-button label="default">Default Size</el-radio-button>
          <el-radio-button label="large">Large Size</el-radio-button>
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
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Modification:</b> {{ record.修饰 }}</p>
            <p><b>Modified tRNA:</b> {{ record.修饰的tRNA }}</p>
            <p><b>Function:</b> {{ record.功能 }}</p>
            <p><b>Functioning Species:</b> {{ record.功能发挥物种 }}</p>
            <p><b>Functioning Tissue or Cell Line:</b> {{ record.功能发挥细胞 }}</p>
            <p><b>Other Functioning Sites:</b> {{ record.功能发挥其他场所 }}</p>
            <p><b>Literature Source(PMID):</b><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record.文献来源" target="_blank" class="tilt-hover">{{record.文献来源}}</a></p>
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
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';

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
    const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNA elements-1.csv');
    const tableSize = ref('default'); // 表格尺寸状态
    const selectedColumns = ref<string[]>([
      '修饰',
      '功能',
      '功能发挥细胞',
      '文献来源'
    ]);

    onMounted(() => {
      loadData();
    });

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Modification', dataIndex: '修饰', width: 140, ellipsis: true, key: '修饰', resizable: true },
      { title: 'Modified tRNA', dataIndex: '修饰的tRNA', width: 140, ellipsis: true, key: '修饰的tRNA', resizable: true },
      { title: 'Function', dataIndex: '功能', width: 500, ellipsis: true, key: '功能', resizable: true },
      { title: 'Functioning Species', dataIndex: '功能发挥物种', width: 500, ellipsis: true, key: '功能发挥物种', resizable: true },
      { title: 'Functioning Tissue or Cell Line', dataIndex: '功能发挥细胞', width: 200, ellipsis: true, key: '功能发挥细胞', resizable: true },
      { title: 'Other Functioning Sites', dataIndex: '功能发挥其他场所', width: 200, ellipsis: true, key: '功能发挥其他场所', resizable: true },
      {
        title: 'PMID', width: 112, ellipsis: true, key: '文献来源', dataIndex: '文献来源',
        customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record.文献来源 || '#'} target="_blank" class="bracket-links">{record.文献来源}</a></div>),
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
      allColumns // 列选择控件
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
</style>
