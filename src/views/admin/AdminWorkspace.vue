<template>
  <div class="admin-workspace">
    <aside class="workspace-sidebar">
      <div class="sidebar-brand">
        <div class="sidebar-brand-mark">EN</div>
        <div>
          <p>{{ t('brand.admin') }}</p>
          <h1>{{ t('brand.center') }}</h1>
        </div>
      </div>

      <nav class="sidebar-primary">
        <button class="sidebar-primary-item" :class="{ active: activePrimarySection === 'overview' }" type="button" @click="openPrimarySection('overview')">
          <el-icon class="sidebar-primary-icon"><DataAnalysis /></el-icon>
          <div class="sidebar-primary-copy">
            <strong>{{ t('nav.overview') }}</strong>
            <small>{{ t('nav.overviewHint') }}</small>
          </div>
        </button>
        <button class="sidebar-primary-item" :class="{ active: activePrimarySection === 'tables' }" type="button" @click="openPrimarySection('tables')">
          <el-icon class="sidebar-primary-icon"><Grid /></el-icon>
          <div class="sidebar-primary-copy">
            <strong>{{ t('nav.data') }}</strong>
            <small>{{ t('nav.dataHint', { count: resources?.overview.table_count || 0 }) }}</small>
          </div>
          <b class="sidebar-primary-badge">{{ resources?.overview.table_count || 0 }}</b>
        </button>
        <button class="sidebar-primary-item" :class="{ active: activePrimarySection === 'docs' }" type="button" @click="openPrimarySection('docs')">
          <el-icon class="sidebar-primary-icon"><Document /></el-icon>
          <div class="sidebar-primary-copy">
            <strong>{{ t('nav.docs') }}</strong>
            <small>{{ t('nav.docsHint', { count: resources?.overview.doc_count || 0 }) }}</small>
          </div>
          <b class="sidebar-primary-badge">{{ resources?.overview.doc_count || 0 }}</b>
        </button>
        <button class="sidebar-primary-item" :class="{ active: activePrimarySection === 'llm' }" type="button" @click="openPrimarySection('llm')">
          <el-icon class="sidebar-primary-icon"><Monitor /></el-icon>
          <div class="sidebar-primary-copy">
            <strong>{{ t('nav.llm') }}</strong>
            <small>{{ t('nav.llmHint', { provider: providerLabel }) }}</small>
          </div>
          <b class="sidebar-primary-badge">{{ providerLabel }}</b>
        </button>
        <button class="sidebar-primary-item" :class="{ active: activePrimarySection === 'audit' }" type="button" @click="openPrimarySection('audit')">
          <el-icon class="sidebar-primary-icon"><Notebook /></el-icon>
          <div class="sidebar-primary-copy">
            <strong>{{ t('nav.audit') }}</strong>
            <small>{{ t('nav.auditHint', { count: auditRows.length }) }}</small>
          </div>
          <b class="sidebar-primary-badge">{{ auditRows.length }}</b>
        </button>
      </nav>

      <div class="sidebar-fill"></div>

      <div class="sidebar-footer">
        <div class="sidebar-admin-meta">
          <div>
            <span>{{ t('sidebar.currentAdmin') }}</span>
            <strong>{{ adminUser?.username || 'admin' }}</strong>
            <small>{{ adminUser?.role || 'administrator' }}</small>
          </div>
          <b></b>
        </div>
        <div class="sidebar-tools">
          <el-tooltip :content="t('tool.language')" placement="right">
            <button class="sidebar-tool-button sidebar-tool-button--label" type="button" @click="toggleLocale">
              {{ locale === 'zh-CN' ? '中' : 'EN' }}
            </button>
          </el-tooltip>
          <el-tooltip :content="themeLabel" placement="right">
            <button class="sidebar-tool-button" type="button" @click="toggleTheme">
              <svg v-if="themeMode === 'dark'" class="sidebar-tool-svg" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M20.74 15.28A8.68 8.68 0 0 1 8.72 3.26A9 9 0 1 0 20.74 15.28Z" fill="currentColor" />
              </svg>
              <svg v-else-if="themeMode === 'light'" class="sidebar-tool-svg" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M6.76 4.84l-1.8-1.79l-1.41 1.41l1.79 1.8l1.42-1.42Zm10.48 0l1.42 1.42l1.79-1.8l-1.41-1.41l-1.8 1.79ZM12 4h1V1h-2v3h1Zm7 8h3v-2h-3v2Zm-7 7h-1v3h2v-3h-1Zm8.95-.64l-1.79-1.79l-1.42 1.41l1.8 1.8l1.41-1.42ZM4.84 17.24l-1.79 1.8l1.41 1.41l1.8-1.79l-1.42-1.42ZM4 12H1v-2h3v2Zm8 5a5 5 0 1 1 0-10a5 5 0 0 1 0 10Z"
                  fill="currentColor"
                />
              </svg>
              <svg v-else class="sidebar-tool-svg" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 2a10 10 0 0 0 0 20a1 1 0 0 0 0-2a8 8 0 1 1 0-16a1 1 0 0 0 0-2Zm0 2v16a8 8 0 0 0 0-16Z"
                  fill="currentColor"
                />
              </svg>
            </button>
          </el-tooltip>
          <el-tooltip :content="t('tool.returnSite')" placement="right">
            <button class="sidebar-tool-button" type="button" @click="openSiteInNewTab">
              <el-icon><House /></el-icon>
            </button>
          </el-tooltip>
          <el-tooltip :content="t('top.logout')" placement="right">
            <button class="sidebar-tool-button sidebar-tool-button--danger" type="button" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
            </button>
          </el-tooltip>
        </div>
      </div>
    </aside>

    <section class="workspace-main">
      <header class="workspace-topbar">
        <div class="workspace-topbar-copy">
          <p class="workspace-eyebrow">{{ activeSectionEyebrow }}</p>
          <h2>{{ activeSectionTitle }}</h2>
          <div v-if="currentView === 'table'" class="workspace-subtitle-control">
            <span>{{ t('table.currentTable') }}</span>
            <el-select
              :model-value="currentResource"
              filterable
              class="workspace-subtitle-select"
              :placeholder="t('table.pickFromTop')"
              @change="handleTableSelectChange"
            >
              <el-option-group
                v-for="group in groupedTableResources"
                :key="group.key"
                :label="group.label"
              >
                <el-option
                  v-for="table in group.items"
                  :key="table.name"
                  :label="table.label"
                  :value="table.name"
                />
              </el-option-group>
            </el-select>
          </div>
          <div v-else-if="currentView === 'doc'" class="workspace-subtitle-control">
            <span>{{ t('doc.currentDoc') }}</span>
            <el-select
              :model-value="currentResource"
              filterable
              class="workspace-subtitle-select workspace-subtitle-select--doc"
              :placeholder="t('doc.pickFromTop')"
              @change="handleDocSelectChange"
            >
              <el-option
                v-for="doc in docsResources"
                :key="doc.filename"
                :label="doc.filename"
                :value="doc.filename"
              />
            </el-select>
          </div>
          <p>{{ activeSectionDescription }}</p>
        </div>

        <div class="workspace-topbar-actions">
          <el-tooltip :content="t('top.refresh')" placement="bottom">
            <button class="toolbar-icon-button" type="button" @click="refreshCurrentView">
              <el-icon><RefreshRight /></el-icon>
            </button>
          </el-tooltip>
          <div
            v-for="item in topbarStats"
            :key="item.key"
            class="topbar-chip"
          >
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </header>

      <main class="workspace-content" :class="{ 'workspace-content--switching': routeSwitching }">
        <div v-if="routeSwitching" class="workspace-loading-bar"></div>
        <section v-if="currentView === 'overview'" class="workspace-panel">
          <div class="overview-stat-grid">
            <article class="metric-card">
              <span>{{ t('overview.managedTables') }}</span>
              <strong>{{ resources?.overview.table_count || 0 }}</strong>
              <small>{{ t('overview.managedTablesHint', { count: resources?.overview.editable_table_count || 0 }) }}</small>
            </article>
            <article class="metric-card">
              <span>{{ t('overview.totalRecords') }}</span>
              <strong>{{ formatNumber(resources?.overview.total_rows || 0) }}</strong>
              <small>{{ t('overview.totalRecordsHint') }}</small>
            </article>
            <article class="metric-card">
              <span>{{ t('overview.docsLibrary') }}</span>
              <strong>{{ resources?.overview.doc_count || 0 }}</strong>
              <small>{{ t('overview.docsLibraryHint') }}</small>
            </article>
            <article class="metric-card">
              <span>{{ t('overview.defaultModel') }}</span>
              <strong>{{ activeModelLabel }}</strong>
              <small>{{ t('overview.defaultModelHint', { provider: providerLabel, count: llmModelOptions.length }) }}</small>
            </article>
          </div>

          <div class="overview-layout">
            <section class="content-card content-card--wide">
              <div class="content-card-header">
                <div>
                  <h3>{{ t('overview.priorityTables') }}</h3>
                  <p>{{ t('overview.priorityTablesHint') }}</p>
                </div>
              </div>
              <div class="resource-list">
                <button
                  v-for="table in topTableResources"
                  :key="table.name"
                  class="resource-row"
                  type="button"
                  @click="navigate('table', table.name)"
                >
                  <div>
                    <strong>{{ table.label }}</strong>
                    <span>{{ formatCategory(table.category) }} · {{ t('table.columns', { count: table.column_count }) }}</span>
                  </div>
                  <b>{{ formatNumber(table.row_count) }}</b>
                </button>
              </div>
            </section>

            <section class="content-card">
              <div class="content-card-header">
                <div>
                  <h3>{{ t('overview.docsAndHelp') }}</h3>
                  <p>{{ t('overview.docsAndHelpHint') }}</p>
                </div>
                <el-button size="small" @click="createDoc">{{ t('doc.create') }}</el-button>
              </div>
              <div class="resource-list">
                <button
                  v-for="doc in docsResources.slice(0, 6)"
                  :key="doc.filename"
                  class="resource-row"
                  type="button"
                  @click="navigate('doc', doc.filename)"
                >
                  <div>
                    <strong>{{ doc.filename }}</strong>
                    <span>{{ doc.editable ? t('state.docEditable') : t('state.readOnlyResource') }}</span>
                  </div>
                  <b>{{ formatBytes(doc.size) }}</b>
                </button>
              </div>
            </section>
          </div>

          <div class="overview-layout">
            <section class="content-card">
              <div class="content-card-header">
                <div>
                  <h3>{{ t('overview.runtimeSnapshot') }}</h3>
                  <p>{{ t('overview.runtimeSnapshotHint') }}</p>
                </div>
              </div>
              <div class="summary-grid">
                <article>
                  <span>{{ t('field.provider') }}</span>
                  <strong>{{ providerLabel }}</strong>
                </article>
                <article>
                  <span>{{ t('field.model') }}</span>
                  <strong>{{ activeModelLabel }}</strong>
                </article>
                <article>
                  <span>{{ t('field.timeout') }}</span>
                  <strong>{{ llmForm.timeout }}s</strong>
                </article>
                <article>
                  <span>{{ t('field.maxMessages') }}</span>
                  <strong>{{ llmForm.max_messages }} msgs</strong>
                </article>
              </div>
            </section>

            <section class="content-card">
              <div class="content-card-header">
                <div>
                  <h3>{{ t('overview.recentAudit') }}</h3>
                  <p>{{ t('overview.recentAuditHint') }}</p>
                </div>
                <el-button size="small" @click="navigate('audit')">{{ t('overview.viewAll') }}</el-button>
              </div>
              <div class="audit-list">
                <div v-for="row in recentAuditRows" :key="row.id" class="audit-row">
                  <div>
                    <strong>{{ row.action }}</strong>
                    <span>{{ row.table_name || 'system' }} · {{ row.username }}</span>
                  </div>
                  <small>{{ row.created_at || 'recently' }}</small>
                </div>
              </div>
            </section>
          </div>
        </section>

        <section v-else-if="currentView === 'table'" class="workspace-panel">
          <div class="content-card">
            <div class="table-controls-bar">
              <div v-if="selectedTableMeta" class="summary-strip">
                <span>{{ selectedTableMeta.primary_columns.length ? `PK · ${selectedTableMeta.primary_columns.join(', ')}` : t('table.noPk') }}</span>
                <span v-if="canInlineEditTable">{{ t('table.inlineHint') }}</span>
              </div>
              <div class="card-actions">
                <el-button @click="openColumnLabelDialog">{{ t('table.configureColumns') }}</el-button>
                <el-button v-if="selectedTableMeta && !selectedTableMeta.read_only" type="primary" @click="openCreateRow">{{ t('table.create') }}</el-button>
              </div>
            </div>

            <div class="table-toolbar">
              <el-input
                v-model="tableQuery.searchText"
                :placeholder="t('table.searchPlaceholder')"
                clearable
                @keyup.enter="runTableSearch"
              />
              <el-select v-model="tableQuery.searchColumn" clearable :placeholder="t('table.allColumns')">
                <el-option
                  v-for="column in selectedTableMeta?.columns || []"
                  :key="column.name"
                  :label="columnDisplayLabel(column)"
                  :value="column.name"
                />
              </el-select>
              <el-select v-model="tableQuery.pageSize" :placeholder="t('table.pageSize')">
                <el-option :value="10" label="10 / page" />
                <el-option :value="20" label="20 / page" />
                <el-option :value="50" label="50 / page" />
                <el-option :value="100" label="100 / page" />
              </el-select>
              <el-button type="primary" @click="runTableSearch">{{ t('table.search') }}</el-button>
            </div>

            <el-alert
              v-if="tableError"
              type="error"
              :closable="false"
              show-icon
              :title="tableError"
              class="inline-alert"
            />

            <div class="table-shell">
              <el-table
                v-loading="tableLoading"
                :data="tableRows"
                border
                stripe
                class="workspace-table"
                table-layout="fixed"
                :empty-text="t('table.noRows')"
                @sort-change="handleTableSortChange"
              >
                <el-table-column
                  v-for="column in selectedTableMeta?.columns || []"
                  :key="column.name"
                  :prop="column.name"
                  :label="columnDisplayLabel(column)"
                  :min-width="columnWidth(column)"
                  sortable="custom"
                  show-overflow-tooltip
                >
                  <template #default="{ row }">
                    <div
                      v-if="isInlineEditing(row, column.name)"
                      class="table-cell-editor"
                    >
                      <input
                        ref="inlineEditInputRef"
                        v-model="inlineEditDraft"
                        class="table-cell-input"
                        @keydown.enter.stop.prevent="saveInlineEdit"
                        @keydown.esc.stop.prevent="cancelInlineEdit"
                        @blur="saveInlineEdit"
                      />
                    </div>
                    <button
                      v-else
                      class="table-cell-display"
                      :class="{ 'table-cell-display--editable': canInlineEditColumn(column.name) }"
                      type="button"
                      :title="canInlineEditColumn(column.name) ? t('table.inlineHint') : ''"
                      @dblclick.stop="beginInlineEdit(row, column.name)"
                    >
                      <span
                        class="table-cell-value"
                        :class="{ 'table-cell-value--empty': displayCellValue(row[column.name]) === '—' }"
                      >
                        {{ displayCellValue(row[column.name]) }}
                      </span>
                    </button>
                  </template>
                </el-table-column>
                <el-table-column v-if="selectedTableMeta && !selectedTableMeta.read_only" :label="t('table.actions')" fixed="right" width="190">
                  <template #default="{ row }">
                    <div class="row-actions">
                      <el-button size="small" type="primary" @click="openEditRow(row)">{{ t('table.edit') }}</el-button>
                      <el-button size="small" type="danger" plain @click="deleteRow(row)">{{ t('table.delete') }}</el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="table-footer">
              <div class="table-meta-inline">
                <span>{{ t('table.total') }} · {{ formatNumber(tablePagination.total) }}</span>
                <span>{{ t('table.page') }} · {{ tablePagination.page }}</span>
              </div>
              <el-pagination
                background
                layout="total, sizes, prev, pager, next, jumper"
                :total="tablePagination.total"
                :current-page="tablePagination.page"
                :page-size="tableQuery.pageSize"
                :page-sizes="[10, 20, 50, 100]"
                @current-change="handleTablePageChange"
                @size-change="handleTableSizeChange"
              />
            </div>
          </div>
        </section>

        <section v-else-if="currentView === 'doc'" class="workspace-panel">
          <div class="content-card">
            <div class="content-card-header content-card-header--actions-only">
              <div class="card-actions">
                <div v-if="selectedDocIsMarkdown && selectedDoc?.editable" class="doc-view-switch">
                  <button
                    class="doc-view-button"
                    :class="{ active: docViewMode === 'edit' }"
                    type="button"
                    @click="docViewMode = 'edit'"
                  >
                    {{ t('doc.modeEdit') }}
                  </button>
                  <button
                    class="doc-view-button"
                    :class="{ active: docViewMode === 'split' }"
                    type="button"
                    @click="docViewMode = 'split'"
                  >
                    {{ t('doc.modeSplit') }}
                  </button>
                  <button
                    class="doc-view-button"
                    :class="{ active: docViewMode === 'preview' }"
                    type="button"
                    @click="docViewMode = 'preview'"
                  >
                    {{ t('doc.modePreview') }}
                  </button>
                </div>
                <el-button @click="createDoc">{{ t('doc.create') }}</el-button>
                <el-button
                  v-if="selectedDoc?.editable"
                  type="primary"
                  :loading="docSaving"
                  @click="saveCurrentDoc"
                >
                  {{ t('doc.save') }}
                </el-button>
                <el-button
                  v-if="selectedDoc?.editable"
                  type="danger"
                  plain
                  @click="deleteCurrentDoc"
                >
                  {{ t('doc.delete') }}
                </el-button>
              </div>
            </div>

            <el-alert
              v-if="docError"
              type="error"
              :closable="false"
              show-icon
              :title="docError"
              class="inline-alert"
            />

            <div
              v-if="selectedDocIsMarkdown"
              class="doc-editor-layout"
              :class="`doc-editor-layout--${selectedDoc?.editable ? docViewMode : 'preview'}`"
            >
              <section v-if="selectedDoc?.editable && docViewMode !== 'preview'" class="doc-panel">
                <header class="doc-panel-head">
                  <strong>{{ t('doc.sourceMarkdown') }}</strong>
                  <span>{{ t('doc.modeSourceHint') }}</span>
                </header>
                <textarea v-model="docEditorContent" class="doc-editor"></textarea>
              </section>

              <section v-if="!selectedDoc?.editable || docViewMode !== 'edit'" class="doc-panel">
                <header class="doc-panel-head">
                  <strong>{{ t('doc.renderedPreview') }}</strong>
                  <span>{{ t('doc.modePreviewHint') }}</span>
                </header>
                <div
                  ref="docPreviewRef"
                  class="doc-preview doc-rendered"
                  @click="handleDocPreviewClick"
                  v-html="docPreviewHtml"
                ></div>
              </section>
            </div>
            <div v-else-if="selectedDoc?.editable" class="doc-editor-shell">
              <textarea v-model="docEditorContent" class="doc-editor"></textarea>
            </div>
            <div v-else class="doc-preview doc-preview--raw">
              <pre>{{ docEditorContent }}</pre>
            </div>
          </div>
        </section>

        <section v-else-if="currentView === 'llm'" class="workspace-panel">
          <div class="llm-layout">
            <section class="content-card">
              <div class="content-card-header">
                <div>
                  <h3>{{ t('llm.runtime') }}</h3>
                  <p>{{ t('llm.runtimeHint') }}</p>
                </div>
                <el-button type="primary" :loading="llmSaving" @click="saveLLMConfig">{{ t('llm.save') }}</el-button>
              </div>

              <div class="llm-grid">
                <el-form-item :label="t('field.provider')">
                  <el-select v-model="llmForm.active_provider">
                    <el-option label="DeepSeek" value="deepseek" />
                    <el-option label="Ollama" value="ollama" />
                  </el-select>
                </el-form-item>

                <el-form-item :label="t('field.model')">
                  <el-select v-model="llmForm.active_model" filterable allow-create default-first-option>
                    <el-option v-for="model in llmModelOptions" :key="model" :label="model" :value="model" />
                  </el-select>
                </el-form-item>

                <el-form-item :label="t('field.timeout')">
                  <el-input-number v-model="llmForm.timeout" :min="5" :max="600" />
                </el-form-item>

                <el-form-item :label="t('field.maxMessages')">
                  <el-input-number v-model="llmForm.max_messages" :min="1" :max="100" />
                </el-form-item>

                <el-form-item :label="t('field.deepseekBaseUrl')">
                  <el-input v-model="llmForm.deepseek_base_url" placeholder="https://api.deepseek.com" />
                </el-form-item>

                <el-form-item :label="t('field.deepseekDefaultModel')">
                  <el-input v-model="llmForm.deepseek_default_model" placeholder="deepseek-chat" />
                </el-form-item>

                <el-form-item class="span-2" :label="t('field.deepseekApiKey')">
                  <el-input v-model="llmForm.deepseek_api_key" type="password" show-password placeholder="sk-..." />
                </el-form-item>

                <el-form-item class="span-2" :label="t('field.deepseekModels')">
                  <el-input v-model="llmText.deepseek_models_text" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />
                </el-form-item>

                <el-form-item :label="t('field.ollamaBaseUrl')">
                  <el-input v-model="llmForm.ollama_base_url" placeholder="http://127.0.0.1:11434" />
                </el-form-item>

                <el-form-item :label="t('field.ollamaDefaultModel')">
                  <el-input v-model="llmForm.ollama_default_model" placeholder="qwen3:32b" />
                </el-form-item>

                <el-form-item class="span-2" :label="t('field.ollamaModels')">
                  <el-input v-model="llmText.ollama_models_text" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />
                </el-form-item>
              </div>
            </section>

            <section class="content-card">
              <div class="content-card-header">
                <div>
                  <h3>{{ t('llm.systemPrompt') }}</h3>
                  <p>{{ t('llm.systemPromptHint') }}</p>
                </div>
              </div>
              <el-form-item :label="t('llm.systemPrompt')">
                <el-input v-model="llmForm.system_prompt" type="textarea" :autosize="{ minRows: 18, maxRows: 30 }" />
              </el-form-item>
            </section>
          </div>
        </section>

        <section v-else-if="currentView === 'audit'" class="workspace-panel">
          <div class="content-card">
            <div class="content-card-header">
                <div>
                  <h3>{{ t('audit.title') }}</h3>
                  <p>{{ t('audit.hint') }}</p>
                </div>
              </div>

            <el-table :data="auditRows" border :empty-text="t('sidebar.noRecentActions')">
              <el-table-column prop="created_at" :label="t('audit.time')" min-width="180" show-overflow-tooltip />
              <el-table-column prop="username" :label="t('audit.user')" width="130" />
              <el-table-column prop="action" :label="t('audit.action')" width="180" show-overflow-tooltip />
              <el-table-column prop="table_name" :label="t('audit.resource')" min-width="180" show-overflow-tooltip />
              <el-table-column prop="record_pk" :label="t('audit.pk')" min-width="180" show-overflow-tooltip />
              <el-table-column :label="t('audit.detail')" width="110">
                <template #default="{ row }">
                  <el-button size="small" @click="openAuditDetail(row)">{{ t('audit.view') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>
      </main>
    </section>

    <el-dialog
      v-model="rowDialogVisible"
      :title="rowDialogMode === 'create' ? t('dialog.createRow', { name: selectedTableMeta?.label || '' }) : t('dialog.editRow', { name: selectedTableMeta?.label || '' })"
      width="min(1100px, 94vw)"
      top="4vh"
      destroy-on-close
    >
      <div class="row-form-grid">
        <el-form-item
          v-for="column in editableColumns"
          :key="column.name"
          :label="columnDisplayLabel(column)"
        >
          <el-input
            v-model="rowForm[column.name]"
            :type="isTextareaColumn(column.type) ? 'textarea' : 'text'"
            :autosize="isTextareaColumn(column.type) ? { minRows: 2, maxRows: 6 } : undefined"
          />
        </el-form-item>
      </div>
      <template #footer>
        <el-button @click="rowDialogVisible = false">{{ t('dialog.cancel') }}</el-button>
        <el-button type="primary" :loading="rowSaving" @click="saveRow">{{ t('dialog.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="columnLabelDialogVisible"
      :title="t('dialog.configureColumns', { name: selectedTableMeta?.label || '' })"
      width="min(960px, 92vw)"
      destroy-on-close
    >
      <div v-if="selectedTableMeta" class="label-form-grid">
        <div
          v-for="column in selectedTableMeta.columns"
          :key="column.name"
          class="label-form-row"
        >
          <div class="label-form-meta">
            <strong>{{ column.name }}</strong>
            <small>{{ t('table.displayLabel') }}</small>
          </div>
          <el-input
            v-model="columnLabelForm[column.name]"
            :placeholder="column.name"
          />
          <el-checkbox
            :model-value="defaultVisibleColumnsForm.includes(column.name)"
            @change="(checked: unknown) => toggleDefaultVisibleColumn(column.name, Boolean(checked))"
          >
            {{ t('table.defaultVisible') }}
          </el-checkbox>
        </div>
      </div>
      <template #footer>
        <el-button @click="columnLabelDialogVisible = false">{{ t('dialog.cancel') }}</el-button>
        <el-button type="primary" :loading="columnLabelSaving" @click="saveColumnLabels">{{ t('dialog.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="auditDialogVisible" :title="t('audit.detailTitle')" width="min(960px, 92vw)">
      <div class="audit-detail" v-if="selectedAuditRow">
        <div class="audit-meta-grid">
          <div><strong>{{ t('audit.user') }}</strong><span>{{ selectedAuditRow.username }}</span></div>
          <div><strong>{{ t('audit.action') }}</strong><span>{{ selectedAuditRow.action }}</span></div>
          <div><strong>{{ t('audit.resource') }}</strong><span>{{ selectedAuditRow.table_name }}</span></div>
          <div><strong>{{ t('audit.pk') }}</strong><span>{{ selectedAuditRow.record_pk }}</span></div>
        </div>
        <div class="audit-json-grid">
          <div>
            <h4>{{ t('audit.before') }}</h4>
            <pre>{{ selectedAuditRow.before_json || '{}' }}</pre>
          </div>
          <div>
            <h4>{{ t('audit.after') }}</h4>
            <pre>{{ selectedAuditRow.after_json || '{}' }}</pre>
          </div>
        </div>
      </div>
    </el-dialog>

    <vue-easy-lightbox
      :visible="docPreviewLightboxVisible"
      :imgs="docPreviewImages"
      :index="docPreviewImageIndex"
      @hide="docPreviewLightboxVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import VueEasyLightbox from 'vue-easy-lightbox';
import {
  ElButton,
  ElCheckbox,
  ElDialog,
  ElFormItem,
  ElIcon,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElMessageBox,
  ElOption,
  ElOptionGroup,
  ElPagination,
  ElSelect,
  ElTable,
  ElTableColumn,
  ElTooltip
} from 'element-plus';
import {
  DataAnalysis,
  Document,
  Grid,
  House,
  Monitor,
  Notebook,
  RefreshRight,
  SwitchButton
} from '@element-plus/icons-vue';

import {
  createAdminDoc,
  createAdminTableRecord,
  deleteAdminDoc,
  deleteAdminTableRecord,
  fetchAdminAuditLogs,
  fetchAdminDoc,
  fetchAdminLLMSettings,
  fetchAdminResources,
  fetchAdminSession,
  fetchAdminTableMeta,
  fetchAdminTableRows,
  saveAdminTableLabels,
  saveAdminTableVisibleColumns,
  saveAdminDoc,
  saveAdminLLMSettings,
  updateAdminTableRecord,
  type AdminAuditRow,
  type AdminDocDetail,
  type AdminLLMSettings,
  type AdminResourcesResponse,
  type AdminTableMeta,
  type AdminUser
} from '@/utils/admin';
import { useAdminI18n } from '@/utils/adminI18n';
import {
  getDefaultVisibleColumnNames,
  getMergedColumnLabels,
  setCachedTableColumnLabelOverrides,
  setCachedTableVisibleColumnNames,
} from '@/utils/tableColumnLabels';
import { useMarkdown } from '@/utils/useMarkdown';

const route = useRoute();
const router = useRouter();
const { locale, setLocale, toggleTheme, themeLabel, themeMode, t } = useAdminI18n();
const { renderMarkdown } = useMarkdown();

const adminUser = ref<AdminUser | null>(null);
const csrfToken = ref('');
const resources = ref<AdminResourcesResponse | null>(null);
const auditRows = ref<AdminAuditRow[]>([]);
const llmSaving = ref(false);
const resourcesLoading = ref(false);

const selectedTableMeta = ref<AdminTableMeta | null>(null);
const tableRows = ref<Record<string, any>[]>([]);
const tableLoading = ref(false);
const tableError = ref('');
const tableQuery = reactive({
  searchText: '',
  searchColumn: '',
  pageSize: 20,
  sortBy: '',
  sortOrder: 'asc'
});
const tablePagination = reactive({
  page: 1,
  total: 0
});

const selectedDoc = ref<AdminDocDetail | null>(null);
const docLoading = ref(false);
const docSaving = ref(false);
const docError = ref('');
const docEditorContent = ref('');
const docViewMode = ref<'edit' | 'split' | 'preview'>('split');
const docPreviewHtml = ref('');
const docPreviewRef = ref<HTMLElement | null>(null);
const docPreviewLightboxVisible = ref(false);
const docPreviewImages = ref<string[]>([]);
const docPreviewImageIndex = ref(0);
const routeSwitching = ref(false);
let routeSwitchToken = 0;

const rowDialogVisible = ref(false);
const rowDialogMode = ref<'create' | 'edit'>('create');
const rowSaving = ref(false);
const rowForm = reactive<Record<string, string>>({});
const originalRow = ref<Record<string, any> | null>(null);
const columnLabelDialogVisible = ref(false);
const columnLabelSaving = ref(false);
const columnLabelForm = reactive<Record<string, string>>({});
const defaultVisibleColumnsForm = ref<string[]>([]);
const inlineEditRow = ref<Record<string, any> | null>(null);
const inlineEditColumn = ref('');
const inlineEditOriginalRow = ref<Record<string, any> | null>(null);
const inlineEditDraft = ref('');
const inlineEditSaving = ref(false);
const inlineEditInputRef = ref<HTMLInputElement | null>(null);

const auditDialogVisible = ref(false);
const selectedAuditRow = ref<AdminAuditRow | null>(null);

const llmForm = reactive<AdminLLMSettings>({
  active_provider: 'ollama',
  active_model: '',
  timeout: 120,
  max_messages: 20,
  system_prompt: '',
  ollama_base_url: '',
  ollama_default_model: '',
  ollama_models: [],
  deepseek_base_url: '',
  deepseek_api_key: '',
  deepseek_default_model: '',
  deepseek_models: [],
  model_options: []
});
const llmText = reactive({
  ollama_models_text: '',
  deepseek_models_text: ''
});

const currentView = computed(() => String(route.query.view || 'overview'));
const currentResource = computed(() => String(route.query.resource || ''));
const tableResources = computed(() => resources.value?.tables || []);
const docsResources = computed(() => resources.value?.docs || []);
const topTableResources = computed(() =>
  [...tableResources.value]
    .filter((item) => item.category !== 'system')
    .sort((a, b) => (b.row_count || 0) - (a.row_count || 0))
    .slice(0, 6)
);
const providerLabel = computed(() => (llmForm.active_provider === 'deepseek' ? 'DeepSeek' : 'Ollama'));
const llmModelOptions = computed(() => {
  const raw = `${llmText.ollama_models_text},${llmText.deepseek_models_text}`;
  return raw
    .replace(/\n/g, ',')
    .split(',')
    .map((item) => item.trim())
    .filter((item, index, arr) => item && arr.indexOf(item) === index);
});
const activeModelLabel = computed(() => {
  const active = String(llmForm.active_model || '').trim();
  if (active) return active;
  if (llmForm.active_provider === 'deepseek') {
    return String(llmForm.deepseek_default_model || '').trim() || 'deepseek-chat';
  }
  return String(llmForm.ollama_default_model || '').trim() || 'qwen3:32b';
});
const pageBusy = computed(() => resourcesLoading.value || tableLoading.value || docLoading.value || llmSaving.value);
const editableColumns = computed(() => (selectedTableMeta.value?.columns || []).filter((column) => column.name !== 'Index'));
const selectedDocIsMarkdown = computed(() => isMarkdownDoc(selectedDoc.value));
const canInlineEditTable = computed(() => Boolean(selectedTableMeta.value && !selectedTableMeta.value.read_only));
const currentDocResource = computed(() =>
  docsResources.value.find((item) => item.filename === currentResource.value) || null
);
const selectedTableLabelMap = computed(() => {
  if (!selectedTableMeta.value) return {};
  const overrides = Object.fromEntries(
    (selectedTableMeta.value.columns || [])
      .map((column) => [column.name, String(column.label_override || '').trim()])
      .filter(([, label]) => Boolean(label))
  ) as Record<string, string>;
  return getMergedColumnLabels(selectedTableMeta.value.name, overrides);
});
const selectedTableDefaultVisibleColumns = computed(() => {
  if (!selectedTableMeta.value) return [];
  const saved = Array.isArray(selectedTableMeta.value.default_visible_columns)
    ? selectedTableMeta.value.default_visible_columns
    : [];
  return saved.length ? saved : getDefaultVisibleColumnNames(selectedTableMeta.value.name);
});
const activeSectionEyebrow = computed(() => {
  if (currentView.value === 'table') return t('section.eyebrowTable');
  if (currentView.value === 'doc') return t('section.eyebrowDoc');
  if (currentView.value === 'llm') return t('section.eyebrowLlm');
  if (currentView.value === 'audit') return t('section.eyebrowAudit');
  return t('section.eyebrowOverview');
});
const activeSectionTitle = computed(() => {
  if (currentView.value === 'table') return selectedTableMeta.value?.label || currentResource.value || t('section.titleTableFallback');
  if (currentView.value === 'doc') return selectedDoc.value?.filename || currentResource.value || t('section.titleDocFallback');
  if (currentView.value === 'llm') return t('section.titleLlm');
  if (currentView.value === 'audit') return t('section.titleAudit');
  return t('section.titleOverview');
});
const activeSectionDescription = computed(() => {
  if (currentView.value === 'table' && selectedTableMeta.value) {
    return t('section.descTable', {
      category: formatCategory(selectedTableMeta.value.category),
      rows: formatNumber(selectedTableMeta.value.row_count),
      state: selectedTableMeta.value.read_only ? t('state.readOnlyResource') : t('state.editableResource')
    });
  }
  if (currentView.value === 'doc' && selectedDoc.value) {
    return t('section.descDoc', {
      mode: selectedDoc.value.editable ? t('state.docEditable') : t('state.docReadOnly'),
      name: selectedDoc.value.filename
    });
  }
  if (currentView.value === 'llm') {
    return t('section.descLlm');
  }
  if (currentView.value === 'audit') {
    return t('section.descAudit');
  }
  return t('section.descOverview');
});
const topbarStats = computed(() => {
  if (currentView.value === 'table' && selectedTableMeta.value) {
    return [
      { key: 'rows', label: t('top.currentRows'), value: formatNumber(selectedTableMeta.value.row_count || 0) },
      { key: 'columns', label: t('top.columns'), value: String(selectedTableMeta.value.column_count || 0) },
      {
        key: 'state',
        label: t('top.state'),
        value: selectedTableMeta.value.read_only ? t('table.readOnly') : t('table.editable')
      }
    ];
  }
  if (currentView.value === 'doc' && currentDocResource.value) {
    return [
      { key: 'type', label: t('top.type'), value: currentDocResource.value.type || 'doc' },
      { key: 'size', label: t('top.size'), value: formatBytes(currentDocResource.value.size || 0) },
      {
        key: 'state',
        label: t('top.state'),
        value: currentDocResource.value.editable ? t('state.docEditable') : t('state.docReadOnly')
      }
    ];
  }
  if (currentView.value === 'llm') {
    return [
      { key: 'provider', label: t('field.provider'), value: providerLabel.value },
      { key: 'model', label: t('field.model'), value: activeModelLabel.value },
      { key: 'timeout', label: t('field.timeout'), value: `${llmForm.timeout}s` }
    ];
  }
  if (currentView.value === 'audit') {
    return [
      { key: 'records', label: t('nav.audit'), value: String(auditRows.value.length) },
      { key: 'user', label: t('audit.user'), value: adminUser.value?.username || 'admin' }
    ];
  }
  return [
    { key: 'tables', label: t('overview.managedTables'), value: String(resources.value?.overview.table_count || 0) },
    { key: 'docs', label: t('overview.docsLibrary'), value: String(resources.value?.overview.doc_count || 0) },
    { key: 'rows', label: t('overview.totalRecords'), value: formatNumber(resources.value?.overview.total_rows || 0) }
  ];
});
const activePrimarySection = computed(() => {
  if (currentView.value === 'table') return 'tables';
  if (currentView.value === 'doc') return 'docs';
  if (currentView.value === 'llm') return 'llm';
  if (currentView.value === 'audit') return 'audit';
  return 'overview';
});
const groupedTableResources = computed(() => {
  const labelMap: Record<string, string> = {
    disease: t('group.disease'),
    natural: t('group.natural'),
    engineered: t('group.engineered'),
    elements: t('group.elements'),
    genome: t('group.genome'),
    system: t('group.system')
  };
  const order = ['disease', 'natural', 'engineered', 'elements', 'genome', 'system'];
  const groups = new Map<string, typeof tableResources.value>();

  tableResources.value.forEach((item) => {
    const key = String(item.category || 'other').toLowerCase();
    const bucket = groups.get(key) || [];
    bucket.push(item);
    groups.set(key, bucket);
  });

  return [...groups.entries()]
    .sort((a, b) => {
      const aIndex = order.indexOf(a[0]);
      const bIndex = order.indexOf(b[0]);
      const normalizedA = aIndex === -1 ? order.length : aIndex;
      const normalizedB = bIndex === -1 ? order.length : bIndex;
      return normalizedA - normalizedB;
    })
    .map(([key, items]) => ({
      key,
      label: labelMap[key] || key.replace(/_/g, ' '),
      items: [...items].sort((a, b) => (b.row_count || 0) - (a.row_count || 0))
    }));
});
function navigate(view: string, resource = '') {
  if (currentView.value === view && currentResource.value === resource) return;
  routeSwitching.value = true;
  router.replace({
    path: '/workspace',
    query: {
      view,
      ...(resource ? { resource } : {})
    }
  });
}

function openPrimarySection(section: 'overview' | 'tables' | 'docs' | 'llm' | 'audit') {
  if (section === 'overview') {
    navigate('overview');
    return;
  }
  if (section === 'tables') {
    const target = currentView.value === 'table' && currentResource.value
      ? currentResource.value
      : (tableResources.value[0]?.name || '');
    navigate(target ? 'table' : 'overview', target);
    return;
  }
  if (section === 'docs') {
    const target = currentView.value === 'doc' && currentResource.value
      ? currentResource.value
      : (docsResources.value[0]?.filename || '');
    navigate(target ? 'doc' : 'overview', target);
    return;
  }
  if (section === 'llm') {
    navigate('llm');
    return;
  }
  navigate('audit');
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-US').format(Number(value || 0));
}

function formatCategory(category: string) {
  const normalized = String(category || '').toLowerCase();
  if (normalized === 'disease') return t('group.disease');
  if (normalized === 'natural') return t('group.natural');
  if (normalized === 'engineered') return t('group.engineered');
  if (normalized === 'elements') return t('group.elements');
  if (normalized === 'genome') return t('group.genome');
  if (normalized === 'system') return t('group.system');
  return category;
}

function isMarkdownDoc(doc: AdminDocDetail | null) {
  if (!doc) return false;
  return /\.(md|markdown)$/i.test(String(doc.filename || '')) || /markdown|md/i.test(String(doc.type || ''));
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

function columnDisplayLabel(columnOrName: string | { name: string }) {
  const name = typeof columnOrName === 'string' ? columnOrName : columnOrName.name;
  return selectedTableLabelMap.value[name] || name;
}

function columnWidth(columnOrName: string | { name: string }) {
  const label = columnDisplayLabel(columnOrName);
  return Math.min(Math.max(String(label || '').length * 14, 132), 280);
}

function isTextareaColumn(type: string) {
  return /text|json|blob/i.test(String(type || ''));
}

function displayCellValue(value: any) {
  if (value == null || value === '') return '—';
  return String(value);
}

function canInlineEditColumn(columnName: string) {
  if (!canInlineEditTable.value || !selectedTableMeta.value) return false;
  if (columnName === 'Index') return false;
  return !selectedTableMeta.value.primary_columns.includes(columnName);
}

function isInlineEditing(row: Record<string, any>, columnName: string) {
  return inlineEditRow.value === row && inlineEditColumn.value === columnName;
}

async function beginInlineEdit(row: Record<string, any>, columnName: string) {
  if (!canInlineEditColumn(columnName) || inlineEditSaving.value) return;
  inlineEditRow.value = row;
  inlineEditColumn.value = columnName;
  inlineEditOriginalRow.value = { ...row };
  inlineEditDraft.value = row[columnName] == null ? '' : String(row[columnName]);
  await nextTick();
  inlineEditInputRef.value?.focus();
  inlineEditInputRef.value?.select();
}

function cancelInlineEdit() {
  inlineEditRow.value = null;
  inlineEditColumn.value = '';
  inlineEditOriginalRow.value = null;
  inlineEditDraft.value = '';
}

async function saveInlineEdit() {
  if (!selectedTableMeta.value || !inlineEditRow.value || !inlineEditColumn.value || inlineEditSaving.value) return;
  const row = inlineEditRow.value;
  const columnName = inlineEditColumn.value;
  const previousValue = row[columnName] == null ? '' : String(row[columnName]);
  if (inlineEditDraft.value === previousValue) {
    cancelInlineEdit();
    return;
  }
  inlineEditSaving.value = true;
  try {
    await updateAdminTableRecord(
      selectedTableMeta.value.name,
      {
        original_row: inlineEditOriginalRow.value,
        updates: {
          [columnName]: inlineEditDraft.value
        }
      },
      csrfToken.value
    );
    row[columnName] = inlineEditDraft.value;
    ElMessage.success({
      message: t('msg.cellSaved'),
      duration: 1000
    });
    cancelInlineEdit();
    void loadAuditLogs();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowSaveFailed'));
  } finally {
    inlineEditSaving.value = false;
  }
}

function openSiteInNewTab() {
  window.open('/', '_blank', 'noopener,noreferrer');
}

function handleTableSelectChange(tableName: string) {
  if (!tableName) return;
  navigate('table', tableName);
}

function handleDocSelectChange(filename: string) {
  if (!filename) return;
  navigate('doc', filename);
}

function toggleLocale() {
  setLocale(locale.value === 'zh-CN' ? 'en' : 'zh-CN');
}

function getDocPreviewImageSources() {
  if (!docPreviewRef.value) return [];
  return Array.from(docPreviewRef.value.querySelectorAll('img'))
    .map((image) => image.getAttribute('data-src') || image.getAttribute('src') || (image as HTMLImageElement).currentSrc || '')
    .map((src) => String(src || '').trim())
    .filter(Boolean);
}

function decorateDocPreviewImages() {
  if (!docPreviewRef.value) return;
  Array.from(docPreviewRef.value.querySelectorAll('img')).forEach((image) => {
    image.setAttribute('loading', 'lazy');
    image.setAttribute('decoding', 'async');
    image.setAttribute('data-previewable', 'true');
  });
}

function handleDocPreviewClick(event: MouseEvent) {
  const target = event.target as HTMLElement | null;
  if (!target || !docPreviewRef.value) return;
  const image = target.closest('img');
  if (!(image instanceof HTMLImageElement) || !docPreviewRef.value.contains(image)) return;

  const sources = getDocPreviewImageSources();
  const source = image.getAttribute('data-src') || image.getAttribute('src') || image.currentSrc || '';
  if (!source) return;

  const index = sources.indexOf(source);
  docPreviewImages.value = sources.length ? sources : [source];
  docPreviewImageIndex.value = index >= 0 ? index : 0;
  docPreviewLightboxVisible.value = true;
}

async function syncRouteState() {
  const token = ++routeSwitchToken;
  routeSwitching.value = true;
  try {
    if (currentView.value === 'table' && currentResource.value) {
      tablePagination.page = 1;
      await selectTable(currentResource.value);
      return;
    }
    if (currentView.value === 'doc' && currentResource.value) {
      await loadSelectedDoc();
      return;
    }
    if (currentView.value === 'llm') {
      await loadLLMSettings();
      return;
    }
    if (currentView.value === 'audit') {
      await loadAuditLogs();
    }
  } finally {
    if (token === routeSwitchToken) {
      routeSwitching.value = false;
    }
  }
}

function openAuditDetail(row: AdminAuditRow) {
  selectedAuditRow.value = row;
  auditDialogVisible.value = true;
}

async function ensureAdminSession() {
  const session = await fetchAdminSession();
  if (!session) {
    await router.replace('/login');
    return false;
  }
  adminUser.value = session.user;
  csrfToken.value = session.csrf_token;
  return true;
}

async function loadResources() {
  resourcesLoading.value = true;
  try {
    resources.value = await fetchAdminResources();
  } finally {
    resourcesLoading.value = false;
  }
}

function applyLLMSettings(settings: AdminLLMSettings | null) {
  if (!settings) return;
  llmForm.active_provider = settings.active_provider || 'ollama';
  llmForm.active_model = settings.active_model || '';
  llmForm.timeout = Number(settings.timeout || 120);
  llmForm.max_messages = Number(settings.max_messages || 20);
  llmForm.system_prompt = settings.system_prompt || '';
  llmForm.ollama_base_url = settings.ollama_base_url || '';
  llmForm.ollama_default_model = settings.ollama_default_model || '';
  llmForm.deepseek_base_url = settings.deepseek_base_url || '';
  llmForm.deepseek_api_key = settings.deepseek_api_key || '';
  llmForm.deepseek_default_model = settings.deepseek_default_model || '';
  llmText.ollama_models_text = Array.isArray(settings.ollama_models) ? settings.ollama_models.join(', ') : '';
  llmText.deepseek_models_text = Array.isArray(settings.deepseek_models) ? settings.deepseek_models.join(', ') : '';
}

async function loadLLMSettings() {
  applyLLMSettings(await fetchAdminLLMSettings());
}

async function loadAuditLogs() {
  auditRows.value = await fetchAdminAuditLogs(40);
}

async function selectTable(table: string) {
  if (!table) return;
  tableError.value = '';
  tableLoading.value = true;
  try {
    selectedTableMeta.value = await fetchAdminTableMeta(table);
    const availableColumns = new Set((selectedTableMeta.value.columns || []).map((column) => column.name));
    const preferredColumns = [
      ...(selectedTableMeta.value.primary_columns || []),
      'id',
      'ID',
      'Index',
      'PMID',
      'pmid'
    ];

    if (tableQuery.searchColumn && !availableColumns.has(tableQuery.searchColumn)) {
      tableQuery.searchColumn = '';
    }

    if (!tableQuery.searchColumn) {
      tableQuery.searchColumn = preferredColumns.find((column) => availableColumns.has(column)) || '';
    }
    await loadSelectedTable();
  } catch (error: any) {
    tableError.value = error?.message || t('msg.tableMetaFailed');
  } finally {
    tableLoading.value = false;
  }
}

async function loadSelectedTable() {
  const table = currentResource.value;
  if (!table) return;
  tableError.value = '';
  tableLoading.value = true;
  cancelInlineEdit();
  try {
    if (selectedTableMeta.value && tableQuery.searchColumn) {
      const validColumns = new Set((selectedTableMeta.value.columns || []).map((column) => column.name));
      if (!validColumns.has(tableQuery.searchColumn)) {
        tableQuery.searchColumn = '';
      }
    }
    const result = await fetchAdminTableRows(table, {
      page: tablePagination.page,
      page_size: tableQuery.pageSize,
      search_text: tableQuery.searchText,
      search_column: tableQuery.searchColumn,
      sort_by: tableQuery.sortBy,
      sort_order: tableQuery.sortOrder,
      case_insensitive: true,
      use_fulltext: !tableQuery.searchColumn
    });
    tableRows.value = Array.isArray(result.rows) ? result.rows : [];
    tablePagination.total = Number(result.total || 0);
  } catch (error: any) {
    tableError.value = error?.message || t('msg.tableLoadFailed');
  } finally {
    tableLoading.value = false;
  }
}

function runTableSearch() {
  tablePagination.page = 1;
  void loadSelectedTable();
}

function handleTablePageChange(page: number) {
  tablePagination.page = page;
  void loadSelectedTable();
}

function handleTableSizeChange(size: number) {
  tableQuery.pageSize = size;
  tablePagination.page = 1;
  void loadSelectedTable();
}

function handleTableSortChange({ prop, order }: { prop?: string; order?: string }) {
  tableQuery.sortBy = prop || '';
  tableQuery.sortOrder = order === 'descending' ? 'desc' : 'asc';
  tablePagination.page = 1;
  void loadSelectedTable();
}

function resetRowForm() {
  Object.keys(rowForm).forEach((key) => delete rowForm[key]);
}

function openCreateRow() {
  cancelInlineEdit();
  rowDialogMode.value = 'create';
  originalRow.value = null;
  resetRowForm();
  editableColumns.value.forEach((column) => {
    rowForm[column.name] = '';
  });
  rowDialogVisible.value = true;
}

function resetColumnLabelForm() {
  Object.keys(columnLabelForm).forEach((key) => delete columnLabelForm[key]);
}

function openColumnLabelDialog() {
  if (!selectedTableMeta.value) return;
  resetColumnLabelForm();
  selectedTableMeta.value.columns.forEach((column) => {
    columnLabelForm[column.name] = columnDisplayLabel(column.name);
  });
  defaultVisibleColumnsForm.value = [...selectedTableDefaultVisibleColumns.value];
  columnLabelDialogVisible.value = true;
}

function toggleDefaultVisibleColumn(columnName: string, checked: boolean) {
  if (checked) {
    if (!defaultVisibleColumnsForm.value.includes(columnName)) {
      defaultVisibleColumnsForm.value = [...defaultVisibleColumnsForm.value, columnName];
    }
    return;
  }
  defaultVisibleColumnsForm.value = defaultVisibleColumnsForm.value.filter((item) => item !== columnName);
}

async function saveColumnLabels() {
  if (!selectedTableMeta.value) return;
  columnLabelSaving.value = true;
  try {
    const labels = Object.fromEntries(
      Object.entries(columnLabelForm).map(([column, label]) => [column, String(label || '').trim()])
    );
    const [labelResult, visibleResult] = await Promise.all([
      saveAdminTableLabels(selectedTableMeta.value.name, { labels }, csrfToken.value),
      saveAdminTableVisibleColumns(
        selectedTableMeta.value.name,
        { columns: defaultVisibleColumnsForm.value },
        csrfToken.value
      )
    ]);
    const saved = labelResult.labels || {};
    const savedVisibleColumns = Array.isArray(visibleResult.columns) ? visibleResult.columns : [];
    selectedTableMeta.value = {
      ...selectedTableMeta.value,
      columns: (selectedTableMeta.value.columns || []).map((column) => ({
        ...column,
        label_override: saved[column.name] || ''
      })),
      default_visible_columns: savedVisibleColumns
    };
    setCachedTableColumnLabelOverrides(selectedTableMeta.value.name, saved);
    setCachedTableVisibleColumnNames(selectedTableMeta.value.name, savedVisibleColumns);
    columnLabelDialogVisible.value = false;
    ElMessage.success(t('msg.columnsConfigured'));
    void loadAuditLogs();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.columnsConfigFailed'));
  } finally {
    columnLabelSaving.value = false;
  }
}

function openEditRow(row: Record<string, any>) {
  cancelInlineEdit();
  rowDialogMode.value = 'edit';
  originalRow.value = { ...row };
  resetRowForm();
  editableColumns.value.forEach((column) => {
    rowForm[column.name] = row[column.name] == null ? '' : String(row[column.name]);
  });
  rowDialogVisible.value = true;
}

async function saveRow() {
  if (!selectedTableMeta.value) return;
  rowSaving.value = true;
  try {
    if (rowDialogMode.value === 'create') {
      await createAdminTableRecord(selectedTableMeta.value.name, { ...rowForm }, csrfToken.value);
      ElMessage.success(t('msg.recordCreated'));
    } else {
      await updateAdminTableRecord(
        selectedTableMeta.value.name,
        {
          original_row: originalRow.value,
          updates: { ...rowForm }
        },
        csrfToken.value
      );
      ElMessage.success(t('msg.recordUpdated'));
    }
    rowDialogVisible.value = false;
    await loadResources();
    await selectTable(selectedTableMeta.value.name);
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowSaveFailed'));
  } finally {
    rowSaving.value = false;
  }
}

async function deleteRow(row: Record<string, any>) {
  if (!selectedTableMeta.value) return;
  cancelInlineEdit();
  try {
    await ElMessageBox.confirm(t('confirm.deleteRow'), t('confirm.deleteTitle'), {
      type: 'warning',
      confirmButtonText: t('table.delete'),
      cancelButtonText: t('dialog.cancel')
    });
  } catch {
    return;
  }
  try {
    await deleteAdminTableRecord(selectedTableMeta.value.name, { original_row: row }, csrfToken.value);
    ElMessage.success(t('msg.recordDeleted'));
    await loadResources();
    await loadSelectedTable();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowDeleteFailed'));
  }
}

async function loadSelectedDoc() {
  if (!currentResource.value) return;
  docError.value = '';
  docLoading.value = true;
  try {
    selectedDoc.value = await fetchAdminDoc(currentResource.value);
    docEditorContent.value = selectedDoc.value.content || '';
    docViewMode.value = selectedDoc.value.editable
      ? (isMarkdownDoc(selectedDoc.value) ? 'split' : 'edit')
      : 'preview';
  } catch (error: any) {
    docError.value = error?.message || t('msg.docLoadFailed');
  } finally {
    docLoading.value = false;
  }
}

async function createDoc() {
  try {
    const { value } = await ElMessageBox.prompt(t('prompt.createDocMessage'), t('prompt.createDocTitle'), {
      confirmButtonText: t('prompt.create'),
      cancelButtonText: t('dialog.cancel'),
      inputValue: '',
      inputPlaceholder: t('prompt.createDocPlaceholder')
    });
    const filename = String(value || '').trim();
    if (!filename) return;
    await createAdminDoc({ filename, content: `# ${filename.replace(/\.md$/i, '')}\n\n` }, csrfToken.value);
    ElMessage.success(t('msg.docCreated'));
    await loadResources();
    navigate('doc', filename);
  } catch (error: any) {
    if (error === 'cancel' || error === 'close') return;
    ElMessage.error(error?.message || t('msg.docCreateFailed'));
  }
}

async function saveCurrentDoc() {
  if (!selectedDoc.value?.editable) return;
  docSaving.value = true;
  try {
    await saveAdminDoc(selectedDoc.value.filename, { content: docEditorContent.value }, csrfToken.value);
    ElMessage.success(t('msg.docSaved'));
    await loadResources();
    await loadSelectedDoc();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.docSaveFailed'));
  } finally {
    docSaving.value = false;
  }
}

async function deleteCurrentDoc() {
  if (!selectedDoc.value?.editable) return;
  try {
    await ElMessageBox.confirm(t('confirm.deleteDoc', { name: selectedDoc.value.filename }), t('confirm.deleteTitle'), {
      type: 'warning',
      confirmButtonText: t('table.delete'),
      cancelButtonText: t('dialog.cancel')
    });
  } catch {
    return;
  }
  try {
    await deleteAdminDoc(selectedDoc.value.filename, csrfToken.value);
    ElMessage.success(t('msg.docDeleted'));
    await loadResources();
    selectedDoc.value = null;
    docEditorContent.value = '';
    navigate('overview');
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.docDeleteFailed'));
  }
}

async function saveLLMConfig() {
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
      ollama_models: llmText.ollama_models_text,
      deepseek_base_url: llmForm.deepseek_base_url,
      deepseek_api_key: llmForm.deepseek_api_key,
      deepseek_default_model: llmForm.deepseek_default_model,
      deepseek_models: llmText.deepseek_models_text
    });
    applyLLMSettings(settings);
    ElMessage.success(t('msg.llmSaved'));
    await loadAuditLogs();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.llmSaveFailed'));
  } finally {
    llmSaving.value = false;
  }
}

async function handleLogout() {
  try {
    await fetch('/admin/api/logout', {
      method: 'POST',
      credentials: 'same-origin'
    });
  } finally {
    await router.replace('/login');
  }
}

async function refreshCurrentView() {
  cancelInlineEdit();
  await loadResources();
  if (currentView.value === 'table' && currentResource.value) {
    await selectTable(currentResource.value);
    return;
  }
  if (currentView.value === 'doc' && currentResource.value) {
    await loadSelectedDoc();
    return;
  }
  if (currentView.value === 'llm') {
    await loadLLMSettings();
    return;
  }
  if (currentView.value === 'audit') {
    await loadAuditLogs();
    return;
  }
  await loadAuditLogs();
}

watch(
  () => [docEditorContent.value, selectedDocIsMarkdown.value] as const,
  async ([content, isMarkdown]) => {
    if (!isMarkdown) {
      docPreviewHtml.value = '';
      docPreviewImages.value = [];
      docPreviewLightboxVisible.value = false;
      return;
    }
    docPreviewHtml.value = await renderMarkdown(content || '');
    await nextTick();
    decorateDocPreviewImages();
    docPreviewImages.value = getDocPreviewImageSources();
  },
  { immediate: true }
);

watch(
  () => [currentView.value, currentResource.value],
  async () => {
    if (!adminUser.value) return;
    await syncRouteState();
  },
  { immediate: false }
);

onMounted(async () => {
  const authed = await ensureAdminSession();
  if (!authed) return;
  await Promise.all([loadResources(), loadLLMSettings(), loadAuditLogs()]);
  if (!route.query.view) {
    navigate('overview');
  } else {
    await syncRouteState();
  }
});
</script>

<style scoped>
.admin-workspace {
  height: 100vh;
  display: grid;
  grid-template-columns: 284px minmax(0, 1fr);
  gap: 0;
  background: #eff3f8;
  overflow: hidden;
}

.workspace-sidebar {
  min-height: 100vh;
  padding: 20px 16px 16px;
  background: var(--admin-sidebar-bg);
  color: var(--admin-sidebar-text);
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  gap: 14px;
  border-right: 1px solid var(--admin-sidebar-border);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.sidebar-brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #eff6ff;
  font-weight: 900;
  letter-spacing: 0.1em;
}

.sidebar-brand p,
.sidebar-brand h1 {
  margin: 0;
}

.sidebar-brand p {
  color: var(--admin-sidebar-brand-subtext);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.sidebar-brand h1 {
  font-size: 1.26rem;
  color: var(--admin-sidebar-brand-text);
}

.sidebar-primary {
  display: grid;
  gap: 8px;
}

.sidebar-fill {
  min-height: 0;
}

.sidebar-primary-item {
  width: 100%;
  padding: 11px 12px;
  border-radius: 14px;
  border: 1px solid var(--admin-sidebar-item-border);
  background: var(--admin-sidebar-item-bg);
  color: inherit;
  text-align: left;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}

.sidebar-primary-item:hover {
  background: var(--admin-sidebar-item-hover);
  border-color: var(--admin-sidebar-item-border-hover);
  transform: translateX(2px);
}

.sidebar-primary-copy {
  min-width: 0;
}

.sidebar-primary-icon {
  color: var(--admin-sidebar-icon);
  font-size: 1rem;
}

.sidebar-primary-copy strong,
.sidebar-primary-copy small {
  display: block;
}

.sidebar-primary-copy strong {
  color: var(--admin-sidebar-text);
  font-weight: 800;
  font-size: 0.92rem;
}

.sidebar-primary-copy small {
  margin-top: 2px;
  color: var(--admin-sidebar-text-muted);
  font-size: 0.78rem;
}

.sidebar-primary-badge {
  min-width: 34px;
  padding: 5px 8px;
  border-radius: 999px;
  background: var(--admin-sidebar-badge-bg);
  color: var(--admin-sidebar-badge-text);
  font-size: 0.72rem;
  font-weight: 800;
  text-align: center;
  white-space: nowrap;
}

.sidebar-primary-item.active {
  background: var(--admin-sidebar-item-active);
  border-color: var(--admin-sidebar-item-active-border);
  box-shadow: inset 3px 0 0 var(--admin-accent);
}

.sidebar-footer {
  display: grid;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--admin-sidebar-border);
}

.admin-segmented {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.admin-segmented-item,
.topbar-theme-toggle {
  border: 0;
  background: transparent;
  color: var(--admin-text-muted);
  padding: 9px 12px;
  border-radius: 999px;
  font-weight: 700;
}

.admin-segmented-item.active {
  background: rgba(37, 99, 235, 0.16);
  color: var(--admin-text);
}

.sidebar-admin-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.sidebar-admin-meta span,
.sidebar-admin-meta strong,
.sidebar-admin-meta small {
  display: block;
}

.sidebar-admin-meta span {
  color: var(--admin-sidebar-brand-subtext);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.sidebar-admin-meta strong {
  margin-top: 4px;
  color: var(--admin-sidebar-text);
}

.sidebar-admin-meta small {
  color: var(--admin-sidebar-text-muted);
}

.sidebar-admin-meta b {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.12);
}

.sidebar-tools {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px;
  border-radius: 999px;
  background: var(--admin-sidebar-tools-bg);
  border: 1px solid var(--admin-sidebar-border);
}

.sidebar-tool-button {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: transparent;
  color: var(--admin-sidebar-text);
}

.sidebar-tool-button:hover {
  background: var(--admin-sidebar-tools-hover);
}

.sidebar-tool-svg {
  width: 17px;
  height: 17px;
}

.sidebar-tool-button--label {
  width: 44px;
  font-size: 0.82rem;
  font-weight: 800;
}

.sidebar-tool-button--danger {
  color: var(--admin-sidebar-danger);
}

.workspace-main {
  min-width: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 100vh;
  background: var(--admin-page);
  overflow: hidden;
}

.workspace-topbar {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding: 28px 32px 20px;
  border-bottom: 1px solid var(--admin-border);
  background: var(--admin-topbar-bg);
}

.workspace-topbar-copy {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.workspace-eyebrow {
  margin: 0;
  color: #2563eb;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.workspace-topbar h2 {
  margin: 0;
  font-size: clamp(2rem, 3vw, 2.8rem);
  line-height: 1.05;
  color: var(--admin-text);
}

.workspace-subtitle-control {
  display: grid;
  gap: 6px;
  min-width: min(100%, 360px);
}

.workspace-subtitle-control span {
  color: var(--admin-text-faint);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.workspace-subtitle-select {
  width: min(100%, 360px);
}

.workspace-subtitle-select :deep(.el-select__wrapper) {
  min-height: 42px;
  padding-inline: 12px;
  border-radius: 12px;
}

.workspace-subtitle-select :deep(.el-select__selected-item) {
  font-size: 0.96rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--admin-text);
}

.workspace-subtitle-select :deep(.el-select__caret) {
  font-size: 0.95rem;
  color: var(--admin-text-faint);
}

.workspace-topbar p {
  margin: 0;
  color: var(--admin-text-muted);
  max-width: 72ch;
  line-height: 1.7;
}

.workspace-topbar-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  align-items: center;
}

.topbar-tools {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px;
  border-radius: 999px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
}

.toolbar-icon-button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: transparent;
  color: var(--admin-text-muted);
}

.toolbar-icon-button .el-icon {
  font-size: 1rem;
}

.toolbar-icon-button:hover {
  background: var(--admin-surface-muted);
  color: var(--admin-text);
}

.toolbar-icon-button--label {
  width: 46px;
  font-weight: 800;
  font-size: 0.82rem;
}

.toolbar-icon-button--danger {
  color: var(--admin-danger);
}

.topbar-chip {
  min-width: 124px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
}

.topbar-chip span,
.topbar-chip strong {
  display: block;
}

.topbar-chip span {
  color: var(--admin-text-faint);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.topbar-chip strong {
  margin-top: 4px;
  color: var(--admin-text);
  font-size: 1rem;
}

.workspace-content {
  min-width: 0;
  overflow: auto;
  overflow-x: hidden;
  padding: 24px 32px 36px;
  transition: opacity 0.18s ease, transform 0.18s ease;
  position: relative;
}

.workspace-panel {
  display: grid;
  gap: 18px;
  min-width: 0;
}

.workspace-content--switching {
  opacity: 0.72;
  transform: translateY(4px);
}

.workspace-loading-bar {
  position: sticky;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent 0%, rgba(37, 99, 235, 0.24) 20%, #2563eb 50%, rgba(37, 99, 235, 0.24) 80%, transparent 100%);
  background-size: 200% 100%;
  animation: workspace-loading 1.1s linear infinite;
  z-index: 2;
}

.content-card {
  border-radius: 16px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
  padding: 22px;
  min-width: 0;
}

.content-card--wide {
  min-width: 0;
}

.content-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.content-card-header--actions-only {
  justify-content: flex-end;
  margin-bottom: 14px;
}

.table-controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.content-card-header h3 {
  margin: 0 0 6px;
  color: var(--admin-text);
  font-size: 1.3rem;
}

.content-card-header p {
  margin: 0;
  color: var(--admin-text-muted);
  line-height: 1.65;
}

.card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.overview-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  padding: 18px;
  border-radius: 14px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
}

.metric-card span,
.metric-card strong,
.metric-card small {
  display: block;
}

.metric-card span {
  color: var(--admin-text-faint);
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 800;
}

.metric-card strong {
  margin: 8px 0 10px;
  color: var(--admin-text);
  font-size: clamp(1.5rem, 2vw, 2.1rem);
  line-height: 1.05;
}

.metric-card small {
  color: var(--admin-text-muted);
  line-height: 1.6;
}

.overview-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 18px;
}

.resource-list,
.audit-list {
  display: grid;
  gap: 10px;
}

.resource-row,
.audit-row {
  width: 100%;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
  text-align: left;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.resource-row strong,
.resource-row span,
.resource-row b,
.audit-row strong,
.audit-row span,
.audit-row small {
  display: block;
}

.resource-row strong,
.resource-row b,
.audit-row strong {
  color: var(--admin-text);
}

.resource-row span,
.audit-row span,
.audit-row small {
  color: var(--admin-text-muted);
}

.resource-row span,
.audit-row span {
  margin-top: 4px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.summary-grid article {
  padding: 16px;
  border-radius: 14px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
}

.summary-grid span,
.summary-grid strong {
  display: block;
}

.summary-grid span {
  color: var(--admin-text-faint);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.summary-grid strong {
  margin-top: 6px;
  color: var(--admin-text);
  font-size: 1.1rem;
}

.summary-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 0;
  flex: 1 1 360px;
}

.summary-strip span {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
  color: var(--admin-text-muted);
  font-size: 0.88rem;
  font-weight: 700;
}

.table-toolbar {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 220px 150px auto;
  gap: 12px;
  margin-bottom: 14px;
}

.inline-alert {
  margin-bottom: 14px;
}

.table-shell {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-surface);
}

.workspace-table {
  width: 100%;
}

.table-shell :deep(.el-table) {
  min-width: 100%;
  background: var(--admin-table-row-bg);
  color: var(--admin-text);
  --el-table-border-color: var(--admin-border);
  --el-table-header-bg-color: var(--admin-table-header-bg);
  --el-table-tr-bg-color: var(--admin-table-row-bg);
  --el-table-row-hover-bg-color: var(--admin-table-row-hover);
  --el-table-current-row-bg-color: var(--admin-table-row-hover);
  --el-table-header-text-color: var(--admin-table-header-text);
  --el-table-text-color: var(--admin-text);
}

.table-shell :deep(.el-table th.el-table__cell) {
  font-weight: 800;
  background: var(--admin-table-header-bg) !important;
  color: var(--admin-table-header-text);
}

.table-shell :deep(.el-table td.el-table__cell) {
  background: var(--admin-table-row-bg);
  color: var(--admin-text);
}

.table-shell :deep(.el-table .el-table__row--striped td.el-table__cell) {
  background: var(--admin-table-row-alt);
}

.table-shell :deep(.el-table td.el-table__cell),
.table-shell :deep(.el-table th.el-table__cell) {
  border-right-color: var(--admin-border);
}

.table-shell :deep(.el-table__inner-wrapper),
.table-shell :deep(.el-table__header-wrapper),
.table-shell :deep(.el-table__body-wrapper),
.table-shell :deep(.el-table__fixed),
.table-shell :deep(.el-table__fixed-right) {
  background: var(--admin-table-row-bg);
}

.table-shell :deep(.el-table__fixed-right-patch) {
  background: var(--admin-table-header-bg);
}

.table-shell :deep(.el-table__body tr:hover > td.el-table__cell) {
  background: var(--admin-table-row-hover) !important;
}

.table-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.table-meta-inline {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  color: var(--admin-text-muted);
  font-size: 0.92rem;
}

.row-actions {
  display: flex;
  gap: 8px;
}

.table-cell-display {
  width: 100%;
  min-height: 38px;
  padding: 0 8px;
  border: none;
  background: transparent;
  text-align: left;
  display: flex;
  align-items: center;
  cursor: default;
}

.table-cell-display--editable {
  cursor: text;
}

.table-cell-display--editable:hover {
  background: var(--admin-surface-muted);
  border-radius: 10px;
}

.table-cell-value {
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--admin-text);
}

.table-cell-value--empty {
  color: var(--admin-text-faint);
}

.table-cell-editor {
  padding: 4px 8px;
}

.table-cell-input {
  width: 100%;
  min-height: 34px;
  padding: 7px 10px;
  border-radius: 10px;
  border: 1px solid var(--admin-accent);
  background: var(--admin-surface);
  color: var(--admin-text);
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.llm-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 18px;
}

.llm-grid,
.row-form-grid,
.label-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 18px;
}

.label-form-row {
  display: grid;
  grid-template-columns: minmax(180px, 220px) minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
}

.label-form-meta strong,
.label-form-meta small {
  display: block;
}

.label-form-meta strong {
  color: var(--admin-text);
  font-size: 0.92rem;
}

.label-form-meta small {
  margin-top: 4px;
  color: var(--admin-text-muted);
  font-size: 0.78rem;
}

.label-form-row :deep(.el-checkbox) {
  justify-self: flex-start;
}

.span-2 {
  grid-column: 1 / -1;
}

.doc-editor-shell,
.doc-preview {
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-surface);
  overflow: hidden;
}

.doc-view-switch {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: 999px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
}

.doc-view-button {
  min-width: 64px;
  padding: 8px 12px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--admin-text-muted);
  font-weight: 700;
}

.doc-view-button.active {
  background: var(--admin-surface);
  color: var(--admin-text);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
}

.doc-editor-layout {
  display: grid;
  gap: 16px;
}

.doc-editor-layout--split {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}

.doc-editor-layout--edit,
.doc-editor-layout--preview {
  grid-template-columns: 1fr;
}

.doc-panel {
  min-width: 0;
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-surface);
  overflow: hidden;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
}

.doc-panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
}

.doc-panel-head strong,
.doc-panel-head span {
  display: block;
}

.doc-panel-head strong {
  color: var(--admin-text);
  font-size: 0.92rem;
}

.doc-panel-head span {
  color: var(--admin-text-muted);
  font-size: 0.78rem;
}

.doc-editor {
  width: 100%;
  min-height: 66vh;
  max-height: 74vh;
  border: none;
  resize: vertical;
  padding: 20px;
  font: 14px/1.7 'SFMono-Regular', 'Consolas', monospace;
  color: var(--admin-text);
  background: var(--admin-surface);
}

.doc-editor:focus {
  outline: none;
}

.doc-preview {
  padding: 20px;
  max-height: 74vh;
  overflow: auto;
}

.doc-preview--raw {
  background: var(--admin-surface);
}

.doc-preview pre,
.audit-json-grid pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font: 13px/1.7 'SFMono-Regular', 'Consolas', monospace;
  color: var(--admin-text);
}

.doc-rendered {
  font: 15px/1.8 "IBM Plex Sans", "Segoe UI", sans-serif;
  color: var(--admin-text);
}

.doc-rendered :deep(h1),
.doc-rendered :deep(h2),
.doc-rendered :deep(h3),
.doc-rendered :deep(h4) {
  margin: 0 0 0.8em;
  color: var(--admin-text);
  line-height: 1.2;
}

.doc-rendered :deep(h1) {
  font-size: 2rem;
}

.doc-rendered :deep(h2) {
  font-size: 1.5rem;
}

.doc-rendered :deep(h3) {
  font-size: 1.2rem;
}

.doc-rendered :deep(p),
.doc-rendered :deep(ul),
.doc-rendered :deep(ol),
.doc-rendered :deep(blockquote),
.doc-rendered :deep(table) {
  margin: 0 0 1em;
}

.doc-rendered :deep(ul),
.doc-rendered :deep(ol) {
  padding-left: 1.35em;
}

.doc-rendered :deep(a) {
  color: var(--admin-accent);
  text-decoration: none;
}

.doc-rendered :deep(blockquote) {
  padding: 0.85em 1em;
  border-left: 3px solid var(--admin-accent);
  background: var(--admin-surface-muted);
  border-radius: 0 12px 12px 0;
}

.doc-rendered :deep(code) {
  padding: 0.12em 0.4em;
  border-radius: 8px;
  background: var(--admin-surface-muted);
  font-size: 0.92em;
}

.doc-rendered :deep(pre) {
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--admin-surface-muted);
  overflow: auto;
}

.doc-rendered :deep(pre code) {
  padding: 0;
  background: transparent;
}

.doc-rendered :deep(table) {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
}

.doc-rendered :deep(th),
.doc-rendered :deep(td) {
  padding: 10px 12px;
  border: 1px solid var(--admin-border);
  text-align: left;
}

.doc-rendered :deep(th) {
  background: var(--admin-surface-muted);
}

.doc-rendered :deep(img) {
  display: block;
  width: min(100%, 780px);
  max-width: 100%;
  height: auto;
  margin: 1.35rem auto;
  border-radius: 18px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.14);
  cursor: zoom-in;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.doc-rendered :deep(img:hover) {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--admin-accent) 35%, var(--admin-border));
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
}

.audit-detail {
  display: grid;
  gap: 16px;
}

.audit-meta-grid,
.audit-json-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.audit-meta-grid div,
.audit-json-grid > div {
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-surface-muted);
  padding: 14px;
}

.audit-meta-grid strong {
  display: block;
  margin-bottom: 6px;
  color: var(--admin-text-faint);
}

.audit-json-grid h4 {
  margin: 0 0 10px;
  color: var(--admin-text);
}

:deep(.el-button) {
  border-radius: 14px;
  font-weight: 700;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper),
:deep(.el-textarea__inner),
:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  border-radius: 12px;
}

:deep(.el-select__wrapper),
:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  background: var(--admin-surface);
  box-shadow: 0 0 0 1px var(--admin-border) inset;
}

:deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f3f6fb;
  border-radius: 12px;
  overflow: hidden;
}

:root[data-admin-theme='dark'] .workspace-sidebar {
  border-right-color: rgba(148, 163, 184, 0.12);
}

:root[data-admin-theme='dark'] .workspace-topbar {
  border-bottom-color: var(--admin-border-strong);
}

:root[data-admin-theme='dark'] .admin-segmented--topbar {
  background: var(--admin-surface-muted);
}

:root[data-admin-theme='dark'] .toolbar-icon-button:hover {
  background: rgba(148, 163, 184, 0.12);
}

:root[data-admin-theme='dark'] .sidebar-tool-button:hover {
  background: rgba(148, 163, 184, 0.12);
}

:root[data-admin-theme='dark'] .workspace-subtitle-select :deep(.el-select__wrapper),
:root[data-admin-theme='dark'] :deep(.el-select__wrapper),
:root[data-admin-theme='dark'] :deep(.el-input__wrapper),
:root[data-admin-theme='dark'] :deep(.el-textarea__inner) {
  background: var(--admin-surface-soft);
  box-shadow: 0 0 0 1px var(--admin-border-strong) inset;
}

:root[data-admin-theme='dark'] :deep(.el-select__selected-item),
:root[data-admin-theme='dark'] :deep(.el-input__inner),
:root[data-admin-theme='dark'] :deep(.el-textarea__inner) {
  color: var(--admin-text);
}

@keyframes workspace-loading {
  from {
    background-position: 200% 0;
  }
  to {
    background-position: -200% 0;
  }
}

:root[data-admin-theme='dark'] :deep(.el-table) {
  --el-table-header-bg-color: #22314b;
  --el-table-row-hover-bg-color: #22314b;
}

:root[data-admin-theme='dark'] :deep(.el-table th.el-table__cell) {
  background: #22314b;
  color: #dce7f5;
  border-bottom-color: var(--admin-border-strong);
}

:root[data-admin-theme='dark'] :deep(.el-table tr),
:root[data-admin-theme='dark'] :deep(.el-table td.el-table__cell) {
  background: var(--admin-surface);
  color: var(--admin-text);
  border-bottom-color: var(--admin-border);
}

:root[data-admin-theme='dark'] :deep(.el-table__inner-wrapper::before) {
  background-color: var(--admin-border-strong);
}

:deep(.el-pagination.is-background .el-pager li),
:deep(.el-pagination.is-background .btn-next),
:deep(.el-pagination.is-background .btn-prev) {
  border-radius: 10px;
}

@media (max-width: 1380px) {
  .overview-stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .overview-layout,
  .llm-layout {
    grid-template-columns: 1fr;
  }

  .workspace-subtitle-select {
    width: min(100%, 320px);
  }
}

@media (max-width: 1180px) {
  .admin-workspace {
    grid-template-columns: 1fr;
    height: auto;
  }

  .workspace-sidebar {
    min-height: auto;
    grid-template-rows: auto auto auto auto;
  }

  .workspace-main {
    min-height: 0;
  }
}

@media (max-width: 900px) {
  .admin-workspace {
    height: auto;
  }

  .workspace-topbar {
    padding: 18px 18px 16px;
  }

  .workspace-content {
    padding: 18px;
  }

  .workspace-topbar-actions,
  .table-controls-bar,
  .content-card-header,
  .card-actions {
    width: 100%;
  }

  .workspace-subtitle-select,
  .workspace-subtitle-control,
  .topbar-tools {
    width: 100%;
    min-width: 0;
  }

  .overview-stat-grid,
  .summary-grid,
  .table-toolbar,
  .llm-grid,
  .row-form-grid,
  .doc-editor-layout--split,
  .audit-meta-grid,
  .audit-json-grid {
    grid-template-columns: 1fr;
  }

  .label-form-row {
    grid-template-columns: 1fr;
  }
}
</style>
