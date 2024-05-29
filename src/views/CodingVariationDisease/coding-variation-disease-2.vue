<template>
  <div class="site--main">
    <h2>Coding Variation in Cancer</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box" style="margin-bottom: 10px">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
      </div>
      <!-- 调整尺寸 -->
      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize">
          <el-radio-button value="small">Small Size</el-radio-button>
          <el-radio-button value="default">Default Size</el-radio-button>
          <el-radio-button value="large">Large Size</el-radio-button>
        </el-radio-group>
      </div>
    </div>
    <!-- 表格组件 -->
    <s-table-provider :hover="true" :locale="locale" >
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
          <template v-if="column.key === 'name'">
            <a>{{ text }}</a>
          </template>
          <template v-else-if="column.key === 'DISEASE'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))" :key="items">
                {{ items }}
              </ElTag>
            </ElSpace>
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Gene Name:</b> {{ record.GENE_NAME }}</p>
            <p><b>Ensembl ID:</b> {{ record.ENSEMBL_ID }}</p>
            <p><b>Mutation URL:</b> <a :href="record.MUTATION_URL" target="_blank">{{ record.MUTATION_URL }}</a></p>
            <p><b>Legacy Mutation ID:</b> {{ record.LEGACY_MUTATION_ID }}</p>
            <p><b>Genomic Mutation ID:</b> {{ record.GENOMIC_MUTATION_ID }}</p>
            <p><b>Mutation Locus in GRCh37:</b> {{ record.MUTATION_LOCUS_IN_GRCh37 }}</p>
            <p><b>Mutation Locus in GRCh38:</b> {{ record.MUTATION_LOCUS_IN_GRCh38 }}</p>
            <p><b>Mutation Type:</b> {{ record.MUTATION_TYPE }}</p>
            <p><b>Mutation CDS:</b> {{ record.MUTATION_CDS }}</p>
            <p><b>Genomic Ref Allele:</b> {{ record.GENOMIC_REF_ALLELE }}</p>
            <p><b>Genomic Mut Allele:</b> {{ record.GENOMIC_MUT_ALLELE }}</p>
            <p><b>Disease:</b>
              <ElSpace>
                <ElTag v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))" :key="items">
                  {{ items }}
                </ElTag>
              </ElSpace>
            </p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted } from 'vue';
import { ElTooltip, ElTag, ElSpace } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';

// 定义数据类型
type DataType = {
  [key: string]: string | string[];
  GENE_NAME: string;
  ENSEMBL_ID: string;
  MUTATION_URL: string;
  LEGACY_MUTATION_ID: string;
  GENOMIC_MUTATION_ID: string;
  MUTATION_LOCUS_IN_GRCh37: string;
  MUTATION_LOCUS_IN_GRCh38: string;
  MUTATION_TYPE: string;
  MUTATION_CDS: string;
  GENOMIC_REF_ALLELE: string;
  GENOMIC_MUT_ALLELE: string;
  DISEASE: string[]; // 修改为数组类型
};

import en from '@shene/table/dist/locale/en'
  const locale = ref(en)

export default defineComponent({
  name: 'CodingVariationDisease2',
  components: {
    ElTooltip
  },
  setup() {
    const { searchText, filteredDataSource, loadData } = useTableData('/data/coding variation in Caner.csv', (data) => {
      // 在加载数据时将 DISEASE 列转换为数组
      return data.map(item => {
        // 处理DISEASE字段
        if (typeof item.DISEASE === 'string') {
          item.DISEASE = item.DISEASE.split(';').map(str => str.trim());
        }
        return item;
      });
    });

    const tableSize = ref('default'); // 表格尺寸状态

    onMounted(() => {
      loadData();
    });

    const renderDiseaseTooltip = (disease) => {
      // 确保 disease 是数组
      const diseaseArray = Array.isArray(disease) ? disease : disease.split(';').map(str => str.trim());
      return diseaseArray.map(item => item.split('/').join(' / ')).join('<br />');
    };

    const columns: STableColumnsType<DataType> = [
      { 
        title: 'Gene Name', 
        dataIndex: 'GENE_NAME', 
        width: 150, 
        ellipsis: true, 
        key: 'GENE_NAME', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="The gene name for which the data has been curated in COSMIC. In most cases this is the accepted HGNC symbol">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Ensembl ID', 
        dataIndex: 'ENSEMBL_ID', 
        width: 180, 
        ellipsis: true, 
        key: 'ENSEMBL_ID', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="The transcript identifier of the gene">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
  title: 'Mutation URL', 
  dataIndex: 'MUTATION_URL', 
  width: 120, 
  ellipsis: true, 
  key: 'MUTATION_URL', 
  resizable: true,
  customRender: ({ text }) => (
    <ElTooltip content="URL of mutation page on the main COSMIC site">
      <div>
        <a href={text || '#'} target="_blank" class="bracket-links">Link</a>
      </div>
    </ElTooltip>
  )
},

      { 
        title: 'Legacy Mutation ID', 
        dataIndex: 'LEGACY_MUTATION_ID', 
        width: 150, 
        ellipsis: true, 
        key: 'LEGACY_MUTATION_ID', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="Legacy mutation identifier (COSM) that represents existing COSM mutation identifiers">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Genomic Mutation ID', 
        dataIndex: 'GENOMIC_MUTATION_ID', 
        width: 170, 
        ellipsis: true, 
        key: 'GENOMIC_MUTATION_ID', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="Genomic mutation identifier (COSV) to indicate the definitive position of the variant on the genome. This identifier is trackable and stable between different versions of the release">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Mutation Locus in GRCh37', 
        dataIndex: 'MUTATION_LOCUS_IN_GRCh37', 
        width: 200, 
        ellipsis: true, 
        key: 'MUTATION_LOCUS_IN_GRCh37', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="The genomic coordinates of the mutation on the GRCh37 assembly">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Mutation Locus in GRCh38', 
        dataIndex: 'MUTATION_LOCUS_IN_GRCh38', 
        width: 200, 
        ellipsis: true, 
        key: 'MUTATION_LOCUS_IN_GRCh38', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="The genomic coordinates of the mutation on the GRCh38 assembly">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Mutation Type', 
        dataIndex: 'MUTATION_TYPE', 
        width: 150, 
        ellipsis: true, 
        key: 'MUTATION_TYPE', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="Type of mutation at the amino acid level (Only collected Nonsense mutations)">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Mutation CDS', 
        dataIndex: 'MUTATION_CDS', 
        width: 150, 
        ellipsis: true, 
        key: 'MUTATION_CDS', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="The change that has occurred in the nucleotide sequence. Formatting is based on the recommendations made by the Human Genome Variation Society (HGVS)">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Genomic Ref Allele', 
        dataIndex: 'GENOMIC_REF_ALLELE', 
        width: 150, 
        ellipsis: true, 
        key: 'GENOMIC_REF_ALLELE', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="Reference allele in the genomic change (on the forward strand)">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Genomic Mut Allele', 
        dataIndex: 'GENOMIC_MUT_ALLELE', 
        width: 150, 
        ellipsis: true, 
        key: 'GENOMIC_MUT_ALLELE', 
        resizable: true, 
        customRender: ({ text }) => (
          <ElTooltip content="Mutant allele in the genomic change (on the forward strand)">
            <span>{text}</span>
          </ElTooltip>
        )
      },
      { 
        title: 'Disease', 
        dataIndex: 'DISEASE', 
        width: 1200, 
        ellipsis: true, 
        key: 'DISEASE', 
        resizable: true,
        customRender: ({ text }) => (
          <ElTooltip content="Diseases with > 1% samples in COSMIC mutated (or frequency > 0.01), where disease = Primary site(tissue) / Primary histology / Sub-histology">
            <span>{text}</span>
          </ElTooltip>
        )
      }
    ];

    return {
      columns,
      filteredDataSource,
      tableSize,
      searchText,
      renderDiseaseTooltip,
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

.bracket-links {
  color: #409eff;
  text-decoration: none;
}

.bracket-links:hover {
  text-decoration: underline;
}
</style>
