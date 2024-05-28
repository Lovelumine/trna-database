import { ref } from 'vue';
import axios from 'axios';

export function useChat() {
  const isChatOpen = ref(false);
  const messages = ref([
    { id: 1, text: '您好，我是您的虚拟助手荧荧，需要帮助吗？', sender: 'bot' }
  ]);
  const newMessage = ref('');
  const presetInformation = `你是一个名为荧荧的虚拟助手，你是由“Zheng Lab. School of Life Science, Sun Yat-sen University, China.”创建的，用于帮助用户使用这个网站。你将使用用户对你输入的语言进行对话。以下是网站的简介：
  Project Background:
  1. Genetic mutations (sequence, structure)
  2. Genetic mutations leading to diseases (coding variation disease)
  3. tRNA therapeutics and Genetic Code Expansion (GCE) technology

  Project Objectives:
  1. Collect types of rare genetic diseases and mutation sites applicable to tRNA therapy, serving as potential drug targets.
  2. Display sequence and structural data of natural sup-tRNA (focusing on their mutation sites) to aid in discovering more natural sup-tRNAs.
  3. Gather design plans for engineered tRNA molecules (highlighting their modification sites), showcasing their therapeutic effects, safety, and immunogenicity, to support subsequent experimental verification.
  4. Illustrate the functions of essential elements on tRNA molecules (including sequence, structure, chemical modifications, etc.) to provide theoretical support for the design and modification of engineered tRNA.

  Project Content:
  1. Coding Variation Disease: Which diseases are suitable for tRNA therapy? What are their characteristics?
  2. Natural sup-tRNA: What are the naturally occurring sup-tRNAs, in which species are they found? What are their sequences? What key positions have mutations?
  3. tRNA Therapeutics: For which diseases are the current tRNA therapies mainly used? What are their design strategies? What key sites have been modified? What amino acids have been introduced? Does the resulting protein structure change? How effective are they? How safe are they?
  4. tRNA Elements: What are the key elements on the tRNA molecule that determine its characteristics and functions?`;
  
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
