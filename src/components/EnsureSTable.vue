<template>
  <!-- 透传所有属性/事件/插槽，只把 pagination 换成“实例私有”的 -->
  <div ref="tableHostRef" class="ensure-table-host">
    <STable v-bind="forwardProps">
      <template v-for="(_, name) in $slots" #[name]="slotProps">
        <slot :name="name" v-bind="slotProps" />
      </template>
    </STable>
  </div>
</template>

<script setup lang="ts">
import '@shene/table/dist/index.css'
import { computed, onBeforeUnmount, onMounted, reactive, ref, toRaw, watch, useAttrs, useSlots } from 'vue'
import { STable } from '@shene/table'
import en from '@shene/table/dist/locale/en'
import cloneDeep from 'lodash.clonedeep'

defineOptions({ inheritAttrs: false })

const attrs = useAttrs() as any
const slots = useSlots()
const compactViewport = ref(false)
const tableHostRef = ref<HTMLElement | null>(null)
const tableHostWidth = ref(0)

let compactMediaQuery: MediaQueryList | null = null
let tableResizeObserver: ResizeObserver | null = null

const syncCompactViewport = () => {
  compactViewport.value = !!compactMediaQuery?.matches
}

onMounted(() => {
  compactMediaQuery = window.matchMedia('(max-width: 640px)')
  syncCompactViewport()
  compactMediaQuery.addEventListener('change', syncCompactViewport)
  if (tableHostRef.value) {
    tableResizeObserver = new ResizeObserver(([entry]) => {
      tableHostWidth.value = Math.round(entry?.contentRect.width || 0)
    })
    tableResizeObserver.observe(tableHostRef.value)
  }
})

onBeforeUnmount(() => {
  compactMediaQuery?.removeEventListener('change', syncCompactViewport)
  tableResizeObserver?.disconnect()
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

const numericWidth = (value: unknown) => {
  if (typeof value === 'number') return value
  if (typeof value !== 'string') return 0
  const match = value.trim().match(/^(\d+(?:\.\d+)?)px$/)
  return match ? Number(match[1]) : 0
}

const leafColumns = (columns: any[]): any[] =>
  columns.flatMap((column) => Array.isArray(column.children) && column.children.length
    ? leafColumns(column.children)
    : [column])

const scaleColumnWidths = (columns: any[], factor: number): any[] =>
  columns.map((column) => {
    const next = { ...column }
    if (Array.isArray(next.children) && next.children.length) {
      next.children = scaleColumnWidths(next.children, factor)
      return next
    }

    const width = numericWidth(next.width) || numericWidth(next.minWidth) || 140
    const fittedWidth = Math.round(width * factor)
    next.width = fittedWidth
    if ('minWidth' in next) next.minWidth = fittedWidth
    return next
  })

const hasExpandControl = computed(() =>
  'expandRowByClick' in attrs
  || 'expandedRowKeys' in attrs
  || 'onUpdate:expandedRowKeys' in attrs
  || Boolean(slots.expandedRowRender)
)

const fitDesktopColumns = (columns: any[]) => {
  // Expandable tables reserve 48px for the disclosure control; ordinary
  // tables do not. Treating every table as expandable left a false spacer in
  // publication tables and made their final columns look misaligned.
  const expandReserve = hasExpandControl.value ? 48 : 0
  const available = Math.max(tableHostWidth.value - expandReserve, 0)
  if (!available) return columns

  const leaves = leafColumns(columns)
  const declaredWidth = leaves.reduce((sum, column) =>
    sum + (numericWidth(column.width) || numericWidth(column.minWidth) || 140), 0)

  if (!declaredWidth) return columns
  // Keep the table edge aligned with the toolbar. The previous 1.28 cap left
  // narrower tables visibly short of the shared content boundary.
  const factor = Math.min(available / declaredWidth, 1.55)
  const requestedMinFactor = Number(attrs.fitMinFactor)
  const minimumFitFactor = Number.isFinite(requestedMinFactor)
    ? Math.min(1, Math.max(0.55, requestedMinFactor))
    : 0.82
  // A modest desktop shrink is preferable to a scrollbar caused by one
  // oversized text column. Very wide schemas still retain horizontal scroll.
  if (factor < minimumFitFactor || Math.abs(factor - 1) < 0.002) return columns

  const scaled = scaleColumnWidths(columns, factor)
  // Rounding each leaf independently can add 1–3px and trigger a scrollbar.
  // Correct against the actual target even when the growth cap is reached.
  const scaledLeaves = leafColumns(scaled)
  const scaledTotal = scaledLeaves.reduce((sum, column) =>
    sum + numericWidth(column.width || column.minWidth), 0)
  const last = scaledLeaves.at(-1)
  const lastWidth = numericWidth(last?.width || last?.minWidth)
  const targetWidth = Math.min(available, Math.round(declaredWidth * factor))
  const remainder = targetWidth - scaledTotal
  if (last && lastWidth && remainder) {
    last.width = lastWidth + remainder
    if ('minWidth' in last) last.minWidth = lastWidth + remainder
  }
  return scaled
}

const effectiveColumns = computed(() => {
  const columns = attrs.columns
  if (!Array.isArray(columns)) return columns
  if (compactViewport.value) return compactColumns(columns)
  return fitDesktopColumns(columns)
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
  const { pagination: _omitPagination, columns: _omitColumns, fitMinFactor: _omitFitMinFactor, ...rest } = attrs
  return {
    ...rest,
    locale: attrs.locale ?? en,
    ...(effectiveColumns.value ? { columns: effectiveColumns.value } : {}),
    pagination: effectivePagination.value
  }
})
</script>

<style scoped>
.ensure-table-host {
  width: 100%;
  min-width: 0;
}

@media (max-width: 640px) {
  :deep(.s-table) {
    --s-pagination-button-width: 28px;
    --s-pagination-button-height: 28px;
    font-size: 13px;
  }

  :deep(.s-table__body) {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
    scrollbar-color: var(--app-border) transparent;
    padding-bottom: 6px;
  }

  :deep(.s-table__body::-webkit-scrollbar) {
    height: 5px;
  }

  :deep(.s-table__body::-webkit-scrollbar-thumb) {
    border-radius: 999px;
    background: var(--app-border);
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

  :deep(.s-table__content) {
    position: relative;
    border-radius: 10px;
    border: 1px solid var(--app-border-light);
    overflow: hidden;
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
