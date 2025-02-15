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
    // 在 setup() 中添加这个函数
    const formatAlignment = (alignment: string) => {
  console.log('原始比对数据：', alignment);
  
  // 按照 <br> 分割行
  const lines = alignment.split('<br>').map(line => line.trim()).filter(line => line.length > 0);
  console.log('分行后的数据：', lines);

  let html = '';

  // 确保每组三行：Query、符号行和 Sbjct
  if (lines.length % 3 !== 0) {
    console.error("比对数据格式不符合预期！行数不是 3 的倍数");
    return ''; // 如果数据不符合预期格式，直接返回空字符串
  }

  // 按照每组三行进行处理
  for (let i = 0; i < lines.length; i += 3) {
    const queryLine = lines[i];   // Query 行
    const matchLine = lines[i + 1]; // 符号行（|、-）
    const sbjctLine = lines[i + 2];  // Sbjct 行

    console.log(`处理第 ${i / 3 + 1} 组数据：`);
    console.log('Query Line:', queryLine);
    console.log('Match Line:', matchLine);
    console.log('Sbjct Line:', sbjctLine);

    // 提取 Query 和 Sbjct 的碱基序列
    const querySeq = extractSequence(queryLine);
    const sbjctSeq = extractSequence(sbjctLine);
    const matchSymbols = matchLine.trim().split('');  // 符号行（|、-）

    console.log('Query 序列：', querySeq);
    console.log('Sbjct 序列：', sbjctSeq);
    console.log('符号行：', matchSymbols);

    // 生成高亮HTML
    html += generateHighlightedHTML(querySeq, matchSymbols, sbjctSeq);
  }

  return html;
};

// 提取序列中的碱基
const extractSequence = (line: string) => {
  const parts = line.split(/\s+/); // 按空格分割，获取碱基序列
  const sequence = parts.slice(2, parts.length - 1).join(''); // 碱基序列应该从第三部分到倒数第二部分
  return sequence;
};

// 生成高亮的HTML
const generateHighlightedHTML = (query: string, symbols: string[], sbjct: string) => {
  let html = '';
  let queryIndex = 0;  // 用来追踪 Query 序列位置
  let sbjctIndex = 0;  // 用来追踪 Sbjct 序列位置

  // 处理 Query 行的高亮
  for (let i = 0; i < symbols.length; i++) {
    const symbol = symbols[i];

    // 如果是缺失位置 (-)，则跳过碱基
    if (symbol === '-') {
      html += `<span class="gap">${symbol}</span>`;
      continue;
    }

    // 如果是匹配或不匹配的碱基
    const queryChar = query[queryIndex++];
    const sbjctChar = sbjct[sbjctIndex++];

    console.log(`Query Char: ${queryChar}, Sbjct Char: ${sbjctChar}, Symbol: ${symbol}`);  // 输出当前字符和符号
    html += `<span class="${getCharClass(queryChar, sbjctChar, symbol)}">${queryChar}</span>`;
  }
  html += '\n';

  // 处理 符号行的高亮
  symbols.forEach((symbol) => {
    html += `<span class="${getSymbolClass(symbol)}">${symbol}</span>`;
  });
  html += '\n';

  // 处理 Sbjct 行的高亮
  sbjctIndex = 0;  // 重置 sbjctIndex
  for (let i = 0; i < symbols.length; i++) {
    const symbol = symbols[i];
    // 如果是缺失位置 (-)，则跳过碱基
    if (symbol === '-') {
      html += `<span class="gap">${symbol}</span>`;
      continue;
    }

    // 查询对应位置的 Sbjct 字符
    const sbjctChar = sbjct[sbjctIndex++];
    const queryChar = query[i];
    console.log(`Sbjct Char: ${sbjctChar}, Query Char: ${queryChar}, Symbol: ${symbol}`);  // 输出当前字符和符号
    html += `<span class="${getCharClass(queryChar, sbjctChar, symbol)}">${sbjctChar}</span>`;
  }
  html += '\n';

  return html;
};

// 根据比对符号返回字符的高亮样式
const getCharClass = (char: string, otherChar: string, symbol: string) => {
  console.log(`字符比对 - Char: ${char}, OtherChar: ${otherChar}, Symbol: ${symbol}`);  // 输出当前的字符比对
  if (char === '-' || otherChar === '-') return 'gap'; // 缺失
  return symbol === '|' ? 'match' : 'mismatch'; // 匹配或不匹配
};

// 根据比对符号返回符号的高亮样式
const getSymbolClass = (symbol: string) => {
  console.log(`符号行比对 - Symbol: ${symbol}`);  // 输出当前符号行
  if (symbol === '|') return 'match-symbol';   // 匹配
  if (symbol === '-') return 'gap-symbol';     // 缺失
  return 'mismatch-symbol';  // 不匹配
};


    const route = useRoute(); // 获取当前路由信息
    const id = route.params.key; // 获取key参数

    const { searchText, filteredDataSource, loadData } = useTableData('https://minio.lumoxuan.cn/ensure/tRNAtherapeutics.csv');
    const loading = ref(true);

    const filteredRecords = computed(() => {
      console.log('过滤记录时 ENSURE_ID:', id);
      return filteredDataSource.value.filter(record => record.ENSURE_ID == id);
    });

    onMounted(async () => {
      try {
        // console.log('开始加载 CSV 数据...');
        await loadData();
        // console.log('CSV 数据加载完成，全部数据:', filteredDataSource.value);
        await nextTick(); // 确保DOM已完全渲染
        // console.log('DOM 渲染完成，开始加载 PDB 文件');
        filteredRecords.value.forEach(record => {
          // console.log('处理记录：', record);
          // console.log('Record.Index:', record.Index, 'Record.ENSURE_ID:', record.ENSURE_ID);
          // 注意：此处传入 record.Index 作为确保文件名和容器 id 一致，请确认Index与ENSURE_ID是否一致
          loadPDBFile(record.Index, record.ENSURE_ID);
          record.formattedAlignment = formatAlignment(record.Alignment);
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
      const pdbFilePath = `https://minio.lumoxuan.cn/ensure/pdb/ensure-${fileId}.pdb`;
      // console.log(`尝试加载 PDB 文件: ${pdbFilePath}`);
      // console.log('检查 3Dmol 对象:', $3Dmol);

      axios
        .get(pdbFilePath)
        .then(response => {
          // console.log(`PDB 文件加载成功, fileId: ${fileId}`, response.data);
          const elementId = 'pdb-container-' + containerId;
          // console.log('尝试查找 DOM 元素，id:', elementId);
          const element = document.getElementById(elementId);

          if (element) {
            // console.log(`找到元素 ${elementId}，尺寸:`, element.offsetHeight, element.offsetWidth);
            if ($3Dmol.createViewer) {
              // console.log('3Dmol.createViewer 可用，开始创建 viewer');
              try {
                const viewer = $3Dmol.createViewer(element, { backgroundColor: 'white' });
                // console.log('Viewer 创建成功:', viewer);
                viewer.addModel(response.data, 'pdb');
                // console.log('模型添加成功，数据:', response.data);
                viewer.setStyle({}, { cartoon: { color: 'spectrum' } });
                // console.log('模型样式设置成功');
                viewer.zoomTo();
                // console.log('调用 zoomTo()');
                viewer.render();
                // console.log('调用 render() 完成，3Dmol 渲染完成');
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

/* 碱基匹配样式 */
::v-deep .match { 
  color: #4CAF50 !important; /* 强制应用绿色 */
}        
::v-deep .mismatch { 
  color: #F44336 !important;  /* 强制应用红色 */
}     
::v-deep .gap { 
  color: #9E9E9E !important; /* 强制应用灰色 */
}  

/* 符号行样式 */
::v-deep .match-symbol { 
  color: #4CAF50 !important; /* 强制应用绿色 */
} 
::v-deep .mismatch-symbol { 
  color: #F44336 !important;  /* 强制应用红色 */
}
::v-deep.gap-symbol { 
  color: #9E9E9E !important; /* 强制应用灰色 */
}

</style>
