<template>
  <div class="site--main">
    <div >
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
      <s-table-provider :hover="true" :locale="locale">
        <s-table
          :columns="columns"
          :data-source="filteredDataSource"
          :row-key="record => record.key"
          :stripe="true"
          :show-sorter-tooltip="true"
          :size="tableSize"
          :expand-row-by-click="true"
          :expanded-row-keys="expandedRowKeys"
          @expandedRowsChange="onExpandedRowsChange"
        >
          <template #bodyCell="{ text, column, record }">
            <template v-if="column.key === 'Citation'">
              <a>{{ text }}</a>
            </template>
            <template v-else-if="column.key === 'Related_disease'">
              <ElSpace>
                <ElTag v-for="item in record.Related_disease.split(';').map(str => str.trim())" :key="item" :type="item === 'cystic fibrosis' ? 'danger' : item === 'Model protein' ? 'info' : 'success'">
                  {{ item }}
                </ElTag>
              </ElSpace>
            </template>
            <!-- <template v-else-if="column.key === 'E_Value'">
              {{ alignments[record.key]?.eValue }}
            </template>
            <template v-else-if="column.key === 'Score'">
              {{ alignments[record.key]?.score }}
            </template>
            <template v-else-if="column.key === 'Alignment'">
              {{ alignments[record.key]?.alignment }}
            </template>
            <template v-else-if="column.key === 'Gaps'">
              {{ alignments[record.key]?.gaps }}
            </template> -->
          </template>
          <template #expandedRowRender="{ record }">
            <a :href="`expanded/${record.ENSURE_ID}`" target="_blank" class="tilt-hover">View Details</a>
          </template>
        </s-table>
      </s-table-provider>
    </div>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed, nextTick,watch } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import { calculateAlignment } from '../../utils/calculateAlignment';
import axios from 'axios';
import { allColumns, DataType } from './columns';
import TranStructure from '@/components/TranStructure.vue';

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'TRNATherapeutics-1',
  components: {
    ElTag,
    ElSpace,
    ElSelect,
    ElOption,
    TranStructure
  },
  setup() {
    const { searchText, filteredDataSource, searchColumn, loadData } = useTableData('/src/data/tRNAtherapeutics.csv');

    const tableSize = ref('default');
    const selectedColumns = ref<string[]>([
      'Related_disease',
      'PTC_model(nonsense_mutation_site)',
      'Species_source_of_origin_tRNA',
      'Sequence_of_sup-tRNA',
      'Reaction_system',
    ]);
    
    const loading = ref(true); // 添加加载状态

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    // const alignments = ref<{ [key: string]: any }>({});

    // const loadAlignments = async (dataSource: DataType[]) => {
    //   for (const record of dataSource) {
    //     const result = await calculateAlignment(record.Sequence_of_origin_tRNA, record.Sequence_of_sup_tRNA);
    //     alignments.value[record.key] = result;
    //   }
    // };

    // const secondaryStructures = ref<{ [key: string]: string }>({});

    // const loadSecondaryStructures = async (dataSource: DataType[]) => {
    //   console.log('Loading secondary structures...');
    //   for (const record of dataSource) {
    //     try {
    //       const response = await axios.post('/scan', { sequence: record.Sequence_of_sup_tRNA });
    //       console.log(`Fetched structure for record ${record.key}:`, response.data.str);
    //       secondaryStructures.value = { ...secondaryStructures.value, [record.key]: response.data.str };
    //     } catch (error) {
    //       console.error(`Failed to fetch secondary structure for record ${record.key}:`, error);
    //       secondaryStructures.value = { ...secondaryStructures.value, [record.key]: 'Error fetching structure' };
    //     }
    //   }
    //   console.log('Secondary structures loaded', secondaryStructures.value);
    //   await nextTick();
    // };

    const expandedRowKeys = ref([]);

    const onExpandedRowsChange = (expandedKeys) => {
      expandedRowKeys.value = expandedKeys.length > 0 ? [expandedKeys[expandedKeys.length - 1]] : [];
    };

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

    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      displayedColumns,
      calculateAlignment,
      allColumns,
      // alignments,
      // secondaryStructures,
      loading, // 添加到返回对象中
      TranStructure,
      expandedRowKeys,
      onExpandedRowsChange,
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

.expanded-row {
  border: 1px solid #ccc;
  padding: 16px;
  margin-bottom: 16px;
}

.section {
  margin-bottom: 16px;
}

.section h2 {
  margin-bottom: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

td {
  border: 1px solid #ddd;
  padding: 8px;
}

a {
  color: blue;
  text-decoration: underline;
}

.loading-message {
  font-size: 20px;
  text-align: center;
  padding: 20px;
}
</style>
