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
    <s-table-provider :hover="true">
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
import { ElTooltip } from 'element-plus';
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
      { title: 'Gene Name', dataIndex: 'GENE_NAME', width: 150, ellipsis: true, key: 'GENE_NAME', resizable: true },
      { title: 'Ensembl ID', dataIndex: 'ENSEMBL_ID', width: 180, ellipsis: true, key: 'ENSEMBL_ID', resizable: true },
      { title: 'Mutation URL', dataIndex: 'MUTATION_URL', width: 120, ellipsis: true, key: 'MUTATION_URL', customRender: ({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">Link</a></div>),
        resizable: true },
      { title: 'Legacy Mutation ID', dataIndex: 'LEGACY_MUTATION_ID', width: 150, ellipsis: true, key: 'LEGACY_MUTATION_ID', resizable: true },
      { title: 'Genomic Mutation ID', dataIndex: 'GENOMIC_MUTATION_ID', width: 170, ellipsis: true, key: 'GENOMIC_MUTATION_ID', resizable: true },
      { title: 'Mutation Locus in GRCh37', dataIndex: 'MUTATION_LOCUS_IN_GRCh37', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh37', resizable: true },
      { title: 'Mutation Locus in GRCh38', dataIndex: 'MUTATION_LOCUS_IN_GRCh38', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh38', resizable: true },
      { title: 'Mutation Type', dataIndex: 'MUTATION_TYPE', width: 150, ellipsis: true, key: 'MUTATION_TYPE', resizable: true },
      { title: 'Mutation CDS', dataIndex: 'MUTATION_CDS', width: 150, ellipsis: true, key: 'MUTATION_CDS', resizable: true },
      { title: 'Genomic Ref Allele', dataIndex: 'GENOMIC_REF_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_REF_ALLELE', resizable: true },
      { title: 'Genomic Mut Allele', dataIndex: 'GENOMIC_MUT_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_MUT_ALLELE', resizable: true },
      { 
        title: 'Disease', 
        dataIndex: 'DISEASE', 
        width: 1200, 
        ellipsis: true, 
        key: 'DISEASE', 
        resizable: true,
      }
    ];

    return {
      columns,
      filteredDataSource,
      tableSize,
      searchText,
      renderDiseaseTooltip
    };
  }
});
</script>
