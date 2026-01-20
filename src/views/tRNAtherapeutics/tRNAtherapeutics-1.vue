<template>
  <div class="site--main">
    <!-- 线性进度条：supData 加载时显示 -->
    <el-progress
      v-if="loadingSup"
      :percentage="100"
      :indeterminate="true"
      :stroke-width="4"
      :show-text="false"
      style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000"
    />

    <div class="content-wrapper">
      <TableToolbar
        v-model="searchText"
        v-model:column="searchColumn"
        v-model:size="tableSize"
        v-model:selected-columns="selectedColumns"
        :search-columns="allColumns"
        :display-columns="allColumns"
      >
        <template #actions>
          <div v-if="EDIT_MODE" class="edit-controls">
            <el-button type="primary" @click="openCreate">New Entry</el-button>
          </div>
        </template>
      </TableToolbar>

      <s-table-provider :hover="true" :locale="locale">
        <s-table
          :columns="columns"
          :data-source="filteredDataSource"
          :row-key="computeRowKey"
          :stripe="true"
          :show-sorter-tooltip="true"
          :size="tableSize"
        >
          <template #bodyCell="{ text, column, record }">
            <template v-if="column.key === 'Citation'">
              <a>{{ text }}</a>
            </template>
            <template v-else-if="column.key === 'Related_disease'">
              <ElSpace>
                <ElTag
                  v-for="item in record.Related_disease.split(';').map(str => str.trim())"
                  :key="item"
                  :type="item === 'cystic fibrosis'
                    ? 'danger'
                    : item === 'Model protein'
                    ? 'info'
                    : 'success'"
                >
                  {{ item }}
                </ElTag>
              </ElSpace>
            </template>
          </template>
        </s-table>
      </s-table-provider>
    </div>

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isCreate ? 'New Entry' : 'Edit Entry'"
      width="70%"
      top="5vh"
      append-to-body
      :close-on-click-modal="false"
      class="edit-dialog"
    >
      <el-form label-width="160px" class="edit-form">
        <el-form-item v-for="col in allColumns" :key="col.key" :label="col.title as string">
          <el-input
            v-model="editForm[col.dataIndex]"
            :placeholder="col.dataIndex"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSave">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="tsx">
import { defineComponent, ref, computed, reactive } from 'vue';
import { ElTag, ElSpace, ElSelect, ElOption, ElProgress, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElMessage } from 'element-plus';
import { STableProvider } from '@shene/table';
import { allColumns } from './columns';
import TranStructure from '@/components/TranStructure.vue';
import en from '@shene/table/dist/locale/en';
import TableToolbar from '@/components/TableToolbar.vue';

const locale = ref(en);
const API_BASE = ''; // 同源部署时留空，否则填后端域名

export default defineComponent({
  name: 'tRNAtherapeutics1',
  components: {
    ElTag,
    ElSpace,
    ElSelect,
    ElOption,
    ElProgress,
    ElButton,
    ElDialog,
    ElForm,
    ElFormItem,
    ElInput,
    TranStructure,
    STableProvider,
    TableToolbar,
  },
  props: {
    selectedPmids:  { type: Array as () => string[], required: true },
    supData:        { type: Array as () => any[], required: true },
    loadingSup:     { type: Boolean, required: true },
  },
  setup(props) {
    // 编辑模式标识：URL ?edit=1 时开启
    const EDIT_MODE = computed(() => {
      try {
        return new URLSearchParams(window.location.search).get('edit') === '1';
      } catch {
        return false;
      }
    });

    // 本地搜索、大小、列控制
    const searchText      = ref('');
    const searchColumn    = ref('');
    const tableSize       = ref<'small'|'default'|'large'>('default');
    const selectedColumns = ref<string[]>([
      'PTC_gene',
      'Species_source_of_origin_tRNA',
      'aa_and_anticodon_of_sup-tRNA',
      'Reaction_system',
      'pre_ENSURE_ID',
      'Reading_through_efficiency'
    ]);

    // 计算要显示的列
    const columns = computed(() => {
      const baseCols = allColumns.filter(col => selectedColumns.value.includes(col.key as string));
      if (EDIT_MODE.value) {
        baseCols.push({
          title: 'Actions',
          key: 'actions',
          dataIndex: 'actions',
          width: 140,
          customRender: ({ record }: any) => (
            <div class="action-cell">
              <ElButton size="small" type="primary" onClick={() => openEdit(record)}>Edit</ElButton>
              <ElButton size="small" type="danger" plain style="margin-left:6px" onClick={() => handleDelete(record)}>Delete</ElButton>
            </div>
          )
        } as any);
      }
      return baseCols;
    });

    // 根据 PMIDs + 本地搜索 过滤 supData
    const filteredDataSource = computed(() => {
      let data = props.supData;
      if (props.selectedPmids.length) {
        data = data.filter(r => props.selectedPmids.includes(String(r.PMID)));
      }
      if (searchText.value) {
        data = data.filter(r => {
          const hay = (searchColumn.value
            ? String(r[searchColumn.value])
            : Object.values(r).join(' ')
          ).toLowerCase();
          return hay.includes(searchText.value.toLowerCase());
        });
      }
      return data;
    });

    // 动态计算 rowKey
    const computeRowKey = (record: any) => {
      // 确保返回一个有效的唯一标识符（如 ENSURE_ID、PMID 或 key）
      return record.ENSURE_ID || record.PMID || record.key || record['Index'] || `row-${Math.random()}`;
    };

    // ===== 编辑/新增对话框 =====
    const editDialogVisible = ref(false);
    const isCreate = ref(false);
    const editingRow = ref<any | null>(null);
    const editForm = reactive<Record<string, any>>({});

    const resetForm = () => {
      Object.keys(editForm).forEach(k => delete editForm[k]);
    };

    const openEdit = (row: any) => {
      if (!EDIT_MODE.value) return;
      isCreate.value = false;
      editingRow.value = row;
      resetForm();
      allColumns.forEach(col => {
        editForm[col.dataIndex] = row[col.dataIndex] ?? '';
      });
      editForm.ENSURE_ID = row.ENSURE_ID;
      editDialogVisible.value = true;
    };

    const openCreate = () => {
      if (!EDIT_MODE.value) return;
      isCreate.value = true;
      editingRow.value = null;
      resetForm();
      allColumns.forEach(col => {
        editForm[col.dataIndex] = '';
      });
      // 默认填入当前展开的 PMID（如果只有一个选中 PMID）
      if (props.selectedPmids.length === 1) {
        editForm.PMID = props.selectedPmids[0];
      }
      editDialogVisible.value = true;
    };

    const handleSave = async () => {
      const ensureId = editForm.ENSURE_ID || editForm.ensure_id;
      if (!ensureId) {
        ElMessage.error('ENSURE_ID is required');
        return;
      }
      const payload = isCreate.value
        ? { ...editForm, ENSURE_ID: ensureId }
        : { ENSURE_ID: ensureId, updates: { ...editForm } };
      const url = isCreate.value
        ? `${API_BASE}/engineered_sup_trna/create`
        : `${API_BASE}/engineered_sup_trna/update`;
      try {
        const resp = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const json = await resp.json();
        if (!resp.ok || json?.error) throw new Error(json?.error || 'Save failed');
        ElMessage.success(isCreate.value ? 'Created' : 'Updated');
        editDialogVisible.value = false;
        // 本地更新数据
        if (isCreate.value) {
          (props.supData as any[]).unshift({ ...editForm });
        } else if (editingRow.value) {
          const idx = (props.supData as any[]).findIndex(r => computeRowKey(r) === computeRowKey(editingRow.value));
          if (idx >= 0) (props.supData as any[])[idx] = { ...editingRow.value, ...editForm };
        }
      } catch (e: any) {
        ElMessage.error(e?.message || 'Save failed');
      }
    };

    const handleDelete = async (row: any) => {
      if (!EDIT_MODE.value) return;
      const ensureId = row.ENSURE_ID || row.ensure_id;
      if (!ensureId) {
        ElMessage.error('ENSURE_ID missing');
        return;
      }
      try {
        const resp = await fetch(`${API_BASE}/engineered_sup_trna/delete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ENSURE_ID: ensureId })
        });
        const json = await resp.json();
        if (!resp.ok || json?.error) throw new Error(json?.error || 'Delete failed');
        ElMessage.success('Deleted');
        const idx = (props.supData as any[]).findIndex(r => computeRowKey(r) === computeRowKey(row));
        if (idx >= 0) (props.supData as any[]).splice(idx, 1);
      } catch (e: any) {
        ElMessage.error(e?.message || 'Delete failed');
      }
    };

    return {
      locale,
      columns,
      filteredDataSource,
      tableSize,
      searchText,
      searchColumn,
      selectedColumns,
      allColumns,
      computeRowKey, // 返回 computeRowKey 方法
      EDIT_MODE,
      editDialogVisible,
      isCreate,
      editForm,
      openEdit,
      openCreate,
      handleSave,
      handleDelete
    };
  }
});
</script>

<style scoped>
.site--main {
  padding: 20px;
}
.content-wrapper {
  display: flex;
  flex-direction: column;
}
.edit-controls {
  margin-left: 12px;
}
.action-cell {
  display: flex;
  align-items: center;
}
.action-cell :deep(.el-button) {
  padding: 4px 10px;
}
.edit-dialog :deep(.el-dialog__body) {
  max-height: 70vh;
  overflow: auto;
}
.edit-form {
  max-height: 65vh;
  overflow: auto;
}
</style>
