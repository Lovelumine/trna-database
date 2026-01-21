<template>
    <div class="alignment-wrappers" :class="{ 'alignment-dark': isDark }">
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
  import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
  
  interface AlignmentItem {
    id: string;
    base: string;
    sup_base: string;
  }
  
  const props = defineProps<{
    alignmentData: AlignmentItem[];
    chunkSize?: number;
  }>();

  const isDark = ref(false);
  let themeObserver: MutationObserver | null = null;
  const media = window.matchMedia('(prefers-color-scheme: dark)');

  const syncTheme = () => {
    const root = document.documentElement;
    const explicit = root.getAttribute('data-theme');
    isDark.value = explicit === 'dark' || (!explicit && root.classList.contains('dark')) || (!explicit && media.matches);
  };

  onMounted(() => {
    syncTheme();
    themeObserver = new MutationObserver(syncTheme);
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });
    if ('addEventListener' in media) {
      media.addEventListener('change', syncTheme);
    } else if ('addListener' in media) {
      media.addListener(syncTheme);
    }
  });

  onBeforeUnmount(() => {
    themeObserver?.disconnect();
    themeObserver = null;
    if ('removeEventListener' in media) {
      media.removeEventListener('change', syncTheme);
    } else if ('removeListener' in media) {
      media.removeListener(syncTheme);
    }
  });

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
  --alignment-border: var(--app-border);
  --alignment-label-bg: var(--app-surface-2);
  --alignment-cell-bg: transparent;
  --alignment-table-bg: var(--app-surface);
  --alignment-text: var(--app-text);
  --alignment-match-bg: #C8E6C9;
  --alignment-mismatch-bg: #FFCDD2;
  --alignment-insertion-bg: #BBDEFB;
  --alignment-deletion-bg: #FFE0B2;
}
.alignment-table {
  border-collapse: collapse;
  margin: 8px 0;
  font-family: monospace;
  table-layout: fixed;
  background: var(--alignment-table-bg);
}
.alignment-table th,
.alignment-table td {
  border: 1px solid var(--alignment-border);
  padding: 2px 4px;
  text-align: center;
  white-space: nowrap;
  font-size: 12px;
  color: var(--alignment-text);
}
.alignment-table td {
  background: var(--alignment-cell-bg);
}
.label-cell {
  background: var(--alignment-label-bg);
  font-weight: bold;
}
.alignment-table td.match {
  background-color: var(--alignment-match-bg);
}
.alignment-table td.mismatch {
  background-color: var(--alignment-mismatch-bg);
}
.alignment-table td.insertion {
  background-color: var(--alignment-insertion-bg);
}
.alignment-table td.deletion {
  background-color: var(--alignment-deletion-bg);
}

@media (prefers-color-scheme: dark) {
  .alignment-wrappers {
    --alignment-border: #2a3343;
    --alignment-label-bg: #1a2232;
    --alignment-cell-bg: #0f172a;
    --alignment-table-bg: #0b1220;
    --alignment-text: #e5e7eb;
    --alignment-match-bg: #183828;
    --alignment-mismatch-bg: #4a1f1f;
    --alignment-insertion-bg: #1b2a45;
    --alignment-deletion-bg: #4b2f1b;
  }
}

:global(:root[data-theme="dark"]) .alignment-wrappers {
  --alignment-border: #2a3343;
  --alignment-label-bg: #1a2232;
  --alignment-cell-bg: #0f172a;
  --alignment-table-bg: #0b1220;
  --alignment-text: #e5e7eb;
  --alignment-match-bg: #183828;
  --alignment-mismatch-bg: #4a1f1f;
  --alignment-insertion-bg: #1b2a45;
  --alignment-deletion-bg: #4b2f1b;
}

:global(html.dark) .alignment-wrappers {
  --alignment-border: #2a3343;
  --alignment-label-bg: #1a2232;
  --alignment-cell-bg: #0f172a;
  --alignment-table-bg: #0b1220;
  --alignment-text: #e5e7eb;
  --alignment-match-bg: #183828;
  --alignment-mismatch-bg: #4a1f1f;
  --alignment-insertion-bg: #1b2a45;
  --alignment-deletion-bg: #4b2f1b;
}

.alignment-wrappers.alignment-dark {
  --alignment-border: #2a3343;
  --alignment-label-bg: #1a2232;
  --alignment-cell-bg: #0f172a;
  --alignment-table-bg: #0b1220;
  --alignment-text: #e5e7eb;
  --alignment-match-bg: #183828;
  --alignment-mismatch-bg: #4a1f1f;
  --alignment-insertion-bg: #1b2a45;
  --alignment-deletion-bg: #4b2f1b;
}
  </style>
