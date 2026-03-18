<template>
  <section class="workspace-panel">
    <div class="media-layout">
      <section class="content-card media-card media-card--list">
        <div class="content-card-header">
          <div>
            <h3>{{ t('media.libraryTitle') }}</h3>
            <p>{{ t('media.libraryHint') }}</p>
          </div>
          <div class="card-actions">
            <el-button @click="resetFilters">{{ t('media.reset') }}</el-button>
            <el-button type="primary" @click="openUploadDialog">{{ t('media.upload') }}</el-button>
          </div>
        </div>

        <div class="media-toolbar">
          <el-input
            v-model="query.search"
            :placeholder="t('media.searchPlaceholder')"
            clearable
            @keyup.enter="runSearch"
          />
          <el-select v-model="query.sourceType" @change="runSearch">
            <el-option value="all" :label="t('media.sourceAll')" />
            <el-option value="library" :label="t('media.sourceLibrary')" />
            <el-option value="docs" :label="t('media.sourceDocs')" />
            <el-option value="table" :label="t('media.sourceTable')" />
            <el-option value="site" :label="t('media.sourceSite')" />
            <el-option value="legacy_pictureid" :label="t('media.sourceLegacyPictureid')" />
            <el-option value="other" :label="t('media.sourceOther')" />
          </el-select>
          <el-select v-model="query.pageSize" @change="runSearch">
            <el-option :value="12" label="12 / page" />
            <el-option :value="24" label="24 / page" />
            <el-option :value="48" label="48 / page" />
          </el-select>
          <el-button type="primary" @click="runSearch">{{ t('media.search') }}</el-button>
        </div>

        <div class="media-filter-bar">
          <span class="media-filter-bar__label">{{ t('media.bindingFilterLabel') }}</span>
          <div class="media-filter-pills">
            <button
              v-for="option in bindingFilterOptions"
              :key="option.value"
              class="media-filter-pill"
              :class="{ active: query.bindingStatus === option.value }"
              type="button"
              @click="setBindingStatus(option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <el-alert
          v-if="mediaError"
          type="error"
          :closable="false"
          show-icon
          :title="mediaError"
          class="inline-alert"
        />

        <section class="media-migration-panel">
          <div class="media-migration-panel__head">
            <div>
              <strong>{{ t('media.migrationTitle') }}</strong>
              <p>{{ t('media.migrationHint') }}</p>
            </div>
            <div class="card-actions">
              <el-button :loading="migrationLoading" @click="loadLegacyPreview">
                {{ t('media.migrationRefresh') }}
              </el-button>
              <el-button type="primary" plain :loading="migrationRunning" @click="runLegacyMigration(true)">
                {{ t('media.migrationDryRun') }}
              </el-button>
              <el-button
                type="primary"
                :loading="migrationRunning"
                :disabled="!migrationPreview?.summary?.migration_ready"
                @click="runLegacyMigration(false)"
              >
                {{ t('media.migrationExecute') }}
              </el-button>
            </div>
          </div>

          <el-alert
            v-if="migrationError"
            type="error"
            :closable="false"
            show-icon
            :title="migrationError"
            class="inline-alert"
          />

          <div v-if="migrationPreview" class="media-migration-summary">
            <article>
              <span>{{ t('media.migrationSummaryTables') }}</span>
              <strong>{{ formatNumber(migrationPreview.summary.table_count || 0) }}</strong>
            </article>
            <article>
              <span>{{ t('media.migrationSummaryCandidates') }}</span>
              <strong>{{ formatNumber(migrationPreview.summary.candidate_count || 0) }}</strong>
            </article>
            <article>
              <span>{{ t('media.migrationSummaryRecordKeys') }}</span>
              <strong>{{ formatNumber(migrationPreview.summary.with_record_key_count || 0) }}</strong>
            </article>
            <article>
              <span>{{ t('media.migrationSummaryReady') }}</span>
              <strong>{{ migrationPreview.summary.migration_ready ? t('media.migrationReadyYes') : t('media.migrationReadyNo') }}</strong>
            </article>
          </div>

          <el-alert
            v-if="migrationPreview && !migrationPreview.summary.migration_ready"
            type="warning"
            :closable="false"
            show-icon
            :title="t('media.migrationWarning')"
            class="inline-alert"
          />

          <div v-if="migrationPreview?.invalid_tables?.length" class="media-migration-invalid">
            <strong>{{ t('media.migrationInvalidTables') }}</strong>
            <span>{{ migrationPreview.invalid_tables.join(', ') }}</span>
          </div>

          <div v-if="migrationPreview?.tables?.length" class="media-migration-table-list">
            <article
              v-for="table in migrationPreview.tables"
              :key="table.table"
              class="media-migration-table-card"
            >
              <header>
                <strong>{{ table.display_name }}</strong>
                <span>{{ table.table }}</span>
              </header>
              <div class="media-migration-table-meta">
                <span>{{ t('media.migrationCandidateCount') }} · {{ formatNumber(table.candidate_count || 0) }}</span>
                <span>{{ t('media.migrationSummaryRecordKeys') }} · {{ formatNumber(table.with_record_key_count || 0) }}</span>
              </div>
              <ul v-if="table.sample_rows?.length" class="media-migration-samples">
                <li v-for="sample in table.sample_rows" :key="`${table.table}:${sample.record_key}:${sample.pictureid}`">
                  <strong>{{ sample.pictureid }}</strong>
                  <span>{{ sample.record_key }}</span>
                </li>
              </ul>
              <p v-else class="media-migration-empty">{{ t('media.fieldPreviewEmpty') }}</p>
            </article>
          </div>

          <div v-if="migrationResult" class="media-migration-result">
            <strong>{{ t('media.migrationResult') }}</strong>
            <span>{{ t('media.migrationSummaryCandidates') }} · {{ formatNumber(migrationResult.summary.created_assets + migrationResult.summary.reused_assets) }}</span>
            <span>{{ migrationResult.dry_run ? t('media.migrationDryRun') : t('media.migrationExecute') }}</span>
            <span>bindings · +{{ formatNumber(migrationResult.summary.created_bindings || 0) }}</span>
          </div>
        </section>

        <div class="media-grid">
          <div v-if="mediaLoading && !mediaItems.length" class="media-skeleton-grid" aria-hidden="true">
            <div v-for="index in query.pageSize" :key="index" class="media-skeleton-card">
              <div class="media-skeleton-thumb" />
              <div class="media-skeleton-line media-skeleton-line--primary" />
              <div class="media-skeleton-line media-skeleton-line--secondary" />
            </div>
          </div>

          <button
            v-for="asset in mediaItems"
            :key="asset.id"
            class="media-tile"
            :class="{ active: selectedAssetId === asset.id }"
            type="button"
            @click="selectAsset(asset.id)"
          >
            <div class="media-thumb-shell">
              <img
                :src="asset.public_url"
                :alt="asset.alt_text || asset.title || asset.original_filename"
                class="media-thumb"
                loading="lazy"
                decoding="async"
              />
            </div>
            <div class="media-tile-copy">
              <strong>{{ asset.title || asset.original_filename }}</strong>
              <span>{{ formatSourceType(asset.source_type) }} · {{ formatBindingStatus(asset.binding_count) }}</span>
            </div>
          </button>

          <div v-if="!mediaLoading && !mediaItems.length" class="media-empty">
            <strong>{{ emptyStateTitle }}</strong>
            <p>{{ emptyStateHint }}</p>
            <div class="media-empty-actions">
              <el-button v-if="showResetInEmptyState" @click="resetFilters">{{ t('media.reset') }}</el-button>
              <el-button type="primary" @click="openUploadDialog">{{ t('media.upload') }}</el-button>
            </div>
          </div>
        </div>

        <div class="table-footer media-footer">
          <div class="table-meta-inline">
            <span>{{ t('media.total') }} · {{ formatNumber(mediaTotal) }}</span>
            <span>{{ t('table.page') }} · {{ query.page }}</span>
          </div>
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="mediaTotal"
            :current-page="query.page"
            :page-size="query.pageSize"
            @current-change="handlePageChange"
          />
        </div>
      </section>

      <section class="content-card media-card media-card--detail">
        <div v-if="selectedAsset" class="media-detail">
          <div class="content-card-header">
            <div>
              <h3>{{ selectedAsset.title || selectedAsset.original_filename }}</h3>
              <p>{{ selectedAsset.original_filename }}</p>
            </div>
            <div class="card-actions">
              <span v-if="detailLoading" class="media-detail-loading">{{ t('media.loadingDetail') }}</span>
              <el-button @click="copyText(selectedAsset.public_url)">{{ t('media.copyUrl') }}</el-button>
              <el-button @click="copyText(selectedAsset.markdown)">{{ t('media.copyMarkdown') }}</el-button>
              <el-button type="primary" :loading="savingMetadata" @click="saveMetadata">{{ t('media.save') }}</el-button>
              <el-button type="danger" plain @click="deleteAsset(selectedAsset)">{{ t('media.delete') }}</el-button>
            </div>
          </div>

          <div class="media-preview-shell">
            <img
              :src="selectedAsset.public_url"
              :alt="selectedAsset.alt_text || selectedAsset.title || selectedAsset.original_filename"
              class="media-preview-image"
            />
          </div>

          <div class="media-meta-grid">
            <article>
              <span>{{ t('media.metaSource') }}</span>
              <strong>{{ formatSourceType(selectedAsset.source_type) }}</strong>
            </article>
            <article>
              <span>{{ t('media.metaFormat') }}</span>
              <strong>{{ selectedAsset.mime_type || selectedAsset.file_ext || 'image' }}</strong>
            </article>
            <article>
              <span>{{ t('media.metaSize') }}</span>
              <strong>{{ formatBytes(selectedAsset.size_bytes) }}</strong>
            </article>
            <article>
              <span>{{ t('media.metaDimensions') }}</span>
              <strong>{{ formatDimensions(selectedAsset) }}</strong>
            </article>
            <article>
              <span>{{ t('media.metaCreatedAt') }}</span>
              <strong>{{ formatDateTime(selectedAsset.created_at) }}</strong>
            </article>
            <article>
              <span>{{ t('media.metaCreatedBy') }}</span>
              <strong>{{ selectedAsset.created_by_username || '—' }}</strong>
            </article>
            <article>
              <span>{{ t('media.metaBinding') }}</span>
              <strong>{{ formatBindingStatus(selectedAsset.binding_count) }}</strong>
            </article>
          </div>

          <div class="media-edit-grid">
            <el-form-item :label="t('media.metaTitle')">
              <el-input v-model="detailForm.title" />
            </el-form-item>
            <el-form-item :label="t('media.metaSource')">
              <el-select v-model="detailForm.source_type">
                <el-option value="library" :label="t('media.sourceLibrary')" />
                <el-option value="docs" :label="t('media.sourceDocs')" />
                <el-option value="table" :label="t('media.sourceTable')" />
                <el-option value="site" :label="t('media.sourceSite')" />
                <el-option value="legacy_pictureid" :label="t('media.sourceLegacyPictureid')" />
                <el-option value="other" :label="t('media.sourceOther')" />
              </el-select>
            </el-form-item>
            <el-form-item class="media-edit-grid__wide" :label="t('media.altText')">
              <el-input v-model="detailForm.alt_text" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />
            </el-form-item>
          </div>

          <div class="media-detail-block">
            <span>{{ t('media.publicUrl') }}</span>
            <code>{{ selectedAsset.public_url }}</code>
          </div>
          <div class="media-detail-block">
            <span>{{ t('media.objectKey') }}</span>
            <code>{{ selectedAsset.object_key }}</code>
          </div>
          <div class="media-detail-block">
            <span>{{ t('media.markdown') }}</span>
            <code>{{ selectedAsset.markdown }}</code>
          </div>
          <div class="media-detail-block">
            <span>{{ t('media.altText') }}</span>
            <code>{{ selectedAsset.alt_text || '—' }}</code>
          </div>

          <div class="media-reference-panel">
            <div class="media-reference-panel__header">
              <strong>{{ t('media.referencesTitle') }}</strong>
              <span>{{ formatNumber(assetReferences.length) }}</span>
            </div>
            <ul v-if="assetReferences.length" class="media-reference-list media-reference-list--full">
              <li v-for="reference in assetReferences" :key="`${reference.type}:${reference.resource}:${reference.field_name || ''}:${reference.record_key || ''}:${reference.slot_key || ''}:${reference.source || ''}`">
                {{ formatReference(reference) }}
              </li>
            </ul>
            <p v-else class="media-reference-empty">{{ t('media.referencesEmpty') }}</p>
          </div>

          <el-alert
            v-if="deleteBlockedReferences.length"
            type="warning"
            :closable="false"
            show-icon
            :title="t('media.deleteBlockedTitle')"
            class="inline-alert media-inline-alert"
          >
            <template #default>
              <ul class="media-reference-list">
                <li
                  v-for="reference in deleteBlockedReferences"
                  :key="`${reference.type}:${reference.resource}:${reference.field_name || ''}:${reference.record_key || ''}:${reference.slot_key || ''}:${reference.source || ''}`"
                >
                  {{ formatReference(reference) }}
                </li>
              </ul>
            </template>
          </el-alert>
        </div>

        <div v-else class="media-empty media-empty--detail">
          <strong>{{ t('media.selectTitle') }}</strong>
          <p>{{ t('media.selectHint') }}</p>
        </div>
      </section>
    </div>

    <el-dialog
      v-model="uploadDialogVisible"
      :title="t('media.uploadDialogTitle')"
      width="min(720px, 92vw)"
      destroy-on-close
    >
      <div class="media-upload-form">
        <div class="media-upload-picker">
          <input
            ref="fileInputRef"
            class="media-file-input"
            type="file"
            accept="image/*"
            @change="handleFileChange"
          />
          <button class="media-file-button" type="button" @click="fileInputRef?.click()">
            {{ uploadFileLabel }}
          </button>
        </div>

        <el-form-item :label="t('media.metaTitle')">
          <el-input v-model="uploadForm.title" />
        </el-form-item>

        <el-form-item :label="t('media.altText')">
          <el-input v-model="uploadForm.alt_text" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />
        </el-form-item>

        <el-form-item :label="t('media.metaSource')">
          <el-select v-model="uploadForm.source_type">
            <el-option value="library" :label="t('media.sourceLibrary')" />
            <el-option value="docs" :label="t('media.sourceDocs')" />
            <el-option value="table" :label="t('media.sourceTable')" />
            <el-option value="site" :label="t('media.sourceSite')" />
            <el-option value="other" :label="t('media.sourceOther')" />
          </el-select>
        </el-form-item>
      </div>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">{{ t('dialog.cancel') }}</el-button>
        <el-button type="primary" :loading="uploading" @click="submitUpload">{{ t('media.upload') }}</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import {
  ElAlert,
  ElButton,
  ElDialog,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElOption,
  ElPagination,
  ElSelect,
} from 'element-plus';

import {
  deleteAdminMedia,
  fetchAdminMediaDetail,
  fetchAdminLegacyPictureidPreview,
  fetchAdminMediaList,
  runAdminLegacyPictureidMigration,
  saveAdminMedia,
  uploadAdminMedia,
  type AdminMediaAsset,
  type AdminLegacyPictureidMigrateResponse,
  type AdminLegacyPictureidPreviewResponse,
  type AdminMediaReference,
} from '@/utils/admin';
import { useAdminI18n } from '@/utils/adminI18n';

const props = defineProps<{
  csrfToken: string;
}>();

const emit = defineEmits<{
  changed: [];
}>();

const { locale, t } = useAdminI18n();

const mediaLoading = ref(false);
const mediaError = ref('');
const mediaItems = ref<AdminMediaAsset[]>([]);
const mediaTotal = ref(0);
const migrationLoading = ref(false);
const migrationRunning = ref(false);
const migrationError = ref('');
const migrationPreview = ref<AdminLegacyPictureidPreviewResponse | null>(null);
const migrationResult = ref<AdminLegacyPictureidMigrateResponse | null>(null);
const selectedAssetId = ref<number | null>(null);
const selectedAssetDetail = ref<AdminMediaAsset | null>(null);
const assetReferences = ref<AdminMediaReference[]>([]);
const detailLoading = ref(false);
const uploadDialogVisible = ref(false);
const uploading = ref(false);
const savingMetadata = ref(false);
const deleteBlockedReferences = ref<AdminMediaReference[]>([]);
const fileInputRef = ref<HTMLInputElement | null>(null);
const uploadForm = reactive({
  file: null as File | null,
  title: '',
  alt_text: '',
  source_type: 'library',
});
const query = reactive({
  search: '',
  sourceType: 'all',
  bindingStatus: 'all',
  page: 1,
  pageSize: 12,
});

const bindingFilterOptions = computed(() => ([
  { value: 'all', label: t('media.bindingAll') },
  { value: 'bound', label: t('media.bindingBound') },
  { value: 'unbound', label: t('media.bindingUnbound') },
]));
const detailForm = reactive({
  title: '',
  alt_text: '',
  source_type: 'library',
});

const selectedAsset = computed(() => {
  if (!selectedAssetId.value) return null;
  if (selectedAssetDetail.value && selectedAssetDetail.value.id === selectedAssetId.value) {
    return selectedAssetDetail.value;
  }
  return mediaItems.value.find((item) => item.id === selectedAssetId.value) || null;
});
const uploadFileLabel = computed(() => uploadForm.file?.name || t('media.pickFile'));
const hasActiveFilters = computed(
  () => Boolean(query.search.trim()) || query.sourceType !== 'all' || query.bindingStatus !== 'all'
);
const showResetInEmptyState = computed(() => hasActiveFilters.value);
const emptyStateTitle = computed(() =>
  hasActiveFilters.value ? t('media.noMatchTitle') : t('media.emptyTitle')
);
const emptyStateHint = computed(() =>
  hasActiveFilters.value ? t('media.noMatchHint') : t('media.emptyHint')
);

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-US').format(Number(value || 0));
}

function formatBytes(bytes: number) {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = Number(bytes);
  let idx = 0;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx += 1;
  }
  return `${size.toFixed(size >= 10 || idx === 0 ? 0 : 1)} ${units[idx]}`;
}

function formatDateTime(value?: string | null) {
  if (!value) return '—';
  try {
    return new Intl.DateTimeFormat(locale.value === 'zh-CN' ? 'zh-CN' : 'en-US', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatSourceType(value?: string | null) {
  const source = String(value || '').trim().toLowerCase();
  if (!source) return t('media.sourceLibrary');
  if (source === 'library') return t('media.sourceLibrary');
  if (source === 'docs') return t('media.sourceDocs');
  if (source === 'table') return t('media.sourceTable');
  if (source === 'site') return t('media.sourceSite');
  if (source === 'legacy_pictureid') return t('media.sourceLegacyPictureid');
  if (source === 'other') return t('media.sourceOther');
  return source;
}

function formatBindingStatus(bindingCount?: number | null) {
  const count = Number(bindingCount || 0);
  if (count <= 0) return t('media.bindingUnbound');
  return t('media.bindingBoundCount', { count });
}

function formatDimensions(asset: AdminMediaAsset) {
  if (!asset.width || !asset.height) return '—';
  return `${asset.width} × ${asset.height}`;
}

function formatReference(reference: AdminMediaReference) {
  const typeMap: Record<string, string> = {
    doc_image: t('media.referenceDoc'),
    table_field: t('media.referenceTable'),
    table_record_slot: t('media.referenceRecordSlot'),
    site_asset: t('media.referenceSiteAsset'),
    manual_attachment: t('media.referenceManual'),
  };
  const typeLabel = typeMap[reference.type] || reference.type;
  const parts = [typeLabel, reference.resource].filter(Boolean);
  if (reference.field_name) {
    parts.push(`${t('media.metaField')}=${reference.field_name}`);
  }
  if (reference.record_key) {
    parts.push(`${t('media.metaRecord')}=${reference.record_key}`);
  }
  if (reference.slot_key) {
    parts.push(`${t('media.metaSlot')}=${reference.slot_key}`);
  }
  if (reference.source && reference.source !== 'binding') {
    parts.push(reference.source);
  }
  return parts.join(' · ');
}

function selectAsset(assetId: number) {
  selectedAssetId.value = assetId;
  deleteBlockedReferences.value = [];
  void loadSelectedAssetDetail();
}

function openUploadDialog() {
  uploadForm.file = null;
  uploadForm.title = '';
  uploadForm.alt_text = '';
  uploadForm.source_type = 'library';
  uploadDialogVisible.value = true;
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement | null;
  uploadForm.file = input?.files?.[0] || null;
}

function resetFilters() {
  query.search = '';
  query.sourceType = 'all';
  query.bindingStatus = 'all';
  query.page = 1;
  query.pageSize = 12;
  void loadMedia();
}

function runSearch() {
  query.page = 1;
  void loadMedia();
}

function setBindingStatus(value: string) {
  if (query.bindingStatus === value) return;
  query.bindingStatus = value;
  runSearch();
}

function handlePageChange(page: number) {
  query.page = page;
  void loadMedia();
}

function applyDetailState(asset: AdminMediaAsset | null, references: AdminMediaReference[] = []) {
  selectedAssetDetail.value = asset;
  assetReferences.value = Array.isArray(references) ? references : [];
  detailForm.title = asset?.title || '';
  detailForm.alt_text = asset?.alt_text || '';
  detailForm.source_type = asset?.source_type || 'library';
}

async function loadSelectedAssetDetail() {
  if (!selectedAssetId.value) {
    applyDetailState(null, []);
    return;
  }
  detailLoading.value = true;
  try {
    const result = await fetchAdminMediaDetail(selectedAssetId.value);
    applyDetailState(result.asset || null, result.references || []);
  } catch (error: any) {
    applyDetailState(selectedAsset.value, []);
    ElMessage.error(error?.message || t('msg.mediaDetailLoadFailed'));
  } finally {
    detailLoading.value = false;
  }
}

async function loadMedia() {
  mediaLoading.value = true;
  mediaError.value = '';
  try {
    const result = await fetchAdminMediaList({
      search: query.search || undefined,
      source_type: query.sourceType === 'all' ? undefined : query.sourceType,
      binding_status: query.bindingStatus === 'all' ? undefined : query.bindingStatus,
      page: query.page,
      page_size: query.pageSize,
    });
    if (query.page > 1 && !result.items?.length && Number(result.total || 0) > 0) {
      query.page -= 1;
      await loadMedia();
      return;
    }
    mediaItems.value = Array.isArray(result.items) ? result.items : [];
    mediaTotal.value = Number(result.total || 0);
    if (selectedAssetId.value && !mediaItems.value.some((item) => item.id === selectedAssetId.value)) {
      selectedAssetId.value = null;
      applyDetailState(null, []);
    }
  } catch (error: any) {
    mediaError.value = error?.message || t('msg.mediaLoadFailed');
  } finally {
    mediaLoading.value = false;
  }
}

async function loadLegacyPreview() {
  migrationLoading.value = true;
  migrationError.value = '';
  try {
    migrationPreview.value = await fetchAdminLegacyPictureidPreview({ sample_limit: 4 });
  } catch (error: any) {
    migrationError.value = error?.message || t('msg.mediaMigrationPreviewFailed');
  } finally {
    migrationLoading.value = false;
  }
}

async function runLegacyMigration(dryRun: boolean) {
  if (!dryRun) {
    try {
      await ElMessageBox.confirm(
        t('confirm.mediaMigrationExecute'),
        t('confirm.deleteTitle'),
        {
          type: 'warning',
          confirmButtonText: t('media.migrationExecute'),
          cancelButtonText: t('dialog.cancel'),
        }
      );
    } catch {
      return;
    }
  }

  migrationRunning.value = true;
  migrationError.value = '';
  try {
    migrationResult.value = await runAdminLegacyPictureidMigration(
      {
        dry_run: dryRun,
        confirm: !dryRun,
      },
      props.csrfToken
    );
    ElMessage.success(dryRun ? t('msg.mediaMigrationDryRunDone') : t('msg.mediaMigrationDone'));
    await Promise.all([loadLegacyPreview(), loadMedia()]);
    emit('changed');
  } catch (error: any) {
    const message = error?.message || t('msg.mediaMigrationPreviewFailed');
    migrationError.value = message;
    ElMessage.error(message);
  } finally {
    migrationRunning.value = false;
  }
}

async function submitUpload() {
  if (!uploadForm.file) {
    ElMessage.error(t('msg.mediaFileRequired'));
    return;
  }
  uploading.value = true;
  try {
    const result = await uploadAdminMedia(uploadForm.file, {
      csrfToken: props.csrfToken,
      title: uploadForm.title,
      alt_text: uploadForm.alt_text,
      source_type: uploadForm.source_type,
    });
    ElMessage.success(result.deduped ? t('msg.mediaDeduped') : t('msg.mediaUploaded'));
    uploadDialogVisible.value = false;
    query.page = 1;
    await loadMedia();
    if (result.asset?.id) {
      selectedAssetId.value = result.asset.id;
    }
    await loadSelectedAssetDetail();
    emit('changed');
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.mediaUploadFailed'));
  } finally {
    uploading.value = false;
  }
}

async function saveMetadata() {
  if (!selectedAssetId.value) return;
  savingMetadata.value = true;
  try {
    const result = await saveAdminMedia(selectedAssetId.value, {
      csrfToken: props.csrfToken,
      title: detailForm.title,
      alt_text: detailForm.alt_text,
      source_type: detailForm.source_type,
    });
    applyDetailState(result.asset || null, result.references || []);
    await loadMedia();
    ElMessage.success(t('msg.mediaSaved'));
    emit('changed');
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.mediaSaveFailed'));
  } finally {
    savingMetadata.value = false;
  }
}

async function deleteAsset(asset: AdminMediaAsset) {
  try {
    await ElMessageBox.confirm(
      t('confirm.deleteMedia', { name: asset.title || asset.original_filename }),
      t('confirm.deleteTitle'),
      {
        type: 'warning',
        confirmButtonText: t('media.delete'),
        cancelButtonText: t('dialog.cancel'),
      }
    );
  } catch {
    return;
  }
  try {
    deleteBlockedReferences.value = [];
    await deleteAdminMedia(asset.id, props.csrfToken);
    ElMessage.success(t('msg.mediaDeleted'));
    await loadMedia();
    emit('changed');
  } catch (error: any) {
    deleteBlockedReferences.value = Array.isArray(error?.references) ? error.references : [];
    if (asset.id === selectedAssetId.value) {
      assetReferences.value = deleteBlockedReferences.value;
    }
    ElMessage.error(error?.message || t('msg.mediaDeleteFailed'));
  }
}

async function copyText(value: string) {
  try {
    await navigator.clipboard.writeText(value);
    ElMessage.success(t('msg.copySuccess'));
  } catch {
    ElMessage.error(t('msg.copyFailed'));
  }
}

defineExpose({
  refresh: async () => {
    await Promise.all([loadMedia(), loadLegacyPreview()]);
  },
});

watch(
  () => selectedAssetId.value,
  (next, prev) => {
    if (next && next !== prev) {
      void loadSelectedAssetDetail();
    }
  }
);

onMounted(() => {
  void loadMedia();
  void loadLegacyPreview();
});
</script>

<style scoped>
.media-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 18px;
}

.media-card {
  min-width: 0;
}

.media-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) 180px 130px auto;
  gap: 12px;
  margin-bottom: 12px;
}

.media-filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.media-filter-bar__label {
  color: var(--admin-text-muted);
  font-size: 0.92rem;
  font-weight: 600;
}

.media-filter-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.media-filter-pill {
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
  color: var(--admin-text-muted);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.88rem;
  font-weight: 600;
  transition: border-color 160ms ease, color 160ms ease, background 160ms ease;
}

.media-filter-pill:hover {
  border-color: color-mix(in srgb, var(--admin-accent) 42%, var(--admin-border) 58%);
  color: var(--admin-text);
}

.media-filter-pill.active {
  background: color-mix(in srgb, var(--admin-accent-soft) 72%, var(--admin-surface) 28%);
  border-color: color-mix(in srgb, var(--admin-accent) 50%, var(--admin-border) 50%);
  color: var(--admin-accent-strong);
}

.media-migration-panel {
  margin-bottom: 18px;
  border: 1px solid var(--admin-border);
  border-radius: 18px;
  background: var(--admin-surface-muted);
  padding: 16px;
  display: grid;
  gap: 14px;
}

.media-migration-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.media-migration-panel__head strong {
  display: block;
  color: var(--admin-text);
  font-size: 1rem;
}

.media-migration-panel__head p {
  margin: 6px 0 0;
  color: var(--admin-text-muted);
  font-size: 0.86rem;
  line-height: 1.6;
}

.media-migration-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.media-migration-summary article,
.media-migration-result {
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-surface);
  padding: 12px 14px;
}

.media-migration-summary span,
.media-migration-summary strong,
.media-migration-result strong,
.media-migration-result span {
  display: block;
}

.media-migration-summary span,
.media-migration-result span {
  color: var(--admin-text-muted);
  font-size: 0.8rem;
}

.media-migration-summary strong {
  margin-top: 6px;
  color: var(--admin-text);
  font-size: 1.05rem;
}

.media-migration-invalid {
  display: grid;
  gap: 4px;
  color: var(--admin-danger, #b91c1c);
  font-size: 0.85rem;
}

.media-migration-invalid strong {
  color: var(--admin-text);
}

.media-migration-table-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.media-migration-table-card {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface);
  padding: 14px;
  display: grid;
  gap: 10px;
}

.media-migration-table-card header {
  display: grid;
  gap: 3px;
}

.media-migration-table-card strong {
  color: var(--admin-text);
}

.media-migration-table-card header span,
.media-migration-table-meta {
  color: var(--admin-text-muted);
  font-size: 0.82rem;
}

.media-migration-table-meta {
  display: grid;
  gap: 4px;
}

.media-migration-samples {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 6px;
}

.media-migration-samples strong,
.media-migration-samples span {
  display: block;
}

.media-migration-samples span,
.media-migration-empty {
  color: var(--admin-text-muted);
  font-size: 0.8rem;
}

.media-migration-empty {
  margin: 0;
}

.media-migration-result {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  align-items: center;
}

.media-migration-result strong {
  color: var(--admin-text);
}

.media-grid {
  min-height: 280px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
}

.media-skeleton-grid {
  display: contents;
}

.media-skeleton-card {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface-muted);
  padding: 12px;
  display: grid;
  gap: 10px;
}

.media-skeleton-thumb,
.media-skeleton-line {
  position: relative;
  overflow: hidden;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.18), rgba(148, 163, 184, 0.28), rgba(148, 163, 184, 0.18));
  background-size: 220% 100%;
  animation: media-skeleton-shimmer 1.6s linear infinite;
}

.media-skeleton-thumb {
  aspect-ratio: 1 / 1;
  border-radius: 12px;
}

.media-skeleton-line {
  height: 12px;
  border-radius: 999px;
}

.media-skeleton-line--primary {
  width: 78%;
}

.media-skeleton-line--secondary {
  width: 52%;
}

.media-tile {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface-muted);
  padding: 12px;
  text-align: left;
  display: grid;
  gap: 10px;
  transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}

.media-tile:hover,
.media-tile.active {
  border-color: rgba(37, 99, 235, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.08);
}

.media-thumb-shell {
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(226, 232, 240, 0.32));
}

.media-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.media-tile-copy {
  display: grid;
  gap: 4px;
}

.media-tile-copy strong {
  color: var(--admin-text);
  font-size: 0.92rem;
  line-height: 1.35;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.media-tile-copy span {
  color: var(--admin-text-muted);
  font-size: 0.78rem;
}

.media-empty {
  min-height: 240px;
  border: 1px dashed var(--admin-border);
  border-radius: 18px;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 10px;
  padding: 24px;
  color: var(--admin-text-muted);
  text-align: center;
  background: var(--admin-surface-muted);
}

.media-empty strong {
  color: var(--admin-text);
  font-size: 1.02rem;
}

.media-empty-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.media-empty--detail {
  min-height: 100%;
}

.media-footer {
  margin-top: 18px;
}

.media-detail {
  display: grid;
  gap: 16px;
}

.media-detail-loading {
  color: var(--admin-text-muted);
  font-size: 0.82rem;
}

.media-edit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.media-edit-grid :deep(.el-form-item) {
  margin-bottom: 0;
}

.media-edit-grid__wide {
  grid-column: 1 / -1;
}

.media-preview-shell {
  border: 1px solid var(--admin-border);
  border-radius: 18px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(226, 232, 240, 0.3));
}

.media-preview-image {
  width: 100%;
  max-height: 360px;
  object-fit: contain;
  display: block;
}

.media-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.media-meta-grid article {
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  padding: 12px;
  background: var(--admin-surface-muted);
}

.media-meta-grid span,
.media-meta-grid strong {
  display: block;
}

.media-meta-grid span {
  color: var(--admin-text-faint);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.media-meta-grid strong {
  margin-top: 4px;
  color: var(--admin-text);
  line-height: 1.5;
}

.media-detail-block {
  display: grid;
  gap: 8px;
}

.media-detail-block span {
  color: var(--admin-text-faint);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.media-detail-block code {
  display: block;
  padding: 11px 12px;
  border-radius: 12px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
  color: var(--admin-text);
  line-height: 1.6;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.media-inline-alert {
  margin-top: 8px;
}

.media-reference-panel {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  padding: 14px;
  background: var(--admin-surface-muted);
  display: grid;
  gap: 12px;
}

.media-reference-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.media-reference-panel__header strong {
  color: var(--admin-text);
}

.media-reference-panel__header span {
  color: var(--admin-text-muted);
  font-size: 0.88rem;
}

.media-reference-list {
  margin: 8px 0 0;
  padding-left: 18px;
  display: grid;
  gap: 6px;
}

.media-reference-list--full {
  margin: 0;
}

.media-reference-empty {
  margin: 0;
  color: var(--admin-text-muted);
}

.media-upload-form {
  display: grid;
  gap: 16px;
}

@keyframes media-skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -20% 0;
  }
}

.media-upload-picker {
  display: grid;
}

.media-file-input {
  display: none;
}

.media-file-button {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px dashed var(--admin-border);
  background: var(--admin-surface-muted);
  color: var(--admin-text);
  font-weight: 700;
  text-align: left;
}

.media-file-button:hover {
  border-color: rgba(37, 99, 235, 0.34);
  background: rgba(37, 99, 235, 0.06);
}

@media (max-width: 1360px) {
  .media-layout {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 880px) {
  .media-toolbar {
    grid-template-columns: minmax(0, 1fr);
  }

  .media-migration-panel__head,
  .media-migration-result {
    flex-direction: column;
    align-items: stretch;
  }

  .media-migration-summary,
  .media-migration-table-list,
  .media-meta-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .media-edit-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
