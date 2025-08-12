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
            <tr v-if ="record.Origin_aa_and_codon_of_PTC_site && record.Origin_aa_and_codon_of_PTC_site.trim() !== ''">
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
            <tr v-if="record.Species_source_of_PTC_gene && record.Species_source_of_PTC_gene.trim() !== ''">
              <td><b>Species Source:</b></td>
              <td>{{ record.Species_source_of_PTC_gene }}</td>
            </tr>
            <tr v-if="record.NCBI_ref_ID && record.NCBI_ref_ID.trim() !== ''">
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
          <h2>Engineered sup-tRNA</h2>
          <table>
            <tr>
              <td><b>ENSURE ID of sup-tRNA:</b></td>
              <td>
                <a :href="record.ENSURE_ID_link" target="_blank">{{ record.ENSURE_ID }}</a>
              </td>
            </tr>
            <tr v-if="record.Species_source_of_origin_tRNA && String(record.Species_source_of_origin_tRNA).trim() !== ''">
              <td><b>Species source:</b></td>
              <td>{{ record.Species_source_of_origin_tRNA }}</td>
            </tr>
            <tr>
              <td><b>AA and Anticodon of sup-tRNA:</b></td>
              <td>{{ record['aa_and_anticodon_of_sup-tRNA'] }}</td>
            </tr>
            <tr v-if="String(record.Reading_through_efficiency).trim() !== ''">
              <td><b>Reading Through Efficiency:</b></td>
              <td>{{ record.Reading_through_efficiency }}</td>
            </tr>
            <tr v-if="String(record.Measuring_of_efficiency).trim() !== ''">
              <td><b>Measuring of Efficiency:</b></td>
              <td>{{ record.Measuring_of_efficiency}}</td>
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
           <!-- </table>
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
            </tr> -->
            <!-- <tr>
              <td><b>AA and Anticodon:</b></td>
              <td>{{ record['aa_and_anticodon_of_sup-tRNA'] }}</td>
            </tr> -->
            <tr
              v-if='record["sup-tRNA_gene"] && String(record["sup-tRNA_gene"]).trim() !== ""'
            >
              <td><b>Gene sequence:</b></td>
              <td style="font-family: monospace;">{{ record['sup-tRNA_gene'] }}</td>
            </tr>
            <tr>
              <td><b>sup-tRNA sequence:</b></td>
              <td style="font-family: monospace;">{{ record['Sequence_of_sup-tRNA'] }}</td>
            </tr>
            <tr>
              <td><b>Secondary structure:</b></td>
              <td style="font-family: monospace;">{{ record['Secondary structure of sup-trna'] }}</td>
            </tr>
            <tr v-if ="record.Modification && String(record.Modification).trim() !== ''">
              <td><b>Modification:</b></td>
              <td>{{ record.Modification }}</td>
            </tr>
          </table>
          <h3>origin tRNA</h3>
          <table>
            <tr v-if="record.rnacentral_ID_of_origin_tRNA && String(record.rnacentral_ID_of_origin_tRNA).trim() !== ''">
              <td><b>Rnacentral ID:</b></td>
              <td>{{ record.rnacentral_ID_of_origin_tRNA }}</td>
            </tr>
            <tr
              v-if="
                record['tRNAscan-SE_ID_of_origin_tRNA'] &&
                String(record['tRNAscan-SE_ID_of_origin_tRNA']).trim() !== ''
              "
            >
              <td><b>tRNAscan-SE ID:</b></td>
              <td>{{ record['tRNAscan-SE_ID_of_origin_tRNA'] }}</td>
            </tr>
            <tr v-if="record.Species_source_of_origin_tRNA && String(record.Species_source_of_origin_tRNA).trim() !== ''">
              <td><b>Species source:</b></td>
              <td>{{ record.Species_source_of_origin_tRNA }}</td>
            </tr>
            <tr v-if="Array.isArray(parseSup(record.aa_and_anticodon_of_origin_tRNA))">
              <td><b>AA and Anticodon:</b></td>
              <td>{{ record.aa_and_anticodon_of_origin_tRNA }}</td>
            </tr>
            <tr v-if="Array.isArray(parseSup(record.Sequence_of_origin_tRNA))">
              <td><b>Origin-tRNA sequence:</b></td>
              <td style="font-family: monospace;">{{ record.Sequence_of_origin_tRNA }}</td>
            </tr>
            <tr v-if="Array.isArray(parseSup(record['Secondary structure']))">
              <td><b>Secondary structure:</b></td>
              <td style="font-family: monospace;">{{ record['Secondary structure'] }}</td>
            </tr>
          </table>
          <h3>Engineered site</h3>
          <table>
            <tr class="toggle-row" v-if="Array.isArray(parseSup(record.js_sup_tRNA)) && parseSup(record.js_sup_tRNA).length > 5">
              <td>
                <b>Sprinzl coordinate</b>
                <!-- 引用徽章 -->
                <sup
                  class="cite-badge"
                  :data-tooltip="CITE_TEXT"
                  aria-label="Sprinzl & Vassilenko 2005"
                >
                  <a
                    :href="CITE_LINK"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="cite-link"
                  >1</a>
                </sup>

                <!-- 切换按钮 -->
                <div class="toggle-group">
                  <button
                    class="toggle-btn"
                    :class="{ active: showSup }"
                    @click="showSup = true"
                  >
                    Sup Numbering
                  </button>
                  <button
                    class="toggle-btn"
                    :class="{ active: !showSup }"
                    @click="showSup = false"
                  >
                    Original Numbering
                  </button>
                </div>
              </td>
              <td>
                <div
                  class="radial-container"
                  v-if="
                    showSup ||
                    (!showSup && parseSup(record.js_origin_tRNA).length >= 5)
                  "
                >
                  <supTrnaRadial
                    v-if="showSup"
                    :data="parseSup(record.js_sup_tRNA)"
                    :width="775"
                    :height="560"
                    :r="12"
                  />
                  <TrnaRadial
                    v-else
                    :data="parseSup(record.js_origin_tRNA)"
                    :width="775"
                    :height="560"
                    :r="12"
                  />
                </div>
              </td>
            </tr>

            <tr v-if="Array.isArray(parseSup(record.js_sup_tRNA)) && parseSup(record.js_sup_tRNA).length > 5">
              <td><b>Alignment:</b></td>
              <td>
                <AlignmentTable
                  :alignmentData="parseSup(record.js_sup_tRNA)"
                  :chunkSize="36"
                />
              </td>
            </tr>

            <tr v-if="Array.isArray(parseSup(record.pairwise_score)) && parseSup(record.pairwise_score).length > 5">
              <td><b>Score:</b></td>
              <td>
                <span class="tooltip">
                  {{ record.pairwise_score }}
                  <span class="tooltip-text">
                    Scoring：
                    <ul>
                      <li>match = +2</li>
                      <li>mismatch = −0.5</li>
                      <li>gap open = −2</li>
                      <li>gap extend = −1</li>
                    </ul>
                  </span>
                </span>
              </td>
            </tr>

            <tr v-if="record['Secondary structure']">
              <td><b>Secondary Structure Comparison:</b></td>
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
<!-- template 里对每个 record 增加 sample 切换按钮 -->
<tr>
  <td><b>3D Structure:</b></td>
  <td>
<div class="sample-switcher">
  <div
    v-for="i in 5"
    :key="i"
    class="seg-btn"
    :class="{ active: record._selectedSample === (i-1) }"
    @click="switchSample(record, i-1)"
  >
    {{ i-1 }}
  </div>
</div>
    <div
      :id="'pdb-container-' + record.ENSURE_ID"
      style="height: 400px; width: 600px;"
    ></div>
  </td>
</tr>
            </table>

          <!-- 参考文献区块 -->
          <div class="references">
            <strong>References</strong>
            <ol>
              <li>
                Sprinzl M, Vassilenko KS.
                <em>Compilation of tRNA sequences and sequences of tRNA genes</em>.
                Nucleic Acids Res. 2005 Jan 1;33(Database issue):D139-40.
                doi: <a :href="CITE_LINK" target="_blank">10.1093/nar/gki012</a>.
                PMID: 15608164; PMCID: PMC539966.
              </li>
            </ol>
          </div>
        </div>

            <!-- 添加主图展示区域 -->
<!-- Cloverleaf Chart -->
<!-- <div class="section">
  <h2>tRNA Cloverleaf Structure</h2>
  <div id="cloverleaf-area" style="border: 1px solid #ccc; margin-top: 20px;"></div>
</div> -->
    </div>
  <!-- <div>
    <TrnaRadial />
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
  loadCIFFile
} from './expandedRowLogic';
import TrnaRadial from '@/components/TrnaRadial.vue'
import supTrnaRadial from '@/components/supTrnaRadial.vue'
import AlignmentTable from '@/components/AlignmentTable.vue';

export default defineComponent({
  name: 'TRNATherapeutics-1',
  components: {
    TranStructure,
    TrnaRadial,
    supTrnaRadial,
    AlignmentTable,
  },
  setup() {
    console.log("[ExpandedRow] setup() invoked.");

    const route = useRoute();
    const id = route.params.key;
    console.log("[ExpandedRow] route param id =>", id);

    // 加载 CSV 数据的自定义逻辑
    const { filteredDataSource, loadData } = useTableData('https://minio.lumoxuan.cn/ensure/Engineered Sup-tRNA.csv');
    const loading = ref(true);

    const showSup = ref(true);

    // 过滤出与当前 id 匹配的记录
    const filteredRecords = computed(() => {
      const result = filteredDataSource.value.filter(record => record.ENSURE_ID == id);
      console.log("[ExpandedRow] computed filteredRecords =>", result);
      return result;
    });

    const parseSup = (str: string) => {
      try {
        return JSON.parse(str);
      } catch {
        return [];
      }
    };

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
          record._selectedSample = 0;
          // 加载 PDB 文件
          loadCIFFile(record.pdbid, record.ENSURE_ID, 0);

          // 格式化 Alignment·
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

    function switchSample(record: any, sampleIdx: number) {
      record._selectedSample = sampleIdx;
      loadCIFFile(record.pdbid, record.ENSURE_ID, sampleIdx);
    }

    // 引用常量
    const CITE_TEXT =
      'Sprinzl M, Vassilenko KS. Compilation of tRNA sequences and sequences of tRNA genes.\n'
      + 'Nucleic Acids Res. 2005 Jan 1;33(Database issue):D139-40.\n'
      + 'doi: 10.1093/nar/gki012. PMID: 15608164; PMCID: PMC539966';
    const CITE_LINK = 'https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gki012';

    return {
      id,
      loading,
      filteredRecords,
      parseSup,
      showSup,
      switchSample,
      CITE_TEXT,
      CITE_LINK
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
  vertical-align: top;
}

a {
  color: #0d6efd;
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

/* —— match/mismatch styles —— */
:deep(.match) { color: #4caf50 !important; }
:deep(.mismatch) { color: #f44336 !important; }
:deep(.gap) { color: #9e9e9e !important; }
:deep(.match-symbol) { color: #4caf50 !important; }
:deep(.mismatch-symbol) { color: #f44336 !important; }
:deep(.gap-symbol) { color: #9e9e9e !important; }

/* —— Toggle group —— */
.toggle-group {
  margin: 8px 0 12px;
  display: inline-flex;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}
.toggle-btn {
  padding: 6px 14px;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
  transition: background-color .2s, color .2s;
}
.toggle-btn:not(.active):hover {
  background: #eee;
}
.toggle-btn.active {
  background: #1976d2;
  color: #fff;
}

.toggle-row td {
  vertical-align: middle;
}

.radial-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* ===== Citation badge ===== */
.cite-badge {
  position: relative;
  display: inline-block;
  background: #1976d2;
  color: #fff;
  font-size: 0.72em;
  width: 1.25em;
  height: 1.25em;
  line-height: 1.25em;
  text-align: center;
  border-radius: 50%;
  margin-left: 6px;
  cursor: help;
}
.cite-link {
  color: inherit;
  text-decoration: none;
  display: block;
}

/* tooltip */
.cite-badge:hover::after {
  content: attr(data-tooltip);
  white-space: pre-wrap;
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.85);
  color: #fff;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.35;
  width: 260px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  z-index: 20;
}
.cite-badge:hover::before {
  content: '';
  position: absolute;
  bottom: 115%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(0,0,0,0.85) transparent transparent transparent;
  z-index: 21;
}

/* ===== Tooltip for score ===== */
.tooltip {
  position: relative;
  display: inline-block;
  cursor: help;
}
.tooltip-text {
  visibility: hidden;
  width: 220px;
  background-color: rgba(0, 0, 0, 0.75);
  color: #fff;
  text-align: left;
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  line-height: 1.4;
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity .2s ease-in-out;
  z-index: 10;
}
.tooltip-text::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: rgba(0,0,0,0.75) transparent transparent transparent;
}
.tooltip:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

/* sample switcher */
.sample-switcher {
  display: inline-flex;
  border: 1px solid #ccc;
  border-radius: 999px;
  overflow: hidden;
  font-size: 0.875rem;
  margin-bottom: 6px;
}
.sample-switcher .seg-btn {
  padding: 4px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color .2s, color .2s;
  color: #555;
}
.sample-switcher .seg-btn:not(:last-child) {
  border-right: 1px solid #ccc;
}
.sample-switcher .seg-btn:hover {
  background-color: #f0f0f0;
}
.sample-switcher .seg-btn.active {
  background-color: #1976d2;
  color: #fff;
}

/* references */
.references {
  margin-top: 16px;
  font-size: 0.9em;
  color: #555;
}
.references ol {
  padding-left: 20px;
  margin: 6px 0;
}
.references li {
  margin-bottom: 4px;
}
</style>