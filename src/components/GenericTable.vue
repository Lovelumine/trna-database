<template>
    <div class="generic-table">
      <!-- 表格组件 -->
      <s-table-provider :hover="hover" :theme-color="themeColor">
        <s-table
          :columns="columns"
          :data-source="dataSource"
          :row-key="rowKey"
          :pagination="pagination"
          :stripe="stripe"
          :show-sorter-tooltip="showSorterTooltip"
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
          <template v-slot:expandedRowRender="{ record }">
            <slot name="expandedRowRender" :record="record"></slot>
          </template>
        </s-table>
      </s-table-provider>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, PropType } from 'vue';
  import { STable, STableProvider } from '@shene/table'; 
  import { useTableData } from 'public/js/useTableData';
  
  export default defineComponent({
    name: 'GenericTable',
    components: {
      STableProvider,
      STable
    },
    props: {
      columns: {
        type: Array as PropType<any[]>,
        required: true
      },
      dataSource: {
        type: Array as PropType<any[]>,
        required: true
      },
      themeColor: {
        type: String,
        default: '#00ACF5'
      },
      pagination: {
        type: Object,
        default: () => ({
          defaultCurrent: 1,
          defaultPageSize: 10,
          showQuickJumper: true,
          showSizeChanger: true,
          showTotal: (total: number) => `共 ${total} 项数据`
        })
      },
      tableSize: {
        type: String,
        default: 'default'
      },
      rowExpandable: {
        type: Function as PropType<(record: any) => boolean>,
        default: () => true
      },
      expandIconColumnIndex: {
        type: Number,
        default: 0
      },
      expandRowByClick: {
        type: Boolean,
        default: true
      },
      hover: {
        type: Boolean,
        default: true
      },
      stripe: {
        type: Boolean,
        default: false
      },
      showSorterTooltip: {
        type: Boolean,
        default: true
      },
      rowKey: {
        type: Function as PropType<(record: any) => string>,
        default: record => record.key
      },
      onSorterChange: Function,
      onResizeColumn: Function,
      onPaginationChange: Function,
      onExpand: Function,
      onExpandedRowsChange: Function
    }
  });
  </script>
  
  <style scoped>
  .generic-table {

  }
  </style>
  