<template>
    <div class="site--main">
      <h2>tRNA Elements 3</h2>
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
              <p><b>Acceptor stem:</b> {{ record.AcceptorStem }}</p>
              <p><b>Anticodon arm:</b> {{ record.AnticodonArm }}</p>
              <p><b>Other location:</b> {{ record.OtherLocation }}</p>
              <p><b>Other domains:</b> {{ record.OtherDomains }}</p>
              <p><b>Reference:</b> {{ record.Reference }}</p>
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
    name: 'TrnaElements3',
    setup() {
      const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNA elements-3.csv');
      const tableSize = ref('default'); // 表格尺寸状态
  
      onMounted(() => {
        loadData();
      });
  
      const columns: STableColumnsType<DataType> = [
        { title: 'aaRS', dataIndex: 'aaRS', width: 120, ellipsis: true, key: 'aaRS', resizable: true },
        { title: 'Acceptor stem', dataIndex: 'AcceptorStem', width: 320, ellipsis: true, key: 'AcceptorStem', resizable: true },
        { title: 'Anticodon arm', dataIndex: 'AnticodonArm', width: 320, ellipsis: true, key: 'AnticodonArm', resizable: true },
        { title: 'Other location', dataIndex: 'OtherLocation', width: 320, ellipsis: true, key: 'OtherLocation', resizable: true },
        { title: 'Other domains', dataIndex: 'OtherDomains', width: 320, ellipsis: true, key: 'OtherDomains', resizable: true },
        {
          title: 'Reference', width: 120, ellipsis: true, key: 'Reference', dataIndex: 'Reference',
          customRender: ({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">来源</a></div>),
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
  