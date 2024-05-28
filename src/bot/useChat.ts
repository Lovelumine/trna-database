import { ref } from 'vue';
import axios from 'axios';

export function useChat() {
  const isChatOpen = ref(false);
  const messages = ref([
    { id: 1, text: '您好，我是您的虚拟助手荧荧，需要帮助吗？', sender: 'bot' }
  ]);
  const newMessage = ref('');
  const presetInformation = `你是一个名为荧荧的虚拟助手，你是由开发团队创建的，用于帮助用户使用这个网站。`; // 预设信息

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
