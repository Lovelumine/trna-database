import { ref, watch } from 'vue';
import { createPagination } from './table';
import type { SortOrder, MysqlTableFilter } from './useMysqlTableData';
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

export function useTableData(table: string, options: ServerTableOptions = {}) {
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
  const searchValues = ref<string[]>([]);
  const filters = ref<MysqlTableFilter[]>([]);
  const sortBy = ref(initialSortBy);
  const sortOrder = ref<SortOrder>(initialSortOrder);
  const pagination = createPagination();
  if (pageSize) pagination.pageSize = pageSize;

  const applyQueryParams = () => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const tableParam = params.get('table');
    if (tableParam && tableParam !== table) return;

    const columnParam =
      params.get('search_column') || params.get('searchColumn') || params.get('column') || '';
    const textParam =
      params.get('search_text') || params.get('searchText') || params.get('text') || '';
    const idParam = params.get('id') || '';

    if (idParam && !textParam) {
      searchColumn.value = 'id';
      searchText.value = idParam;
    } else {
      if (columnParam) searchColumn.value = columnParam;
      if (textParam) searchText.value = textParam;
    }

    const pageParam = params.get('page');
    const pageSizeParam = params.get('page_size') || params.get('pageSize');
    const sortByParam = params.get('sort_by') || params.get('sortBy');
    const sortOrderParam = params.get('sort_order') || params.get('sortOrder');

    if (pageParam) {
      const pageNumber = Number.parseInt(pageParam, 10);
      if (Number.isFinite(pageNumber) && pageNumber > 0) {
        pagination.current = pageNumber;
      }
    }
    if (pageSizeParam) {
      const pageSizeNumber = Number.parseInt(pageSizeParam, 10);
      if (Number.isFinite(pageSizeNumber) && pageSizeNumber > 0) {
        pagination.pageSize = pageSizeNumber;
      }
    }
    if (sortByParam) sortBy.value = sortByParam;
    if (sortOrderParam === 'asc' || sortOrderParam === 'desc') {
      sortOrder.value = sortOrderParam;
    }
  };

  applyQueryParams();

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
    searchValues: searchValues.value,
    filters: filters.value,
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
    fetchRows,
    prefetchRange,
    cancelPrefetch,
    fetchStats,
    searchText,
    searchColumn,
    searchValues,
    filters,
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
