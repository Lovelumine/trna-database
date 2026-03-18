<template>
  <el-dialog
    v-model="dialogVisible"
    :title="t('dialog.configureVirtualMedia', { name: tableMeta?.label || '' })"
    width="min(980px, 94vw)"
    top="6vh"
    destroy-on-close
  >
    <div class="virtual-media-shell">
      <div class="virtual-media-head">
        <div>
          <h3>{{ t('virtualMedia.title') }}</h3>
          <p>{{ t('virtualMedia.hint') }}</p>
        </div>
        <el-button type="primary" plain @click="addField">{{ t('virtualMedia.add') }}</el-button>
      </div>

      <el-alert
        v-if="saveError"
        type="error"
        :closable="false"
        show-icon
        :title="saveError"
        class="inline-alert"
      />

      <div v-if="fields.length" class="virtual-media-list">
        <article
          v-for="(field, index) in fields"
          :key="field.uid"
          class="virtual-media-card"
        >
          <header class="virtual-media-card__head">
            <div>
              <strong>{{ field.label || field.key || `${t('virtualMedia.slot')} ${index + 1}` }}</strong>
              <small>{{ field.key || t('virtualMedia.keyPlaceholder') }}</small>
            </div>
            <el-button type="danger" plain size="small" @click="removeField(field.uid)">
              {{ t('virtualMedia.remove') }}
            </el-button>
          </header>

          <div class="virtual-media-grid">
            <el-form-item :label="t('virtualMedia.key')">
              <el-input v-model="field.key" :placeholder="t('virtualMedia.keyPlaceholder')" />
            </el-form-item>
            <el-form-item :label="t('virtualMedia.label')">
              <el-input v-model="field.label" :placeholder="t('virtualMedia.labelPlaceholder')" />
            </el-form-item>
            <el-form-item :label="t('virtualMedia.placement')">
              <el-select v-model="field.placement">
                <el-option value="record" :label="t('virtualMedia.placementRecord')" />
                <el-option value="detail" :label="t('virtualMedia.placementDetail')" />
                <el-option value="gallery" :label="t('virtualMedia.placementGallery')" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('virtualMedia.sortOrder')">
              <el-input-number v-model="field.sort_order" :min="0" :max="9999" />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="field.multiple">{{ t('virtualMedia.multiple') }}</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="field.required">{{ t('virtualMedia.required') }}</el-checkbox>
            </el-form-item>
          </div>
        </article>
      </div>

      <div v-else class="virtual-media-empty">
        <strong>{{ t('virtualMedia.emptyTitle') }}</strong>
        <p>{{ t('virtualMedia.emptyHint') }}</p>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">{{ t('dialog.cancel') }}</el-button>
      <el-button type="primary" :loading="saving" @click="saveFields">{{ t('dialog.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  ElAlert,
  ElButton,
  ElCheckbox,
  ElDialog,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElOption,
  ElSelect,
} from 'element-plus';

import {
  saveAdminTableVirtualMediaFields,
  type AdminTableMeta,
  type AdminVirtualMediaField,
} from '@/utils/admin';
import { useAdminI18n } from '@/utils/adminI18n';

type VirtualMediaFieldDraft = AdminVirtualMediaField & {
  uid: string;
};

const props = defineProps<{
  modelValue: boolean;
  csrfToken: string;
  tableMeta: AdminTableMeta | null;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  saved: [fields: AdminVirtualMediaField[]];
}>();

const { t } = useAdminI18n();
const saving = ref(false);
const saveError = ref('');
const fields = ref<VirtualMediaFieldDraft[]>([]);

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
});

function makeUid() {
  return `virtual-media-${Math.random().toString(36).slice(2, 10)}`;
}

function initializeForm() {
  fields.value = (props.tableMeta?.virtual_media_fields || []).map((field) => ({
    uid: makeUid(),
    key: String(field.key || ''),
    label: String(field.label || ''),
    multiple: Boolean(field.multiple),
    placement: field.placement || 'record',
    required: Boolean(field.required),
    sort_order: Number(field.sort_order || 0),
  }));
}

function addField() {
  fields.value = [
    ...fields.value,
    {
      uid: makeUid(),
      key: '',
      label: '',
      multiple: false,
      placement: 'record',
      required: false,
      sort_order: fields.value.length ? Math.max(...fields.value.map((item) => Number(item.sort_order || 0))) + 10 : 10,
    },
  ];
}

function removeField(uid: string) {
  fields.value = fields.value.filter((field) => field.uid !== uid);
}

function buildPayload(): AdminVirtualMediaField[] {
  return fields.value.map(({ uid: _uid, ...field }) => ({
    key: String(field.key || '').trim(),
    label: String(field.label || '').trim(),
    multiple: Boolean(field.multiple),
    placement: field.placement || 'record',
    required: Boolean(field.required),
    sort_order: Number(field.sort_order || 0),
  }));
}

async function saveFields() {
  if (!props.tableMeta) return;
  saving.value = true;
  saveError.value = '';
  try {
    const result = await saveAdminTableVirtualMediaFields(
      props.tableMeta.name,
      { fields: buildPayload() },
      props.csrfToken
    );
    emit('saved', result.virtual_media_fields || []);
    dialogVisible.value = false;
    ElMessage.success(t('msg.virtualMediaSaved'));
  } catch (error: any) {
    const message = error?.message || t('msg.virtualMediaSaveFailed');
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
.virtual-media-shell {
  display: grid;
  gap: 16px;
}

.virtual-media-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.virtual-media-head h3,
.virtual-media-head p {
  margin: 0;
}

.virtual-media-head h3 {
  color: var(--admin-text);
  font-size: 1.08rem;
}

.virtual-media-head p {
  margin-top: 6px;
  color: var(--admin-text-muted);
  line-height: 1.6;
  max-width: 70ch;
}

.virtual-media-list {
  display: grid;
  gap: 14px;
}

.virtual-media-card {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface);
  padding: 16px;
  display: grid;
  gap: 14px;
}

.virtual-media-card__head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.virtual-media-card__head strong,
.virtual-media-card__head small {
  display: block;
}

.virtual-media-card__head strong {
  color: var(--admin-text);
}

.virtual-media-card__head small {
  margin-top: 4px;
  color: var(--admin-text-muted);
}

.virtual-media-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 16px;
}

.virtual-media-empty {
  padding: 24px;
  border-radius: 16px;
  border: 1px dashed var(--admin-border);
  background: var(--admin-surface-muted);
}

.virtual-media-empty strong,
.virtual-media-empty p {
  margin: 0;
}

.virtual-media-empty p {
  margin-top: 8px;
  color: var(--admin-text-muted);
  line-height: 1.6;
}

@media (max-width: 880px) {
  .virtual-media-grid {
    grid-template-columns: 1fr;
  }
}
</style>
