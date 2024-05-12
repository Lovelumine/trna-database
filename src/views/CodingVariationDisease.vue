<template>
  <div class="site--main">
    <h2>Coding variation Disease</h2>
    <!-- 顶部行包含尺寸调整和搜索框 -->
    <div class="top-controls">
            <!-- 搜索框 -->
            <div class="search-box" style="margin-bottom: 10px">
        <input v-model="searchText" @input="filterData" placeholder="输入搜索内容" class="search-input">
      </div>
            <!-- 调整尺寸 -->
      <div class="size-controls" style="margin-bottom: 10px">
        <el-radio-group v-model="tableSize" >
          <el-radio-button label="small" >小尺寸</el-radio-button>
          <el-radio-button label="default">默认尺寸</el-radio-button>
          <el-radio-button label="large">大尺寸</el-radio-button>
        </el-radio-group>
      </div>
    </div>
    <!-- 表格组件 -->
    <s-table-provider :hover="true">
      <s-table
        :theme-color="themeColor"
        :columns="columns"
        :data-source="filteredDataSource"
        :row-key="record => record.key"
        :pagination="pagination"
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
            <p><b>突变类型:</b> {{ record.mutationType }}</p>
            <p><b>疾病名称:</b> {{ record.diseaseName }}</p>
            <p><b>Phenotype MIM number:</b> {{ record.Phenotype }}</p>
            <p><b>致病基因:</b> {{ record.gene }}</p>
            <p><b>Gene/Locus MIM number:</b> {{ record.Locus }}</p>
            <p><b>变异位点:</b> {{ record.mutationSite }}</p>
            <p><b>原有密码子及氨基酸:</b> {{ record.originalCodon }}</p>
            <p><b>突变后密码子及氨基酸:</b> {{ record.mutatedCodon }}</p>
            <p><b>染色体:</b> {{ record.chromosome }}</p>
            <p><b>Genome position:</b> {{ record.Genomeposition }}</p>
            <p><b>de novo / inherited:</b> {{ record.denovoinherited }}</p>
            <p><b>发病率:</b> {{ record.incidenceRate }}</p>
            <p><b>zygosity:</b> {{ record.zygosity }}</p>
            <p><b>诊断/治病方案:</b> {{ record.treatmentPlan }}</p>
            <p><b>参考文献:</b> <a :href="record.References" target="_blank" class="tilt-hover">参考文献</a></p>
            <p><b>来源:</b> <a :href="record.source" target="_blank" class="tilt-hover">链接</a></p>
          </div>
        </template>
      </s-table>
    </s-table-provider>
  </div>
</template>



<script lang="tsx">
import { STableProvider } from '@shene/table'
import { ref, defineComponent, onMounted, computed } from 'vue';
import Papa from 'papaparse';
import type { STableColumnsType } from '@shene/table'; 

// 定义数据类型
interface DataType {
  key: string;
  mutationType: string;
  diseaseName: string;
  Phenotype:string;
  gene: string;
  Locus: string;
  mutationSite: string;
  originalCodon: string;
  mutatedCodon: string;
  chromosome: string;
  Genomeposition: string;
  denovoinherited: string;
  zygosity: string;
  incidenceRate: string;
  treatmentPlan: string;
  References: string;
  source: string;
}

export default defineComponent({
  name: 'CodingVariationDisease',
  setup() {
    const searchText = ref('');
    const allData = ref<DataType[]>([]);
      const filteredDataSource = computed(() => {
  if (!searchText.value) return allData.value;
  return allData.value.filter(item => 
    Object.keys(item).some(key => 
      item[key] !== null && item[key] !== undefined &&
      item[key].toString().toLowerCase().includes(searchText.value.toLowerCase())
    )
  );
});



    const columns: STableColumnsType<DataType> = [
      {
        title: '突变类型',
        dataIndex: 'mutationType',
        width: 120,
        key: 'mutationType',
        resizable: true,
        filter: {
          type: 'multiple',
          list: [
            {
              text: 'missense',
              value: 'missense'
            },
            {
              text: 'nonsense',
              value: 'nonsense'
            }
          ],
          onFilter: (value, record) => value.includes(record.mutationType)
        }
      },
      { title: '疾病名称', width: 420, dataIndex: 'diseaseName', key: 'diseaseName', resizable: true },
      { title: 'Phenotype MIM number', width: 200, dataIndex: 'Phenotype', key: 'Phenotype', resizable: true },
      { title: '致病基因', width: 120, dataIndex: 'gene', key: 'gene', resizable: true },
      { title: 'Gene/Locus MIM number', width: 200, dataIndex: 'Locus', key: 'Locus', resizable: true },
      { title: '变异位点', width: 120, dataIndex: 'mutationSite', key: 'mutationSite', resizable: true },
      { title: '原有密码子及氨基酸', width: 140, dataIndex: 'originalCodon', key: 'originalCodon', resizable: true },
      { title: '突变后密码子及氨基酸', width: 180, dataIndex: 'mutatedCodon', key: 'mutatedCodon', resizable: true },
      { title: '染色体', width: 120, dataIndex: 'chromosome', key: 'chromosome', resizable: true },  
      { title: 'Genome position', width: 220, dataIndex: 'Genomeposition', key: 'Genomeposition', resizable: true },        
      {
        title: 'de novo / inherited',
        dataIndex: 'denovoinherited',
        width: 180,
        key: 'denovoinherited',
        resizable: true,
        filter: {
          type: 'multiple',
          list: [
            {
              text: 'de novo',
              value: 'de novo'
            },
            {
              text: 'inherited',
              value: 'inherited'
            }
          ],
          onFilter: (value, record) => value.includes(record.denovoinherited)
        }
      },
      {
        title: '发病率',
        width: 720,
        dataIndex: 'incidenceRate',
        key: 'incidenceRate',
        resizable: true,
        sorter: (a, b) => parseFloat(a.incidenceRate) - parseFloat(b.incidenceRate)
      },
      { title: 'zygosity', width: 140, dataIndex: 'zygosity', key: 'zygosity', resizable: true },
      { title: '诊断/治疗方案', width: 720, dataIndex: 'treatmentPlan', key: 'treatmentPlan', resizable: true },
      {title: '参考文献',width: 120,key: 'References',dataIndex: 'References',customRender:({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">来源</a></div>
		),resizable: true
	},
      {title: '来源',width: 120,key: 'source',dataIndex: 'source',customRender:({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">来源</a></div>
		),resizable: true
	}
    ];
    const hover = ref(true)
    const themeColor = ref('#E80B0E');  // 主题颜色
    const pagination = ref({
      defaultCurrent: 1,
      defaultPageSize: 10,
      showQuickJumper: true,
      showSizeChanger: true,
      showTotal: total => `共 ${total} 项数据`
    });

    const tableSize = ref('default'); // 新增尺寸状态

    const rowExpandable = (record: DataType) => true;
    const expandRowByClick = ref(true);
    const expandIconColumnIndex = ref(0);

    onMounted(() => {
      fetch('/data/coding variation Disease v1.1.csv')
        .then(response => response.text())
        .then(csvData => {
          Papa.parse(csvData, {
            header: true,
            delimiter: ',',
            skipEmptyLines: true,
            dynamicTyping: true,
            complete: (results) => {
              const filledData = results.data.map((item, index) => {
                return { key: index.toString(), ...item };
              });
              allData.value = filledData;
              pagination.value.total = filledData.length;
            }
          });
        });
    });


    return {
      columns,
      filteredDataSource,
      pagination,
      expandRowByClick,
      expandIconColumnIndex,
      tableSize,
      searchText,
    };
  }
});
</script>

