<!-- src/views/AIYingying/AISidebar.vue -->
<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <img src="https://framerusercontent.com/images/1w0lzT7QXS4SRJgD02kucFjmSL4.png" alt="logo" />
        <div class="title">AI Yingying</div>
      </div>
    </div>

    <div class="note-banner">
      <div class="note-text">{{ noteText }}</div>
      <button
        v-if="!noteAcknowledged"
        class="note-ack"
        type="button"
        @click="acknowledgeNote"
      >
        I understand
      </button>
    </div>

    <button class="new-chat" type="button" @click="createSession">
      New chat
    </button>

    <div class="session-list">
      <div
        v-for="session in sessions"
        :key="session.id"
        class="session-item"
        :class="{ active: session.id === activeId }"
        role="button"
        tabindex="0"
        @click="selectSession(session.id)"
        @keydown.enter="selectSession(session.id)"
      >
        <div v-if="editingId !== session.id" class="session-row">
          <div class="session-title">{{ session.title || 'New chat' }}</div>
          <div v-if="confirmDeleteId !== session.id" class="session-actions">
            <button
              class="session-action"
              type="button"
              @click.stop="startRename(session)"
              aria-label="Rename session"
            >
              Rename
            </button>
            <button
              class="session-action danger"
              type="button"
              @click.stop="startDelete(session)"
              aria-label="Delete session"
            >
              Delete
            </button>
          </div>
        </div>
        <div v-else class="session-edit" @click.stop>
          <input
            v-model="editingTitle"
            class="session-input"
            type="text"
            maxlength="80"
            @keydown.enter.stop="confirmRename(session)"
            @keydown.esc.stop="cancelRename"
          />
          <div class="session-edit-actions">
            <button class="session-action" type="button" @click.stop="confirmRename(session)">
              Save
            </button>
            <button class="session-action" type="button" @click.stop="cancelRename">
              Cancel
            </button>
          </div>
        </div>
        <div v-if="confirmDeleteId === session.id" class="session-delete" @click.stop>
          <span>Delete this chat?</span>
          <div class="session-delete-actions">
            <button
              class="session-action danger"
              type="button"
              @click.stop="confirmDelete(session)"
            >
              Delete
            </button>
            <button class="session-action" type="button" @click.stop="cancelDelete">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    sessions: { type: Array, required: true },
    activeId: { type: String, required: true },
    noteAcknowledged: { type: Boolean, required: true },
    noteText: { type: String, required: true }
  },
  data() {
    return {
      editingId: '',
      editingTitle: '',
      confirmDeleteId: ''
    };
  },
  methods: {
    selectSession(id) {
      this.editingId = '';
      this.editingTitle = '';
      this.confirmDeleteId = '';
      this.$emit('session-selected', id);
    },
    createSession() {
      this.$emit('new-session');
    },
    acknowledgeNote() {
      this.$emit('acknowledge-note');
    },
    startRename(session) {
      this.confirmDeleteId = '';
      this.editingId = session.id;
      this.editingTitle = session?.title || 'New chat';
    },
    confirmRename(session) {
      const next = (this.editingTitle || '').trim();
      if (next) {
        this.$emit('rename-session', session.id, next);
      }
      this.editingId = '';
      this.editingTitle = '';
    },
    cancelRename() {
      this.editingId = '';
      this.editingTitle = '';
    },
    startDelete(session) {
      this.editingId = '';
      this.editingTitle = '';
      this.confirmDeleteId = session.id;
    },
    confirmDelete(session) {
      this.$emit('delete-session', session.id);
      this.confirmDeleteId = '';
    },
    cancelDelete() {
      this.confirmDeleteId = '';
    }
  }
};
</script>

<style scoped>
.sidebar {
  width: 232px;
  height: 100%;
  background-color: var(--app-surface);
  display: flex;
  flex-direction: column;
  padding: 12px 10px;
  border-right: 1px solid var(--app-border);
  gap: 8px;
  overflow-x: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 8px;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.new-chat {
  width: 100%;
  border: 1px solid var(--app-accent);
  background: var(--app-accent);
  color: #fff;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.note-banner {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 12px;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 12px;
}

.note-text {
  font-size: 12px;
  color: #92400e;
  line-height: 1.4;
  font-weight: 600;
}

.note-ack {
  align-self: flex-start;
  padding: 6px 10px;
  font-size: 12px;
  border: 1px solid #f59e0b;
  border-radius: 12px;
  background: #f59e0b;
  color: #fff;
  cursor: pointer;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 2px;
  min-width: 0;
}

.session-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 8px 8px 10px;
  border-radius: 8px;
  border: 1px solid transparent;
  border-left: 3px solid transparent;
  background: transparent;
  color: var(--app-text);
  cursor: pointer;
  text-align: left;
  transition: background 0.2s ease, border-color 0.2s ease;
  min-width: 0;
  position: relative;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.session-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
}

.session-actions {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
  position: absolute;
  right: 6px;
  top: 6px;
  pointer-events: none;
}

.session-item:hover .session-actions {
  opacity: 1;
  pointer-events: auto;
}

.session-item:focus .session-actions {
  opacity: 1;
  pointer-events: auto;
}

.session-edit {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.session-input {
  width: 100%;
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid var(--app-border);
  background: var(--app-surface-2);
  color: var(--app-text);
  font-size: 12px;
}

.session-edit-actions,
.session-delete-actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.session-delete {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 11px;
  color: var(--app-text-muted);
  margin-top: 6px;
}

.session-action {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 8px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  color: var(--app-text-muted);
  cursor: pointer;
}

.session-action.danger {
  border-color: rgba(231, 76, 60, 0.5);
  color: #e74c3c;
}

.session-item:hover {
  background: var(--app-surface-2);
  border-color: var(--app-border);
  border-left-color: var(--app-accent);
}

.session-item.active {
  background: var(--app-surface-2);
  border-color: var(--app-border);
  border-left-color: var(--app-accent);
}

.session-title {
  font-size: 12px;
  font-weight: 600;
  line-height: 1.2;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  padding-right: 52px;
  max-width: 100%;
}

@media screen and (max-width: 768px) {
  .sidebar {
    width: 62px;
  }

  .title {
    display: none;
  }

  .new-chat {
    font-size: 0;
    padding: 10px;
  }

  .session-title {
    display: none;
  }

  .session-actions {
    display: none;
  }
}

:root[data-theme="dark"] .sidebar,
html.dark .sidebar {
  background-color: #151a23;
  border-right-color: rgba(255, 255, 255, 0.08);
}

:root[data-theme="dark"] .note-banner,
html.dark .note-banner {
  background: #3a2a12;
  border-color: #c58a1a;
}

:root[data-theme="dark"] .note-text,
html.dark .note-text {
  color: #f6d28b;
}

:root[data-theme="dark"] .session-item,
html.dark .session-item {
  color: #e0e6f0;
}

:root[data-theme="dark"] .session-item:hover,
html.dark .session-item:hover,
:root[data-theme="dark"] .session-item.active,
html.dark .session-item.active {
  background: #1e2430;
  border-color: rgba(255, 255, 255, 0.08);
  border-left-color: #4c71d8;
}
</style>
