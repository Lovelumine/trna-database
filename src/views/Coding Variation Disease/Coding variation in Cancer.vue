<template>
  <div class="site--main">
    <h2>Coding Variation in Cancer</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
    <div class="top-controls">
      <!-- 搜索框 -->
      <div class="search-box">
        <input v-model="searchText" placeholder="Enter search content" class="search-input">
        <el-select v-model="searchColumn" placeholder="Select column to search" class="search-column-select">
          <el-option :key="'all'" :label="'All columns'" :value="''" />
          <el-option
            v-for="column in allColumns"
            :key="column.key"
            :value="column.dataIndex"
          />
        </el-select>
      </div>
      <!-- 调整尺寸 -->
      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize">
          <el-radio-button value="small">Small Size</el-radio-button>
          <el-radio-button value="default">Default Size</el-radio-button>
          <el-radio-button value="large">Large Size</el-radio-button>
        </el-radio-group>
      </div>
      <!-- 选择显示列 -->
      <div class="column-controls" style="margin-bottom: 10px">
        <el-select v-model="selectedColumns" multiple placeholder="Select columns to display" collapse-tags class="column-select">
          <el-option
            v-for="column in allColumns"
            :key="column.key"
            :label="column.title as string"
            :value="column.key"
          />
        </el-select>
      </div>
    </div>
    <!-- 表格组件 -->
    <s-table-provider :hover="true" :locale="locale">
      <s-table
        :columns="displayedColumns"
        :data-source="filteredDataSource"
        :row-key="record => record.key"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
      >
        <template #bodyCell="{ text, column, record }">
          <template v-if="column.key === 'DISEASE'">
            <ElSpace>
              <ElTag v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
                {{ items }}
              </ElTag>
            </ElSpace>
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Gene Name:</b> {{ record.GENE_NAME }}</p>
            <p><b>Ensembl ID:</b> {{ record.ENSEMBL_ID }}</p>
            <p><b>Genomic Mutation ID:</b> <a :href="record.GENOMIC_MUTATION_URL" target="_blank" class="tilt-hover">{{ record.GENOMIC_MUTATION_ID }}</a></p>
            <p><b>Legacy Mutation ID:</b><a :href="record.LEGACY_MUTATION_URL" target="_blank" class="tilt-hover">{{ record.LEGACY_MUTATION_ID }}</a></p>
            <p><b>Mutation Locus in GRCh37:</b> {{ record.MUTATION_LOCUS_IN_GRCh37 }}</p>
            <p><b>Mutation Locus in GRCh38:</b> {{ record.MUTATION_LOCUS_IN_GRCh38 }}</p>
            <p><b>Mutation Type:</b> {{ record.MUTATION_TYPE }}</p>
            <p><b>Mutation CDS:</b> {{ record.MUTATION_CDS }}</p>
            <p><b>MUTATION AA:</b> {{ record.MUTATION_AA }}</p>            
            <p><b>Genomic Ref Allele:</b> {{ record.GENOMIC_REF_ALLELE }}</p>
            <p><b>Genomic Mut Allele:</b> {{ record.GENOMIC_MUT_ALLELE }}</p>
            <p><b>Disease:</b>
              <ElSpace>
                <ElTag v-for="items in (Array.isArray(record.DISEASE) ? record.DISEASE : record.DISEASE.split(';').map(str => str.trim()))" :key="items" :type="getTagType(items)">
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
import { defineComponent, ref, onMounted, computed,watch } from 'vue';
import { ElTooltip, ElTag, ElSpace, ElSelect, ElOption } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';
import {getTagType} from '../../utils/tag.js'

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
  MUTATION_AA: string;
  GENOMIC_REF_ALLELE: string;
  GENOMIC_MUT_ALLELE: string;
  DISEASE: string[]; // 修改为数组类型
  tags: string[];
};

// 定义允许的标签类型
type TagType = 'success' | 'warning' | 'info' | 'primary' | 'danger';

import en from '@shene/table/dist/locale/en'
  const locale = ref(en)

export default defineComponent({
  name: 'CodingVariationDisease2',
  components: {
    ElTooltip,
    ElTag,
    ElSpace,
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource, searchColumn,loadData } = useTableData('/data/PTC in Cancer.csv', (data) => {
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
    const selectedColumns = ref<string[]>([
      'GENE_NAME',
      'MUTATION_LOCUS_IN_GRCh37',
      'MUTATION_LOCUS_IN_GRCh38',
      'MUTATION_TYPE',
      'DISEASE'
    ]);

    onMounted(async() => {
      await loadData();
      triggerColumnChange();
    });

    const triggerColumnChange = () => {
      // 模拟点击列选择控件以触发数据刷新
      selectedColumns.value = [...selectedColumns.value];
    };

    watch([tableSize, searchColumn, searchText, selectedColumns], async () => {
      await loadData();
    });

    const allColumns: STableColumnsType<DataType> = [
      { title: 'Mutation Type', dataIndex: 'MUTATION_TYPE', width: 150, ellipsis: true, key: 'MUTATION_TYPE', resizable: true ,        filter: {
          type: 'multiple',
          list: [
            { text: 'Missense', value: 'Missense' },
            { text: 'Nonsense', value: 'Nonsense' },
            {text:'Frameshift',value:'Frameshift'},
            {text:'Deletion-Frameshift',value:'Deletion-Frameshift'},
            {text:'Insertion-Frameshift',value:'Insertion-Frameshift'}
          ],
          onFilter: (value, record) => value.includes(record.MUTATION_TYPE)
        }},
      { title: 'Gene Name', dataIndex: 'GENE_NAME', width: 150, ellipsis: true, key: 'GENE_NAME', resizable: true },
      { title: 'Ensembl ID', dataIndex: 'ENSEMBL_ID', width: 180, ellipsis: true, key: 'ENSEMBL_ID', resizable: true },
      { title: 'Genomic Mutation ID', dataIndex: 'GENOMIC_MUTATION_ID', width: 120, ellipsis: true, key: 'GENOMIC_MUTATION_ID', resizable: true },
      { title: 'Genomic Mutation URL', dataIndex: 'GENOMIC_MUTATION_URL', width: 120, ellipsis: true, key: 'GENOMIC_MUTATION_URL', resizable: true },
      { title: 'Legacy Mutation ID', dataIndex: 'LEGACY_MUTATION_ID', width: 150, ellipsis: true, key: 'LEGACY_MUTATION_ID', resizable: true },
      { title: 'Legacy Mutation URL', dataIndex: 'LEGACY_MUTATION_URL', width: 150, ellipsis: true, key: 'LEGACY_MUTATION_URL', resizable: true },
      { title: 'Mutation Locus in GRCh37', dataIndex: 'MUTATION_LOCUS_IN_GRCh37', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh37', resizable: true },
      { title: 'Mutation Locus in GRCh38', dataIndex: 'MUTATION_LOCUS_IN_GRCh38', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh38', resizable: true },
      { title: 'Mutation CDS', dataIndex: 'MUTATION_CDS', width: 150, ellipsis: true, key: 'MUTATION_CDS', resizable: true },
      { title: 'MUTATION AA', dataIndex: 'MUTATION_AA', width: 150, ellipsis: true, key: 'MUTATION_AA', resizable: true },
      { title: 'Genomic Ref Allele', dataIndex: 'GENOMIC_REF_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_REF_ALLELE', resizable: true },
      { title: 'Genomic Mut Allele', dataIndex: 'GENOMIC_MUT_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_MUT_ALLELE', resizable: true },
      { title: 'Disease', dataIndex: 'DISEASE', width: 1200, ellipsis: true, key: 'DISEASE', resizable: true }
    ];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      displayedColumns,
      locale,
      searchColumn,
      selectedColumns,
      allColumns, // 列选择控件
      getTagType // 获取标签类型
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

.size-controls, .column-controls {
  display: flex;
  align-items: center;
}

.column-select {
  margin-left: 10px;
  width: 200px; /* 设置选择框的宽度 */
}
</style>
