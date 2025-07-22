<template>
  <div class="site--main">
    <h2>Coding Variation in Genetic Disease</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
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
        :columns="columns"
        :data-source="filteredDataSource"
        :row-key="record => record.key"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
      >
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Mutation Type:</b> {{ record.mutationType }}</p>
            <p><b>Disease Name:</b> {{ record.diseaseName }}</p>
            <p><b>Phenotype MIM Number:</b> {{ record.Phenotype }}</p>
            <p><b>GenBank Accession Number:</b> {{ record['GenBank Accession Number']}}</p>
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
        <VChart :option="treemapOption" autoresize style="height:400px;border:2px solid #ccc; padding:8px; border-radius:4px;" />
      </div>

      <div class="chart-col">
        <h3>③ Stop Codon Change Heatmap（Nonsense）</h3>
        <VChart :option="heatmapOption" autoresize style="height:450px;" />
      </div>
    </div>
  </section>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed ,watch} from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption  } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import type { EChartsOption } from 'echarts';
import {pagination} from '../../utils/table'
import {allColumns,selectedColumns} from './CodingVariation1Columns'

// 定义数据类型
type DataType = { [key: string]: string };

  import en from '@shene/table/dist/locale/en'
  const locale = ref(en)

export default defineComponent({
  name: 'CodingVariationDisease',
  components: {
    ElTag,
    ElSpace,
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource, loadData ,searchColumn} = useTableData('https://minio.lumoxuan.cn/ensure/Coding Variation in Genetic Disease.csv');
    const tableSize = ref('default'); // 表格尺寸状态

    onMounted(async() => {
      await loadData();
      triggerColumnChange();
    });

    const triggerColumnChange = () => {
      // 模拟点击列选择控件以触发数据刷新
      selectedColumns.value = [...selectedColumns.value];
    };


    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );



    // —— 1. Treemap 配置
// —— 1. Treemap 配置（按 mutationType -> gene 层级） 
const treemapOption = computed<EChartsOption>(() => {
  // 构造 type → gene → count
  const nested: Record<string, Record<string, number>> = {};
  filteredDataSource.value.forEach((row: any) => {
    const type = row.mutationType || 'Unknown';
    const gene = row.gene         || 'Unknown';
    nested[type] = nested[type] || {};
    nested[type][gene] = (nested[type][gene] || 0) + 1;
  });

  // 转成两层数据
  const data = Object.entries(nested).map(([type, geneCounts]) => {
    const sorted = Object.entries(geneCounts).sort((a, b) => b[1] - a[1]);
    const top10  = sorted.slice(0, 10);
    const others = sorted.slice(10).reduce((s, [,c]) => s + c, 0);
    const children = top10.map(([gene, cnt]) => ({ name: gene, value: cnt }));
    if (others) children.push({ name: 'Others', value: others });
    return { name: type, children };
  });

  return {
    tooltip: {
      trigger: 'item',
      formatter: (info: any) => `${info.name}: ${info.value}`
    },
    series: [{
      type: 'treemap',
      data,
      leafDepth: 2,  // 展示到 gene 这一层
      // === 新增 upperLabel ===
      upperLabel: {
        show: true,
        height: 30,
          formatter: (info: any) => {
            const depth = info.treePathInfo.length;
            // depth===1 是 root，不显示
            // depth===2 才是 mutationType 层，显示 “Type: count”
            return depth === 2 ? `${info.name}: ${info.value}` : '';
          },
        textStyle: {
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
      label: {
        show: true,
        // gene 层也显示 name: value
        formatter: (info: any) => `${info.name}: ${info.value}`,
        position: 'inside'
      },
      breadcrumb: {
        show: true,
        left: 'center',
        top: '5px'
      }
    }]
  };
});
        
// —— 2. Stacked Bar 配置（按各模式总数降序；各合子类型按其总数降序）
    const stackedBarOption = computed<EChartsOption>(() => {
      // 收集所有模式和合子情况，以及计数
      const modeTotals: Record<string, number> = {};
      const zygoTotals: Record<string, number> = {};
      const counter: Record<string, Record<string, number>> = {};

      filteredDataSource.value.forEach((row: any) => {
        const mode = row.denovoinherited || 'Unknown';
        const zygo = row.zygosity || 'Unknown';

        // 初始化
        counter[mode] = counter[mode] || {};
        counter[mode][zygo] = (counter[mode][zygo] || 0) + 1;

        // 累加模式和合子总数
        modeTotals[mode] = (modeTotals[mode] || 0) + 1;
        zygoTotals[zygo] = (zygoTotals[zygo] || 0) + 1;
      });

      // 按总数降序排序模式列表
      const modeList = Object.entries(modeTotals)
        .sort((a, b) => b[1] - a[1])
        .map(([mode]) => mode);

      // 按总数降序排序合子类型列表
      const zygoList = Object.entries(zygoTotals)
        .sort((a, b) => b[1] - a[1])
        .map(([zygo]) => zygo);

      return {
        // title: { text: 'Inheritance Mode & Zygosity (sorted)', left: 'center' },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: {
          data: zygoList,
          top: 30
        },
        grid: {
          top: 60,
          bottom: 40,
          left: 80,
          right: 20,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: modeList,
          axisLabel: { rotate: 30 }
        },
        yAxis: {
          type: 'value'
        },
        series: zygoList.map(zygo => ({
          name: zygo,
          type: 'bar',
          stack: 'total',
          data: modeList.map(mode => counter[mode]?.[zygo] || 0),
          emphasis: {
            itemStyle: { borderColor: '#333', borderWidth: 1 }
          },
          itemStyle: { borderRadius: 4 }
        }))
      };
    });

    // —— 3. Heatmap 配置
    const heatmapOption = computed<EChartsOption>(() => {
          // 原始 stop vs 突变 stop 频次统计
          const combo: Record<string, Record<string, number>> = {}
          const originalStops = new Set<string>()
          const mutatedStops = new Set<string>()

          filteredDataSource.value
          .filter((row: any) => row.mutationType === 'Nonsense')
          .forEach((row: any) => {
            const codon = String(row['Codon Change'] || '').trim()
            // 解构时加默认值，防止 split 结果不完整
            const [orig = '', mut = ''] = codon.split('-')
            // 如果格式不对，跳过
            if (!orig || !mut) return

            originalStops.add(orig)
            mutatedStops.add(mut)

            combo[orig] = combo[orig] || {}
            combo[orig][mut] = (combo[orig][mut] || 0) + 1
          })

          // 对类别排序，保证可重复渲染时顺序一致
          const yList = Array.from(originalStops).sort()
          const xList = Array.from(mutatedStops).sort()

          // 构造 heatmap 数据 [xIndex, yIndex, value]
          const heatData: [number, number, number][] = []
          yList.forEach((o, i) => {
            xList.forEach((m, j) => {
              heatData.push([j, i, combo[o]?.[m] || 0])
            })
          })

          // 计算 visualMap 的最大值，避免空数组时报错
          const values = heatData.map(d => d[2])
          const maxCount = values.length > 0 ? Math.max(...values) : 0

          return {
            title: {
              text: 'Stop Codon Changes Frequency Heatmap',
              left: 'center',
            },
            tooltip: {
              trigger: 'item',
              formatter: params => {
                const [xIdx, yIdx, v] = params.value as number[]
                return [
                  `Original Stop: ${yList[yIdx]}`,
                  `Mutated Stop: ${xList[xIdx]}`,
                  `Count: ${v}`,
                ].join('<br/>')
              },
            },
            xAxis: {
              type: 'category',
              data: xList,
              name: 'Mutated Stop',
              axisLabel: {
                rotate: 45,
                interval: 0,
              },
            },
            yAxis: {
              type: 'category',
              data: yList,
              name: 'Original Stop',
            },
            visualMap: {
              min: 0,
              max: maxCount,
              calculable: true,
              orient: 'horizontal',
              left: 'center',
              bottom: '-1%',
            },
            series: [
              {
                type: 'heatmap',
                data: heatData,
                label: { show: false },
              },
            ],
          }
        })

    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      locale,
      selectedColumns,
      searchColumn,
      displayedColumns,
      allColumns, // 列选择控件
      triggerColumnChange,
      treemapOption,
      stackedBarOption,
      heatmapOption,
      pagination,
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
</style>
