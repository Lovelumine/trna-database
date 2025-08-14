<template>
  <!-- 透传所有属性/事件/插槽，只把 pagination 换成“实例私有”的 -->
  <STable v-bind="forwardProps" v-on="$attrs">
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps" />
    </template>
  </STable>
</template>

<script setup lang="ts">
import { computed, reactive, toRaw, watch, useAttrs } from 'vue'
import { STable } from '@shene/table'
import cloneDeep from 'lodash.clonedeep'

const attrs = useAttrs() as any

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

// 透传其余属性，仅替换 pagination
const forwardProps = computed(() => {
  const { pagination: _omit, ...rest } = attrs
  return { ...rest, pagination: innerPagination }
})
</script>