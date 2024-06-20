import { ref } from 'vue';
import axios from 'axios';
import { systemInformation, projectBackground, projectObjectives, projectContent } from './presetInformation';
import {modomicsnatural} from './modomicsnatural'


export function useChat() {


  const isChatOpen = ref(false);
const messages = ref<Array<{ id: number; text: string; sender: string; image?: string }>>([
  { id: 1, text: 'Hello, I am your virtual assistant Yingying. How can I assist you today?', sender: 'bot' }
]);

  const newMessage = ref('');
  const newImage = ref(null); // 新增，存储上传的图片
  const imagePreview = ref(''); // 新增，存储图片预览的 URL

  const presetInformation = `
    ${systemInformation}
    ${projectBackground}
    ${projectObjectives}
    ${projectContent}
    ${modomicsnatural}
  `;

  // 切换聊天窗口的显示状态
  const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value;
  };

  // 发送消息
  const sendMessage = async () => {
    if (newMessage.value.trim() !== '' || newImage.value) {
      const textContent = newMessage.value.trim();
      const imageBase64 = newImage.value ? await toBase64(newImage.value) : null;

      messages.value.push({
        id: Date.now(),
        sender: 'user',
        text: textContent,
        image: imageBase64 ? `data:image/jpeg;base64,${imageBase64}` : null
      });
      newMessage.value = '';
      newImage.value = null; // 发送后清空图片
      imagePreview.value = ''; // 清空预览

      // 准备对话上下文
      const conversation = messages.value.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: [
          { type: "text", text: msg.text || '' },
          msg.image ? { type: "image_url", image_url: { url: msg.image } } : null
        ].filter(content => content !== null)
      }));

      // 确保所有消息的 content 字段都是字符串数组并且不是空
      conversation.forEach(msg => {
        msg.content.forEach(contentItem => {
          if (typeof contentItem.text !== 'string' || contentItem.text.trim() === '') {
            contentItem.text = '无内容'; // 使用默认值替换空内容
          }
        });
      });

      // 在对话上下文中添加预设信息
      conversation.unshift({
        role: 'system',
        content: [{ type: "text", text: presetInformation }]
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

        // 检查 API 响应，确保 content 存在
        const botMessage = response.data.choices[0].message.content;
        if (typeof botMessage === 'string') {
          messages.value.push({ id: Date.now(), text: botMessage.trim(), sender: 'bot' });
        } else {
          messages.value.push({ id: Date.now(), text: '抱歉，我无法处理您的请求。', sender: 'bot' });
        }
      } catch (error) {
        console.error('Error communicating with OpenAI API:', error.response ? error.response.data : error.message);
        messages.value.push({ id: Date.now(), text: '抱歉，我无法处理您的请求。', sender: 'bot' });
      }
    }
  };

// 将图片转换为 Base64 编码
const toBase64 = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = () => {
    const result = reader.result;
    if (typeof result === 'string') {
      resolve(result.split(',')[1]);
    } else {
      reject(new Error('FileReader result is not a string'));
    }
  };
  reader.onerror = error => reject(error);
});


  // 触发图片上传
  const triggerImageUpload = () => {
    document.getElementById('image-input').click();
  };

  // 预览图片
  const previewImage = (event: Event) => {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    if (file) {
      newImage.value = file;
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          imagePreview.value = reader.result;
        }
      };
    }
  };

  return { isChatOpen, messages, newMessage, newImage, imagePreview, toggleChat, sendMessage, triggerImageUpload, previewImage };
}
