<template>
  <div class="site--main">
    <h2>Coding Variation in Cancers</h2>

    <!-- 顶部行 -->
    <div class="top-controls">
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

      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize">
          <el-radio-button value="small">Small Size</el-radio-button>
          <el-radio-button value="default">Default Size</el-radio-button>
          <el-radio-button value="large">Large Size</el-radio-button>
        </el-radio-group>
      </div>

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
        :pagination="paginationView"                
        @update:pagination="(p) => Object.assign(pagination, p)"  
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
import { defineComponent, ref, onMounted, computed, watch, toRaw } from 'vue';   // ✅ 引入 toRaw
import { ElTooltip, ElTag, ElSpace, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import { getTagType } from '../../utils/tag.js';
import type { EChartsOption } from 'echarts';
import { createPagination } from '../../utils/table';
import { allColumns, selectedColumns } from './CodingVariationCancerColumns';

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'CodingVariationDisease2',
  components: { ElTooltip, ElTag, ElSpace, ElSelect, ElOption },
  setup() {
    const { searchText, filteredDataSource, searchColumn, loadData } =
      useTableData('https://minio.lumoxuan.cn/ensure/Coding Variation in Cancer.csv', (data) =>
        data.map((item: any) => {
          if (typeof item.DISEASE === 'string') {
            item.DISEASE = item.DISEASE.split(';').map((s: string) => s.trim());
          }
          return item;
        })
      );

    const pagination = createPagination();
    const tableSize = ref<'small' | 'default' | 'large'>('default');

    onMounted(async () => {
      await loadData();
      selectedColumns.value = [...selectedColumns.value]; // 可留可删
    });

    // ✅ 关键：每次渲染给子组件一个“新引用”的分页对象
    const paginationView = computed(() => ({ ...toRaw(pagination) }));

    // 稳定 rowKey（不要用 index）
    const rowKey = (r: any) =>
      r?.GENOMIC_MUTATION_ID ?? r?.ENSEMBL_ID ?? `${r?.GENE_NAME ?? ''}-${r?.MUTATION_CDS ?? ''}`;

    // 外部筛选（搜索/列选择）时回到第 1 页
    watch([searchText, searchColumn, selectedColumns], () => {
      pagination.current = 1;
    });

    // 数据源长度变化时，同步 total，并把 current 夹紧到合法页
    watch(
      () => filteredDataSource.value.length,
      (len) => {
        pagination.total = len;
        const maxPage = Math.max(1, Math.ceil(len / pagination.pageSize));
        if (pagination.current > maxPage) pagination.current = maxPage;
      },
      { immediate: true }
    );

    // ✅ 额外：监听 pageSize，用户改每页条数时同步夹紧
    watch(
      () => pagination.pageSize,
      () => {
        const maxPage = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));
        if (pagination.current > maxPage) pagination.current = maxPage;
      }
    );

    // 表格内部变化：只维护 total 与越界夹紧（不要整体替换 pagination）
    const handleTableChange = () => {
      pagination.total = filteredDataSource.value.length;
      const maxPage = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));
      if (pagination.current > maxPage) pagination.current = maxPage;
    };

    const displayedColumns = computed(() =>
      allColumns.filter((c) => selectedColumns.value.includes(c.key as string))
    );

    // 1) Ref→Mut Heatmap
    const alleleHeatmapOption = computed<EChartsOption>(() => {
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

      const refList = Array.from(refSet).sort();
      const mutList = Array.from(mutSet).sort();

      const data: [number, number, number][] = [];
      refList.forEach((ref, i) => {
        mutList.forEach((mut, j) => data.push([j, i, combo[ref]?.[mut] || 0]));
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
      const counter: Record<string, number> = {};
      filteredDataSource.value.forEach((r: any) => {
        const arr = Array.isArray(r.DISEASE)
          ? r.DISEASE
          : String(r.DISEASE)
              .split(/[;/]/)
              .map((s) => s.trim())
              .filter(Boolean);
        arr.forEach((d: string) => (counter[d] = (counter[d] || 0) + 1));
      });
      const wordData = Object.entries(counter).map(([name, value]) => ({ name, value }));
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
      tableSize,
      searchText,
      locale,
      searchColumn,
      selectedColumns,
      allColumns,
      getTagType,
      // 分页
      pagination,
      paginationView,     // ✅ 暴露出去给模板用
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
.top-controls { display: flex; justify-content: space-between; align-items: center; }
.search-box { flex-grow: 1; margin-right: 10px; }
.size-controls, .column-controls { display: flex; align-items: center; }
.column-select { margin-left: 10px; width: 200px; }
.chart-section-wrapper { overflow-x: auto; padding: 10px 0; }
.chart-row { display: flex; flex-direction: column; gap: 20px; }
.chart-col { width: 100%; }
</style>