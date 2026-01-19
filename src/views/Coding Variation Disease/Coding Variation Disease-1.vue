<template>
  <div class="site--main">
    <h2>Coding Variation in Genetic Disorders</h2>

    <!-- 顶部行包含尺寸调整和搜索框 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input" />
        <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
          <el-option :key="'all'" :label="'All columns'" :value="''" />
          <el-option v-for="column in allColumns" :key="column.key" :value="column.dataIndex" />
        </el-select>
      </div>

      <!-- 调整尺寸 -->
      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize">
          <el-radio-button value="small">Small Size</el-radio-button>
          <el-radio-button value="default">Default Size</el-radio-button>
          <el-radio-button value="large">Large Size</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 选择显示列 -->
      <div class="column-controls" style="margin-bottom: 10px">
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
            :label="typeof column.title === 'string' ? column.title : String(column.key)"
            :value="column.key"
          />
        </el-select>
      </div>
    </div>

    <!-- 表格组件 -->
    <s-table-provider :hover="true" :theme-color="'#00ACF5'" :locale="locale">
      <s-table
        :columns="columns"
        :data-source="rows"
        :row-key="rowKey"
        :stripe="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
        :loading="loading"
        @update:pagination="handlePaginationUpdate"
        @change="handleSorterChange"
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
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useServerTable } from '../../utils/useServerTable';
import type { EChartsOption } from 'echarts';
import { allColumns, selectedColumns } from './CodingVariation1Columns';

type DataType = { [key: string]: string };

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'CodingVariationDisease',
  components: { ElTag, ElSpace, ElSelect, ElOption },
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
      watchSearch,
      fetchStats
    } = useServerTable(TABLE_NAME);

    const stats = ref<Record<string, any[]>>({});

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

    watchSearch(loadStats);

    onMounted(async () => {
      await loadPage();
      await loadStats();
      selectedColumns.value = [...selectedColumns.value];
    });

    // 稳定 rowKey（不要依赖 index）
    const rowKey = (r: any) =>
      r?.key ??
      r?.id ??
      `${r?.gene ?? ''}-${r?.mutationSite ?? ''}-${r?.['Protein Alteration'] ?? ''}-${r?.Genomeposition ?? ''}`;

    const displayedColumns = computed(() =>
      allColumns.filter((column) => selectedColumns.value.includes(column.key as string))
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

      return {
        title: { text: 'Stop Codon Changes Frequency Heatmap', left: 'center' },
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
        xAxis: { type: 'category', data: xList, name: 'Mutated Codon', axisLabel: { rotate: 45, interval: 0 } },
        yAxis: { type: 'category', data: yList, name: 'Original Codon' },
        visualMap: { min: 0, max: maxCount, calculable: true, orient: 'horizontal', left: 'center', bottom: '-1%' },
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

      return {
        tooltip: { trigger: 'item', formatter: (info: any) => `${info.name}: ${info.value}` },
        series: [
          {
            type: 'treemap',
            data,
            leafDepth: 2,
            upperLabel: {
              show: true,
              height: 30,
              formatter: (info: any) => (info.treePathInfo.length === 2 ? `${info.name}: ${info.value}` : ''),
              textStyle: { fontSize: 14, fontWeight: 'bold' }
            },
            label: { show: true, formatter: (info: any) => `${info.name}: ${info.value}`, position: 'inside' },
            breadcrumb: { show: true, left: 'center', top: '5px' }
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

      return {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: zygoList, top: 30 },
        grid: { top: 60, bottom: 40, left: 80, right: 20, containLabel: true },
        xAxis: { type: 'category', data: modeList, axisLabel: { rotate: 30 } },
        yAxis: { type: 'value' },
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
      rowKey
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
.chart-section-wrapper {
  /* 横向滚动的外层不用改 */
  overflow-x: auto;
  padding: 10px 0;
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
