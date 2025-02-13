<!-- src/views/tRNAtherapeutics/tRNAtherapeutics.vue -->
<template>
  <div class="site--main">
    <h2>Engineered Sup-tRNA</h2>

    <!-- PMID选择表格 -->
    <div class="table-section">
      <s-table-provider :hover="true" :locale="locale">
        <s-table
          :columns="pmidColumns"
          :data-source="paginatedPmidData"
          :row-key="record => record.PMID"
          :row-selection="rowSelection"
          :pagination="pagination"
          :stripe="true"
          :show-sorter-tooltip="true"
          @change="handleTableChange"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'PMID'">
              <a :href="`https://pubmed.ncbi.nlm.nih.gov/${record.PMID}`" target="_blank">
                {{ record.PMID }}
              </a>
            </template>
          </template>
        </s-table>
      </s-table-provider>
    </div>

    <!-- 根据选择PMID展示的表格 -->
    <div class="table-section">
      <tRNAtherapeutics1 :selectedPmids="selectedPmids" />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { STableProvider } from '@shene/table';
import Papa from 'papaparse';
import tRNAtherapeutics1 from './tRNAtherapeutics-1.vue';

import en from '@shene/table/dist/locale/en';
const locale = ref(en);

export default {
  name: 'tRNAtherapeutics',
  components: {
    tRNAtherapeutics1,
    STableProvider
  },
  setup() {

    // PMID表格配置
    const pmidColumns = ref([
      {
        title: 'PMID',
        dataIndex: 'PMID',
        key: 'PMID',
        width: 40,
      },
      {
        title: 'Title',
        dataIndex: 'Title',
        key: 'Title',
        width: 300,
        ellipsis: true
      },
      {
        title: 'Source',
        dataIndex: 'Source',
        key: 'Source',
        width: 150,
        filters: [
          { text: 'Nature', value: 'Nature' },
          { text: 'Science', value: 'Science' },
          { text: 'Cell', value: 'Cell' }
        ],
        onFilter: (value, record) => record.Source.includes(value)
      },
      {
        title: 'Author',
        dataIndex: 'Author',
        key: 'Author',
        width: 200,
        ellipsis: true
      },
      {
        title: 'PubDate',
        dataIndex: 'PubDate',
        key: 'PubDate',
        width: 120,
      }
    ]);

    // 数据状态
    const rawPmidData = ref([]);
    const selectedPmids = ref([]);
    const pagination = ref({
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true
    });

    // 分页数据
    const paginatedPmidData = computed(() => {
      const start = (pagination.value.current - 1) * pagination.value.pageSize;
      const end = start + pagination.value.pageSize;
      return rawPmidData.value.slice(start, end);
    });

    // 多选配置
    const rowSelection = ref({
      selectedRowKeys: selectedPmids,
      onChange: (selectedKeys) => {
        selectedPmids.value = selectedKeys;
      },
      preserveSelectedRowKeys: true
    });

    // 加载CSV数据
    onMounted(async () => {
      const response = await fetch('https://minio.lumoxuan.cn/ensure/pmid_article_info_extended.csv');
      const csvText = await response.text();

      Papa.parse(csvText, {
        complete: (result) => {
          rawPmidData.value = result.data.slice(1).map(row => ({
            PubDate: formatDate(row[0]),
            Source: row[1],
            Author: formatAuthors(row[2]),
            Title: row[3],
            PMID: String(row[4])
          }));
          pagination.value.total = rawPmidData.value.length;
        },
        skipEmptyLines: true,
        header: false
      });
    });

    // 表格变化处理
    const handleTableChange = (pag, filters, sorter) => {
      if (pag) {
        pagination.value = { ...pagination.value, ...pag };
      }
    };

    // 辅助方法
    const formatDate = (dateStr) => {
      // 实现日期格式化逻辑
      return new Date(dateStr).toLocaleDateString();
    };

    const formatAuthors = (authorsStr) => {
      // 实现作者格式化逻辑
      return authorsStr.split(',').slice(0, 3).join(', ') + ' et al.';
    };

    return {
      locale,
      pmidColumns,
      paginatedPmidData,
      pagination,
      rowSelection,
      selectedPmids,
      handleTableChange
    };
  }
};
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.table-section {
  margin-bottom: 30px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
}

::v-deep .s-table {
  border-radius: 8px;
  overflow: hidden;
}

::v-deep .s-table-header {
  background: #fafafa;
}

::v-deep .s-table-row:hover {
  background: #f5f7fa !important;
}
</style>