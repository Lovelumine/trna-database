<template>
  <div class="site--main">
    <!-- 1. PMID 加载骨架 -->
    <div v-if="loadingPmid" class="skeleton-wrapper">
      <el-skeleton :rows="5" animated style="margin-bottom:24px; border-radius:8px;" />
    </div>

    <!-- 2. PMID 表格 -->
    <div v-else class="table-section">
      <h2>Engineered sup-tRNA</h2>
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
            <!-- 触发展开即按 PMID 调后端 /search 拉取，仅该 PMID 相关行 -->
            <span v-if="triggerFetch(record.PMID)" style="display:none"></span>
            <tRNAtherapeutics1
              :selectedPmids="[record.PMID]"
              :supData="supByPmid[record.PMID] || []"
              :loadingSup="loadingSupByPmid[record.PMID] ?? true"
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

    <!-- 3. 聚合小文件加载骨架（用于总体图表） -->
    <div v-if="!loadingPmid && loadingSup" class="skeleton-wrapper">
      <el-skeleton variant="rect" animated style="height:400px; border-radius:8px;" />
    </div>

    <!-- 4. 渲染 “Per-Position Alignment Variation” 图表 -->
    <section v-if="!loadingSup" style="margin:24px 0">
      <h3>Per-Position Alignment Variation</h3>
      <VChart :option="perPositionOption" autoresize style="height:400px;" />
    </section>
  </div>
</template>

<script lang="tsx">
import { ref, computed, onMounted, watch } from 'vue';
import { STableProvider } from '@shene/table';
import Papa from 'papaparse';
import tRNAtherapeutics1 from './tRNAtherapeutics-1.vue';
import en from '@shene/table/dist/locale/en';
import type { EChartsOption } from 'echarts';
import { ElSkeleton } from 'element-plus';

const locale = ref(en);

// 图表改为读取你的小文件（保持不变）
const PERPOS_COUNTS_URL = 'https://minio.lumoxuan.cn/ensure/Engineered-Sup-tRNA.perpos.counts.csv';

// 后端 API（同源部署可留空，或写你的后端域名/端口）
const API_BASE = ''; // 如需直连本机后端：'http://127.0.0.1:8000'

export default {
  name: 'tRNAtherapeutics',
  components: { tRNAtherapeutics1, STableProvider, ElSkeleton },
  setup() {
    // ===== 加载状态 =====
    const loadingPmid = ref(true);  // PMID 主表格（保留 CSV 流程）
    const loadingSup  = ref(true);  // 图表小文件

    // ===== 每行展开 -> 用后端 MySQL /search_table 按 PMID 分批拉取 =====
    const supByPmid = ref<Record<string, any[]>>({});
    const loadingSupByPmid = ref<Record<string, boolean>>({});
    const fetchedSet = new Set<string>();

    async function fetchSupRowsForPmid(pmid: string) {
      loadingSupByPmid.value[pmid] = true;
      try {
        // ★ 修改点：改用 MySQL 搜索接口 /search_table，精确按 PMID 查询 sup-tRNA 记录
        const payload = {
          table: 'Engineered_sup_tRNA',
          column: 'PMID',
          value: pmid,
          mode: 'exact',
          limit: 1000
        };
        const resp = await fetch(`${API_BASE}/search_table`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const json = await resp.json();
        // 后端返回 { results: [...] }，直接取结果即可
        supByPmid.value[pmid] = Array.isArray(json?.results) ? json.results : [];
      } catch (e) {
        console.error('[fetchSupRowsForPmid] error:', e);
        supByPmid.value[pmid] = [];
      } finally {
        loadingSupByPmid.value[pmid] = false;
      }
    }

    function triggerFetch(pmid: string) {
      if (!fetchedSet.has(pmid)) {
        fetchedSet.add(pmid);
        void fetchSupRowsForPmid(pmid);
      }
      return true;
    }

    // ===== PMID 主表格（保持不变：仍然从 CSV 加载） =====
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

    watch([searchText, searchColumn], () => {
      pagination.value.current = 1;
    });

    watch(
      () => filteredPmidData.value.length,
      (len) => {
        pagination.value.total = len;
        const maxPage = Math.max(1, Math.ceil(len / pagination.value.pageSize));
        if (pagination.value.current > maxPage) pagination.value.current = maxPage;
      },
      { immediate: true }
    );

    watch(
      () => pagination.value.pageSize,
      () => {
        const total = filteredPmidData.value.length;
        pagination.value.total = total;
        const maxPage = Math.max(1, Math.ceil(total / pagination.value.pageSize));
        if (pagination.value.current > maxPage) pagination.value.current = maxPage;
      }
    );

    const handleTableChange = (pag: any) => {
      pagination.value = { ...pagination.value, ...pag };
      const total = filteredPmidData.value.length;
      pagination.value.total = total;
      const maxPage = Math.max(1, Math.ceil(total / pagination.value.pageSize));
      if (pagination.value.current > maxPage) pagination.value.current = maxPage;
    };

    // ===== 图表：读取聚合后的小 CSV（保持不变） =====
    type PerRow = { position: string; match: number; mismatch: number; insertion: number; deletion: number };
    const perposRows = ref<PerRow[]>([]);

    const perPositionOption = computed<EChartsOption>(() => {
      if (!perposRows.value.length) {
        return {
          tooltip: { trigger: 'axis' },
          legend:  { data: [], top: 30 },
          xAxis:   { type: 'category', data: [], name: 'position' },
          yAxis:   { type: 'value', name: 'count' },
          series:  []
        };
      }

      // 先把能转成数字的按数字升序，其余（如 V1、7a1）保持原文件顺序排在后面
      const rows = [...perposRows.value];
      const numRows  = rows.filter(r => !Number.isNaN(Number(r.position)))
                           .sort((a, b) => Number(a.position) - Number(b.position));
      const restRows = rows.filter(r =>  Number.isNaN(Number(r.position))); // 保留原顺序
      const ordered  = numRows.concat(restRows);

      const positions = ordered.map(r => r.position);
      const match     = ordered.map(r => r.match);
      const mismatch  = ordered.map(r => r.mismatch);
      const insertion = ordered.map(r => r.insertion);
      const deletion  = ordered.map(r => r.deletion);

      return {
        tooltip: { trigger: 'axis' },
        legend:  { data: ['match','mismatch','insertion','deletion'], top: 30 },
        xAxis:   { type: 'category', data: positions, name: 'position', axisLabel: { rotate: 45 } },
        yAxis:   { type: 'value', name: 'count' },
        series: [
          { name: 'match',     type: 'bar', stack: 'all', data: match,     itemStyle: { borderRadius: 4 } },
          { name: 'mismatch',  type: 'bar', stack: 'all', data: mismatch,  itemStyle: { borderRadius: 4 } },
          { name: 'insertion', type: 'bar', stack: 'all', data: insertion, itemStyle: { borderRadius: 4 } },
          { name: 'deletion',  type: 'bar', stack: 'all', data: deletion,  itemStyle: { borderRadius: 4 } }
        ]
      };
    });

    // ===== 挂载：先加载 PMID CSV，再加载小 CSV（保持不变） =====
    onMounted(async () => {
      // 1) PMID 列表（保持不变）
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

      // 2) 小 CSV（图表）
      try {
        const resp2 = await fetch(PERPOS_COUNTS_URL);
        const txt2  = await resp2.text();
        Papa.parse(txt2, {
          header: true,
          skipEmptyLines: true,
          complete(res) {
            perposRows.value = (res.data as any[]).map(r => ({
              position: String(r.position),
              match:     Number(r.match ?? 0),
              mismatch:  Number(r.mismatch ?? 0),
              insertion: Number(r.insertion ?? 0),
              deletion:  Number(r.deletion ?? 0)
            }));
          }
        });
      } catch (e) {
        console.error('load PERPOS_COUNTS_URL failed:', e);
      } finally {
        loadingSup.value = false;
      }
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

      // 展开行数据（已改为 MySQL）
      supByPmid,
      loadingSupByPmid,
      triggerFetch,
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