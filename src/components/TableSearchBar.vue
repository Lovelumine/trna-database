<template>
  <div class="table-search" :class="{ 'is-disabled': disabled }">
    <span class="table-search__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" role="img" focusable="false">
        <path
          d="M10.5 3a7.5 7.5 0 0 1 5.9 12.1l3.75 3.75a1 1 0 0 1-1.4 1.42l-3.76-3.76A7.5 7.5 0 1 1 10.5 3Zm0 2a5.5 5.5 0 1 0 0 11a5.5 5.5 0 0 0 0-11Z"
        />
      </svg>
    </span>
    <input
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      class="table-search__input"
      type="search"
      aria-label="Search table"
      @input="onInput"
    />
    <button
      v-if="modelValue"
      class="table-search__clear"
      type="button"
      :disabled="disabled"
      aria-label="Clear search"
      @click="clearInput"
    >
      <span aria-hidden="true">×</span>
    </button>
    <span class="table-search__divider" aria-hidden="true"></span>
    <el-select
      :model-value="column"
      :placeholder="columnPlaceholder"
      :disabled="disabled"
      class="table-search__select"
      @update:model-value="onColumnChange"
    >
      <el-option v-if="showAll" key="__all" :label="allLabel" :value="allValue" />
      <el-option
        v-for="option in normalizedColumns"
        :key="option.key"
        :label="option.label"
        :value="option.value"
      />
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ElSelect, ElOption } from 'element-plus';

type ColumnLike = {
  key?: string | number;
  title?: string;
  dataIndex?: string;
  label?: string;
  value?: string | number;
};

const props = withDefaults(
  defineProps<{
    modelValue: string;
    column: string;
    columns: ColumnLike[];
    placeholder?: string;
    columnPlaceholder?: string;
    allLabel?: string;
    allValue?: string;
    showAll?: boolean;
    disabled?: boolean;
  }>(),
  {
    placeholder: 'Enter search content',
    columnPlaceholder: 'Select column to search',
    allLabel: 'All columns',
    allValue: '',
    showAll: true,
    disabled: false
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'update:column', value: string): void;
  (e: 'clear'): void;
}>();

const normalizedColumns = computed(() => {
  return (props.columns || [])
    .map((column) => {
      const value =
        (column.dataIndex ?? column.value ?? column.key ?? '') as string | number;
      const label =
        column.title ?? column.label ?? String(column.dataIndex ?? column.key ?? '');
      const key = column.key ?? value ?? label;
      return { key, label: String(label), value: String(value) };
    })
    .filter((option) => option.value !== '');
});

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
};

const onColumnChange = (value: string) => {
  emit('update:column', value);
};

const clearInput = () => {
  emit('update:modelValue', '');
  emit('clear');
};
</script>

<style scoped>
.table-search {
  display: flex;
  align-items: center;
  width: 100%;
  min-height: 38px;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  gap: 6px;
}

.table-search__icon {
  display: inline-flex;
  width: 18px;
  height: 18px;
  color: var(--app-text-muted);
}

.table-search__icon svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}

.table-search__input {
  flex: 1;
  border: 0;
  background: transparent;
  color: inherit;
  font-size: 14px;
  padding: 6px 4px;
  outline: none;
  min-width: 120px;
}

.table-search__input::placeholder {
  color: var(--app-text-faint);
}

.table-search__clear {
  border: 0;
  background: transparent;
  color: var(--app-text-muted);
  font-size: 18px;
  line-height: 1;
  padding: 0 6px;
  cursor: pointer;
}

.table-search__clear:hover {
  color: var(--app-text);
}

.table-search__divider {
  width: 1px;
  height: 22px;
  background: var(--app-border);
}

.table-search__select {
  min-width: 170px;
  max-width: 220px;
}

.table-search.is-disabled {
  opacity: 0.6;
  pointer-events: none;
}

:deep(.table-search__select .el-select__wrapper) {
  box-shadow: none;
  background: transparent;
  border: 0;
  padding: 0 6px;
}

:deep(.table-search__select .el-select__placeholder) {
  color: var(--app-text-faint);
}

:deep(.table-search__select .el-select__selected-item) {
  color: var(--app-text);
}

@media (max-width: 720px) {
  .table-search {
    flex-wrap: wrap;
    border-radius: 16px;
    padding: 6px 10px;
  }

  .table-search__divider {
    display: none;
  }

  .table-search__select {
    width: 100%;
    min-width: 100%;
  }
}
</style>
