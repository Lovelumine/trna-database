<!-- src/views/tRNAtherapeutics/tRNAtherapeutics.vue -->
<template>
  <div class="site--main">
    <h2>Engineered Sup-tRNA</h2>

    <!-- PMID选择表格 -->
    <div class="table-section">
      <s-table-provider :hover="true" :theme-color="'#00ACF5'" :locale="locale">
  <s-table
    :columns="pmidColumns"
    :data-source="paginatedPmidData"
    :row-key="record => record.PMID"
    :expand-row-by-click="true"
    @change="handleTableChange"
  >
    <template #expandedRowRender="{ record }">
      <!-- ✅ 根据PMID动态加载tRNAtherapeutics1组件 -->
      <tRNAtherapeutics1 :selectedPmids="[record.PMID]" />
    </template>

    <!-- 正常单元格渲染 -->
    <template #default="{ text, column, record }">
      <span v-if="column.dataIndex === 'PMID'">
        <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID" target="_blank">{{ text }}</a>
      </span>
      <span v-else>{{ text }}</span>
    </template>
  </s-table>
</s-table-provider>
    </div>

    <!-- 根据选择PMID展示的表格 -->
    <!-- <div class="table-section">
      <tRNAtherapeutics1 :selectedPmids="selectedPmids" />
    </div> -->
    <section style="margin: 24px 0">
      <h3>Per-Position Alignment Variation</h3>
      <VChart
        :option="perPositionOption"
        autoresize
        style="height: 400px;"
      />
    </section>
  </div>

</template>

<script lang="tsx">
import { ref, computed, onMounted } from 'vue';
import { STableProvider } from '@shene/table';
import Papa from 'papaparse';
import tRNAtherapeutics1 from './tRNAtherapeutics-1.vue';
import { useTableData } from '../../assets/js/useTableData.js';
import en from '@shene/table/dist/locale/en';
const locale = ref(en);

import type { EChartsOption, ECElementEvent } from 'echarts';

interface AlignmentItem {
    id: string;
    base: string;
    sup_base: string;
  }

export default {
  name: 'tRNAtherapeutics',
  components: {
    tRNAtherapeutics1,
    STableProvider
  },
  setup() {

  const { searchText, filteredDataSource, searchColumn, loadData } = useTableData('https://minio.lumoxuan.cn/ensure/tRNAtherapeutics.csv');

  const getType = (item: AlignmentItem): 'match'|'mismatch'|'insertion'|'deletion' => {
      return item.base === '-' && item.sup_base !== '-' ? 'insertion'
           : item.base !== '-' && item.sup_base === '-' ? 'deletion'
           : item.base === item.sup_base               ? 'match'
           : 'mismatch';
    };
      // —— 1. Overall 统计
      const alignmentCounts = computed(() => {
      const cnt = { match:0, mismatch:0, insertion:0, deletion:0 };
      filteredDataSource.value.forEach((rec: any) => {
        let arr: AlignmentItem[] = [];
        try { arr = JSON.parse(String(rec.js_sup_tRNA)); } catch { return; }
        arr.forEach(item => { cnt[getType(item)]++; });
      });
      return cnt;
    });

    const alignmentOption = computed<EChartsOption>(() => {
      const cats = ['match','mismatch','insertion','deletion'];
      const data = cats.map(c => alignmentCounts.value[c]);
      return {
        title: { text: 'Alignment Variation', left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: cats, axisLabel: { rotate: 45 } },
        yAxis: { type: 'value' },
        series: [
          {
            type: 'bar',
            data,
            itemStyle: { borderRadius: 8 }
          }
        ]
      };
    });

    // —— 2. 点击 mismatch 展示明细
    const mismatchDetails = ref<{from:string,to:string,count:number}[]>([]);
    const onChartClick = (params: ECElementEvent) => {
      if (params.name !== 'mismatch') {
        mismatchDetails.value = [];
        return;
      }
      const pairCnt: Record<string,Record<string,number>> = {};
      filteredDataSource.value.forEach((rec: any) => {
        let arr: AlignmentItem[] = [];
        try { arr = JSON.parse(String(rec.js_sup_tRNA)); } catch { return; }
        arr.forEach(item => {
          if (getType(item) === 'mismatch') {
            pairCnt[item.base] = pairCnt[item.base] || {};
            pairCnt[item.base][item.sup_base] = (pairCnt[item.base][item.sup_base]||0)+1;
          }
        });
      });
      const details: typeof mismatchDetails.value = [];
      for (const from in pairCnt)
        for (const to in pairCnt[from])
          details.push({ from, to, count: pairCnt[from][to] });
      mismatchDetails.value = details;
    };

    // —— 3. Per-position 统计
    const perPositionCounts = computed(() => {
      const M: Record<string,Record<'match'|'mismatch'|'insertion'|'deletion',number>> = {};
      filteredDataSource.value.forEach((rec: any) => {
        let arr: AlignmentItem[] = [];
        try { arr = JSON.parse(String(rec.js_sup_tRNA)); } catch { return; }
        arr.forEach(item => {
          const pos = item.id;
          if (!M[pos]) M[pos] = { match:0, mismatch:0, insertion:0, deletion:0 };
          M[pos][ getType(item) ]++;
        });
      });
      return M;
    });

      const perPositionOption = computed(() => {
    // 1. 按数字排序所有位置
    const positions = Object.keys(perPositionCounts.value)
      .sort((a, b) => Number(a) - Number(b));

    // 2. 构造每一种类型的堆积柱状系列
    const types = ['match','mismatch','insertion','deletion'] as const;
    const mutableTypes = [...types]; // now a mutable string[]
    const series = mutableTypes.map(type => ({
      name: type,
      type: 'bar' as const,
      stack: 'all' as const,
      data: positions.map(p => perPositionCounts.value[p][type]),
      itemStyle: { borderRadius: 4 }
    }));

    // 3. Build & cast the option
    const option = {
      title:    { text: 'Per-Position Alignment Variation', left: 'center' },
      tooltip:  { trigger: 'axis' },
      legend:   { data: mutableTypes, top: 30 },
      xAxis:    { type: 'category', data: positions, name: 'position', axisLabel: { rotate: 45 } },
      yAxis:    { type: 'value', name: 'count' },
      series
    };
    return option as EChartsOption;
  });

    // PMID表格配置
    const pmidColumns = ref([
      {
        title: 'PMID',
        dataIndex: 'PMID',
        key: 'PMID',
        width: 40,
      },
      {
        title: 'Title',
        dataIndex: 'Title',
        key: 'Title',
        width: 300,
        ellipsis: true
      },
      {
        title: 'Source',
        dataIndex: 'Source',
        key: 'Source',
        width: 150,
        filters: [
          { text: 'Nature', value: 'Nature' },
          { text: 'Science', value: 'Science' },
          { text: 'Cell', value: 'Cell' }
        ],
        onFilter: (value, record) => record.Source.includes(value)
      },
      {
        title: 'Author',
        dataIndex: 'Author',
        key: 'Author',
        width: 200,
        ellipsis: true
      },
      {
        title: 'PubDate',
        dataIndex: 'PubDate',
        key: 'PubDate',
        width: 120,
      }
    ]);

    // 数据状态
    const rawPmidData = ref([]);
    const selectedPmids = ref([]);
    const pagination = ref({
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true
    });

    // 分页数据
    const paginatedPmidData = computed(() => {
      const start = (pagination.value.current - 1) * pagination.value.pageSize;
      const end = start + pagination.value.pageSize;
      return rawPmidData.value.slice(start, end);
    });

    // 多选配置
    const rowSelection = ref({
      selectedRowKeys: selectedPmids,
      onChange: (selectedKeys) => {
        selectedPmids.value = selectedKeys;
      },
      preserveSelectedRowKeys: true
    });

    // 加载CSV数据
    onMounted(async () => {
      
      const response = await fetch('https://minio.lumoxuan.cn/ensure/pmid_article_info_extended.csv');
      await loadData()
      const csvText = await response.text();

      Papa.parse(csvText, {
        complete: (result) => {
          rawPmidData.value = result.data.slice(1).map(row => ({
            PubDate: formatDate(row[0]),
            Source: row[1],
            Author: formatAuthors(row[2]),
            Title: row[3],
            PMID: String(row[4])
          }));
          pagination.value.total = rawPmidData.value.length;
        },
        skipEmptyLines: true,
        header: false
      });
    });

    // 表格变化处理
    const handleTableChange = (pag, filters, sorter) => {
      if (pag) {
        pagination.value = { ...pagination.value, ...pag };
      }
    };

    // 辅助方法
    const formatDate = (dateStr) => {
      // 实现日期格式化逻辑
      return new Date(dateStr).toLocaleDateString();
    };

    const formatAuthors = (authorsStr) => {
      // 实现作者格式化逻辑
      return authorsStr.split(',').slice(0, 3).join(', ') + ' et al.';
    };

    return {
      locale,
      pmidColumns,
      paginatedPmidData,
      pagination,
      rowSelection,
      selectedPmids,
      handleTableChange,
      alignmentOption,
      onChartClick,
      mismatchDetails,
      perPositionOption
    };
  }
};
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.table-section {
  margin-bottom: 30px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
}

:deep(.s-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.s-table-header) {
  background: #fafafa;
}

:deep(.s-table-row:hover) {
  background: #f5f7fa !important;
}
</style>