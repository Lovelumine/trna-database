//src/views/AIYingying/ChatBox/chatService.ts
export interface Message {
  name: string;
  avatar: string;
  text: string;
}

export class ChatService {
  private messages: Message[] = [
    {
      name: 'YingYing',
      avatar:
        'https://framerusercontent.com/images/p0mVMX1aJictMR1RM9fE1PrTrRQ.png',
      text: 'Hello, I am your virtual assistant YingYing. How can I assist you today?',
    },
  ];

  getMessages() {
    return this.messages;
  }

  addUserMessage(text: string) {
    this.messages.push({
      name: 'You',
      avatar: 'https://framerusercontent.com/images/JnbQ2qAMPu3VRXkbzDhwoMnHpk.png',
      text,
    });
  }

  async addAiResponse(menuId: number, sceneId: number, onProgress: (message: Message) => void) {
    const menuResponses = {
      1: 'Intelligent Document',
      2: '灵感激发',
      3: '多语言翻译',
      4: '续写故事',
      5: '小说朗读',
      6: '会话历史记录',
    };
    const sceneResponses = {
      1: 'AY-GLM4.0',
      2: '傲娇',
    };
    const menuResponse = menuResponses[menuId] || '菜单';
    const sceneResponse = sceneResponses[sceneId] || '性格';
    const response = `你选择了${menuResponse}，模型是${sceneResponse}。`;

    const message: Message = {
      name: '荧荧',
      avatar: 'https://framerusercontent.com/images/p0mVMX1aJictMR1RM9fE1PrTrRQ.png',
      text: '',
    };

    this.messages.push(message);

    // 增加延迟开始回复
    await new Promise(resolve => setTimeout(resolve, 1000)); // 延迟1秒

    for (const char of response) {
      await new Promise(resolve => setTimeout(resolve, 100)); // 模拟逐字回复的延迟
      message.text += char;
      onProgress(message);
    }
  }

  resetMessages(sceneId: number = 1) {
    const sceneResponses = {
      1: '默认',
      2: '傲娇',
    };

    const sceneResponse = sceneResponses[sceneId] || '默认';

    const initialText = sceneResponse === '傲娇' 
      ? '哼，欢迎使用智能助手荧荧。有什么问题就快问吧，别浪费我的时间。'
      : 'Hello, I am your virtual assistant YingYing. How can I assist you today?';

    this.messages = [
      {
        name: 'YingYing',
        avatar:
          'https://framerusercontent.com/images/p0mVMX1aJictMR1RM9fE1PrTrRQ.png',
        text: initialText,
      },
    ];
  }
}
