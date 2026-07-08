<template>
  <!-- 透传所有属性/事件/插槽，只把 pagination 换成“实例私有”的 -->
  <STable v-bind="forwardProps">
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps" />
    </template>
  </STable>
</template>

<script setup lang="ts">
import '@shene/table/dist/index.css'
import { computed, onBeforeUnmount, onMounted, reactive, ref, toRaw, watch, useAttrs } from 'vue'
import { STable } from '@shene/table'
import cloneDeep from 'lodash.clonedeep'

defineOptions({ inheritAttrs: false })

const attrs = useAttrs() as any
const compactViewport = ref(false)

let compactMediaQuery: MediaQueryList | null = null

const syncCompactViewport = () => {
  compactViewport.value = !!compactMediaQuery?.matches
}

onMounted(() => {
  compactMediaQuery = window.matchMedia('(max-width: 640px)')
  syncCompactViewport()
  compactMediaQuery.addEventListener('change', syncCompactViewport)
})

onBeforeUnmount(() => {
  compactMediaQuery?.removeEventListener('change', syncCompactViewport)
})

// 每个 s-table 实例一份独立的 pagination
const innerPagination = reactive({})

// 父层传入变化时，同步“拷贝”到私有 pagination（避免共享引用）
watch(
  () => attrs.pagination,
  (val) => {
    const src = val ? cloneDeep(toRaw(val)) : {}
    // 原地清空再赋值，保持响应式引用不变
    Object.keys(innerPagination).forEach(k => delete (innerPagination as any)[k])
    Object.assign(innerPagination, src)
  },
  { immediate: true, deep: true }
)

const compactNumericWidth = (width: number) => {
  if (width <= 72) return width
  if (width >= 640) return 260
  if (width >= 420) return 240
  if (width >= 260) return 220
  if (width >= 200) return 180
  return width
}

const compactWidth = (width: unknown) => {
  if (typeof width === 'number') return compactNumericWidth(width)
  if (typeof width !== 'string') return width

  const match = width.trim().match(/^(\d+(?:\.\d+)?)px$/)
  if (!match) return width

  return `${compactNumericWidth(Number(match[1]))}px`
}

const compactColumns = (columns: any[]): any[] => {
  return columns.map((column) => {
    const next = { ...column }
    if ('width' in next) next.width = compactWidth(next.width)
    if ('minWidth' in next) next.minWidth = compactWidth(next.minWidth)
    if (Array.isArray(next.children)) next.children = compactColumns(next.children)
    return next
  })
}

const effectiveColumns = computed(() => {
  const columns = attrs.columns
  if (!compactViewport.value || !Array.isArray(columns)) return columns
  return compactColumns(columns)
})

const effectivePagination = computed(() => {
  if (!compactViewport.value) return innerPagination

  return {
    ...innerPagination,
    showQuickJumper: false,
    showLessItems: true,
    size: 'small'
  }
})

// 透传其余属性/事件，仅替换 pagination
const forwardProps = computed(() => {
  const { pagination: _omitPagination, columns: _omitColumns, ...rest } = attrs
  return {
    ...rest,
    ...(effectiveColumns.value ? { columns: effectiveColumns.value } : {}),
    pagination: effectivePagination.value
  }
})
</script>

<style scoped>
@media (max-width: 640px) {
  :deep(.s-table) {
    --s-pagination-button-width: 28px;
    --s-pagination-button-height: 28px;
    font-size: 13px;
  }

  :deep(.s-table__body) {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  :deep(.s-table__cell-inner .s-table__cell-content) {
    padding: 10px 8px;
    line-height: 1.35;
  }

  :deep(.s-table__header-cell-title-inner) {
    line-height: 1.25;
  }

  :deep(.s-table__pagination) {
    justify-content: flex-start !important;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  :deep(.s-pagination) {
    min-width: max-content;
    flex-wrap: nowrap;
    font-size: 12px;
  }

  :deep(.s-pagination__item),
  :deep(.s-pagination__prev),
  :deep(.s-pagination__next),
  :deep(.s-pagination__jump-prev),
  :deep(.s-pagination__jump-next) {
    margin-right: 4px;
  }

  :deep(.s-pagination__options) {
    margin: 0 4px;
  }

  :deep(.s-pagination__options-quick-jumper) {
    display: none;
  }
}
</style>
