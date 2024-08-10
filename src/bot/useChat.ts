//src/bot/useChat.ts
import { ref } from 'vue';
import { systemInformation, projectBackground, projectObjectives, projectContent, QA } from './presetInformation';
import { modomicsnatural } from './modomicsnatural';

export function useChat() {
  const isChatOpen = ref(false);
  const messages = ref<Array<{ id: number; text: string; sender: string; image?: string }>>([
    { id: 1, text: 'Hello, I am your virtual assistant Yingying. How can I assist you today?', sender: 'bot' }
  ]);

  const newMessage = ref('');
  const newImage = ref(null);
  const imagePreview = ref('');

  const presetInformation = `
    ${systemInformation}
    ${projectBackground}
    ${projectObjectives}
    ${projectContent}
    ${QA}
    ${modomicsnatural}
  `;

  const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value;
  };

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
      newImage.value = null;
      imagePreview.value = '';

      const conversation = messages.value.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: [
          { type: "text", text: msg.text || '' },
          msg.image ? { type: "image_url", image_url: { url: msg.image } } : null
        ].filter(content => content !== null)
      }));

      conversation.unshift({
        role: 'system',
        content: [{ type: "text", text: presetInformation }]
      });

      console.log('Sending conversation:', conversation);

      try {
        const response = await fetch('/api/openai', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            messages: conversation,
            stream: true
          })
        });

        if (!response.body) {
          throw new Error('ReadableStream not supported in this environment.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let completeMessage = '';
        let buffer = ''; // 用于存储未完成的JSON数据
        const botMessageId = Date.now();

        // 首次添加一条空消息，用于更新
        messages.value.push({ id: botMessageId, text: '', sender: 'bot' });

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          let lines = buffer.split('\n');
          buffer = lines.pop() || ''; // 保留最后一行作为未完成部分

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.replace('data: ', '');
              if (jsonStr !== '[DONE]') {
                try {
                  const parsed = JSON.parse(jsonStr);
                  const content = parsed.choices[0]?.delta?.content;
                  if (content) {
                    completeMessage += content;
                    const botMessage = messages.value.find(msg => msg.id === botMessageId);
                    if (botMessage) {
                      botMessage.text = completeMessage.trim();
                    }
                  }
                } catch (error) {
                  console.error('Error parsing stream chunk:', error);
                }
              }
            }
          }
        }

        console.log('Stream ended');

      } catch (error) {
        console.error('Error communicating with OpenAI API:', error.message);
        messages.value.push({ id: Date.now(), text: 'Sorry, I could not process your request.', sender: 'bot' });
      }
    }
  };

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

  const triggerImageUpload = () => {
    document.getElementById('image-input').click();
  };

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
