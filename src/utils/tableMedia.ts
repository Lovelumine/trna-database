export type TableMediaFieldConfig = {
  renderer?: 'text' | 'image' | 'url' | 'file';
  source?: 'auto' | 'direct' | 'template';
  template?: string;
  width?: number;
  height?: number;
  fit?: 'contain' | 'cover' | 'fill';
  preview?: boolean;
};

type TableMediaFieldMap = Record<string, TableMediaFieldConfig>;
export type TableRowMediaEntry = {
  binding?: {
    id?: number;
    binding_type?: string;
    resource_name?: string;
    field_name?: string;
    record_key?: string;
    slot_key?: string;
  };
  asset?: {
    id?: number;
    public_url?: string;
    object_key?: string;
    title?: string;
    alt_text?: string;
  };
};

const LEGACY_MINIO_PICTURE_TEMPLATE = 'https://minio.lumoxuan.cn/ensure/picture/{value}.png';

const DEFAULT_MEDIA_FIELD_CONFIG: Record<string, TableMediaFieldMap> = {
  nonsense_sup_rna: {
    'Structure of sup-tRNA': {
      renderer: 'image',
      source: 'direct',
      width: 100,
      height: 100,
      fit: 'cover',
      preview: true,
    },
    pictureid: {
      renderer: 'image',
      source: 'template',
      template: LEGACY_MINIO_PICTURE_TEMPLATE,
      width: 100,
      height: 100,
      fit: 'cover',
      preview: true,
    },
  },
  frameshift_sup_trna: {
    'Structure of sup-tRNA': {
      renderer: 'image',
      source: 'direct',
      width: 100,
      height: 100,
      fit: 'cover',
      preview: true,
    },
    pictureid: {
      renderer: 'image',
      source: 'template',
      template: LEGACY_MINIO_PICTURE_TEMPLATE,
      width: 100,
      height: 100,
      fit: 'cover',
      preview: true,
    },
    Notes: {
      renderer: 'image',
      source: 'template',
      template: LEGACY_MINIO_PICTURE_TEMPLATE,
      width: 100,
      height: 100,
      fit: 'cover',
      preview: true,
    },
  },
  construction_sup_trna: {
    'Structure of sup-tRNA': {
      renderer: 'image',
      source: 'direct',
      width: 100,
      height: 100,
      fit: 'cover',
      preview: true,
    },
  },
  blast_results: {
    pictureid: {
      renderer: 'image',
      source: 'template',
      template: LEGACY_MINIO_PICTURE_TEMPLATE,
      width: 100,
      height: 100,
      fit: 'cover',
      preview: true,
    },
  },
};

const mediaConfigCache = new Map<string, TableMediaFieldMap>();
const inflight = new Map<string, Promise<TableMediaFieldMap>>();

function normalizeKey(value: unknown): string {
  return String(value || '').trim();
}

function normalizeConfig(raw: unknown): TableMediaFieldMap {
  const config = raw && typeof raw === 'object' ? (raw as Record<string, any>) : {};
  const normalized: TableMediaFieldMap = {};
  for (const [fieldName, item] of Object.entries(config)) {
    const field = normalizeKey(fieldName);
    if (!field || !item || typeof item !== 'object') continue;
    const renderer = normalizeKey(item.renderer).toLowerCase();
    const source = normalizeKey(item.source).toLowerCase();
    const template = normalizeKey(item.template);
    const current: TableMediaFieldConfig = {};
    if (renderer === 'image' || renderer === 'url' || renderer === 'file' || renderer === 'text') {
      current.renderer = renderer as TableMediaFieldConfig['renderer'];
    }
    if (source === 'auto' || source === 'direct' || source === 'template') {
      current.source = source as TableMediaFieldConfig['source'];
    }
    if (template) current.template = template;
    for (const key of ['width', 'height'] as const) {
      const value = Number(item[key] || 0);
      if (Number.isFinite(value) && value > 0) current[key] = value;
    }
    const fit = normalizeKey(item.fit).toLowerCase();
    if (fit === 'contain' || fit === 'cover' || fit === 'fill') current.fit = fit as TableMediaFieldConfig['fit'];
    if (typeof item.preview === 'boolean') current.preview = item.preview;
    if (Object.keys(current).length) normalized[field] = current;
  }
  return normalized;
}

export function getDefaultTableMediaFieldConfig(table: string): TableMediaFieldMap {
  return { ...(DEFAULT_MEDIA_FIELD_CONFIG[normalizeKey(table)] || {}) };
}

export function getMergedTableMediaFieldConfig(table: string, overrides: TableMediaFieldMap = {}): TableMediaFieldMap {
  return {
    ...getDefaultTableMediaFieldConfig(table),
    ...normalizeConfig(overrides),
  };
}

export async function fetchTableMediaFieldConfig(table: string, force = false): Promise<TableMediaFieldMap> {
  const tableName = normalizeKey(table);
  if (!tableName) return {};
  if (!force && mediaConfigCache.has(tableName)) {
    return { ...(mediaConfigCache.get(tableName) || {}) };
  }
  if (!force && inflight.has(tableName)) {
    return { ...((await inflight.get(tableName)) || {}) };
  }
  const task = fetch(`/api/tables/${encodeURIComponent(tableName)}/media_fields`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin',
  })
    .then(async (resp) => {
      if (!resp.ok) return {};
      const json = await resp.json().catch(() => ({}));
      const fields = normalizeConfig(json?.fields);
      mediaConfigCache.set(tableName, fields);
      return fields;
    })
    .finally(() => inflight.delete(tableName));
  inflight.set(tableName, task);
  return { ...(await task) };
}

export function setCachedTableMediaFieldConfig(table: string, fields: TableMediaFieldMap) {
  const tableName = normalizeKey(table);
  if (!tableName) return;
  mediaConfigCache.set(tableName, normalizeConfig(fields));
}

export function getTableMediaFieldConfig(table: string, field: string, overrides: TableMediaFieldMap = {}): TableMediaFieldConfig {
  const merged = getMergedTableMediaFieldConfig(table, overrides);
  return { ...(merged[normalizeKey(field)] || {}) };
}

export function resolveMediaSource(table: string, field: string, value: unknown, overrides: TableMediaFieldMap = {}): string {
  const raw = normalizeKey(value);
  if (!raw) return '';
  if (/^(https?:)?\/\//i.test(raw) || raw.startsWith('data:')) {
    return raw;
  }
  const config = getTableMediaFieldConfig(table, field, overrides);
  const source = normalizeKey(config.source).toLowerCase();
  if (source === 'template' && config.template) {
    return String(config.template).replaceAll('{value}', encodeURIComponent(raw));
  }
  return raw;
}

function getRowMediaBucket(row: any, bucket: 'fields' | 'slots'): Record<string, TableRowMediaEntry[]> {
  const media = row && typeof row === 'object' ? row.__media : null;
  const value = media && typeof media === 'object' ? media[bucket] : null;
  return value && typeof value === 'object' ? (value as Record<string, TableRowMediaEntry[]>) : {};
}

export function getRowBoundFieldMediaEntries(row: any, field: string): TableRowMediaEntry[] {
  const fieldKey = normalizeKey(field);
  if (!fieldKey) return [];
  const fields = getRowMediaBucket(row, 'fields');
  const matches = Array.isArray(fields[fieldKey]) ? fields[fieldKey] : [];
  return matches;
}

export function getRowBoundFieldMediaEntry(row: any, field: string): TableRowMediaEntry | null {
  const matches = getRowBoundFieldMediaEntries(row, field);
  return matches[0] || null;
}

export function getRowBoundFieldMediaUrl(row: any, field: string): string {
  const matches = getRowBoundFieldMediaEntries(row, field);
  for (const entry of matches) {
    const url = normalizeKey(entry?.asset?.public_url);
    if (url) return url;
  }
  return '';
}

export function getRowBoundSlotMediaUrl(row: any, slotKey: string): string {
  const safeSlotKey = normalizeKey(slotKey);
  if (!safeSlotKey) return '';
  const slots = getRowMediaBucket(row, 'slots');
  const matches = Array.isArray(slots[safeSlotKey]) ? slots[safeSlotKey] : [];
  for (const entry of matches) {
    const url = normalizeKey(entry?.asset?.public_url);
    if (url) return url;
  }
  return '';
}
