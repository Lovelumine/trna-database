<template>
 <div class="site--main">
    <h2>tRNA Characterastic</h2>
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
    </div>
    <!-- 表格组件 -->
    <s-table-provider :hover="true" :theme-color="'#00ACF5'">
      <s-table
        :columns="columns"
        :data-source="filteredDataSource"
        :row-key="record => record.key"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
      >
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>tRNA Features:</b> {{ record.tRNA特征 }}</p>
            <p><b>Function:</b> {{ record.功能 }}</p>
            <p><b>Cells:</b> {{ record.细胞 }}</p>
            <p><b>Literature Source(PMID):</b><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record.参考文献" target="_blank" class="tilt-hover">{{record.参考文献}}</a></p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted } from 'vue';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';

// 定义数据类型
type DataType = { [key: string]: string };

export default defineComponent({
  name: 'TrnaElements2',
  setup() {
    const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNA elements-2.csv');
    const tableSize = ref('default'); // 表格尺寸状态

    onMounted(() => {
      loadData();
    });

    const columns: STableColumnsType<DataType> = [
      { title: 'tRNA Features', dataIndex: 'tRNA特征', width: 320, ellipsis: true, key: 'tRNA特征', resizable: true },
      { title: 'Function', dataIndex: '功能', width: 320, ellipsis: true, key: '功能', resizable: true },
      { title: 'Cells', dataIndex: '细胞', width: 200, ellipsis: true, key: '细胞', resizable: true },
      {
        title: 'PMID', width: 120, ellipsis: true, key: '参考文献', dataIndex: '参考文献',
        customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record.参考文献 || '#'} target="_blank" class="bracket-links">{record.参考文献}</a></div>),
        resizable: true
      }
    ];

    return {
      columns,
      filteredDataSource,
      tableSize,
      searchText,
    };
  }
});
</script>
