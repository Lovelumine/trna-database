// utils/table.ts
import { reactive } from 'vue';

export interface EnsurePagination {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  pageSizeOptions?: string[]; // ← 改成 string[]
}

export const DEFAULT_PAGINATION: EnsurePagination = {
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  pageSizeOptions: ['10','20','50','100'] // ← 用字符串
};

export function createPagination(overrides: Partial<EnsurePagination> = {}) {
  return reactive<EnsurePagination>({ ...DEFAULT_PAGINATION, ...overrides });
}