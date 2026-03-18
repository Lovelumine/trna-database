<template>
  <el-dialog
    v-model="dialogVisible"
    :title="t('dialog.configureMedia', { name: tableMeta?.label || '' })"
    width="min(1200px, 94vw)"
    top="4vh"
    destroy-on-close
  >
    <div class="media-fields-shell">
      <div class="media-fields-head">
        <div>
          <h3>{{ t('mediaField.title') }}</h3>
          <p>{{ t('mediaField.hint') }}</p>
        </div>
        <div class="media-fields-summary">
          <span>{{ t('mediaField.sampleRow') }} · {{ hasSampleRow ? t('mediaField.sampleAvailable') : t('mediaField.sampleMissing') }}</span>
          <span>{{ t('mediaField.explicitRules', { count: configuredCount }) }}</span>
        </div>
      </div>

      <el-alert
        v-if="saveError"
        type="error"
        :closable="false"
        show-icon
        :title="saveError"
        class="inline-alert"
      />

      <div v-if="tableMeta" class="media-fields-grid">
        <article
          v-for="column in tableMeta.columns"
          :key="column.name"
          class="media-field-card"
          :class="{ 'media-field-card--disabled': !fieldState(column.name).enabled }"
        >
          <header class="media-field-card-head">
            <div class="media-field-card-meta">
              <strong>{{ column.name }}</strong>
              <small>{{ columnDisplayLabel(column) }}</small>
            </div>
            <div class="media-field-card-tags">
              <span v-if="fieldState(column.name).fromDefault" class="media-field-tag">{{ t('mediaField.inheritedDefault') }}</span>
              <span v-if="fieldState(column.name).hasSaved" class="media-field-tag media-field-tag--accent">{{ t('mediaField.savedOverride') }}</span>
            </div>
          </header>

          <div class="media-field-toggle">
            <el-switch
              :model-value="fieldState(column.name).enabled"
              @change="(value: unknown) => toggleField(column.name, Boolean(value))"
            />
            <span>{{ fieldState(column.name).enabled ? t('mediaField.enabled') : t('mediaField.disabled') }}</span>
          </div>

          <div v-if="fieldState(column.name).enabled" class="media-field-form">
            <el-form-item :label="t('mediaField.renderer')">
              <el-select v-model="fieldState(column.name).renderer">
                <el-option value="image" :label="t('mediaField.rendererImage')" />
                <el-option value="url" :label="t('mediaField.rendererUrl')" />
                <el-option value="file" :label="t('mediaField.rendererFile')" />
                <el-option value="text" :label="t('mediaField.rendererText')" />
              </el-select>
            </el-form-item>

            <el-form-item :label="t('mediaField.source')">
              <el-select v-model="fieldState(column.name).source">
                <el-option value="auto" :label="t('mediaField.sourceAuto')" />
                <el-option value="direct" :label="t('mediaField.sourceDirect')" />
                <el-option value="template" :label="t('mediaField.sourceTemplate')" />
              </el-select>
            </el-form-item>

            <el-form-item
              v-if="fieldState(column.name).source === 'template'"
              class="span-2"
              :label="t('mediaField.template')"
            >
              <el-input
                v-model="fieldState(column.name).template"
                :placeholder="t('mediaField.templatePlaceholder')"
              />
            </el-form-item>

            <template v-if="fieldState(column.name).renderer === 'image'">
              <el-form-item :label="t('mediaField.width')">
                <el-input-number v-model="fieldState(column.name).width" :min="1" :max="1200" />
              </el-form-item>

              <el-form-item :label="t('mediaField.height')">
                <el-input-number v-model="fieldState(column.name).height" :min="1" :max="1200" />
              </el-form-item>

              <el-form-item :label="t('mediaField.fit')">
                <el-select v-model="fieldState(column.name).fit">
                  <el-option value="contain" :label="t('mediaField.fitContain')" />
                  <el-option value="cover" :label="t('mediaField.fitCover')" />
                  <el-option value="fill" :label="t('mediaField.fitFill')" />
                </el-select>
              </el-form-item>

              <el-form-item :label="t('mediaField.preview')">
                <el-switch v-model="fieldState(column.name).preview" />
              </el-form-item>
            </template>
          </div>

          <div v-else class="media-field-disabled-note">
            {{ fieldState(column.name).fromDefault ? t('mediaField.disableDefaultHint') : t('mediaField.notConfigured') }}
          </div>

          <div class="media-field-preview">
            <div class="media-field-preview-row">
              <span>{{ t('mediaField.sampleValue') }}</span>
              <code>{{ formatSampleValue(column.name) }}</code>
            </div>

            <template v-if="fieldState(column.name).enabled">
              <div class="media-field-preview-row">
                <span>{{ t('mediaField.resolvedValue') }}</span>
                <code>{{ resolvePreviewValue(column.name) || '—' }}</code>
              </div>

              <div v-if="fieldState(column.name).renderer === 'image'" class="media-field-preview-box">
                <img
                  v-if="resolvePreviewValue(column.name)"
                  :src="resolvePreviewValue(column.name)"
                  :alt="columnDisplayLabel(column)"
                  class="media-field-preview-image"
                />
                <div v-else class="media-field-preview-empty">{{ t('mediaField.noPreview') }}</div>
              </div>

              <div v-else-if="fieldState(column.name).renderer === 'url' || fieldState(column.name).renderer === 'file'" class="media-field-preview-link">
                <a
                  v-if="resolvePreviewValue(column.name)"
                  :href="resolvePreviewValue(column.name)"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ t('mediaField.openResolved') }}
                </a>
                <span v-else>{{ t('mediaField.noPreview') }}</span>
              </div>
            </template>
          </div>
        </article>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">{{ t('dialog.cancel') }}</el-button>
      <el-button type="primary" :loading="saving" @click="saveFields">{{ t('dialog.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import {
  ElAlert,
  ElButton,
  ElDialog,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElOption,
  ElSelect,
  ElSwitch,
} from 'element-plus';

import {
  saveAdminTableMediaFields,
  type AdminTableMediaFieldConfig,
  type AdminTableMeta,
} from '@/utils/admin';
import { useAdminI18n } from '@/utils/adminI18n';
import {
  getDefaultTableMediaFieldConfig,
  getMergedTableMediaFieldConfig,
  resolveMediaSource,
  setCachedTableMediaFieldConfig,
} from '@/utils/tableMedia';

type MediaFieldDraft = {
  enabled: boolean;
  renderer: 'text' | 'image' | 'url' | 'file';
  source: 'auto' | 'direct' | 'template';
  template: string;
  width: number | null;
  height: number | null;
  fit: 'contain' | 'cover' | 'fill';
  preview: boolean;
  fromDefault: boolean;
  hasSaved: boolean;
};

const props = defineProps<{
  modelValue: boolean;
  csrfToken: string;
  tableMeta: AdminTableMeta | null;
  sampleRow?: Record<string, any> | null;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  saved: [fields: Record<string, AdminTableMediaFieldConfig>];
}>();

const { t } = useAdminI18n();

const saving = ref(false);
const saveError = ref('');
const form = reactive<Record<string, MediaFieldDraft>>({});

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
});

const hasSampleRow = computed(() => Boolean(props.sampleRow && Object.keys(props.sampleRow).length));
const configuredCount = computed(() =>
  Object.values(form).filter((item) => item.enabled || item.fromDefault || item.hasSaved).length
);

function resetForm() {
  Object.keys(form).forEach((key) => delete form[key]);
}

function createDraft(config: AdminTableMediaFieldConfig, fromDefault: boolean, hasSaved: boolean): MediaFieldDraft {
  return {
    enabled: true,
    renderer: (config.renderer || 'image') as MediaFieldDraft['renderer'],
    source: (config.source || 'auto') as MediaFieldDraft['source'],
    template: String(config.template || ''),
    width: Number(config.width || 120) || 120,
    height: Number(config.height || 120) || 120,
    fit: (config.fit || 'contain') as MediaFieldDraft['fit'],
    preview: typeof config.preview === 'boolean' ? config.preview : true,
    fromDefault,
    hasSaved,
  };
}

function buildDisabledDraft(fromDefault: boolean, hasSaved: boolean): MediaFieldDraft {
  return {
    enabled: false,
    renderer: 'text',
    source: 'auto',
    template: '',
    width: 120,
    height: 120,
    fit: 'contain',
    preview: true,
    fromDefault,
    hasSaved,
  };
}

function isLegacyDefaultDisabled(savedConfig?: AdminTableMediaFieldConfig | null, fromDefault = false) {
  if (!fromDefault || !savedConfig) return false;
  return savedConfig.renderer === 'text' && (!savedConfig.source || savedConfig.source === 'auto') && !savedConfig.template;
}

function initializeForm() {
  resetForm();
  if (!props.tableMeta) return;

  const defaults = getDefaultTableMediaFieldConfig(props.tableMeta.name);
  const saved = props.tableMeta.media_fields || {};
  const merged = getMergedTableMediaFieldConfig(props.tableMeta.name, saved);

  props.tableMeta.columns.forEach((column) => {
    const fromDefault = Boolean(defaults[column.name]);
    const hasSaved = Boolean(saved[column.name]);
    const savedConfig = saved[column.name];
    if (isLegacyDefaultDisabled(savedConfig, fromDefault)) {
      form[column.name] = buildDisabledDraft(fromDefault, hasSaved);
      return;
    }
    const effective = merged[column.name];
    if (effective && Object.keys(effective).length) {
      form[column.name] = createDraft(effective, fromDefault, hasSaved);
      return;
    }
    form[column.name] = buildDisabledDraft(fromDefault, hasSaved);
  });
}

function fieldState(columnName: string) {
  if (!form[columnName]) {
    form[columnName] = buildDisabledDraft(false, false);
  }
  return form[columnName];
}

function toggleField(columnName: string, enabled: boolean) {
  fieldState(columnName).enabled = enabled;
}

function formatSampleValue(columnName: string) {
  const value = props.sampleRow?.[columnName];
  if (value == null || value === '') return t('mediaField.noSample');
  const text = String(value);
  return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

function buildOverrideConfig(columnName: string): Record<string, AdminTableMediaFieldConfig> {
  const draft = fieldState(columnName);
  if (!draft.enabled) {
    return {
      [columnName]: {
        renderer: 'text',
        source: 'auto',
      },
    };
  }
  const config: AdminTableMediaFieldConfig = {
    renderer: draft.renderer,
    source: draft.source,
  };
  if (draft.source === 'template' && draft.template.trim()) {
    config.template = draft.template.trim();
  }
  if (draft.renderer === 'image') {
    if (draft.width && draft.width > 0) config.width = draft.width;
    if (draft.height && draft.height > 0) config.height = draft.height;
    config.fit = draft.fit;
    config.preview = Boolean(draft.preview);
  }
  return { [columnName]: config };
}

function resolvePreviewValue(columnName: string) {
  if (!props.tableMeta) return '';
  const value = props.sampleRow?.[columnName];
  if (value == null || value === '') return '';
  const draft = fieldState(columnName);
  if (!draft.enabled) return '';
  return resolveMediaSource(props.tableMeta.name, columnName, value, buildOverrideConfig(columnName));
}

function columnDisplayLabel(column: { name: string; label_override?: string }) {
  return String(column.label_override || '').trim() || column.name;
}

function buildPayloadFields() {
  const fields: Record<string, AdminTableMediaFieldConfig> = {};
  Object.entries(form).forEach(([columnName, draft]) => {
    if (!draft.enabled) {
      if (draft.fromDefault) {
        fields[columnName] = { renderer: 'text', source: 'auto' };
      }
      return;
    }
    const config: AdminTableMediaFieldConfig = {
      renderer: draft.renderer,
      source: draft.source,
    };
    if (draft.source === 'template' && draft.template.trim()) {
      config.template = draft.template.trim();
    }
    if (draft.renderer === 'image') {
      if (draft.width && draft.width > 0) config.width = draft.width;
      if (draft.height && draft.height > 0) config.height = draft.height;
      config.fit = draft.fit;
      config.preview = Boolean(draft.preview);
    }
    fields[columnName] = config;
  });
  return fields;
}

async function saveFields() {
  if (!props.tableMeta) return;
  saving.value = true;
  saveError.value = '';
  try {
    const result = await saveAdminTableMediaFields(
      props.tableMeta.name,
      { fields: buildPayloadFields() },
      props.csrfToken
    );
    const fields = result.fields || {};
    setCachedTableMediaFieldConfig(props.tableMeta.name, fields);
    emit('saved', fields);
    dialogVisible.value = false;
    ElMessage.success(t('msg.mediaFieldsSaved'));
  } catch (error: any) {
    const message = error?.message || t('msg.mediaFieldsSaveFailed');
    saveError.value = message;
    ElMessage.error(message);
  } finally {
    saving.value = false;
  }
}

watch(
  () => [props.modelValue, props.tableMeta?.name] as const,
  ([visible]) => {
    if (visible) {
      initializeForm();
      saveError.value = '';
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.media-fields-shell {
  display: grid;
  gap: 16px;
}

.media-fields-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.media-fields-head h3,
.media-fields-head p {
  margin: 0;
}

.media-fields-head h3 {
  color: var(--admin-text);
  font-size: 1.14rem;
}

.media-fields-head p {
  margin-top: 6px;
  color: var(--admin-text-muted);
  line-height: 1.6;
  max-width: 68ch;
}

.media-fields-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.media-fields-summary span {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
  color: var(--admin-text-muted);
  font-size: 0.84rem;
  font-weight: 700;
}

.media-fields-grid {
  display: grid;
  gap: 14px;
}

.media-field-card {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface);
  padding: 16px;
  display: grid;
  gap: 14px;
}

.media-field-card--disabled {
  opacity: 0.9;
}

.media-field-card-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.media-field-card-meta strong,
.media-field-card-meta small {
  display: block;
}

.media-field-card-meta strong {
  color: var(--admin-text);
  font-size: 0.96rem;
}

.media-field-card-meta small {
  margin-top: 4px;
  color: var(--admin-text-muted);
}

.media-field-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.media-field-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
  color: var(--admin-text-muted);
  font-size: 0.76rem;
  font-weight: 800;
}

.media-field-tag--accent {
  color: #1d4ed8;
  border-color: rgba(37, 99, 235, 0.24);
  background: rgba(37, 99, 235, 0.08);
}

.media-field-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--admin-text);
  font-weight: 700;
}

.media-field-form {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px 16px;
}

.media-field-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.media-field-disabled-note {
  color: var(--admin-text-muted);
  line-height: 1.6;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--admin-surface-muted);
  border: 1px dashed var(--admin-border);
}

.media-field-preview {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 14px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
}

.media-field-preview-row {
  display: grid;
  gap: 6px;
}

.media-field-preview-row span {
  color: var(--admin-text-faint);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.media-field-preview-row code {
  padding: 8px 10px;
  border-radius: 10px;
  background: var(--admin-surface);
  border: 1px solid var(--admin-border);
  color: var(--admin-text);
  white-space: pre-wrap;
  word-break: break-word;
}

.media-field-preview-box {
  width: 180px;
  height: 140px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
  display: grid;
  place-items: center;
}

.media-field-preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f8fafc;
}

.media-field-preview-empty {
  padding: 0 16px;
  text-align: center;
  color: var(--admin-text-muted);
  font-size: 0.88rem;
}

.media-field-preview-link a {
  color: var(--admin-accent);
  font-weight: 700;
  text-decoration: none;
}

.media-field-preview-link span {
  color: var(--admin-text-muted);
}

.span-2 {
  grid-column: span 2;
}

@media (max-width: 1080px) {
  .media-field-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .media-field-form {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: auto;
  }

  .media-field-preview-box {
    width: 100%;
    max-width: 220px;
  }
}
</style>
