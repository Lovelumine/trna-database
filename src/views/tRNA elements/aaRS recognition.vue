<template>
  <div class="site--main">
    <h2>aaRS Recognition</h2>
    <div class="top-controls">
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
        <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
          <el-option :key="'all'" :label="'All columns'" :value="''" />
          <el-option v-for="column in allColumns" :key="column.key" :value="column.dataIndex" />
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
        :data-source="filteredDataSource"
        :row-key="rowKey"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="paginationView"
        @update:pagination="(p) => Object.assign(pagination, p)"
        @change="handleTableChange"
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
import { defineComponent, ref, onMounted, watch, computed, toRaw } from 'vue';
import { ElSelect, ElOption } from 'element-plus';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import { allColumns, selectedColumns, isPMID } from './aaRScolumns';
import en from '@shene/table/dist/locale/en';

type DataType = {
  aaRS: string;
  AcceptorStem: string;
  AnticodonArm: string;
  OtherLocation: string;
  OtherDomains: string;
  Reference: string | number;
};

const locale = ref(en);

export default defineComponent({
  name: 'TrnaElements3',
  components: { ElSelect, ElOption },
  setup() {
    const { searchText, filteredDataSource, searchColumn, loadData } =
      useTableData('https://minio.lumoxuan.cn/ensure/aaRS%20Recognition.csv');

    const tableSize = ref<'small' | 'default' | 'large'>('default');

    // 受控分页对象
    const pagination = ref({
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true
    });

    onMounted(async () => {
      await loadData();
      // 触发列显示计算
      selectedColumns.value = [...selectedColumns.value];
    });

    // 给子组件一个“新引用”的分页对象，避免内部缓存老引用
    const paginationView = computed(() => ({ ...toRaw(pagination.value) }));

    // 稳定的 rowKey（避免用 index）
    const rowKey = (r: any, idx: number) =>
      r?.key ?? `${r?.aaRS ?? ''}-${r?.AcceptorStem ?? ''}-${idx}`;

    // 外部筛选变化 → 回到第 1 页
    watch([searchText, searchColumn, selectedColumns], () => {
      pagination.value.current = 1;
    });

    // 同步 total，并把 current 夹紧到合法页
    watch(
      () => filteredDataSource.value.length,
      (len) => {
        pagination.value.total = len;
        const maxPage = Math.max(1, Math.ceil(len / pagination.value.pageSize));
        if (pagination.value.current > maxPage) pagination.value.current = maxPage;
      },
      { immediate: true }
    );

    // pageSize 变化时也夹紧 current，并刷新 total
    watch(
      () => pagination.value.pageSize,
      () => {
        const total = filteredDataSource.value.length;
        pagination.value.total = total;
        const maxPage = Math.max(1, Math.ceil(total / pagination.value.pageSize));
        if (pagination.value.current > maxPage) pagination.value.current = maxPage;
      }
    );

    // 表格内部翻页/改每页条数：只合并 current/pageSize，并用外部筛选后的 total
    const handleTableChange = (page: any) => {
      if (page?.current != null)  pagination.value.current  = page.current;
      if (page?.pageSize != null) pagination.value.pageSize = page.pageSize;

      const total = filteredDataSource.value.length;
      pagination.value.total = total;

      const maxPage = Math.max(1, Math.ceil(total / pagination.value.pageSize));
      if (pagination.value.current > maxPage) pagination.value.current = maxPage;
    };

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
      filteredDataSource,
      rowKey,
      tableSize,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      allColumns,
      isPMID,
      // 分页
      pagination,
      paginationView,
      handleTableChange
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