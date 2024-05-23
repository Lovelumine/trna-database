<template>
  <div class="site--main">
    <h2>tRNA Elements 1</h2>
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
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
      >
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>功能:</b> {{ record.功能 }}</p>
            <p><b>功能发挥细胞:</b> {{ record.功能发挥细胞 }}</p>
            <p><b>文献来源:</b>{{record.文献来源}}</p>
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
  name: 'TrnaElements1',
  setup() {
    const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNA elements-1.csv');
    const tableSize = ref('default'); // 表格尺寸状态

    onMounted(() => {
      loadData();
    });

    const columns: STableColumnsType<DataType> = [
      { title: '修饰', dataIndex: '修饰', width: 120, ellipsis: true, key: '修饰', resizable: true },
      { title: '功能', dataIndex: '功能', width: 320, ellipsis: true, key: '功能', resizable: true },
      { title: '功能发挥细胞', dataIndex: '功能发挥细胞', width: 200, ellipsis: true, key: '功能发挥细胞', resizable: true },
      {
        title: '文献来源', width: 320, ellipsis: true, key: '文献来源', dataIndex: '文献来源',
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
