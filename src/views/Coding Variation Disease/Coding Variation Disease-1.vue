<template>
  <div class="site--main">
    <h2>Coding Variation Disease</h2>
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
    <s-table-provider :hover="true" :theme-color="'#00ACF5'" :locale="locale">
      <s-table
        :columns="columns"
        :data-source="filteredDataSource"
        :row-key="record => record.key"
        :stripe="true"
        :show-sorter-tooltip="true"
        :size="tableSize"
        :expand-row-by-click="true"
      >
        <template #expandedRowRender="{ record }">
          <div>
            <p><b>Mutation Type:</b> {{ record.mutationType }}</p>
            <p><b>Disease Name:</b> {{ record.diseaseName }}</p>
            <p><b>Phenotype MIM Number:</b> {{ record.Phenotype }}</p>
            <p><b>GenBank Accession Number:</b> {{ record.GenBankaccessionnumber}}</p>
            <p><b>Gene:</b> {{ record.gene }}</p>
            <p><b>Gene/Locus MIM Number:</b> {{ record.Locus }}</p>
            <p><b>Mutation Site:</b> {{ record.mutationSite }}</p>
            <p><b>Original Codon and Amino Acid:</b> {{ record.originalCodon }}</p>
            <p><b>Mutated Codon and Amino Acid:</b> {{ record.mutatedCodon }}</p>
            <p><b>Chromosome:</b> {{ record.chromosome }}</p>
            <p><b>Genome Position:</b> {{ record.Genomeposition }}</p>
            <p><b>De Novo / Inherited:</b> {{ record.denovoinherited }}</p>
            <p><b>Zygosity:</b> {{ record.zygosity }}</p>
            <p><b>Incidence Rate:</b> {{ record.incidenceRate }}</p>
            <p><b>Diagnostic Method:</b> {{ record.DiagnosticMethod }}</p>
            <p><b>References:</b> <a :href="record.References" target="_blank" class="tilt-hover">References</a></p>
            <p><b>Source:</b> <a :href="record.source" target="_blank" class="tilt-hover">Link</a></p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption  } from 'element-plus';
import { STableProvider } from '@shene/table';
import type { STableColumnsType } from '@shene/table';
import { useTableData } from '../../assets/js/useTableData.js';

// 定义数据类型
type DataType = { [key: string]: string };

  import en from '@shene/table/dist/locale/en'
  const locale = ref(en)

export default defineComponent({
  name: 'CodingVariationDisease',
  components: {
    ElTag,
    ElSpace,
    ElSelect,
    ElOption
  },
  setup() {
    const { searchText, filteredDataSource, loadData ,searchColumn} = useTableData('/data/PTC in Genetic Disease.csv');
    const tableSize = ref('default'); // 表格尺寸状态

    onMounted(() => {
      loadData();
    });

    const selectedColumns = ref<string[]>([
      'mutationType',
      'diseaseName',
      'gene',
      'originalCodon',
      'mutatedCodon',

  ])
    const allColumns: STableColumnsType<DataType> = [
      {
        title: 'Mutation Type',
        dataIndex: 'mutationType',
        width: 140, ellipsis: true,
        key: 'mutationType',
        resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'Missense', value: 'Missense' },
            { text: 'Nonsense', value: 'Nonsense' }
          ],
          onFilter: (value, record) => value.includes(record.mutationType)
        }
      },
      { title: 'Disease Name', dataIndex: 'diseaseName', width: 320, ellipsis: true, key: 'diseaseName', resizable: true },
      { title: 'Phenotype MIM Number', dataIndex: 'Phenotype', width: 200, ellipsis: true, key: 'Phenotype', resizable: true },
      { title: 'GenBank Accession Number', dataIndex: 'GenBankaccessionnumber', width: 200, ellipsis: true, key: 'GenBankaccessionnumber', resizable: true },
      { title: 'Gene', dataIndex: 'gene', width: 120, ellipsis: true, key: 'gene', resizable: true },
      { title: 'Gene/Locus MIM Number', dataIndex: 'Locus', width: 200, ellipsis: true, key: 'Locus', resizable: true },
      { title: 'Mutation Site', dataIndex: 'mutationSite', width: 120, ellipsis: true, key: 'mutationSite', resizable: true },
      { title: 'Original Codon and Amino Acid', dataIndex: 'originalCodon', width: 240, ellipsis: true, key: 'originalCodon', resizable: true },
      { title: 'Mutated Codon and Amino Acid', dataIndex: 'mutatedCodon', width: 240, ellipsis: true, key: 'mutatedCodon', resizable: true },
      { title: 'Chromosome', dataIndex: 'chromosome', width: 120, ellipsis: true, key: 'chromosome', resizable: true },
      { title: 'Genome Position', dataIndex: 'Genomeposition', width: 220, ellipsis: true, key: 'Genomeposition', resizable: true },
      {
        title: 'De Novo / Inherited',
        dataIndex: 'denovoinherited',
        width: 180, ellipsis: true,
        key: 'denovoinherited',
        resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'de novo', value: 'de novo' },
            { text: 'inherited', value: 'inherited' },
            { text: 'de novo / inherited', value: 'de novo / inherited' },
            { text: 'uncertain', value: 'uncertain' },
          ],
          onFilter: (value, record) => value.includes(record.denovoinherited)
        }
      },
      { title: 'Zygosity', dataIndex: 'zygosity', width: 140, ellipsis: true, key: 'zygosity', resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'heterozygous', value: 'heterozygous' },
            { text: 'hemizygous', value: 'hemizygous' },
            { text: 'homozygous', value: 'homozygous' },
          ],
          onFilter: (value, record) => value.includes(record.zygosity)
        } },
      {
        title: 'Incidence Rate',
        dataIndex: 'incidenceRate',
        width: 320, ellipsis: true,
        key: 'incidenceRate',
        resizable: true,
        sorter: (a, b) => parseFloat(a.incidenceRate) - parseFloat(b.incidenceRate)
      },
      { title: 'Diagnostic Method', dataIndex: 'DiagnosticMethod', width: 320, ellipsis: true, key: 'DiagnosticMethod', resizable: true },
      {
        title: 'References', width: 120, ellipsis: true, key: 'References', dataIndex: 'References',
        customRender: ({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">References</a></div>),
        resizable: true
      },
      {
        title: 'Source', width: 120, ellipsis: true, key: 'source', dataIndex: 'source',
        customRender: ({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">Link</a></div>),
        resizable: true
      }
    ];

    const displayedColumns = computed(() =>
      allColumns.filter(column => selectedColumns.value.includes(column.key as string))
    );

    return {
      columns: displayedColumns,
      filteredDataSource,
      tableSize,
      searchText,
      locale,
      selectedColumns,
      searchColumn,
      displayedColumns,
      allColumns // 列选择控件
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
