import { ref } from 'vue';
import axios from 'axios';

export type SortOrder = 'asc' | 'desc';

export type MysqlStatFilter = {
  column: string;
  op?: 'eq' | 'neq';
  value: string | number;
};

export type MysqlTableFilter = {
  column: string;
  values: Array<string | number>;
  mode?: 'contains';
};

export type MysqlTableStat =
  | {
      type: 'value_counts';
      name?: string;
      column: string;
      split_regex?: string;
      top_n?: number;
      filters?: MysqlStatFilter[];
    }
  | {
      type: 'matrix_counts';
      name?: string;
      x_column: string;
      y_column: string;
      filters?: MysqlStatFilter[];
    }
  | {
      type: 'codon_change_heatmap';
      name?: string;
      column: string;
      exclude_mut_regex?: string;
      filters?: MysqlStatFilter[];
    };

export interface MysqlTablePageParams {
  page: number;
  pageSize: number;
  searchText?: string;
  searchColumn?: string;
  searchValues?: string[];
  filters?: MysqlTableFilter[];
  sortBy?: string;
  sortOrder?: SortOrder;
  caseInsensitive?: boolean;
  useFulltext?: boolean;
  fulltextIndex?: string;
}

export interface MysqlTableStatsParams {
  stats: Array<string | MysqlTableStat>;
  searchText?: string;
  searchColumn?: string;
  searchValues?: string[];
  filters?: MysqlTableFilter[];
  caseInsensitive?: boolean;
  useFulltext?: boolean;
  fulltextIndex?: string;
}

export function useMysqlTableData(table: string) {
  const rows = ref<any[]>([]);
  const total = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const cache = new Map<string, { rows: any[]; total: number }>();
  const cacheOrder: string[] = [];
  const MAX_CACHE_SIZE = 30;
  const prefetchControllers = new Set<AbortController>();
  let prefetchToken = 0;

  const serializeFilters = (filters?: MysqlTableFilter[]) => {
    if (!filters || !filters.length) return '';
    const normalized = filters
      .map((f) => {
        const values = (f.values || []).map(String).sort().join(',');
        return `${f.column}:${values}:${f.mode || 'contains'}`;
      })
      .sort();
    return normalized.join(';');
  };

  const buildKey = (params: MysqlTablePageParams) =>
    [
      table,
      params.page,
      params.pageSize,
      params.searchText || '',
      params.searchColumn || '',
      (params.searchValues || []).join(','),
      serializeFilters(params.filters),
      params.sortBy || '',
      params.sortOrder || 'asc',
      params.caseInsensitive === false ? '0' : '1',
      params.useFulltext === false ? '0' : '1',
      params.fulltextIndex || ''
    ].join('|');

  const setCache = (key: string, payload: { rows: any[]; total: number }) => {
    if (!cache.has(key)) {
      cacheOrder.push(key);
    }
    cache.set(key, payload);
    while (cacheOrder.length > MAX_CACHE_SIZE) {
      const drop = cacheOrder.shift();
      if (drop) cache.delete(drop);
    }
  };

  const cancelPrefetch = () => {
    prefetchToken += 1;
    prefetchControllers.forEach((controller) => controller.abort());
    prefetchControllers.clear();
  };

  const fetchRows = async (
    params: MysqlTablePageParams,
    options: { useCache?: boolean; refresh?: boolean } = {}
  ) => {
    const key = buildKey(params);
    const useCache = options.useCache !== false;
    if (useCache && cache.has(key) && !options.refresh) {
      const cached = cache.get(key)!;
      rows.value = cached.rows;
      total.value = cached.total;
      return;
    }

    loading.value = true;
    error.value = null;
    try {
      const payload = {
        table,
        page: params.page,
        page_size: params.pageSize,
        search_text: params.searchText || '',
        search_column: params.searchColumn || '',
        search_values: params.searchValues || [],
        filters: params.filters || [],
        sort_by: params.sortBy || '',
        sort_order: params.sortOrder || 'asc',
        case_insensitive: params.caseInsensitive !== false,
        use_fulltext: params.useFulltext !== false,
        fulltext_index: params.fulltextIndex || ''
      };
      const resp = await axios.post('/table_rows', payload);
      const nextRows = resp.data?.rows || [];
      const nextTotal = Number(resp.data?.total ?? 0);
      rows.value = nextRows;
      total.value = nextTotal;
      if (useCache) {
        setCache(key, { rows: nextRows, total: nextTotal });
      }
    } catch (err: any) {
      error.value = err?.response?.data?.error || err?.message || 'Unknown error';
    } finally {
      loading.value = false;
    }
  };

  const prefetchRows = async (params: MysqlTablePageParams, token: number) => {
    const key = buildKey(params);
    if (cache.has(key)) return;
    if (token !== prefetchToken) return;
    const controller = new AbortController();
    prefetchControllers.add(controller);
    try {
      const payload = {
        table,
        page: params.page,
        page_size: params.pageSize,
        search_text: params.searchText || '',
        search_column: params.searchColumn || '',
        search_values: params.searchValues || [],
        filters: params.filters || [],
        sort_by: params.sortBy || '',
        sort_order: params.sortOrder || 'asc',
        case_insensitive: params.caseInsensitive !== false,
        use_fulltext: params.useFulltext !== false,
        fulltext_index: params.fulltextIndex || ''
      };
      const resp = await axios.post('/table_rows', payload, {
        signal: controller.signal
      });
      setCache(key, {
        rows: resp.data?.rows || [],
        total: Number(resp.data?.total ?? 0)
      });
    } catch {
      // ignore prefetch errors
    } finally {
      prefetchControllers.delete(controller);
    }
  };

  const prefetchRange = async (
    params: MysqlTablePageParams,
    count: number,
    options: { concurrency?: number } = {}
  ) => {
    cancelPrefetch();
    const token = prefetchToken;
    const pages = Array.from({ length: count }, (_, i) => params.page + i + 1);
    const concurrency = Math.max(
      1,
      Math.min(options.concurrency ?? 4, pages.length)
    );
    let index = 0;

    const worker = async () => {
      while (token === prefetchToken) {
        const page = pages[index++];
        if (!page) break;
        await prefetchRows({ ...params, page }, token);
      }
    };

    const workers = Array.from({ length: concurrency }, () => worker());
    await Promise.all(workers);
  };

  const fetchStats = async (params: MysqlTableStatsParams) => {
    const payload = {
      table,
      stats: params.stats || [],
      search_text: params.searchText || '',
      search_column: params.searchColumn || '',
      search_values: params.searchValues || [],
      filters: params.filters || [],
      case_insensitive: params.caseInsensitive !== false,
      use_fulltext: params.useFulltext !== false,
      fulltext_index: params.fulltextIndex || ''
    };
    const resp = await axios.post('/table_stats', payload);
    return resp.data || {};
  };

  return {
    rows,
    total,
    loading,
    error,
    fetchRows,
    prefetchRange,
    cancelPrefetch,
    fetchStats
  };
}
