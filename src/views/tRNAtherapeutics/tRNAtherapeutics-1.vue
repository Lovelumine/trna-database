<template>
  <div class="site--main">
    <div >
      <div class="top-controls">
        <!-- 搜索框 -->
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
            <template v-else-if="column.key === 'E_Value'">
              {{ alignments[record.key]?.eValue }}
            </template>
            <template v-else-if="column.key === 'Score'">
              {{ alignments[record.key]?.score }}
            </template>
            <template v-else-if="column.key === 'Alignment'">
              {{ alignments[record.key]?.alignment }}
            </template>
            <template v-else-if="column.key === 'Gaps'">
              {{ alignments[record.key]?.gaps }}
            </template>
          </template>
          <template #expandedRowRender="{ record }">
            <div class="expanded-row">
              <div class="section">
                <h2>PTC Disease</h2>
                <table>
                  <tr>
                    <td><b>Related Disease:</b></td>
                    <td>{{ record.Related_disease }}</td>
                  </tr>
                  <tr>
                    <td><b>Pathogenic Gene:</b></td>
                    <td>
                      <a :href="record.Coding_Variation_Disease_database_link" target="_blank">{{ record.Pathogenic_gene }}</a>
                    </td>
                  </tr>
                  <tr>
                    <td><b>PTC Site:</b></td>
                    <td>
                      <a :href="record.PTC_site_link" target="_blank">{{ record.PTC_site }}</a>
                    </td>
                  </tr>
                  <tr>
                    <td><b>Origin AA and Codon:</b></td>
                    <td>{{ record.Origin_aa_and_codon_of_PTC_site }}</td>
                  </tr>
                  <tr>
                    <td><b>PTC Codon:</b></td>
                    <td>{{ record.PTC_codon }}</td>
                  </tr>
                </table>
              </div>
              <div class="section">
                <h2>PTC Model</h2>
                <table>
                  <tr>
                    <td><b>PTC Model:</b></td>
                    <td>{{ record.PTC_model }}</td>
                  </tr>
                  <tr>
                    <td><b>PTC Model Sequence:</b></td>
                    <td>{{ record.Sequence_of_PTC_model }}</td>
                  </tr>
                  <tr>
                    <td><b>Species Source:</b></td>
                    <td>{{ record.Species_source_of_PTC_model}}</td>
                  </tr>
                  <tr>
                    <td><b>NCBI ref ID:</b></td>
                    <td>{{ record.NCBI_ref_ID}}</td>
                  </tr>
                </table>
              </div>
              <div class="section">
                <h2>Sup-tRNA Treatment</h2>
                <table>
                  <tr>
                    <td><b>ENSURE ID of sup-tRNA:</b></td>
                    <td>
                      <a :href="record.ENSURE_ID_link" target="_blank">{{ record.ENSURE_ID }}</a>
                    </td>
                  </tr>
                  <tr>
                    <td><b>Species source:</b></td>
                    <td>{{ record.Species_source_of_origin_tRNA}}</td>
                  </tr>
                  <tr>
                    <td><b>AA and Anticodon of sup-tRNA:</b></td>
                    <td>{{ record.aa_and_anticodon_of_sup_tRNA }}</td>
                  </tr>
                  <tr>
                    <td><b>Dose:</b></td>
                    <td>{{ record.Delivery_as_vector_or_IVT_tRNA }}</td>
                  </tr>
                  <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'IVT_tRNA'">
                    <td><b>Dose_for_IVT_tRNA_delivery:</b></td>
                    <td>{{ record.Dose_for_IVT_tRNA_delivery }}</td>
                  </tr>
                  <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'vector'">
                    <td><b>Dose for vector delivery:</b></td>
                    <td>{{ record.Dose_for_vector_delivery}}</td>
                  </tr>
                  <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'vector'">
                    <td><b>Gene Copy Per Vector:</b></td>
                    <td>{{ record.tRNA_gene_copy_number_for_vector_delivery}}</td>
                  </tr>
                  <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'vector'">
                    <td><b>Promoter Per Copy:</b></td>
                    <td>{{ record.Promoter_for_vector_delivery}}</td>
                  </tr>
                </table>
              </div>
              <div class="section">
                <h2>Sup-tRNA Information</h2>
                <h3>Sup-tRNA</h3>
                <table>
                  <tr>
                    <td><b>ENSURE ID :</b></td>
                    <td>
                      <a :href="record.ENSURE_ID_link" target="_blank">{{ record.ENSURE_ID }}</a>
                    </td>
                  </tr>
                  <tr>
                    <td><b>AA and Anticodon:</b></td>
                    <td>{{ record.aa_and_anticodon_of_sup_tRNA }}</td>
                  </tr>
                  <tr>
                    <td><b>Gene sequence:</b></td>
                    <td>{{ record.sup_tRNA_gene}}</td>
                  </tr>
                  <tr>
                    <td><b>tRNA sequence:</b></td>
                    <td>{{ record.Sequence_of_sup_tRNA}}</td>
                  </tr>
                  <tr>
                    <td><b>Modification:</b></td>
                    <td>{{ record.Modification}}</td>
                  </tr>
                  <tr>
                    <td><b>Secondary structure:</b></td>
                    <td>{{ secondaryStructures[record.key] }}</td>
                  </tr>
                </table>
                <h3>origin tRNA</h3>
                <table>
                  <tr>
                    <td><b>Rnacentral ID:</b></td>
                    <td>{{ record.rnacentral_ID_of_origin_tRNA}}</td>
                  </tr>
                  <tr>
                    <td><b>tRNAscan-SE ID:</b></td>
                    <td>{{ record.tRNAscan_SE_ID_of_origin_tRNA}}</td>
                  </tr>
                  <tr>
                    <td><b>Species source:</b></td>
                    <td>{{ record.Species_source_of_origin_tRNA}}</td>
                  </tr>
                  <tr>
                    <td><b>AA and Anticodon:</b></td>
                    <td>{{ record.aa_and_anticodon_of_origin_tRNA}}</td>
                  </tr>
                  <tr>
                    <td><b>tRNA sequence:</b></td>
                    <td>{{ record.Sequence_of_origin_tRNA}}</td>
                  </tr>
                </table>
                <h3>Engineered site</h3>
                <table>
                  <tr>
                    <td><b>Alignment:</b></td>
                    <td>  <pre v-html="alignments[record.key]?.alignment"></pre></td>
                  </tr>
                  <tr>
                    <td><b>E-Value:</b></td>
                    <td>{{ alignments[record.key]?.eValue }}</td>
                  </tr>
                  <tr>
                    <td><b>Score:</b></td>
                    <td>{{ alignments[record.key]?.score }}</td>
                  </tr>
                  <tr>
                    <td><b>Gaps:</b></td>
                    <td>{{ alignments[record.key]?.gaps }}</td>
                  </tr>
                </table>
              </div>
            </div>
          </template>
        </s-table>
      </s-table-provider>
    </div>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed, nextTick } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import { calculateAlignment } from '../../utils/calculateAlignment';
import axios from 'axios';

type DataType = { [key: string]: string };

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default defineComponent({
  name: 'TRNATherapeutics-1',
  components: {
    ElTag,
    ElSpace,
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource, searchColumn, loadData } = useTableData('/data/tRNAtherapeutics.csv');

    const tableSize = ref('default');
    const selectedColumns = ref<string[]>([
      'Related_disease',
      'PTC_model',
      'Species_source_of_PTC_model',
      'Sequence_of_PTC_model',
      'Reaction_system',
    ]);
    
    const loading = ref(true); // 添加加载状态

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Related Disease', dataIndex: 'Related_disease', width: 200, ellipsis: true, key: 'Related_disease', 
        filter: {
          type: 'multiple',
          list: [
            { text: 'cystic fibrosis', value: 'cystic fibrosis' },
            { text: 'Model protein', value: 'Model protein' },
            { text: 'primary ciliary dyskinesia (PCD)', value: 'primary ciliary dyskinesia (PCD)' },
            { text: 'Xeroderma pigmentosum', value: 'Xeroderma pigmentosum' }, 
            { text: 'hereditary diffuse gastric cancer (HDGC)', value: 'hereditary diffuse gastric cancer (HDGC)' },    
            { text: 'mucopolysaccharidosis type I', value: 'mucopolysaccharidosis type I' },    
          ],
          onFilter: (value, record) => value.includes(record.Related_disease)
        },
        resizable: true },
      { title: 'Pathogenic Gene', dataIndex: 'Pathogenic_gene', width: 150, ellipsis: true, key: 'Pathogenic_gene', resizable: true },
      { title: 'PTC Model', dataIndex: 'PTC_model', width: 100, ellipsis: true, key: 'PTC_model', resizable: true },
      { title: 'Species Source of PTC Model', dataIndex: 'Species_source_of_PTC_model', width: 220, ellipsis: true, key: 'Species_source_of_PTC_model', resizable: true },
      { title: 'NCBI ref ID', dataIndex: 'NCBI_ref_ID', width: 220, ellipsis: true, key: 'NCBI_ref_ID', resizable: true },
      { title: 'Sequence of PTC Model', dataIndex: 'Sequence_of_PTC_model', width: 280, ellipsis: true, key: 'Sequence_of_PTC_model', resizable: true },
      { title: 'PTC Site', dataIndex: 'PTC_site', width: 150, ellipsis: true, key: 'PTC_site', resizable: true },
      { title: 'Origin AA and Codon of PTC Site', dataIndex: 'Origin_aa_and_codon_of_PTC_site', width: 200, ellipsis: true, key: 'Origin_aa_and_codon_of_PTC_site', resizable: true },
      { title: 'PTC Codon', dataIndex: 'PTC_codon', width: 100, ellipsis: true, key: 'PTC_codon', resizable: true },
      { title: 'Delivery as Vector or IVT tRNA', dataIndex: 'Delivery_as_vector_or_IVT_tRNA', width: 200, ellipsis: true, key: 'Delivery_as_vector_or_IVT_tRNA', resizable: true },
      { title: 'AA and Anticodon of Origin tRNA', dataIndex: 'aa_and_anticodon_of_origin_tRNA', width: 200, ellipsis: true, key: 'aa_and_anticodon_of_origin_tRNA', resizable: true },
      { title: 'AA and Anticodon of sup-tRNA', dataIndex: 'aa_and_anticodon_of_sup_tRNA', width: 200, ellipsis: true, key: 'aa_and_anticodon_of_sup_tRNA', resizable: true },
      { title: 'Rnacentral ID of Origin tRNA', dataIndex: 'rnacentral_ID_of_origin_tRNA', width: 100, ellipsis: true, key: 'rnacentral_ID_of_origin_tRNA', resizable: true },
      { title: 'tRNAscan-SE ID of origin tRNA', dataIndex: 'tRNAscan_SE_ID_of_origin_tRNA', width: 300, ellipsis: true, key: 'tRNAscan_SE_ID_of_origin_tRNA', resizable: true },
      { title: 'Species Source of Origin tRNA', dataIndex: 'Species_source_of_origin_tRNA', width: 300, ellipsis: true, key: 'Species_source_of_origin_tRNA', resizable: true },
      { title: 'ENSURE ID', dataIndex: 'ENSURE_ID', width: 300, ellipsis: true, key: 'ENSURE_ID', resizable: true },
      { title: 'Sequence of Origin tRNA', dataIndex: 'Sequence_of_origin_tRNA', width: 300, ellipsis: true, key: 'Sequence_of_origin_tRNA', resizable: true },
      { title: 'Sequence of Sup-tRNA', dataIndex: 'Sequence_of_sup_tRNA', width: 300, ellipsis: true, key: 'Sequence_of_sup_tRNA', resizable: true },
      { title: 'sup-tRNA Gene', dataIndex: 'sup_tRNA_gene', width: 300, ellipsis: true, key: 'sup_tRNA_gene', resizable: true },
      { title: 'Modification', dataIndex: 'Modification', width: 300, ellipsis: true, key: 'Modification', resizable: true },
      { title: 'Prediction_of_tRNAScan-SE', dataIndex: 'Prediction_of_tRNAScan-SE', width: 300, ellipsis: true, key: 'Prediction_of_tRNAScan-SE', resizable: true },
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
      { title: 'Dose for IVT tRNA Delivery', dataIndex: 'Dose_for_IVT_tRNA_delivery', width: 150, ellipsis: true, key: 'Dose_for_IVT_tRNA_delivery', resizable: true },
      { title: 'Dose for Vector Delivery', dataIndex: 'Dose_for_IVT_tRNA_delivery', width: 150, ellipsis: true, key: 'Dose_for_IVT_tRNA_delivery', resizable: true },
      { title: 'tRNA Gene Copy Number for Vector Delivery', dataIndex: 'tRNA_gene_copy_number_for_vector_delivery', width: 150, ellipsis: true, key: 'tRNA_gene_copy_number_for_vector_delivery', resizable: true },
      { title: 'Promoter for Vector Delivery', dataIndex: 'Promoter_for_vector_delivery', width: 150, ellipsis: true, key: 'Promoter_for_vector_delivery', resizable: true },
      { title: 'Safety', dataIndex: 'Safety', width: 100, ellipsis: true, key: 'Safety', resizable: true },
      { title: 'Immunogenicity', dataIndex: 'Immunogenicity', width: 150, ellipsis: true, key: 'Immunogenicity', resizable: true },
      { title: 'Citation', dataIndex: 'Citation', width: 300, ellipsis: true, key: 'Citation', resizable: true },
      { title: 'Notes', dataIndex: 'notes', width: 300, ellipsis: true, key: 'notes', resizable: true }
    ];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    const alignments = ref<{ [key: string]: any }>({});

    const loadAlignments = async (dataSource: DataType[]) => {
      for (const record of dataSource) {
        const result = await calculateAlignment(record.Sequence_of_origin_tRNA, record.Sequence_of_sup_tRNA);
        alignments.value[record.key] = result;
      }
    };

    const secondaryStructures = ref<{ [key: string]: string }>({});

    const loadSecondaryStructures = async (dataSource: DataType[]) => {
      console.log('Loading secondary structures...');
      for (const record of dataSource) {
        try {
          const response = await axios.post('/scan', { sequence: record.Sequence_of_sup_tRNA });
          console.log(`Fetched structure for record ${record.key}:`, response.data.str);
          secondaryStructures.value = { ...secondaryStructures.value, [record.key]: response.data.str };
        } catch (error) {
          console.error(`Failed to fetch secondary structure for record ${record.key}:`, error);
          secondaryStructures.value = { ...secondaryStructures.value, [record.key]: 'Error fetching structure' };
        }
      }
      console.log('Secondary structures loaded', secondaryStructures.value);
      await nextTick();
    };

    onMounted(async () => {
      console.log('On mounted hook triggered');
      try {
        await loadData();
        console.log('Data loaded');
        await Promise.all([loadAlignments(filteredDataSource.value), loadSecondaryStructures(filteredDataSource.value)]);
        console.log('Alignments and Secondary structures loaded');
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        loading.value = false;
      }
    });

    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      searchColumn,
      locale,
      selectedColumns,
      displayedColumns,
      calculateAlignment,
      allColumns,
      alignments,
      secondaryStructures,
      loading, // 添加到返回对象中
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

.expanded-row {
  border: 1px solid #ccc;
  padding: 16px;
  margin-bottom: 16px;
}

.section {
  margin-bottom: 16px;
}

.section h2 {
  margin-bottom: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

td {
  border: 1px solid #ddd;
  padding: 8px;
}

a {
  color: blue;
  text-decoration: underline;
}

.loading-message {
  font-size: 20px;
  text-align: center;
  padding: 20px;
}
</style>
