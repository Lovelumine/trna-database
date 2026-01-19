<template>
  <div class="site--main">
    <h2>aaRS Recognition</h2>
    <div class="top-controls">
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
        <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
          <el-option :key="'all'" :label="'All columns'" :value="''" />
          <el-option
            v-for="column in searchableColumns"
            :key="column.key"
            :label="column.title as string"
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
    </div>

    <s-table-provider :hover="true" :theme-color="'#00ACF5'" :locale="locale">
      <s-table
        :columns="displayedColumns"
        :data-source="rows"
        :row-key="rowKey"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
        :loading="loading"
        @update:pagination="handlePaginationUpdate"
        @change="handleSorterChange"
      >
        <template #expandedRowRender="{ record }">
          <div>
            <p v-if="record.aaRS"><b>AARS:</b> {{ record.aaRS }}</p>
            <p v-if="record.AcceptorStem"><b>Acceptor stem:</b> {{ record.AcceptorStem }}</p>
            <p v-if="record.AnticodonArm"><b>Anticodon arm:</b> {{ record.AnticodonArm }}</p>
            <p v-if="record.OtherLocation"><b>Other location:</b> {{ record.OtherLocation }}</p>
            <p v-if="record.OtherDomains"><b>Other domains:</b> {{ record.OtherDomains }}</p>
            <p><b>Reference/PMID:</b>
              <span v-if="isPMID(record.Reference)">
                <span v-for="(pmid, index) in String(record.Reference).split(',')" :key="index">
                  <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + pmid.trim()" target="_blank" class="tilt-hover">{{ pmid.trim() }}</a>
                  <span v-if="index < String(record.Reference).split(',').length - 1">, </span>
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
import { ElSelect, ElOption } from 'element-plus';
import { useServerTable } from '../../utils/useServerTable';
import { allColumns, selectedColumns, isPMID } from './aaRScolumns';
import en from '@shene/table/dist/locale/en';

const locale = ref(en);

export default defineComponent({
  name: 'TrnaElements3',
  components: { ElSelect, ElOption },
  setup() {
    const TABLE_NAME = 'aars_recognition';
    const {
      rows,
      loading,
      searchText,
      searchColumn,
      tableSize,
      pagination,
      loadPage,
      handlePaginationUpdate,
      handleSorterChange,
      watchSearch
    } = useServerTable(TABLE_NAME);

    // 稳定的 rowKey（避免用 index）
    const rowKey = (r: any, idx: number) =>
      r?.key ?? `${r?.aaRS ?? ''}-${r?.AcceptorStem ?? ''}-${idx}`;

    watchSearch();

    onMounted(async () => {
      await loadPage();
      selectedColumns.value = [...selectedColumns.value];
    });

    // 搜索列：只展示带 dataIndex 的叶子列，避免 undefined
    const searchableColumns = computed(() => {
      const cols: any[] = [];
      allColumns.forEach((column: any) => {
        if (column.dataIndex) cols.push(column);
        if (Array.isArray(column.children)) {
          column.children.forEach((child: any) => {
            if (child?.dataIndex) cols.push(child);
          });
        }
      });
      return cols;
    });

    // 列显示：父列/子列一起按 selectedColumns 过滤
    const displayedColumns = computed(() =>
      allColumns.flatMap((column) => {
        if (selectedColumns.value.includes(column.key as string)) {
          return column;
        }
        if (column.children) {
          const children = column.children.filter((c) =>
            selectedColumns.value.includes(c.key as string)
          );
          if (children.length) {
            return { ...column, children };
          }
        }
        return [];
      })
    );

    return {
      // 表格
      displayedColumns,
      rows,
      rowKey,
      tableSize,
      loading,
      searchText,
      searchColumn,
      locale,
      searchableColumns,
      selectedColumns,
      allColumns,
      isPMID,
      // 分页
      pagination,
      handlePaginationUpdate,
      handleSorterChange
    };
  }
});
</script>

<style scoped>
.site--main { padding: 20px; }
.top-controls { display: flex; justify-content: space-between; align-items: center; }
.search-box { flex-grow: 1; margin-right: 10px; display: flex; gap: 8px; }
.size-controls, .column-controls { display: flex; align-items: center; }
.column-select { margin-left: 10px; width: 200px; }
.bracket-links { color: #00ACF5; text-decoration: none; margin-right: 5px; }
.bracket-links:hover { text-decoration: underline; }
</style>
