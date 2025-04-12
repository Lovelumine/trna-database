import { ref } from 'vue';

export function useChat(apiKey: string) { 
  const isChatOpen = ref(false);
  const messages = ref<Array<{ id: number; text: string; sender: string; image?: string }>>([
    { id: 1, text: 'Hello, I am your virtual assistant YingYing. How can I assist you today?', sender: 'bot' }
  ]);

  const newMessage = ref('');
  const newImage = ref(null);
  const imagePreview = ref('');

  const apiBaseURL = '/api';
  let applicationId = '';
  let chatId = '';

  const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value;
  };

  const fetchApplicationProfile = async () => {
    try {
      const response = await fetch(`${apiBaseURL}/application/profile`, {
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'AUTHORIZATION': apiKey, 
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      applicationId = data.data.id;
      console.log('Application ID:', applicationId);
    } catch (error) {
      console.error('Error fetching application profile:', error);
    }
  };

  const openChatSession = async () => {
    try {
      const response = await fetch(`${apiBaseURL}/application/${applicationId}/chat/open`, {
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'AUTHORIZATION': apiKey, 
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      chatId = data.data;
      console.log('Chat ID:', chatId);
    } catch (error) {
      console.error('Error opening chat session:', error);
    }
  };

  const sendMessage = async () => {
    if (newMessage.value.trim() !== '' || newImage.value) {
      if (!chatId) {
        console.error('Chat ID is not available. Unable to send message.');
        return;
      }

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

      console.log('Sending message:', textContent);

      try {
        const response = await fetch(`${apiBaseURL}/application/chat_message/${chatId}`, {
          method: 'POST',
          headers: {
            'accept': 'application/json',
            'AUTHORIZATION': apiKey,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: textContent,
            re_chat: false,
            stream: true
          })
        });

        if (!response.body) {
          throw new Error('ReadableStream not supported in this environment.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let completeMessage = '';
        let buffer = '';
        const botMessageId = Date.now();

        // Add an empty message to be updated later
        messages.value.push({ id: botMessageId, text: '', sender: 'bot' });

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          let lines = buffer.split('\n');
          buffer = lines.pop() || ''; 

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.replace('data: ', '');
              if (jsonStr !== '[DONE]') {
                try {
                  const parsed = JSON.parse(jsonStr);
                  const content = parsed.content;
                  if (content) {
                    completeMessage += content;
                    const botMessage = messages.value.find(msg => msg.id === botMessageId);
                    if (botMessage) {
                      botMessage.text = completeMessage.trim();
                    }
                    console.log('Received chunk:', content);
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
        console.error('Error communicating with API:', error.message);
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

  const initializeChat = async () => {
    await fetchApplicationProfile();
    await openChatSession();
  };

  const resetChat = async (newApiKey: string) => {
    apiKey = newApiKey; 
    messages.value = []; 
    await fetchApplicationProfile(); 
    await openChatSession(); 
    messages.value.push({ id: 1, text: 'Hello, I am your virtual assistant YingYing. How can I assist you today?', sender: 'bot' });
  };

  initializeChat();

  return { 
    isChatOpen, 
    messages, 
    newMessage, 
    newImage, 
    imagePreview, 
    toggleChat, 
    sendMessage, 
    triggerImageUpload, 
    previewImage,
    resetChat 
  };
}

