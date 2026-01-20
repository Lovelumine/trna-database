<template>
  <div class="site--main">
    <h2>Nonsense sup-tRNA</h2>
    <!-- 顶部行包含尺寸调整、搜索框和列选择 -->
    <TableToolbar
      v-model="searchText"
      v-model:column="searchColumn"
      v-model:size="tableSize"
      v-model:selected-columns="selectedColumns"
      :search-columns="allColumns"
      :display-columns="allColumns"
    />

    <!-- 表格 -->
    <div class="custom-tag-styles">
      <s-table-provider :hover="true" :locale="locale">
        <s-table
          :columns="displayedColumns"
          :data-source="rows"
          :row-key="rowKey"
          :stripe="true"
          :show-sorter-tooltip="true"
          :size="tableSize"
        :expand-row-by-click="true"
        :loading="loading"
        :pagination="pagination"
        @update:pagination="handlePaginationUpdate"
        @change="handleTableChange"
        >
          <template #bodyCell="{ text, column, record }">
            <template v-if="column.key === 'Species'">
              <em>{{ text }}</em>
            </template>

            <template v-else-if="column.key === 'Structure of sup-tRNA'">
              <el-image style="width: 100px; height: 100px" :src="text" :preview-src-list="[text]" fit="cover" />
            </template>

            <template v-else-if="column.key === 'Stop codon for readthrough'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Stop codon for readthrough']) ? record['Stop codon for readthrough'] : record['Stop codon for readthrough'].split(';').map(str => str.trim()))"
                  :key="items"
                  :type="getTagType(items)"
                >{{ items }}</ElTag>
              </ElSpace>
            </template>

            <template v-else-if="column.key === 'Noncanonical charged amino acids'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids'] : record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))"
                  :key="items"
                  :type="getTagType(items)"
                >{{ items }}</ElTag>
              </ElSpace>
            </template>

            <template v-else-if="column.key === 'Readthrough mechanism'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Readthrough mechanism']) ? record['Readthrough mechanism'] : record['Readthrough mechanism'].split(';').map(str => str.trim()))"
                  :key="items"
                  :type="getTagType(items)"
                >{{ items }}</ElTag>
              </ElSpace>
            </template>

            <template v-else-if="column.key === 'PMID of references'">
              <ElSpace>
                <span v-for="(pmid, index) in getPmidList(record['PMID of references'])" :key="index">
                  <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + pmid.trim()" target="_blank" class="bracket-links">{{ pmid.trim() }}</a>
                  <span v-if="index < getPmidList(record['PMID of references']).length - 1">, </span>
                </span>
              </ElSpace>
            </template>

            <template v-else>
              <span>{{ text }}</span>
            </template>
          </template>

          <template #expandedRowRender="{ record }">
            <div>
              <p><b>Species:</b> <em>{{ record.Species }}</em></p>
              <p><b>Species ID:</b> {{ record['Species ID'] }}</p>
              <p><b>Tissue/Organelle of Origin:</b> {{ record['Tissue/Organelle of Origin'] }}</p>
              <p><b>Anticodon before mutation:</b> {{ record['Anticodon before mutation'] }}</p>
              <p><b>Anticodon after mutation:</b> {{ record['Anticodon after mutation'] }}</p>

              <p><b>Stop codon for readthrough:</b>
                <ElSpace>
                  <ElTag
                    v-for="items in (Array.isArray(record['Stop codon for readthrough']) ? record['Stop codon for readthrough'] : record['Stop codon for readthrough'].split(';').map(str => str.trim()))"
                    :key="items"
                    :type="getTagType(items)"
                  >{{ items }}</ElTag>
                </ElSpace>
              </p>

              <p><b>Noncanonical charged amino acids:</b>
                <ElSpace>
                  <ElTag
                    v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids'] : record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))"
                    :key="items"
                    :type="getTagType(items)"
                  >{{ items }}</ElTag>
                </ElSpace>
              </p>

              <p><b>RNA central ID of tRNA:</b> {{ record['RNA central ID of tRNA'] }}</p>
              <p><b>tRNA sequence before mutation:</b> {{ record['tRNA sequence before mutation'] }}</p>
              <p><b>tRNA sequence after mutation:</b> <span v-html="highlightMutation(record['tRNA sequence after mutation'])"></span></p>

              <div>
                <b>Structure of sup-tRNA:</b>
                <img
                  :src="`https://minio.lumoxuan.cn/ensure/picture/${record.pictureid}.png`"
                  @click="showLightbox(record.pictureid)"
                  style="width: 100px; cursor: pointer;"
                />
              </div>

              <p><b>Readthrough mechanism:</b>
                <ElSpace>
                  <ElTag
                    v-for="items in (Array.isArray(record['Readthrough mechanism']) ? record['Readthrough mechanism'] : record['Readthrough mechanism'].split(';').map(str => str.trim()))"
                    :key="items"
                    :type="getTagType(items)"
                  >{{ items }}</ElTag>
                </ElSpace>
              </p>

              <p><b>Mutational position of sup-tRNA:</b> {{ record['Mutational position of sup-tRNA'] }}</p>

              <p><b>PMID of references:</b>
                <span v-for="(pmid, index) in getPmidList(record['PMID of references'])" :key="index">
                  <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + pmid.trim()" target="_blank" class="tilt-hover">{{ pmid.trim() }}</a>
                  <span v-if="index < getPmidList(record['PMID of references']).length - 1">, </span>
                </span>
              </p>

              <p><b>Notes:</b> {{ record['Notes'] }}</p>
            </div>
          </template>
        </s-table>
      </s-table-provider>

      <vue-easy-lightbox
        :key="lightboxKey"
        :visible="visible"
        :imgs="lightboxImgs"
        :index="0"
        @hide="hideLightbox"
      />
    </div>

    <!-- 图表 -->
    <section class="chart-section-wrapper">
      <div class="chart-row">
                <div class="chart-col">
          <h3>① Species Distribution</h3>
          <VChart :option="speciesOption" autoresize style="height:400px;" />
        </div>
        <div class="chart-col">
          <h3>② Stop Codon Readthrough Distribution</h3>
          <VChart :option="stopCodonOption" autoresize style="height:300px;" />
        </div>
        <div class="chart-col">
          <h3>③ Distribution of Amino Acids charged on sup-tRNA</h3>
          <VChart :option="aaOption" autoresize style="height:300px;" />
        </div>
        <div class="chart-col">
          <h3>④ Tissue/Organelle of Origin</h3>
          <VChart :option="tissueOption" autoresize style="height:300px;" />
        </div>
        <div class="chart-col">
          <h3>⑤ Anticodon Mutation Heatmap</h3>
          <VChart :option="anticodonHeatmapOption" autoresize style="height:300px;" />
        </div>

      </div>
    </section>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useTableData } from '../../utils/useTableData';
import VueEasyLightbox from 'vue-easy-lightbox';
import { highlightMutation } from '../../utils/highlightMutation.js';
import { getTagType } from '../../utils/tag.js';
import type { EChartsOption } from 'echarts';
import 'echarts/lib/chart/bar';
import 'echarts/lib/chart/heatmap';
import { allColumns, selectedColumns } from './naturalSupTRNAColumns';
import TableToolbar from '@/components/TableToolbar.vue';

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'NaturalSupTRNA',
  components: { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption, VueEasyLightbox, TableToolbar },
  setup() {
    const TABLE_NAME = 'nonsense_sup_rna';
    const {
      rows,
      loading,
      searchText,
      searchColumn,
      searchValues,
      filters,
      tableSize,
      pagination,
      loadPage,
      handlePaginationUpdate,
      handleSorterChange,
      handleTableChange: handleTableChangeBase,
      watchSearch,
      fetchStats
    } = useTableData(TABLE_NAME);

    const stats = ref<Record<string, any[]>>({});

    // ✅ Lightbox refs — 之前缺这个才会报 visible 未定义
    const visible = ref(false);
    const lightboxImgs = ref<string[]>([]);
    const lightboxKey = ref(0);

    const showLightbox = (pictureid: string) => {
      const imgUrl = `https://minio.lumoxuan.cn/ensure/picture/${pictureid}.png`;
      lightboxImgs.value = [imgUrl];
      lightboxKey.value += 1;
      visible.value = true;
    };
    const hideLightbox = () => { visible.value = false; };

    const loadStats = async () => {
      try {
        const resp = await fetchStats({
          stats: [
            { type: 'value_counts', name: 'species_counts', column: 'Species' },
            {
              type: 'value_counts',
              name: 'stop_codon_counts',
              column: 'Stop codon for readthrough',
              split_regex: '[;,/]'
            },
            {
              type: 'value_counts',
              name: 'aa_counts',
              column: 'Noncanonical charged amino acids',
              split_regex: '[;,/]'
            },
            {
              type: 'value_counts',
              name: 'tissue_counts',
              column: 'Tissue/Organelle of Origin'
            },
            {
              type: 'matrix_counts',
              name: 'anticodon_heatmap',
              x_column: 'Anticodon after mutation',
              y_column: 'Anticodon before mutation'
            },
            {
              type: 'value_counts',
              name: 'mechanism_counts',
              column: 'Readthrough mechanism',
              split_regex: '[;]'
            }
          ],
          searchText: searchText.value,
          searchColumn: searchColumn.value,
          searchValues: searchValues.value,
          filters: filters.value,
          useFulltext: !searchColumn.value
        });
        stats.value = resp || {};
      } catch {
        stats.value = {};
      }
    };

    watchSearch(loadStats);
    watch(
      () => filters.value,
      () => {
        void loadStats();
      },
      { deep: true }
    );

    onMounted(async () => {
      await loadPage();
      await loadStats();
      selectedColumns.value = [...selectedColumns.value];
    });

    const rowKey = (r: any) => {
      if (r?.__rowid != null) return String(r.__rowid);
      const parts = [
        r?.['RNA central ID of tRNA'],
        r?.['ENSURE ID of tRNA'],
        r?.['Species ID'],
        r?.Species,
        r?.['Anticodon before mutation'],
        r?.['Anticodon after mutation'],
        r?.['PMID of references'],
        r?.pictureid,
        r?.['tRNA sequence before mutation'],
        r?.['tRNA sequence after mutation']
      ]
        .filter((v) => v != null && v !== '')
        .map(String);
      if (parts.length) return parts.join('|');
      return 'row';
    };

    // 工具函数
    const getPmidList = (pmidString: any) => String(pmidString).split('、');

    // 列选择
    const stopCodonFilters = computed(() => {
      const items = (stats.value?.stop_codon_counts || []) as Array<{
        name: string;
        value: number;
      }>;
      return items
        .filter((item) => item.name)
        .sort((a, b) => b.value - a.value)
        .map((item) => ({ text: `${item.name} (${item.value})`, value: item.name }));
    });

    const aaFilters = computed(() => {
      const items = (stats.value?.aa_counts || []) as Array<{ name: string; value: number }>;
      return items
        .filter((item) => item.name)
        .sort((a, b) => b.value - a.value)
        .map((item) => ({ text: `${item.name} (${item.value})`, value: item.name }));
    });

    const mechanismFilters = computed(() => {
      const items = (stats.value?.mechanism_counts || []) as Array<{
        name: string;
        value: number;
      }>;
      return items
        .filter((item) => item.name)
        .sort((a, b) => b.value - a.value)
        .map((item) => ({ text: `${item.name} (${item.value})`, value: item.name }));
    });

    const displayedColumns = computed(() =>
      allColumns
        .filter((column) => selectedColumns.value.includes(column.key as string))
        .map((column) => {
          if (column.key === 'Stop codon for readthrough') {
            const baseFilter = column.filter || { type: 'multiple' };
            return {
              ...column,
              filter: {
                ...baseFilter,
                list:
                  stopCodonFilters.value.length > 0
                    ? stopCodonFilters.value
                    : baseFilter.list
              }
            };
          }
          if (column.key === 'Noncanonical charged amino acids') {
            const baseFilter = column.filter || { type: 'multiple' };
            return {
              ...column,
              filter: {
                ...baseFilter,
                list: aaFilters.value.length > 0 ? aaFilters.value : baseFilter.list
              }
            };
          }
          if (column.key === 'Readthrough mechanism') {
            const baseFilter = column.filter || { type: 'multiple' };
            return {
              ...column,
              filter: {
                ...baseFilter,
                list:
                  mechanismFilters.value.length > 0
                    ? mechanismFilters.value
                    : baseFilter.list
              }
            };
          }
          return column;
        })
    );

    const normalizeFilterKey = (
      list: Array<{ column: string; values: string[]; mode?: string }>
    ) => {
      return list
        .map((item) => {
          const values = [...item.values].sort().join(',');
          return `${item.column}:${values}:${item.mode || 'contains'}`;
        })
        .sort()
        .join('|');
    };

    const applyTableFilters = (tableFilters?: Record<string, any>) => {
      const nextFilters = Object.entries(tableFilters || {})
        .map(([column, raw]) => {
          const values = Array.isArray(raw) ? raw : raw ? [raw] : [];
          const cleaned = values.map((v) => String(v)).filter(Boolean);
          if (!cleaned.length) return null;
          return { column, values: cleaned, mode: 'contains' as const };
        })
        .filter(Boolean) as Array<{ column: string; values: string[]; mode: 'contains' }>;
      const prevKey = normalizeFilterKey(filters.value);
      const nextKey = normalizeFilterKey(nextFilters);
      if (prevKey !== nextKey) {
        filters.value = nextFilters;
        pagination.current = 1;
        return true;
      }
      return false;
    };

    const handleTableChange = (page?: any, tableFilters?: any, sorter?: any) => {
      const changed = applyTableFilters(tableFilters);
      handleTableChangeBase(changed ? undefined : page, tableFilters, sorter);
    };

    // 图表 —— 统计与热图
    const stopCodonOption = computed<EChartsOption>(() => {
      const items = (stats.value?.stop_codon_counts || []) as Array<{ name: string; value: number }>;
      const entries = items
        .filter((item) => item.name)
        .map((item) => [item.name, Number(item.value) || 0] as [string, number])
        .sort((a, b) => b[1] - a[1]);
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: entries.map(([k]) => k), axisLabel: { rotate: 0 } },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: entries.map(([, v]) => v), itemStyle: { borderRadius: 4 } }]
      };
    });

    const aaOption = computed<EChartsOption>(() => {
      const items = (stats.value?.aa_counts || []) as Array<{ name: string; value: number }>;
      const entries = items
        .filter((item) => item.name)
        .map((item) => [item.name, Number(item.value) || 0] as [string, number])
        .sort((a, b) => b[1] - a[1]);
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: entries.map(([k]) => k) },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: entries.map(([, v]) => v), itemStyle: { borderRadius: 4 } }]
      };
    });

    const tissueOption = computed<EChartsOption>(() => {
      const items = (stats.value?.tissue_counts || []) as Array<{ name: string; value: number }>;
      const entries = items
        .filter((item) => item.name)
        .map((item) => [item.name, Number(item.value) || 0] as [string, number])
        .sort((a, b) => b[1] - a[1]);
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: entries.map(([k]) => k) },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: entries.map(([, v]) => v), itemStyle: { borderRadius: 4 } }]
      };
    });

    const speciesOption = computed<EChartsOption>(() => {
      const items = (stats.value?.species_counts || []) as Array<{ name: string; value: number }>;
      const entries = items
        .filter((item) => item.name)
        .map((item) => [item.name, Number(item.value) || 0] as [string, number])
        .sort((a, b) => b[1] - a[1]);

      return {
        tooltip: { trigger: 'axis' },
        grid: {
          top: '10%',
          right: '10%',
          bottom: '50%',
          left: '10%'
        },
        xAxis: {
          type: 'category',
          data: entries.map(([k]) => k),
          axisLabel: {
            rotate: 45,
            interval: 0,
            fontSize: 12,
            fontStyle: 'italic'
          }
        },
        yAxis: { type: 'value' },
        series: [
          {
            type: 'bar',
            data: entries.map(([, v]) => v),
            itemStyle: { borderRadius: 4 }
          }
        ]
      };
    });

    const anticodonHeatmapOption = computed<EChartsOption>(() => {
      const items = (stats.value?.anticodon_heatmap || []) as Array<{
        x: string;
        y: string;
        count: number;
      }>;
      const beforeList = new Set<string>();
      const afterList = new Set<string>();
      const matrix: Record<string, Record<string, number>> = {};

      items.forEach((item) => {
        const b = item.y;
        const a = item.x;
        if (!b || !a) return;
        beforeList.add(b);
        afterList.add(a);
        matrix[b] = matrix[b] || {};
        matrix[b][a] = (matrix[b][a] || 0) + Number(item.count || 0);
      });

      const bs = Array.from(beforeList).sort();
      const as_ = Array.from(afterList).sort();

      const data: [number, number, number][] = [];
      bs.forEach((b, i) => as_.forEach((a, j) => data.push([j, i, matrix[b]?.[a] || 0])));
      const maxVal = data.length ? Math.max(...data.map((d) => d[2])) : 0;

      return {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const [x, y, v] = params.value as [number, number, number];
            return `Before: ${bs[y]}<br/>After: ${as_[x]}<br/>Count: ${v}`;
          }
        },
        xAxis: { type: 'category', data: as_, axisLabel: { rotate: 45 } },
        yAxis: { type: 'category', data: bs },
        visualMap: { min: 0, max: maxVal, calculable: true, orient: 'horizontal', left: 'center', bottom: '-2%' },
        series: [{ type: 'heatmap', data, emphasis: { itemStyle: { borderColor: '#000', borderWidth: 1 } } }]
      };
    });

    return {
      // 数据与列
      allColumns,
      displayedColumns,
      rows,

      // 控件
      tableSize,
      loading,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      getTagType,

      // 预览（Lightbox）
      visible,
      lightboxImgs,
      lightboxKey,
      showLightbox,
      hideLightbox,
      highlightMutation,

      // 分页（稳定）
      pagination,
      handlePaginationUpdate,
      handleSorterChange,
      handleTableChange,

      // 其它
      rowKey,
      getPmidList,

      // 图表
      stopCodonOption,
      aaOption,
      tissueOption,
      anticodonHeatmapOption,
      speciesOption
    };
  }
});
</script>

<style>
.s-table__filter-dropdown-content { overflow-y: auto; }

.site--main { padding: 20px; }

.custom-tag-styles .el-tag.el-tag--info {
  --el-tag-bg-color:#f5e1f8;
  --el-tag-border-color: var(--el-color-info-light-8);
  --el-tag-hover-color: var(--el-color-info);
  --el-tag-text-color:#ed8afc
}

.chart-section-wrapper { overflow-x: auto; padding: 10px 0; }
.chart-row { display: flex; flex-direction: column; gap: 20px; }
.chart-col { width: 100%; }
</style>
