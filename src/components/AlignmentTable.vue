<template>
    <div class="alignment-wrappers">
      <table
        v-for="(chunk, index) in chunks"
        :key="index"
        class="alignment-table"
      >
        <tr>
          <th class="label-cell">ID</th>
          <td v-for="item in chunk" :key="item.id">{{ item.id }}</td>
        </tr>
        <tr>
          <th class="label-cell">Origin</th>
          <td
            v-for="item in chunk"
            :key="item.id + '_base'"
            :class="getType(item)"
          >
            {{ item.base }}
          </td>
        </tr>
        <tr>
          <th class="label-cell">sup-tRNA</th>
          <td
            v-for="item in chunk"
            :key="item.id + '_sup'"
            :class="getType(item)"
          >
            {{ item.sup_base }}
          </td>
        </tr>
      </table>
    </div>
  </template>
  
  <script lang="ts" setup>
  import { computed } from 'vue';
  
  interface AlignmentItem {
    id: string;
    base: string;
    sup_base: string;
  }
  
  const props = defineProps<{
    alignmentData: AlignmentItem[];
    chunkSize?: number;
  }>();
  
  // 默认每块显示 20 列，可通过 chunkSize 调整
  const size = props.chunkSize || 20;
  const chunks = computed(() => {
    const result: AlignmentItem[][] = [];
    for (let i = 0; i < props.alignmentData.length; i += size) {
      result.push(props.alignmentData.slice(i, i + size));
    }
    return result;
  });
  
  /**
   * Determine cell type based on base and sup_base values
   */
  const getType = (item: AlignmentItem): 'match' | 'mismatch' | 'insertion' | 'deletion' => {
    return item.base === '-' && item.sup_base !== '-'
      ? 'insertion'
      : item.base !== '-' && item.sup_base === '-'
        ? 'deletion'
        : item.base === item.sup_base
          ? 'match'
          : 'mismatch';
  };
  </script>
  
  <style scoped>
  .alignment-wrappers {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .alignment-table {
    border-collapse: collapse;
    margin: 8px 0;
    font-family: monospace;
    table-layout: fixed;
  }
  .alignment-table th,
  .alignment-table td {
    border: 1px solid #ddd;
    padding: 2px 4px;
    text-align: center;
    white-space: nowrap;
    font-size: 12px;
  }
  .label-cell {
    background: #f5f5f5;
    font-weight: bold;
  }
  .alignment-table td.match {
    background-color: #C8E6C9; /* 浅绿色 */
  }
  .alignment-table td.mismatch {
    background-color: #FFCDD2; /* 浅红色 */
  }
  .alignment-table td.insertion {
    background-color: #BBDEFB; /* 浅蓝色 */
  }
  .alignment-table td.deletion {
    background-color: #FFE0B2; /* 浅橙色 */
  }
  </style>