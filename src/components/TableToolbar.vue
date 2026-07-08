<template>
  <div class="table-toolbar">
    <div class="table-toolbar__search">
      <TableSearchBar
        v-model="searchValue"
        v-model:column="searchColumnValue"
        :columns="searchColumns"
        :placeholder="searchPlaceholder"
        :column-placeholder="searchColumnPlaceholder"
        :disabled="disabled"
      />
    </div>

    <div v-if="showSizeControl" class="table-toolbar__size">
      <el-segmented v-model="sizeValue" :options="sizeOptions" :disabled="disabled" />
    </div>

    <div v-if="showColumnsControl" class="table-toolbar__columns">
      <el-select
        v-model="selectedColumnsValue"
        multiple
        collapse-tags
        :placeholder="columnSelectPlaceholder"
        class="table-toolbar__column-select"
        :disabled="disabled"
      >
        <el-option
          v-for="column in columnOptions"
          :key="column.key"
          :label="column.label"
          :value="column.value"
        />
      </el-select>
    </div>

    <div v-if="$slots.actions" class="table-toolbar__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import 'element-plus/dist/index.css';
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { ElSegmented, ElSelect, ElOption } from 'element-plus';
import TableSearchBar from '@/components/TableSearchBar.vue';

type ColumnLike = {
  key?: string | number;
  title?: string;
  dataIndex?: string;
  label?: string;
  value?: string | number;
};

type SizeLabels = {
  small: string;
  default: string;
  large: string;
};

const props = withDefaults(
  defineProps<{
    modelValue: string;
    column: string;
    searchColumns: ColumnLike[];
    size?: 'small' | 'default' | 'large';
    selectedColumns?: string[];
    displayColumns?: ColumnLike[];
    showSize?: boolean;
    showColumns?: boolean;
    disabled?: boolean;
    searchPlaceholder?: string;
    searchColumnPlaceholder?: string;
    columnSelectPlaceholder?: string;
    sizeLabels?: SizeLabels;
  }>(),
  {
    size: 'default',
    selectedColumns: () => [],
    displayColumns: undefined,
    showSize: true,
    showColumns: undefined,
    disabled: false,
    searchPlaceholder: 'Enter search content',
    searchColumnPlaceholder: 'Select column to search',
    columnSelectPlaceholder: 'Select columns to display',
    sizeLabels: () => ({
      small: 'Compact',
      default: 'Comfortable',
      large: 'Spacious'
    })
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'update:column', value: string): void;
  (e: 'update:size', value: 'small' | 'default' | 'large'): void;
  (e: 'update:selectedColumns', value: string[]): void;
}>();

const searchValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const searchColumnValue = computed({
  get: () => props.column,
  set: (value) => emit('update:column', value)
});

const sizeValue = computed({
  get: () => props.size,
  set: (value) => emit('update:size', value)
});

const selectedColumnsValue = computed({
  get: () => props.selectedColumns ?? [],
  set: (value) => emit('update:selectedColumns', value)
});

const columnOptions = computed(() => {
  const source = props.displayColumns ?? props.searchColumns ?? [];
  return source
    .map((column) => {
      const value =
        (column.key ?? column.dataIndex ?? column.value ?? '') as string | number;
      const label =
        (typeof column.title === 'string' && column.title) ||
        (typeof column.label === 'string' && column.label) ||
        String(column.dataIndex ?? column.key ?? '');
      return { key: String(value || label), label: String(label), value: String(value) };
    })
    .filter((option) => option.value !== '');
});

const showSizeControl = computed(() => props.showSize !== false);

const showColumnsControl = computed(() => {
  if (props.showColumns !== undefined) return props.showColumns;
  return Array.isArray(props.selectedColumns);
});

const compactViewport = ref(false);

let compactMediaQuery: MediaQueryList | null = null;

const syncCompactViewport = () => {
  compactViewport.value = !!compactMediaQuery?.matches;
};

onMounted(() => {
  compactMediaQuery = window.matchMedia('(max-width: 520px)');
  syncCompactViewport();
  compactMediaQuery.addEventListener('change', syncCompactViewport);
});

onBeforeUnmount(() => {
  compactMediaQuery?.removeEventListener('change', syncCompactViewport);
});

const sizeOptions = computed(() => {
  const compact = compactViewport.value;
  return [
    { label: compact ? 'Compact' : props.sizeLabels.small, value: 'small' },
    { label: compact ? 'Default' : props.sizeLabels.default, value: 'default' },
    { label: compact ? 'Large' : props.sizeLabels.large, value: 'large' }
  ];
});
</script>

<style scoped>
.table-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.table-toolbar__search {
  flex: 1;
  min-width: 260px;
}

.table-toolbar__size,
.table-toolbar__columns,
.table-toolbar__actions {
  display: flex;
  align-items: center;
}

.table-toolbar__column-select {
  min-width: 200px;
}

@media (max-width: 840px) {
  .table-toolbar {
    align-items: stretch;
  }

  .table-toolbar__search {
    min-width: 100%;
  }

  .table-toolbar__size,
  .table-toolbar__columns,
  .table-toolbar__actions {
    width: 100%;
  }

  .table-toolbar__size :deep(.el-segmented) {
    width: 100%;
  }

  .table-toolbar__size :deep(.el-segmented__item) {
    flex: 1 1 0;
    min-width: 0;
  }

  .table-toolbar__column-select {
    width: 100%;
    min-width: 100%;
  }
}

@media (max-width: 520px) {
  .table-toolbar {
    gap: 10px;
  }

  .table-toolbar__size :deep(.el-segmented) {
    --el-segmented-item-selected-bg-color: var(--app-accent);
    border-radius: 8px;
    padding: 2px;
    background: var(--app-surface-2);
  }

  .table-toolbar__size :deep(.el-segmented__item) {
    min-height: 34px;
  }

  .table-toolbar__size :deep(.el-segmented__item-label) {
    padding: 0 8px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
