<template>
  <div class="site--main">
    <h2>tRNA Recognition AARS</h2>
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
            <p><b>AARS:</b> {{ record.aaRS }}</p>
            <p><b>Acceptor stem:</b> {{ record.AcceptorStem }}</p>
            <p><b>Anticodon arm:</b> {{ record.AnticodonArm }}</p>
            <p><b>Other location:</b> {{ record.OtherLocation }}</p>
            <p><b>Other domains:</b> {{ record.OtherDomains }}</p>
            <p><b>Reference/PMID:</b> 
              <span v-if="isPMID(record.Reference)">
                <span v-for="(pmid, index) in record.Reference.split(',')" :key="index">
                  <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + pmid.trim()" target="_blank" class="tilt-hover">{{ pmid.trim() }}</a>
                  <span v-if="index < record.Reference.split(',').length - 1">,</span>
                </span>
              </span>
              <span v-else>{{ record.Reference }}</span>
            </p>
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
type DataType = {
  aaRS: string;
  AcceptorStem: string;
  AnticodonArm: string;
  OtherLocation: string;
  OtherDomains: string;
  Reference: string;
};

import en from '@shene/table/dist/locale/en'
const locale = ref(en)

// 判断是否为PMID格式
function isPMID(reference) {
  return /^\d+(,\s*\d+)*$/.test(reference);
}

export default defineComponent({
  name: 'TrnaElements3',
  components: {
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNA elements-3.csv');
    const tableSize = ref('default'); // 表格尺寸状态
    const selectedColumns = ref<string[]>([
      'aaRS',
      'AcceptorStem',
      'AnticodonArm',
      'OtherLocation',
      'OtherDomains',
    ]);

    onMounted(() => {
      loadData();
    });

    const allColumns: STableColumnsType<DataType> = [
      {
        title: 'AARS',
        ellipsis: true,
        dataIndex: 'aaRS',
        resizable: true,
        key: 'aaRS',
        width: 120,
        fixed: true,
        align: 'center'
      },
      {
        title: 'Identity Element Location',
        key: 'IdentityElementLocation',
        align: 'center',
        ellipsis: true,
        resizable: true,
        children: [
          {
            title: 'Acceptor stem',
            dataIndex: 'AcceptorStem',
            key: 'AcceptorStem',
            resizable: true,
            ellipsis: true,
            width: 200,
            align: 'center'
          },
          {
            title: 'Anticodon arm',
            dataIndex: 'AnticodonArm',
            ellipsis: true,
            resizable: true,
            key: 'AnticodonArm',
            width: 200,
            align: 'center'
          },
          {
            title: 'Other location',
            dataIndex: 'OtherLocation',
            resizable: true,
            ellipsis: true,
            key: 'OtherLocation',
            width:160,
            align: 'center'
          },
          {
            title: 'Other domains (d-arm/T-arm/variable arm)',
            dataIndex: 'OtherDomains',
            key: 'OtherDomains',
            resizable: true,
            ellipsis: true,
            width: 300,
            align: 'center'
          }
        ]
      },
      {
        title: 'Reference/PMID',
        dataIndex: 'Reference',
        key: 'Reference',
        resizable: true,
        width: 200,
        align: 'center',
        ellipsis: true,
        customRender: ({ text, record }) => {
          if (isPMID(record.Reference)) {
            return (
              <div>
                {record.Reference.split(',').map((pmid, index, array) => (
                  <span key={pmid}>
                    <a href={`https://pubmed.ncbi.nlm.nih.gov/${pmid.trim()}`} target="_blank" class="bracket-links">{pmid.trim()}</a>
                    {index < array.length - 1 && ','}
                  </span>
                ))}
              </div>
            );
          } else {
            return <div>{record.Reference}</div>;
          }
        }
      }
    ];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string) || column.children?.some(child => selectedColumns.value.includes(child.key as string)))
    );

    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      locale,
      selectedColumns,
      displayedColumns,
      allColumns, // 列选择控件
      isPMID // 添加isPMID函数
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
  margin-right: 5px;
}

.bracket-links:hover {
  text-decoration: underline;
}
</style>
