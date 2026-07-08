<template>
  <div class="site--main">
    <!-- 1. PMID 加载骨架 -->
    <div v-if="loadingPmid" class="skeleton-wrapper">
      <el-skeleton :rows="5" animated style="margin-bottom:24px; border-radius:8px;" />
    </div>

    <!-- 2. PMID 表格 -->
    <div v-else class="table-section">
      <h2>Engineered sup-tRNA</h2>
      <TableToolbar
        v-model="searchText"
        v-model:column="searchColumn"
        v-model:size="tableSize"
        :search-columns="pmidSearchableColumns"
        :show-columns="false"
      />

      <s-table-provider :hover="true" theme-color="#00ACF5" :locale="locale">
        <s-table
          :columns="pmidColumns"
          :data-source="filteredPmidData"
          :pagination="pagination"
          :row-key="record => record.PMID"
          :expand-row-by-click="true"
          :size="tableSize"
          @change="handleTableChange"
          @pagination-change="handlePaginationChange"
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
            <el-tooltip
              :content="cellTooltipContent(text, column)"
              placement="top"
              effect="light"
              :show-after="150"
              :hide-after="0"
              :disabled="!cellTooltipContent(text, column)"
            >
              <a
                v-if="column.dataIndex === 'PMID'"
                :href="`https://pubmed.ncbi.nlm.nih.gov/${text}`"
                target="_blank"
                rel="noopener noreferrer"
                class="pmid-link-button"
                :aria-label="cellTooltipContent(text, column)"
                @click.stop
              >
                <Link />
              </a>
              <span v-else-if="column.dataIndex === 'Source'" class="pmid-text-cell"><em>{{ text }}</em></span>
              <span v-else class="pmid-text-cell">{{ text }}</span>
            </el-tooltip>
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
import tRNAtherapeutics1 from './tRNAtherapeutics-1.vue';
import en from '@shene/table/dist/locale/en';
import type { EChartsOption } from 'echarts';
import { ElSkeleton, ElTooltip } from 'element-plus';
import { Link } from '@element-plus/icons-vue';
import TableToolbar from '@/components/TableToolbar.vue';
import VChart from '@/components/LazyChart.vue';

const locale = ref(en);

// 后端 API（同源部署可留空，或写你的后端域名/端口）
const API_BASE = ''; // 如需直连本机后端：'http://127.0.0.1:8010'
const PMID_TABLE = 'pmid_article_info_extended';
const PERPOS_TABLE = 'engineered_sup_trna_perpos_counts';

export default {
  name: 'tRNAtherapeutics',
  components: { tRNAtherapeutics1, STableProvider, ElSkeleton, ElTooltip, Link, TableToolbar, VChart },
  setup() {
    // ===== 加载状态 =====
    const loadingPmid = ref(true);  // PMID 主表格（MySQL）
    const loadingSup  = ref(true);  // 图表数据（MySQL）

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

    // ===== PMID 主表格（MySQL） =====
    const searchText   = ref('');
    const searchColumn = ref('');
    const tableSize    = ref<'small'|'default'|'large'>('default');
    const rawPmidData  = ref<any[]>([]);
    const pagination   = ref({ current:1, pageSize:10, total:0, showSizeChanger:true, showQuickJumper:true });
    const selectedPubYear = ref('');
    const pubDateSortOrder = ref<'desc'|'asc'>('desc');

    const pubYearOptions = computed(() => {
      return Array.from(new Set(
        rawPmidData.value
          .map(row => String(row.PubYear ?? ''))
          .filter(Boolean)
      )).sort((a, b) => Number(b) - Number(a));
    });

    const pubDateFilterOptions = computed(() => [
      { text: 'All years', value: '__all__' },
      ...pubYearOptions.value.map(year => ({ text: year, value: year }))
    ]);

    const pmidColumns = computed(() => [
      { title:'Title', dataIndex:'Title', key:'Title', width:760, ellipsis:true, resizable:true },
      { title:'Source', dataIndex:'Source', key:'Source', width:180, resizable:true,
        customRender: ({ text }: any) => <em>{text}</em>
      },
      { title:'Author', dataIndex:'Author', key:'Author', width:480, ellipsis:true, resizable:true },
      {
        title:'PubDate',
        dataIndex:'PubDate',
        key:'PubDate',
        width:126,
        resizable:true,
        sorter: true,
        sortOrder: pubDateSortOrder.value === 'desc' ? 'descend' : 'ascend',
        sortDirections: ['descend', 'ascend'],
        filter: {
          type: 'single',
          list: pubDateFilterOptions.value,
          resetValue: '',
          onFilter: (value: string, record: any) => {
            if (!value || value === '__all__') return true;
            return String(record.PubYear ?? '') === String(value);
          }
        }
      },
      { title:'ID', dataIndex:'PMID', key:'PMID', width:48, align:'center', resizable:true,
        customRender: ({ text }: any) => (
          <a
            href={`https://pubmed.ncbi.nlm.nih.gov/${text}`}
            target="_blank"
            rel="noopener noreferrer"
            class="pmid-link-button"
            aria-label={`Open PubMed ${text}`}
          >
            <Link />
          </a>
        )
      }
    ]);
    const pmidSearchableColumns = computed(() => pmidColumns.value);

    const filteredPmidData = computed(() => {
      let data = rawPmidData.value;
      if (selectedPubYear.value) {
        data = data.filter(r => String(r.PubYear ?? '') === selectedPubYear.value);
      }
      if (searchText.value) {
        data = data.filter(r => {
          const hay = (searchColumn.value
            ? String(r[searchColumn.value])
            : Object.values(r).join(' ')
          ).toLowerCase();
          return hay.includes(searchText.value.toLowerCase());
        });
      }
      return [...data].sort((a, b) => {
        const left = Number(a._pubDateMs ?? -Infinity);
        const right = Number(b._pubDateMs ?? -Infinity);
        return pubDateSortOrder.value === 'desc' ? right - left : left - right;
      });
    });
    watch([searchText, searchColumn, selectedPubYear, pubDateSortOrder], () => {
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

    const handleTableChange = (pag: any, filters?: Record<string, any>, sorter?: any) => {
      const selectedYear = Array.isArray(filters?.PubDate) ? String(filters?.PubDate?.[0] ?? '') : '';
      selectedPubYear.value = selectedYear === '__all__' ? '' : selectedYear;
      if (!Array.isArray(filters?.PubDate) || !filters?.PubDate?.length) {
        selectedPubYear.value = '';
      }

      const order = Array.isArray(sorter) ? sorter[0]?.order : sorter?.order;
      if (order === 'ascend') pubDateSortOrder.value = 'asc';
      if (order === 'descend') pubDateSortOrder.value = 'desc';

      pagination.value = { ...pagination.value, ...pag };
      const total = filteredPmidData.value.length;
      pagination.value.total = total;
      const maxPage = Math.max(1, Math.ceil(total / pagination.value.pageSize));
      if (pagination.value.current > maxPage) pagination.value.current = maxPage;
    };

    const handlePaginationChange = (pag: any) => {
      pagination.value = { ...pagination.value, ...pag };
      const total = filteredPmidData.value.length;
      pagination.value.total = total;
      const maxPage = Math.max(1, Math.ceil(total / pagination.value.pageSize));
      if (pagination.value.current > maxPage) pagination.value.current = maxPage;
    };

    const cellTooltipContent = (text: unknown, column: any) => {
      const value = String(text ?? '').trim();
      if (!value) return '';
      if (column?.dataIndex === 'PMID') return `Open PubMed ${value}`;
      return value;
    };

    // ===== 图表：读取聚合后的 MySQL 表 =====
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

    const fetchTableRows = async <T,>(payload: Record<string, any>): Promise<T[]> => {
      const resp = await fetch(`${API_BASE}/table_rows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || `table_rows failed: ${resp.status}`);
      }
      const json = await resp.json();
      return Array.isArray(json?.rows) ? json.rows : [];
    };

    const formatPubDate = (value: string) => {
      if (!value) return '';
      const date = new Date(value);
      return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString();
    };

    const parsePubDateMs = (value: string) => {
      if (!value) return -Infinity;
      const normalized = value.replace(/-/g, '/');
      const date = new Date(normalized);
      const ms = date.getTime();
      return Number.isNaN(ms) ? -Infinity : ms;
    };

    const extractPubYear = (value: string) => {
      const match = String(value || '').match(/\b(19|20)\d{2}\b/);
      return match?.[0] ?? '';
    };

    const formatAuthors = (value: string) => {
      if (!value) return '';
      const trimmed = value.trim();
      if (!trimmed) return '';
      if (trimmed.toLowerCase().includes('et al.')) return trimmed;
      const parts = trimmed.split(',').map(p => p.trim()).filter(Boolean);
      if (!parts.length) return trimmed;
      return parts.slice(0, 3).join(', ') + (parts.length > 3 ? ' et al.' : '');
    };

    // ===== 挂载：先加载 PMID 表，再加载 perpos 表 =====
    onMounted(async () => {
      // 1) PMID 列表
      try {
        const rows = await fetchTableRows<any>({
          table: PMID_TABLE,
          page: 1,
          page_size: 10000,
          search_text: '',
          search_column: '',
          sort_by: '',
          sort_order: 'asc',
          case_insensitive: true
        });
        rawPmidData.value = rows.map((row) => ({
          PubDate: formatPubDate(String(row.PubDate ?? '')),
          PubYear: extractPubYear(String(row.PubDate ?? '')),
          _pubDateMs: parsePubDateMs(String(row.PubDate ?? '')),
          Source: String(row.Source ?? ''),
          Author: formatAuthors(String(row.Author ?? '')),
          Title: String(row.Title ?? ''),
          PMID: String(row.PMID ?? '')
        }));
        pagination.value.total = rawPmidData.value.length;
      } catch(e) {
        console.error(e);
      } finally {
        loadingPmid.value = false;
      }

      // 2) perpos 表（图表）
      try {
        const rows = await fetchTableRows<any>({
          table: PERPOS_TABLE,
          page: 1,
          page_size: 10000,
          search_text: '',
          search_column: '',
          sort_by: '',
          sort_order: 'asc',
          case_insensitive: true
        });
        perposRows.value = rows.map(row => ({
          position: String(row.position ?? ''),
          match: Number(row.match ?? 0),
          mismatch: Number(row.mismatch ?? 0),
          insertion: Number(row.insertion ?? 0),
          deletion: Number(row.deletion ?? 0)
        }));
      } catch (e) {
        console.error('load PERPOS_TABLE failed:', e);
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
      selectedPubYear,
      pubDateSortOrder,
      pubYearOptions,
      pagination,
      filteredPmidData,
      handleTableChange,
      handlePaginationChange,
      cellTooltipContent,

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
.site--main {
  box-sizing: border-box;
  width: min(1760px, calc(100vw - 128px));
  max-width: none;
  margin: 0 auto;
  padding: 20px;
  color: var(--app-text);
  --thera-card-bg: #ffffff;
  --thera-card-border: var(--app-border);
  --thera-card-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  --thera-table-header-bg: #fafafa;
  --thera-row-hover: #f5f7fa;
  --thera-skeleton-bg: #f0f2f5;
  --thera-input-bg: #ffffff;
  --thera-input-border: #cccccc;
  --thera-input-text: var(--app-text);
}
.skeleton-wrapper { width: 100%; }
.table-section {
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 30px;
  background: var(--thera-card-bg);
  border: 1px solid var(--thera-card-border);
  border-radius: 8px;
  box-shadow: var(--thera-card-shadow);
  padding: 16px;
}
:deep(.s-table)          { border-radius: 8px; overflow: hidden; }
:deep(.s-table-header),
:deep(.s-table__header)   { background: var(--thera-table-header-bg); }
:deep(.s-table .s-table__column-sort) {
  background: inherit;
}
:deep(.s-table__body .s-table__column-sort) {
  background: inherit;
}
:deep(.s-table-row:hover){ background: var(--thera-row-hover) !important; }
h2 { margin-bottom: 16px; color: var(--app-text); }
h3 { margin-bottom: 12px; color: var(--app-text); }
.el-skeleton__wrapper { background-color: var(--thera-skeleton-bg); }
:deep(.pmid-text-cell) {
  display: block;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
:deep(.pmid-link-button) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  color: var(--app-text);
  background: var(--app-surface);
  font-size: 16px;
  line-height: 1;
  text-decoration: none;
}
:deep(.pmid-link-button svg) {
  width: 16px;
  height: 16px;
}
:deep(.pmid-link-button:hover) {
  border-color: #2f65b0;
  color: #2f65b0;
  background: rgba(47, 101, 176, 0.08);
}
@media (prefers-color-scheme: dark) {
  .site--main {
    --thera-card-bg: var(--app-surface);
    --thera-card-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
    --thera-table-header-bg: var(--app-surface-2);
    --thera-row-hover: var(--app-surface-2);
    --thera-skeleton-bg: var(--app-surface-2);
    --thera-input-bg: var(--app-surface);
    --thera-input-border: var(--app-border);
  }
}

@media (max-width: 900px) {
  .site--main {
    width: 100%;
    padding: 20px;
  }
}

:global(:root[data-theme="dark"]) .site--main {
  --thera-card-bg: var(--app-surface);
  --thera-card-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
  --thera-table-header-bg: var(--app-surface-2);
  --thera-row-hover: var(--app-surface-2);
  --thera-skeleton-bg: var(--app-surface-2);
  --thera-input-bg: var(--app-surface);
  --thera-input-border: var(--app-border);
}
</style>
