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
                <ElTag v-for="item in record.Related_disease.split(';').map(str => str.trim())" :key="item">
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
            </div>
          </template>
        </s-table>
      </s-table-provider>
    </div>
  </template>
  
  <script lang="tsx">
  import { defineComponent, ref, onMounted } from 'vue';
  import { ElTag, ElSpace } from 'element-plus';
  import { STableProvider } from '@shene/table';
  import type { STableColumnsType } from '@shene/table';
  import { useTableData } from '../../assets/js/useTableData.js';
  
  type DataType = {
    [key: string]: string;
    Related_disease: string;
    Pathogenic_gene: string;
    PTC_model: string;
    Species_source_of_PTC_model: string;
    Sequence_of_PTC_model: string;
    PTC_site: string;
    Origin_aa_and_codon_of_PTC_site: string;
    PTC_codon: string;
    Delivery_as_vector_or_IVT_tRNA: string;
    Delivery_method: string;
    Ref_length: string;
    Engineered_aaRS: string;
    Reading_through_efficiency: string;
    Measuring_of_efficiency: string;
    Supplenmentary_information_of_Measurement: string;
    Reaction_system: string;
    Safety: string;
    Immunogenicity: string;
    Investigation: string;
    Citation: string;
  };
  
  import en from '@shene/table/dist/locale/en'
  const locale = ref(en)

  export default defineComponent({
    name: 'TRNATherapeutics-1',
    setup() {
      const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNAtherapeutics.csv');
  
      const tableSize = ref('default');
  
      onMounted(() => {
        loadData();
      });
  
      const columns: STableColumnsType<DataType> = [
        { title: 'Related Disease', dataIndex: 'Related_disease', width: 150, ellipsis: true, key: 'Related_disease', resizable: true },
        { title: 'Pathogenic Gene', dataIndex: 'Pathogenic_gene', width: 150, ellipsis: true, key: 'Pathogenic_gene', resizable: true },
        { title: 'PTC Model', dataIndex: 'PTC_model', width: 100, ellipsis: true, key: 'PTC_model', resizable: true },
        { title: 'Species Source of PTC Model', dataIndex: 'Species_source_of_PTC_model', width: 200, ellipsis: true, key: 'Species_source_of_PTC_model', resizable: true },
        { title: 'Sequence of PTC Model', dataIndex: 'Sequence_of_PTC_model', width: 200, ellipsis: true, key: 'Sequence_of_PTC_model', resizable: true },
        { title: 'PTC Site', dataIndex: 'PTC_site', width: 150, ellipsis: true, key: 'PTC_site', resizable: true },
        { title: 'Origin AA and Codon of PTC Site', dataIndex: 'Origin_aa_and_codon_of_PTC_site', width: 200, ellipsis: true, key: 'Origin_aa_and_codon_of_PTC_site', resizable: true },
        { title: 'PTC Codon', dataIndex: 'PTC_codon', width: 100, ellipsis: true, key: 'PTC_codon', resizable: true },
        { title: 'Delivery as Vector or IVT tRNA', dataIndex: 'Delivery_as_vector_or_IVT_tRNA', width: 200, ellipsis: true, key: 'Delivery_as_vector_or_IVT_tRNA', resizable: true },
        { title: 'Delivery Method', dataIndex: 'Delivery_method', width: 150, ellipsis: true, key: 'Delivery_method', resizable: true },
        { title: 'Ref Length', dataIndex: 'Ref_length', width: 100, ellipsis: true, key: 'Ref_length', resizable: true },
        { title: 'Engineered aaRS', dataIndex: 'Engineered_aaRS', width: 150, ellipsis: true, key: 'Engineered_aaRS', resizable: true },
        { title: 'Reading Through Efficiency', dataIndex: 'Reading_through_efficiency', width: 200, ellipsis: true, key: 'Reading_through_efficiency', resizable: true },
        { title: 'Measuring of Efficiency', dataIndex: 'Measuring_of_efficiency', width: 200, ellipsis: true, key: 'Measuring_of_efficiency', resizable: true },
        { title: 'Supplementary Information of Measurement', dataIndex: 'Supplenmentary_information_of_Measurement', width: 300, ellipsis: true, key: 'Supplenmentary_information_of_Measurement', resizable: true },
        { title: 'Reaction System', dataIndex: 'Reaction_system', width: 150, ellipsis: true, key: 'Reaction_system', resizable: true },
        { title: 'Safety', dataIndex: 'Safety', width: 100, ellipsis: true, key: 'Safety', resizable: true },
        { title: 'Immunogenicity', dataIndex: 'Immunogenicity', width: 150, ellipsis: true, key: 'Immunogenicity', resizable: true },
        { title: 'Investigation', dataIndex: 'Investigation', width: 300, ellipsis: true, key: 'Investigation', resizable: true },
        { title: 'Citation', dataIndex: 'Citation', width: 300, ellipsis: true, key: 'Citation', resizable: true }
      ];
  
      return {
        columns,
        filteredDataSource,
        tableSize,
      searchText,
      locale,
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

.size-controls {
  display: flex;
  align-items: center;
}
</style>

  