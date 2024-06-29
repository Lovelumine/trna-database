<template>
  <div class="site--main">
    <h2>Nonsense Sup-RNA</h2>
    <!-- 顶部行包含尺寸调整、搜索框和列选择 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
        <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
          <el-option :key="'all'" :label="'All columns'" :value="''" />
          <el-option v-for="column in allColumns" :key="column.key" :value="column.dataIndex" />
        </el-select>
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
    <div class="custom-tag-styles">
    <s-table-provider :hover="true" :locale="locale" >
      <s-table 
        :columns="displayedColumns" 
        :data-source="filteredDataSource" 
        :row-key="record => record.key" 
        :stripe="true" 
        :show-sorter-tooltip="true" 
        :size="tableSize" 
        :expand-row-by-click="true" 
        @sorter-change="onSorterChange"
        :loading="loading"
      >
        <template #bodyCell="{ text, column, record }">
          <template v-if="column.key === 'Structure of sup-tRNA'">
            <el-image style="width: 100px; height: 100px" :src="text" :preview-src-list="[text]" fit="cover" />
          </template>
          <template v-else-if="column.key === 'Stop codon for readthrough'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray(record['Stop codon for readthrough']) ? record['Stop codon for readthrough']: record['Stop codon for readthrough'].split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace>
          </template>
          <template v-else-if="column.key === 'Noncanonical charged amino acids'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids']: record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace>
          </template>
          <template v-else-if="column.key === 'Readthrough mechanism'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray( record['Readthrough mechanism']) ?  record['Readthrough mechanism'] :  record['Readthrough mechanism'].split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
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
            <p><b>Species ID:</b> {{ record['Species ID']}}</p>
            <p><b>Tissue/Organelle of Origin:</b> {{ record['Tissue/Organelle of Origin'] }}</p>
            <p><b>Anticodon before mutation:</b> {{ record['Anticodon before mutation'] }}</p>
            <p><b>Anticodon after mutation:</b> {{ record['Anticodon after mutation'] }}</p>
            <p><b>Stop codon for readthrough:</b> <ElSpace>
              <ElTag v-for="items in (Array.isArray(record['Stop codon for readthrough']) ? record['Stop codon for readthrough'] : record['Stop codon for readthrough'].split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace></p>
            <p><b>Noncanonical charged amino acids:</b> <ElSpace>
              <ElTag v-for="items in (Array.isArray(record['Noncanonical charged amino acids']) ? record['Noncanonical charged amino acids'] : record['Noncanonical charged amino acids'].split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace></p>
            <p><b>RNA central ID of tRNA:</b> {{ record['RNA central ID of tRNA'] }}</p>
            <p><b>tRNA sequence before mutation:</b> {{ record['tRNA sequence before mutation'] }}</p>
            <p><b>tRNA sequence after mutation:</b> <span v-html="highlightMutation(record['tRNA sequence after mutation'])"></span></p>

            <div>
              <b>Structure of sup-tRNA:</b>
              <img :src="`https://trna.lumoxuan.cn/src/assets/data/picture/${record.pictureid}.png`" @click="showLightbox(record.pictureid)" style="width: 100px; cursor: pointer;" />
            </div>
           <p><b>Readthrough mechanism:</b> <ElSpace>
              <ElTag v-for="items in (Array.isArray(record['Readthrough mechanism']) ? record['Readthrough mechanism'] : record['Readthrough mechanism'].split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace></p>
            <p><b>Mutational position of sup-tRNA:</b> {{ record['Mutational position of sup-tRNA'] }}</p>
            <p><b>PMID of references:</b> <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record['PMID of references']" target="_blank" class="tilt-hover">{{record['PMID of references']}}</a></p>
            <p><b>Notes:</b> {{ record['Notes'] }}</p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
    <vue-easy-lightbox :key="lightboxKey" :visible="visible" :imgs="lightboxImgs" :index="0" @hide="hideLightbox" />
  </div></div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed, nextTick } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElImage, ElSelect, ElOption } from 'element-plus';
import { STableProvider, STableProps  } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import VueEasyLightbox from 'vue-easy-lightbox';
import {highlightMutation} from '../../utils/highlightMutation.js'
import {getTagType} from '../../utils/tag.js'
import {processCSVData} from '../../utils/processCSVData.js'
import { sortData } from '../../utils/sort.js';
import axios from 'axios';

type DataType = {
  [key: string]: string | string[];
  key: string; 
  Species: string;
  'Anticodon before mutation': string;
  'Anticodon after mutation': string;
  'Stop codon for readthrough': string[];
  'Noncanonical charged amino acids': string[];
  'tRNA_sequence_before_mutation': string;
  'tRNA_sequence_after_mutation': string;
  'RNA central ID of tRNA':string;
  'Structure of sup-tRNA': string;
  'Readthrough mechanism': string;
  'Mutational position of sup-tRNA': string;
  'PMID': string;
  pictureid: string;
};

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'NaturalSupTRNA',
  components: {
    ElTooltip,
    ElImage,
    ElSelect,
    ElOption,
    VueEasyLightbox,
  },
  setup() {
    const { searchText, filteredDataSource: originalFilteredDataSource, searchColumn, loadData } = useTableData('/src/assets/data/Nonsense Sup-RNA.csv', (data) => {
      return processCSVData(data, ['Stop codon for readthrough', 'Noncanonical charged amino acids','Readthrough mechanism']);
    });

    const tableSize = ref('default');
    const selectedColumns = ref<string[]>(['Species', 'Stop Codon for Readthrough', 'Noncanonical charged amino acids','Readthrough mechanism']);
    const loading = ref(false);
    const dataSource = ref<DataType[]>([]);
    const sortedDataSource = ref<DataType[]>([]);

    onMounted(async () => {
      await loadData();
      dataSource.value = originalFilteredDataSource.value;
      sortedDataSource.value = originalFilteredDataSource.value;
      const style = document.createElement('style');
    style.innerHTML = `
    `;
    document.head.appendChild(style);
  
    });

    const visible = ref(false);
    const lightboxImgs = ref<string[]>([]);
    const lightboxKey = ref(0);

    const showLightbox = (pictureid: string) => {
      const imgUrl = `https://trna.lumoxuan.cn/src/assets/data/picture/${pictureid}.png`;
      lightboxImgs.value = [imgUrl];
      lightboxKey.value += 1;  // 更新key以重新渲染组件
      visible.value = true;
    };

    const hideLightbox = () => {
      visible.value = false;
    };

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Species', dataIndex: 'Species', width: 280, ellipsis: true, key: 'Species', resizable: true, sorter: true },
      { title: 'Species ID', dataIndex: 'Species ID', width: 280, ellipsis: true, key: 'Species ID', resizable: true, sorter: true },
      { title: 'Tissue/Organelle of Origin', dataIndex: 'Tissue/Organelle of Origin', width: 280, ellipsis: true, key: 'Tissue/Organelle of Origin', resizable: true, sorter: true },      
      { title: 'Anticodon before mutation', dataIndex: 'Anticodon before mutation', width: 180, ellipsis: true, key: 'Anticodon before mutation', resizable: true },
      { title: 'Anticodon after mutation', dataIndex: 'Anticodon after mutation', width: 180, ellipsis: true, key: 'Anticodon after mutation', resizable: true },
      { title: 'Stop codon for readthrough', dataIndex: 'Stop codon for readthrough', width: 240, ellipsis: true, key: 'Stop Codon for Readthrough', resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'UAG(amber)', value: 'UAG(amber)' },
            { text: 'UAA(ochre)', value: 'UAA(ochre)' },
            { text: 'UGA(opal)', value: 'UGA(opal)'},        
          ],
          onFilter:(value, record) => value.includes(record.Stop_codon_for_readthrough)|| record.Stop_codon_for_readthrough.includes(value)
        }
      },
      { title: 'RNA central ID of tRNA', dataIndex: 'RNA central ID of tRNA', width: 250, ellipsis: true, key: 'RNA central ID of tRNA', resizable: true,
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
          onFilter: (value, record) => value.includes(record.Noncanonical_charged_amino_acids)
        }
      },
      { title: 'Noncanonical charged amino acids', dataIndex: 'Noncanonical charged amino acids', width: 260, ellipsis: true, key: 'Noncanonical charged amino acids', resizable: true },
       { title: 'tRNA sequence before mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      { title: 'tRNA sequence after mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      { title: 'Readthrough mechanism', dataIndex: 'Readthrough mechanism', width: 280, ellipsis: true, key: 'Readthrough mechanism', resizable: true ,        filter: {
          type: 'multiple',
          list: [
            { text: 'a single base mutation in anticodon', value: 'a single base mutation in anticodon' },
            { text: 'recode/reassignment', value: 'recode/reassignment ' },
            { text: 'wobble/misread/mispair/mismatch', value: 'wobble/misread/mispair/mismatch' },
            { text: 'a base mutation outside the anticodon', value: 'a base mutation outside the anticodon' },
            { text: 'mischarge', value: 'mischarge' },
            { text: 'other', value: 'other' },
            { text: 'unknown', value: 'unknown' },
          ],
          onFilter: (value, record)=> value.includes(record['Readthrough mechanism'])
        }},
      { title: 'Mutational position of sup-tRNA', dataIndex: 'Mutational position of sup-tRNA', width: 250, ellipsis: true, key: 'Mutational position of sup-tRNA', resizable: true },
      { title: 'PMID of references', dataIndex: 'PMID', width: 150, ellipsis: true, key: 'PMID', customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID || '#'} target="_blank" class="bracket-links">{record.PMID}</a></div>), resizable: true },
      { title: 'Notes', dataIndex: 'Notes', width: 150, ellipsis: true, key: 'Notes', resizable: true }
    ];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );


    const onSorterChange = (params: any) => {
      let sorter: { field?: string, order?: 'ascend' | 'descend' } = {};
      if (Array.isArray(params)) {
        sorter = params[0];
      } else {
        sorter = params;
      }

      loading.value = true;
      const timer = setTimeout(() => {
        sortedDataSource.value = sortData(originalFilteredDataSource.value, sorter);
        loading.value = false;
        clearTimeout(timer);
      }, 300);
    };

    const filteredDataSource = computed(() => {
      if (!searchText.value) {
        return sortedDataSource.value;
      }
      return sortedDataSource.value.filter(record => {
        if (!searchColumn.value) {
          return Object.values(record).some(val => String(val).toLowerCase().includes(searchText.value.toLowerCase()));
        }
        return String(record[searchColumn.value]).toLowerCase().includes(searchText.value.toLowerCase());
      });
    });

    const secondaryStructures = ref<{ [key: string]: string }>({});

    return {
      allColumns,
      displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      highlightMutation,
      visible,
      lightboxKey,
      lightboxImgs,
      showLightbox,
      hideLightbox,
      getTagType, // 获取标签类型
      onSorterChange,
      loading
    };
  }
});
</script>

<style>
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
