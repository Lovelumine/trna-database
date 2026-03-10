//src/views/AIYingying/AIYingying.vue
<template>
  <div id="ai-app">
    <div class="assistant-shell">
      <button
        v-if="mobileNavOpen"
        class="mobile-nav-backdrop"
        type="button"
        aria-label="Close chat navigation"
        @click="closeMobileNav"
      ></button>

      <Sidebar
        class="assistant-sidebar"
        :class="{ 'mobile-open': mobileNavOpen }"
        :sessions="sessions"
        :activeId="activeConversationId"
        :noteAcknowledged="noteAcknowledged"
        :noteText="noteText"
        @session-selected="selectSession"
        @new-session="createNewConversation"
        @rename-session="renameSession"
        @delete-session="deleteSession"
        @open-note-modal="openNoteModal"
      />
      <div class="content-wrapper">
        <div class="mobile-topbar">
          <button
            class="mobile-nav-toggle"
            type="button"
            aria-label="Open chat navigation"
            @click="toggleMobileNav"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 7h16M4 12h16M4 17h10" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"></path>
            </svg>
          </button>
          <div class="mobile-topbar-copy">
            <span class="mobile-topbar-label">ENSURE Assistant</span>
            <strong>AI Yingying</strong>
          </div>
          <button class="mobile-note-button" type="button" @click="openNoteModal">
            {{ noteAcknowledged ? 'Usage note' : 'Review note' }}
          </button>
        </div>
        <div class="main-content">
          <ChatBox
            v-if="activeConversationId"
            :key="activeConversationId"
            :conversationId="activeConversationId"
            :apiKey="apiKey"
            :noteAcknowledged="noteAcknowledged"
            :noteText="noteText"
            :noteModalVisible="noteModalVisible"
            @conversation-updated="handleConversationUpdated"
            @acknowledge-note="acknowledgeNote"
            @close-note-modal="closeNoteModal"
            @open-note-modal="openNoteModal"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Sidebar from './AISidebar.vue';
import ChatBox from './ChatBox/ChatBox.vue';
import { warmChatSession } from '@/utils/useChat';

const sessionsStorageKey = 'ai_chat_sessions';
const noteAckStorageKey = 'ai_note_ack_global';
const noteTextValue = 'Note: AI-generated responses may be inaccurate. Please verify important information.';
const mobileBreakpoint = 860;

const createSessionId = () =>
  `chat_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

export default {
  name: 'App',
  components: {
    Sidebar,
    ChatBox
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const isShared = computed(() => route.query.shared === '1');

    const sessions = ref([]);
    const activeConversationId = ref('');
    const draftId = ref('');
    const noteAcknowledged = ref(false);
    const noteText = ref(noteTextValue);
    const noteModalVisible = ref(false);
    const mobileNavOpen = ref(false);

    const apiKey = computed(() => {
      if (isShared.value) return import.meta.env.VITE_API_KEY;
      return (
        import.meta.env.VITE_API_KEY_11 ||
        import.meta.env.VITE_API_KEY_DEFAULT ||
        import.meta.env.VITE_API_KEY
      );
    });

    const persistSessions = () => {
      localStorage.setItem(sessionsStorageKey, JSON.stringify(sessions.value));
    };

    const loadSessions = () => {
      try {
        const raw = localStorage.getItem(sessionsStorageKey);
        sessions.value = raw ? JSON.parse(raw) : [];
      } catch {
        sessions.value = [];
      }
    };

    const ensureSharedSession = () => {
      if (!isShared.value) return;
      const sharedId = 'floating-assistant';
      const exists = sessions.value.find(s => s.id === sharedId);
      if (!exists) {
        sessions.value.unshift({
          id: sharedId,
          title: 'AI Web Navigator',
          updatedAt: Date.now(),
          customTitle: true
        });
        persistSessions();
      }
      void warmChatSession(apiKey.value, sharedId);
      activeConversationId.value = sharedId;
    };

    const ensureSessionById = (id) => {
      if (!id) return;
      const exists = sessions.value.find(s => s.id === id);
      if (!exists) {
        sessions.value.unshift({
          id,
          title: 'New chat',
          updatedAt: Date.now(),
          customTitle: false
        });
        persistSessions();
      }
      void warmChatSession(apiKey.value, id);
      activeConversationId.value = id;
    };

    const createNewConversation = async () => {
      if (isShared.value) await router.replace({ path: '/AIYingying' });
      if (draftId.value && !sessions.value.some(s => s.id === draftId.value)) {
        void warmChatSession(apiKey.value, draftId.value);
        activeConversationId.value = draftId.value;
        mobileNavOpen.value = false;
        return;
      }
      const id = createSessionId();
      draftId.value = id;
      void warmChatSession(apiKey.value, id);
      activeConversationId.value = id;
      mobileNavOpen.value = false;
    };

    const selectSession = (id) => {
      void warmChatSession(apiKey.value, id);
      activeConversationId.value = id;
      mobileNavOpen.value = false;
    };

    const handleConversationUpdated = (meta) => {
      if (!meta?.id) return;
      const idx = sessions.value.findIndex(s => s.id === meta.id);
      const existing = idx >= 0 ? sessions.value[idx] : null;
      const shouldKeepTitle = existing?.customTitle || existing?.autoTitle;
      const incomingTitle = meta?.title || 'New chat';
      const isAiTitle = meta?.source === 'ai';
      const nextTitle = isAiTitle
        ? incomingTitle
        : (shouldKeepTitle ? existing.title : incomingTitle);
      const next = {
        id: meta.id,
        title: nextTitle,
        updatedAt: meta.updatedAt || Date.now(),
        customTitle: existing?.customTitle || false,
        autoTitle: isAiTitle || existing?.autoTitle || false
      };
      if (idx >= 0) sessions.value.splice(idx, 1);
      sessions.value.unshift(next);
      persistSessions();
      if (draftId.value === meta.id) {
        draftId.value = '';
      }
    };

    const renameSession = (id, title) => {
      const idx = sessions.value.findIndex(s => s.id === id);
      if (idx < 0) return;
      sessions.value[idx] = {
        ...sessions.value[idx],
        title,
        customTitle: true,
        autoTitle: false,
        updatedAt: Date.now()
      };
      persistSessions();
    };

    const deleteSession = (id) => {
      sessions.value = sessions.value.filter(s => s.id !== id);
      localStorage.removeItem(`ai_chat_session_${id}`);
      if (activeConversationId.value === id) {
        activeConversationId.value = sessions.value[0]?.id || '';
        if (!activeConversationId.value) {
          createNewConversation();
        }
      }
      persistSessions();
    };

    const closeMobileNav = () => {
      mobileNavOpen.value = false;
    };

    const toggleMobileNav = () => {
      mobileNavOpen.value = !mobileNavOpen.value;
    };

    const handleViewportResize = () => {
      if (window.innerWidth > mobileBreakpoint) {
        mobileNavOpen.value = false;
      }
    };

    onMounted(() => {
      loadSessions();
      noteAcknowledged.value = localStorage.getItem(noteAckStorageKey) === '1';
      noteModalVisible.value = !noteAcknowledged.value;
      const requestedId = typeof route.query.session === 'string' ? route.query.session : '';
      if (requestedId) {
        ensureSessionById(requestedId);
        return;
      }
      if (isShared.value) {
        ensureSharedSession();
        return;
      }
      if (!sessions.value.length) {
        createNewConversation();
      } else if (!activeConversationId.value) {
        activeConversationId.value = sessions.value[0].id;
        void warmChatSession(apiKey.value, activeConversationId.value);
      }
      window.addEventListener('resize', handleViewportResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleViewportResize);
    });

    const acknowledgeNote = () => {
      noteAcknowledged.value = true;
      localStorage.setItem(noteAckStorageKey, '1');
      noteModalVisible.value = false;
    };

    const openNoteModal = () => {
      noteModalVisible.value = true;
    };

    const closeNoteModal = () => {
      if (!noteAcknowledged.value) return;
      noteModalVisible.value = false;
    };

    return {
      sessions,
      activeConversationId,
      draftId,
      apiKey,
      noteAcknowledged,
      noteText,
      noteModalVisible,
      mobileNavOpen,
      selectSession,
      createNewConversation,
      handleConversationUpdated,
      renameSession,
      deleteSession,
      acknowledgeNote,
      openNoteModal,
      closeNoteModal,
      closeMobileNav,
      toggleMobileNav
    };
  }
};
</script>

<style>
#ai-app {
  --ai-bg: #edf3fb;
  --ai-shell: #f8fbff;
  --ai-sidebar: #f3f7fc;
  --ai-panel: #fbfdff;
  --ai-card: #ffffff;
  --ai-card-muted: #f3f7fc;
  --ai-card-strong: #ebf2ff;
  --ai-border: rgba(15, 23, 42, 0.08);
  --ai-border-strong: rgba(47, 111, 237, 0.18);
  --ai-text: #0f172a;
  --ai-muted: #5f6b7c;
  --ai-accent: #2f6fed;
  --ai-accent-strong: #224ebf;
  --ai-accent-soft: rgba(47, 111, 237, 0.12);
  --ai-warning-soft: #fff4d7;
  --ai-warning-border: rgba(245, 158, 11, 0.24);
  --ai-warning-text: #8f5d12;
  --ai-shell-shadow: 0 24px 54px rgba(15, 23, 42, 0.08);
  --ai-card-shadow: 0 14px 28px rgba(15, 23, 42, 0.05);
  --ai-user-start: #dfeafe;
  --ai-user-end: #cfdefd;
  --ai-user-text: #17366d;
  --ai-user-shadow: 0 10px 24px rgba(47, 111, 237, 0.12);
  --ai-user-action-bg: rgba(255, 255, 255, 0.68);
  --ai-user-action-border: rgba(23, 54, 109, 0.12);
  display: flex;
  height: 100vh;
  height: 100dvh;
  min-height: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
  background:
    radial-gradient(36rem 20rem at top left, rgba(47, 111, 237, 0.1), transparent 62%),
    radial-gradient(32rem 18rem at right bottom, rgba(16, 185, 129, 0.08), transparent 66%),
    linear-gradient(180deg, #f3f7fc 0%, var(--ai-bg) 100%);
}

.assistant-shell {
  display: flex;
  flex: 1;
  min-width: 0;
  min-height: 0;
  position: relative;
  overflow: hidden;
  border-radius: 0;
  border: none;
  background: var(--ai-shell);
  box-shadow: none;
}

.assistant-sidebar {
  flex-shrink: 0;
}

.mobile-nav-backdrop,
.mobile-topbar {
  display: none;
}

.content-wrapper {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
  overflow: hidden;
  background: var(--ai-panel);
  border-left: 1px solid var(--ai-border);
}

.main-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 0;
}

@media (max-width: 860px) {
  #ai-app {
    height: 100vh;
    height: 100dvh;
    padding: 0;
  }

  .mobile-nav-backdrop {
    display: block;
    position: absolute;
    inset: 0;
    z-index: 21;
    border: none;
    background: rgba(15, 23, 42, 0.36);
    backdrop-filter: blur(4px);
  }

  .mobile-topbar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: calc(10px + env(safe-area-inset-top)) 14px 10px;
    background: linear-gradient(180deg, rgba(248, 251, 255, 0.96), rgba(248, 251, 255, 0.88));
    border-bottom: 1px solid var(--ai-border);
  }

  .mobile-nav-toggle,
  .mobile-note-button {
    min-height: 38px;
    border-radius: 12px;
    border: 1px solid var(--ai-border);
    background: var(--ai-card);
    color: var(--ai-text);
    font-size: 12px;
    font-weight: 700;
  }

  .mobile-nav-toggle {
    width: 40px;
    min-width: 40px;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-nav-toggle svg {
    width: 18px;
    height: 18px;
  }

  .mobile-topbar-copy {
    display: flex;
    flex-direction: column;
    min-width: 0;
    flex: 1;
  }

  .mobile-topbar-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ai-accent);
  }

  .mobile-topbar-copy strong {
    font-size: 15px;
    color: var(--ai-text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .mobile-note-button {
    padding: 0 12px;
    white-space: nowrap;
  }

  .assistant-sidebar {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    width: min(86vw, 330px);
    z-index: 22;
    transform: translateX(-104%);
    transition: transform 0.24s ease;
    box-shadow: 0 22px 48px rgba(15, 23, 42, 0.18);
  }

  .assistant-sidebar.mobile-open {
    transform: translateX(0);
  }

  .content-wrapper {
    border-left: none;
  }
}

:root[data-theme="dark"] #ai-app,
html.dark #ai-app {
  --ai-bg: #09111d;
  --ai-shell: #0d1522;
  --ai-sidebar: #0c1522;
  --ai-panel: #0f1828;
  --ai-card: #111c2d;
  --ai-card-muted: #0f1928;
  --ai-card-strong: #162338;
  --ai-border: rgba(148, 163, 184, 0.14);
  --ai-border-strong: rgba(106, 168, 255, 0.24);
  --ai-text: #edf3ff;
  --ai-muted: #9aa9c0;
  --ai-accent: #6aa8ff;
  --ai-accent-strong: #3c7eff;
  --ai-accent-soft: rgba(106, 168, 255, 0.14);
  --ai-warning-soft: #2c2212;
  --ai-warning-border: rgba(245, 158, 11, 0.24);
  --ai-warning-text: #f2c46b;
  --ai-shell-shadow: 0 28px 60px rgba(0, 0, 0, 0.34);
  --ai-card-shadow: 0 16px 30px rgba(0, 0, 0, 0.18);
  --ai-user-start: #3f84ff;
  --ai-user-end: #2661dc;
  --ai-user-text: #ffffff;
  --ai-user-shadow: 0 14px 28px rgba(34, 78, 191, 0.22);
  --ai-user-action-bg: rgba(255, 255, 255, 0.14);
  --ai-user-action-border: rgba(255, 255, 255, 0.2);
  background:
    radial-gradient(40rem 24rem at top left, rgba(60, 126, 255, 0.16), transparent 62%),
    radial-gradient(30rem 16rem at right bottom, rgba(34, 197, 94, 0.08), transparent 68%),
    linear-gradient(180deg, #07101a 0%, var(--ai-bg) 100%);
}

:root[data-theme="dark"] .assistant-shell,
html.dark .assistant-shell {
  box-shadow: none;
}
</style>
  
