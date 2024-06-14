<template>
    <div class="site--main">
      <div class="top-controls">
        <div class="search-box" style="margin-bottom: 10px">
          <input v-model="searchText" placeholder="Enter search content" class="search-input">
        </div>
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
          <el-option
            v-for="column in allColumns"
            :key="column.key"
            :label="column.title as string"
            :value="column.key"
          />
        </el-select>
      </div>
      </div>
      <s-table-provider :hover="true" :locale="locale">
        <s-table
          :columns="columns"
          :data-source="filteredDataSource"
          :row-key="record => record.key"
          :stripe="true"
          :show-sorter-tooltip="true"
          :size="tableSize"
          :expand-row-by-click="true"
        >
          <template #bodyCell="{ text, column, record }">
            <template v-if="column.key === 'Citation'">
              <a>{{ text }}</a>
            </template>
            <template v-else-if="column.key === 'Related_disease'">
              <ElSpace>
                <ElTag v-for="item in record.Related_disease.split(';').map(str => str.trim())" :key="item" :type="item === 'cystic fibrosis' ? 'danger' : item === 'Model protein' ? 'info' : 'success'">
                  {{ item }}
                </ElTag>
              </ElSpace>
            </template>
          </template>
          <template #expandedRowRender="{ record }">
            <div>
              <p><b>Pathogenic Gene:</b> {{ record.Pathogenic_gene }}</p>
              <p><b>PTC Model:</b> {{ record.PTC_model }}</p>
              <p><b>Species Source of PTC Model:</b> {{ record.Species_source_of_PTC_model }}</p>
              <p><b>Sequence of PTC Model:</b> {{ record.Sequence_of_PTC_model }}</p>
              <p><b>PTC Site:</b> {{ record.PTC_site }}</p>
              <p><b>Origin AA and Codon of PTC Site:</b> {{ record.Origin_aa_and_codon_of_PTC_site }}</p>
              <p><b>PTC Codon:</b> {{ record.PTC_codon }}</p>
              <p><b>Delivery as Vector or IVT tRNA:</b> {{ record.Delivery_as_vector_or_IVT_tRNA }}</p>
              <p><b>Delivery Method:</b> {{ record.Delivery_method }}</p>
              <p><b>Supplenmentary Information of Delivery:</b>{{ record.Supplenmentary_information_of_delivery }}</p>
              <p><b>AA and Anticodon of Origin tRNA:</b> {{ record.aa_and_anticodon_of_origin_tRNA }}</p>
              <p><b>AA and Anticodon of Sup-tRNA:</b> {{ record.aa_and_anticodon_of_sup_tRNA }}</p>
              <p><b>Rnacentralc ID of Origin tRNA:</b>{{ record.rnacentral_ID_of_origin_tRNA }}</p>
              <p><b>tRNAscan-SE ID of Origin tRNA:</b>{{ record.rnacentral_ID_of_origin_tRNA }}</p>
              <p><b>Species Source of Origin tRNA:</b>{{ record.rnacentral_ID_of_origin_tRNA }}</p>
              <p><b>Sequence of Origin tRNA:</b>{{ record.Sequence_of_origin_tRNA }}</p>
              <p><b>Sequence of Sup-tRNA:</b>{{ record.Sequence_of_sup_tRNA}}</p>
              <p><b>Alignment:</b><pre>{{ record.Alignment}}</pre></p>
              <p><b>E-Value:</b>{{ record.E_Value }}</p>
              <p><b>Score:</b>{{ record.Score }}</p>
              <p><b>Identities:</b>{{ record.Identities }}</p>
              <p><b>Gaps:</b>{{ record.Gaps }}</p>
              <p><b>Ref Length:</b> {{ record.Ref_length }}</p>
              <p><b>Engineered aaRS:</b> {{ record.Engineered_aaRS }}</p>
              <p><b>Reading Through Efficiency:</b> {{ record.Reading_through_efficiency }}</p>
              <p><b>Measuring of Efficiency:</b> {{ record.Measuring_of_efficiency }}</p>
              <p><b>Supplementary Information of Measurement:</b> {{ record.Supplenmentary_information_of_Measurement }}</p>
              <p><b>Reaction System:</b> {{ record.Reaction_system }}</p>
              <p><b>Safety:</b> {{ record.Safety }}</p>
              <p><b>Immunogenicity:</b> {{ record.Immunogenicity }}</p>
              <p><b>Investigation:</b> {{ record.Investigation }}</p>
              <p><b>Citation:</b> {{ record.Citation }}</p>
              <p><b>notes:</b>{{ record.notes }}</p>
            </div>
          </template>
        </s-table>
      </s-table-provider>
    </div>
  </template>
  
  <script lang="tsx">
  import { defineComponent, ref, onMounted, computed } from 'vue';
  import { ElTag, ElSpace, ElSelect, ElOption  } from 'element-plus';
  import { STableProvider } from '@shene/table';
  import type { STableColumnsType } from '@shene/table';
  import { useTableData } from '../../assets/js/useTableData.js';
  
  type DataType = { [key: string]: string };
  
  import en from '@shene/table/dist/locale/en'
  const locale = ref(en)

  export default defineComponent({
    name: 'TRNATherapeutics-1',
    components: {
    ElTag,
    ElSpace,
    ElSelect,
    ElOption
  },
    setup() {
      const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNAtherapeutics.csv');
  
      const tableSize = ref('default');
      const selectedColumns = ref<string[]>([
      'Related_disease',
      'PTC_model',
      'Species_source_of_PTC_model',
      'Sequence_of_PTC_model',
      'Reaction_system',
    ]);
  
      onMounted(() => {
        loadData();
      });
  
      const allColumns: STableColumnsType<DataType> = [
        { title: 'Related Disease', dataIndex: 'Related_disease', width: 200, ellipsis: true, key: 'Related_disease', 
        filter: {
          type: 'multiple',
          list: [
            { text: 'cystic fibrosis', value: 'cystic fibrosis' },
            { text: 'Model protein', value: 'Model protein' },
            { text: 'primary ciliary dyskinesia (PCD)', value: 'primary ciliary dyskinesia (PCD)'},
            { text: 'Xeroderma pigmentosum', value: 'Xeroderma pigmentosum'},         
          ],
          onFilter: (value, record) => value.includes(record.Related_disease)
        },
        resizable: true },
        { title: 'Pathogenic Gene', dataIndex: 'Pathogenic_gene', width: 150, ellipsis: true, key: 'Pathogenic_gene', resizable: true },
        { title: 'PTC Model', dataIndex: 'PTC_model', width: 100, ellipsis: true, key: 'PTC_model', resizable: true },
        { title: 'Species Source of PTC Model', dataIndex: 'Species_source_of_PTC_model', width: 220, ellipsis: true, key: 'Species_source_of_PTC_model', resizable: true },
        { title: 'Sequence of PTC Model', dataIndex: 'Sequence_of_PTC_model', width: 280, ellipsis: true, key: 'Sequence_of_PTC_model', resizable: true },
        { title: 'PTC Site', dataIndex: 'PTC_site', width: 150, ellipsis: true, key: 'PTC_site', resizable: true },
        { title: 'Origin AA and Codon of PTC Site', dataIndex: 'Origin_aa_and_codon_of_PTC_site', width: 200, ellipsis: true, key: 'Origin_aa_and_codon_of_PTC_site', resizable: true },
        { title: 'PTC Codon', dataIndex: 'PTC_codon', width: 100, ellipsis: true, key: 'PTC_codon', resizable: true },
        { title: 'Delivery as Vector or IVT tRNA', dataIndex: 'Delivery_as_vector_or_IVT_tRNA', width: 200, ellipsis: true, key: 'Delivery_as_vector_or_IVT_tRNA', resizable: true },
        { title: 'Delivery Method', dataIndex: 'Delivery_method', width: 150, ellipsis: true, key: 'Delivery_method', resizable: true },
        { title: 'Supplenmentary_information_of_delivery', dataIndex: 'Supplenmentary_information_of_delivery', width: 100, ellipsis: true, key: 'Supplenmentary_information_of_delivery', resizable: true },
        { title: 'AA and Anticodon of Origin tRNA', dataIndex: 'aa_and_anticodon_of_origin_tRNA', width: 300, ellipsis: true, key: 'aa_and_anticodon_of_origin_tRNA', resizable: true },
        { title: 'AA and Anticodon of Sup-tRNA', dataIndex: 'aa_and_anticodon_of_sup_tRNA', width: 300, ellipsis: true, key: 'aa_and_anticodon_of_sup_tRNA', resizable: true },
        { title: 'Rnacentral ID of Origin tRNA', dataIndex: 'rnacentral_ID_of_origin_tRNA', width: 300, ellipsis: true, key: 'rnacentral_ID_of_origin_tRNA', resizable: true },
        { title: 'tRNAscan-SE ID of origin tRNA', dataIndex: 'tRNAscan-SE_ID_of_origin_tRNA', width: 300, ellipsis: true, key: 'tRNAscan-SE_ID_of_origin_tRNA', resizable: true },
        { title: 'Species Source of Origin tRNA', dataIndex: 'Species_source_of_origin_tRNA', width: 300, ellipsis: true, key: 'Species_source_of_origin_tRNA', resizable: true },
        { title: 'Sequence of Origin tRNA', dataIndex: 'Sequence_of_origin_tRNA', width: 300, ellipsis: true, key: 'Sequence_of_origin_tRNA', resizable: true },
        { title: 'Sequence of Sup-tRNA', dataIndex: 'Sequence_of_sup_tRNA', width: 300, ellipsis: true, key: 'Sequence_of_sup_tRNA', resizable: true },
        { title: 'Alignment', dataIndex: 'Alignment', width: 300, ellipsis: true, key: 'Alignment', resizable: true },
        { title: 'E-Value', dataIndex: 'E_Value', width: 300, ellipsis: true, key: 'E_Value', resizable: true },
        { title: 'Score', dataIndex: 'Score', width: 300, ellipsis: true, key: 'Score', resizable: true },
        { title: 'Identities', dataIndex: 'Identities', width: 300, ellipsis: true, key: 'Identities', resizable: true },
        { title: 'Gaps', dataIndex: 'Gaps', width: 300, ellipsis: true, key: 'Gaps', resizable: true },
        { title: 'Ref Length', dataIndex: 'Ref_length', width: 100, ellipsis: true, key: 'Ref_length', resizable: true },
        { title: 'Engineered aaRS', dataIndex: 'Engineered_aaRS', width: 150, ellipsis: true, key: 'Engineered_aaRS', resizable: true },
        { title: 'Reading Through Efficiency', dataIndex: 'Reading_through_efficiency', width: 200, ellipsis: true, key: 'Reading_through_efficiency', resizable: true },
        { title: 'Measuring of Efficiency', dataIndex: 'Measuring_of_efficiency', width: 200, ellipsis: true, key: 'Measuring_of_efficiency', resizable: true },
        { title: 'Supplementary Information of Measurement', dataIndex: 'Supplenmentary_information_of_Measurement', width: 300, ellipsis: true, key: 'Supplenmentary_information_of_Measurement', resizable: true },
        { title: 'Reaction System', dataIndex: 'Reaction_system', width: 150, ellipsis: true, key: 'Reaction_system', resizable: true },
        { title: 'Safety', dataIndex: 'Safety', width: 100, ellipsis: true, key: 'Safety', resizable: true },
        { title: 'Immunogenicity', dataIndex: 'Immunogenicity', width: 150, ellipsis: true, key: 'Immunogenicity', resizable: true },
        { title: 'Investigation', dataIndex: 'Investigation', width: 300, ellipsis: true, key: 'Investigation', resizable: true },
        { title: 'Citation', dataIndex: 'Citation', width: 300, ellipsis: true, key: 'Citation', resizable: true },
        { title: 'Notes', dataIndex: 'notes', width: 300, ellipsis: true, key: 'notes', resizable: true }
  
      ];
  
      const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );


    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      locale,
      selectedColumns,
      displayedColumns,
      allColumns // 列选择控件
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

.size-controls, .column-controls {
  display: flex;
  align-items: center;
}

.column-select {
  margin-left: 10px;
  width: 200px; /* 设置选择框的宽度 */
}
</style>

  