import axios from 'axios';

export async function fetchOpenAIResponse(apiKey: string, prompt: string) {
    try {
      const response = await axios.post(`${import.meta.env.VITE_OPENAI_API_BASE_URL}/chat/completions`, {
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 500,
        temperature: 0.7,
      }, {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
      });
  
      // 获取返回的内容
      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('OpenAI API 请求失败:', error);
      return null;
    }
  }
  