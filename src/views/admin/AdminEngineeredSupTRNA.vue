<template>
  <div class="admin-page">
    <header class="admin-header">
      <div class="admin-header-copy">
        <p class="admin-eyebrow">ENSURE Admin</p>
        <h1>Engineered sup-tRNA 管理</h1>
        <p v-if="adminUser" class="admin-subtitle">
          当前登录：{{ adminUser.username }} · {{ adminUser.role }}
        </p>
        <div class="admin-status-row">
          <span class="admin-chip">{{ providerLabel }}</span>
          <span class="admin-chip">{{ activeModelLabel }}</span>
          <span class="admin-chip admin-chip--muted">{{ pagination.total }} records</span>
        </div>
      </div>

      <div class="admin-header-actions">
        <el-button @click="refreshAll" :loading="pageLoading">刷新</el-button>
        <el-button type="primary" @click="openCreate">新建条目</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </header>

    <section class="admin-overview">
      <article
        v-for="card in overviewCards"
        :key="card.label"
        class="admin-stat-card"
      >
        <p class="admin-stat-label">{{ card.label }}</p>
        <strong class="admin-stat-value">{{ card.value }}</strong>
        <span class="admin-stat-meta">{{ card.meta }}</span>
      </article>
    </section>

    <section class="admin-layout">
      <section class="admin-card admin-card--llm">
        <div class="admin-card-header">
          <div>
            <h2>LLM 配置</h2>
            <p>默认聊天模型走这里配置；保留 Ollama，同时支持 DeepSeek 和统一系统提示词。</p>
          </div>
          <el-button type="primary" :loading="llmSaving" @click="saveLLMConfig">保存 LLM 配置</el-button>
        </div>

        <div class="admin-form-grid llm-grid">
          <el-form-item label="当前 Provider" class="admin-form-item">
            <el-select v-model="llmForm.active_provider">
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="Ollama" value="ollama" />
            </el-select>
          </el-form-item>

          <el-form-item label="当前模型" class="admin-form-item">
            <el-select v-model="llmForm.active_model" filterable allow-create default-first-option>
              <el-option
                v-for="model in llmModelOptions"
                :key="model"
                :label="model"
                :value="model"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="超时（秒）" class="admin-form-item">
            <el-input-number v-model="llmForm.timeout" :min="5" :max="600" />
          </el-form-item>

          <el-form-item label="最大上下文消息数" class="admin-form-item">
            <el-input-number v-model="llmForm.max_messages" :min="1" :max="100" />
          </el-form-item>

          <el-form-item label="DeepSeek Base URL" class="admin-form-item">
            <el-input v-model="llmForm.deepseek_base_url" placeholder="https://api.deepseek.com" />
          </el-form-item>

          <el-form-item label="DeepSeek 默认模型" class="admin-form-item">
            <el-input v-model="llmForm.deepseek_default_model" placeholder="deepseek-chat" />
          </el-form-item>

          <el-form-item label="DeepSeek API Key" class="admin-form-item admin-form-item--full">
            <el-input
              v-model="llmForm.deepseek_api_key"
              type="password"
              show-password
              placeholder="sk-..."
            />
          </el-form-item>

          <el-form-item label="DeepSeek 模型列表" class="admin-form-item admin-form-item--full">
            <el-input
              v-model="llmForm.deepseek_models_text"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
              placeholder="deepseek-chat, deepseek-reasoner"
            />
          </el-form-item>

          <el-form-item label="Ollama Base URL" class="admin-form-item">
            <el-input v-model="llmForm.ollama_base_url" placeholder="http://127.0.0.1:11434" />
          </el-form-item>

          <el-form-item label="Ollama 默认模型" class="admin-form-item">
            <el-input v-model="llmForm.ollama_default_model" placeholder="qwen3:32b" />
          </el-form-item>

          <el-form-item label="Ollama 模型列表" class="admin-form-item admin-form-item--full">
            <el-input
              v-model="llmForm.ollama_models_text"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
              placeholder="qwen3:32b, gemma3:27b"
            />
          </el-form-item>

          <el-form-item label="系统提示词" class="admin-form-item admin-form-item--full">
            <el-input
              v-model="llmForm.system_prompt"
              type="textarea"
              :autosize="{ minRows: 6, maxRows: 12 }"
              placeholder="系统提示词"
            />
          </el-form-item>
        </div>
      </section>

      <aside class="admin-card admin-card--side">
        <div class="admin-card-header">
          <div>
            <h2>当前状态</h2>
            <p>把运行态信息、数据规模和最近动作收在一起，避免来回翻找。</p>
          </div>
        </div>

        <div class="admin-side-stack">
          <div class="admin-side-block">
            <span class="admin-side-label">默认聊天配置</span>
            <strong>{{ activeModelLabel }}</strong>
            <p>{{ providerLabel }} · 最多 {{ llmForm.max_messages }} 条上下文 · {{ llmModelOptions.length }} 个模型候选</p>
          </div>

          <div class="admin-side-block">
            <span class="admin-side-label">数据与搜索</span>
            <strong>{{ pagination.total }} records</strong>
            <p>{{ columns.length }} 列字段；当前默认搜索列 {{ searchColumn || 'ENSURE_ID' }}</p>
          </div>

          <div class="admin-side-block">
            <span class="admin-side-label">最近审计</span>
            <strong>{{ latestAuditTitle }}</strong>
            <p>{{ latestAuditMeta }}</p>
          </div>
        </div>
      </aside>
    </section>

    <section class="admin-card">
      <div class="admin-card-header">
        <div>
          <h2>Engineered sup-tRNA 数据表</h2>
          <p>支持按 ENSURE_ID / PMID / Gene / Disease 进行筛选、分页和行级编辑。</p>
        </div>
      </div>

      <TableToolbar
        v-model="searchText"
        v-model:column="searchColumn"
        v-model:size="tableSize"
        :search-columns="searchColumns"
        :show-columns="false"
        search-placeholder="输入 ENSURE_ID / PMID / Gene 等关键词"
        search-column-placeholder="选择搜索列"
      />

      <el-alert
        v-if="loadError"
        type="error"
        show-icon
        :closable="false"
        :title="loadError"
        style="margin-bottom: 12px"
      />

      <el-table
        v-loading="pageLoading"
        :data="rows"
        stripe
        border
        :size="tableSize"
        class="admin-table"
        empty-text="当前没有匹配的数据"
      >
        <el-table-column
          v-for="column in displayColumns"
          :key="column.prop"
          :prop="column.prop"
          :label="column.label"
          :min-width="column.minWidth"
          show-overflow-tooltip
        />

        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <div class="admin-row-actions">
              <el-button size="small" type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="admin-pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          :page-size="pagination.pageSize"
          :current-page="pagination.current"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
        />
      </div>
    </section>

    <section class="admin-card">
      <div class="admin-card-header">
        <div>
          <h2>最近审计日志</h2>
          <p>记录 create / update / delete / login / logout 操作。</p>
        </div>
        <el-button @click="loadAuditLogs">刷新日志</el-button>
      </div>

      <el-table :data="auditRows" border stripe size="small" empty-text="暂时没有审计记录">
        <el-table-column prop="created_at" label="时间" min-width="180" show-overflow-tooltip />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="动作" width="120" />
        <el-table-column prop="table_name" label="表" width="180" show-overflow-tooltip />
        <el-table-column prop="record_pk" label="主键" min-width="160" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="140" show-overflow-tooltip />
      </el-table>
    </section>

    <el-dialog
      v-model="dialogVisible"
      :title="isCreateMode ? '新建 Engineered sup-tRNA 条目' : '编辑 Engineered sup-tRNA 条目'"
      width="min(980px, 92vw)"
      top="4vh"
      destroy-on-close
    >
      <div class="admin-form-grid">
        <el-form-item
          v-for="column in formColumns"
          :key="column.name"
          :label="column.name"
          class="admin-form-item"
        >
          <el-input
            v-model="formState[column.name]"
            :disabled="!isCreateMode && column.name === 'ENSURE_ID'"
            :type="isTextarea(column.type) ? 'textarea' : 'text'"
            :autosize="isTextarea(column.type) ? { minRows: 2, maxRows: 6 } : undefined"
            :placeholder="column.name"
          />
        </el-form-item>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElButton, ElPagination, ElTable, ElTableColumn, ElDialog, ElInput, ElFormItem, ElMessage, ElMessageBox, ElAlert, ElSelect, ElOption, ElInputNumber } from 'element-plus';

import TableToolbar from '@/components/TableToolbar.vue';
import { adminJsonHeaders, fetchAdminAuditLogs, fetchAdminLLMSettings, fetchAdminSession, saveAdminLLMSettings, type AdminAuditRow, type AdminUser } from '@/utils/admin';
import { useTableData } from '@/utils/useTableData';

type ColumnMeta = {
  name: string;
  type: string;
};

const router = useRouter();

const adminUser = ref<AdminUser | null>(null);
const csrfToken = ref('');
const dialogVisible = ref(false);
const isCreateMode = ref(true);
const saving = ref(false);
const llmSaving = ref(false);
const loadError = ref('');
const auditRows = ref<AdminAuditRow[]>([]);
const columns = ref<ColumnMeta[]>([]);
const originalEnsureId = ref('');
const formState = reactive<Record<string, string>>({});
const llmForm = reactive({
  active_provider: 'ollama',
  active_model: '',
  timeout: 120,
  max_messages: 20,
  system_prompt: '',
  ollama_base_url: '',
  ollama_default_model: '',
  ollama_models_text: '',
  deepseek_base_url: '',
  deepseek_api_key: '',
  deepseek_default_model: '',
  deepseek_models_text: ''
});

const {
  rows,
  loading,
  searchText,
  searchColumn,
  tableSize,
  pagination,
  loadPage,
  handlePaginationUpdate,
  watchSearch
} = useTableData('Engineered_sup_tRNA', {
  pageSize: 20
});

const pageLoading = computed(() => loading.value || saving.value);
const providerLabel = computed(() => (llmForm.active_provider === 'deepseek' ? 'DeepSeek' : 'Ollama'));
const activeModelLabel = computed(() => {
  const active = String(llmForm.active_model || '').trim();
  if (active) return active;
  if (llmForm.active_provider === 'deepseek') {
    return String(llmForm.deepseek_default_model || '').trim() || 'deepseek-chat';
  }
  return String(llmForm.ollama_default_model || '').trim() || 'qwen3:32b';
});
const llmModelOptions = computed(() => {
  const raw = `${llmForm.ollama_models_text},${llmForm.deepseek_models_text}`;
  return raw
    .replace(/\n/g, ',')
    .split(',')
    .map((item) => item.trim())
    .filter((item, index, arr) => item && arr.indexOf(item) === index);
});
const latestAuditTitle = computed(() => {
  const latest = auditRows.value[0];
  if (!latest) return 'No activity yet';
  return `${latest.action || 'activity'} · ${latest.username || 'system'}`;
});
const latestAuditMeta = computed(() => {
  const latest = auditRows.value[0];
  if (!latest) return '登录、写操作和配置变更会出现在这里。';
  const rawTime = String(latest.created_at || '').replace('T', ' ').slice(0, 16);
  return [latest.table_name || 'app_settings', latest.record_pk || 'record', rawTime].filter(Boolean).join(' · ');
});
const overviewCards = computed(() => [
  {
    label: '默认模型',
    value: activeModelLabel.value,
    meta: `${providerLabel.value} · ${llmModelOptions.value.length} candidate models`
  },
  {
    label: '数据记录',
    value: new Intl.NumberFormat('en-US').format(Number(pagination.total || 0)),
    meta: 'Engineered_sup_tRNA'
  },
  {
    label: '字段数量',
    value: String(columns.value.length || 0),
    meta: searchColumn.value ? `默认搜索列 ${searchColumn.value}` : '等待列元数据'
  },
  {
    label: '最近审计',
    value: auditRows.value[0]?.action || 'No activity',
    meta: latestAuditMeta.value
  }
]);

const preferredColumns = [
  'ENSURE_ID',
  'PMID',
  'PTC_gene',
  'Related_disease',
  'Species_source_of_origin_tRNA',
  'aa_and_anticodon_of_sup-tRNA',
  'Reading_through_efficiency'
];

const displayColumns = computed(() => {
  const available = new Set(columns.value.map((column) => column.name));
  return preferredColumns
    .filter((name) => available.has(name))
    .map((name) => ({
      prop: name,
      label: name,
      minWidth: name === 'Related_disease' ? 260 : 180
    }));
});

const searchColumns = computed(() =>
  columns.value.map((column) => ({
    key: column.name,
    dataIndex: column.name,
    title: column.name
  }))
);

const formColumns = computed(() =>
  columns.value.filter((column) => column.name !== 'Index')
);

function resetForm() {
  Object.keys(formState).forEach((key) => {
    delete formState[key];
  });
}

function isTextarea(type: string) {
  return /text|json|blob/i.test(type);
}

async function ensureAdminSession() {
  const session = await fetchAdminSession();
  if (!session) {
    await router.replace('/admin/login');
    return false;
  }
  adminUser.value = session.user;
  csrfToken.value = session.csrf_token;
  return true;
}

async function loadColumns() {
  const resp = await fetch('/engineered_sup_trna/columns', {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  const json = await resp.json().catch(() => ({}));
  columns.value = Array.isArray(json?.columns)
    ? json.columns.map((item: any) => ({
        name: String(item?.name || ''),
        type: String(item?.type || '')
      })).filter((item: ColumnMeta) => item.name)
    : [];

  if (!searchColumn.value && columns.value.some((column) => column.name === 'ENSURE_ID')) {
    searchColumn.value = 'ENSURE_ID';
  }
}

async function loadAuditLogs() {
  auditRows.value = await fetchAdminAuditLogs(20);
}

async function loadLLMSettings() {
  const settings = await fetchAdminLLMSettings();
  if (!settings) return;
  llmForm.active_provider = settings.active_provider || 'ollama';
  llmForm.active_model = settings.active_model || '';
  llmForm.timeout = Number(settings.timeout || 120);
  llmForm.max_messages = Number(settings.max_messages || 20);
  llmForm.system_prompt = settings.system_prompt || '';
  llmForm.ollama_base_url = settings.ollama_base_url || '';
  llmForm.ollama_default_model = settings.ollama_default_model || '';
  llmForm.ollama_models_text = Array.isArray(settings.ollama_models) ? settings.ollama_models.join(', ') : '';
  llmForm.deepseek_base_url = settings.deepseek_base_url || '';
  llmForm.deepseek_api_key = settings.deepseek_api_key || '';
  llmForm.deepseek_default_model = settings.deepseek_default_model || '';
  llmForm.deepseek_models_text = Array.isArray(settings.deepseek_models) ? settings.deepseek_models.join(', ') : '';
}

async function refreshAll() {
  loadError.value = '';
  try {
    await loadPage();
    await loadAuditLogs();
  } catch (error: any) {
    loadError.value = error?.message || '加载数据失败';
  }
}

async function saveLLMConfig() {
  if (!csrfToken.value) {
    ElMessage.error('管理员会话已失效，请重新登录');
    await router.replace('/admin/login');
    return;
  }

  llmSaving.value = true;
  try {
    const settings = await saveAdminLLMSettings({
      csrfToken: csrfToken.value,
      active_provider: llmForm.active_provider,
      active_model: llmForm.active_model,
      timeout: llmForm.timeout,
      max_messages: llmForm.max_messages,
      system_prompt: llmForm.system_prompt,
      ollama_base_url: llmForm.ollama_base_url,
      ollama_default_model: llmForm.ollama_default_model,
      ollama_models: llmForm.ollama_models_text,
      deepseek_base_url: llmForm.deepseek_base_url,
      deepseek_api_key: llmForm.deepseek_api_key,
      deepseek_default_model: llmForm.deepseek_default_model,
      deepseek_models: llmForm.deepseek_models_text
    });
    llmForm.active_provider = settings.active_provider || llmForm.active_provider;
    llmForm.active_model = settings.active_model || llmForm.active_model;
    ElMessage.success('LLM 配置已保存');
    await loadAuditLogs();
  } catch (error: any) {
    ElMessage.error(error?.message || '保存 LLM 配置失败');
  } finally {
    llmSaving.value = false;
  }
}

function openCreate() {
  isCreateMode.value = true;
  originalEnsureId.value = '';
  resetForm();
  formColumns.value.forEach((column) => {
    formState[column.name] = '';
  });
  dialogVisible.value = true;
}

function openEdit(row: Record<string, any>) {
  isCreateMode.value = false;
  originalEnsureId.value = String(row.ENSURE_ID || '');
  resetForm();
  formColumns.value.forEach((column) => {
    formState[column.name] = row[column.name] == null ? '' : String(row[column.name]);
  });
  dialogVisible.value = true;
}

async function handleSave() {
  const ensureId = String(formState.ENSURE_ID || '').trim();
  if (!ensureId) {
    ElMessage.error('ENSURE_ID 不能为空');
    return;
  }
  if (!csrfToken.value) {
    ElMessage.error('管理员会话已失效，请重新登录');
    await router.replace('/admin/login');
    return;
  }

  saving.value = true;
  try {
    const payload = isCreateMode.value
      ? { ...formState, ENSURE_ID: ensureId }
      : { ENSURE_ID: originalEnsureId.value || ensureId, updates: { ...formState } };

    const url = isCreateMode.value
      ? '/engineered_sup_trna/create'
      : '/engineered_sup_trna/update';

    const resp = await fetch(url, {
      method: 'POST',
      headers: adminJsonHeaders(csrfToken.value),
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok || json?.error) {
      throw new Error(json?.error || '保存失败');
    }

    ElMessage.success(isCreateMode.value ? '创建成功' : '更新成功');
    dialogVisible.value = false;
    await refreshAll();
  } catch (error: any) {
    ElMessage.error(error?.message || '保存失败');
  } finally {
    saving.value = false;
  }
}

async function handleDelete(row: Record<string, any>) {
  const ensureId = String(row.ENSURE_ID || '').trim();
  if (!ensureId) {
    ElMessage.error('ENSURE_ID 缺失');
    return;
  }

  try {
    await ElMessageBox.confirm(`确认删除 ${ensureId} 吗？`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    });
  } catch {
    return;
  }

  try {
    const resp = await fetch('/engineered_sup_trna/delete', {
      method: 'POST',
      headers: adminJsonHeaders(csrfToken.value),
      credentials: 'same-origin',
      body: JSON.stringify({ ENSURE_ID: ensureId })
    });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok || json?.error) {
      throw new Error(json?.error || '删除失败');
    }
    ElMessage.success('删除成功');
    await refreshAll();
  } catch (error: any) {
    ElMessage.error(error?.message || '删除失败');
  }
}

async function handleLogout() {
  try {
    await fetch('/admin/api/logout', {
      method: 'POST',
      credentials: 'same-origin'
    });
  } finally {
    await router.replace('/admin/login');
  }
}

function handleCurrentChange(page: number) {
  handlePaginationUpdate({
    ...pagination,
    current: page
  });
}

function handleSizeChange(size: number) {
  handlePaginationUpdate({
    ...pagination,
    current: 1,
    pageSize: size
  });
}

onMounted(async () => {
  const authed = await ensureAdminSession();
  if (!authed) return;
  await loadLLMSettings();
  await loadColumns();
  await refreshAll();
  watchSearch();
});
</script>

<style scoped>
.admin-page {
  padding: 24px;
  display: grid;
  gap: 20px;
  background:
    linear-gradient(180deg, #f7fbff 0%, #eef5ff 100%);
  min-height: 100vh;
}

.admin-header,
.admin-card {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(10, 37, 64, 0.08);
  box-shadow: 0 16px 42px rgba(10, 37, 64, 0.08);
}

.admin-header-copy {
  display: grid;
  gap: 8px;
}

.admin-header {
  padding: 24px 28px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.admin-header h1 {
  margin: 0 0 8px;
  color: #0a2540;
}

.admin-eyebrow {
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.8rem;
  color: #00acf5;
  font-weight: 700;
}

.admin-subtitle {
  margin: 0;
  color: #506176;
}

.admin-status-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.admin-chip {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(48, 110, 246, 0.14);
  background: rgba(48, 110, 246, 0.08);
  color: #1f4bcc;
  font-size: 0.82rem;
  font-weight: 700;
}

.admin-chip--muted {
  color: #506176;
  background: rgba(10, 37, 64, 0.05);
  border-color: rgba(10, 37, 64, 0.08);
}

.admin-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.admin-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.admin-stat-card {
  padding: 18px 20px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(245, 250, 255, 0.96));
  border: 1px solid rgba(10, 37, 64, 0.08);
  box-shadow: 0 12px 28px rgba(10, 37, 64, 0.06);
  display: grid;
  gap: 8px;
}

.admin-stat-label {
  margin: 0;
  color: #607085;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.admin-stat-value {
  color: #0a2540;
  font-size: 1.4rem;
  line-height: 1.1;
}

.admin-stat-meta {
  color: #607085;
  font-size: 0.92rem;
  line-height: 1.5;
}

.admin-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(300px, 0.8fr);
  gap: 20px;
  align-items: start;
}

.admin-card {
  padding: 20px;
}

.admin-card--llm {
  min-height: 100%;
}

.admin-card--side {
  display: grid;
  gap: 16px;
  position: sticky;
  top: 20px;
}

.admin-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.admin-card-header h2 {
  margin: 0 0 4px;
  color: #0a2540;
}

.admin-card-header p {
  margin: 0;
  color: #607085;
}

.admin-side-stack {
  display: grid;
  gap: 12px;
}

.admin-side-block {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(242, 248, 255, 0.96), rgba(255, 255, 255, 0.96));
  border: 1px solid rgba(10, 37, 64, 0.08);
  display: grid;
  gap: 8px;
}

.admin-side-label {
  color: #607085;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.admin-side-block strong {
  color: #0a2540;
  font-size: 1.08rem;
}

.admin-side-block p {
  margin: 0;
  color: #607085;
  line-height: 1.55;
}

.admin-table {
  width: 100%;
}

.admin-row-actions {
  display: flex;
  gap: 8px;
}

.admin-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.admin-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 18px;
  max-height: 68vh;
  overflow: auto;
  padding-right: 4px;
}

.admin-form-item {
  margin-bottom: 0;
}

.admin-form-item--full {
  grid-column: 1 / -1;
}

.llm-grid :deep(.el-select),
.llm-grid :deep(.el-input-number) {
  width: 100%;
}

@media (max-width: 900px) {
  .admin-page {
    padding: 16px;
  }

  .admin-overview,
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .admin-card--side {
    position: static;
  }

  .admin-form-grid {
    grid-template-columns: 1fr;
  }

  .admin-pagination {
    justify-content: flex-start;
  }
}
</style>
