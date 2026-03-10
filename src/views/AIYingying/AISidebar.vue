<!-- src/views/AIYingying/AISidebar.vue -->
<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="profile-card">
        <div class="logo">
          <div class="logo-mark">
            <img src="https://framerusercontent.com/images/1w0lzT7QXS4SRJgD02kucFjmSL4.png" alt="logo" />
          </div>
          <div class="logo-copy">
            <div class="eyebrow">ENSURE Assistant</div>
            <div class="title">AI Yingying</div>
            <div class="subtitle">sup-tRNA research assistant</div>
          </div>
        </div>

        <div class="note-banner" :class="{ acknowledged: noteAcknowledged }">
          <div class="note-topline">
            <span class="note-badge">{{ noteAcknowledged ? 'Acknowledged' : 'Review required' }}</span>
            <button class="note-link" type="button" @click="openNoteModal">
              {{ noteAcknowledged ? 'Usage note' : 'Unlock chat' }}
            </button>
          </div>
          <div class="note-text">
            {{ noteAcknowledged ? 'AI answers can be inaccurate. Verify key claims and citations.' : 'Review the usage note before chatting.' }}
          </div>
        </div>
      </div>
    </div>

    <button class="new-chat" type="button" @click="createSession">
      <span class="new-chat-plus">+</span>
      <span>New chat</span>
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

    <div class="sidebar-footer">
      <button
        class="theme-toggle"
        type="button"
        :aria-pressed="isDarkMode"
        @click="toggleTheme"
      >
        <span class="theme-toggle-icon" aria-hidden="true">
          <svg v-if="isDarkMode" viewBox="0 0 24 24">
            <path d="M21 12.8A8.8 8.8 0 1 1 11.2 3a7.1 7.1 0 0 0 9.8 9.8Z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"></path>
          </svg>
          <svg v-else viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.9"></circle>
            <path d="M12 2.4v2.4M12 19.2v2.4M4.8 4.8l1.7 1.7M17.5 17.5l1.7 1.7M2.4 12h2.4M19.2 12h2.4M4.8 19.2l1.7-1.7M17.5 6.5l1.7-1.7" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"></path>
          </svg>
        </span>
        <span>{{ isDarkMode ? 'Dark mode' : 'Light mode' }}</span>
      </button>

      <a
        class="return-link"
        href="/"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Return to ENSURE website in a new tab"
        title="Open ENSURE in a new tab"
      >
        <span class="return-link-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="M15 18l-6-6 6-6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
          </svg>
        </span>
        <span>Return to ENSURE</span>
      </a>
    </div>
  </div>
</template>

<script>
import { getThemeMode, setThemeMode } from '@/utils/theme';

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
      confirmDeleteId: '',
      isDarkMode: false
    };
  },
  mounted() {
    this.syncThemeState();
  },
  methods: {
    syncThemeState() {
      const root = document.documentElement;
      const storedMode = getThemeMode();
      this.isDarkMode = storedMode === 'dark' || (storedMode === 'system' && (root.classList.contains('dark') || root.getAttribute('data-theme') === 'dark'));
    },
    toggleTheme() {
      setThemeMode(this.isDarkMode ? 'light' : 'dark');
      this.syncThemeState();
    },
    selectSession(id) {
      this.editingId = '';
      this.editingTitle = '';
      this.confirmDeleteId = '';
      this.$emit('session-selected', id);
    },
    createSession() {
      this.$emit('new-session');
    },
    openNoteModal() {
      this.$emit('open-note-modal');
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
  width: 280px;
  height: 100%;
  background: var(--ai-sidebar);
  display: flex;
  flex-direction: column;
  padding: 12px;
  border-right: 1px solid var(--ai-border);
  gap: 10px;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: stretch;
}

.profile-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  padding: 12px;
  border-radius: 18px;
  border: 1px solid var(--ai-border);
  background: linear-gradient(180deg, var(--ai-card), var(--ai-card-muted));
  box-shadow: var(--ai-card-shadow);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(180deg, var(--ai-accent-soft), transparent);
  border: 1px solid var(--ai-border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo img {
  width: 24px;
  height: 24px;
}

.logo-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.eyebrow {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--ai-accent);
}

.title {
  font-size: 15px;
  font-weight: 700;
  color: var(--ai-text);
  line-height: 1.2;
}

.subtitle {
  font-size: 12px;
  line-height: 1.25;
  color: var(--ai-muted);
}

.note-banner {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  padding: 9px 10px;
  border-radius: 14px;
  background: linear-gradient(180deg, var(--ai-card-muted), var(--ai-card));
  border: 1px solid var(--ai-warning-border);
  box-sizing: border-box;
  box-shadow: none;
}

.note-banner.acknowledged {
  background: linear-gradient(180deg, var(--ai-card-muted), var(--ai-card));
  border-color: var(--ai-border-strong);
}

.note-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.note-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 22px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: var(--ai-warning-text);
  font-size: 9px;
  font-weight: 700;
}

.note-banner.acknowledged .note-badge {
  background: var(--ai-accent-soft);
  color: var(--ai-accent);
}

.note-link {
  border: none;
  background: transparent;
  color: var(--ai-accent);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
  white-space: nowrap;
}

.note-text {
  font-size: 11px;
  color: var(--ai-muted);
  line-height: 1.35;
  font-weight: 600;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.new-chat {
  width: 100%;
  min-height: 44px;
  border: 1px solid var(--ai-border-strong);
  background: linear-gradient(180deg, var(--ai-card-muted), var(--ai-card));
  color: var(--ai-accent-strong);
  padding: 0 14px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: none;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.new-chat:hover {
  transform: translateY(-1px);
  border-color: rgba(47, 111, 237, 0.32);
  background: linear-gradient(180deg, var(--ai-card), var(--ai-accent-soft));
}

.new-chat-plus {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: var(--ai-accent-soft);
  color: var(--ai-accent);
}

.session-list {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 8px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
  min-width: 0;
}

.session-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 11px 12px;
  border-radius: 14px;
  border: 1px solid transparent;
  background: var(--ai-card);
  color: var(--ai-text);
  cursor: pointer;
  text-align: left;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
  min-width: 0;
  position: relative;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
  box-shadow: none;
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
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid var(--ai-border);
  background: var(--ai-card);
  color: var(--ai-text);
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
  font-size: 12px;
  color: var(--ai-muted);
  margin-top: 6px;
}

.session-action {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 10px;
  border: 1px solid var(--ai-border);
  background: var(--ai-card);
  color: var(--ai-muted);
  cursor: pointer;
}

.session-action.danger {
  border-color: rgba(248, 113, 113, 0.3);
  color: #ef4444;
}

.session-item:hover {
  transform: translateY(-1px);
  background: var(--ai-card);
  border-color: var(--ai-border);
}

.session-item.active {
  background: var(--ai-card-strong);
  border-color: var(--ai-border-strong);
}

.session-title {
  font-size: 12px;
  font-weight: 700;
  line-height: 1.35;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  padding-right: 64px;
  max-width: 100%;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 2px;
}

.theme-toggle,
.return-link {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  min-height: 40px;
  padding: 0 12px;
  border-radius: 14px;
  border: 1px solid var(--ai-border);
  background: var(--ai-card);
  color: var(--ai-text);
  text-decoration: none;
  font-size: 12px;
  font-weight: 700;
  box-shadow: var(--ai-card-shadow);
}

.theme-toggle {
  cursor: pointer;
  justify-content: flex-start;
}

.theme-toggle-icon,
.return-link-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: var(--ai-card-muted);
  color: var(--ai-accent);
  flex-shrink: 0;
}

.theme-toggle-icon svg,
.return-link-icon svg {
  width: 14px;
  height: 14px;
}

@media screen and (max-width: 860px) {
  .sidebar {
    width: 100%;
    padding: calc(14px + env(safe-area-inset-top)) 14px calc(16px + env(safe-area-inset-bottom));
    gap: 12px;
  }

  .profile-card {
    padding: 14px;
  }

  .session-actions {
    display: none;
  }

  .new-chat {
    min-height: 46px;
  }
}
</style>
