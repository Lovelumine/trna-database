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
  };
};

export type AdminTableColumn = {
  name: string;
  type: string;
  label_override?: string;
};

export type AdminTableMeta = AdminTableResource & {
  columns: AdminTableColumn[];
  default_visible_columns: string[];
};

export type AdminTableLabelsResponse = {
  table: string;
  labels: Record<string, string>;
};

export type AdminTableVisibleColumnsResponse = {
  table: string;
  columns: string[];
};

export type AdminTableRowsResponse = {
  table: string;
  total: number;
  page: number;
  page_size: number;
  rows: Record<string, any>[];
};

export type AdminDocDetail = {
  filename: string;
  type: string;
  editable: boolean;
  content: string;
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

export function adminJsonHeaders(csrfToken = ''): HeadersInit {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }
  return headers;
}
