<template>
  <div class="site--main">
    <h2>Frameshift sup-tRNA</h2>

    <!-- 顶部行：搜索 / 尺寸 / 列选择 -->
    <div class="top-controls">
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input" />
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

      <div class="column-controls" style="margin-bottom: 10px">
        <el-select v-model="selectedColumns" multiple placeholder="Select columns to display" collapse-tags class="column-select">
          <el-option v-for="column in allColumns" :key="column.key" :label="column.title as string" :value="column.key" />
        </el-select>
      </div>
    </div>

    <!-- 表格 -->
    <div class="custom-tag-styles">
      <s-table-provider :hover="true" :locale="locale">
        <s-table
          :columns="displayedColumns"
          :data-source="filteredDataSource"
          :row-key="rowKey"
          :stripe="true"
          :show-sorter-tooltip="true"
          :size="tableSize"
          :expand-row-by-click="true"
          :loading="loading"
          :pagination="paginationView"
          @update:pagination="(p) => Object.assign(pagination, p)"
          @sorter-change="onSorterChange"
          @change="handleTableChange"
        >
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
                  :key="items"
                  :type="getTagType(items)"
                >
                  {{ items }}
                </ElTag>
              </ElSpace>
            </template>

            <template v-else-if="column.key === 'Noncanonical charged amino acids'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids'] : record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))"
                  :key="items"
                  :type="getTagType(items)"
                >
                  {{ items }}
                </ElTag>
              </ElSpace>
            </template>

            <template v-else-if="column.key === 'Readthrough mechanism'">
              <ElSpace>
                <ElTag
                  v-for="items in (Array.isArray(record['Readthrough mechanism']) ? record['Readthrough mechanism'] : record['Readthrough mechanism'].split(';').map(str => str.trim()))"
                  :key="items"
                  :type="getTagType(items)"
                >
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
                    :key="items"
                    :type="getTagType(items)"
                  >
                    {{ items }}
                  </ElTag>
                </ElSpace>
              </p>

              <p><b>Noncanonical charged amino acids:</b>
                <ElSpace>
                  <ElTag
                    v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids'] : record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))"
                    :key="items"
                    :type="getTagType(items)"
                  >
                    {{ items }}
                  </ElTag>
                </ElSpace>
              </p>

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
                  >
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

              <p v-if="record.Notes">
                <b>Notes:</b>
                <img
                  :src="`https://minio.lumoxuan.cn/ensure/picture/${record.Notes}.png`"
                  @click="showLightbox(record.Notes)"
                  style="width: 100px; cursor: pointer;"
                />
              </p>
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
          <VChart :option="speciesOption" autoresize style="height:300px;" />
        </div>

        <div class="chart-col">
          <h3>② Codon-for-Readthrough Distribution</h3>
          <VChart :option="codonOption" autoresize style="height:300px;" />
        </div>

        <div class="chart-col">
          <h3>③ Distribution of Amino Acids charged on sup-tRNA</h3>
          <VChart :option="aaOption" autoresize style="height:300px;" />
        </div>

        <div class="chart-col">
          <h3>④ Readthrough Mechanism Distribution</h3>
          <VChart :option="mechOption" autoresize style="height:300px;" />
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
import { defineComponent, ref, onMounted, computed, watch, toRaw } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import VueEasyLightbox from 'vue-easy-lightbox';
import { highlightMutation } from '../../utils/highlightMutation.js';
import { getTagType } from '../../utils/tag.js';
import { processCSVData } from '../../utils/processCSVData.js';
import { allColumns, selectedColumns } from './Frameshiftcolumns';
import { sortData } from '../../utils/sort.js';
import { createPagination } from '../../utils/table';
import type { EChartsOption } from 'echarts';
import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'NaturalSupTRNA',
  components: { ElTooltip, ElImage, ElSelect, ElOption, VueEasyLightbox },
  setup() {
    const { searchText, filteredDataSource: originalFilteredDataSource, searchColumn, loadData } =
      useTableData(
        'https://minio.lumoxuan.cn/ensure/Frameshift sup-tRNA.csv',
        (data) => processCSVData(data, ['Codon for readthrough', 'Noncanonical charged amino acids', 'Readthrough mechanism'])
      );

    const tableSize = ref<'small' | 'default' | 'large'>('default');
    const loading = ref(false);
    const sortedDataSource = ref<any[]>([]);

    // Lightbox
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

    // 分页：稳定引用
    const pagination = createPagination();
    const paginationView = computed(() => ({ ...toRaw(pagination) }));

    onMounted(async () => {
      await loadData();
      sortedDataSource.value = originalFilteredDataSource.value;
      // 触发一次列刷新（可选）
      selectedColumns.value = [...selectedColumns.value];
    });

    // 排序
    const onSorterChange = (params: any) => {
      let sorter: { field?: string; order?: 'ascend' | 'descend' } = Array.isArray(params) ? params[0] : params;
      loading.value = true;
      const timer = setTimeout(() => {
        sortedDataSource.value = sortData(originalFilteredDataSource.value, sorter);
        loading.value = false;
        clearTimeout(timer);
      }, 300);
    };

    // 搜索（基于排序后的数据）
    const filteredDataSource = computed(() => {
      const q = String(searchText.value ?? '').toLowerCase();
      if (!q) return sortedDataSource.value;

      if (!searchColumn.value) {
        return sortedDataSource.value.filter((record: any) =>
          Object.values(record).some((val) => String(val).toLowerCase().includes(q))
        );
      }
      return sortedDataSource.value.filter((record: any) =>
        String(record[searchColumn.value]).toLowerCase().includes(q)
      );
    });

    // 外部筛选时回到第 1 页
    watch([searchText, searchColumn, selectedColumns], () => {
      pagination.current = 1;
    });

    // 同步 total & 夹紧页码
    watch(
      () => filteredDataSource.value.length,
      (len) => {
        pagination.total = len;
        const maxPage = Math.max(1, Math.ceil(len / pagination.pageSize));
        if (pagination.current > maxPage) pagination.current = maxPage;
      },
      { immediate: true }
    );

    // pageSize 变化时夹紧
    watch(
      () => pagination.pageSize,
      () => {
        const maxPage = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));
        if (pagination.current > maxPage) pagination.current = maxPage;
      }
    );

    // 表格内部变化：只回写 current/pageSize，total 固定取外部过滤后的全集
    const handleTableChange = (page?: any) => {
      if (page?.current != null) pagination.current = page.current;
      if (page?.pageSize != null) pagination.pageSize = page.pageSize;
      pagination.total = filteredDataSource.value.length;
      const maxPage = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));
      if (pagination.current > maxPage) pagination.current = maxPage;
    };

    // 稳定的 rowKey（避免 index）
    const rowKey = (r: any, idx: number) =>
      r?.key ??
      r?.['PMID'] ??
      `${r?.Species ?? ''}-${r?.['Anticodon after mutation'] ?? ''}-${idx}`;

    // 列选择
    const displayedColumns = computed(() =>
      allColumns.filter((column) => selectedColumns.value.includes(column.key as string))
    );

    // 统计图表
    const speciesOption = computed<EChartsOption>(() => {
      const counts: Record<string, number> = {};
      filteredDataSource.value.forEach((r: any) => {
        const sp = r.Species || 'Unknown';
        counts[sp] = (counts[sp] || 0) + 1;
      });
      const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: entries.map(([sp]) => sp) ,      axisLabel: {
        fontStyle: 'italic',
      },},
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: entries.map(([, c]) => c), itemStyle: { borderRadius: 4 } }]
      };
    });

    const codonOption = computed<EChartsOption>(() => {
      const counts: Record<string, number> = {};
      filteredDataSource.value.forEach((r: any) => {
        const list = Array.isArray(r['Codon for readthrough'])
          ? r['Codon for readthrough']
          : String(r['Codon for readthrough']).split(';').map((s) => s.trim()).filter(Boolean);
        list.forEach((c) => (counts[c] = (counts[c] || 0) + 1));
      });
      const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: entries.map(([k]) => k), axisLabel: { rotate: 45 } },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: entries.map(([, v]) => v), itemStyle: { borderRadius: 4 } }]
      };
    });

    const aaOption = computed<EChartsOption>(() => {
      const counts: Record<string, number> = {};
      filteredDataSource.value.forEach((r: any) => {
        const list = Array.isArray(r['Noncanonical charged amino acids'])
          ? r['Noncanonical charged amino acids']
          : String(r['Noncanonical charged amino acids']).split(/[;,/]/).map((s) => s.trim()).filter(Boolean);
        list.forEach((aa) => (counts[aa] = (counts[aa] || 0) + 1));
      });
      const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: entries.map(([k]) => k), axisLabel: { rotate: 45 } },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: entries.map(([, v]) => v), itemStyle: { borderRadius: 4 } }]
      };
    });

    const mechOption = computed<EChartsOption>(() => {
      const counts: Record<string, number> = {};
      filteredDataSource.value.forEach((r: any) => {
        const list = Array.isArray(r['Readthrough mechanism'])
          ? r['Readthrough mechanism']
          : String(r['Readthrough mechanism']).split(/[;,/]/).map((s) => s.trim()).filter(Boolean);
        list.forEach((m) => (counts[m] = (counts[m] || 0) + 1));
      });
      const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
      return {
        tooltip: { trigger: 'axis' },
        grid: { top: 50, bottom: 10, left: 80, right: 20, containLabel: true },
        xAxis: { type: 'category', data: entries.map(([k]) => k), axisLabel: { rotate: 30 } },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: entries.map(([, v]) => v), itemStyle: { borderRadius: 4 } }]
      };
    });

    const anticodonHeatmapOption = computed<EChartsOption>(() => {
      const beforeSet = new Set<string>();
      const afterSet = new Set<string>();
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
        visualMap: { min: 0, max: maxVal, calculable: true, orient: 'horizontal', left: 'center', bottom: '-5%' },
        series: [{ type: 'heatmap', data }]
      };
    });

    const getPmidList = (pmidString: any) => String(pmidString).split('、');

    return {
      // 数据 & 列
      allColumns,
      displayedColumns,
      filteredDataSource,

      // 控件
      tableSize,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      getTagType,

      // Lightbox
      visible,
      lightboxImgs,
      lightboxKey,
      showLightbox,
      hideLightbox,
      highlightMutation,

      // 排序/加载
      onSorterChange,
      loading,

      // 分页
      pagination,
      paginationView,
      handleTableChange,
      rowKey,

      // 工具
      getPmidList,

      // 图表
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
.site--main { padding: 20px; }

.top-controls { display: flex; justify-content: space-between; align-items: center; }
.search-box { flex-grow: 1; margin-right: 10px; }
.size-controls, .column-controls { display: flex; align-items: center; }
.column-select { margin-left: 10px; width: 200px; }

.chart-section-wrapper { overflow-x: auto; padding: 10px 0; }
.chart-row { display: flex; flex-direction: column; gap: 20px; }
.chart-col { width: 100%; }
</style>