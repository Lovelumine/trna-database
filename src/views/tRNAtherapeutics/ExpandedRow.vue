<template>
    <div class="site--main">
      <div>
        <div v-for="record in filteredRecords" :key="record.key" class="expanded-row">
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
          <!-- <td>{{ secondaryStructures[record.key] }}</td> -->
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
        <!-- <tr>
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
        </tr> -->
        <!-- <tr v-if="secondaryStructures[record.key]">
          <td><b>Secondary Structure Diagram:</b></td>
          <td >
            {{ console.log(record.key, secondaryStructures[record.key], record.Sequence_of_sup_tRNA) }}
            <div style="max-height: 420px; max-width: 360px; overflow: auto; margin: auto">
              <TranStructure
                :titleA="'Origin-tRNA'"
                :titleB="'Sup-tRNA'" 
                :initialName="record.key"
                :initialStructure=" secondaryStructures[record.key]"
                :initialSequence="record.Sequence_of_origin_tRNA"
                :initialModifiedSequence="record.Sequence_of_sup_tRNA"
              />
            </div>
          </td>
        </tr> -->
      </table>
    </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="tsx">
  import { defineComponent, ref, onMounted, computed } from 'vue';
  import axios from 'axios';
  import { useTableData } from '../../assets/js/useTableData.js';
  import { calculateAlignment } from '../../utils/calculateAlignment';
  
  export default defineComponent({
    name: 'TRNATherapeutics-1',
    setup() {
      const { searchText, filteredDataSource, loadData } = useTableData('/data/tRNAtherapeutics.csv');
  
      const loading = ref(true);
  
      const alignments = ref<{ [key: string]: any }>({});
  
      const loadAlignments = async (dataSource) => {
        for (const record of dataSource) {
          const result = await calculateAlignment(record.Sequence_of_origin_tRNA, record.Sequence_of_sup_tRNA);
          alignments.value[record.key] = result;
        }
      };
  
      const secondaryStructures = ref<{ [key: string]: string }>({});
  
      const loadSecondaryStructures = async (dataSource) => {
        for (const record of dataSource) {
          try {
            const response = await axios.post('/scan', { sequence: record.Sequence_of_sup_tRNA });
            secondaryStructures.value = { ...secondaryStructures.value, [record.key]: response.data.str };
          } catch (error) {
            secondaryStructures.value = { ...secondaryStructures.value, [record.key]: 'Error fetching structure' };
          }
        }
      };
  
      const filteredRecords = computed(() => {
        return filteredDataSource.value.filter(record => record.ENSURE_ID === 'ttd27');
      });
  
      onMounted(async () => {
        try {
          await loadData();
          await Promise.all([loadAlignments(filteredDataSource.value), loadSecondaryStructures(filteredDataSource.value)]);
        } catch (error) {
          console.error('Failed to load data:', error);
        } finally {
          loading.value = false;
        }
      });
  
      return {
        filteredRecords,
        loading,
      };
    }
  });
  </script>
  
  <style scoped>
  .site--main {
    padding: 20px;
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
  