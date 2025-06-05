<template>
  <div class="site--main">
    <!-- 顶部线性进度条，仅在数据首次加载时显示（无限循环动效） -->
    <el-progress
      v-if="loading"
      :percentage="100"
      :indeterminate="true"
      :stroke-width="4"
      :show-text="false"
      style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000"
    />

    <div class="content-wrapper">
      <div class="top-controls">
        <!-- 搜索框 -->
        <div class="search-box">
          <input
            v-model="searchText"
            placeholder="Enter search content"
            class="search-input"
          />
          <el-select
            v-model="searchColumn"
            placeholder="Select column to search"
            class="search-column-select"
          >
            <el-option :key="'all'" :label="'All columns'" :value="''" />
            <el-option
              v-for="column in allColumns"
              :key="column.key"
              :value="column.dataIndex"
            />
          </el-select>
        </div>

        <!-- 大小切换 -->
        <div class="size-controls">
          <el-radio-group v-model="tableSize">
            <el-radio-button value="small">Small Size</el-radio-button>
            <el-radio-button value="default">Default Size</el-radio-button>
            <el-radio-button value="large">Large Size</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 选择显示列 -->
        <div class="column-controls">
          <el-select
            v-model="selectedColumns"
            multiple
            placeholder="Select columns to display"
            collapse-tags
            class="column-select"
          >
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
        >
          <template #bodyCell="{ text, column, record }">
            <template v-if="column.key === 'Citation'">
              <a>{{ text }}</a>
            </template>
            <template v-else-if="column.key === 'Related_disease'">
              <ElSpace>
                <ElTag
                  v-for="item in record.Related_disease.split(';').map(str => str.trim())"
                  :key="item"
                  :type="
                    item === 'cystic fibrosis'
                      ? 'danger'
                      : item === 'Model protein'
                      ? 'info'
                      : 'success'
                  "
                >
                  {{ item }}
                </ElTag>
              </ElSpace>
            </template>
          </template>
        </s-table>
      </s-table-provider>
    </div>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption, ElProgress } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import { allColumns } from './columns';
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
    ElProgress,
    TranStructure,
  },
  props: {
    selectedPmids: { type: Array, default: () => [] },
  },
  setup(props) {
    // 只在首次挂载时加载 CSV，一旦加载完成就不再重复 fetch
    const { searchText, filteredDataSource, searchColumn, loadData } =
      useTableData('https://minio.lumoxuan.cn/ensure/tRNAtherapeutics.csv');

    const tableSize = ref<'small' | 'default' | 'large'>('default');
    const selectedColumns = ref<string[]>([
      'Related_disease',
      'Species_source_of_origin_tRNA',
      'aa_and_anticodon_of_sup-tRNA',
      'Reaction_system',
      'pre_ENSURE_ID',
    ]);

    // 控制进度条显示，仅在第一次加载时 true
    const loading = ref(true);

    // 计算要显示的列
    const displayedColumns = computed(() =>
      allColumns.filter((col) =>
        selectedColumns.value.includes(col.key as string)
      )
    );

    // 根据父组件传来的 PMIDs 过滤数据
    const filteredDataSourceWithPmid = computed(() => {
      if (props.selectedPmids.length > 0) {
        return filteredDataSource.value.filter((record) =>
          props.selectedPmids.includes(String(record.PMID))
        );
      }
      return filteredDataSource.value;
    });

    // 首次挂载时调用一次 loadData，并关闭 loading
    onMounted(async () => {
      loading.value = true;
      await loadData();
      loading.value = false;
    });

    return {
      columns: displayedColumns,
      filteredDataSource: filteredDataSourceWithPmid,
      tableSize,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      allColumns,
      loading,
      TranStructure,
    };
  },
});
</script>

<style scoped>
.site--main {
  padding: 20px;
  position: relative;
}

.content-wrapper {
  display: flex;
  flex-direction: column;}

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.search-box {
  flex-grow: 1;
  margin-right: 10px;
}

.size-controls,
.column-controls {
  display: flex;
  align-items: center;
}

.column-select {
  margin-left: 10px;
  width: 200px; /* 设置选择框的宽度 */
}

.search-input {
  padding: 10px 20px;
  font-size: 16px;
  border: 2px solid #007cf07d;
  border-radius: 25px;
  width: 150px; /* 设置初始宽度 */
  transition: all 0.4s ease-in-out; /* 平滑过渡效果 */
}

.search-input:focus {
  width: 300px; /* 聚焦时扩展宽度 */
  outline: none;
  border-color: #0056b3;
}

.search-column-select {
  margin-left: 10px; /* 与搜索框之间的间距 */
  width: 150px; /* 设置选择框的宽度 */
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
  color: #409eff;
  text-decoration: underline;
}
</style>