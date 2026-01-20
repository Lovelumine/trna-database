<template>
  <div class="site--main">
    <h2>Coding Variation in Genetic Disorders</h2>

    <!-- 顶部行包含尺寸调整和搜索框 -->
    <TableToolbar
      v-model="searchText"
      v-model:column="searchColumn"
      v-model:size="tableSize"
      v-model:selected-columns="selectedColumns"
      :search-columns="allColumns"
      :display-columns="allColumns"
    />

    <!-- 表格组件 -->
    <s-table-provider :hover="true" :theme-color="'#00ACF5'" :locale="locale">
      <s-table
        :columns="columns"
        :data-source="rows"
        :row-key="rowKey"
        :stripe="true"
        :size="tableSize"
        :expand-row-by-click="true"
        v-model:expandedRowKeys="expandedRowKeys"
        :pagination="pagination"
        :loading="loading"
        @update:pagination="handlePaginationUpdate"
        @change="handleTableChange"
      >
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Mutation Type:</b> {{ record.mutationType }}</p>
            <p><b>Disease Name:</b> {{ record.diseaseName }}</p>
            <p><b>Phenotype MIM Number:</b> {{ record.Phenotype }}</p>
            <p><b>GenBank Accession Number:</b> {{ record['GenBank Accession Number'] }}</p>
            <p><b>Gene:</b> {{ record.gene }}</p>
            <p><b>Gene/Locus MIM Number:</b> {{ record.Locus }}</p>
            <p><b>Mutation Site:</b> {{ record.mutationSite }}</p>
            <p><b>Protein Alteration:</b> {{ record['Protein Alteration'] }}</p>
            <p><b>Codon Change:</b> {{ record['Codon Change'] }}</p>
            <p><b>Chromosome:</b> {{ record.chromosome }}</p>
            <p><b>Genome Position:</b> {{ record.Genomeposition }}</p>
            <p><b>De Novo / Inherited:</b> {{ record.denovoinherited }}</p>
            <p><b>Zygosity:</b> {{ record.zygosity }}</p>
            <p><b>Incidence Rate:</b> {{ record.incidenceRate }}</p>
            <p><b>Diagnostic Method:</b> {{ record.DiagnosticMethod }}</p>
            <p><b>References:</b> <a :href="record.References" target="_blank" class="tilt-hover">References</a></p>
            <p><b>Source:</b> <a :href="record.source" target="_blank" class="tilt-hover">Link</a></p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
  </div>

  <!-- 图表区最外层：允许横向滚动 -->
  <section class="chart-section-wrapper">
    <div class="chart-row">
      <div class="chart-col">
        <h3>① Inheritance Mode & Zygosity</h3>
        <VChart :option="stackedBarOption" autoresize style="height:350px;" />
      </div>

      <div class="chart-col">
        <h3>② Gene Frequency Treemap</h3>
        <VChart :option="treemapOption" autoresize style="height:400px; border:2px solid #ccc; padding:8px; border-radius:4px;" />
      </div>

      <div class="chart-col">
        <h3>③ Stop Codon Change Heatmap（Nonsense）</h3>
        <VChart :option="heatmapOption" autoresize style="height:450px;" />
      </div>

      <div class="chart-col">
        <h3>④ Stop Codon Change Heatmap（Missense）</h3>
        <VChart :option="heatmapOptionMissense" autoresize style="height:450px;" />
      </div>

      <div class="chart-col">
        <h3>⑤ Stop Codon Change Heatmap（Frameshift）</h3>
        <VChart :option="heatmapOptionFrameshift" autoresize style="height:450px;" />
      </div>
    </div>
  </section>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, onUnmounted, computed } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useTableData } from '../../utils/useTableData';
import type { EChartsOption } from 'echarts';
import { allColumns, selectedColumns } from './CodingVariation1Columns';
import TableToolbar from '@/components/TableToolbar.vue';

type DataType = { [key: string]: string };

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'CodingVariationDisease',
  components: { ElTag, ElSpace, ElSelect, ElOption, TableToolbar },
  setup() {
    const TABLE_NAME = 'coding_variation_genetic_disease';
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
      handleTableChange: handleTableChangeBase,
      watchSearch,
      fetchStats
    } = useTableData(TABLE_NAME);

    const stats = ref<Record<string, any[]>>({});
    const expandedRowKeys = ref<any[]>([]);
    const chartTextColor = ref('#e5e7eb');
    const chartMutedColor = ref('#cbd5f5');
    const chartSurfaceColor = ref('#111827');
    const chartBorderColor = ref('rgba(148, 163, 184, 0.35)');
    const chartIsDark = ref(false);

    const readCssVar = (name: string, fallback: string) => {
      if (typeof window === 'undefined') return fallback;
      const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
      return value || fallback;
    };

    const refreshChartColors = () => {
      const root = document.documentElement;
      chartTextColor.value = readCssVar('--app-text', '#e5e7eb');
      chartMutedColor.value = readCssVar('--app-text-muted', '#cbd5f5');
      chartSurfaceColor.value = readCssVar('--app-surface', '#111827');
      chartBorderColor.value = readCssVar('--app-border', 'rgba(148, 163, 184, 0.35)');
      chartIsDark.value =
        root.classList.contains('dark') ||
        root.getAttribute('data-theme') === 'dark' ||
        (root.getAttribute('data-theme') !== 'light' &&
          window.matchMedia('(prefers-color-scheme: dark)').matches);
    };

    const loadStats = async () => {
      try {
        const resp = await fetchStats({
          stats: [
            {
              type: 'matrix_counts',
              name: 'type_gene_matrix',
              x_column: 'gene',
              y_column: 'mutationType'
            },
            {
              type: 'matrix_counts',
              name: 'inherit_zygosity',
              x_column: 'denovoinherited',
              y_column: 'zygosity'
            },
            {
              type: 'codon_change_heatmap',
              name: 'nonsense_codon',
              column: 'Codon Change',
              exclude_mut_regex: 'TGT',
              filters: [{ column: 'mutationType', op: 'eq', value: 'nonsense' }]
            },
            {
              type: 'codon_change_heatmap',
              name: 'missense_codon',
              column: 'Codon Change',
              filters: [{ column: 'mutationType', op: 'eq', value: 'missense' }]
            },
            {
              type: 'codon_change_heatmap',
              name: 'frameshift_codon',
              column: 'Codon Change',
              filters: [{ column: 'mutationType', op: 'eq', value: 'frameshift' }]
            },
            {
              type: 'value_counts',
              name: 'mutation_type_counts',
              column: 'mutationType'
            }
          ],
          searchText: searchText.value,
          searchColumn: searchColumn.value,
          useFulltext: !searchColumn.value
        });
        stats.value = resp || {};
      } catch {
        stats.value = {};
      }
    };

    watchSearch(async () => {
      await loadStats();
      tryAutoExpand();
    });

    const applyMutationTypeFilter = (filters?: Record<string, any>) => {
      const raw = filters?.mutationType;
      const values = Array.isArray(raw) ? raw : raw ? [raw] : [];
      if (!values.length && searchColumn.value === 'mutationType') {
        const shouldClear = searchText.value !== '';
        if (shouldClear) {
          searchText.value = '';
          searchColumn.value = '';
          pagination.current = 1;
        }
        return shouldClear;
      }
      if (!values.length) return false;

      const next = String(values[0]);
      const changed =
        searchText.value !== next || searchColumn.value !== 'mutationType';
      if (changed) {
        searchText.value = next;
        searchColumn.value = 'mutationType';
        pagination.current = 1;
      }
      return changed;
    };

    const handleTableChange = (page?: any, filters?: any, sorter?: any) => {
      const filterChanged = applyMutationTypeFilter(filters);
      if (filterChanged) return;
      handleTableChangeBase(page, filters, sorter);
    };

    onMounted(async () => {
      await loadPage();
      await loadStats();
      selectedColumns.value = [...selectedColumns.value];
      tryAutoExpand();
    });

    let themeObserver: MutationObserver | null = null;
    let mediaQuery: MediaQueryList | null = null;
    const handleMediaChange = () => refreshChartColors();

    onMounted(() => {
      refreshChartColors();
      themeObserver = new MutationObserver(refreshChartColors);
      themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class', 'data-theme']
      });
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      if ('addEventListener' in mediaQuery) {
        mediaQuery.addEventListener('change', handleMediaChange);
      } else if ('addListener' in mediaQuery) {
        mediaQuery.addListener(handleMediaChange);
      }
    });

    onUnmounted(() => {
      if (themeObserver) themeObserver.disconnect();
      if (mediaQuery) {
        if ('removeEventListener' in mediaQuery) {
          mediaQuery.removeEventListener('change', handleMediaChange);
        } else if ('removeListener' in mediaQuery) {
          mediaQuery.removeListener(handleMediaChange);
        }
      }
    });

    // 稳定 rowKey（不要依赖 index）
    const rowKey = (r: any) =>
      r?.id ??
      r?.key ??
      `${r?.gene ?? ''}-${r?.mutationSite ?? ''}-${r?.['Protein Alteration'] ?? ''}-${r?.Genomeposition ?? ''}`;

    const shouldAutoExpand = () => {
      if (typeof window === 'undefined') return false;
      const params = new URLSearchParams(window.location.search);
      const tableParam = params.get('table');
      if (tableParam && tableParam !== TABLE_NAME) return false;
      return params.get('expand') === '1';
    };

    const tryAutoExpand = () => {
      if (!shouldAutoExpand() || expandedRowKeys.value.length) return;
      if (!searchColumn.value || searchText.value === '') return;
      const target = rows.value.find(
        (row: any) => String(row?.[searchColumn.value]) === String(searchText.value)
      );
      if (target) {
        expandedRowKeys.value = [rowKey(target)];
      }
    };

    const mutationTypeFilters = computed(() => {
      const items = (stats.value?.mutation_type_counts || []) as Array<{
        name: string;
        value: number;
      }>;
      return items
        .slice()
        .sort((a, b) => b.value - a.value)
        .map((item) => ({
          text: `${item.name} (${item.value})`,
          value: item.name
        }));
    });

    const displayedColumns = computed(() =>
      allColumns
        .filter((column) => selectedColumns.value.includes(column.key as string))
        .map((column) => {
          if (column.key !== 'mutationType') return column;
          const baseFilter = column.filter || { type: 'multiple' };
          return {
            ...column,
            filter: {
              ...baseFilter,
              list: mutationTypeFilters.value
            }
          };
        })
    );

    const buildCodonHeatmap = (
      items: Array<{ orig: string; mut: string; count: number }>
    ): EChartsOption => {
      const originalStops = new Set<string>();
      const mutatedStops = new Set<string>();
      const combo: Record<string, Record<string, number>> = {};

      items.forEach((item) => {
        const orig = item.orig;
        const mut = item.mut;
        if (!orig || !mut) return;
        originalStops.add(orig);
        mutatedStops.add(mut);
        combo[orig] = combo[orig] || {};
        combo[orig][mut] = (combo[orig][mut] || 0) + Number(item.count || 0);
      });

      const yList = Array.from(originalStops).sort();
      const xList = Array.from(mutatedStops).sort();
      const heatData: [number, number, number][] = [];
      yList.forEach((o, i) => xList.forEach((m, j) => heatData.push([j, i, combo[o]?.[m] || 0])));
      const maxCount = heatData.length ? Math.max(...heatData.map((d) => d[2])) : 0;
      const textColor = chartTextColor.value;
      const mutedColor = chartMutedColor.value;

      return {
        title: {
          text: 'Stop Codon Changes Frequency Heatmap',
          left: 'center',
          textStyle: { color: textColor }
        },
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const [xIdx, yIdx, v] = params.value as number[];
            return [
              `Original Codon: ${yList[yIdx]}`,
              `Mutated Codon: ${xList[xIdx]}`,
              `Count: ${v}`
            ].join('<br/>');
          }
        },
        xAxis: {
          type: 'category',
          data: xList,
          name: 'Mutated Codon',
          axisLabel: { rotate: 45, interval: 0, color: textColor },
          nameTextStyle: { color: textColor },
          axisLine: { lineStyle: { color: mutedColor } },
          axisTick: { lineStyle: { color: mutedColor } }
        },
        yAxis: {
          type: 'category',
          data: yList,
          name: 'Original Codon',
          axisLabel: { color: textColor },
          nameTextStyle: { color: textColor },
          axisLine: { lineStyle: { color: mutedColor } },
          axisTick: { lineStyle: { color: mutedColor } }
        },
        visualMap: {
          min: 0,
          max: maxCount,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '-1%',
          textStyle: { color: textColor }
        },
        series: [{ type: 'heatmap', data: heatData, label: { show: false } }]
      };
    };

    // —— 1. Treemap（按 mutationType -> gene）
    const treemapOption = computed<EChartsOption>(() => {
      const items = (stats.value?.type_gene_matrix || []) as Array<{
        x: string;
        y: string;
        count: number;
      }>;
      const nested: Record<string, Record<string, number>> = {};
      items.forEach((item) => {
        const type = item.y || 'Unknown';
        const gene = item.x || 'Unknown';
        nested[type] = nested[type] || {};
        nested[type][gene] = (nested[type][gene] || 0) + Number(item.count || 0);
      });

      const data = Object.entries(nested).map(([type, geneCounts]) => {
        const sorted = Object.entries(geneCounts).sort((a, b) => b[1] - a[1]);
        const top10 = sorted.slice(0, 10);
        const others = sorted.slice(10).reduce((s, [, c]) => s + c, 0);
        const children = top10.map(([gene, cnt]) => ({ name: gene, value: cnt }));
        if (others) children.push({ name: 'Others', value: others });
        return { name: type, children };
      });

      const textColor = chartTextColor.value;
      const treemapBorderColor = chartBorderColor.value;
      const treemapColors = chartIsDark.value
        ? ['#6aa7ff', '#7fe3a2', '#f8d07a']
        : ['#3a6ee8', '#4dbb6b', '#e8b44a'];

      return {
        tooltip: { trigger: 'item', formatter: (info: any) => `${info.name}: ${info.value}` },
        color: treemapColors,
        series: [
          {
            type: 'treemap',
            data,
            leafDepth: 2,
            upperLabel: {
              show: true,
              height: 30,
              formatter: (info: any) => (info.treePathInfo.length === 2 ? `${info.name}: ${info.value}` : ''),
              textStyle: { fontSize: 14, fontWeight: 'bold', color: textColor }
            },
            label: {
              show: true,
              formatter: (info: any) => `${info.name}: ${info.value}`,
              position: 'inside',
              color: textColor
            },
            breadcrumb: { show: true, left: 'center', top: '5px', textStyle: { color: textColor } },
            levels: [
              {
                itemStyle: {
                  borderColor: treemapBorderColor,
                  borderWidth: 1,
                  gapWidth: 2
                }
              },
              {
                itemStyle: {
                  borderColor: treemapBorderColor,
                  borderWidth: 1,
                  gapWidth: 1
                }
              }
            ]
          }
        ]
      };
    });

    // —— 2. 堆叠柱图（Inheritance Mode & Zygosity）
    const stackedBarOption = computed<EChartsOption>(() => {
      const modeTotals: Record<string, number> = {};
      const zygoTotals: Record<string, number> = {};
      const counter: Record<string, Record<string, number>> = {};

      const items = (stats.value?.inherit_zygosity || []) as Array<{
        x: string;
        y: string;
        count: number;
      }>;
      items.forEach((item) => {
        const mode = item.x || 'Unknown';
        const zygo = item.y || 'Unknown';
        counter[mode] = counter[mode] || {};
        counter[mode][zygo] = (counter[mode][zygo] || 0) + Number(item.count || 0);
        modeTotals[mode] = (modeTotals[mode] || 0) + Number(item.count || 0);
        zygoTotals[zygo] = (zygoTotals[zygo] || 0) + Number(item.count || 0);
      });

      const modeList = Object.entries(modeTotals)
        .sort((a, b) => b[1] - a[1])
        .map(([mode]) => mode);

      const zygoList = Object.entries(zygoTotals)
        .sort((a, b) => b[1] - a[1])
        .map(([zygo]) => zygo);

      const textColor = chartTextColor.value;
      const mutedColor = chartMutedColor.value;

      return {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: zygoList, top: 30, textStyle: { color: textColor } },
        grid: { top: 60, bottom: 40, left: 80, right: 20, containLabel: true },
        xAxis: {
          type: 'category',
          data: modeList,
          axisLabel: { rotate: 30, color: textColor },
          axisLine: { lineStyle: { color: mutedColor } },
          axisTick: { lineStyle: { color: mutedColor } }
        },
        yAxis: {
          type: 'value',
          axisLabel: { color: textColor },
          axisLine: { lineStyle: { color: mutedColor } },
          splitLine: { lineStyle: { color: mutedColor, opacity: 0.25 } }
        },
        series: zygoList.map((zygo) => ({
          name: zygo,
          type: 'bar',
          stack: 'total',
          data: modeList.map((mode) => counter[mode]?.[zygo] || 0),
          emphasis: { itemStyle: { borderColor: '#333', borderWidth: 1 } },
          itemStyle: { borderRadius: 4 }
        }))
      };
    });

    // —— 3. Heatmap（Nonsense）
    const heatmapOption = computed<EChartsOption>(() => {
      const items = (stats.value?.nonsense_codon || []) as Array<{
        orig: string;
        mut: string;
        count: number;
      }>;
      return buildCodonHeatmap(items);
    });

    // —— 4. Heatmap（Frameshift）
    const heatmapOptionFrameshift = computed<EChartsOption>(() => {
      const items = (stats.value?.frameshift_codon || []) as Array<{
        orig: string;
        mut: string;
        count: number;
      }>;
      return buildCodonHeatmap(items);
    });

    // —— 5. Heatmap（Missense）
    const heatmapOptionMissense = computed<EChartsOption>(() => {
      const items = (stats.value?.missense_codon || []) as Array<{
        orig: string;
        mut: string;
        count: number;
      }>;
      return buildCodonHeatmap(items);
    });

    return {
      columns: displayedColumns,
      rows,
      tableSize,
      loading,
      searchText,
      locale,
      selectedColumns,
      searchColumn,
      displayedColumns,
      allColumns, // 列选择控件
      treemapOption,
      stackedBarOption,
      heatmapOption,
      heatmapOptionMissense,
      heatmapOptionFrameshift,
      // 分页
      pagination,
      handlePaginationUpdate,
      handleSorterChange,
      handleTableChange,
      rowKey,
      expandedRowKeys
    };
  }
});
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.chart-section-wrapper {
  /* 横向滚动的外层不用改 */
  overflow-x: auto;
  padding: 10px 0;
}

.chart-section-wrapper h3 {
  color: var(--app-text);
}

/* 把原来的横向 flex 换成纵向 flex */
.chart-row {
  display: flex;
  flex-direction: column;  /* 改成纵向堆叠 */
  gap: 20px;               /* 每行间距 */
}

/* 每个图表占满整行 */
.chart-col {
  width: 100%;             /* 撑满父容器宽度 */
  /* 删除或注释掉原来的 flex 相关设置：
     flex: 0 0 auto;
     width: 1000px;
  */
}
/* 在你的全局或组件 <style> 中添加 */
.help-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  border-radius: 50%;
  background-color: #1976d2;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  margin-left: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.help-icon:hover {
  background-color: #005bb5;
}
</style>
