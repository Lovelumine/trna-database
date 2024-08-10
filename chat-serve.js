import express from 'express';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';
import bodyParser from 'body-parser';
import winston from 'winston';

// 加载 .env 文件中的环境变量
dotenv.config();

const app = express();
const port = 3001; // 设置一个不同于前端的端口

app.use(cors());
app.use(express.json({ limit: '50mb' })); // 设置请求体大小限制
app.use(bodyParser.json({ limit: '50mb' })); // 设置请求体大小限制
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

const OPENAI_API_KEY = process.env.VITE_OPENAI_API_KEY;
const API_BASE_URL = 'https://lqapi.lqqq.ltd/v1'; // 统一使用这个URL

// 创建日志记录器
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.printf(info => `${info.timestamp} ${info.level}: ${info.message}`)
  ),
  transports: [
    new winston.transports.File({ filename: 'combined.log' }), // 保存所有日志
    new winston.transports.File({ filename: 'error.log', level: 'error' }) // 仅保存错误日志
  ],
});

// 打印 API 密钥以确认读取成功（仅用于调试）
logger.info('OpenAI API Key: ' + OPENAI_API_KEY);
logger.info('API Base URL: ' + API_BASE_URL);

// 处理文本与图片请求，支持流式传输
app.post('/api/openai', async (req, res) => {
  logger.info('Received request body: ' + JSON.stringify(req.body)); // 增加控制台输出，查看请求体
  try {
    const response = await axios({
      method: 'post',
      url: `${API_BASE_URL}/chat/completions`,
      data: {
        model: 'gpt-4o',
        messages: req.body.messages,
        max_tokens: 1000,
        stream: true, // 启用流式传输
      },
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      responseType: 'stream' // 设置响应类型为流
    });

    // 直接将流输出到响应中
    response.data.pipe(res);

    response.data.on('end', () => {
      logger.info('Stream ended');
    });
  } catch (error) {
    logger.error('Error communicating with OpenAI API: ' + (error.response ? JSON.stringify(error.response.data) : error.message));
    res.status(500).json({ error: 'Error communicating with OpenAI API' });
  }
});

app.listen(port, () => {
  logger.info(`Server running at http://localhost:${port}`);
});
