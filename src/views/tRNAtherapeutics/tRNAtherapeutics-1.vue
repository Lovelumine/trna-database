<template>
  <div class="site--main">
    <!-- 线性进度条：supData 加载时显示 -->
    <el-progress
      v-if="loadingSup"
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
            <el-option key="all" label="All columns" :value="''" />
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
import { defineComponent, ref, computed } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption, ElProgress } from 'element-plus';
import { STableProvider } from '@shene/table';
import { allColumns } from './columns';
import TranStructure from '@/components/TranStructure.vue';
import en from '@shene/table/dist/locale/en';

const locale = ref(en);

export default defineComponent({
  name: 'tRNAtherapeutics1',
  components: {
    ElTag,
    ElSpace,
    ElSelect,
    ElOption,
    ElProgress,
    TranStructure,
    STableProvider,
  },
  props: {
    selectedPmids:  { type: Array as () => string[], required: true },
    supData:        { type: Array as () => any[], required: true },
    loadingSup:     { type: Boolean, required: true },
  },
  setup(props) {
    // 本地搜索、大小、列控制
    const searchText      = ref('');
    const searchColumn    = ref('');
    const tableSize       = ref<'small'|'default'|'large'>('default');
    const selectedColumns = ref<string[]>([
      'PTC_gene',
      'Species_source_of_origin_tRNA',
      'aa_and_anticodon_of_sup-tRNA',
      'Reaction_system',
      'pre_ENSURE_ID',
      'Reading_through_efficiency'
    ]);

    // 计算要显示的列
    const columns = computed(() =>
      allColumns.filter(col => selectedColumns.value.includes(col.key as string))
    );

    // 根据 PMIDs + 本地搜索 过滤 supData
    const filteredDataSource = computed(() => {
      let data = props.supData;
      if (props.selectedPmids.length) {
        data = data.filter(r => props.selectedPmids.includes(String(r.PMID)));
      }
      if (searchText.value) {
        data = data.filter(r => {
          const hay = (searchColumn.value
            ? String(r[searchColumn.value])
            : Object.values(r).join(' ')
          ).toLowerCase();
          return hay.includes(searchText.value.toLowerCase());
        });
      }
      return data;
    });

    return {
      locale,
      columns,
      filteredDataSource,
      tableSize,
      searchText,
      searchColumn,
      selectedColumns,
      allColumns
    };
  }
});
</script>

<style scoped>
.site--main {
  padding: 20px;
}
.content-wrapper {
  display: flex;
  flex-direction: column;
}
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
  width: 200px;
}
.search-input {
  padding: 10px 20px;
  font-size: 16px;
  border: 2px solid #007cf07d;
  border-radius: 25px;
  width: 150px;
  transition: all 0.4s ease-in-out;
}
.search-input:focus {
  width: 300px;
  outline: none;
  border-color: #0056b3;
}
.search-column-select {
  margin-left: 10px;
  width: 150px;
}
</style>