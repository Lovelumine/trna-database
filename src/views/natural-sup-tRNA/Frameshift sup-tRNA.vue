<template>
  <div class="site--main">
    <h2>Frameshift sup-tRNA</h2>
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
          @sorter-change="onSorterChange" :loading="loading">
          <template #bodyCell="{ text, column, record }">
            <template v-if="column.key === 'Species'">
    <em>{{ text }}</em>
  </template>
            <template v-else-if="column.key === 'Structure of sup-tRNA'">
              <el-image style="width: 100px; height: 100px" :src="text" :preview-src-list="[text]" fit="cover" />
            </template>
            <template v-else-if="column.key === 'Codon for readthrough'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Codon for readthrough']) ? record['Codon for readthrough'] : record['Codon for readthrough'].split(';').map(str => str.trim()))"
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
              <p><b>Codon for readthrough:</b>
                <ElSpace>
                  <ElTag
                    v-for="items in (Array.isArray(record['Codon for readthrough']) ? record['Codon for readthrough'] : record['Codon for readthrough'].split(';').map(str => str.trim()))"
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
        <!-- 1. Species Distribution -->
        <div class="chart-col">
          <h3>① Species Distribution</h3>
          <VChart :option="speciesOption" autoresize style="height:300px; width: 800px;" />
        </div>

        <!-- 2. Codon for Readthrough -->
        <div class="chart-col">
          <h3>② Codon-for-Readthrough Distribution</h3>
          <VChart :option="codonOption" autoresize style="height:300px;width: 600px;" />
        </div>

        <!-- 3. Noncanonical Amino Acids -->
        <div class="chart-col">
          <h3>③ Noncanonical Charged Amino Acids</h3>
          <VChart :option="aaOption" autoresize style="height:300px;" />
        </div>

        <!-- 4. Readthrough Mechanism -->
        <div class="chart-col">
          <h3>④ Readthrough Mechanism Distribution</h3>
          <VChart :option="mechOption" autoresize style="height:300px;width: 400px;" />
        </div>

        <!-- 5. Anticodon Mutation Heatmap -->
        <div class="chart-col">
          <h3>⑤ Anticodon Mutation Heatmap</h3>
          <VChart :option="anticodonHeatmapOption" autoresize style="height:300px;width: 400px;" />
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import VueEasyLightbox from 'vue-easy-lightbox';
import { highlightMutation } from '../../utils/highlightMutation.js'
import { getTagType } from '../../utils/tag.js'
import { processCSVData } from '../../utils/processCSVData.js'
import { sortData } from '../../utils/sort.js';

type DataType = {
  [key: string]: string | string[];
  key: string;
  Species: string;
  'Anticodon before mutation': string;
  'Anticodon after mutation': string;
  'Codon for readthrough': string[];
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

import type { EChartsOption } from 'echarts';


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
    const { searchText, filteredDataSource: originalFilteredDataSource, searchColumn, loadData } = useTableData('https://minio.lumoxuan.cn/ensure/Frameshift sup-tRNA.csv', (data) => {
      return processCSVData(data, ['Codon for readthrough', 'Noncanonical charged amino acids', 'Readthrough mechanism']);
    });

    const tableSize = ref('default');
    const selectedColumns = ref<string[]>(['Species', 'Codon for readthrough', 'Anticodon after mutation', 'Codon for readthrough', 'Noncanonical charged amino acids', 'Readthrough mechanism']);
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

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Species', dataIndex: 'Species', width: 240, ellipsis: true, key: 'Species', resizable: true, sorter: true },
      { title: 'Species ID', dataIndex: 'Species ID', width: 280, ellipsis: true, key: 'Species ID', resizable: true, sorter: true },
      { title: 'Anticodon before mutation', dataIndex: 'Anticodon before mutation', width: 180, ellipsis: true, key: 'Anticodon before mutation', resizable: true },
      { title: 'Anticodon after mutation', dataIndex: 'Anticodon after mutation', width: 180, ellipsis: true, key: 'Anticodon after mutation', resizable: true },
      {
        title: 'Codon for readthrough', dataIndex: 'Codon for readthrough', width: 240, ellipsis: true, key: 'Codon for readthrough', resizable: true
      },
      {
        title: 'Noncanonical charged amino acids', dataIndex: 'Noncanonical charged amino acids', width: 260, ellipsis: true, key: 'Noncanonical charged amino acids', resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'Val', value: 'Val' },
            { text: 'Gln', value: 'Gln' },
            { text: 'Lys', value: 'Lys' },
            { text: 'Pro', value: 'Pro' },
            { text: 'Gly', value: 'Gly' },
            { text: 'Thr', value: 'Thr' },
          ],
          onFilter: (value, record) => value.includes(record['Noncanonical charged amino acids']) || record['Noncanonical charged amino acids'].includes(value)
        }
      },
      { title: 'tRNA sequence before mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      { title: 'tRNA sequence after mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      {
        title: 'Readthrough mechanism', dataIndex: 'Readthrough mechanism', width: 280, ellipsis: true, key: 'Readthrough mechanism', resizable: true, filter: {
          type: 'multiple',
          list: [
            { text: 'mutations in the anticodon', value: 'mutations in the anticodon' },
            { text: 'tRNA hopping', value: 'tRNA hopping' },
            { text: 'quadruple pairing', value: 'quadruple pairing' },
            { text: 'mutations outside the anticodon', value: 'mutations outside the anticodon' },
          ],
    onFilter: (value, record) => {
      const mechanism = record['Readthrough mechanism'];
      return value.some(val => mechanism.includes(val));
    }}
      },
      { title: 'Mutational position of sup-tRNA', dataIndex: 'Mutational position of sup-tRNA', width: 250, ellipsis: true, key: 'Mutational position of sup-tRNA', resizable: true },
      { title: 'PMID of references', 
  dataIndex: 'PMID of references', 
  key: 'PMID of references', 
  resizable: true,
  width: 250, 
  align: 'center',
  ellipsis: true, 
  customRender: ({ text, record }) => {
    const reference = String(record['PMID of references']); // 确保 Reference 是字符串类型
    return (
        <div>
            {reference.split('、').map((pmid, index, array) => (
                <span key={pmid.trim()}>
                    <a href={`https://pubmed.ncbi.nlm.nih.gov/${pmid.trim()}`} target="_blank" class="bracket-links">{pmid.trim()}</a>
                    {index < array.length - 1 && '、'}
                </span>
            ))}
        </div>
    );
}}
];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    const getPmidList = (pmidString) => {
      return String(pmidString).split('、');
    };

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
    

    // 1. Species Distribution
const speciesOption = computed<EChartsOption>(() => {
  const counts: Record<string, number> = {};
  filteredDataSource.value.forEach((r: any) => {
    const sp = r.Species || 'Unknown';
    counts[sp] = (counts[sp] || 0) + 1;
  });
  const cats = Object.keys(counts);
  return {
    title: { text: 'Species Distribution', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: cats },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: cats.map(c => counts[c]) }],
    itemStyle: { borderRadius: 4 }
  };
});

// 2. Codon-for-Readthrough Distribution
const codonOption = computed<EChartsOption>(() => {
  const counts: Record<string, number> = {};
  filteredDataSource.value.forEach((r: any) => {
    const list = Array.isArray(r['Codon for readthrough'])
      ? r['Codon for readthrough']
      : String(r['Codon for readthrough'])
          .split(';')
          .map(s => s.trim())
          .filter(Boolean);
    list.forEach(cod => counts[cod] = (counts[cod] || 0) + 1);
  });
  const cats = Object.keys(counts);
  return {
    title: { text: 'Codon-for-Readthrough', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: cats , axisLabel: { rotate: 45 } },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: cats.map(c => counts[c]) }],
    itemStyle: { borderRadius: 4 }
  };
});

// 3. Noncanonical Charged Amino Acids
const aaOption = computed<EChartsOption>(() => {
  const counts: Record<string, number> = {};
  filteredDataSource.value.forEach((r: any) => {
    const list = Array.isArray(r['Noncanonical charged amino acids'])
      ? r['Noncanonical charged amino acids']
      : String(r['Noncanonical charged amino acids'])
          .split(';')
          .map(s => s.trim())
          .filter(Boolean);
    list.forEach(aa => counts[aa] = (counts[aa] || 0) + 1);
  });
  const cats = Object.keys(counts);
  return {
    title: { text: 'Noncanonical Charged Amino Acids', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: cats },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: cats.map(c => counts[c]) }],
    itemStyle: { borderRadius: 4 }
  };
});

// 4. Readthrough Mechanism Distribution
const mechOption = computed<EChartsOption>(() => {
  const counts: Record<string, number> = {};
  filteredDataSource.value.forEach((r: any) => {
    const list = Array.isArray(r['Readthrough mechanism'])
      ? r['Readthrough mechanism']
      : String(r['Readthrough mechanism'])
          .split(';')
          .map(s => s.trim())
          .filter(Boolean);
    list.forEach(m => counts[m] = (counts[m] || 0) + 1);
  });
  const cats = Object.keys(counts);
  return {
    title: { text: 'Readthrough Mechanism', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: {
      top: 50,
      bottom: 10,      // ← 给底部留出足够空间
      left: 80,
      right: 20,
      containLabel: true
    },
    xAxis: { type: 'category', data: cats , axisLabel: { rotate: 30 } ,margin: 50},
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: cats.map(c => counts[c]) }],
    itemStyle: { borderRadius: 4 }
  };
});

// 5. Anticodon Mutation Heatmap
const anticodonHeatmapOption = computed<EChartsOption>(() => {
  const beforeSet = new Set<string>();
  const afterSet  = new Set<string>();
  const matrix: Record<string, Record<string, number>> = {};
  filteredDataSource.value.forEach((r: any) => {
    const b = r['Anticodon before mutation'];
    const a = r['Anticodon after mutation'];
    if (!b || !a) return;
    beforeSet.add(b);
    afterSet.add(a);
    matrix[b] = matrix[b] || {};
    matrix[b][a] = (matrix[b][a] || 0) + 1;
  });
  const bs = Array.from(beforeSet).sort();
  const as_ = Array.from(afterSet).sort();
  // 构造 [xIdx, yIdx, count]
  const data: [number,number,number][] = [];
  bs.forEach((b, i) =>
    as_.forEach((a, j) =>
      data.push([j, i, matrix[b]?.[a] || 0])
    )
  );
  const maxVal = data.length ? Math.max(...data.map(d=>d[2])) : 0;
  return {
    title: { text: 'Anticodon Mutation Heatmap', left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: params => {
        const [x,y,v] = params.value as [number,number,number];
        return `Before: ${bs[y]}<br/>After: ${as_[x]}<br/>Count: ${v}`;
      }
    },
    xAxis: { type: 'category', data: as_, axisLabel: { rotate: 45 } },
    yAxis: { type: 'category', data: bs },
    visualMap: { min: 0, max: maxVal, calculable: true, orient: 'horizontal', left: 'center', bottom: '5%' },
    series: [{ type: 'heatmap', data }]
  };
});

    return {
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
      getPmidList, // 添加getPmidList方法
      loading,
      speciesOption,
  codonOption,
  aaOption,
  mechOption,
  anticodonHeatmapOption
    };
  }
});
</script>

<style>
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

.chart-section-wrapper {
  overflow-x: auto;
  margin-top: 20px;
}
.chart-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 20px;
}
.chart-col {
  flex: 0 0 auto;
  width: auto;
}
</style>
