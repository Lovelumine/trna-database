<template>
  <div class="site--main">
    <h2>Coding Variation in Cancers</h2>
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
    <s-table-provider :hover="true" :locale="locale">
      <s-table
        :columns="displayedColumns"
        :data-source="filteredDataSource"
        :row-key="record => record.key"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
      >
        <template #bodyCell="{ text, column, record }">
          <template v-if="column.key === 'DISEASE'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
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
            <p><b>Legacy Mutation ID:</b><a :href="record.LEGACY_MUTATION_URL" target="_blank" class="tilt-hover">{{ record.LEGACY_MUTATION_ID }}</a></p>
            <p><b>Mutation Locus in GRCh37:</b> {{ record.MUTATION_LOCUS_IN_GRCh37 }}</p>
            <p><b>Mutation Locus in GRCh38:</b> {{ record.MUTATION_LOCUS_IN_GRCh38 }}</p>
            <p><b>Mutation Type:</b> {{ record.MUTATION_TYPE }}</p>
            <p><b>Mutation CDS:</b> {{ record.MUTATION_CDS }}</p>
            <p><b>MUTATION AA:</b> {{ record.MUTATION_AA }}</p>            
            <p><b>Genomic Ref Allele:</b> {{ record.GENOMIC_REF_ALLELE }}</p>
            <p><b>Genomic Mut Allele:</b> {{ record.GENOMIC_MUT_ALLELE }}</p>
            <p><b>Disease:</b>
              <ElSpace>
                <ElTag v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                  {{ items }}
                </ElTag>
              </ElSpace>
            </p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
    <section class="chart-section-wrapper">
    <div class="chart-row">
      <!-- 1. Ref→Mut Heatmap -->
      <div class="chart-col">
        <h3>④ Ref→Mut Allele Heatmap</h3>
        <VChart
          :option="alleleHeatmapOption"
          autoresize
          style="height:400px;"
        />
      </div>

      <!-- 2. Disease Word Cloud -->
      <div class="chart-col">
        <h3>⑤ Cancer Disease Word Cloud</h3>
        <VChart
          :option="diseaseWordcloudOption"
          autoresize
          style="height:400px;"
        />
      </div>
    </div>
  </section>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed,watch } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import {getTagType} from '../../utils/tag.js'
import type { EChartsOption } from 'echarts'
import {pagination} from '../../utils/table'
import {allColumns,selectedColumns} from './CodingVariationCancerColumns'

// 定义数据类型
type DataType = {
  [key: string]: string | string[];
  GENE_NAME: string;
  ENSEMBL_ID: string;
  MUTATION_URL: string;
  LEGACY_MUTATION_ID: string;
  GENOMIC_MUTATION_ID: string;
  MUTATION_LOCUS_IN_GRCh37: string;
  MUTATION_LOCUS_IN_GRCh38: string;
  MUTATION_TYPE: string;
  MUTATION_CDS: string;
  MUTATION_AA: string;
  GENOMIC_REF_ALLELE: string;
  GENOMIC_MUT_ALLELE: string;
  DISEASE: string[]; // 修改为数组类型
  tags: string[];
};

// 定义允许的标签类型
type TagType = 'success' | 'warning' | 'info' | 'primary' | 'danger';

import en from '@shene/table/dist/locale/en'
  const locale = ref(en)

export default defineComponent({
  name: 'CodingVariationDisease2',
  components: {
    ElTooltip,
    ElTag,
    ElSpace,
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource, searchColumn,loadData } = useTableData('https://minio.lumoxuan.cn/ensure/Coding Variation in Cancer.csv', (data) => {
      // 在加载数据时将 DISEASE 列转换为数组
      return data.map(item => {
        // 处理DISEASE字段
        if (typeof item.DISEASE === 'string') {
          item.DISEASE = item.DISEASE.split(';').map(str => str.trim());
        }
        return item;
      });
    });

    const tableSize = ref('default'); // 表格尺寸状态


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



    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    const alleleHeatmapOption = computed<EChartsOption>(() => {
  // 1. 构建 ref vs mut 计数矩阵
  const combo: Record<string, Record<string, number>> = {};
  const refSet = new Set<string>();
  const mutSet = new Set<string>();

  filteredDataSource.value.forEach((r: any) => {
    const ref = r.GENOMIC_REF_ALLELE || '';
    const mut = r.GENOMIC_MUT_ALLELE || '';
    if (!ref || !mut) return;

    refSet.add(ref);
    mutSet.add(mut);
    combo[ref] = combo[ref] || {};
    combo[ref][mut] = (combo[ref][mut] || 0) + 1;
  });

  // 2. 排序列与行
  const refList = Array.from(refSet).sort();
  const mutList = Array.from(mutSet).sort();

  // 3. 将矩阵展开为 heatmap 格式的 [x, y, value]
  const data: [number, number, number][] = [];
  refList.forEach((ref, i) => {
    mutList.forEach((mut, j) => {
      data.push([j, i, combo[ref]?.[mut] || 0]);
    });
  });

  // 4. 计算 visualMap 的最大值
  const allCounts = data.map(d => d[2]);
  const maxCount = allCounts.length > 0 ? Math.max(...allCounts) : 0;

  // 5. 返回 ECharts 配置
  return {
    tooltip: {
      position: 'top',
      // ←—— 这里修改：从 params.value 解构
      formatter: (params: any) => {
        const [x, y, v] = params.value as [number, number, number];
        return `Ref: ${refList[y]} → Mut: ${mutList[x]}<br/>Count: ${v}`;
      }
    },
    xAxis: {
      type: 'category',
      data: mutList,
      axisLabel: { rotate: 0 },
      name: 'Mutated Allele'
    },
    yAxis: {
      type: 'category',
      data: refList,
      name: 'Reference Allele'
    },
    visualMap: {
      min: 0,
      max: maxCount,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '-5%'
    },
    series: [
      {
        type: 'heatmap',
        data,
        emphasis: {
          itemStyle: { borderColor: '#333', borderWidth: 1 }
        }
      }
    ]
  };
});

    // —— 新增 2：Disease Word Cloud 配置
    const diseaseWordcloudOption = computed<EChartsOption>(() => {
      // 统计每个 disease 的出现次数
      const counter: Record<string, number> = {}
      filteredDataSource.value.forEach((r: any) => {
        const arr = Array.isArray(r.DISEASE) 
          ? r.DISEASE 
          : String(r.DISEASE)
      .split(/[;/]/)           // 同时以 ; 和 / 作为分隔符
      .map(str => str.trim())
      .filter(Boolean)         // 去掉空串
        arr.forEach(d => {
          if (!d) return
          counter[d] = (counter[d] || 0) + 1
        })
      })
      // 转成 ECharts 要求的格式
      const wordData = Object.entries(counter).map(([name, value]) => ({ name, value }))

      return {
        tooltip: { show: false },
        series: [{
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
            // 随机颜色
            color: () => {
              const r = Math.round(Math.random() * 160)
              const g = Math.round(Math.random() * 160)
              const b = Math.round(Math.random() * 160)
              return `rgb(${r},${g},${b})`
            }
          },
          data: wordData
        }]
      }
    })


    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      displayedColumns,
      locale,
      searchColumn,
      selectedColumns,
      allColumns, // 列选择控件
      getTagType, // 获取标签类型
      alleleHeatmapOption,
      diseaseWordcloudOption,
      pagination
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
