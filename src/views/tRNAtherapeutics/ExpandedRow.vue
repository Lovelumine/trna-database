<template>
  <div class="site--main">
    <h1>ENSURE_ID:{{ id }}</h1>
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
              <td>{{ record['PTC_site'] }}</td>
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
              <td>{{ record.Species_source_of_PTC_gene }}</td>
            </tr>
            <tr>
              <td><b>NCBI ref ID:</b></td>
              <td>{{ record.NCBI_ref_ID }}</td>
            </tr>
            <tr>
              <td><b>PMID:</b></td>
              <td>
                <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record['PMID']" target="_blank" class="tilt-hover">
                  {{ record['PMID'] }}
                </a>
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
              <td>{{ record.Species_source_of_origin_tRNA }}</td>
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
            <!-- <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'IVT_tRNA'">
              <td><b>Dose_for_IVT_tRNA_delivery:</b></td>
              <td>{{ record.Dose_for_IVT_tRNA_delivery }}</td>
            </tr>
            <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'vector'">
              <td><b>Dose for vector delivery:</b></td>
              <td>{{ record.Dose_for_vector_delivery }}</td>
            </tr>
            <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'vector'">
              <td><b>Gene Copy Per Vector:</b></td>
              <td>{{ record.tRNA_gene_copy_number_for_vector_delivery }}</td>
            </tr>
            <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'vector'">
              <td><b>Promoter Per Copy:</b></td>
              <td>{{ record.Promoter_for_vector_delivery }}</td>
            </tr> -->
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
              <td style="font-family: monospace;">{{ record['sup-tRNA_gene'] }}</td>
            </tr>
            <tr>
              <td><b>Sup-tRNA sequence:</b></td>
              <td style="font-family: monospace;">{{ record['Sequence_of_sup-tRNA'] }}</td>
            </tr>
            <tr>
              <td><b>Secondary structure:</b></td>
              <td style="font-family: monospace;">{{ record['Secondary structure of sup-trna'] }}</td>
            </tr>
            <tr>
              <td><b>Modification:</b></td>
              <td>{{ record.Modification }}</td>
            </tr>
          </table>
          <h3>origin tRNA</h3>
          <table>
            <tr>
              <td><b>Rnacentral ID:</b></td>
              <td>{{ record.rnacentral_ID_of_origin_tRNA }}</td>
            </tr>
            <tr>
              <td><b>tRNAscan-SE ID:</b></td>
              <td>{{ record['tRNAscan-SE_ID_of_origin_tRNA'] }}</td>
            </tr>
            <tr>
              <td><b>Species source:</b></td>
              <td>{{ record.Species_source_of_origin_tRNA }}</td>
            </tr>
            <tr>
              <td><b>AA and Anticodon:</b></td>
              <td>{{ record.aa_and_anticodon_of_origin_tRNA }}</td>
            </tr>
            <tr>
              <td><b>Origin-tRNA sequence:</b></td>
              <td style="font-family: monospace;">{{ record.Sequence_of_origin_tRNA }}</td>
            </tr>
            <tr>
              <td><b>Secondary structure:</b></td>
              <td style="font-family: monospace;">{{ record['Secondary structure'] }}</td>
            </tr>
          </table>
          <h3>Engineered site</h3>
          <table>
            <tr>
              <td><b>Alignment:</b></td>
              <td>
                <pre v-html="record.formattedAlignment"></pre>
              </td>
            </tr>
            <tr>
              <td><b>E-Value:</b></td>
              <td>{{ record['E-Value'] }}</td>
            </tr>
            <tr>
              <td><b>Score:</b></td>
              <td>{{ record.Score }}</td>
            </tr>
            <tr>
              <td><b>Gaps:</b></td>
              <td>{{ record.Gaps }}</td>
            </tr>
            <tr v-if="record['Secondary structure']">
              <td><b>Secondary Structure Diagram:</b></td>
              <td>
                <!-- 调试输出 -->
                <!-- {{ console.log('Record key:', record.key, 'Secondary structure:', record['Secondary structure'], 'Sup-tRNA sequence:', record['Sequence_of_sup-tRNA']) }} -->
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
            <!-- 添加主图展示区域 -->
<!-- Cloverleaf Chart -->
<!-- <div class="section">
  <h2>tRNA Cloverleaf Structure</h2>
  <div id="cloverleaf-area" style="border: 1px solid #ccc; margin-top: 20px;"></div>
</div> -->
    </div>
  </div>
</template>



<script lang="tsx">
import { defineComponent, ref, onMounted, computed, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useTableData } from '../../assets/js/useTableData.js';
import TranStructure from '@/components/TranStructure.vue';
import * as d3 from 'd3';
import { draw_cloverleaf, draw_base_distro } from '@/utils/tRNAviz/js/consensusESM.js';
import "@/utils/tRNAviz/css/explorer.css";
// 从同目录下导入提取出的逻辑函数
import {
  formatAlignment,
  loadPDBFile
} from './expandedRowLogic';

export default defineComponent({
  name: 'TRNATherapeutics-1',
  components: {
    TranStructure
  },
  setup() {
    console.log("[ExpandedRow] setup() invoked.");

    const route = useRoute();
    const id = route.params.key;
    console.log("[ExpandedRow] route param id =>", id);

    // 加载 CSV 数据的自定义逻辑
    const { filteredDataSource, loadData } = useTableData('https://minio.lumoxuan.cn/ensure/tRNAtherapeutics.csv');
    const loading = ref(true);

    // 过滤出与当前 id 匹配的记录
    const filteredRecords = computed(() => {
      const result = filteredDataSource.value.filter(record => record.ENSURE_ID == id);
      console.log("[ExpandedRow] computed filteredRecords =>", result);
      return result;
    });

    onMounted(async () => {
      console.log("[ExpandedRow] onMounted() start...");
      try {
        console.log("[ExpandedRow] Begin loadData() for CSV...");
        await loadData();
        console.log("[ExpandedRow] CSV data loaded =>", filteredDataSource.value);

        await nextTick();
        console.log("[ExpandedRow] DOM updated. handle each record...");

        filteredRecords.value.forEach(record => {
          console.log("[ExpandedRow] handle record =>", record);
          // 加载 PDB 文件
          loadPDBFile(record.Index, record.ENSURE_ID);

          // 格式化 Alignment
          record.formattedAlignment = formatAlignment(record.Alignment);
        });

        // 现在去加载 ala.json（其结构是 { "1": {...}, "2": {...}, ... }）
        console.log("[ExpandedRow] Fetching JSON for Cloverleaf from ala.json...");
        d3.json("https://minio.lumoxuan.cn/ensure/trnaviz/ala.json")
          .then(plotData => {
            console.log("[ExpandedRow] ala.json loaded =>", plotData);

            // 3) 使用 draw_cloverleaf
            //   第2个参数 isotype 可随意，这里假定 "Ala" 或 "Any"
            draw_cloverleaf(plotData, "Ala", "https://minio.lumoxuan.cn/ensure/trnaviz/ala.json");
            
            // 4) 如果你想同时画 base distro，可以再调用 draw_base_distro
            //   但是要先看 consensus.js 的 draw_base_distro 需要什么参数
            //   (它里面常见用法: draw_base_distro(plotData, 'cloverleaf') )
            //   这里就示例一下：
            draw_base_distro(plotData, 'cloverleaf');
            
          })
          .catch(err => {
            console.error("[ExpandedRow] d3.json error =>", err);
          });
      } catch (error) {
        console.error("[ExpandedRow] onMounted error =>", error);
      } finally {
        loading.value = false;
        console.log("[ExpandedRow] onMounted finished. loading =>", loading.value);
      }
    });

    return {
      filteredRecords,
      loading,
      id,
      TranStructure
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

/* 碱基匹配样式 */
:deep(.match) { 
  color: #4CAF50 !important; /* 强制应用绿色 */
}        
:deep(.mismatch) { 
  color: #F44336 !important;  /* 强制应用红色 */
}     
:deep(.gap) { 
  color: #9E9E9E !important; /* 强制应用灰色 */
}  

/* 符号行样式 */
:deep(.match-symbol) { 
  color: #4CAF50 !important;
} 
:deep(.mismatch-symbol) { 
  color: #F44336 !important;
}
:deep(.gap-symbol) { 
  color: #9E9E9E !important;
}

</style>
