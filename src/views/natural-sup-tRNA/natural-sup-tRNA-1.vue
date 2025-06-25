<template>
  <div class="site--main">
    <h2>Nonsense Sup-RNA</h2>
    <!-- 顶部行包含尺寸调整、搜索框和列选择 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
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
        <el-select v-model="selectedColumns" multiple placeholder="Select columns to display" collapse-tags
          class="column-select">
          <el-option v-for="column in allColumns" :key="column.key" :label="column.title as string"
            :value="column.key" />
        </el-select>
      </div>
    </div>
    <!-- 表格组件 -->
    <div class="custom-tag-styles">
      <s-table-provider :hover="true" :locale="locale">
        <s-table :columns="displayedColumns" :data-source="filteredDataSource" :row-key="record => record.key"
          :stripe="true" :show-sorter-tooltip="true" :size="tableSize" :expand-row-by-click="true"
          @sorter-change="onSorterChange" :loading="loading" :pagination="pagination">
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
                  :key="items" :type="getTagType(items)">
                  {{ items }}
                </ElTag>
              </ElSpace>
            </template>
            <template v-else-if="column.key === 'Noncanonical charged amino acids'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids'] : record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))"
                  :key="items" :type="getTagType(items)">
                  {{ items }}
                </ElTag>
              </ElSpace>
            </template>
            <template v-else-if="column.key === 'Readthrough mechanism'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Readthrough mechanism']) ? record['Readthrough mechanism'] : record['Readthrough mechanism'].split(';').map(str => str.trim()))"
                  :key="items" :type="getTagType(items)">
                  {{ items }}
                </ElTag>
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
                    :key="items" :type="getTagType(items)">
                    {{ items }}
                  </ElTag>
                </ElSpace>
              </p>
              <p><b>Noncanonical charged amino acids:</b>
                <ElSpace>
                  <ElTag
                    v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids'] : record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))"
                    :key="items" :type="getTagType(items)">
                    {{ items }}
                  </ElTag>
                </ElSpace>
              </p>
              <p><b>RNA central ID of tRNA:</b> {{ record['RNA central ID of tRNA'] }}</p>
              <p><b>tRNA sequence before mutation:</b> {{ record['tRNA sequence before mutation'] }}</p>
              <p><b>tRNA sequence after mutation:</b> <span
                  v-html="highlightMutation(record['tRNA sequence after mutation'])"></span></p>

              <div>
                <b>Structure of sup-tRNA:</b>
                <img :src="`https://minio.lumoxuan.cn/ensure/picture/${record.pictureid}.png`"
                  @click="showLightbox(record.pictureid)" style="width: 100px; cursor: pointer;" />
              </div>
              <p><b>Readthrough mechanism:</b>
                <ElSpace>
                  <ElTag
                    v-for="items in (Array.isArray(record['Readthrough mechanism']) ? record['Readthrough mechanism'] : record['Readthrough mechanism'].split(';').map(str => str.trim()))"
                    :key="items" :type="getTagType(items)">
                    {{ items }}
                  </ElTag>
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
      <vue-easy-lightbox :key="lightboxKey" :visible="visible" :imgs="lightboxImgs" :index="0" @hide="hideLightbox" />
    </div>
    <section class="chart-section-wrapper">
      <div class="chart-row">
        <!-- 1. Stop Codon 分布 -->
        <div class="chart-col">
          <h3>① Stop Codon Readthrough Distribution</h3>
          <VChart
            :option="stopCodonOption"
            autoresize
            style="height:300px;"
          />
        </div>

        <!-- 2. Distribution of Amino Acids chared on sup-tRNA分布 -->
        <div class="chart-col">
          <h3>② Distribution of Amino Acids chared on sup-tRNA</h3>
          <VChart
            :option="aaOption"
            autoresize
            style="height:300px;"
          />
        </div>

        <!-- 3. Tissue/Organelle 分布 -->
        <div class="chart-col">
          <h3>③ Tissue/Organelle of Origin</h3>
          <VChart
            :option="tissueOption"
            autoresize
            style="height:300px;"
          />
        </div>

        <!-- 4. Anticodon 突变 Heatmap -->
        <div class="chart-col">
          <h3>④ Anticodon Mutation Heatmap</h3>
          <VChart
            :option="anticodonHeatmapOption"
            autoresize
            style="height:300px;"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed, nextTick } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider, STableProps } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import VueEasyLightbox from 'vue-easy-lightbox';
import { highlightMutation } from '../../utils/highlightMutation.js'
import { getTagType } from '../../utils/tag.js'
import { processCSVData } from '../../utils/processCSVData.js'
import { sortData } from '../../utils/sort.js';
import type { EChartsOption } from 'echarts';
import 'echarts/lib/chart/bar';
import 'echarts/lib/chart/heatmap';
import { allColumns, selectedColumns } from './naturalSupTRNAColumns';
import { pagination } from '../../utils/table'

type DataType = {
  [key: string]: string | string[];
  key: string;
  Species: string;
  'Anticodon before mutation': string;
  'Anticodon after mutation': string;
  'Stop codon for readthrough': string[];
  'Noncanonical charged amino acids': string[];
  'tRNA_sequence_before_mutation': string;
  'tRNA_sequence_after_mutation': string;
  'RNA central ID of tRNA': string;
  'Structure of sup-tRNA': string;
  'Readthrough mechanism': string;
  'Mutational position of sup-tRNA': string;
  'PMID': string;
  pictureid: string;
};

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'NaturalSupTRNA',
  components: {
    ElTooltip,
    ElImage,
    ElSelect,
    ElOption,
    VueEasyLightbox,
  },
  setup() {
    const { searchText, filteredDataSource: originalFilteredDataSource, searchColumn, loadData } = useTableData('https://minio.lumoxuan.cn/ensure/Nonsense Sup-RNA.csv', (data) => {
      return processCSVData(data, ['Stop codon for readthrough', 'Noncanonical charged amino acids', 'Readthrough mechanism']);
    });

    const tableSize = ref('default');
 const loading = ref(false);
    const dataSource = ref<DataType[]>([]);
    const sortedDataSource = ref<DataType[]>([]);

    onMounted(async () => {
      await loadData();
      dataSource.value = originalFilteredDataSource.value;
      sortedDataSource.value = originalFilteredDataSource.value;
    });

    const visible = ref(false);
    const lightboxImgs = ref<string[]>([]);
    const lightboxKey = ref(0);

    const showLightbox = (pictureid: string) => {
      const imgUrl = `https://minio.lumoxuan.cn/ensure/picture/${pictureid}.png`;
      lightboxImgs.value = [imgUrl];
      lightboxKey.value += 1;  // 更新key以重新渲染组件
      visible.value = true;
    };

    const hideLightbox = () => {
      visible.value = false;
    };


    const getPmidList = (pmidString) => {
      return String(pmidString).split('、');
    };

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );


    const onSorterChange = (params: any) => {
      let sorter: { field?: string, order?: 'ascend' | 'descend' } = {};
      if (Array.isArray(params)) {
        sorter = params[0];
      } else {
        sorter = params;
      }

      loading.value = true;
      const timer = setTimeout(() => {
        sortedDataSource.value = sortData(originalFilteredDataSource.value, sorter);
        loading.value = false;
        clearTimeout(timer);
      }, 300);
    };

    const filteredDataSource = computed(() => {
      if (!searchText.value) {
        return sortedDataSource.value;
      }
      return sortedDataSource.value.filter(record => {
        if (!searchColumn.value) {
          return Object.values(record).some(val => String(val).toLowerCase().includes(searchText.value.toLowerCase()));
        }
        return String(record[searchColumn.value]).toLowerCase().includes(searchText.value.toLowerCase());
      });
    });

    const secondaryStructures = ref<{ [key: string]: string }>({});

// —— 1. Stop Codon for Readthrough 分布（按频次从高到低排序）
const stopCodonOption = computed<EChartsOption>(() => {
  const counts: Record<string, number> = {};

  filteredDataSource.value.forEach((r: any) => {
    // 兜底转换：如果它本身是数组就用它，否则按分号/逗号/斜杠拆成数组
    const list = Array.isArray(r['Stop codon for readthrough'])
      ? r['Stop codon for readthrough']
      : String(r['Stop codon for readthrough'])
          .split(/[;,/]/)
          .map(s => s.trim())
          .filter(Boolean);

    list.forEach(code => {
      counts[code] = (counts[code] || 0) + 1;
    });
  });

  // 转为 [codon, count] 数组并按 count 倒序排序
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);

  // 拆分成 categories（codon）和 data（频次）
  const categories = entries.map(([codon]) => codon);
  const data = entries.map(([, cnt]) => cnt);

  return {
    // 如果需要标题，可以取消注释下一行
    // title: { text: 'Stop Codon Readthrough (sorted)', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { rotate: 0 }
    },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data,
        itemStyle: { borderRadius: 4 }
      }
    ]
  };
});

// —— 2. Noncanonical Amino Acids 分布
const aaOption = computed<EChartsOption>(() => {
  const counts: Record<string, number> = {};
  filteredDataSource.value.forEach((r: any) => {
    const list = Array.isArray(r['Noncanonical charged amino acids'])
      ? r['Noncanonical charged amino acids']
      : String(r['Noncanonical charged amino acids'])
          .split(/[;,/]/)
          .map(s => s.trim())
          .filter(Boolean);

    list.forEach(aa => {
      counts[aa] = (counts[aa] || 0) + 1;
    });
  });

  // 将 counts 转为 [name, value]，并按 value 倒序排序
  const entries = Object.entries(counts)
    .sort((a, b) => b[1] - a[1]);

  // 再拆分成 categories 和 data
  const categories = entries.map(e => e[0]);
  const data = entries.map(e => e[1]);

  return {
    // title: { text: 'Noncanonical Amino Acids (sorted)', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data,
      itemStyle: { borderRadius: 4 }
    }]
  };
});

// —— 3. Tissue/Organelle 分布（按频次从高到低排序）
const tissueOption = computed<EChartsOption>(() => {
  const counts: Record<string, number> = {};
  filteredDataSource.value.forEach((r: any) => {
    const org = r['Tissue/Organelle of Origin'] || 'Unknown';
    counts[org] = (counts[org] || 0) + 1;
  });

  // 转成 [org, count] 数组并按 count 倒序排序
  const entries = Object.entries(counts)
    .sort((a, b) => b[1] - a[1]);

  // 拆分成 categories 和 data
  const categories = entries.map(([org]) => org);
  const data = entries.map(([, count]) => count);

  return {
    // 如果需要标题，可以打开下面这一行
    // title: { text: 'Tissue/Organelle of Origin (sorted)', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data,
      itemStyle: { borderRadius: 4 }
    }]
  };
});
    // —— 4. Anticodon Before→After Heatmap
    const anticodonHeatmapOption = computed<EChartsOption>(() => {
  const beforeList = new Set<string>()
  const afterList  = new Set<string>()
  const matrix: Record<string, Record<string, number>> = {}

  filteredDataSource.value.forEach((r: any) => {
    const b = r['Anticodon before mutation']
    const a = r['Anticodon after mutation']
    if (!b || !a) return
    beforeList.add(b)
    afterList.add(a)
    matrix[b] = matrix[b] || {}
    matrix[b][a] = (matrix[b][a] || 0) + 1
  })

  const bs = Array.from(beforeList).sort()
  const as_ = Array.from(afterList).sort()
  if (!bs.length || !as_.length) {
    return {
      // title: { text: 'Anticodon Mutation Heatmap', left: 'center' },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'category', data: [] },
      series: [{ type: 'heatmap', data: [] }],
      visualMap: { min: 0, max: 0 },
    }
  }

  const data: [number, number, number][] = []
  bs.forEach((b, i) =>
    as_.forEach((a, j) =>
      data.push([j, i, matrix[b]?.[a] || 0])
    )
  )

  const maxVal = data.length ? Math.max(...data.map(d => d[2])) : 0

  return {
    // title: { text: 'Anticodon Mutation Heatmap', left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: params => {
        // params.value 就是 [xIndex, yIndex, count]
        const [x, y, v] = params.value as [number, number, number]
        return `Before: ${bs[y]}<br/>After: ${as_[x]}<br/>Count: ${v}`
      }
    },
    xAxis: { type: 'category', data: as_, axisLabel: { rotate: 45 } },
    yAxis: { type: 'category', data: bs },
    visualMap: {
      min: 0,
      max: maxVal,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '-2%'
    },
    series: [{
      type: 'heatmap',
      data,
      emphasis: { itemStyle: { borderColor: '#000', borderWidth: 1 } }
    }]
  }
})

    return {
      stopCodonOption,
      aaOption,
      tissueOption,
      anticodonHeatmapOption,
      allColumns,
      displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      highlightMutation,
      visible,
      lightboxKey,
      lightboxImgs,
      showLightbox,
      hideLightbox,
      getTagType, // 获取标签类型
      onSorterChange,
      loading,
      pagination,
      getPmidList
    };
  }
});
</script>

<style>

.s-table__filter-dropdown-content {
    overflow-y: auto;
}
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

.size-controls,
.column-controls {
  display: flex;
  align-items: center;
}

.column-select {
  margin-left: 10px;
  width: 200px;
}

  .custom-tag-styles .el-tag.el-tag--info {
    --el-tag-bg-color:#f5e1f8;
    --el-tag-border-color: var(--el-color-info-light-8);
    --el-tag-hover-color: var(--el-color-info);
    --el-tag-text-color:#ed8afc
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
