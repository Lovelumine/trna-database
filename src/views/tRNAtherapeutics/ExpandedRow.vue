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
            <tr v-if="record.Delivery_as_vector_or_IVT_tRNA === 'IVT_tRNA'">
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
              <td style="font-family: monospace;">{{ record['sup-tRNA_gene'] }}</td>
            </tr>
            <tr>
              <td><b>tRNA sequence:</b></td>
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
              <td><b>tRNA sequence:</b></td>
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
                <pre v-html="record.Alignment"></pre>
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
                {{ console.log('Record key:', record.key, 'Secondary structure:', record['Secondary structure'], 'Sup-tRNA sequence:', record['Sequence_of_sup-tRNA']) }}
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
import { defineComponent, ref, onMounted, computed, nextTick } from 'vue';
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
    const route = useRoute(); // 获取当前路由信息
    const id = route.params.key; // 获取key参数

    const { searchText, filteredDataSource, loadData } = useTableData('/src/assets/data/tRNAtherapeutics.csv');
    const loading = ref(true);

    const filteredRecords = computed(() => {
      console.log('过滤记录时 ENSURE_ID:', id);
      return filteredDataSource.value.filter(record => record.ENSURE_ID == id);
    });

    onMounted(async () => {
      try {
        console.log('开始加载 CSV 数据...');
        await loadData();
        console.log('CSV 数据加载完成，全部数据:', filteredDataSource.value);
        await nextTick(); // 确保DOM已完全渲染
        console.log('DOM 渲染完成，开始加载 PDB 文件');
        filteredRecords.value.forEach(record => {
          console.log('处理记录：', record);
          console.log('Record.Index:', record.Index, 'Record.ENSURE_ID:', record.ENSURE_ID);
          // 注意：此处传入 record.Index 作为确保文件名和容器 id 一致，请确认Index与ENSURE_ID是否一致
          loadPDBFile(record.Index, record.ENSURE_ID);
        });
      } catch (error) {
        console.error('加载数据时出错:', error);
      } finally {
        loading.value = false;
      }
    });

    /**
     * 加载指定 ENSURE_ID 的 PDB 文件
     * @param {string} fileId - 用于构造 PDB 文件路径的标识（例如 record.Index）
     * @param {string} containerId - 用于在 DOM 中查找容器的标识（例如 record.ENSURE_ID）
     */
    const loadPDBFile = (fileId: string, containerId: string) => {
      const pdbFilePath = `/src/assets/data/pdb/ensure-${fileId}.pdb`;
      console.log(`尝试加载 PDB 文件: ${pdbFilePath}`);
      console.log('检查 3Dmol 对象:', $3Dmol);

      axios
        .get(pdbFilePath)
        .then(response => {
          console.log(`PDB 文件加载成功, fileId: ${fileId}`, response.data);
          const elementId = 'pdb-container-' + containerId;
          console.log('尝试查找 DOM 元素，id:', elementId);
          const element = document.getElementById(elementId);

          if (element) {
            console.log(`找到元素 ${elementId}，尺寸:`, element.offsetHeight, element.offsetWidth);
            if ($3Dmol.createViewer) {
              console.log('3Dmol.createViewer 可用，开始创建 viewer');
              try {
                const viewer = $3Dmol.createViewer(element, { backgroundColor: 'white' });
                console.log('Viewer 创建成功:', viewer);
                viewer.addModel(response.data, 'pdb');
                console.log('模型添加成功，数据:', response.data);
                viewer.setStyle({}, { cartoon: { color: 'spectrum' } });
                console.log('模型样式设置成功');
                viewer.zoomTo();
                console.log('调用 zoomTo()');
                viewer.render();
                console.log('调用 render() 完成，3Dmol 渲染完成');
              } catch (viewerError) {
                console.error('创建 viewer 或渲染过程中出错:', viewerError);
              }
            } else {
              console.error('错误: 3Dmol.createViewer 不可用');
            }
          } else {
            console.error(`错误: 未找到 id 为 ${elementId} 的 DOM 元素`);
          }
        })
        .catch(error => {
          console.error(`加载 PDB 文件失败, fileId: ${fileId}`, error);
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
