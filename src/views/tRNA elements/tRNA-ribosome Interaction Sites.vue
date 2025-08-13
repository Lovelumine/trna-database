<template>
  <div class="ribosome-sites">
    <h3>tRNA–Ribosome Interaction Sites</h3>

    <!-- 术语与缩写说明 -->
    <el-alert
      class="legend-alert"
      type="info"
      :closable="false"
      show-icon
      title="Legend"
    >
      AC, anticodon; acc., acceptor; D loop, D stem, the dihydrouracil loop
      and stem of tRNA; T loop, T stem, the thymidine-containing loop and stem
      of tRNA. RNA contacts are indicated as follows: bk, backbone; bs, base;
      bp, base pair.
    </el-alert>

    <!-- 顶部控件：搜索、表格尺寸、列选择 -->
    <div class="top-controls">
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
        <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
          <el-option :key="'all'" :label="'All columns'" :value="''" />
          <el-option
            v-for="column in allColumns"
            :key="column.key"
            :value="column.dataIndex"
          />
        </el-select>
      </div>

      <div class="size-controls">
        <el-radio-group v-model="tableSize">
          <el-radio-button value="small">Small</el-radio-button>
          <el-radio-button value="default">Default</el-radio-button>
          <el-radio-button value="large">Large</el-radio-button>
        </el-radio-group>
      </div>

      <div class="column-controls">
        <el-select v-model="selectedColumns" multiple collapse-tags placeholder="Select columns" class="column-select">
          <el-option
            v-for="column in allColumns"
            :key="column.key"
            :label="typeof column.title === 'string' ? column.title : String(column.key)"
            :value="column.key"
          />
        </el-select>
      </div>
    </div>

    <!-- 表格 -->
    <s-table-provider :hover="true" :theme-color="'#00ACF5'" :locale="locale">
      <s-table
        :columns="columns"
        :data-source="filteredDataSource"
        :row-key="row => row.key || row['Site'] + '-' + row['Interaction'] + '-' + row['tRNA positions']"
        :stripe="true"
        :size="tableSize"
        :expand-row-by-click="true"
        :pagination="pagination"
      >
        <template #expandedRowRender="{ record }">
          <div class="expanded">
            <p><b>Site:</b> {{ record['site'] }}</p>
            <p><b>tRNA Region:</b> {{ record['tRNA region'] }}</p>
            <p><b>tRNA positions:</b> {{ record['tRNA positions'] }}</p>
            <p><b>Ribosome positions:</b> {{ record['Ribosome positions'] }}</p>
          </div>
        </template>
      </s-table>
    </s-table-provider>

    <!-- 图片：点击打开 Lightbox -->
    <div class="image-row">
      <button
        v-for="(src, i) in images"
        :key="src"
        class="img-wrap"
        type="button"
        :aria-label="`Open ${alts[i]}`"
        @click="open(i)"
      >
        <img :src="src" :alt="alts[i]" loading="lazy" />
      </button>
    </div>

    <vue-easy-lightbox
      :visible="lightbox.visible"
      :imgs="images"
      :index="lightbox.index"
      :loop="true"
      @hide="lightbox.visible = false"
    />
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { ElSelect, ElOption, ElRadioGroup, ElRadioButton, ElAlert } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import { pagination } from '../../utils/table';
import VueEasyLightbox from 'vue-easy-lightbox';

// 列配置（TSX 拆分）
import en from '@shene/table/dist/locale/en';
import { allColumns, selectedColumns } from './RibosomeInteractionColumns';

export default defineComponent({
  name: 'TrnaRibosomeInteractionSites',
  components: {
    ElSelect,
    ElOption,
    ElRadioGroup,
    ElRadioButton,
    ElAlert,
    VueEasyLightbox
  },
  setup() {
    const locale = ref(en);
    const tableSize = ref<'small'|'default'|'large'>('default');

    // 加载 CSV
    const { searchText, filteredDataSource, loadData, searchColumn } =
      useTableData('https://minio.lumoxuan.cn/ensure/tRNA_ribosome_interactions.csv');

    onMounted(async () => {
      await loadData();
      triggerColumnChange();
    });

    const triggerColumnChange = () => {
      selectedColumns.value = [...selectedColumns.value];
    };

    const columns = computed<STableColumnsType<any>>(() =>
      allColumns.filter(col => selectedColumns.value.includes(col.key as string))
    );

    // 图片 & lightbox
    const images = [
      'https://minio.lumoxuan.cn/ensure/elementpic/A-site.png',
      'https://minio.lumoxuan.cn/ensure/elementpic/P-site.png',
      'https://minio.lumoxuan.cn/ensure/elementpic/E-site.png'
    ];
    const alts = ['A-site', 'P-site', 'E-site'];
    const lightbox = ref({ visible: false, index: 0 });
    const open = (i: number) => {
      lightbox.value.index = i;
      lightbox.value.visible = true;
    };

    return {
      // table
      locale,
      tableSize,
      columns,
      filteredDataSource,
      searchText,
      searchColumn,
      allColumns,
      selectedColumns,
      triggerColumnChange,
      pagination,

      // images
      images,
      alts,
      lightbox,
      open
    };
  }
});
</script>

<style scoped>
.ribosome-sites { margin-top: 20px; }

/* 说明块样式 */
.legend-alert {
  margin: 8px 0 14px;
}

.top-controls {
  display: flex; gap: 12px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;
}
.search-box { display: flex; gap: 8px; align-items: center; }
.search-input { width: 260px; height: 32px; padding: 0 10px; border: 1px solid #ddd; border-radius: 6px; }
.search-column-select { width: 200px; }
.column-select { width: 260px; }

.expanded p { margin: 4px 0; }

/* 响应式网格：桌面3列、平板2列、手机1列 */
.image-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
}
@media (max-width: 1024px) {
  .image-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .image-row { grid-template-columns: 1fr; }
}
.img-wrap {
  display: block; width: 100%; aspect-ratio: 16/10; border: 1px dashed #ddd;
  border-radius: 8px; background: #fafafa; overflow: hidden; cursor: zoom-in; padding: 0;
}
.img-wrap img {
  width: 100%; height: 100%; object-fit: contain; display: block; padding: 8px;
}
.img-wrap:hover { border-color: #bbb; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
</style>