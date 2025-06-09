<template>
  <div class="blast-results-container">
    <div class="blast-results">
      <h2>BLAST Results</h2>
      <s-table
        :columns="columns"
        :data-source="filteredDataSource"
        :expand-icon-column-index="expandIconColumnIndex"
        :expand-row-by-click="expandRowByClick"
        @expand="onExpand"
        @expandedRowsChange="onExpandedRowsChange"
      >
        <template #bodyCell="{ text, column, record }">
          <template v-if="column.key === 'title'">
            <div v-for="(line, i) in record.stitleLines" :key="i">
              <strong>{{ line.key }}:</strong> {{ line.value }}
            </div>
          </template>
          <template v-else>
            {{ text }}
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <div class="more-detail">
            <p class="title"><b>Query Sequence:</b></p>
            <p class="content">{{ record.qseq }}</p>
            <br />
            <p class="title"><b>Subject Sequence:</b></p>
            <p class="content">{{ record.sseq }}</p>
            <br />
            <p class="title"><b>Title:</b></p>
            <div v-for="(line, i) in record.stitleLines" :key="i">
              <strong>{{ line.key }}:</strong> {{ line.value }}
            </div>
          </div>
        </template>
      </s-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, watch } from 'vue';

const props = defineProps({
  blastResult: {
    type: String,
    required: true
  }
});

const columns = [
  { title: 'Query ID', dataIndex: 'qseqid', key: 'qseqid', width: 120 },
  { title: 'Subject ID', dataIndex: 'sseqid', key: 'sseqid', width: 120 },
  { title: 'Percent Identity', dataIndex: 'pident', key: 'pident', width: 150 },
  { title: 'Alignment Length', dataIndex: 'length', key: 'length', width: 150 },
  { title: 'Mismatches', dataIndex: 'mismatch', key: 'mismatch', width: 120 },
  { title: 'Gap Openings', dataIndex: 'gapopen', key: 'gapopen', width: 120 },
  { title: 'Query Start', dataIndex: 'qstart', key: 'qstart', width: 120 },
  { title: 'Query End', dataIndex: 'qend', key: 'qend', width: 120 },
  { title: 'Subject Start', dataIndex: 'sstart', key: 'sstart', width: 120 },
  { title: 'Subject End', dataIndex: 'send', key: 'send', width: 120 },
  { title: 'E-value', dataIndex: 'evalue', key: 'evalue', width: 120 },
  { title: 'Bit Score', dataIndex: 'bitscore', key: 'bitscore', width: 120 }
];

const dataSource = computed(() => {
  if (!props.blastResult) return [];
  return props.blastResult.split('\n').filter(line => line.trim()).map((line, index) => {
    const fields = line.split('\t');
    const stitle = fields[14] || '';
    const stitleLines = stitle.split(' ').reduce((acc, part) => {
      const [key, ...values] = part.split(':');
      if (values.length > 0) {
        acc.push({ key, value: values.join(':') });
      } else if (acc.length > 0) {
        acc[acc.length - 1].value += ` ${part}`;
      }
      return acc;
    }, []);

    return {
      key: index.toString(),
      qseqid: fields[0],
      sseqid: fields[1],
      pident: fields[2],
      length: fields[3],
      mismatch: fields[4],
      gapopen: fields[5],
      qstart: fields[6],
      qend: fields[7],
      sstart: fields[8],
      send: fields[9],
      evalue: fields[10],
      bitscore: fields[11],
      qseq: fields[12],
      sseq: fields[13],
      stitle,
      stitleLines
    };
  });
});

const filteredDataSource = computed(() => {
  // 忽略第一行
  return dataSource.value.slice(1);
});

const hideExpandIcon = ref(false);
const expandRowByClick = ref(true);
const expandIconColumnIndex = ref(0);

watch(hideExpandIcon, newValue => {
  expandIconColumnIndex.value = newValue ? -1 : 0;
});

const onExpand = (expanded, record) => {
  console.log('expanded', expanded);
  console.log('record', record);
};

const onExpandedRowsChange = keys => {
  console.log('keys', keys);
};
</script>

<style scoped>
.blast-results-container {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.blast-results {
  width: 60%;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow: hidden; /* 移除滚动条 */
  padding: 20px;
}

.more-detail {
  line-height: 22px;
}
.more-detail > p {
  display: inline-block;
  margin: 4px 0;
}
.more-detail > p.title {
  width: 120px;
}

@media (max-width: 600px) {
  .blast-results {
    max-width: 80vw;
  }
}
</style>
