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
      <el-radio-group v-model="sizeValue" :disabled="disabled">
        <el-radio-button value="small">{{ sizeLabels.small }}</el-radio-button>
        <el-radio-button value="default">{{ sizeLabels.default }}</el-radio-button>
        <el-radio-button value="large">{{ sizeLabels.large }}</el-radio-button>
      </el-radio-group>
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
import { computed } from 'vue';
import { ElRadioGroup, ElRadioButton, ElSelect, ElOption } from 'element-plus';
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
      small: 'Small Size',
      default: 'Default Size',
      large: 'Large Size'
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
}
</style>
