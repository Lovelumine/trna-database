export type AdminUser = {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  last_login_at?: string | null;
};

export type AdminSession = {
  authenticated: boolean;
  user: AdminUser;
  csrf_token: string;
};

export type AdminAuditRow = {
  id: number;
  username: string;
  role: string;
  action: string;
  table_name: string;
  record_pk: string;
  created_at?: string | null;
  ip_address?: string | null;
  before_json?: string | null;
  after_json?: string | null;
};

export type AdminLLMSettings = {
  active_provider: string;
  active_model: string;
  timeout: number;
  max_messages: number;
  system_prompt: string;
  ollama_base_url: string;
  ollama_default_model: string;
  ollama_models: string[];
  deepseek_base_url: string;
  deepseek_api_key: string;
  deepseek_default_model: string;
  deepseek_models: string[];
  model_options: string[];
};

export type AdminAIWorkflowSettings = {
  workflow_enable: boolean;
  conversation_router_enable: boolean;
  conversation_router_model: string;
  conversation_router_timeout: number;
  router_confidence_threshold: number;
  max_retrieval_rounds: number;
  max_tool_steps_per_round: number;
  max_total_tool_steps: number;
  retrieval_judge_enable: boolean;
  retrieval_judge_model: string;
  retrieval_judge_threshold: number;
  stop_on_no_new_evidence: boolean;
  stop_on_repeated_plan: boolean;
  allow_pubmed_deepen: boolean;
  allow_table_deepen: boolean;
  allow_doc_deepen: boolean;
  final_critic_enable: boolean;
};

export type AdminTableResource = {
  name: string;
  label: string;
  category: string;
  row_count: number;
  column_count: number;
  primary_columns: string[];
  read_only: boolean;
};

export type AdminDocResource = {
  filename: string;
  type: string;
  editable: boolean;
  size: number;
};

export type AdminResourcesResponse = {
  tables: AdminTableResource[];
  docs: AdminDocResource[];
  overview: {
    table_count: number;
    editable_table_count: number;
    doc_count: number;
    total_rows: number;
    media_count?: number;
  };
};

export type AdminTableMediaFieldConfig = {
  renderer?: 'text' | 'image' | 'url' | 'file';
  source?: 'auto' | 'direct' | 'template';
  template?: string;
  width?: number;
  height?: number;
  fit?: 'contain' | 'cover' | 'fill';
  preview?: boolean;
};

export type AdminVirtualMediaField = {
  key: string;
  label: string;
  multiple?: boolean;
  placement?: 'record' | 'detail' | 'gallery';
  required?: boolean;
  sort_order?: number;
  orphan?: boolean;
};

export type AdminTableColumn = {
  name: string;
  type: string;
  label_override?: string;
};

export type AdminTableMeta = AdminTableResource & {
  columns: AdminTableColumn[];
  default_visible_columns: string[];
  media_fields?: Record<string, AdminTableMediaFieldConfig>;
  virtual_media_fields?: AdminVirtualMediaField[];
};

export type AdminTableLabelsResponse = {
  table: string;
  labels: Record<string, string>;
};

export type AdminTableVisibleColumnsResponse = {
  table: string;
  columns: string[];
};

export type AdminTableMediaFieldsResponse = {
  table: string;
  fields: Record<string, AdminTableMediaFieldConfig>;
};

export type AdminTableVirtualMediaFieldsResponse = {
  table: string;
  virtual_media_fields: AdminVirtualMediaField[];
};

export type AdminTableRowsResponse = {
  table: string;
  total: number;
  page: number;
  page_size: number;
  rows: Record<string, any>[];
};

export type AdminRecordMediaSlotBinding = {
  binding: {
    id: number;
    asset_id: number;
    binding_type: string;
    resource_name: string;
    field_name: string;
    record_key: string;
    slot_key: string;
    extra?: Record<string, any>;
    created_by?: number | null;
    created_by_username?: string;
    created_at?: string | null;
  };
  asset?: AdminMediaAsset | null;
};

export type AdminRecordMediaSlot = AdminVirtualMediaField & {
  bindings: AdminRecordMediaSlotBinding[];
};

export type AdminRecordMediaSlotsResponse = {
  table: string;
  record_key: string;
  match_columns: string[];
  row: Record<string, any>;
  slots: AdminRecordMediaSlot[];
};

export type AdminDocDetail = {
  filename: string;
  type: string;
  editable: boolean;
  content: string;
};

export type AdminMediaAsset = {
  id: number;
  bucket: string;
  object_key: string;
  public_url: string;
  mime_type: string;
  file_ext: string;
  size_bytes: number;
  width?: number | null;
  height?: number | null;
  sha256: string;
  title: string;
  alt_text: string;
  original_filename: string;
  source_type: string;
  created_by?: number | null;
  created_by_username?: string;
  created_at?: string | null;
  markdown: string;
  binding_count?: number;
  reference_count?: number;
};

export type AdminMediaReference = {
  type: string;
  resource: string;
  field_name?: string;
  record_key?: string;
  slot_key?: string;
  source?: string;
  binding_id?: number | null;
  created_at?: string | null;
};

export type AdminMediaListResponse = {
  page: number;
  page_size: number;
  total: number;
  items: AdminMediaAsset[];
};

export type AdminMediaDetailResponse = {
  asset: AdminMediaAsset;
  references: AdminMediaReference[];
};

async function parseJson(resp: Response) {
  return resp.json().catch(() => ({}));
}

async function ensureOk(resp: Response, fallback: string) {
  const json = await parseJson(resp);
  if (!resp.ok || json?.error) {
    throw new Error(json?.error || fallback);
  }
  return json;
}

export async function fetchAdminSession(): Promise<AdminSession | null> {
  const resp = await fetch('/admin/api/me', {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  if (!resp.ok) {
    return null;
  }
  return (await resp.json()) as AdminSession;
}

export async function fetchAdminAuditLogs(limit = 20): Promise<AdminAuditRow[]> {
  const resp = await fetch(`/admin/api/audit_logs?limit=${limit}`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  if (!resp.ok) {
    return [];
  }
  const json = await resp.json();
  return Array.isArray(json?.rows) ? json.rows : [];
}

export async function fetchAdminLLMSettings(): Promise<AdminLLMSettings | null> {
  const resp = await fetch('/admin/api/llm_settings', {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  if (!resp.ok) return null;
  return (await resp.json()) as AdminLLMSettings;
}

export async function fetchAdminAIWorkflowSettings(): Promise<AdminAIWorkflowSettings | null> {
  const resp = await fetch('/admin/api/ai_workflow_settings', {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  if (!resp.ok) return null;
  return (await resp.json()) as AdminAIWorkflowSettings;
}

export async function fetchAdminResources(): Promise<AdminResourcesResponse | null> {
  const resp = await fetch('/admin/api/resources', {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  if (!resp.ok) return null;
  return (await resp.json()) as AdminResourcesResponse;
}

export async function fetchAdminTableMeta(table: string): Promise<AdminTableMeta> {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/meta`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  return (await ensureOk(resp, '加载表结构失败')) as AdminTableMeta;
}

export async function fetchAdminTableRows(table: string, payload: Record<string, any>): Promise<AdminTableRowsResponse> {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/rows`, {
    method: 'POST',
    headers: adminJsonHeaders(),
    credentials: 'same-origin',
    body: JSON.stringify(payload)
  });
  return (await ensureOk(resp, '加载表数据失败')) as AdminTableRowsResponse;
}

export async function createAdminTableRecord(table: string, payload: Record<string, any>, csrfToken: string) {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/create`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload)
  });
  return await ensureOk(resp, '创建记录失败');
}

export async function updateAdminTableRecord(table: string, payload: Record<string, any>, csrfToken: string) {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/update`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload)
  });
  return await ensureOk(resp, '更新记录失败');
}

export async function deleteAdminTableRecord(table: string, payload: Record<string, any>, csrfToken: string) {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/delete`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload)
  });
  return await ensureOk(resp, '删除记录失败');
}

export async function saveAdminTableLabels(
  table: string,
  payload: { labels: Record<string, string> },
  csrfToken: string
): Promise<AdminTableLabelsResponse> {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/labels`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  return (await ensureOk(resp, '保存列名失败')) as AdminTableLabelsResponse;
}

export async function saveAdminTableVisibleColumns(
  table: string,
  payload: { columns: string[] },
  csrfToken: string
): Promise<AdminTableVisibleColumnsResponse> {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/visible_columns`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  return (await ensureOk(resp, '保存默认列失败')) as AdminTableVisibleColumnsResponse;
}

export async function saveAdminTableMediaFields(
  table: string,
  payload: { fields: Record<string, AdminTableMediaFieldConfig> },
  csrfToken: string
): Promise<AdminTableMediaFieldsResponse> {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/media_fields`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  return (await ensureOk(resp, '保存图片字段配置失败')) as AdminTableMediaFieldsResponse;
}

export async function saveAdminTableVirtualMediaFields(
  table: string,
  payload: { fields: AdminVirtualMediaField[] },
  csrfToken: string
): Promise<AdminTableVirtualMediaFieldsResponse> {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/virtual_media_fields`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  return (await ensureOk(resp, '保存记录图片槽位失败')) as AdminTableVirtualMediaFieldsResponse;
}

export async function fetchAdminRecordMediaSlots(
  table: string,
  payload: { original_row: Record<string, any> }
): Promise<AdminRecordMediaSlotsResponse> {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/record_media_slots`, {
    method: 'POST',
    headers: adminJsonHeaders(),
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  return (await ensureOk(resp, '加载记录图片槽位失败')) as AdminRecordMediaSlotsResponse;
}

export async function bindAdminRecordMediaSlot(
  table: string,
  payload: {
    original_row: Record<string, any>;
    slot_key: string;
    asset_id: number;
    replace_existing?: boolean;
  },
  csrfToken: string
) {
  const resp = await fetch(`/admin/api/tables/${encodeURIComponent(table)}/record_media_slots/bind`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload),
  });
  return await ensureOk(resp, '绑定记录图片失败');
}

export async function fetchAdminDoc(filename: string): Promise<AdminDocDetail> {
  const resp = await fetch(`/admin/api/docs/${encodeURIComponent(filename)}`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin'
  });
  return (await ensureOk(resp, '加载文档失败')) as AdminDocDetail;
}

export async function createAdminDoc(payload: { filename: string; content: string }, csrfToken: string) {
  const resp = await fetch('/admin/api/docs', {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload)
  });
  return await ensureOk(resp, '创建文档失败');
}

export async function saveAdminDoc(filename: string, payload: { content: string }, csrfToken: string) {
  const resp = await fetch(`/admin/api/docs/${encodeURIComponent(filename)}`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(payload)
  });
  return await ensureOk(resp, '保存文档失败');
}

export async function deleteAdminDoc(filename: string, csrfToken: string) {
  const resp = await fetch(`/admin/api/docs/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin'
  });
  return await ensureOk(resp, '删除文档失败');
}

export async function fetchAdminMediaList(params: { search?: string; source_type?: string; binding_status?: string; page?: number; page_size?: number } = {}): Promise<AdminMediaListResponse> {
  const query = new URLSearchParams();
  if (params.search) query.set('search', String(params.search));
  if (params.source_type) query.set('source_type', String(params.source_type));
  if (params.binding_status) query.set('binding_status', String(params.binding_status));
  if (params.page) query.set('page', String(params.page));
  if (params.page_size) query.set('page_size', String(params.page_size));
  const resp = await fetch(`/admin/api/media${query.toString() ? `?${query.toString()}` : ''}`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin',
  });
  return (await ensureOk(resp, '加载媒体库失败')) as AdminMediaListResponse;
}

export async function uploadAdminMedia(
  file: File,
  payload: { csrfToken: string; title?: string; alt_text?: string; source_type?: string }
): Promise<{ asset: AdminMediaAsset; deduped?: boolean }> {
  const form = new FormData();
  form.append('file', file);
  if (payload.title) form.append('title', payload.title);
  if (payload.alt_text) form.append('alt_text', payload.alt_text);
  if (payload.source_type) form.append('source_type', payload.source_type);
  const resp = await fetch('/admin/api/media/upload', {
    method: 'POST',
    credentials: 'same-origin',
    headers: payload.csrfToken ? { 'X-CSRF-Token': payload.csrfToken } : undefined,
    body: form,
  });
  return (await ensureOk(resp, '上传图片失败')) as { asset: AdminMediaAsset; deduped?: boolean };
}

export async function fetchAdminMediaDetail(assetId: number): Promise<AdminMediaDetailResponse> {
  const resp = await fetch(`/admin/api/media/${assetId}`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin',
  });
  return (await ensureOk(resp, '加载媒体详情失败')) as AdminMediaDetailResponse;
}

export async function saveAdminMedia(
  assetId: number,
  payload: { csrfToken: string; title?: string; alt_text?: string; source_type?: string }
): Promise<AdminMediaDetailResponse> {
  const csrfToken = String(payload?.csrfToken || '');
  const body = { ...payload };
  delete body.csrfToken;
  const resp = await fetch(`/admin/api/media/${assetId}`, {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(body),
  });
  return (await ensureOk(resp, '保存媒体元数据失败')) as AdminMediaDetailResponse;
}

export async function deleteAdminMediaBinding(bindingId: number, csrfToken: string) {
  const resp = await fetch(`/admin/api/media/bindings/${bindingId}`, {
    method: 'DELETE',
    credentials: 'same-origin',
    headers: csrfToken ? { 'X-CSRF-Token': csrfToken } : undefined,
  });
  return await ensureOk(resp, '删除图片绑定失败');
}

export async function deleteAdminMedia(assetId: number, csrfToken: string) {
  const resp = await fetch(`/admin/api/media/${assetId}`, {
    method: 'DELETE',
    credentials: 'same-origin',
    headers: csrfToken ? { 'X-CSRF-Token': csrfToken } : undefined,
  });
  const json = await parseJson(resp);
  if (!resp.ok || json?.error) {
    const error: Error & { references?: AdminMediaReference[] } = new Error(
      json?.error || '删除图片失败'
    );
    if (Array.isArray(json?.references)) {
      error.references = json.references;
    }
    throw error;
  }
  return json;
}

export async function saveAdminLLMSettings(payload: Record<string, any>): Promise<AdminLLMSettings> {
  const csrfToken = String(payload?.csrfToken || '');
  const body = { ...payload };
  delete body.csrfToken;
  const resp = await fetch('/admin/api/llm_settings', {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(body)
  });
  const json = await resp.json().catch(() => ({}));
  if (!resp.ok || json?.error) {
    throw new Error(json?.error || '保存 LLM 配置失败');
  }
  return json?.settings as AdminLLMSettings;
}

export async function saveAdminAIWorkflowSettings(payload: Record<string, any>): Promise<AdminAIWorkflowSettings> {
  const csrfToken = String(payload?.csrfToken || '');
  const body = { ...payload };
  delete body.csrfToken;
  const resp = await fetch('/admin/api/ai_workflow_settings', {
    method: 'POST',
    headers: adminJsonHeaders(csrfToken),
    credentials: 'same-origin',
    body: JSON.stringify(body)
  });
  const json = await resp.json().catch(() => ({}));
  if (!resp.ok || json?.error) {
    throw new Error(json?.error || '保存 AI workflow 配置失败');
  }
  return json?.settings as AdminAIWorkflowSettings;
}

export function adminJsonHeaders(csrfToken = ''): HeadersInit {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }
  return headers;
}
