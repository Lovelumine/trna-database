<template>
  <div class="site--main">
    <h2>Natural Sup-tRNA</h2>
    <!-- 顶部行包含尺寸调整、搜索框和列选择 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box" style="margin-bottom: 10px">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
      </div>
      <!-- 调整尺寸 -->
      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize">
          <el-radio-button value="small">Small Size</el-radio-button>
          <el-radio-button value="default">Default Size</el-radio-button>
          <el-radio-button value="large">Large Size</el-radio-button>
        </el-radio-group>
      </div>
      <!-- 选择显示列 -->
      <div class="column-controls" style="margin-bottom: 10px">
        <el-select v-model="selectedColumns" multiple placeholder="Select columns to display" collapse-tags class="column-select">
          <el-option v-for="column in allColumns" :key="column.key" :label="column.title as string" :value="column.key" />
        </el-select>
      </div>
    </div>
    <!-- 表格组件 -->
    <s-table-provider :hover="true" :locale="locale">
      <s-table :columns="displayedColumns" :data-source="filteredDataSource" :row-key="record => record.key" :stripe="true" :show-sorter-tooltip="true" :size="tableSize" :expand-row-by-click="true">
        <template #bodyCell="{ text, column, record }">
          <template v-if="column.key === 'Structure of sup-tRNA'">
            <el-image style="width: 100px; height: 100px" :src="text" :preview-src-list="[text]" fit="cover" />
          </template>
          <template v-else-if="column.key === 'Stopcodonforreadthrough'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray(record.Stopcodonforreadthrough) ? record.Stopcodonforreadthrough : record.Stopcodonforreadthrough.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace>
          </template>
          <template v-else-if="column.key === 'NoncanonicalChargedAminoAcids'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray(record.NoncanonicalChargedAminoAcids) ? record.NoncanonicalChargedAminoAcids : record.NoncanonicalChargedAminoAcids.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace>
          </template>
          <template v-else>
            <span>{{ text }}</span>
          </template>
        </template>

        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Species:</b> {{ record.Species }}</p>
            <p><b>Anticodon before mutation:</b> {{ record['Anticodon before mutation'] }}</p>
            <p><b>Anticodon after mutation:</b> {{ record['Anticodon after mutation'] }}</p>
            <p><b>Stop codon for readthrough:</b>              <ElSpace>
                <ElTag v-for="items in (Array.isArray(record.Stopcodonforreadthrough) ? record.Stopcodonforreadthrough : record.Stopcodonforreadthrough.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                  {{ items }}
                </ElTag>
              </ElSpace></p>
            <p><b>Noncanonical charged amino acids:</b> <ElSpace>
                <ElTag v-for="items in (Array.isArray(record.NoncanonicalChargedAminoAcids) ? record.NoncanonicalChargedAminoAcids : record.NoncanonicalChargedAminoAcids.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                  {{ items }}
                </ElTag>
              </ElSpace></p>
            <p><b>tRNA sequence before mutation:</b> {{ record['tRNA sequence before mutation'] }}</p>
            <p><b>tRNA sequence after  mutation:</b> <span v-html="highlightMutation(record['tRNA sequence after mutation'])"></span></p>
            <div>
              <b>Structure of sup-tRNA:</b>
              <img :src="`https://trna.lumoxuan.cn/data/picture/${record.pictureid}.png`" @click="showLightbox(record.pictureid)" style="width: 100px; cursor: pointer;" />
            </div>
            <p><b>Readthrough mechanism:</b> {{ record['Readthrough mechanism'] }}</p>
            <p><b>Mutational position of sup-tRNA:</b> {{ record['Mutational position of sup-tRNA'] }}</p>
            <p><b>PMID of references:</b> {{ record['PMID of references'] }}</p>
            <p><b>Note:</b> {{ record['Note'] }}</p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
    <vue-easy-lightbox :key="lightboxKey" :visible="visible" :imgs="lightboxImgs" :index="0" @hide="hideLightbox" />
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import VueEasyLightbox from 'vue-easy-lightbox';
import {highlightMutation} from '../../utils/highlightMutation.js'
import {getTagType} from '../../utils/tag.js'
import {processCSVData} from '../../utils/processCSVData.js'

type DataType = {
  [key: string]: string | string[];
  Species: string;
  'Anticodon before mutation': string;
  'Anticodon after mutation': string;
  'Stop codon for readthrough': string[];
  'Noncanonical charged amino acids': string[];
  'tRNA sequence before mutation': string;
  'tRNA sequence after mutation': string;
  'Structure of sup-tRNA': string;
  'Readthrough mechanism': string;
  'Mutational position of sup-tRNA': string;
  'PMID of references': string;
  pictureid: string;
};

import en from '@shene/table/dist/locale/en';
import { dataType } from 'element-plus/es/components/table-v2/src/common.js';
const locale = ref(en);

export default defineComponent({
  name: 'NaturalSupTRNA',
  components: {
    ElTooltip,
    ElImage,
    ElSelect,
    ElOption,
    VueEasyLightbox
  },
  setup() {
    const { searchText, filteredDataSource, loadData } = useTableData('/data/natural-sup-tRNA.csv', (data) => {
      return processCSVData(data, ['Stopcodonforreadthrough', 'NoncanonicalChargedAminoAcids']);
    });

    console.log();

    const tableSize = ref('default');
    const selectedColumns = ref<string[]>(['Species', 'Anticodon before mutation', 'Anticodon after mutation', 'Stopcodonforreadthrough','Mutational position of sup-tRNA']);


    onMounted(() => {
      loadData();
    });
    
    const visible = ref(false);
    const lightboxImgs = ref<string[]>([]);
    const lightboxKey = ref(0);


    const showLightbox = (pictureid: string) => {
      const imgUrl = `https://trna.lumoxuan.cn/data/picture/${pictureid}.png`;
      lightboxImgs.value = [imgUrl];
      lightboxKey.value += 1;  // 更新key以重新渲染组件
      visible.value = true;
    };

    const hideLightbox = () => {
      visible.value = false;
    };

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Species', dataIndex: 'Species', width: 150, ellipsis: true, key: 'Species', resizable: true },
      { title: 'Anticodon before mutation', dataIndex: 'Anticodon before mutation', width: 180, ellipsis: true, key: 'Anticodon before mutation', resizable: true },
      { title: 'Anticodon after mutation', dataIndex: 'Anticodon after mutation', width: 180, ellipsis: true, key: 'Anticodon after mutation', resizable: true },
      { title: 'Stop codon for readthrough', dataIndex: 'Stopcodonforreadthrough', width: 200, ellipsis: true, key: 'Stopcodonforreadthrough', resizable: true ,
      filter: {
          type: 'multiple',
          list: [
            { text: 'UAG(amber)', value: 'UAG(amber)' },
            { text: 'UAA(ochre)', value: 'UAA(ochre)' },
            { text: 'UGA(opal)', value: 'UGA(opal)'},        
          ],
          onFilter: (value, record) => record.Stopcodonforreadthrough.includes(value)
        },
      },
      { title: 'Noncanonical charged amino acids', dataIndex: 'NoncanonicalChargedAminoAcids', width: 150, ellipsis: true, key: 'NoncanonicalChargedAminoAcids', resizable: true,
      filter: {
          type: 'multiple',
          list: [
            { text: 'Ser', value: 'Ser' },
            { text: 'Gln', value: 'Gln' },
            { text: 'Trp', value: 'Trp' },
            { text: 'Tyr', value: 'Tyr' },
            { text: 'Leu', value: 'Leu' },
            { text: 'Arg', value: 'Arg' },
            { text: 'Gly', value: 'Gly' },
            { text: 'Pro', value: 'Pro' },
            { text: 'Glu', value: 'Glu' },
            { text: 'Sec', value: 'Sec' },       
            { text: 'Cys', value: 'Cys' },
            { text: 'Pyl', value: 'Pyl' },
          ],
          onFilter: (value, record) => record.NoncanonicalChargedAminoAcids.includes(value)
        },
       },
      { title: 'tRNA sequence before mutation', dataIndex: 'tRNA sequence before mutation', width: 200, ellipsis: true, key: 'tRNA sequence before mutation', resizable: true },
      { title: 'tRNA sequence after mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      { title: 'Readthrough mechanism', dataIndex: 'Readthrough mechanism', width: 200, ellipsis: true, key: 'Readthrough mechanism', resizable: true },
      { title: 'Mutational position of sup-tRNA', dataIndex: 'Mutational position of sup-tRNA', width: 250, ellipsis: true, key: 'Mutational position of sup-tRNA', resizable: true },
      { title: 'PMID of references', dataIndex: 'PMID of references', width: 150, ellipsis: true, key: 'PMID of references', resizable: true },
      { title: 'Note', dataIndex: 'Note', width: 150, ellipsis: true, key: 'Note', resizable: true }
    ];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    return {
      allColumns,
      displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      locale,
      selectedColumns,
      highlightMutation,
      visible,
      lightboxKey,
      lightboxImgs,
      showLightbox,
      hideLightbox,
      getTagType // 获取标签类型
    };
  }
});
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  flex-grow: 1;
  margin-right: 10px;
}

.size-controls,
.column-controls {
  display: flex;
  align-items: center;
}

.column-select {
  margin-left: 10px;
  width: 200px;
}
</style>
