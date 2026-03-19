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
        <button class="sidebar-primary-item" :class="{ active: activePrimarySection === 'media' }" type="button" @click="openPrimarySection('media')">
          <el-icon class="sidebar-primary-icon"><PictureFilled /></el-icon>
          <div class="sidebar-primary-copy">
            <strong>{{ t('nav.media') }}</strong>
            <small>{{ t('nav.mediaHint', { count: resources?.overview.media_count || 0 }) }}</small>
          </div>
          <b class="sidebar-primary-badge">{{ resources?.overview.media_count || 0 }}</b>
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
              <span>{{ t('overview.mediaLibrary') }}</span>
              <strong>{{ resources?.overview.media_count || 0 }}</strong>
              <small>{{ t('overview.mediaLibraryHint') }}</small>
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
                <div v-if="selectedTableMeta && !selectedTableMeta.read_only" class="summary-strip-actions">
                  <el-button
                    v-if="!tableDeleteMode"
                    size="small"
                    type="danger"
                    plain
                    @click="enterTableDeleteMode"
                  >
                    {{ t('table.deleteSelected') }}
                  </el-button>
                  <template v-else>
                    <span class="summary-strip-selection">{{ t('table.deleteSelectedCount', { count: tableDeleteSelection.length }) }}</span>
                    <el-button
                      size="small"
                      type="danger"
                      :disabled="!tableDeleteSelection.length"
                      @click="confirmDeleteSelectedRows"
                    >
                      {{ t('table.confirmDelete') }}
                    </el-button>
                    <el-button size="small" @click="cancelTableDeleteMode">
                      {{ t('table.cancelDelete') }}
                    </el-button>
                  </template>
                </div>
              </div>
              <div class="table-toolbar">
                <div class="table-search-bar">
                  <el-select
                    v-model="tableQuery.searchColumn"
                    size="small"
                    clearable
                    class="table-search-bar__select"
                    :placeholder="t('table.allColumns')"
                  >
                    <el-option
                      v-for="column in selectedTableMeta?.columns || []"
                      :key="column.name"
                      :label="columnDisplayLabel(column)"
                      :value="column.name"
                    />
                  </el-select>
                  <el-input
                    size="small"
                    v-model="tableQuery.searchText"
                    class="table-search-bar__input"
                    :placeholder="t('table.searchPlaceholder')"
                    clearable
                    @keyup.enter="runTableSearch"
                  />
                  <el-button size="small" type="primary" class="table-search-bar__submit" @click="runTableSearch">{{ t('table.search') }}</el-button>
                </div>
              </div>
              <div class="card-actions card-actions--inline">
                <el-select
                  v-model="tableQuery.pageSize"
                  size="small"
                  class="table-page-size"
                  :placeholder="t('table.pageSize')"
                  @change="handleTableSizeChange"
                >
                  <el-option :value="10" label="10 / page" />
                  <el-option :value="20" label="20 / page" />
                  <el-option :value="50" label="50 / page" />
                  <el-option :value="100" label="100 / page" />
                </el-select>
                <el-button size="small" @click="openColumnLabelDialog">{{ t('table.configureColumns') }}</el-button>
                <el-button size="small" @click="openMediaFieldDialog">{{ t('table.configureMedia') }}</el-button>
                <el-button size="small" @click="openVirtualMediaDialog">{{ t('table.configureSlots') }}</el-button>
                <el-button v-if="selectedTableMeta && !selectedTableMeta.read_only" size="small" type="primary" @click="openCreateRow">{{ t('table.create') }}</el-button>
              </div>
            </div>

            <el-alert
              v-if="tableError"
              type="error"
              :closable="false"
              show-icon
              :title="tableError"
              class="inline-alert"
            />

            <div ref="tableShellRef" class="table-shell">
              <s-table-provider
                :hover="true"
                :bordered="true"
                :locale="adminTableLocale"
                theme-color="#2563eb"
                custom-class="admin-s-table-provider"
              >
                <s-table
                  ref="tableRef"
                  class="workspace-table"
                  :columns="adminTableColumns"
                  :data-source="tableRows"
                  :row-key="adminTableRowKey"
                  :loading="tableLoading"
                  :stripe="true"
                  :wrap-text="true"
                  :bordered="true"
                  :pagination="adminTablePagination"
                  :row-selection="adminTableRowSelection"
                  :scroll-x="adminTableScrollX"
                  @update:pagination="handleSTablePaginationUpdate"
                  @change="handleSTableChange"
                />
              </s-table-provider>
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

        <AdminMediaPanel
          v-else-if="currentView === 'media'"
          ref="mediaPanelRef"
          :csrf-token="csrfToken"
          @changed="handleMediaChanged"
        />

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
                  <h3>{{ t('workflow.title') }}</h3>
                  <p>{{ t('workflow.hint') }}</p>
                </div>
                <el-button type="primary" :loading="workflowSaving" @click="saveWorkflowConfig">{{ t('llm.save') }}</el-button>
              </div>

              <div class="llm-grid">
                <el-form-item :label="t('workflow.enable')">
                  <el-switch v-model="workflowForm.workflow_enable" />
                </el-form-item>

                <el-form-item :label="t('workflow.routerEnable')">
                  <el-switch v-model="workflowForm.conversation_router_enable" />
                </el-form-item>

                <el-form-item :label="t('workflow.routerTimeout')">
                  <el-input-number v-model="workflowForm.conversation_router_timeout" :min="1" :max="60" />
                </el-form-item>

                <el-form-item :label="t('workflow.routerThreshold')">
                  <el-input-number v-model="workflowForm.router_confidence_threshold" :min="0" :max="1" :step="0.05" :precision="2" />
                </el-form-item>

                <el-form-item :label="t('workflow.routerModel')">
                  <el-input v-model="workflowForm.conversation_router_model" :placeholder="t('workflow.routerModelPlaceholder')" />
                </el-form-item>

                <el-form-item :label="t('workflow.judgeEnable')">
                  <el-switch v-model="workflowForm.retrieval_judge_enable" />
                </el-form-item>

                <el-form-item :label="t('workflow.maxRounds')">
                  <el-input-number v-model="workflowForm.max_retrieval_rounds" :min="1" :max="5" />
                </el-form-item>

                <el-form-item :label="t('workflow.stepsPerRound')">
                  <el-input-number v-model="workflowForm.max_tool_steps_per_round" :min="1" :max="8" />
                </el-form-item>

                <el-form-item :label="t('workflow.totalSteps')">
                  <el-input-number v-model="workflowForm.max_total_tool_steps" :min="1" :max="24" />
                </el-form-item>

                <el-form-item :label="t('workflow.judgeThreshold')">
                  <el-input-number v-model="workflowForm.retrieval_judge_threshold" :min="0" :max="1" :step="0.05" :precision="2" />
                </el-form-item>

                <el-form-item :label="t('workflow.judgeModel')">
                  <el-input v-model="workflowForm.retrieval_judge_model" :placeholder="t('workflow.judgeModelPlaceholder')" />
                </el-form-item>

                <el-form-item :label="t('workflow.finalCritic')">
                  <el-switch v-model="workflowForm.final_critic_enable" />
                </el-form-item>

                <el-form-item :label="t('workflow.stopNoEvidence')">
                  <el-switch v-model="workflowForm.stop_on_no_new_evidence" />
                </el-form-item>

                <el-form-item :label="t('workflow.stopRepeatedPlan')">
                  <el-switch v-model="workflowForm.stop_on_repeated_plan" />
                </el-form-item>

                <el-form-item class="span-2" :label="t('workflow.deepenSources')">
                  <div class="workflow-checkboxes">
                    <el-checkbox v-model="workflowForm.allow_table_deepen">{{ t('workflow.allowTable') }}</el-checkbox>
                    <el-checkbox v-model="workflowForm.allow_pubmed_deepen">{{ t('workflow.allowPubmed') }}</el-checkbox>
                    <el-checkbox v-model="workflowForm.allow_doc_deepen">{{ t('workflow.allowDocs') }}</el-checkbox>
                  </div>
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
      v-model="tableImageDialogVisible"
      :title="t('tableImage.title')"
      width="min(1040px, 94vw)"
      destroy-on-close
      @closed="closeTableImageDialog"
    >
      <div class="table-image-workbench">
        <div class="table-image-workbench__preview-shell">
          <img
            v-if="tableImagePreviewUrl"
            :src="tableImagePreviewUrl"
            :alt="columnDisplayLabel(tableImageColumn || 'image')"
            class="table-image-workbench__preview"
          />
          <div v-else class="table-image-workbench__empty">
            {{ t('tableImage.empty') }}
          </div>
        </div>
        <div class="table-image-workbench__side">
          <div class="table-image-workbench__meta">
            <article>
              <span>{{ t('tableImage.field') }}</span>
              <strong>{{ columnDisplayLabel(tableImageColumn || '') || '—' }}</strong>
            </article>
            <article>
              <span>{{ t('tableImage.rawValue') }}</span>
              <strong>{{ tableImageRawValue || '—' }}</strong>
            </article>
            <article>
              <span>{{ t('tableImage.assetTitle') }}</span>
              <strong>{{ tableImageAsset?.title || tableImageAsset?.object_key || '—' }}</strong>
            </article>
          </div>
          <div class="table-image-workbench__actions">
            <el-button class="table-image-workbench__action-button" :disabled="!tableImagePreviewUrl" @click="downloadTableImage">
              {{ t('tableImage.download') }}
            </el-button>
            <el-button
              class="table-image-workbench__action-button"
              type="primary"
              plain
              :disabled="!canPickMediaAssetForColumn(tableImageColumn)"
              :loading="tableImageActionLoading"
              @click="openTableImageReplacementPicker"
            >
              {{ t('tableImage.replace') }}
            </el-button>
            <el-button
              class="table-image-workbench__action-button"
              plain
              :disabled="!tableImageRow || !tableImageColumn || tableImageActionLoading"
              @click="removeTableImage"
            >
              {{ t('tableImage.remove') }}
            </el-button>
            <el-button
              class="table-image-workbench__action-button"
              type="danger"
              plain
              :disabled="!tableImageAsset?.id || tableImageActionLoading"
              :loading="tableImageActionLoading"
              @click="deleteTableImageAsset"
            >
              {{ t('tableImage.delete') }}
            </el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="tableImageDialogVisible = false">{{ t('dialog.close') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="textCellDialogVisible"
      :title="t('tableTextEditor.title')"
      width="min(760px, 94vw)"
      destroy-on-close
      @closed="closeTextCellDialog"
    >
      <div class="text-cell-editor-dialog">
        <div class="text-cell-editor-dialog__meta">
          <article>
            <span>{{ t('tableTextEditor.field') }}</span>
            <strong>{{ columnDisplayLabel(textCellDialogColumn || '') || '—' }}</strong>
          </article>
        </div>
        <el-input
          ref="textCellDialogInputRef"
          v-model="textCellDialogDraft"
          type="textarea"
          :autosize="{ minRows: 10, maxRows: 20 }"
          class="text-cell-editor-dialog__input"
          @keydown.esc.stop.prevent="closeTextCellDialog"
          @keydown.meta.enter.stop.prevent="saveTextCellDialog"
          @keydown.ctrl.enter.stop.prevent="saveTextCellDialog"
        />
      </div>
      <template #footer>
        <el-button @click="closeTextCellDialog">{{ t('dialog.cancel') }}</el-button>
        <el-button type="primary" :loading="textCellDialogSaving" @click="saveTextCellDialog">{{ t('dialog.save') }}</el-button>
      </template>
    </el-dialog>

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
          :class="{ 'row-form-item--wide': isImageEditorColumn(column) }"
        >
          <template v-if="isImageEditorColumn(column)">
            <div class="row-media-field">
              <div class="row-media-preview-shell">
                <img
                  v-if="rowFieldPreviewUrl(column.name)"
                  :src="rowFieldPreviewUrl(column.name)"
                  :alt="columnDisplayLabel(column)"
                  class="row-media-preview-image"
                />
                <div v-else class="row-media-preview-empty">
                  {{ t('rowMedia.empty') }}
                </div>
              </div>
              <div class="row-media-actions">
                <el-button
                  type="primary"
                  plain
                  :disabled="!canPickMediaAssetForColumn(column.name)"
                  @click="openFieldMediaPicker(column.name)"
                >
                  {{ t('rowMedia.pick') }}
                </el-button>
                <el-button plain @click="clearFieldMedia(column.name)">
                  {{ t('rowMedia.clear') }}
                </el-button>
                <el-button text @click="toggleRawField(column.name)">
                  {{ isRawFieldVisible(column.name) ? t('rowMedia.hideRaw') : t('rowMedia.showRaw') }}
                </el-button>
              </div>
              <div class="row-media-meta">
                <span>{{ t('rowMedia.currentValue') }}</span>
                <strong>{{ rowFieldRawValue(column.name) || '—' }}</strong>
              </div>
              <el-input
                v-if="isRawFieldVisible(column.name)"
                v-model="rowForm[column.name]"
                :type="isTextareaColumn(column.type) ? 'textarea' : 'text'"
                :autosize="isTextareaColumn(column.type) ? { minRows: 2, maxRows: 6 } : undefined"
              />
            </div>
          </template>
          <el-input
            v-else
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

    <el-dialog
      v-model="fieldMediaPickerVisible"
      :title="t('rowMedia.pickerTitle')"
      width="min(980px, 94vw)"
      destroy-on-close
    >
      <div class="row-media-picker">
        <p class="row-media-picker__hint">{{ t('rowMedia.pickerHint') }}</p>
        <div class="row-media-picker__toolbar">
          <input
            ref="fieldMediaUploadInputRef"
            class="row-media-picker__upload-input"
            type="file"
            accept="image/*"
            @change="handleFieldMediaUploadChange"
          />
          <el-input
            v-model="fieldMediaQuery.search"
            :placeholder="t('rowMedia.pickerSearch')"
            @keyup.enter="loadFieldMediaLibrary"
          />
          <div class="row-media-picker__toolbar-actions">
            <el-checkbox v-model="fieldMediaQuery.onlyUnbound" @change="handleFieldMediaBindingFilterChange">
              {{ t('rowMedia.onlyUnbound') }}
            </el-checkbox>
            <el-button :loading="fieldMediaUploading" @click="fieldMediaUploadInputRef?.click()">
              {{ t('rowMedia.quickUpload') }}
            </el-button>
            <el-button type="primary" :loading="fieldMediaLibraryLoading" @click="loadFieldMediaLibrary">
              {{ t('media.search') }}
            </el-button>
          </div>
        </div>
        <div v-if="fieldMediaAssets.length" class="row-media-picker-grid">
          <button
            v-for="asset in fieldMediaAssets"
            :key="asset.id"
            type="button"
            class="row-media-picker-card"
            @click="chooseFieldMediaAsset(asset)"
          >
            <div class="row-media-picker-card__thumb">
              <img :src="asset.public_url" :alt="asset.alt_text || asset.title || asset.original_filename" />
            </div>
            <div class="row-media-picker-card__copy">
              <strong>{{ asset.title || asset.original_filename }}</strong>
              <span>{{ extractLegacyPictureidFromAsset(asset) || asset.original_filename }}</span>
            </div>
            <span class="row-media-picker-card__action">{{ t('rowMedia.pickAction') }}</span>
          </button>
        </div>
        <div v-else class="row-media-picker-empty">
          {{ t('rowMedia.libraryEmpty') }}
        </div>
      </div>
      <template #footer>
        <el-button @click="fieldMediaPickerVisible = false">{{ t('dialog.cancel') }}</el-button>
      </template>
    </el-dialog>

    <AdminTableMediaFieldsDialog
      v-model="mediaFieldDialogVisible"
      :csrf-token="csrfToken"
      :table-meta="selectedTableMeta"
      :sample-row="tableRows[0] || null"
      @saved="handleMediaFieldsSaved"
    />

    <AdminVirtualMediaFieldsDialog
      v-model="virtualMediaDialogVisible"
      :csrf-token="csrfToken"
      :table-meta="selectedTableMeta"
      @saved="handleVirtualMediaFieldsSaved"
    />

    <AdminRecordMediaSlotsDialog
      v-model="recordMediaDialogVisible"
      :csrf-token="csrfToken"
      :table-meta="selectedTableMeta"
      :row="selectedRecordMediaRow"
      @changed="handleRecordMediaChanged"
    />

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
import { computed, h, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue';
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
  ElSelect,
  ElTooltip
} from 'element-plus';
import type {
  STableColumnsType,
  STableInstance,
  STableLocale,
  STablePaginationConfig,
  STableRowSelection
} from '@shene/table';
import enTableLocale from '@shene/table/dist/locale/en';
import zhTableLocale from '@shene/table/dist/locale/zh_CN';
import {
  DataAnalysis,
  Document,
  Grid,
  House,
  Monitor,
  Notebook,
  PictureFilled,
  RefreshRight,
  SwitchButton
} from '@element-plus/icons-vue';

import {
  fetchAdminAIWorkflowSettings,
  fetchAdminMediaList,
  uploadAdminMedia,
  type AdminVirtualMediaField,
  createAdminDoc,
  createAdminTableRecord,
  deleteAdminMedia,
  deleteAdminDoc,
  deleteAdminTableRecord,
  fetchAdminAuditLogs,
  fetchAdminDoc,
  fetchAdminLLMSettings,
  fetchAdminResources,
  fetchAdminSession,
  fetchAdminTableMeta,
  fetchAdminTableRows,
  saveAdminAIWorkflowSettings,
  saveAdminTableLabels,
  saveAdminTableVisibleColumns,
  saveAdminDoc,
  saveAdminLLMSettings,
  updateAdminTableRecord,
  type AdminAIWorkflowSettings,
  type AdminAuditRow,
  type AdminDocDetail,
  type AdminLLMSettings,
  type AdminMediaAsset,
  type AdminTableMediaFieldConfig,
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
import {
  getRowBoundFieldMediaEntry,
  getRowBoundFieldMediaUrl,
  resolveMediaSource,
} from '@/utils/tableMedia';
import { useMarkdown } from '@/utils/useMarkdown';
import AdminMediaPanel from './AdminMediaPanel.vue';
import AdminRecordMediaSlotsDialog from './AdminRecordMediaSlotsDialog.vue';
import AdminTableMediaFieldsDialog from './AdminTableMediaFieldsDialog.vue';
import AdminVirtualMediaFieldsDialog from './AdminVirtualMediaFieldsDialog.vue';

const route = useRoute();
const router = useRouter();
const { locale, setLocale, toggleTheme, themeLabel, themeMode, t } = useAdminI18n();
const { renderMarkdown } = useMarkdown();

const adminUser = ref<AdminUser | null>(null);
const csrfToken = ref('');
const resources = ref<AdminResourcesResponse | null>(null);
const auditRows = ref<AdminAuditRow[]>([]);
const llmSaving = ref(false);
const workflowSaving = ref(false);
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
const mediaPanelRef = ref<{ refresh: () => Promise<void> } | null>(null);
const routeSwitching = ref(false);
let routeSwitchToken = 0;

const rowDialogVisible = ref(false);
const rowDialogMode = ref<'create' | 'edit'>('create');
const rowSaving = ref(false);
const rowForm = reactive<Record<string, string>>({});
const originalRow = ref<Record<string, any> | null>(null);
const tableShellRef = ref<HTMLElement | null>(null);
const tableImageDialogVisible = ref(false);
const tableImageActionLoading = ref(false);
const tableImageRow = ref<Record<string, any> | null>(null);
const tableImageColumn = ref('');
const fieldMediaPickerVisible = ref(false);
const fieldMediaPickerMode = ref<'rowForm' | 'tableCell'>('rowForm');
const fieldMediaPickerColumn = ref('');
const fieldMediaLibraryLoading = ref(false);
const fieldMediaUploading = ref(false);
const fieldMediaUploadInputRef = ref<HTMLInputElement | null>(null);
const fieldMediaAssets = ref<AdminMediaAsset[]>([]);
const fieldMediaQuery = reactive({
  search: '',
  onlyUnbound: false,
  page: 1,
  pageSize: 24,
});
const rowRawFieldVisibility = reactive<Record<string, boolean>>({});
const columnLabelDialogVisible = ref(false);
const columnLabelSaving = ref(false);
const mediaFieldDialogVisible = ref(false);
const virtualMediaDialogVisible = ref(false);
const recordMediaDialogVisible = ref(false);
const columnLabelForm = reactive<Record<string, string>>({});
const defaultVisibleColumnsForm = ref<string[]>([]);
const selectedRecordMediaRow = ref<Record<string, any> | null>(null);
const inlineEditRow = ref<Record<string, any> | null>(null);
const inlineEditColumn = ref('');
const inlineEditOriginalRow = ref<Record<string, any> | null>(null);
const inlineEditDraft = ref('');
const inlineEditSaving = ref(false);
const inlineEditInputRef = ref<any>(null);
const inlineEditOverlayRect = reactive({
  top: 0,
  left: 0,
  width: 0,
  minHeight: 0,
});
const textCellDialogVisible = ref(false);
const textCellDialogRow = ref<Record<string, any> | null>(null);
const textCellDialogColumn = ref('');
const textCellDialogOriginalRow = ref<Record<string, any> | null>(null);
const textCellDialogDraft = ref('');
const textCellDialogSaving = ref(false);
const textCellDialogInputRef = ref<any>(null);
const tableRef = ref<STableInstance | null>(null);
const tableDeleteMode = ref(false);
const tableDeleteSelectionKeys = ref<Array<string | number>>([]);
const tableDeleteSelection = ref<Record<string, any>[]>([]);
let tableCellOriginalRows = new WeakMap<Record<string, any>, Map<string, Record<string, any>>>();
let tableCellSavingStates = new WeakMap<Record<string, any>, Set<string>>();

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
const workflowForm = reactive<AdminAIWorkflowSettings>({
  workflow_enable: true,
  conversation_router_enable: true,
  conversation_router_model: '',
  conversation_router_timeout: 15,
  router_confidence_threshold: 0.7,
  max_retrieval_rounds: 2,
  max_tool_steps_per_round: 4,
  max_total_tool_steps: 12,
  retrieval_judge_enable: true,
  retrieval_judge_model: '',
  retrieval_judge_threshold: 0.8,
  stop_on_no_new_evidence: true,
  stop_on_repeated_plan: true,
  allow_pubmed_deepen: true,
  allow_table_deepen: true,
  allow_doc_deepen: true,
  final_critic_enable: true
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
const pageBusy = computed(() => resourcesLoading.value || tableLoading.value || docLoading.value || llmSaving.value || workflowSaving.value);
const editableColumns = computed(() => (selectedTableMeta.value?.columns || []).filter((column) => column.name !== 'Index'));
const selectedDocIsMarkdown = computed(() => isMarkdownDoc(selectedDoc.value));
const canInlineEditTable = computed(() => Boolean(selectedTableMeta.value && !selectedTableMeta.value.read_only));
const selectedTableHasVirtualMediaFields = computed(() => Boolean(selectedTableMeta.value?.virtual_media_fields?.length));
const tableImagePreviewUrl = computed(() => {
  if (!tableImageRow.value || !tableImageColumn.value) return '';
  return rowCellPreviewUrl(tableImageRow.value, tableImageColumn.value);
});
const tableImageRawValue = computed(() => {
  if (!tableImageRow.value || !tableImageColumn.value) return '';
  return normalizeFieldName(tableImageRow.value[tableImageColumn.value]);
});
const tableImageBoundEntry = computed(() => {
  if (!tableImageRow.value || !tableImageColumn.value) return null;
  return getRowBoundFieldMediaEntry(tableImageRow.value, tableImageColumn.value);
});
const tableImageAsset = computed(() => tableImageBoundEntry.value?.asset || null);
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
const selectedTableIdentityColumns = computed(() => {
  if (!selectedTableMeta.value) return [];
  const availableColumns = new Set((selectedTableMeta.value.columns || []).map((column) => column.name));
  const orderedCandidates = [
    ...(selectedTableMeta.value.primary_columns || []),
    'ENSURE_ID',
    'ensure_id',
    'id',
    'ID',
    'Index',
    'PMID',
    'pmid'
  ];
  return orderedCandidates.filter((columnName, index, arr) =>
    availableColumns.has(columnName) && arr.indexOf(columnName) === index
  );
});
const adminTableLocale = computed<STableLocale>(() => ({
  ...(locale.value === 'zh-CN' ? zhTableLocale : enTableLocale),
  emptyText: t('table.noRows')
}));
const adminTablePagination = computed<STablePaginationConfig>(() => ({
  current: tablePagination.page,
  pageSize: tableQuery.pageSize,
  total: tablePagination.total,
  showQuickJumper: true,
  showSizeChanger: false,
  pageSizeOptions: ['10', '20', '50', '100'],
  position: ['bottomRight']
}));
const adminTableScrollX = computed(() => {
  const baseColumns = (selectedTableMeta.value?.columns || []).reduce((total, column) => total + columnWidth(column), 0);
  const deleteColumn = tableDeleteMode.value ? 52 : 0;
  const slotColumn = selectedTableHasVirtualMediaFields.value ? 110 : 0;
  return Math.max(baseColumns + deleteColumn + slotColumn + 48, 960);
});
const adminTableRowSelection = computed<STableRowSelection<Record<string, any>> | undefined>(() => {
  if (!tableDeleteMode.value) return undefined;
  return {
    type: 'checkbox',
    fixed: true,
    columnWidth: 52,
    selectedRowKeys: tableDeleteSelectionKeys.value,
    onChange: handleTableSelectionChange
  };
});
const adminTableColumns = computed<STableColumnsType<Record<string, any>>>(() => {
  const baseColumns = (selectedTableMeta.value?.columns || []).map((column) => ({
    title: columnDisplayLabel(column),
    dataIndex: column.name,
    key: column.name,
    width: columnWidth(column),
    sorter: true,
    sortOrder: tableQuery.sortBy === column.name ? tableSortOrderForSTable(tableQuery.sortOrder) : null,
    wrapText: true,
    autoHeight: !isImageDisplayColumn(column.name),
    customRender: ({ record }: { record: Record<string, any> }) => renderAdminTableCell(record, column.name),
  }));

  if (selectedTableHasVirtualMediaFields.value) {
    baseColumns.push({
      title: t('table.images'),
      dataIndex: '__record_media_slots__',
      key: '__record_media_slots__',
      width: 110,
      fixed: 'right',
      customRender: ({ record }: { record: Record<string, any> }) => renderRecordMediaAction(record)
    });
  }

  return baseColumns;
});
const activeSectionEyebrow = computed(() => {
  if (currentView.value === 'table') return t('section.eyebrowTable');
  if (currentView.value === 'doc') return t('section.eyebrowDoc');
  if (currentView.value === 'media') return t('section.eyebrowMedia');
  if (currentView.value === 'llm') return t('section.eyebrowLlm');
  if (currentView.value === 'audit') return t('section.eyebrowAudit');
  return t('section.eyebrowOverview');
});
const activeSectionTitle = computed(() => {
  if (currentView.value === 'table') return selectedTableMeta.value?.label || currentResource.value || t('section.titleTableFallback');
  if (currentView.value === 'doc') return selectedDoc.value?.filename || currentResource.value || t('section.titleDocFallback');
  if (currentView.value === 'media') return t('section.titleMedia');
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
  if (currentView.value === 'media') {
    return t('section.descMedia');
  }
  if (currentView.value === 'llm') {
    return t('section.descLlm');
  }
  if (currentView.value === 'audit') {
    return t('section.descAudit');
  }
  return t('section.descOverview');
});
const inlineEditStyle = computed(() => {
  const viewportWidth = typeof window === 'undefined' ? 1440 : window.innerWidth;
  const desiredWidth = Math.max(
    inlineEditOverlayRect.width + 56,
    Math.min(720, Math.max(320, inlineEditDraft.value.length * 11))
  );
  const maxWidth = Math.max(280, viewportWidth - 32);
  const width = Math.min(desiredWidth, maxWidth);
  const left = Math.min(
    inlineEditOverlayRect.left,
    Math.max(16, viewportWidth - width - 16)
  );
  return {
    top: `${inlineEditOverlayRect.top}px`,
    left: `${Math.max(16, left)}px`,
    width: `${width}px`,
    minHeight: `${Math.max(46, inlineEditOverlayRect.minHeight)}px`,
  };
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
  if (currentView.value === 'media') {
    return [
      { key: 'assets', label: t('top.assets'), value: String(resources.value?.overview.media_count || 0) },
      { key: 'docs', label: t('overview.docsLibrary'), value: String(resources.value?.overview.doc_count || 0) },
      { key: 'rows', label: t('overview.totalRecords'), value: formatNumber(resources.value?.overview.total_rows || 0) }
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
  if (currentView.value === 'media') return 'media';
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

function openPrimarySection(section: 'overview' | 'tables' | 'docs' | 'media' | 'llm' | 'audit') {
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
  if (section === 'media') {
    navigate('media');
    return;
  }
  if (section === 'llm') {
    navigate('llm');
    return;
  }
  navigate('audit');
}

async function handleMediaChanged() {
  await loadResources();
  await loadAuditLogs();
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
  const name = typeof columnOrName === 'string' ? columnOrName : columnOrName.name;
  if (isImageDisplayColumn(name)) return 188;
  const label = columnDisplayLabel(columnOrName);
  return Math.min(Math.max(String(label || '').length * 14, 132), 280);
}

function tableSortOrderForSTable(sortOrder: string) {
  if (sortOrder === 'desc') return 'descend';
  if (sortOrder === 'asc') return 'ascend';
  return null;
}

function buildAdminTableRowIdentity(row: Record<string, any>) {
  const parts = selectedTableIdentityColumns.value
    .map((columnName) => normalizeFieldName(row?.[columnName]))
    .filter(Boolean);
  if (parts.length) {
    return `${currentResource.value}::${parts.join('||')}`;
  }
  const fallbackIndex = tableRows.value.indexOf(row);
  if (fallbackIndex >= 0) {
    return `${currentResource.value}::fallback::${fallbackIndex}`;
  }
  return `${currentResource.value}::json::${JSON.stringify(row || {})}`;
}

function adminTableRowKey(row: Record<string, any>) {
  return buildAdminTableRowIdentity(row);
}

function trackTableCellOriginalRow(row: Record<string, any>, columnName: string) {
  const normalizedColumn = normalizeFieldName(columnName);
  let rowSnapshots = tableCellOriginalRows.get(row);
  if (!rowSnapshots) {
    rowSnapshots = new Map<string, Record<string, any>>();
    tableCellOriginalRows.set(row, rowSnapshots);
  }
  if (!rowSnapshots.has(normalizedColumn)) {
    rowSnapshots.set(normalizedColumn, { ...row });
  }
}

function getTrackedTableCellOriginalRow(row: Record<string, any>, columnName: string) {
  return tableCellOriginalRows.get(row)?.get(normalizeFieldName(columnName)) || null;
}

function isTableCellSaving(row: Record<string, any>, columnName: string) {
  return Boolean(tableCellSavingStates.get(row)?.has(normalizeFieldName(columnName)));
}

function setTableCellSaving(row: Record<string, any>, columnName: string, saving: boolean) {
  const normalizedColumn = normalizeFieldName(columnName);
  let rowSavingColumns = tableCellSavingStates.get(row);

  if (saving) {
    if (!rowSavingColumns) {
      rowSavingColumns = new Set<string>();
      tableCellSavingStates.set(row, rowSavingColumns);
    }
    rowSavingColumns.add(normalizedColumn);
    return;
  }

  if (!rowSavingColumns) return;
  rowSavingColumns.delete(normalizedColumn);
  if (!rowSavingColumns.size) {
    tableCellSavingStates.delete(row);
  }
}

function clearTrackedTableCellOriginalRow(row: Record<string, any>, columnName: string) {
  const normalizedColumn = normalizeFieldName(columnName);
  const rowSnapshots = tableCellOriginalRows.get(row);
  if (!rowSnapshots) return;
  rowSnapshots.delete(normalizedColumn);
}

function clearTableEditTracking() {
  tableCellOriginalRows = new WeakMap<Record<string, any>, Map<string, Record<string, any>>>();
  tableCellSavingStates = new WeakMap<Record<string, any>, Set<string>>();
}

function renderTableTextValue(row: Record<string, any>, columnName: string, preserveLineBreaks = false) {
  const value = displayCellValue(row[columnName]);
  return h(
    'span',
    {
      class: ['table-cell-value', { 'table-cell-value--empty': value === '—' }],
      title: value,
      style: preserveLineBreaks ? { whiteSpace: 'pre-wrap' } : undefined,
    },
    value
  );
}

function renderTableImageCell(row: Record<string, any>, columnName: string) {
  const previewUrl = rowCellPreviewUrl(row, columnName);
  const value = displayCellValue(row[columnName]);
  return h('div', { class: 'table-cell-media' }, [
    previewUrl
      ? h(
        'button',
        {
          class: 'table-cell-media__thumb',
          type: 'button',
          onClick: (event: MouseEvent) => {
            event.stopPropagation();
            openTableImageDialog(row, columnName);
          }
        },
        [
          h('img', {
            src: previewUrl,
            alt: columnDisplayLabel(columnName),
            class: 'table-cell-media__image',
            loading: 'lazy',
            decoding: 'async',
          })
        ]
      )
      : h(
        'button',
        {
          class: 'table-cell-media__empty table-cell-media__empty-button',
          type: 'button',
          title: columnDisplayLabel(columnName),
          onClick: (event: MouseEvent) => {
            event.stopPropagation();
            openTableImageDialog(row, columnName);
          }
        },
        '—'
      ),
    h('span', { class: 'table-cell-media__value', title: value }, value)
  ]);
}

function renderTableTextDialogTrigger(row: Record<string, any>, columnName: string) {
  return h(
    'button',
    {
      class: [
        'table-cell-display',
        'table-cell-display--editable',
        'table-cell-display--dialog',
        { 'table-cell-display--editing': isInlineEditing(row, columnName) }
      ],
      type: 'button',
      onDblclick: (event: MouseEvent) => {
        event.stopPropagation();
        void openTextCellDialog(row, columnName);
      }
    },
    [renderTableTextValue(row, columnName, true)]
  );
}

function renderTableInlineEditTrigger(row: Record<string, any>, columnName: string) {
  if (isInlineEditing(row, columnName)) {
    return h(
      'div',
      {
        class: 'table-inline-editor table-inline-editor--embedded',
        onMousedown: (event: MouseEvent) => event.stopPropagation(),
        onClick: (event: MouseEvent) => event.stopPropagation(),
      },
      [
        h(ElInput, {
          ref: inlineEditInputRef,
          modelValue: inlineEditDraft.value,
          'onUpdate:modelValue': (value: string) => {
            inlineEditDraft.value = value;
          },
          type: 'text',
          class: 'table-inline-editor__input',
          onKeydown: (event: KeyboardEvent) => {
            if (event.key === 'Enter') {
              handleInlineEditEnter(event, columnName);
              return;
            }
            if (event.key === 'Escape') {
              event.preventDefault();
              cancelInlineEdit();
            }
          }
        })
      ]
    );
  }

  return h(
    'button',
    {
      class: [
        'table-cell-display',
        'table-cell-display--editable',
        { 'table-cell-display--editing': isInlineEditing(row, columnName) }
      ],
      type: 'button',
      onDblclick: (event: MouseEvent) => {
        event.stopPropagation();
        void beginInlineEdit(row, columnName, event);
      }
    },
    [renderTableTextValue(row, columnName)]
  );
}

function renderRecordMediaAction(row: Record<string, any>) {
  return h('div', { class: 'row-actions' }, [
    h(
      ElButton,
      {
        size: 'small',
        plain: true,
        disabled: tableDeleteMode.value,
        onClick: (event: MouseEvent) => {
          event.stopPropagation();
          openRecordMediaSlots(row);
        }
      },
      { default: () => t('table.images') }
    )
  ]);
}

function renderAdminTableCell(row: Record<string, any>, columnName: string) {
  if (isImageDisplayColumn(columnName)) {
    return renderTableImageCell(row, columnName);
  }
  if (canInlineEditColumn(columnName) && inlineEditUsesTextarea(columnName, row)) {
    return renderTableTextDialogTrigger(row, columnName);
  }
  if (canInlineEditColumn(columnName)) {
    return renderTableInlineEditTrigger(row, columnName);
  }
  if (inlineEditUsesTextarea(columnName, row)) {
    return renderTableTextValue(row, columnName, true);
  }
  return renderTableTextValue(row, columnName);
}

function normalizeFieldName(value: unknown) {
  return String(value || '').trim();
}

function getSelectedTableMediaConfig(columnName: string): AdminTableMediaFieldConfig {
  const fieldName = normalizeFieldName(columnName);
  if (!fieldName) return {};
  return selectedTableMeta.value?.media_fields?.[fieldName] || {};
}

function isLegacyPictureidColumn(columnName: string) {
  return normalizeFieldName(columnName).toLowerCase() === 'pictureid';
}

function isImageEditorColumn(column: { name: string }) {
  if (isLegacyPictureidColumn(column.name)) return true;
  return getSelectedTableMediaConfig(column.name).renderer === 'image';
}

function isImageDisplayColumn(columnName: string) {
  if (isLegacyPictureidColumn(columnName)) return true;
  return getSelectedTableMediaConfig(columnName).renderer === 'image';
}

function canPickMediaAssetForColumn(columnName: string) {
  if (isLegacyPictureidColumn(columnName)) return true;
  const config = getSelectedTableMediaConfig(columnName);
  return (config.renderer === 'image' || config.renderer === 'url' || config.renderer === 'file')
    && config.source === 'direct';
}

function rowFieldRawValue(columnName: string) {
  return normalizeFieldName(rowForm[columnName]);
}

function rowFieldPreviewUrl(columnName: string) {
  if (!selectedTableMeta.value) return '';
  const raw = rowFieldRawValue(columnName);
  if (raw) {
    const resolved = resolveMediaSource(
      selectedTableMeta.value.name,
      columnName,
      raw,
      selectedTableMeta.value.media_fields || {}
    );
    if (resolved) return resolved;
  }
  if (originalRow.value) {
    return getRowBoundFieldMediaUrl(originalRow.value, columnName);
  }
  return '';
}

function resetRowMediaState() {
  fieldMediaPickerVisible.value = false;
  fieldMediaPickerMode.value = 'rowForm';
  fieldMediaPickerColumn.value = '';
  fieldMediaAssets.value = [];
  fieldMediaQuery.search = '';
  fieldMediaQuery.onlyUnbound = false;
  fieldMediaQuery.page = 1;
  Object.keys(rowRawFieldVisibility).forEach((key) => delete rowRawFieldVisibility[key]);
}

function toggleRawField(columnName: string) {
  const fieldName = normalizeFieldName(columnName);
  rowRawFieldVisibility[fieldName] = !rowRawFieldVisibility[fieldName];
}

function isRawFieldVisible(columnName: string) {
  return Boolean(rowRawFieldVisibility[normalizeFieldName(columnName)]);
}

function extractLegacyPictureidFromAsset(asset: AdminMediaAsset) {
  const candidates = [asset.object_key, asset.original_filename, asset.title]
    .map((value) => normalizeFieldName(value))
    .filter(Boolean);
  for (const candidate of candidates) {
    const tail = candidate.split('/').pop() || candidate;
    const stripped = tail.replace(/\.[A-Za-z0-9]+$/, '').trim();
    if (stripped) return decodeURIComponent(stripped);
  }
  return '';
}

function mapAssetValueForColumn(asset: AdminMediaAsset, columnName: string) {
  if (isLegacyPictureidColumn(columnName)) {
    return extractLegacyPictureidFromAsset(asset);
  }
  const config = getSelectedTableMediaConfig(columnName);
  if ((config.renderer === 'image' || config.renderer === 'url' || config.renderer === 'file') && config.source === 'direct') {
    return normalizeFieldName(asset.public_url);
  }
  return '';
}

async function loadFieldMediaLibrary() {
  if (!fieldMediaPickerColumn.value) return;
  fieldMediaLibraryLoading.value = true;
  try {
    const sourceType = isLegacyPictureidColumn(fieldMediaPickerColumn.value) ? 'legacy_pictureid' : undefined;
    const result = await fetchAdminMediaList({
      search: fieldMediaQuery.search || undefined,
      source_type: sourceType,
      binding_status: fieldMediaQuery.onlyUnbound ? 'unbound' : undefined,
      page: fieldMediaQuery.page,
      page_size: fieldMediaQuery.pageSize,
    });
    fieldMediaAssets.value = Array.isArray(result.items) ? result.items : [];
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowMediaLoadFailed'));
  } finally {
    fieldMediaLibraryLoading.value = false;
  }
}

function handleFieldMediaBindingFilterChange() {
  fieldMediaQuery.page = 1;
  void loadFieldMediaLibrary();
}

function suggestedFieldMediaUploadTitle() {
  const columnName = normalizeFieldName(fieldMediaPickerColumn.value);
  if (!columnName) return '';
  if (fieldMediaPickerMode.value === 'tableCell' && tableImageRow.value) {
    const cellValue = normalizeFieldName(tableImageRow.value[columnName]);
    if (cellValue) return cellValue;
  }
  const rawValue = normalizeFieldName(rowForm[columnName]);
  if (rawValue) return rawValue;
  return normalizeFieldName(fieldMediaQuery.search);
}

async function handleFieldMediaUploadChange(event: Event) {
  const input = event.target as HTMLInputElement | null;
  const file = input?.files?.[0] || null;
  if (!file || !fieldMediaPickerColumn.value) return;
  fieldMediaUploading.value = true;
  try {
    const sourceType = isLegacyPictureidColumn(fieldMediaPickerColumn.value) ? 'legacy_pictureid' : 'library';
    const suggestedTitle = suggestedFieldMediaUploadTitle();
    const result = await uploadAdminMedia(file, {
      csrfToken: csrfToken.value,
      title: suggestedTitle || undefined,
      source_type: sourceType,
    });
    ElMessage.success(result.deduped ? t('msg.mediaDeduped') : t('msg.mediaUploaded'));
    await loadFieldMediaLibrary();
    if (result.asset) {
      await chooseFieldMediaAsset(result.asset);
    }
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.mediaUploadFailed'));
  } finally {
    fieldMediaUploading.value = false;
    if (input) input.value = '';
  }
}

async function openFieldMediaPicker(columnName: string) {
  fieldMediaPickerMode.value = 'rowForm';
  fieldMediaPickerColumn.value = normalizeFieldName(columnName);
  fieldMediaQuery.search = '';
  fieldMediaQuery.onlyUnbound = false;
  fieldMediaQuery.page = 1;
  fieldMediaPickerVisible.value = true;
  await loadFieldMediaLibrary();
}

async function chooseFieldMediaAsset(asset: AdminMediaAsset) {
  if (!fieldMediaPickerColumn.value) return;
  const nextValue = mapAssetValueForColumn(asset, fieldMediaPickerColumn.value);
  if (!nextValue) {
    ElMessage.error(t('msg.rowMediaLoadFailed'));
    return;
  }
  if (fieldMediaPickerMode.value === 'tableCell') {
    await replaceTableImage(asset, nextValue);
    return;
  }
  rowForm[fieldMediaPickerColumn.value] = nextValue;
  fieldMediaPickerVisible.value = false;
}

function clearFieldMedia(columnName: string) {
  rowForm[normalizeFieldName(columnName)] = '';
}

function inlineEditUsesTextarea(columnName: string, row?: Record<string, any> | null) {
  const rawValue = row?.[columnName];
  const normalized = rawValue == null ? '' : String(rawValue);
  if (!normalized) return false;
  if (normalized.includes('\n')) return true;
  if (normalized.length >= 48) return true;
  return /[_/\\-]/.test(normalized) && normalized.length >= 28;
}

function displayCellValue(value: any) {
  if (value == null || value === '') return '—';
  return String(value);
}

function rowCellPreviewUrl(row: Record<string, any>, columnName: string) {
  if (!selectedTableMeta.value) return '';
  const bound = getRowBoundFieldMediaUrl(row, columnName);
  if (bound) return bound;
  return resolveMediaSource(
    selectedTableMeta.value.name,
    columnName,
    row?.[columnName],
    selectedTableMeta.value.media_fields || {}
  );
}

function canInlineEditColumn(columnName: string) {
  if (!canInlineEditTable.value || !selectedTableMeta.value) return false;
  if (tableDeleteMode.value) return false;
  if (columnName === 'Index') return false;
  if (isImageDisplayColumn(columnName)) return false;
  return !selectedTableMeta.value.primary_columns.includes(columnName);
}

function openTableImageDialog(row: Record<string, any>, columnName: string) {
  tableImageRow.value = row;
  tableImageColumn.value = normalizeFieldName(columnName);
  tableImageDialogVisible.value = true;
}

function closeTableImageDialog() {
  tableImageDialogVisible.value = false;
  tableImageRow.value = null;
  tableImageColumn.value = '';
}

function downloadTableImage() {
  const safeUrl = normalizeFieldName(tableImagePreviewUrl.value);
  if (!safeUrl) return;
  const link = document.createElement('a');
  link.href = safeUrl;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.download = tableImageRawValue.value || safeUrl.split('/').pop() || 'image';
  document.body.appendChild(link);
  link.click();
  link.remove();
}

async function openTableImageReplacementPicker() {
  if (!tableImageColumn.value || !tableImageRow.value) return;
  fieldMediaPickerMode.value = 'tableCell';
  fieldMediaPickerColumn.value = tableImageColumn.value;
  fieldMediaQuery.search = '';
  fieldMediaQuery.onlyUnbound = false;
  fieldMediaQuery.page = 1;
  fieldMediaPickerVisible.value = true;
  await loadFieldMediaLibrary();
}

async function replaceTableImage(asset: AdminMediaAsset, nextValue: string) {
  if (!selectedTableMeta.value || !tableImageRow.value || !tableImageColumn.value) return;
  tableImageActionLoading.value = true;
  try {
    await updateAdminTableRecord(
      selectedTableMeta.value.name,
      {
        original_row: tableImageRow.value,
        updates: { [tableImageColumn.value]: nextValue },
      },
      csrfToken.value
    );
    fieldMediaPickerVisible.value = false;
    ElMessage.success(t('msg.recordUpdated'));
    await loadSelectedTable();
    closeTableImageDialog();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowSaveFailed'));
  } finally {
    tableImageActionLoading.value = false;
  }
}

async function removeTableImage() {
  if (!selectedTableMeta.value || !tableImageRow.value || !tableImageColumn.value) return;
  tableImageActionLoading.value = true;
  try {
    await updateAdminTableRecord(
      selectedTableMeta.value.name,
      {
        original_row: tableImageRow.value,
        updates: { [tableImageColumn.value]: '' },
      },
      csrfToken.value
    );
    ElMessage.success(t('tableImage.removed'));
    await loadSelectedTable();
    closeTableImageDialog();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowSaveFailed'));
  } finally {
    tableImageActionLoading.value = false;
  }
}

async function deleteTableImageAsset() {
  if (!tableImageAsset.value?.id) return;
  const assetName = tableImageAsset.value.title || tableImageAsset.value.object_key || tableImageRawValue.value || 'image';
  try {
    await ElMessageBox.confirm(
      t('confirm.deleteMedia', { name: assetName }),
      t('confirm.deleteTitle'),
      {
        type: 'warning',
        confirmButtonText: t('tableImage.delete'),
        cancelButtonText: t('dialog.cancel'),
      }
    );
  } catch {
    return;
  }
  tableImageActionLoading.value = true;
  try {
    await deleteAdminMedia(tableImageAsset.value.id, csrfToken.value);
    ElMessage.success(t('msg.mediaDeleted'));
    await loadResources();
    await loadSelectedTable();
    closeTableImageDialog();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.mediaDeleteFailed'));
  } finally {
    tableImageActionLoading.value = false;
  }
}

function isInteractiveDragTarget(target: EventTarget | null) {
  if (!(target instanceof HTMLElement)) return false;
  return Boolean(
    target.closest(
      'button, a, input, textarea, select, label, .el-button, .el-input, .el-select, .el-checkbox, .row-actions, .table-inline-editor, .table-cell-display, .table-cell-media__thumb'
    )
  );
}

function getActiveInlineEditAnchor() {
  if (!tableShellRef.value || !inlineEditRow.value || !inlineEditColumn.value) return null;
  return tableShellRef.value.querySelector('.table-cell-display--editing') as HTMLElement | null;
}

function updateInlineEditPosition(anchor?: HTMLElement | null) {
  const target = anchor || getActiveInlineEditAnchor();
  if (!target) return;
  const rect = target.getBoundingClientRect();
  inlineEditOverlayRect.top = rect.top;
  inlineEditOverlayRect.left = rect.left;
  inlineEditOverlayRect.width = rect.width;
  inlineEditOverlayRect.minHeight = rect.height;
}

async function focusInlineEditInput() {
  await nextTick();
  inlineEditInputRef.value?.focus?.();
  const nativeInput = inlineEditInputRef.value?.input
    || inlineEditInputRef.value?.$el?.querySelector?.('input');
  if (typeof nativeInput?.select === 'function') {
    nativeInput.select();
  }
}

function getTableHorizontalScrollTarget() {
  if (!tableShellRef.value) return null;
  return (
    tableShellRef.value.querySelector('.el-scrollbar__wrap') ||
    tableShellRef.value.querySelector('.el-table__body-wrapper') ||
    tableShellRef.value
  ) as HTMLElement | null;
}

function handleTableDragMove(event: MouseEvent) {
  const scrollTarget = getTableHorizontalScrollTarget();
  if (!tableDragState.active || !scrollTarget) return;
  const deltaX = event.clientX - tableDragState.startX;
  scrollTarget.scrollLeft = tableDragState.startScrollLeft - deltaX;
}

function stopTableDrag() {
  if (!tableDragState.active) return;
  tableDragState.active = false;
  tableShellRef.value?.classList.remove('table-shell--dragging');
  document.body.classList.remove('admin-table-dragging');
  window.removeEventListener('mousemove', handleTableDragMove);
  window.removeEventListener('mouseup', stopTableDrag);
}

function beginTableDrag(event: MouseEvent) {
  const scrollTarget = getTableHorizontalScrollTarget();
  if (event.button !== 0 || !tableShellRef.value || !scrollTarget) return;
  if (inlineEditRow.value && !(event.target instanceof HTMLElement && event.target.closest('.table-inline-editor'))) {
    void saveInlineEdit();
    return;
  }
  if (scrollTarget.scrollWidth <= scrollTarget.clientWidth) return;
  if (isInteractiveDragTarget(event.target)) return;
  tableDragState.active = true;
  tableDragState.startX = event.clientX;
  tableDragState.startScrollLeft = scrollTarget.scrollLeft;
  tableShellRef.value.classList.add('table-shell--dragging');
  document.body.classList.add('admin-table-dragging');
  window.addEventListener('mousemove', handleTableDragMove);
  window.addEventListener('mouseup', stopTableDrag);
  event.preventDefault();
}

function isInlineEditing(row: Record<string, any>, columnName: string) {
  return inlineEditRow.value === row && inlineEditColumn.value === columnName;
}

async function persistCellUpdate(
  row: Record<string, any>,
  columnName: string,
  originalRow: Record<string, any> | null,
  nextValue: string
) {
  if (!selectedTableMeta.value) return false;
  const previousValueSource = originalRow || row;
  const previousValue = previousValueSource[columnName] == null ? '' : String(previousValueSource[columnName]);
  if (nextValue === previousValue) return false;
  await updateAdminTableRecord(
    selectedTableMeta.value.name,
    {
      original_row: originalRow,
      updates: {
        [columnName]: nextValue,
      },
    },
    csrfToken.value
  );
  row[columnName] = nextValue;
  ElMessage.success({
    message: t('msg.cellSaved'),
    duration: 1000,
  });
  void loadAuditLogs();
  return true;
}

async function openTextCellDialog(row: Record<string, any>, columnName: string) {
  if (!canInlineEditColumn(columnName) || textCellDialogSaving.value) return;
  if (inlineEditRow.value && (inlineEditRow.value !== row || inlineEditColumn.value !== columnName)) {
    await saveInlineEdit();
  }
  cancelInlineEdit();
  textCellDialogRow.value = row;
  textCellDialogColumn.value = columnName;
  textCellDialogOriginalRow.value = { ...row };
  textCellDialogDraft.value = row[columnName] == null ? '' : String(row[columnName]);
  textCellDialogVisible.value = true;
  await nextTick();
  const textarea = textCellDialogInputRef.value?.textarea
    || textCellDialogInputRef.value?.$el?.querySelector?.('textarea');
  textarea?.focus?.();
}

async function handleSTableCellEdited(
  row: Record<string, any>,
  columnName: string,
  newRowData: Record<string, any>
) {
  if (!selectedTableMeta.value) return;
  const originalRow = getTrackedTableCellOriginalRow(row, columnName) || { ...row };
  const nextValue = newRowData?.[columnName] == null ? '' : String(newRowData[columnName]);
  if (isTableCellSaving(row, columnName)) return;
  setTableCellSaving(row, columnName, true);
  try {
    await persistCellUpdate(row, columnName, originalRow, nextValue);
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowSaveFailed'));
    await loadSelectedTable();
  } finally {
    setTableCellSaving(row, columnName, false);
    clearTrackedTableCellOriginalRow(row, columnName);
  }
}

async function beginInlineEdit(row: Record<string, any>, columnName: string, event?: MouseEvent) {
  if (!canInlineEditColumn(columnName) || inlineEditSaving.value) return;
  if (inlineEditUsesTextarea(columnName, row)) {
    await openTextCellDialog(row, columnName);
    return;
  }
  closeTextCellDialog();
  if (inlineEditRow.value && (inlineEditRow.value !== row || inlineEditColumn.value !== columnName)) {
    await saveInlineEdit();
  }
  inlineEditRow.value = row;
  inlineEditColumn.value = columnName;
  inlineEditOriginalRow.value = { ...row };
  inlineEditDraft.value = row[columnName] == null ? '' : String(row[columnName]);
  await nextTick();
  await focusInlineEditInput();
}

function cancelInlineEdit() {
  inlineEditRow.value = null;
  inlineEditColumn.value = '';
  inlineEditOriginalRow.value = null;
  inlineEditDraft.value = '';
  inlineEditOverlayRect.top = 0;
  inlineEditOverlayRect.left = 0;
  inlineEditOverlayRect.width = 0;
  inlineEditOverlayRect.minHeight = 0;
}

function closeTextCellDialog() {
  if (textCellDialogSaving.value) return;
  textCellDialogVisible.value = false;
  textCellDialogRow.value = null;
  textCellDialogColumn.value = '';
  textCellDialogOriginalRow.value = null;
  textCellDialogDraft.value = '';
}

function handleInlineEditEnter(event: KeyboardEvent, columnName: string) {
  event.preventDefault();
  void saveInlineEdit();
}

function handleTableSelectionChange(selectedKeys: Array<string | number>, rows: Record<string, any>[]) {
  if (!tableDeleteMode.value) return;
  tableDeleteSelectionKeys.value = Array.isArray(selectedKeys) ? [...selectedKeys] : [];
  tableDeleteSelection.value = Array.isArray(rows) ? [...rows] : [];
}

function enterTableDeleteMode() {
  closeTextCellDialog();
  tableDeleteMode.value = true;
  tableDeleteSelectionKeys.value = [];
  tableDeleteSelection.value = [];
}

function cancelTableDeleteMode() {
  tableDeleteMode.value = false;
  tableDeleteSelectionKeys.value = [];
  tableDeleteSelection.value = [];
}

async function confirmDeleteSelectedRows() {
  if (!selectedTableMeta.value || !tableDeleteSelection.value.length) return;
  try {
    await ElMessageBox.confirm(
      `${t('confirm.deleteRows', { count: tableDeleteSelection.value.length })}\n${t('confirm.deleteRowsWarning')}`,
      t('confirm.deleteTitle'),
      {
        type: 'warning',
        confirmButtonText: t('table.confirmDelete'),
        cancelButtonText: t('table.cancelDelete'),
      }
    );
  } catch {
    return;
  }

  const rowsToDelete = [...tableDeleteSelection.value];
  try {
    for (const row of rowsToDelete) {
      await deleteAdminTableRecord(selectedTableMeta.value.name, { original_row: row }, csrfToken.value);
    }
    ElMessage.success(t('msg.recordsDeleted', { count: rowsToDelete.length }));
    cancelTableDeleteMode();
    await loadResources();
    await loadSelectedTable();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowDeleteFailed'));
  }
}

async function saveInlineEdit() {
  if (!selectedTableMeta.value || !inlineEditRow.value || !inlineEditColumn.value || inlineEditSaving.value) return;
  const row = inlineEditRow.value;
  const columnName = inlineEditColumn.value;
  inlineEditSaving.value = true;
  try {
    await persistCellUpdate(row, columnName, inlineEditOriginalRow.value, inlineEditDraft.value);
    cancelInlineEdit();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowSaveFailed'));
  } finally {
    inlineEditSaving.value = false;
  }
}

function handleGlobalInlineMouseDown(event: MouseEvent) {
  if (!inlineEditRow.value || inlineEditSaving.value) return;
  if (!(event.target instanceof HTMLElement)) return;
  if (event.target.closest('.table-inline-editor')) return;
  void saveInlineEdit();
}

function handleInlineEditViewportChange() {
  if (!inlineEditRow.value || !inlineEditColumn.value) return;
  updateInlineEditPosition();
}

async function saveTextCellDialog() {
  if (!selectedTableMeta.value || !textCellDialogRow.value || !textCellDialogColumn.value || textCellDialogSaving.value) return;
  textCellDialogSaving.value = true;
  try {
    await persistCellUpdate(
      textCellDialogRow.value,
      textCellDialogColumn.value,
      textCellDialogOriginalRow.value,
      textCellDialogDraft.value
    );
    closeTextCellDialog();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.rowSaveFailed'));
  } finally {
    textCellDialogSaving.value = false;
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
      await Promise.all([loadLLMSettings(), loadWorkflowSettings()]);
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

function applyWorkflowSettings(settings: AdminAIWorkflowSettings | null) {
  if (!settings) return;
  workflowForm.workflow_enable = Boolean(settings.workflow_enable);
  workflowForm.conversation_router_enable = Boolean(settings.conversation_router_enable);
  workflowForm.conversation_router_model = settings.conversation_router_model || '';
  workflowForm.conversation_router_timeout = Number(settings.conversation_router_timeout || 15);
  workflowForm.router_confidence_threshold = Number(settings.router_confidence_threshold || 0.7);
  workflowForm.max_retrieval_rounds = Number(settings.max_retrieval_rounds || 2);
  workflowForm.max_tool_steps_per_round = Number(settings.max_tool_steps_per_round || 4);
  workflowForm.max_total_tool_steps = Number(settings.max_total_tool_steps || 12);
  workflowForm.retrieval_judge_enable = Boolean(settings.retrieval_judge_enable);
  workflowForm.retrieval_judge_model = settings.retrieval_judge_model || '';
  workflowForm.retrieval_judge_threshold = Number(settings.retrieval_judge_threshold || 0.8);
  workflowForm.stop_on_no_new_evidence = Boolean(settings.stop_on_no_new_evidence);
  workflowForm.stop_on_repeated_plan = Boolean(settings.stop_on_repeated_plan);
  workflowForm.allow_pubmed_deepen = Boolean(settings.allow_pubmed_deepen);
  workflowForm.allow_table_deepen = Boolean(settings.allow_table_deepen);
  workflowForm.allow_doc_deepen = Boolean(settings.allow_doc_deepen);
  workflowForm.final_critic_enable = Boolean(settings.final_critic_enable);
}

async function loadLLMSettings() {
  applyLLMSettings(await fetchAdminLLMSettings());
}

async function loadWorkflowSettings() {
  applyWorkflowSettings(await fetchAdminAIWorkflowSettings());
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
  closeTextCellDialog();
  clearTableEditTracking();
  cancelTableDeleteMode();
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

function handleSTablePaginationUpdate(pagination: Partial<STablePaginationConfig>) {
  const nextPageSize = Number(pagination.pageSize || tableQuery.pageSize);
  const pageSizeChanged = nextPageSize !== tableQuery.pageSize;
  const nextPage = Number(pagination.current || (pageSizeChanged ? 1 : tablePagination.page));
  const pageChanged = nextPage !== tablePagination.page;

  if (!pageSizeChanged && !pageChanged) return;

  if (pageSizeChanged) {
    tableQuery.pageSize = nextPageSize;
  }
  tablePagination.page = pageSizeChanged ? 1 : nextPage;
  void loadSelectedTable();
}

function handleTableSizeChange(size: number) {
  if (Number(size) === tableQuery.pageSize) return;
  tableQuery.pageSize = Number(size);
  tablePagination.page = 1;
  void loadSelectedTable();
}

function extractSTableSorter(sorter: any) {
  const normalized = Array.isArray(sorter) ? sorter[0] : sorter;
  const field = normalized?.field || normalized?.columnKey || normalized?.dataIndex || normalized?.key;
  const orderRaw = normalized?.order || normalized?.sortOrder || null;
  if (!field) return null;
  if (!orderRaw) {
    return {
      field: String(field),
      order: null,
    };
  }
  return {
    field: String(field),
    order: orderRaw === 'descending' || orderRaw === 'descend' ? 'desc' : 'asc',
  };
}

function handleSTableChange(_pagination?: Partial<STablePaginationConfig>, _filters?: any, sorter?: any) {
  const resolved = extractSTableSorter(sorter);
  if (!resolved) return;

  const nextSortBy = resolved.order ? resolved.field : '';
  const nextSortOrder = resolved.order || 'asc';
  if (tableQuery.sortBy === nextSortBy && tableQuery.sortOrder === nextSortOrder) return;

  tableQuery.sortBy = nextSortBy;
  tableQuery.sortOrder = nextSortOrder;
  tablePagination.page = 1;
  void loadSelectedTable();
}

function resetRowForm() {
  Object.keys(rowForm).forEach((key) => delete rowForm[key]);
}

function openCreateRow() {
  cancelInlineEdit();
  closeTextCellDialog();
  rowDialogMode.value = 'create';
  originalRow.value = null;
  resetRowForm();
  resetRowMediaState();
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

function openMediaFieldDialog() {
  if (!selectedTableMeta.value) return;
  mediaFieldDialogVisible.value = true;
}

function openVirtualMediaDialog() {
  if (!selectedTableMeta.value) return;
  virtualMediaDialogVisible.value = true;
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

async function handleMediaFieldsSaved(fields: Record<string, AdminTableMediaFieldConfig>) {
  if (!selectedTableMeta.value) return;
  selectedTableMeta.value = {
    ...selectedTableMeta.value,
    media_fields: fields,
  };
  await loadAuditLogs();
}

async function handleVirtualMediaFieldsSaved(fields: AdminVirtualMediaField[]) {
  if (!selectedTableMeta.value) return;
  selectedTableMeta.value = {
    ...selectedTableMeta.value,
    virtual_media_fields: fields,
  };
  await loadAuditLogs();
}

function openRecordMediaSlots(row: Record<string, any>) {
  selectedRecordMediaRow.value = { ...row };
  recordMediaDialogVisible.value = true;
}

async function handleRecordMediaChanged() {
  await loadAuditLogs();
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

async function saveWorkflowConfig() {
  workflowSaving.value = true;
  try {
    const settings = await saveAdminAIWorkflowSettings({
      csrfToken: csrfToken.value,
      workflow_enable: workflowForm.workflow_enable,
      conversation_router_enable: workflowForm.conversation_router_enable,
      conversation_router_model: workflowForm.conversation_router_model,
      conversation_router_timeout: workflowForm.conversation_router_timeout,
      router_confidence_threshold: workflowForm.router_confidence_threshold,
      max_retrieval_rounds: workflowForm.max_retrieval_rounds,
      max_tool_steps_per_round: workflowForm.max_tool_steps_per_round,
      max_total_tool_steps: workflowForm.max_total_tool_steps,
      retrieval_judge_enable: workflowForm.retrieval_judge_enable,
      retrieval_judge_model: workflowForm.retrieval_judge_model,
      retrieval_judge_threshold: workflowForm.retrieval_judge_threshold,
      stop_on_no_new_evidence: workflowForm.stop_on_no_new_evidence,
      stop_on_repeated_plan: workflowForm.stop_on_repeated_plan,
      allow_pubmed_deepen: workflowForm.allow_pubmed_deepen,
      allow_table_deepen: workflowForm.allow_table_deepen,
      allow_doc_deepen: workflowForm.allow_doc_deepen,
      final_critic_enable: workflowForm.final_critic_enable
    });
    applyWorkflowSettings(settings);
    ElMessage.success(t('msg.workflowSaved'));
    await loadAuditLogs();
  } catch (error: any) {
    ElMessage.error(error?.message || t('msg.workflowSaveFailed'));
  } finally {
    workflowSaving.value = false;
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
  closeTextCellDialog();
  clearTableEditTracking();
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
    await Promise.all([loadLLMSettings(), loadWorkflowSettings()]);
    return;
  }
  if (currentView.value === 'media') {
    await Promise.all([loadResources(), loadAuditLogs(), mediaPanelRef.value?.refresh?.()]);
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

watch(
  () => rowDialogVisible.value,
  (visible) => {
    if (!visible) {
      resetRowMediaState();
    }
  }
);

onMounted(async () => {
  window.addEventListener('mousedown', handleGlobalInlineMouseDown, true);
  const authed = await ensureAdminSession();
  if (!authed) return;
  await Promise.all([loadResources(), loadLLMSettings(), loadWorkflowSettings(), loadAuditLogs()]);
  if (!route.query.view) {
    navigate('overview');
  } else {
    await syncRouteState();
  }
});

onUnmounted(() => {
  window.removeEventListener('mousedown', handleGlobalInlineMouseDown, true);
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
  display: grid;
  grid-template-columns: auto minmax(340px, 420px) minmax(0, 1fr);
  gap: 12px 16px;
  align-items: center;
  margin-bottom: 12px;
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
  align-items: center;
  justify-content: flex-end;
  margin-left: 0;
}

.overview-stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  flex-wrap: nowrap;
  gap: 8px;
  margin: 0;
  min-width: 0;
  align-items: center;
  justify-self: start;
}

.summary-strip span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: var(--admin-surface-muted);
  border: 1px solid var(--admin-border);
  color: var(--admin-text-muted);
  font-size: 0.81rem;
  font-weight: 700;
}

.table-toolbar {
  display: flex;
  align-items: center;
  margin: 0;
  min-width: 0;
  width: 100%;
  max-width: 560px;
  justify-self: center;
}

.table-search-bar {
  display: grid;
  grid-template-columns: 160px minmax(0, 1fr) 112px;
  gap: 10px;
  min-width: 0;
  width: 100%;
}

.table-search-bar__select,
.table-search-bar__input {
  min-width: 0;
}

.table-search-bar__select :deep(.el-select__wrapper),
.table-search-bar__input :deep(.el-input__wrapper) {
  min-height: 38px;
  border-radius: 14px;
}

.table-search-bar__select :deep(.el-select__wrapper) {
  padding-inline: 12px;
}

.table-search-bar__input :deep(.el-input__wrapper) {
  padding-inline: 14px;
}

.table-search-bar__submit {
  min-height: 38px;
  border-radius: 14px;
  font-weight: 700;
}

.card-actions--inline {
  gap: 10px;
  justify-content: flex-end;
  min-width: 0;
  width: 100%;
  justify-self: end;
  flex-wrap: wrap;
}

.table-page-size {
  width: 124px;
}

.inline-alert {
  margin-bottom: 14px;
}

.table-shell {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-surface);
}

.workspace-table {
  width: 100%;
}

.table-shell :deep(.s-table) {
  min-width: 100%;
  background: var(--admin-table-row-bg);
  color: var(--admin-text);
}

.table-shell :deep(.s-table__content) {
  background: var(--admin-table-row-bg);
}

.table-shell :deep(.s-table__header-cell) {
  font-weight: 800;
  background: var(--admin-table-header-bg);
  color: var(--admin-table-header-text);
}

.table-shell :deep(.s-table__cell),
.table-shell :deep(.s-table__header-cell) {
  border-color: var(--admin-border);
}

.table-shell :deep(.s-table__row) {
  background: var(--admin-table-row-bg);
}

.table-shell :deep(.s-table__row.s-table__row-odd) {
  background: var(--admin-table-row-alt);
}

.table-shell :deep(.s-table__row.s-table__row-hover),
.table-shell :deep(.s-table__row:hover) {
  background: var(--admin-table-row-hover);
}

.table-shell :deep(.s-table__row.s-table__row-selected),
.table-shell :deep(.s-table__row.s-table__row-selected .s-table__cell) {
  background: rgba(37, 99, 235, 0.08);
}

.table-shell :deep(.s-table__cell) {
  background: transparent;
  color: var(--admin-text);
  vertical-align: top;
}

.table-shell :deep(.s-table__cell-inner .s-table__cell-content) {
  padding: 10px 8px;
  color: var(--admin-text);
  line-height: 1.52;
  white-space: normal;
  word-break: break-word;
}

.table-shell :deep(.s-table__cell-fix-left),
.table-shell :deep(.s-table__cell-fix-right) {
  background: inherit;
}

.table-shell :deep(.s-table__header),
.table-shell :deep(.s-table__body),
.table-shell :deep(.s-table__summary) {
  background: var(--admin-table-row-bg);
}

.table-shell :deep(.s-table__cell-edit-wrap .el-input__wrapper) {
  min-height: 44px;
  padding-inline: 12px;
  border-radius: 12px;
  border: 1px solid var(--admin-accent);
  background: var(--admin-surface);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

.table-shell :deep(.s-table__pagination) {
  margin: 0;
  padding: 0 16px 16px;
}

.table-shell :deep(.s-table__center-viewport),
.table-shell :deep(.s-table__horizontal-scroll-viewport) {
  scrollbar-gutter: stable both-edges;
}

.table-shell :deep(.table-cell-media) {
  display: grid;
  justify-items: center;
  gap: 8px;
  padding: 6px 0;
}

.table-shell :deep(.table-cell-media__thumb) {
  width: 92px;
  height: 92px;
  padding: 0;
  border: 1px solid var(--admin-border);
  border-radius: 12px;
  background: var(--admin-surface-muted);
  overflow: hidden;
  cursor: zoom-in;
}

.table-shell :deep(.table-cell-media__image) {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  background: var(--admin-surface);
}

.table-shell :deep(.table-cell-media__empty) {
  width: 92px;
  height: 92px;
  border: 1px dashed var(--admin-border);
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: var(--admin-text-faint);
  background: var(--admin-surface-muted);
  font-weight: 700;
}

.table-shell :deep(.table-cell-media__empty-button) {
  padding: 0;
  cursor: pointer;
}

.table-shell :deep(.table-cell-media__value) {
  width: 100%;
  text-align: center;
  color: var(--admin-text-muted);
  font-size: 0.82rem;
  line-height: 1.35;
  word-break: break-word;
}

.summary-strip-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.summary-strip-selection {
  color: var(--admin-text-muted);
  font-weight: 700;
}

.table-shell :deep(.row-actions) {
  display: flex;
  gap: 8px;
}

.table-shell :deep(.table-cell-display) {
  width: 100%;
  min-height: 48px;
  padding: 10px 8px;
  border: none;
  background: transparent;
  text-align: left;
  display: flex;
  align-items: flex-start;
  cursor: pointer;
}

.table-shell :deep(.table-cell-display:hover) {
  background: var(--admin-surface-muted);
  border-radius: 10px;
}

.table-shell :deep(.table-cell-display--editable) {
  cursor: text;
}

.table-shell :deep(.table-cell-display--editing) {
  background: var(--admin-surface);
  border-radius: 12px;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.16);
}

.table-shell :deep(.table-cell-value) {
  width: 100%;
  overflow: visible;
  text-overflow: unset;
  white-space: normal;
  word-break: break-word;
  line-height: 1.52;
  color: var(--admin-text);
}

.table-shell :deep(.table-cell-value--empty) {
  color: var(--admin-text-faint);
}

.table-inline-editor {
  width: 100%;
  pointer-events: auto;
}

.table-inline-editor--embedded {
  padding: 6px 8px;
}

.table-inline-editor__input {
  width: 100%;
}

.table-inline-editor__input :deep(.el-input__wrapper) {
  min-height: 42px;
  padding-inline: 12px;
  border-radius: 12px;
  border: 1px solid var(--admin-accent);
  background: var(--admin-surface);
  box-shadow:
    0 0 0 2px rgba(37, 99, 235, 0.12);
}

.table-image-workbench {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 20px;
}

.table-image-workbench__preview-shell {
  min-height: 440px;
  border-radius: 20px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
  padding: 18px;
  display: grid;
  place-items: center;
}

.table-image-workbench__preview {
  width: 100%;
  max-height: 68vh;
  object-fit: contain;
  border-radius: 14px;
  background: var(--admin-surface);
}

.table-image-workbench__empty {
  color: var(--admin-text-muted);
  font-weight: 700;
}

.table-image-workbench__side {
  display: grid;
  align-content: start;
  gap: 16px;
}

.table-image-workbench__meta {
  display: grid;
  gap: 12px;
}

.table-image-workbench__meta article {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
}

.table-image-workbench__meta span,
.table-image-workbench__meta strong {
  display: block;
}

.table-image-workbench__meta span {
  color: var(--admin-text-faint);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.table-image-workbench__meta strong {
  margin-top: 6px;
  color: var(--admin-text);
  line-height: 1.5;
  word-break: break-word;
}

.table-image-workbench__tip {
  margin: 0;
  color: var(--admin-text-muted);
  line-height: 1.6;
}

.table-image-workbench__actions {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  align-items: stretch;
  grid-auto-rows: 52px;
}

.table-image-workbench__action-button {
  width: 100%;
  height: 100%;
  min-height: 52px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  font-weight: 700;
  box-sizing: border-box;
}

.table-image-workbench__actions > * {
  width: 100%;
  min-width: 0;
  align-self: stretch;
}

.table-image-workbench__actions :deep(.el-button) {
  width: 100%;
  min-height: 52px;
  height: 100%;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  box-sizing: border-box;
  padding-inline: 16px;
}

.table-image-workbench__actions :deep(.el-button > span),
.table-image-workbench__action-button :deep(span) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  text-align: center;
  line-height: 1.25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-cell-editor-dialog {
  display: grid;
  gap: 16px;
}

.text-cell-editor-dialog__meta {
  display: grid;
  gap: 12px;
}

.text-cell-editor-dialog__meta article {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
}

.text-cell-editor-dialog__meta span,
.text-cell-editor-dialog__meta strong {
  display: block;
}

.text-cell-editor-dialog__meta span {
  color: var(--admin-text-faint);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.text-cell-editor-dialog__meta strong {
  margin-top: 6px;
  color: var(--admin-text);
  line-height: 1.5;
}

.text-cell-editor-dialog__input :deep(.el-textarea__inner) {
  min-height: 320px !important;
  padding: 16px 18px;
  line-height: 1.72;
  border-radius: 16px;
  resize: vertical;
  font-size: 0.98rem;
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

.row-form-item--wide {
  grid-column: 1 / -1;
}

.row-media-field {
  display: grid;
  gap: 12px;
}

.row-media-preview-shell {
  min-height: 200px;
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(226, 232, 240, 0.34));
  display: grid;
  place-items: center;
}

.row-media-preview-image {
  width: 100%;
  max-height: 360px;
  object-fit: contain;
  display: block;
}

.row-media-preview-empty {
  color: var(--admin-text-muted);
  font-size: 0.92rem;
}

.row-media-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.row-media-meta {
  display: grid;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid var(--admin-border);
  border-radius: 14px;
  background: var(--admin-surface-muted);
}

.row-media-meta span {
  color: var(--admin-text-faint);
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.row-media-meta strong {
  color: var(--admin-text);
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.row-media-picker {
  display: grid;
  gap: 16px;
}

.row-media-picker__hint {
  margin: 0;
  color: var(--admin-text-muted);
  line-height: 1.6;
}

.row-media-picker__toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.row-media-picker__toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.row-media-picker__upload-input {
  display: none;
}

.row-media-picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  max-height: 58vh;
  overflow: auto;
  padding-right: 4px;
}

.row-media-picker-card {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface-muted);
  padding: 12px;
  display: grid;
  gap: 10px;
  text-align: left;
  transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}

.row-media-picker-card:hover {
  border-color: rgba(37, 99, 235, 0.32);
  transform: translateY(-1px);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
}

.row-media-picker-card__thumb {
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.12), rgba(226, 232, 240, 0.3));
}

.row-media-picker-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.row-media-picker-card__copy {
  display: grid;
  gap: 4px;
}

.row-media-picker-card__copy strong {
  color: var(--admin-text);
  line-height: 1.35;
}

.row-media-picker-card__copy span,
.row-media-picker-card__action,
.row-media-picker-empty {
  color: var(--admin-text-muted);
  font-size: 0.82rem;
}

.row-media-picker-card__action {
  font-weight: 700;
}

.row-media-picker-empty {
  padding: 20px;
  border: 1px dashed var(--admin-border);
  border-radius: 16px;
  background: var(--admin-surface-muted);
  text-align: center;
}

.span-2 {
  grid-column: 1 / -1;
}

.workflow-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 18px;
  min-height: 40px;
  align-items: center;
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

  .table-controls-bar {
    grid-template-columns: auto minmax(280px, 1fr);
  }

  .card-actions {
    justify-content: flex-start;
  }

  .summary-strip,
  .table-toolbar {
    grid-column: auto;
  }

  .card-actions--inline {
    grid-column: 1 / -1;
    justify-self: stretch;
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

  .table-controls-bar {
    grid-template-columns: 1fr;
  }

  .table-toolbar {
    max-width: none;
    justify-self: stretch;
  }

  .table-search-bar {
    grid-template-columns: 148px minmax(0, 1fr) 104px;
  }

  .summary-strip,
  .card-actions--inline {
    grid-column: 1 / -1;
  }

  .card-actions--inline {
    justify-content: flex-start;
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

  .card-actions {
    margin-left: 0;
    justify-content: flex-start;
  }

  .workspace-subtitle-select,
  .workspace-subtitle-control,
  .topbar-tools {
    width: 100%;
    min-width: 0;
  }

  .overview-stat-grid,
  .summary-grid,
  .llm-grid,
  .row-form-grid,
  .doc-editor-layout--split,
  .audit-meta-grid,
  .audit-json-grid {
    grid-template-columns: 1fr;
  }

  .summary-strip {
    flex-wrap: wrap;
  }

  .table-toolbar,
  .table-search-bar {
    width: 100%;
    max-width: none;
  }

  .label-form-row {
    grid-template-columns: 1fr;
  }

  .row-media-picker__toolbar,
  .row-media-picker-grid {
    grid-template-columns: 1fr;
  }

  .table-image-workbench,
  .table-image-workbench__actions {
    grid-template-columns: 1fr;
  }

  .table-search-bar {
    grid-template-columns: 1fr;
  }
}
</style>
