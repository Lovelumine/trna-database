<!-- src/views/tRNAtherapeutics/tRNAtherapeutics.vue -->
<template>
  <div class="site--main">
    <!-- 1. 当 loading 为 true 时，显示骨架屏占位 -->
    <div v-if="loading" class="skeleton-wrapper">
      <!-- 表格骨架：5 行占位 -->
      <el-skeleton
        :rows="5"
        animated
        style="margin-bottom: 24px; border-radius: 8px;"
      />
      <!-- 图表骨架：矩形占位 -->
      <el-skeleton
        variant="rect"
        animated
        style="height: 400px; border-radius: 8px;"
      />
    </div>

    <!-- 2. 数据加载完成后，展示真实内容 -->
    <div v-else>
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
                <a
                  :href="'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID"
                  target="_blank"
                  >{{ text }}</a
                >
              </span>
              <span v-else>{{ text }}</span>
            </template>
          </s-table>
        </s-table-provider>
      </div>

      <section style="margin: 24px 0">
        <h3>Per-Position Alignment Variation</h3>
        <VChart :option="perPositionOption" autoresize style="height: 400px;" />
      </section>
    </div>
  </div>
</template>

<script lang="tsx">
import { ref, computed, onMounted } from 'vue';
import { STableProvider } from '@shene/table';
import Papa from 'papaparse';
import tRNAtherapeutics1 from './tRNAtherapeutics-1.vue';
import { useTableData } from '../../assets/js/useTableData.js';
import en from '@shene/table/dist/locale/en';
import type { EChartsOption, ECElementEvent } from 'echarts';
import { ElSkeleton } from 'element-plus';

const locale = ref(en);

interface AlignmentItem {
  id: string;
  base: string;
  sup_base: string;
}

export default {
  name: 'tRNAtherapeutics',
  components: {
    tRNAtherapeutics1,
    STableProvider,
    ElSkeleton,
  },
  setup() {
    // 1. 使用 useTableData 加载 tRNAtherapeutics.csv，只在首次挂载时触发
    const { searchText, filteredDataSource, searchColumn, loadData } =
      useTableData('https://minio.lumoxuan.cn/ensure/tRNAtherapeutics.csv');

    // 2. 加载 PMID 表格 CSV 所需状态
    const rawPmidData = ref<any[]>([]);
    const selectedPmids = ref<string[]>([]);
    const pagination = ref({
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true,
    });

    // 3. 用来控制页面总体的 loading 状态
    const loading = ref(true);

    // 4. 计算分页后的 PMID 数据
    const paginatedPmidData = computed(() => {
      const start = (pagination.value.current - 1) * pagination.value.pageSize;
      const end = start + pagination.value.pageSize;
      return rawPmidData.value.slice(start, end);
    });

    // 5. 定义列配置
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
        ellipsis: true,
      },
      {
        title: 'Source',
        dataIndex: 'Source',
        key: 'Source',
        width: 150,
        filters: [
          { text: 'Nature', value: 'Nature' },
          { text: 'Science', value: 'Science' },
          { text: 'Cell', value: 'Cell' },
        ],
        onFilter: (value: string, record: any) => record.Source.includes(value),
      },
      {
        title: 'Author',
        dataIndex: 'Author',
        key: 'Author',
        width: 200,
        ellipsis: true,
      },
      {
        title: 'PubDate',
        dataIndex: 'PubDate',
        key: 'PubDate',
        width: 120,
      },
    ]);

    // 6. 过滤 tRNA 数据时，先尝试解析 js_sup_tRNA 字段
    const getType = (
      item: AlignmentItem
    ): 'match' | 'mismatch' | 'insertion' | 'deletion' => {
      return item.base === '-' && item.sup_base !== '-'
        ? 'insertion'
        : item.base !== '-' && item.sup_base === '-'
        ? 'deletion'
        : item.base === item.sup_base
        ? 'match'
        : 'mismatch';
    };

    // 7. 计算每种类型的总数
    const alignmentCounts = computed(() => {
      const cnt = { match: 0, mismatch: 0, insertion: 0, deletion: 0 };
      filteredDataSource.value.forEach((rec: any) => {
        let arr: AlignmentItem[] = [];
        try {
          arr = JSON.parse(String(rec.js_sup_tRNA));
        } catch {
          return;
        }
        arr.forEach((item) => {
          cnt[getType(item)]++;
        });
      });
      return cnt;
    });

    // 8. 点击 mismatch 时展示明细（可扩展，目前暂不需要使用）
    const mismatchDetails = ref<
      { from: string; to: string; count: number }[]
    >([]);
    const onChartClick = (params: ECElementEvent) => {
      if (params.name !== 'mismatch') {
        mismatchDetails.value = [];
        return;
      }
      const pairCnt: Record<string, Record<string, number>> = {};
      filteredDataSource.value.forEach((rec: any) => {
        let arr: AlignmentItem[] = [];
        try {
          arr = JSON.parse(String(rec.js_sup_tRNA));
        } catch {
          return;
        }
        arr.forEach((item) => {
          if (getType(item) === 'mismatch') {
            pairCnt[item.base] = pairCnt[item.base] || {};
            pairCnt[item.base][item.sup_base] =
              (pairCnt[item.base][item.sup_base] || 0) + 1;
          }
        });
      });
      const details: typeof mismatchDetails.value = [];
      for (const from in pairCnt)
        for (const to in pairCnt[from])
          details.push({ from, to, count: pairCnt[from][to] });
      mismatchDetails.value = details;
    };

    // 9. 计算每个位点的各类型堆积柱状数据
    const perPositionCounts = computed(() => {
      const M: Record<
        string,
        Record<'match' | 'mismatch' | 'insertion' | 'deletion', number>
      > = {};
      filteredDataSource.value.forEach((rec: any) => {
        let arr: AlignmentItem[] = [];
        try {
          arr = JSON.parse(String(rec.js_sup_tRNA));
        } catch {
          return;
        }
        arr.forEach((item) => {
          const pos = item.id;
          if (!M[pos]) M[pos] = { match: 0, mismatch: 0, insertion: 0, deletion: 0 };
          M[pos][getType(item)]++;
        });
      });
      return M;
    });

    const perPositionOption = computed<EChartsOption>(() => {
      // 按数字排序所有位置
      const positions = Object.keys(perPositionCounts.value).sort(
        (a, b) => Number(a) - Number(b)
      );
      // 构造堆积柱状系列
      const types = ['match', 'mismatch', 'insertion', 'deletion'] as const;
      const series = types.map((type) => ({
        name: type,
        type: 'bar' as const,
        stack: 'all' as const,
        data: positions.map((p) => perPositionCounts.value[p][type]),
        itemStyle: { borderRadius: 4 },
      }));
      return {
        tooltip: { trigger: 'axis' },
        legend: { data: [...types], top: 30 },
        xAxis: {
          type: 'category',
          data: positions,
          name: 'position',
          axisLabel: { rotate: 45 },
        },
        yAxis: { type: 'value', name: 'count' },
        series,
      } as EChartsOption;
    });

    // 10. 表格分页变化处理
    const handleTableChange = (pag: any) => {
      if (pag) {
        pagination.value = { ...pagination.value, ...pag };
      }
    };

    // 11. 辅助方法：日期格式化 和 作者格式化
    const formatDate = (dateStr: string) => {
      return new Date(dateStr).toLocaleDateString();
    };
    const formatAuthors = (authorsStr: string) => {
      return authorsStr.split(',').slice(0, 3).join(', ') + ' et al.';
    };

    // 12. 页面挂载时，依次加载两份 CSV：tRNAtherapeutics.csv 和 pmid_article_info_extended.csv
    onMounted(async () => {
      loading.value = true;

      // 12.1 加载 tRNAtherapeutics.csv
      await loadData();

      // 12.2 加载 PMID 表格的 CSV
      try {
        const response = await fetch(
          'https://minio.lumoxuan.cn/ensure/pmid_article_info_extended.csv'
        );
        const csvText = await response.text();
        Papa.parse(csvText, {
          complete: (result) => {
            rawPmidData.value = result.data.slice(1).map((row: any[]) => ({
              PubDate: formatDate(row[0]),
              Source: row[1],
              Author: formatAuthors(row[2]),
              Title: row[3],
              PMID: String(row[4]),
            }));
            pagination.value.total = rawPmidData.value.length;
          },
          skipEmptyLines: true,
          header: false,
        });
      } catch (e) {
        console.error('Failed to load PMID CSV:', e);
      } finally {
        // 两份 CSV 数据都加载完毕后，关掉 loading
        loading.value = false;
      }
    });

    return {
      locale,
      pmidColumns,
      paginatedPmidData,
      pagination,
      handleTableChange,
      alignmentCounts,
      alignmentOption: computed(() => ({
        title: {
          text: 'Alignment Variation',
          left: 'center',
        },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: ['match', 'mismatch', 'insertion', 'deletion'],
          axisLabel: { rotate: 45 },
        },
        yAxis: { type: 'value' },
        series: [
          {
            type: 'bar',
            data: ['match', 'mismatch', 'insertion', 'deletion'].map(
              (c) => alignmentCounts.value[c]
            ),
            itemStyle: { borderRadius: 8 },
          },
        ],
      })),

      onChartClick,
      mismatchDetails,
      perPositionOption,
      loading,
    };
  },
};
</script>

<style scoped>
.site--main {
  padding: 20px;
}

/* 骨架屏容器 */
.skeleton-wrapper {
  width: 100%;
}

/* 白色卡片式表格 */
.table-section {
  margin-bottom: 30px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
}

/* s-table 自定义样式 */
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

/* 标题 */
h2 {
  margin-bottom: 16px;
}

/* 小标题 */
h3 {
  margin-bottom: 12px;
}

/* 调整 loading 遮罩所在容器的相对定位 */
.site--main .el-loading-mask {
  border-radius: 8px;
}

/* 美化骨架屏的背景 */
.el-skeleton__wrapper {
  background-color: #f0f2f5;
}

/* 美化 SVG 图表区 */
</style>