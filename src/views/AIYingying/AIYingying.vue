//src/views/AIYingying/AIYingying.vue
<template>
  <div id="ai-app">
    <Sidebar
      :sessions="sessions"
      :activeId="activeConversationId"
      :noteAcknowledged="noteAcknowledged"
      :noteText="noteText"
      @session-selected="selectSession"
      @new-session="createNewConversation"
      @rename-session="renameSession"
      @delete-session="deleteSession"
      @acknowledge-note="acknowledgeNote"
    />
    <div class="content-wrapper">
      <div class="main-content">
        <ChatBox
          v-if="activeConversationId"
          :key="activeConversationId"
          :conversationId="activeConversationId"
          :apiKey="apiKey"
          :noteAcknowledged="noteAcknowledged"
          @conversation-updated="handleConversationUpdated"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Sidebar from './AISidebar.vue';
import ChatBox from './ChatBox/ChatBox.vue';

const sessionsStorageKey = 'ai_chat_sessions';
const noteAckStorageKey = 'ai_note_ack_global';
const noteTextValue = 'Note: AI-generated responses may be inaccurate. Please verify important information.';

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
      activeConversationId.value = id;
    };

    const createNewConversation = async () => {
      if (isShared.value) await router.replace({ path: '/AIYingying' });
      if (draftId.value && !sessions.value.some(s => s.id === draftId.value)) {
        activeConversationId.value = draftId.value;
        return;
      }
      const id = createSessionId();
      draftId.value = id;
      activeConversationId.value = id;
    };

    const selectSession = (id) => {
      activeConversationId.value = id;
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

    onMounted(() => {
      loadSessions();
      noteAcknowledged.value = localStorage.getItem(noteAckStorageKey) === '1';
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
      }
    });

    const acknowledgeNote = () => {
      noteAcknowledged.value = true;
      localStorage.setItem(noteAckStorageKey, '1');
    };

    return {
      sessions,
      activeConversationId,
      draftId,
      apiKey,
      noteAcknowledged,
      noteText,
      selectSession,
      createNewConversation,
      handleConversationUpdated,
      renameSession,
      deleteSession,
      acknowledgeNote
    };
  }
};
</script>

<style>
#ai-app {
  display: flex;
  height: calc(100vh - 80px);
  gap: 0;
  padding: 0;
  background: var(--app-bg);
}

.content-wrapper {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
  overflow: hidden;
  border-left: 1px solid var(--app-border);
}

.main-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 0;
}
</style>
  
