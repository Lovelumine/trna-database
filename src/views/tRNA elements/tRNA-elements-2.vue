<template>
    <div class="site--main">
      <h2>tRNA Elements 2</h2>
      <!-- 顶部行包含尺寸调整和搜索框 -->
      <div class="top-controls">
        <!-- 搜索框 -->
        <div class="search-box" style="margin-bottom: 10px">
          <input v-model="searchText" placeholder="输入搜索内容" class="search-input">
        </div>
        <!-- 调整尺寸 -->
        <div class="size-controls" style="margin-bottom: 10px">
          <el-radio-group v-model="tableSize">
            <el-radio-button label="small">小尺寸</el-radio-button>
            <el-radio-button label="default">默认尺寸</el-radio-button>
            <el-radio-button label="large">大尺寸</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <!-- 表格组件 -->
      <s-table-provider :hover="true" :theme-color="'#00ACF5'">
        <s-table
          :columns="columns"
          :data-source="filteredDataSource"
          :row-key="record => record.key"
          :pagination="pagination"
          :stripe="true"
          :show-sorter-tooltip="true"
          :size="tableSize"
          @sorter-change="onSorterChange"
          @resize-column="onResizeColumn"
          @pagination-change="onPaginationChange"
          :row-expandable="rowExpandable"
          :expand-icon-column-index="expandIconColumnIndex"
          :expand-row-by-click="expandRowByClick"
          @expand="onExpand"
          @expandedRowsChange="onExpandedRowsChange"
        >
          <template #expandedRowRender="{ record }">
            <div>
              <p><b>tRNA特征:</b> {{ record.tRNA特征 }}</p>
              <p><b>功能:</b> {{ record.功能 }}</p>
              <p><b>细胞:</b> {{ record.细胞 }}</p>
              <p><b>参考文献:</b> {{ record.参考文献 }}</p>
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
        { title: 'AARS', dataIndex: 'AARS', width: 120, ellipsis: true, key: 'AARS', resizable: true },
        { title: 'tRNA特征', dataIndex: 'tRNA特征', width: 320, ellipsis: true, key: 'tRNA特征', resizable: true },
        { title: '功能', dataIndex: '功能', width: 320, ellipsis: true, key: '功能', resizable: true },
        { title: '细胞', dataIndex: '细胞', width: 200, ellipsis: true, key: '细胞', resizable: true },
        {
          title: '参考文献', width: 120, ellipsis: true, key: '参考文献', dataIndex: '参考文献',
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
  