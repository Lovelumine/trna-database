<template>
  <div id="bot-container" ref="element" @mousedown="startDrag">
    <div id="bot-icon" @click="toggleChat">
      <img src="/bot-image.png" alt="Bot Icon" @dragstart.prevent />
    </div>
    <div id="chat-box" v-if="isChatOpen">
      <div id="chat-header">
        <span>Smart Web Navigator</span>
        <button @click="toggleChat" class="close-button">
          <el-icon><close /></el-icon>
        </button>
      </div>
      <div id="chat-content">
        <div v-for="message in messages" :key="message.id" :class="message.sender">
          <img v-if="message.sender === 'bot'" src="/bot-image.png" alt="Bot Avatar" class="avatar"/>
          <img v-if="message.sender === 'user'" src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png" alt="User Avatar" class="avatar"/>
          <div class="message">
            {{ message.text }}
          </div>
        </div>
      </div>
      <div id="chat-input-container">
        <input
          id="chat-input"
          v-model="newMessage"
          @keypress.enter="sendMessage"
          placeholder="Type a message..."
        />
        <button @click="sendMessage" id="send-button">Send</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import { useDraggable } from './Draggable';
import { useChat } from './useChat';
import { ElIcon } from 'element-plus';
import { Close } from '@element-plus/icons-vue';

export default defineComponent({
  name: 'BotComponent',
  components: {
    ElIcon,
    Close
  },
  setup() {
    const { element, startDrag } = useDraggable();
    const { isChatOpen, messages, newMessage, toggleChat, sendMessage } = useChat();

    // Debugging the state of the chat visibility
    watch(isChatOpen, (newVal) => {
      console.log("Chat Open State Changed:", newVal);
    });

    // Debugging message updates
    watch(messages, (newVal) => {
      console.log("Messages Updated:", newVal);
    }, { deep: true });

    return { element, startDrag, isChatOpen, messages, newMessage, toggleChat, sendMessage };
  }
});
</script>


