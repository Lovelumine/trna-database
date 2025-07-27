<template>
  <div class="site--main">
    <!-- 1. PMID 加载时，先展示表格骨架 -->
    <div v-if="loadingPmid" class="skeleton-wrapper">
      <el-skeleton :rows="5" animated style="margin-bottom:24px; border-radius:8px;" />
    </div>

    <!-- 2. PMID 加载完成后，展示 PMID 表格 -->
    <div v-else class="table-section">
      <h2>Engineered Sup-tRNA</h2>
      <div class="top-controls">
        <div class="search-box">
          <input v-model="searchText" placeholder="Enter search content" class="search-input" />
          <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
            <el-option key="all" label="All columns" :value="''" />
            <el-option
              v-for="col in pmidSearchableColumns"
              :key="col.key"
              :label="col.title"
              :value="col.dataIndex"
            />
          </el-select>
        </div>
        <div class="size-controls">
          <el-radio-group v-model="tableSize">
            <el-radio-button value="small">Small Size</el-radio-button>
            <el-radio-button value="default">Default Size</el-radio-button>
            <el-radio-button value="large">Large Size</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <s-table-provider :hover="true" theme-color="#00ACF5" :locale="locale">
        <s-table
          :columns="pmidColumns"
          :data-source="paginatedFilteredPmidData"
          :pagination="pagination"
          :row-key="record => record.PMID"
          :expand-row-by-click="true"
          :size="tableSize"
          @change="handleTableChange"
        >
          <template #expandedRowRender="{ record }">
            <!-- 传入 supData 和加载状态，子组件展示进度条 -->
            <tRNAtherapeutics1
              :selectedPmids="[record.PMID]"
              :supData="supData"
              :loadingSup="loadingSup"
            />
          </template>
          <template #default="{ text, column }">
            <span v-if="column.dataIndex === 'PMID'">
              <a :href="`https://pubmed.ncbi.nlm.nih.gov/${text}`" target="_blank">{{ text }}</a>
            </span>
            <span v-else-if="column.dataIndex === 'Source'"><em>{{ text }}</em></span>
            <span v-else>{{ text }}</span>
          </template>
        </s-table>
      </s-table-provider>
    </div>

    <!-- 3. supData 加载时，显示图表骨架 -->
    <div v-if="!loadingPmid && loadingSup" class="skeleton-wrapper">
      <el-skeleton variant="rect" animated style="height:400px; border-radius:8px;" />
    </div>

    <!-- 4. supData 加载完成后，渲染 Alignment 图表 -->
    <section v-if="!loadingSup" style="margin:24px 0">
      <h3>Per-Position Alignment Variation</h3>
      <VChart :option="perPositionOption" autoresize style="height:400px;" />
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
import type { EChartsOption } from 'echarts';
import { ElSkeleton } from 'element-plus';

const locale = ref(en);
interface AlignmentItem { id: string; base: string; sup_base: string; }

export default {
  name: 'tRNAtherapeutics',
  components: { tRNAtherapeutics1, STableProvider, ElSkeleton },
  setup() {
    // 两个加载状态：PMID 和 supData
    const loadingPmid = ref(true);
    const loadingSup  = ref(true);

    // 父组件中只加载一次 sup-tRNA 数据
    const { filteredDataSource: supData, loadData: loadSupData } =
      useTableData('https://minio.lumoxuan.cn/ensure/Engineered Sup-tRNA.csv');

    // PMID 表格搜索与分页
    const searchText   = ref('');
    const searchColumn = ref('');
    const tableSize    = ref<'small'|'default'|'large'>('default');
    const rawPmidData  = ref<any[]>([]);
    const pagination   = ref({ current:1, pageSize:10, total:0, showSizeChanger:true, showQuickJumper:true });

    const pmidColumns = ref([
      { title:'PMID', dataIndex:'PMID', key:'PMID', width:100, resizable:true,
        customRender: ({ text }: any) => (
          <a href={`https://pubmed.ncbi.nlm.nih.gov/${text}`} target="_blank">{text}</a>
        )
      },
      { title:'Title', dataIndex:'Title', key:'Title', width:500, ellipsis:true, resizable:true },
      { title:'Source', dataIndex:'Source', key:'Source', width:150, resizable:true,
        customRender: ({ text }: any) => <em>{text}</em>
      },
      { title:'Author', dataIndex:'Author', key:'Author', width:200, ellipsis:true, resizable:true },
      { title:'PubDate', dataIndex:'PubDate', key:'PubDate', width:120, resizable:true }
    ]);
    const pmidSearchableColumns = pmidColumns.value;

    // 过滤 & 分页 PMID 数据
    const filteredPmidData = computed(() => {
      if (!searchText.value) return rawPmidData.value;
      return rawPmidData.value.filter(r => {
        const hay = (searchColumn.value
          ? String(r[searchColumn.value])
          : Object.values(r).join(' ')
        ).toLowerCase();
        return hay.includes(searchText.value.toLowerCase());
      });
    });
    const paginatedFilteredPmidData = computed(() => {
      const start = (pagination.value.current - 1) * pagination.value.pageSize;
      return filteredPmidData.value.slice(start, start + pagination.value.pageSize);
    });
    const handleTableChange = (pag: any) => {
      pagination.value = { ...pagination.value, ...pag };
    };

    // 基于 supData 构建 Alignment 图表
    const safeRecords = computed(() => supData.value || []);
    const getType = (item: AlignmentItem) =>
      item.base === '-' && item.sup_base !== '-' ? 'insertion'
      : item.base !== '-' && item.sup_base === '-' ? 'deletion'
      : item.base === item.sup_base               ? 'match'
      : 'mismatch';
    const perPositionCounts = computed(() => {
      const M: Record<string, any> = {};
      safeRecords.value.forEach(rec => {
        let arr: AlignmentItem[] = [];
        try { arr = JSON.parse(rec.js_sup_tRNA || '[]'); } catch {}
        arr.forEach(it => {
          const p = it.id;
          if (!M[p]) M[p] = { match:0, mismatch:0, insertion:0, deletion:0 };
          M[p][getType(it)]++;
        });
      });
      return M;
    });
    const perPositionOption = computed<EChartsOption>(() => {
      const positions = Object.keys(perPositionCounts.value).sort((a,b)=>+a - +b);
      const types = ['match','mismatch','insertion','deletion'];
      const series = types.map(type => ({
        name: type, type:'bar' as const, stack:'all',
        data: positions.map(p => perPositionCounts.value[p][type]),
        itemStyle:{ borderRadius:4 }
      }));
      return {
        tooltip: { trigger:'axis' },
        legend:  { data: types.slice(), top:30 },
        xAxis:   { type:'category', data:positions, name:'position', axisLabel:{ rotate:45 } },
        yAxis:   { type:'value', name:'count' },
        series
      };
    });

    // 挂载顺序：先加载 PMID，再加载 supData
    onMounted(async () => {
      // 加载 PMID
      try {
        const resp = await fetch('https://minio.lumoxuan.cn/ensure/pmid_article_info_extended.csv');
        const txt  = await resp.text();
        Papa.parse(txt, {
          skipEmptyLines:true,
          header: false,
          complete(result) {
            rawPmidData.value = result.data.slice(1).map((r: any[]) => ({
              PubDate: new Date(r[0]).toLocaleDateString(),
              Source:  r[1],
              Author:  r[2].split(',').slice(0,3).join(', ') + ' et al.',
              Title:   r[3],
              PMID:    String(r[4]),
            }));
            pagination.value.total = rawPmidData.value.length;
          }
        });
      } catch(e) {
        console.error(e);
      } finally {
        loadingPmid.value = false;
      }
      // 加载 sup-tRNA 数据
      await loadSupData();
      loadingSup.value = false;
    });

    return {
      locale,
      pmidColumns,
      pmidSearchableColumns,
      searchText,
      searchColumn,
      tableSize,
      pagination,
      paginatedFilteredPmidData,
      handleTableChange,
      perPositionOption,
      loadingPmid,
      loadingSup,
      supData,
    };
  }
};
</script>

<style scoped>
.site--main { padding: 20px; }
.skeleton-wrapper { width: 100%; }
.table-section {
  margin-bottom: 30px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  padding: 16px;
}
:deep(.s-table)          { border-radius: 8px; overflow: hidden; }
:deep(.s-table-header)   { background: #fafafa; }
:deep(.s-table-row:hover){ background: #f5f7fa!important; }
h2 { margin-bottom: 16px; }
h3 { margin-bottom: 12px; }
.el-skeleton__wrapper { background-color: #f0f2f5; }
.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.search-box { flex: 1; margin-right: 10px; display: flex; gap: 8px; }
.size-controls { display: flex; }
.search-input { flex: 1; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px; }
.search-column-select { width: 180px; }
</style>