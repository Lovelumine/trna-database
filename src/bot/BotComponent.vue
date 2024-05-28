<template>
    <div id="bot-container" ref="botContainer" @mousedown="startDrag">
      <div id="bot-icon" @click="toggleChat">
        <img src="/bot-image.png" alt="Bot Icon" @dragstart.prevent />
      </div>
      <div id="chat-box" v-if="isChatOpen">
        <div id="chat-header">
          <span>Yingying</span>
          <button @click="toggleChat">关闭</button>
        </div>
        <div id="chat-content">
          <div v-for="message in messages" :key="message.id" :class="message.sender">
            {{ message.text }}
          </div>
        </div>
        <input
          id="chat-input"
          v-model="newMessage"
          @keypress.enter="sendMessage"
          placeholder="输入消息..."
        />
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import { useDraggable } from './Draggable';
  import { useChat } from './useChat';
  
  export default defineComponent({
    name: 'BotComponent',
    setup() {
      const { element, startDrag } = useDraggable();
      const { isChatOpen, messages, newMessage, toggleChat, sendMessage } = useChat();
      return { element, startDrag, isChatOpen, messages, newMessage, toggleChat, sendMessage };
    }
  });
  </script>
  
  