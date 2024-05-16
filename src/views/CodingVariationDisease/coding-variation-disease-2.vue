<template>
    <div class="site--main">
      <h2>Coding variation in Cancer</h2>
      <!-- 顶部行包含尺寸调整和搜索框 -->
      <div class="top-controls">
        <!-- 搜索框 -->
        <div class="search-box" style="margin-bottom: 10px">
          <input v-model="searchText" placeholder="输入搜索内容" class="search-input">
        </div>
        <!-- 调整尺寸 -->
        <div class="size-controls" style="margin-bottom: 10px">
          <el-radio-group v-model="tableSize">
            <el-radio-button label="small">小尺寸</el-radio-button>
            <el-radio-button label="default">默认尺寸</el-radio-button>
            <el-radio-button label="large">大尺寸</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <!-- 表格组件 -->
      <s-table-provider :hover="true" :theme-color="'#00ACF5'">
        <s-table
          :columns="columns"
          :data-source="filteredDataSource"
          :row-key="record => record.key"
          :pagination="pagination"
          :stripe="true"
          :show-sorter-tooltip="true"
          :size="tableSize"
          @sorter-change="onSorterChange"
          @resize-column="onResizeColumn"
          @pagination-change="onPaginationChange"
          :row-expandable="rowExpandable"
          :expand-icon-column-index="expandIconColumnIndex"
          :expand-row-by-click="expandRowByClick"
          @expand="onExpand"
          @expandedRowsChange="onExpandedRowsChange"
        >
          <template #expandedRowRender="{ record }">
            <div>
              <p><b>GENE NAME:</b> {{ record.GENE_NAME }}</p>
              <p><b>ENSEMBL ID:</b> {{ record.ENSEMBL_ID }}</p>
              <p><b>MUTATION URL:</b> <a :href="record.MUTATION_URL" target="_blank">{{ record.MUTATION_URL }}</a></p>
              <p><b>LEGACY MUTATION ID:</b> {{ record.LEGACY_MUTATION_ID }}</p>
              <p><b>GENOMIC MUTATION ID:</b> {{ record.GENOMIC_MUTATION_ID }}</p>
              <p><b>MUTATION LOCUS IN GRCh37:</b> {{ record.MUTATION_LOCUS_IN_GRCh37 }}</p>
              <p><b>MUTATION LOCUS IN GRCh38:</b> {{ record.MUTATION_LOCUS_IN_GRCh38 }}</p>
              <p><b>MUTATION TYPE:</b> {{ record.MUTATION_TYPE }}</p>
              <p><b>MUTATION CDS:</b> {{ record.MUTATION_CDS }}</p>
              <p><b>GENOMIC REF ALLELE:</b> {{ record.GENOMIC_REF_ALLELE }}</p>
              <p><b>GENOMIC MUT ALLELE:</b> {{ record.GENOMIC_MUT_ALLELE }}</p>
              <p><b>DISEASE:</b> {{ record.DISEASE }}</p>
            </div>
          </template>
        </s-table>
      </s-table-provider>
    </div>
  </template>
  
  <script lang="tsx">
  import { defineComponent, ref, onMounted } from 'vue';
  import { STableProvider } from '@shene/table';
  import type { STableColumnsType } from '@shene/table';
  import { useTableData } from '../../assets/js/useTableData.js';
  
  // 定义数据类型
  type DataType = { [key: string]: string };
  
  export default defineComponent({
    name: 'CodingVariationDisease2',
    setup() {
      const { searchText, filteredDataSource, loadData } = useTableData('/data/coding variation in Caner.csv');
      const tableSize = ref('default'); // 表格尺寸状态
  
      onMounted(() => {
        loadData();
      });
  
      const columns: STableColumnsType<DataType> = [
        { title: 'GENE NAME', dataIndex: 'GENE_NAME', width: 150, ellipsis: true, key: 'GENE_NAME', resizable: true },
        { title: 'ENSEMBL ID', dataIndex: 'ENSEMBL_ID', width: 150, ellipsis: true, key: 'ENSEMBL_ID', resizable: true },
        { title: 'MUTATION URL', dataIndex: 'MUTATION_URL', width: 200, ellipsis: true, key: 'MUTATION_URL', resizable: true },
        { title: 'LEGACY MUTATION ID', dataIndex: 'LEGACY_MUTATION_ID', width: 150, ellipsis: true, key: 'LEGACY_MUTATION_ID', resizable: true },
        { title: 'GENOMIC MUTATION ID', dataIndex: 'GENOMIC_MUTATION_ID', width: 150, ellipsis: true, key: 'GENOMIC_MUTATION_ID', resizable: true },
        { title: 'MUTATION LOCUS IN GRCh37', dataIndex: 'MUTATION_LOCUS_IN_GRCh37', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh37', resizable: true },
        { title: 'MUTATION LOCUS IN GRCh38', dataIndex: 'MUTATION_LOCUS_IN_GRCh38', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh38', resizable: true },
        { title: 'MUTATION TYPE', dataIndex: 'MUTATION_TYPE', width: 150, ellipsis: true, key: 'MUTATION_TYPE', resizable: true },
        { title: 'MUTATION CDS', dataIndex: 'MUTATION_CDS', width: 150, ellipsis: true, key: 'MUTATION_CDS', resizable: true },
        { title: 'GENOMIC REF ALLELE', dataIndex: 'GENOMIC_REF_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_REF_ALLELE', resizable: true },
        { title: 'GENOMIC MUT ALLELE', dataIndex: 'GENOMIC_MUT_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_MUT_ALLELE', resizable: true },
        { title: 'DISEASE', dataIndex: 'DISEASE', width: 200, ellipsis: true, key: 'DISEASE', resizable: true }
      ];
  
      return {
        columns,
        filteredDataSource,
        tableSize,
        searchText,
      };
    }
  });
  </script>
  