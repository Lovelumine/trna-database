import {
  allColumns as codingVariationCancerColumns,
  selectedColumns as codingVariationCancerSelectedColumns,
} from '@/views/Coding Variation Disease/CodingVariationCancerColumns';
import {
  allColumns as codingVariationDiseaseColumns,
  selectedColumns as codingVariationDiseaseSelectedColumns,
} from '@/views/Coding Variation Disease/CodingVariation1Columns';
import {
  allColumns as naturalNonsenseColumns,
  selectedColumns as naturalNonsenseSelectedColumns,
} from '@/views/natural-sup-tRNA/naturalSupTRNAColumns';
import {
  allColumns as frameshiftColumns,
  selectedColumns as frameshiftSelectedColumns,
} from '@/views/natural-sup-tRNA/Frameshiftcolumns';
import { allColumns as constructionColumns } from '@/views/natural-sup-tRNA/Constructioncolumns';
import { allColumns as engineeredColumns } from '@/views/tRNAtherapeutics/columns';
import {
  allColumns as modificationColumns,
  selectedColumns as modificationSelectedColumns,
} from '@/views/tRNA elements/FunctionAndModificationColumns';
import {
  allColumns as aarsColumns,
  selectedColumns as aarsSelectedColumns,
} from '@/views/tRNA elements/aaRScolumns';
import {
  allColumns as eftuColumns,
  selectedColumns as eftuSelectedColumns,
} from '@/views/tRNA elements/EFTUcolumns';
import {
  allColumns as ribosomeColumns,
  selectedColumns as ribosomeSelectedColumns,
} from '@/views/tRNA elements/RibosomeInteractionColumns';

type ColumnLike = {
  title?: any;
  key?: string;
  dataIndex?: string | string[];
  children?: ColumnLike[];
  [key: string]: any;
};

type ColumnLabelMap = Record<string, string>;
type ColumnKeyList = string[];

const overrideCache = new Map<string, ColumnLabelMap>();
const inflight = new Map<string, Promise<ColumnLabelMap>>();
const visibleColumnsCache = new Map<string, string[]>();
const visibleColumnsInflight = new Map<string, Promise<string[]>>();

function normalizeKey(value: unknown): string {
  if (Array.isArray(value)) return String(value[0] || '').trim();
  return String(value || '').trim();
}

function extractColumnLabels(columns: ColumnLike[], target: ColumnLabelMap = {}) {
  for (const column of columns || []) {
    const key = normalizeKey(column.dataIndex || column.key);
    if (key && typeof column.title === 'string') {
      target[key] = column.title;
    }
    if (Array.isArray(column.children) && column.children.length) {
      extractColumnLabels(column.children, target);
    }
  }
  return target;
}

function collectColumnDescriptors(columns: ColumnLike[], target: Array<{ field: string; key: string }> = []) {
  for (const column of columns || []) {
    const field = normalizeKey(column.dataIndex || column.key);
    const key = normalizeKey(column.key || column.dataIndex);
    if (field && key) {
      target.push({ field, key });
    }
    if (Array.isArray(column.children) && column.children.length) {
      collectColumnDescriptors(column.children, target);
    }
  }
  return target;
}

const DEFAULT_COLUMN_LABELS: Record<string, ColumnLabelMap> = {
  coding_variation_cancer: extractColumnLabels(codingVariationCancerColumns as ColumnLike[]),
  coding_variation_genetic_disease: {
    ...extractColumnLabels(codingVariationDiseaseColumns as ColumnLike[]),
    'Protein Alteration': 'Protein Alteration',
  },
  nonsense_sup_rna: extractColumnLabels(naturalNonsenseColumns as ColumnLike[]),
  frameshift_sup_trna: extractColumnLabels(frameshiftColumns as ColumnLike[]),
  construction_sup_trna: extractColumnLabels(constructionColumns as ColumnLike[]),
  Engineered_sup_tRNA: extractColumnLabels(engineeredColumns as ColumnLike[]),
  function_and_modification: extractColumnLabels(modificationColumns as ColumnLike[]),
  aars_recognition: extractColumnLabels(aarsColumns as ColumnLike[]),
  ef_tu: extractColumnLabels(eftuColumns as ColumnLike[]),
  trna_ribosome_interactions: extractColumnLabels(ribosomeColumns as ColumnLike[]),
};

const COLUMN_DESCRIPTOR_MAP: Record<string, Array<{ field: string; key: string }>> = {
  coding_variation_cancer: collectColumnDescriptors(codingVariationCancerColumns as ColumnLike[]),
  coding_variation_genetic_disease: collectColumnDescriptors(codingVariationDiseaseColumns as ColumnLike[]),
  nonsense_sup_rna: collectColumnDescriptors(naturalNonsenseColumns as ColumnLike[]),
  frameshift_sup_trna: collectColumnDescriptors(frameshiftColumns as ColumnLike[]),
  construction_sup_trna: collectColumnDescriptors(constructionColumns as ColumnLike[]),
  Engineered_sup_tRNA: collectColumnDescriptors(engineeredColumns as ColumnLike[]),
  function_and_modification: collectColumnDescriptors(modificationColumns as ColumnLike[]),
  aars_recognition: collectColumnDescriptors(aarsColumns as ColumnLike[]),
  ef_tu: collectColumnDescriptors(eftuColumns as ColumnLike[]),
  trna_ribosome_interactions: collectColumnDescriptors(ribosomeColumns as ColumnLike[]),
};

const DEFAULT_VISIBLE_COLUMN_KEYS: Record<string, ColumnKeyList> = {
  coding_variation_cancer: [...codingVariationCancerSelectedColumns.value],
  coding_variation_genetic_disease: [...codingVariationDiseaseSelectedColumns.value],
  nonsense_sup_rna: [...naturalNonsenseSelectedColumns.value],
  frameshift_sup_trna: [...frameshiftSelectedColumns.value],
  construction_sup_trna: [
    'Species',
    'Anticodon before mutation',
    'Anticodon after mutation',
    'Stop codon for readthrough',
    'Mutational position of sup-tRNA',
  ],
  Engineered_sup_tRNA: [
    'PTC_gene',
    'Species_source_of_origin_tRNA',
    'aa_and_anticodon_of_sup-tRNA',
    'Reaction_system',
    'pre_ENSURE_ID',
    'Reading_through_efficiency',
  ],
  function_and_modification: [...modificationSelectedColumns.value],
  aars_recognition: [...aarsSelectedColumns.value],
  ef_tu: [...eftuSelectedColumns.value],
  trna_ribosome_interactions: [...ribosomeSelectedColumns.value],
};

function getColumnDescriptors(table: string) {
  return COLUMN_DESCRIPTOR_MAP[String(table || '').trim()] || [];
}

function getPreferredKeyForField(table: string, field: string) {
  const descriptors = getColumnDescriptors(table).filter((item) => item.field === normalizeKey(field));
  if (!descriptors.length) return normalizeKey(field);
  const defaults = getDefaultVisibleColumnKeys(table);
  const preferred = descriptors.find((item) => defaults.includes(item.key));
  return preferred?.key || descriptors[0].key;
}

function dedupeStrings(items: unknown[]) {
  const values: string[] = [];
  for (const item of items || []) {
    const text = normalizeKey(item);
    if (text && !values.includes(text)) values.push(text);
  }
  return values;
}

export function getDefaultVisibleColumnKeys(table: string): ColumnKeyList {
  return [...(DEFAULT_VISIBLE_COLUMN_KEYS[String(table || '').trim()] || [])];
}

export function getDefaultVisibleColumnNames(table: string): ColumnKeyList {
  const descriptors = getColumnDescriptors(table);
  const defaults = getDefaultVisibleColumnKeys(table);
  return dedupeStrings(
    defaults.map((key) => descriptors.find((item) => item.key === key)?.field || key)
  );
}

export function mapVisibleColumnNamesToKeys(table: string, columnNames: string[]): ColumnKeyList {
  return dedupeStrings(
    (columnNames || []).map((name) => getPreferredKeyForField(table, normalizeKey(name)))
  );
}

export function getDefaultColumnLabels(table: string): ColumnLabelMap {
  return { ...(DEFAULT_COLUMN_LABELS[String(table || '').trim()] || {}) };
}

export async function fetchTableColumnLabelOverrides(table: string, force = false): Promise<ColumnLabelMap> {
  const tableName = String(table || '').trim();
  if (!tableName) return {};
  if (!force && overrideCache.has(tableName)) {
    return { ...(overrideCache.get(tableName) || {}) };
  }
  if (!force && inflight.has(tableName)) {
    return { ...((await inflight.get(tableName)) || {}) };
  }
  const task = fetch(`/api/tables/${encodeURIComponent(tableName)}/column_labels`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin',
  })
    .then(async (resp) => {
      if (!resp.ok) return {};
      const json = await resp.json().catch(() => ({}));
      const labels = json?.labels && typeof json.labels === 'object' ? json.labels : {};
      const normalized: ColumnLabelMap = {};
      for (const [key, value] of Object.entries(labels)) {
        const columnKey = normalizeKey(key);
        const text = String(value || '').trim();
        if (columnKey && text) normalized[columnKey] = text;
      }
      overrideCache.set(tableName, normalized);
      return normalized;
    })
    .finally(() => {
      inflight.delete(tableName);
    });
  inflight.set(tableName, task);
  return { ...(await task) };
}

export async function fetchTableVisibleColumnNames(table: string, force = false): Promise<string[]> {
  const tableName = String(table || '').trim();
  if (!tableName) return [];
  if (!force && visibleColumnsCache.has(tableName)) {
    return [...(visibleColumnsCache.get(tableName) || [])];
  }
  if (!force && visibleColumnsInflight.has(tableName)) {
    return [...((await visibleColumnsInflight.get(tableName)) || [])];
  }
  const task = fetch(`/api/tables/${encodeURIComponent(tableName)}/default_columns`, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin',
  })
    .then(async (resp) => {
      if (!resp.ok) return [];
      const json = await resp.json().catch(() => ({}));
      const columns = Array.isArray(json?.columns) ? json.columns : [];
      const normalized = dedupeStrings(columns);
      visibleColumnsCache.set(tableName, normalized);
      return normalized;
    })
    .finally(() => {
      visibleColumnsInflight.delete(tableName);
    });
  visibleColumnsInflight.set(tableName, task);
  return [...(await task)];
}

export async function getRuntimeColumnsWithLabels<T extends ColumnLike>(table: string, columns: T[]): Promise<T[]> {
  const overrides = await fetchTableColumnLabelOverrides(table);
  return cloneColumnsWithLabels(table, columns, overrides);
}

export function setCachedTableColumnLabelOverrides(table: string, labels: ColumnLabelMap) {
  const tableName = String(table || '').trim();
  if (!tableName) return;
  const normalized: ColumnLabelMap = {};
  for (const [key, value] of Object.entries(labels || {})) {
    const columnKey = normalizeKey(key);
    const text = String(value || '').trim();
    if (columnKey && text) normalized[columnKey] = text;
  }
  overrideCache.set(tableName, normalized);
}

export function setCachedTableVisibleColumnNames(table: string, columns: string[]) {
  const tableName = String(table || '').trim();
  if (!tableName) return;
  visibleColumnsCache.set(tableName, dedupeStrings(columns || []));
}

export function getMergedColumnLabels(table: string, extraOverrides: ColumnLabelMap = {}): ColumnLabelMap {
  return {
    ...getDefaultColumnLabels(table),
    ...(overrideCache.get(String(table || '').trim()) || {}),
    ...(extraOverrides || {}),
  };
}

export async function getRuntimeVisibleColumnKeys(table: string, fallback: string[] = []): Promise<string[]> {
  const names = await fetchTableVisibleColumnNames(table);
  if (names.length) {
    return mapVisibleColumnNamesToKeys(table, names);
  }
  const defaults = getDefaultVisibleColumnKeys(table);
  return defaults.length ? defaults : [...fallback];
}

function cloneColumnWithLabels(column: ColumnLike, labels: ColumnLabelMap): ColumnLike {
  const next: ColumnLike = { ...column };
  const key = normalizeKey(column.dataIndex || column.key);
  const label = key ? labels[key] : '';
  if (label) {
    next.title = label;
  }
  if (Array.isArray(column.children) && column.children.length) {
    next.children = column.children.map((child) => cloneColumnWithLabels(child, labels));
  }
  return next;
}

export function cloneColumnsWithLabels<T extends ColumnLike>(table: string, columns: T[], extraOverrides: ColumnLabelMap = {}): T[] {
  const labels = getMergedColumnLabels(table, extraOverrides);
  return (columns || []).map((column) => cloneColumnWithLabels(column, labels) as T);
}
