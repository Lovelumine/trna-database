<template>
    <div id="bot-container">
      <div id="bot-icon" @click="toggleChat">
        <img src="/bot-image.png" alt="Bot Icon" />
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
  
  <script lang="tsx">
  import { defineComponent, ref } from 'vue';
  
  export default defineComponent({
    name: 'BotComponent',
    setup() {
      const isChatOpen = ref(false);
      const messages = ref([
        { id: 1, text: '您好，我是您的虚拟助手，需要帮助吗？', sender: 'bot' }
      ]);
      const newMessage = ref('');
  
      const toggleChat = () => {
        isChatOpen.value = !isChatOpen.value;
      };
  
      const sendMessage = () => {
        if (newMessage.value.trim() !== '') {
          messages.value.push({ id: Date.now(), text: newMessage.value, sender: 'user' });
          newMessage.value = '';
          // Here you can add the logic to send the message to the backend and get a response
          setTimeout(() => {
            messages.value.push({ id: Date.now(), text: '这是机器人的回复', sender: 'bot' });
          }, 1000);
        }
      };
  
      return { isChatOpen, messages, newMessage, toggleChat, sendMessage };
    }
  });
  </script>
  