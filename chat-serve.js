import express from 'express';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';

// 加载 .env 文件中的环境变量
dotenv.config();

const app = express();
const port = 3001; // 设置一个不同于前端的端口

app.use(cors());
app.use(express.json());

const OPENAI_API_KEY = process.env.VITE_OPENAI_API_KEY;

// 打印 API 密钥以确认读取成功（仅用于调试）
console.log('OpenAI API Key:', OPENAI_API_KEY);

app.post('/api/openai', async (req, res) => {
  console.log('Received request body:', req.body); // 增加控制台输出，查看请求体
  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: req.body.messages,
        max_tokens: 150,
      },
      {
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
          'Content-Type': 'application/json',
        }
      }
    );
    res.json(response.data);
  } catch (error) {
    console.error('Error communicating with OpenAI API:', error.response ? error.response.data : error.message);
    res.status(500).json({ error: 'Error communicating with OpenAI API' });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
