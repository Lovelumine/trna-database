import express from 'express';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';
import multer from 'multer';
import fs from 'fs';
import FormData from 'form-data';
import bodyParser from 'body-parser';

// 加载 .env 文件中的环境变量
dotenv.config();

const app = express();
const port = 3001; // 设置一个不同于前端的端口

app.use(cors());
app.use(express.json({ limit: '50mb' })); // 设置请求体大小限制
app.use(bodyParser.json({ limit: '50mb' })); // 设置请求体大小限制
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

const OPENAI_API_KEY = process.env.VITE_OPENAI_API_KEY;
const API_BASE_URL = 'https://api.lqqq.ltd/v1'; // 统一使用这个URL


// 打印 API 密钥以确认读取成功（仅用于调试）
console.log('OpenAI API Key:', OPENAI_API_KEY);
console.log('API Base URL:', API_BASE_URL);

// 处理文本与图片请求
app.post('/api/openai', async (req, res) => {
  console.log('Received request body:', req.body); // 增加控制台输出，查看请求体
  try {
    const response = await axios.post(
      `${API_BASE_URL}/chat/completions`,
      {
        model: 'gpt-4',
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



// 处理图片生成请求
app.post('/api/openai/image-generation', async (req, res) => {
  const data = {
    model: "dall-e-3",
    prompt: req.body.prompt, // 使用请求体中的 prompt
    n: req.body.n || 1,
    size: req.body.size || "1024x1024"
  };

  const config = {
    method: 'post',
    url: `${API_BASE_URL}/images/generations`,
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
      'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
      'Content-Type': 'application/json'
    },
    data: data
  };

  try {
    const response = await axios(config);
    res.json(response.data);
  } catch (error) {
    console.error('Error communicating with OpenAI API:', error.response ? error.response.data : error.message);
    res.status(500).json({ error: 'Error communicating with OpenAI API' });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
