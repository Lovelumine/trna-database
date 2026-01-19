import { ref, watch } from 'vue';
import { createPagination } from './table';
import type { SortOrder } from './useMysqlTableData';
import { useMysqlTableData } from './useMysqlTableData';

export type ServerTableSize = 'small' | 'default' | 'large';

export type ServerTableOptions = {
  pageSize?: number;
  prefetchPages?: number;
  prefetchConcurrency?: number;
  debounceMs?: number;
  useFulltextWhenNoColumn?: boolean;
  normalizeRow?: (row: any) => any;
  initialSortBy?: string;
  initialSortOrder?: SortOrder;
  fulltextIndex?: string;
};

export function useServerTable(table: string, options: ServerTableOptions = {}) {
  const {
    pageSize,
    prefetchPages = 0,
    prefetchConcurrency = 4,
    debounceMs = 300,
    useFulltextWhenNoColumn = true,
    normalizeRow,
    initialSortBy = '',
    initialSortOrder = 'asc',
    fulltextIndex
  } = options;

  const tableSize = ref<ServerTableSize>('default');
  const searchText = ref('');
  const searchColumn = ref('');
  const sortBy = ref(initialSortBy);
  const sortOrder = ref<SortOrder>(initialSortOrder);
  const pagination = createPagination();
  if (pageSize) pagination.pageSize = pageSize;

  const {
    rows,
    total,
    loading,
    error,
    fetchRows,
    prefetchRange,
    cancelPrefetch,
    fetchStats
  } = useMysqlTableData(table);

  const buildParams = (pageOverride?: number) => ({
    page: pageOverride ?? pagination.current,
    pageSize: pagination.pageSize,
    searchText: searchText.value,
    searchColumn: searchColumn.value,
    sortBy: sortBy.value,
    sortOrder: sortOrder.value,
    useFulltext: useFulltextWhenNoColumn && !searchColumn.value,
    fulltextIndex
  });

  const applyRowTransform = () => {
    if (!normalizeRow) return;
    rows.value = rows.value.map((row) => normalizeRow(row));
  };

  const schedulePrefetch = (maxPage: number) => {
    if (prefetchPages <= 0) return;
    const remaining = maxPage - pagination.current;
    const count = Math.min(prefetchPages, remaining);
    if (count <= 0) return;
    const baseParams = buildParams(pagination.current);
    const run = () => {
      void prefetchRange(baseParams, count, { concurrency: prefetchConcurrency });
    };
    const idle = (window as any).requestIdleCallback;
    if (typeof idle === 'function') {
      idle(() => run());
    } else {
      window.setTimeout(() => run(), 0);
    }
  };

  const loadPage = async () => {
    cancelPrefetch();
    await fetchRows(buildParams());
    applyRowTransform();
    pagination.total = total.value;
    const maxPage = Math.max(1, Math.ceil(pagination.total / pagination.pageSize));
    if (pagination.current > maxPage) pagination.current = maxPage;
    schedulePrefetch(maxPage);
  };

  const extractSorter = (sorter: any) => {
    if (!sorter) return null;
    const normalized = Array.isArray(sorter) ? sorter[0] : sorter;
    const field =
      normalized?.field || normalized?.columnKey || normalized?.dataIndex || normalized?.key;
    const orderRaw = normalized?.order || normalized?.sortOrder;
    if (!field || !orderRaw) return null;
    const order =
      orderRaw === 'ascend'
        ? 'asc'
        : orderRaw === 'descend'
        ? 'desc'
        : orderRaw === 'asc' || orderRaw === 'desc'
        ? orderRaw
        : null;
    if (!order) return null;
    return { field, order };
  };

  const handlePaginationUpdate = (p: any) => {
    if (p) Object.assign(pagination, p);
    loadPage();
  };

  const handleTableChange = (page?: any, _filters?: any, sorter?: any) => {
    if (page) Object.assign(pagination, page);
    const s = extractSorter(sorter);
    if (s) {
      sortBy.value = s.field;
      sortOrder.value = s.order;
      pagination.current = 1;
    } else {
      sortBy.value = '';
      sortOrder.value = 'asc';
    }
    loadPage();
  };

  const handleSorterChange = (_page?: any, _filters?: any, sorter?: any) => {
    const s = extractSorter(sorter);
    if (!s) return;
    sortBy.value = s.field;
    sortOrder.value = s.order;
    pagination.current = 1;
    loadPage();
  };

  const watchSearch = (extra?: () => Promise<void> | void) => {
    let timer: number | null = null;
    return watch([searchText, searchColumn], () => {
      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(async () => {
        pagination.current = 1;
        await loadPage();
        if (extra) await extra();
      }, debounceMs);
    });
  };

  return {
    rows,
    total,
    loading,
    error,
    fetchStats,
    searchText,
    searchColumn,
    tableSize,
    pagination,
    sortBy,
    sortOrder,
    loadPage,
    handlePaginationUpdate,
    handleTableChange,
    handleSorterChange,
    watchSearch
  };
}
