<template>
  <div class="site--main">
    <h1>ENSURE_ID:{{ id }}</h1>
    <div>
      <div v-for="record in filteredRecords" :key="record.key" class="expanded-row">
        <div class="section header-actions" v-if="EDIT_MODE">
          <el-button size="small" type="primary" @click="enterEdit(record)" v-if="!isEditing(record)">Edit</el-button>
          <template v-else>
            <el-button size="small" type="success" @click="saveEdit(record)">Save</el-button>
            <el-button size="small" @click="cancelEdit(record)" style="margin-left:6px">Cancel</el-button>
          </template>
        </div>

        <div class="section">
          <h2>PTC Disease </h2>
          <table>
            <tr>
              <td><b>Related Disease:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Related_disease }}</template>
                <el-input v-else v-model="record._draft.Related_disease" type="textarea" autosize />
              </td>
            </tr>
            <tr>
              <td><b>PTC Gene:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.PTC_gene }}</template>
                <el-input v-else v-model="record._draft.PTC_gene" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record['PTC_site']) || isEditing(record)">
              <td><b>PTC Site:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record['PTC_site'] }}</template>
                <el-input v-else v-model="record._draft['PTC_site']" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Origin_aa_and_codon_of_PTC_site) || isEditing(record)">
              <td><b>Origin AA and Codon:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Origin_aa_and_codon_of_PTC_site }}</template>
                <el-input v-else v-model="record._draft.Origin_aa_and_codon_of_PTC_site" type="textarea" autosize />
              </td>
            </tr>
            <tr>
              <td><b>PTC Codon:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.PTC_codon }}</template>
                <el-input v-else v-model="record._draft.PTC_codon" type="textarea" autosize />
              </td>
            </tr>
          </table>
        </div>
        <div class="section">
          <h2>PTC Model</h2>
          <table>
            <tr v-if="showRow(record['PTC(mutation_site)']) || isEditing(record)">
              <td><b>PTC Model Sequence:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record['PTC(mutation_site)'] }}</template>
                <el-input v-else v-model="record._draft['PTC(mutation_site)']" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Species_source_of_PTC_gene) || isEditing(record)">
              <td><b>Species Source:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Species_source_of_PTC_gene }}</template>
                <el-input v-else v-model="record._draft.Species_source_of_PTC_gene" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.NCBI_ref_ID) || isEditing(record)">
          <td><b>NCBI ref ID:</b></td>
          <td>
            <template v-if="!isEditing(record)">{{ record.NCBI_ref_ID }}</template>
            <el-input v-else v-model="record._draft.NCBI_ref_ID" type="textarea" autosize />
          </td>
            </tr>
            <tr>
              <td><b>PMID:</b></td>
              <td>
                <template v-if="!isEditing(record)">
                  <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + record['PMID']" target="_blank" class="tilt-hover">
                    {{ record['PMID'] }}
                  </a>
                </template>
                <el-input v-else v-model="record._draft.PMID" />
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
                <template v-if="!isEditing(record)">
                  <a :href="record.ENSURE_ID_link" target="_blank">{{ record.ENSURE_ID }}</a>
                </template>
                <el-input v-else v-model="record._draft.ENSURE_ID" />
              </td>
            </tr>
            <tr v-if="showRow(record.Species_source_of_origin_tRNA) || isEditing(record)">
              <td><b>Species source:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Species_source_of_origin_tRNA }}</template>
                <el-input v-else v-model="record._draft.Species_source_of_origin_tRNA" type="textarea" autosize />
              </td>
            </tr>
            <tr>
              <td><b>AA and Anticodon of sup-tRNA:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record['aa_and_anticodon_of_sup-tRNA'] }}</template>
                <el-input v-else v-model="record._draft['aa_and_anticodon_of_sup-tRNA']" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Reading_through_efficiency) || isEditing(record)">
              <td><b>Reading Through Efficiency:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Reading_through_efficiency }}</template>
                <el-input v-else v-model="record._draft.Reading_through_efficiency" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Measuring_of_efficiency) || isEditing(record)">
              <td><b>Measuring of Efficiency:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Measuring_of_efficiency}}</template>
                <el-input v-else v-model="record._draft.Measuring_of_efficiency" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Delivery_as_vector_or_IVT_tRNA) || isEditing(record)">
              <td><b>Dose:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Delivery_as_vector_or_IVT_tRNA }}</template>
                <el-input v-else v-model="record._draft.Delivery_as_vector_or_IVT_tRNA" type="textarea" autosize />
              </td>
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
            <tr v-if="showRow(record['sup-tRNA_gene']) || isEditing(record)">
              <td><b>Gene sequence:</b></td>
              <td style="font-family: monospace;">
                <template v-if="!isEditing(record)">{{ record['sup-tRNA_gene'] }}</template>
                <el-input v-else v-model="record._draft['sup-tRNA_gene']" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record['Sequence_of_sup-tRNA']) || isEditing(record)">
              <td><b>sup-tRNA sequence:</b></td>
              <td style="font-family: monospace;">
                <template v-if="!isEditing(record)">{{ record['Sequence_of_sup-tRNA'] }}</template>
                <el-input v-else v-model="record._draft['Sequence_of_sup-tRNA']" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record['Secondary structure of sup-trna']) || isEditing(record)">
              <td><b>Secondary structure:</b></td>
              <td style="font-family: monospace;">
                <template v-if="!isEditing(record)">{{ record['Secondary structure of sup-trna'] }}</template>
                <el-input v-else v-model="record._draft['Secondary structure of sup-trna']" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Modification) || isEditing(record)">
              <td><b>Modification:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Modification }}</template>
                <el-input v-else v-model="record._draft.Modification" type="textarea" autosize />
              </td>
            </tr>
          </table>
          <h3>origin tRNA</h3>
          <table>
            <tr v-if="showRow(record.rnacentral_ID_of_origin_tRNA) || isEditing(record)">
              <td><b>Rnacentral ID:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.rnacentral_ID_of_origin_tRNA }}</template>
                <el-input v-else v-model="record._draft.rnacentral_ID_of_origin_tRNA" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record['tRNAscan-SE_ID_of_origin_tRNA']) || isEditing(record)">
              <td><b>tRNAscan-SE ID:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record['tRNAscan-SE_ID_of_origin_tRNA'] }}</template>
                <el-input v-else v-model="record._draft['tRNAscan-SE_ID_of_origin_tRNA']" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Species_source_of_origin_tRNA) || isEditing(record)">
              <td><b>Species source:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.Species_source_of_origin_tRNA }}</template>
                <el-input v-else v-model="record._draft.Species_source_of_origin_tRNA" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.aa_and_anticodon_of_origin_tRNA) || isEditing(record)">
              <td><b>AA and Anticodon:</b></td>
              <td>
                <template v-if="!isEditing(record)">{{ record.aa_and_anticodon_of_origin_tRNA }}</template>
                <el-input v-else v-model="record._draft.aa_and_anticodon_of_origin_tRNA" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record.Sequence_of_origin_tRNA) || isEditing(record)">
              <td><b>Origin-tRNA sequence:</b></td>
              <td style="font-family: monospace;">
                <template v-if="!isEditing(record)">{{ record.Sequence_of_origin_tRNA }}</template>
                <el-input v-else v-model="record._draft.Sequence_of_origin_tRNA" type="textarea" autosize />
              </td>
            </tr>
            <tr v-if="showRow(record['Secondary structure']) || isEditing(record)">
              <td><b>Secondary structure:</b></td>
              <td style="font-family: monospace;">
                <template v-if="!isEditing(record)">{{ record['Secondary structure'] }}</template>
                <el-input v-else v-model="record._draft['Secondary structure']" type="textarea" autosize />
              </td>
            </tr>
          </table>
          <h3 v-if="hasEngineeredData(record) || isEditing(record)">Engineered site</h3>
          <table v-if="hasEngineeredData(record) || isEditing(record)">
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

            <tr v-if="(showRow(record['Secondary structure']) && showRow(record['Secondary structure of sup-trna'])) || isEditing(record)">
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
<tr v-if="hasEngineeredData(record) || isEditing(record)">
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

    <!-- 警示提示 -->
    <div class="af3-warning">
      <small style="color: #a94442;">
        ⚠ Predicted by AlphaFold3, for visualization only. Accuracy not guaranteed.
      </small>
    </div>
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
import TranStructure from '@/components/TranStructure.vue';
import * as d3 from 'd3';
import { draw_cloverleaf, draw_base_distro } from '@/utils/tRNAviz/js/consensusESM.js';
import "@/utils/tRNAviz/css/explorer.css";
import { formatAlignment, loadCIFFile } from './expandedRowLogic';
import TrnaRadial from '@/components/TrnaRadial.vue';
import supTrnaRadial from '@/components/supTrnaRadial.vue';
import AlignmentTable from '@/components/AlignmentTable.vue';
import { ElButton, ElInput, ElMessage } from 'element-plus';

const API_BASE = ''; // 同源部署时留空

export default defineComponent({
  name: 'TRNATherapeutics-1',
  components: { TranStructure, TrnaRadial, supTrnaRadial, AlignmentTable, ElButton, ElInput },
  setup() {
    const route = useRoute();
    const id = route.params.key as string;

    const loading = ref(true);
    const showSup = ref(true);
    const records = ref<any[]>([]);
    const EDIT_MODE = computed(() => {
      try {
        return new URLSearchParams(window.location.search).get('edit') === '1';
      } catch {
        return false;
      }
    });

    // 后端接口（优先同源，其次可填你的服务地址）
    const API_ENDPOINTS = [
      '/search_table',
    ];

    const filteredRecords = computed(() => {
      // 一般后端已按 ENSURE_ID 精确返回；此处再保险过滤一下
      return records.value.filter((r: any) => String(r.ENSURE_ID) === String(id));
    });

    const isEditing = (rec: any) => !!rec._editing;

    const parseSup = (str: string) => {
      try { return JSON.parse(str); } catch { return []; }
    };

    const showRow = (val: any) => {
      if (val === undefined || val === null) return false;
      if (Array.isArray(val)) return val.length > 0;
      return String(val).trim() !== '';
    };

    const hasEngineeredData = (rec: any) => {
      const sup = parseSup(rec.js_sup_tRNA);
      const origin = parseSup(rec.js_origin_tRNA);
      const score = parseSup(rec.pairwise_score);
      return (
        (Array.isArray(sup) && sup.length > 0) ||
        (Array.isArray(origin) && origin.length > 0) ||
        (Array.isArray(score) && score.length > 0) ||
        showRow(rec['Secondary structure']) ||
        showRow(rec['Secondary structure of sup-trna']) ||
        showRow(rec.pdbid)
      );
    };

    async function fetchByEnsureId(ensureId: string): Promise<boolean> {
      const payload = {
        table: 'Engineered_sup_tRNA',
        column: 'ENSURE_ID',
        value: ensureId,
        mode: 'exact',
        limit: 50
      };

      for (const ep of API_ENDPOINTS) {
        try {
          const controller = new AbortController();
          const t = setTimeout(() => controller.abort(), 8000);
          const resp = await fetch(ep, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: controller.signal
          });
          clearTimeout(t);
          if (!resp.ok) continue;

          const data = await resp.json();
          if (data?.error) continue;

          const rows: any[] = Array.isArray(data?.results) ? data.results : [];
          records.value = rows.map((x: any, i: number) => ({
            ...x,
            key: x.ENSURE_ID || `${ensureId}-${i}`,
            // 方便模板里使用的链接字段
            ENSURE_ID_link: x.ENSURE_ID_link || `#/${ensureId}`
          }));

          return true;
        } catch {
          // 尝试下一个端点
        }
      }
      return false;
    }

    function switchSample(record: any, sampleIdx: number) {
      record._selectedSample = sampleIdx;
      loadCIFFile(record.pdbid, record.ENSURE_ID, sampleIdx);
    }

    const enterEdit = (rec: any) => {
      if (!EDIT_MODE.value) return;
      rec._editing = true;
      rec._draft = { ...rec };
    };

    const cancelEdit = (rec: any) => {
      rec._editing = false;
      rec._draft = null;
    };

    const saveEdit = async (rec: any) => {
      if (!EDIT_MODE.value) return;
      const ensureId = rec.ENSURE_ID || rec._draft?.ENSURE_ID;
      if (!ensureId) {
        ElMessage.error('ENSURE_ID missing');
        return;
      }
      const updates: Record<string, any> = { ...(rec._draft || {}) };
      try {
        const resp = await fetch(`${API_BASE}/engineered_sup_trna/update`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ENSURE_ID: ensureId, updates })
        });
        const json = await resp.json();
        if (!resp.ok || json?.error) throw new Error(json?.error || 'Save failed');
        Object.assign(rec, rec._draft);
        rec._editing = false;
        ElMessage.success('Saved');
      } catch (e: any) {
        ElMessage.error(e?.message || 'Save failed');
      }
    };

    onMounted(async () => {
      try {
        await fetchByEnsureId(id);
        await nextTick();

        // 初始化每条记录的 3D / 对齐格式化（若字段存在）
        filteredRecords.value.forEach((record: any) => {
          record._selectedSample = 0;
          if (record.pdbid) {
            loadCIFFile(record.pdbid, record.ENSURE_ID, 0);
          }
          try {
            if (record.Alignment) {
              record.formattedAlignment = formatAlignment(record.Alignment);
            }
          } catch {}
        });

        // 可视化底图（按需保留）
        d3.json("https://minio.lumoxuan.cn/ensure/trnaviz/ala.json")
          .then(plotData => {
            draw_cloverleaf(plotData, "Ala", "https://minio.lumoxuan.cn/ensure/trnaviz/ala.json");
            draw_base_distro(plotData, 'cloverleaf');
          })
          .catch(() => {});
      } finally {
        loading.value = false;
      }
    });

    const CITE_TEXT =
      'Sprinzl M, Vassilenko KS. Compilation of tRNA sequences and sequences of tRNA genes.\n' +
      'Nucleic Acids Res. 2005 Jan 1;33(Database issue):D139-40.\n' +
      'doi: 10.1093/nar/gki012. PMID: 15608164; PMCID: PMC539966';
    const CITE_LINK = 'https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gki012';

    return {
      id,
      loading,
      filteredRecords,
      parseSup,
      showRow,
      showSup,
      hasEngineeredData,
      switchSample,
      CITE_TEXT,
      CITE_LINK,
      EDIT_MODE,
      isEditing,
      enterEdit,
      cancelEdit,
      saveEdit
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

.header-actions {
  display: flex;
  justify-content: flex-end;
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
.af3-warning {
  margin-top: 6px;
  font-size: 12px;
  color: #a94442; /* 红色提示 */
  font-style: italic;
}

</style>
