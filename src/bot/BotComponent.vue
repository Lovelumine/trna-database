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
  import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue';
  
  export default defineComponent({
    name: 'BotComponent',
    setup() {
      const isChatOpen = ref(false);
      const messages = ref([
        { id: 1, text: '您好，我是您的虚拟助手，需要帮助吗？', sender: 'bot' }
      ]);
      const newMessage = ref('');
      const botContainer = ref<HTMLElement | null>(null);
      let offsetX = 0;
      let offsetY = 0;
      let isDragging = false;
  
      const toggleChat = () => {
        isChatOpen.value = !isChatOpen.value;
      };
  
      const sendMessage = () => {
        if (newMessage.value.trim() !== '') {
          messages.value.push({ id: Date.now(), text: newMessage.value, sender: 'user' });
          newMessage.value = '';
          // 这里可以添加逻辑，将消息发送到后台并获取回复
          setTimeout(() => {
            messages.value.push({ id: Date.now(), text: '这是机器人的回复', sender: 'bot' });
          }, 1000);
        }
      };
  
      const startDrag = (event: MouseEvent) => {
        if (botContainer.value) {
          console.log('Drag started');
          isDragging = true;
          offsetX = event.clientX - botContainer.value.getBoundingClientRect().left;
          offsetY = event.clientY - botContainer.value.getBoundingClientRect().top;
          document.addEventListener('mousemove', onDrag);
          document.addEventListener('mouseup', stopDrag);
        }
      };
  
      const onDrag = (event: MouseEvent) => {
        if (isDragging && botContainer.value) {
          console.log(`Dragging at (${event.clientX}, ${event.clientY})`);
          botContainer.value.style.left = `${event.clientX - offsetX}px`;
          botContainer.value.style.top = `${event.clientY - offsetY}px`;
        }
      };
  
      const stopDrag = () => {
        if (isDragging) {
          console.log('Drag stopped');
          isDragging = false;
          document.removeEventListener('mousemove', onDrag);
          document.removeEventListener('mouseup', stopDrag);
        }
      };
  
      onMounted(() => {
        document.addEventListener('mouseup', stopDrag);
      });
  
      onBeforeUnmount(() => {
        document.removeEventListener('mouseup', stopDrag);
        document.removeEventListener('mousemove', onDrag);
      });
  
      return { isChatOpen, messages, newMessage, toggleChat, sendMessage, botContainer, startDrag };
    }
  });
  </script>
  