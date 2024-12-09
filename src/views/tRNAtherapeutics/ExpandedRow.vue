<template>
    <div class="site--main">
        <h1>ENSURE_ID:{{id}}</h1>
      <div>
        <div v-for="record in filteredRecords" :key="record.key" class="expanded-row">
            <div class="section">
      <h2>PTC Disease </h2>
      <table>
        <tr>
          <td><b>Related Disease:</b></td>
          <td>{{ record.Related_disease }}</td>
        </tr>
        <tr>
          <td><b>PTC Gene:</b></td>
          <td>{{ record.PTC_gene }}</td>
        </tr>
        <tr>
          <td><b>PTC Site:</b></td>
          <td>
            {{ record['PTC_site']}}
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
          <td><b>PTC Model Sequence:</b></td>
          <td>{{ record['PTC(mutation_site)'] }}</td>
        </tr>
        <tr>
          <td><b>Species Source:</b></td>
          <td>{{ record.Species_source_of_PTC_gene}}</td>
        </tr>
        <tr>
          <td><b>NCBI ref ID:</b></td>
          <td>{{ record.NCBI_ref_ID}}</td>
        </tr>
        <tr>
          <td><b>PMID:</b></td>
          <td><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record['PMID']" target="_blank" class="tilt-hover">{{record['PMID']}}</a>
          </td>
        </tr>
      </table>
    </div>
    <div class="section">
      <h2>Engineered Sup-tRNA</h2>
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
          <td>{{ record['aa_and_anticodon_of_sup-tRNA'] }}</td>
        </tr>
        <tr>
          <td><b>Reading Through Efficiency:</b></td>
          <td>{{ record['Reading_through_efficiency'] }}</td>
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
            <a :href="record.ENSURE_ID_link" target="_blank" class="tilt-hover">{{ record.ENSURE_ID }}</a>
          </td>
        </tr>
        <tr>
          <td><b>AA and Anticodon:</b></td>
          <td>{{ record['aa_and_anticodon_of_sup-tRNA'] }}</td>
        </tr>
        <tr>
          <td><b>Gene sequence:</b></td>
          <td style="font-family: monospace;">{{ record['sup-tRNA_gene']}}</td>
        </tr>
        <tr>
          <td><b>tRNA sequence:</b></td>
          <td style="font-family: monospace;">{{ record['Sequence_of_sup-tRNA']}}</td>
        </tr>
        <tr>
          <td><b>Secondary structure:</b></td>
          <td style="font-family: monospace;">{{ record['Secondary structure of sup-trna']}}</td>
        </tr>
        <tr>
          <td><b>Modification:</b></td>
          <td>{{ record.Modification}}</td>
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
          <td>{{ record['tRNAscan-SE_ID_of_origin_tRNA']}}</td>
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
          <td style="font-family: monospace;">{{ record.Sequence_of_origin_tRNA}}</td>
        </tr>
        <tr>
          <td><b>Secondary structure:</b></td>
          <td style="font-family: monospace;">{{ record['Secondary structure']}}</td>
        </tr>
      </table>
      <h3>Engineered site</h3>
      <table>
        <tr>
          <td><b>Alignment:</b></td>
          <td>  <pre v-html="record.Alignment"></pre></td>
        </tr>
        <tr>
          <td><b>E-Value:</b></td>
          <td>{{ record['E-Value']}}</td>
        </tr>
        <tr>
          <td><b>Score:</b></td>
          <td>{{ record.Score }}</td>
        </tr>
        <tr>
          <td><b>Gaps:</b></td>
          <td>{{ record.Gaps }}</td>
        </tr> 
        <tr v-if=" record['Secondary structure']">
          <td><b>Secondary Structure Diagram:</b></td>
          <td >
            {{ console.log(record.key,  record['Secondary structure'], record['Sequence_of_sup-tRNA']) }}
            <div style="max-height: 420px; max-width: 360px; overflow: auto; margin: auto">
              <TranStructure
                :titleA="'Origin-tRNA'"
                :titleB="'Sup-tRNA'" 
                :initialName="record.NCBI_ref_ID"
                :initialStructure="record['Secondary structure']"
                :supStructure="record['Secondary structure of sup-trna']"
                :initialSequence="record.Sequence_of_origin_tRNA"
                :initialModifiedSequence="record['Sequence_of_sup-tRNA']"
              />
            </div>
          </td>
        </tr>
     <!-- New PDB Viewer Row -->
   <tr>
      <td><b>3D Structure:</b></td>
              <td>
                <div
                  :id="'pdb-container-' + record.ENSURE_ID"
                  style="height: 400px; width: 400px; position: relative"
                  class="viewer_3Dmoljs"
                ></div>
              </td>
            </tr>
      </table>
    </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="tsx">
  import { defineComponent, ref, onMounted, computed , nextTick} from 'vue';
  import axios from 'axios';
  import { useRoute } from 'vue-router';
  import { useTableData } from '../../assets/js/useTableData.js';
  import TranStructure from '@/components/TranStructure.vue';
  import * as $3Dmol from '3dmol';
  export default defineComponent({
    name: 'TRNATherapeutics-1',
    components: {
    TranStructure
  },
    setup() {

        const route = useRoute();  // 使用useRoute获取当前路由信息
        const id = route.params.key;  // 获取key参数

      const { searchText, filteredDataSource, loadData } = useTableData('/src/assets/data/tRNAtherapeutics.csv');
  
      const loading = ref(true);

  
      const filteredRecords = computed(() => {
        return filteredDataSource.value.filter(record => record.pre_ENSURE_ID == id);
      });
  
      onMounted(async () => {
      try {
        await loadData();
        await nextTick(); // Ensure DOM is fully rendered before loading PDB files
        filteredRecords.value.forEach(record => {
          loadPDBFile(record.ENSURE_ID);
        });
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        loading.value = false;
      }
    });
      const loadPDBFile = (ensureId) => {
      const pdbFilePath = `/src/assets/data/pdb/${ensureId}.pdb`;
      axios.get(pdbFilePath)
        .then(response => {
          const element = document.getElementById('pdb-container-' + ensureId);
          if (element) {
            const viewer = $3Dmol.createViewer(element, { backgroundColor: 'white' });
            viewer.addModel(response.data, 'pdb');
            viewer.setStyle({}, { cartoon: { color: 'spectrum' } });
            viewer.zoomTo();
            viewer.render();
          }
        })
        .catch(error => {
          console.error(`Failed to load PDB file for ${ensureId}:`, error);
        });
    };
  
      return {
        filteredRecords,
        loading,
        id,
        TranStructure,
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

  .viewer_3Dmoljs {
  position: relative;
}
  </style>
  