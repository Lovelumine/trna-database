<template>
  <div class="site--main">
    <h2>Coding Variation in Cancers</h2>

    <!-- 顶部行 -->
    <TableToolbar
      v-model="searchText"
      v-model:column="searchColumn"
      v-model:size="tableSize"
      v-model:selected-columns="selectedColumns"
      :search-columns="allColumns"
      :display-columns="allColumns"
    >
      <template #actions>
        <div v-if="isAdmin" class="index-controls">
          <el-button size="small" :loading="rebuildLoading" @click="rebuildFulltext">
            Refresh Search Index
          </el-button>
        </div>
      </template>
    </TableToolbar>

    <!-- 表格 -->
    <s-table-provider :hover="true" :locale="locale">
      <s-table
        :columns="displayedColumns"
        :data-source="filteredDataSource"
        :row-key="rowKey"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
        :loading="loading"
        @update:pagination="handlePaginationUpdate"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'DISEASE'">
            <ElSpace>
              <ElTag
                v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))"
                :key="items"
                :type="getTagType(items)"
              >
                {{ items }}
              </ElTag>
            </ElSpace>
          </template>
        </template>

        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Gene Name:</b> {{ record.GENE_NAME }}</p>
            <p><b>Ensembl ID:</b> {{ record.ENSEMBL_ID }}</p>
            <p><b>Genomic Mutation ID:</b> <a :href="record.GENOMIC_MUTATION_URL" target="_blank" class="tilt-hover">{{ record.GENOMIC_MUTATION_ID }}</a></p>
            <p><b>Legacy Mutation ID:</b> <a :href="record.LEGACY_MUTATION_URL" target="_blank" class="tilt-hover">{{ record.LEGACY_MUTATION_ID }}</a></p>
            <p><b>Mutation Locus in GRCh37:</b> {{ record.MUTATION_LOCUS_IN_GRCh37 }}</p>
            <p><b>Mutation Locus in GRCh38:</b> {{ record.MUTATION_LOCUS_IN_GRCh38 }}</p>
            <p><b>Mutation Type:</b> {{ record.MUTATION_TYPE }}</p>
            <p><b>Mutation CDS:</b> {{ record.MUTATION_CDS }}</p>
            <p><b>MUTATION AA:</b> {{ record.MUTATION_AA }}</p>
            <p><b>Genomic Ref Allele:</b> {{ record.GENOMIC_REF_ALLELE }}</p>
            <p><b>Genomic Mut Allele:</b> {{ record.GENOMIC_MUT_ALLELE }}</p>
            <p><b>Disease:</b>
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))"
                  :key="items"
                  :type="getTagType(items)"
                >
                  {{ items }}
                </ElTag>
              </ElSpace>
            </p>
          </div>
        </template>
      </s-table>
    </s-table-provider>

    <!-- 图表 -->
    <section class="chart-section-wrapper">
      <div class="chart-row">
        <div class="chart-col">
          <h3>④ Ref→Mut Allele Heatmap</h3>
          <VChart :option="alleleHeatmapOption" autoresize style="height:400px;" />
        </div>

        <div class="chart-col">
          <h3>⑤ Cancer Disease Word Cloud</h3>
          <VChart :option="diseaseWordcloudOption" autoresize style="height:400px;" />
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElSelect, ElOption, ElButton, ElMessage } from 'element-plus';
import axios from 'axios';
import { STableProvider } from '@shene/table';
import { useMysqlTableData } from '../../utils/useMysqlTableData';
import { getTagType } from '../../utils/tag.js';
import type { EChartsOption } from 'echarts';
import { createPagination } from '../../utils/table';
import { allColumns, selectedColumns } from './CodingVariationCancerColumns';
import TableToolbar from '@/components/TableToolbar.vue';

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'CodingVariationDisease2',
  components: { ElTooltip, ElTag, ElSpace, ElSelect, ElOption, ElButton, TableToolbar },
  setup() {
    const TABLE_NAME = 'coding_variation_cancer';
    const { rows, total, loading, fetchRows, prefetchRange, cancelPrefetch, fetchStats } =
      useMysqlTableData(TABLE_NAME);
    const isAdmin = computed(() => {
      try {
        return new URLSearchParams(window.location.search).get('admin') === '1';
      } catch {
        return false;
      }
    });
    const searchText = ref('');
    const searchColumn = ref('');
    const pagination = createPagination();
    const tableSize = ref<'small' | 'default' | 'large'>('default');
    const stats = ref<{ allele_heatmap?: any[]; disease_wordcloud?: any[] }>({});
    const sortBy = ref('');
    const sortOrder = ref<'asc' | 'desc'>('asc');
    const rebuildLoading = ref(false);

    const normalizeDisease = (item: any) => {
      if (typeof item.DISEASE === 'string') {
        item.DISEASE = item.DISEASE
          .split(';')
          .map((s: string) => s.trim())
          .filter(Boolean);
      }
      return item;
    };

    const loadPage = async () => {
      cancelPrefetch();
      await fetchRows({
        page: pagination.current,
        pageSize: pagination.pageSize,
        searchText: searchText.value,
        searchColumn: searchColumn.value,
        sortBy: sortBy.value,
        sortOrder: sortOrder.value,
        useFulltext: searchColumn.value === ''
      });
      rows.value = rows.value.map(normalizeDisease);
      pagination.total = total.value;
      const maxPage = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));
      if (pagination.current > maxPage) pagination.current = maxPage;

      const PREFETCH_PAGES = 10;
      const remaining = maxPage - pagination.current;
      const count = Math.min(PREFETCH_PAGES, remaining);
      if (count > 0) {
        const baseParams = {
          page: pagination.current,
          pageSize: pagination.pageSize,
          searchText: searchText.value,
          searchColumn: searchColumn.value,
          sortBy: sortBy.value,
          sortOrder: sortOrder.value,
          useFulltext: searchColumn.value === ''
        };
        const run = () => {
          void prefetchRange(baseParams, count, { concurrency: 6 });
        };
        const idle = (window as any).requestIdleCallback;
        if (typeof idle === 'function') {
          idle(() => run());
        } else {
          window.setTimeout(() => run(), 0);
        }
      }
    };

    const loadStats = async () => {
      try {
        const resp = await fetchStats({
          stats: ['allele_heatmap', 'disease_wordcloud'],
          searchText: searchText.value,
          searchColumn: searchColumn.value,
          useFulltext: searchColumn.value === ''
        });
        stats.value = resp || {};
      } catch (err) {
        stats.value = {};
      }
    };

    onMounted(async () => {
      await loadPage();
      await loadStats();
      selectedColumns.value = [...selectedColumns.value]; // 可留可删
    });

    // 稳定 rowKey（不要用 index）
    const rowKey = (r: any) =>
      r?.GENOMIC_MUTATION_ID ?? r?.ENSEMBL_ID ?? `${r?.GENE_NAME ?? ''}-${r?.MUTATION_CDS ?? ''}`;

    let searchTimer: number | null = null;
    const scheduleSearch = () => {
      if (searchTimer) window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(async () => {
        pagination.current = 1;
        await loadPage();
        await loadStats();
      }, 300);
    };

    watch([searchText, searchColumn], scheduleSearch);

    const extractSorter = (sorter: any) => {
      if (!sorter) return null;
      const normalized = Array.isArray(sorter) ? sorter[0] : sorter;
      const field =
        normalized?.field || normalized?.columnKey || normalized?.dataIndex || normalized?.key;
      const orderRaw = normalized?.order || normalized?.sortOrder;
      if (!field || !orderRaw) return null;
      const order =
        orderRaw === 'ascend'
          ? 'asc'
          : orderRaw === 'descend'
          ? 'desc'
          : orderRaw === 'asc' || orderRaw === 'desc'
          ? orderRaw
          : null;
      if (!order) return null;
      return { field, order };
    };

    const handlePaginationUpdate = (p: any) => {
      if (p) Object.assign(pagination, p);
      loadPage();
    };

    const handleTableChange = (page?: any, _filters?: any, sorter?: any) => {
      if (page) Object.assign(pagination, page);
      const s = extractSorter(sorter);
      if (s) {
        sortBy.value = s.field;
        sortOrder.value = s.order;
        pagination.current = 1;
      } else {
        sortBy.value = '';
        sortOrder.value = 'asc';
      }
      loadPage();
    };

    const rebuildFulltext = async () => {
      rebuildLoading.value = true;
      try {
        await axios.post('/table_fulltext_rebuild', {
          table: TABLE_NAME,
          index_name: 'ft_all'
        });
        ElMessage.success('Search index refreshed');
      } catch (err: any) {
        ElMessage.error(err?.response?.data?.error || err?.message || 'Refresh failed');
      } finally {
        rebuildLoading.value = false;
      }
    };

    const displayedColumns = computed(() =>
      allColumns.filter((c) => selectedColumns.value.includes(c.key as string))
    );
    const filteredDataSource = computed(() => rows.value);

    // 1) Ref→Mut Heatmap
    const alleleHeatmapOption = computed<EChartsOption>(() => {
      const items = (stats.value?.allele_heatmap || []) as Array<{
        ref: string;
        mut: string;
        count: number;
      }>;
      const refSet = new Set<string>();
      const mutSet = new Set<string>();
      const combo = new Map<string, number>();

      items.forEach((item) => {
        const ref = item.ref || '';
        const mut = item.mut || '';
        if (!ref || !mut) return;
        refSet.add(ref);
        mutSet.add(mut);
        combo.set(`${ref}|||${mut}`, Number(item.count) || 0);
      });

      const refList = Array.from(refSet).sort();
      const mutList = Array.from(mutSet).sort();

      const data: [number, number, number][] = [];
      refList.forEach((ref, i) => {
        mutList.forEach((mut, j) => {
          const count = combo.get(`${ref}|||${mut}`) || 0;
          data.push([j, i, count]);
        });
      });

      const maxCount = data.length ? Math.max(...data.map((d) => d[2])) : 0;

      return {
        tooltip: {
          position: 'top',
          formatter: (params: any) => {
            const [x, y, v] = params.value as [number, number, number];
            return `Ref: ${refList[y]} → Mut: ${mutList[x]}<br/>Count: ${v}`;
          }
        },
        xAxis: { type: 'category', data: mutList, axisLabel: { rotate: 0 }, name: 'Mutated Allele' },
        yAxis: { type: 'category', data: refList, name: 'Reference Allele' },
        visualMap: { min: 0, max: maxCount, calculable: true, orient: 'horizontal', left: 'center', bottom: '-5%' },
        series: [{ type: 'heatmap', data, emphasis: { itemStyle: { borderColor: '#333', borderWidth: 1 } } }]
      };
    });

    // 2) Disease Word Cloud
    const diseaseWordcloudOption = computed<EChartsOption>(() => {
      const wordData = (stats.value?.disease_wordcloud || []).map((item: any) => ({
        name: String(item.name ?? ''),
        value: Number(item.value ?? 0)
      }));
      return {
        tooltip: { show: false },
        series: [
          {
            type: 'wordCloud',
            shape: 'circle',
            gridSize: 1,
            sizeRange: [12, 60],
            rotationRange: [-90, 90],
            rotationStep: 45,
            left: 'center',
            top: 'center',
            width: '100%',
            height: '100%',
            textStyle: {
              color: () => {
                const r = Math.round(Math.random() * 160);
                const g = Math.round(Math.random() * 160);
                const b = Math.round(Math.random() * 160);
                return `rgb(${r},${g},${b})`;
              }
            },
            data: wordData
          }
        ]
      };
    });

    return {
      // 表格
      displayedColumns,
      filteredDataSource,
      loading,
      tableSize,
      searchText,
      locale,
      searchColumn,
      selectedColumns,
      allColumns,
      getTagType,
      rebuildLoading,
      rebuildFulltext,
      isAdmin,
      // 分页
      pagination,
      handlePaginationUpdate,
      handleTableChange,
      rowKey,
      // 图表
      alleleHeatmapOption,
      diseaseWordcloudOption
    };
  }
});
</script>

<style scoped>
.site--main { padding: 20px; }
.chart-section-wrapper { overflow-x: auto; padding: 10px 0; }
.chart-row { display: flex; flex-direction: column; gap: 20px; }
.chart-col { width: 100%; }
</style>
