<template>
  <el-dialog
    v-model="dialogVisible"
    :title="t('dialog.recordMediaSlots', { name: tableMeta?.label || '' })"
    width="min(1180px, 95vw)"
    top="4vh"
    destroy-on-close
  >
    <div class="record-media-shell">
      <div class="record-media-head">
        <div>
          <h3>{{ t('recordMedia.title') }}</h3>
          <p>{{ t('recordMedia.hint') }}</p>
        </div>
        <div class="record-media-summary">
          <span>{{ t('recordMedia.recordKey') }} · {{ recordKey || '—' }}</span>
        </div>
      </div>

      <el-alert
        v-if="loadError"
        type="error"
        :closable="false"
        show-icon
        :title="loadError"
        class="inline-alert"
      />

      <div class="record-media-toolbar">
        <el-input
          v-model="libraryQuery.search"
          :placeholder="t('recordMedia.searchPlaceholder')"
          clearable
          @keyup.enter="loadLibrary"
        />
        <el-select v-model="libraryQuery.sourceType" @change="loadLibrary">
          <el-option value="all" :label="t('media.sourceAll')" />
          <el-option value="library" :label="t('media.sourceLibrary')" />
          <el-option value="docs" :label="t('media.sourceDocs')" />
          <el-option value="table" :label="t('media.sourceTable')" />
          <el-option value="site" :label="t('media.sourceSite')" />
          <el-option value="legacy_pictureid" :label="t('media.sourceLegacyPictureid')" />
          <el-option value="other" :label="t('media.sourceOther')" />
        </el-select>
        <el-button @click="loadLibrary">{{ t('recordMedia.searchAction') }}</el-button>
      </div>

      <div v-if="!slotsLoading && !slots.length" class="record-media-empty">
        <strong>{{ t('recordMedia.emptyTitle') }}</strong>
        <p>{{ t('recordMedia.emptyHint') }}</p>
      </div>

      <div v-loading="slotsLoading" class="record-media-list">
        <article
          v-for="slot in slots"
          :key="slot.key"
          class="record-media-card"
        >
          <header class="record-media-card__head">
            <div>
              <strong>{{ slot.label || slot.key }}</strong>
              <small>{{ slot.key }}</small>
            </div>
            <div class="record-media-card__meta">
              <span>{{ slot.multiple ? t('recordMedia.multiple') : t('recordMedia.single') }}</span>
              <span v-if="slot.required">{{ t('recordMedia.required') }}</span>
              <span v-if="slot.orphan">{{ t('recordMedia.orphan') }}</span>
            </div>
          </header>

          <div class="record-media-bind-row">
            <el-select
              v-model="slotSelections[slot.key]"
              filterable
              clearable
              :loading="libraryLoading"
              :placeholder="t('recordMedia.pickAsset')"
            >
              <el-option
                v-for="asset in libraryAssets"
                :key="asset.id"
                :label="asset.title || asset.original_filename"
                :value="asset.id"
              />
            </el-select>
            <el-button
              type="primary"
              :loading="bindingSlotKey === slot.key"
              @click="bindSlot(slot)"
            >
              {{ t('recordMedia.bind') }}
            </el-button>
          </div>

          <div v-if="slot.bindings.length" class="record-media-bound-list">
            <article
              v-for="item in slot.bindings"
              :key="item.binding.id"
              class="record-media-bound"
            >
              <div class="record-media-bound__thumb">
                <img
                  v-if="item.asset?.public_url"
                  :src="item.asset.public_url"
                  :alt="item.asset.alt_text || item.asset.title || item.asset.original_filename"
                />
                <div v-else class="record-media-bound__empty">#{{ item.binding.asset_id }}</div>
              </div>
              <div class="record-media-bound__copy">
                <strong>{{ item.asset?.title || item.asset?.original_filename || `#${item.binding.asset_id}` }}</strong>
                <span>{{ item.asset?.public_url || t('recordMedia.assetMissing') }}</span>
              </div>
              <el-button
                size="small"
                type="danger"
                plain
                :loading="removingBindingId === item.binding.id"
                @click="removeBinding(item.binding.id)"
              >
                {{ t('recordMedia.unbind') }}
              </el-button>
            </article>
          </div>

          <div v-else class="record-media-bound-empty">
            {{ t('recordMedia.noBindings') }}
          </div>
        </article>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">{{ t('dialog.close') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import {
  ElAlert,
  ElButton,
  ElDialog,
  ElInput,
  ElMessage,
  ElOption,
  ElSelect,
} from 'element-plus';

import {
  bindAdminRecordMediaSlot,
  deleteAdminMediaBinding,
  fetchAdminMediaList,
  fetchAdminRecordMediaSlots,
  type AdminMediaAsset,
  type AdminRecordMediaSlot,
  type AdminTableMeta,
} from '@/utils/admin';
import { useAdminI18n } from '@/utils/adminI18n';

const props = defineProps<{
  modelValue: boolean;
  csrfToken: string;
  tableMeta: AdminTableMeta | null;
  row: Record<string, any> | null;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  changed: [];
}>();

const { t } = useAdminI18n();
const slotsLoading = ref(false);
const libraryLoading = ref(false);
const loadError = ref('');
const recordKey = ref('');
const slots = ref<AdminRecordMediaSlot[]>([]);
const libraryAssets = ref<AdminMediaAsset[]>([]);
const bindingSlotKey = ref('');
const removingBindingId = ref<number | null>(null);
const slotSelections = reactive<Record<string, number | null>>({});
const libraryQuery = reactive({
  search: '',
  sourceType: 'all',
});

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
});

function resetSelections() {
  Object.keys(slotSelections).forEach((key) => delete slotSelections[key]);
}

async function loadLibrary() {
  libraryLoading.value = true;
  try {
    const result = await fetchAdminMediaList({
      search: libraryQuery.search || undefined,
      source_type: libraryQuery.sourceType === 'all' ? undefined : libraryQuery.sourceType,
      page: 1,
      page_size: 24,
    });
    libraryAssets.value = Array.isArray(result.items) ? result.items : [];
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.mediaLoadFailed'));
  } finally {
    libraryLoading.value = false;
  }
}

async function loadSlots() {
  if (!props.tableMeta || !props.row) return;
  slotsLoading.value = true;
  loadError.value = '';
  try {
    const result = await fetchAdminRecordMediaSlots(props.tableMeta.name, {
      original_row: props.row,
    });
    recordKey.value = result.record_key || '';
    slots.value = Array.isArray(result.slots) ? result.slots : [];
    resetSelections();
    slots.value.forEach((slot) => {
      slotSelections[slot.key] = null;
    });
  } catch (error: any) {
    slots.value = [];
    recordKey.value = '';
    loadError.value = error?.message || t('msg.recordMediaLoadFailed');
  } finally {
    slotsLoading.value = false;
  }
}

async function bindSlot(slot: AdminRecordMediaSlot) {
  if (!props.tableMeta || !props.row) return;
  const assetId = Number(slotSelections[slot.key] || 0);
  if (!assetId) {
    ElMessage.error(t('msg.recordMediaPickAsset'));
    return;
  }
  bindingSlotKey.value = slot.key;
  try {
    await bindAdminRecordMediaSlot(
      props.tableMeta.name,
      {
        original_row: props.row,
        slot_key: slot.key,
        asset_id: assetId,
        replace_existing: !slot.multiple,
      },
      props.csrfToken
    );
    slotSelections[slot.key] = null;
    await loadSlots();
    emit('changed');
    ElMessage.success(t('msg.recordMediaBound'));
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.recordMediaBindFailed'));
  } finally {
    bindingSlotKey.value = '';
  }
}

async function removeBinding(bindingId: number) {
  removingBindingId.value = bindingId;
  try {
    await deleteAdminMediaBinding(bindingId, props.csrfToken);
    await loadSlots();
    emit('changed');
    ElMessage.success(t('msg.recordMediaUnbound'));
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.recordMediaUnbindFailed'));
  } finally {
    removingBindingId.value = null;
  }
}

watch(
  () => [props.modelValue, props.tableMeta?.name, JSON.stringify(props.row || {})] as const,
  ([visible]) => {
    if (visible) {
      void Promise.all([loadSlots(), loadLibrary()]);
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.modelValue) {
    void Promise.all([loadSlots(), loadLibrary()]);
  }
});
</script>

<style scoped>
.record-media-shell {
  display: grid;
  gap: 16px;
}

.record-media-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.record-media-head h3,
.record-media-head p {
  margin: 0;
}

.record-media-head h3 {
  color: var(--admin-text);
  font-size: 1.08rem;
}

.record-media-head p {
  margin-top: 6px;
  color: var(--admin-text-muted);
  line-height: 1.6;
  max-width: 72ch;
}

.record-media-summary span {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
  color: var(--admin-text-muted);
  font-size: 0.84rem;
  font-weight: 700;
}

.record-media-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) 180px auto;
  gap: 12px;
}

.record-media-list {
  display: grid;
  gap: 14px;
}

.record-media-card {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface);
  padding: 16px;
  display: grid;
  gap: 14px;
}

.record-media-card__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.record-media-card__head strong,
.record-media-card__head small {
  display: block;
}

.record-media-card__head small {
  margin-top: 4px;
  color: var(--admin-text-muted);
}

.record-media-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.record-media-card__meta span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
  color: var(--admin-text-muted);
  font-size: 0.76rem;
  font-weight: 700;
}

.record-media-bind-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
}

.record-media-bound-list {
  display: grid;
  gap: 10px;
}

.record-media-bound {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 10px;
  border-radius: 14px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
}

.record-media-bound__thumb {
  width: 76px;
  height: 76px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-media-bound__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.record-media-bound__empty {
  color: var(--admin-text-muted);
  font-size: 0.85rem;
  font-weight: 700;
}

.record-media-bound__copy {
  min-width: 0;
}

.record-media-bound__copy strong,
.record-media-bound__copy span {
  display: block;
}

.record-media-bound__copy strong {
  color: var(--admin-text);
}

.record-media-bound__copy span {
  margin-top: 4px;
  color: var(--admin-text-muted);
  font-size: 0.84rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.record-media-empty,
.record-media-bound-empty {
  padding: 20px;
  border: 1px dashed var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface-muted);
}

.record-media-empty strong,
.record-media-empty p {
  margin: 0;
}

.record-media-empty p {
  margin-top: 8px;
  color: var(--admin-text-muted);
  line-height: 1.6;
}

.record-media-bound-empty {
  color: var(--admin-text-muted);
  font-size: 0.9rem;
}

@media (max-width: 900px) {
  .record-media-toolbar,
  .record-media-bind-row,
  .record-media-bound {
    grid-template-columns: 1fr;
  }
}
</style>
