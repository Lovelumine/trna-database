import { ref } from 'vue';
import axios from 'axios';
import { systemInformation, projectBackground, projectObjectives, projectContent } from './presetInformation.ts';

export function useChat() {
  const isChatOpen = ref(false);
  const messages = ref([
    { id: 1, text: 'Hello, I am your virtual assistant Yingying. How can I assist you today?', sender: 'bot' }
  ]);
  const newMessage = ref('');

  const presetInformation = `
    ${systemInformation}
    ${projectBackground}
    ${projectObjectives}
    ${projectContent}
  `;

  const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value;
  };

  const sendMessage = async () => {
    if (newMessage.value.trim() !== '') {
      const userMessage = newMessage.value.trim();
      messages.value.push({ id: Date.now(), text: userMessage, sender: 'user' });
      newMessage.value = '';

      // 准备对话上下文
      const conversation = messages.value.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text || ''
      }));

      // 确保所有消息的 content 字段都是字符串并且不是空
      conversation.forEach(msg => {
        if (typeof msg.content !== 'string' || msg.content.trim() === '') {
          msg.content = '无内容'; // 使用默认值替换空内容
        }
      });

      // 在对话上下文中添加预设信息
      conversation.unshift({
        role: 'system',
        content: presetInformation
      });

      console.log('Sending conversation:', conversation); // 调试信息

      // 使用 OpenAI 生成回答
      try {
        const response = await axios.post(
          'https://op.lovelumine.com/api/openai', // 代理服务器的地址
          {
            messages: conversation
          }
        );
        messages.value.push({ id: Date.now(), text: response.data.choices[0].message.content.trim(), sender: 'bot' });
      } catch (error) {
        console.error('Error communicating with OpenAI API:', error.response ? error.response.data : error.message);
        messages.value.push({ id: Date.now(), text: '抱歉，我无法处理您的请求。', sender: 'bot' });
      }
    }
  };

  return { isChatOpen, messages, newMessage, toggleChat, sendMessage };
}
