// useChat.ts
import { ref } from 'vue';

export function useChat() {
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
      setTimeout(() => {
        messages.value.push({ id: Date.now(), text: '这是机器人的回复', sender: 'bot' });
      }, 1000);
    }
  };

  return { isChatOpen, messages, newMessage, toggleChat, sendMessage };
}
