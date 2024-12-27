<template>
    <div class="video-summary">
      <h3>视频 AI 总结</h3>
  
      <!-- 分页导航栏 -->
      <div class="pagination">
        <button
          v-for="(tab, index) in tabs"
          :key="index"
          @click="currentTab = tab"
          :class="{ active: currentTab === tab }"
        >
          {{ tab }}
        </button>
      </div>
  
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>AI分析中...</p>
      </div>
  
      <div v-else>
        <!-- 概览部分 -->
        <div v-if="currentTab === '概览'" class="content">
          <h4>概览</h4>
          <p v-if="summary">{{ summary }}</p>
          <p v-else>未能生成概览</p>
        </div>
  
        <!-- 要点部分 -->
        <div v-if="currentTab === '要点'" class="content">
          <h4>要点</h4>
          <ul v-if="keyPoints.length">
            <li v-for="(point, index) in keyPoints" :key="index">
              <a href="#" @click.prevent="seekTo(point.time)">{{ point.time }}</a>
              {{ point.emoji }} {{ point.key }}
            </li>
          </ul>
          <p v-else>未能生成要点</p>
        </div>
  
        <!-- 问题部分 -->
        <div v-if="currentTab === '问题'" class="content">
          <h4>问题</h4>
          <ul v-if="questions.length">
            <li v-for="(qa, index) in questions" :key="index">
              <strong>Q: {{ qa.question }}</strong>
              <p>A: {{ qa.answer }}</p>
            </li>
          </ul>
          <p v-else>未能生成问题</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue';
  import { fetchOpenAIResponse } from './useOpenAI';
  
  // 定义组件 props
  const props = defineProps({
    subtitles: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    language: {
      type: String,
      default: '中文',
    }
  });
  
  // 定义状态变量
  const loading = ref(true);
  const summary = ref('');
  const keyPoints = ref([]);
  const questions = ref([]);
  const currentTab = ref('概览'); // 当前显示的分页
  const tabs = ['概览', '要点', '问题']; // 分页选项
  
  // 加载 .srt 文件内容
  const loadSrtContent = async () => {
    try {
      const response = await fetch(props.subtitles);
      if (!response.ok) {
        throw new Error(`Failed to load subtitles: ${response.statusText}`);
      }
      return await response.text();
    } catch (error) {
      console.error('Error loading SRT file:', error);
      return '';
    }
  };
  
  const generateSummary = async () => {
    loading.value = true;
  
    // 加载 .srt 文件内容
    const subtitlesContent = await loadSrtContent();
  
    const summaryPrompt = `
      You are a helpful assistant that summarize video subtitle.
      Summarize in language '${props.language}'.
      Answer in markdown json format.

            example output format:
      {
       "内容概述": "简要的内容概述。",
       "summary": "简要的总结。"
       }
       
      End of response.
  
      The video's title: '''${props.title}'''.
      The video's subtitles:


  
      '''
      ${subtitlesContent}
      '''
    `;
  
    const keyPointsPrompt = `
      You are a helpful assistant that summarize key points of video subtitle.
      Summarize 3 to 8 brief key points in language '${props.language}'.
      Answer in markdown json format.
      The emoji should be related to the key point and 1 char length.
  
      example output format:
  
      [
        {
          "time": "03:00",
          "emoji": "👍",
          "key": "key point 1"
        },
        {
          "time": "10:05",
          "emoji": "😊",
          "key": "key point 2"
        }
      ]
  
      The video's title: '''${props.title}'''.
      The video's subtitles:
  
      '''
      ${subtitlesContent}
      '''
    `;
  
    const questionsPrompt = `
      You are a helpful assistant that skilled at extracting questions from video subtitle.
      Accurately extract key questions and their corresponding answers from the video subtitles based on the actual content provided.
      Answer in language '${props.language}'.
      Format the output in markdown json format.

      example output format:
      {
      "questions": [
      {
      "question": "问题1？",
      "answer": "答案1。"
    },
    {
      "question": "问题2？",
      "answer": "答案2。"
    }
  ]
}
  End of response.
  
      The video's title: '''${props.title}'''.
      The video's subtitles:
  
      '''
      ${subtitlesContent}
      '''
    `;
  
    try {
      const apiKey = import.meta.env.VITE_OPENAI_API_KEY;
  
      // 获取概览
      const summaryResponse = await fetchOpenAIResponse(apiKey, summaryPrompt);
      const summaryJson = parseOpenAIResponse(summaryResponse);
      summary.value = summaryJson?.摘要 || summaryJson?.summary || summaryJson?.总结 || "未能生成摘要";
  
      // 获取要点
      const keyPointsResponse = await fetchOpenAIResponse(apiKey, keyPointsPrompt);
      keyPoints.value = parseOpenAIResponse(keyPointsResponse) || [];
  
      // 获取问题
      const questionsResponse = await fetchOpenAIResponse(apiKey, questionsPrompt);
      const parsedQuestions = parseOpenAIResponse(questionsResponse);
      if (parsedQuestions && parsedQuestions.questions) {
        questions.value = parsedQuestions.questions;
      }
  
    } catch (error) {
      console.error('生成总结时发生错误:', error);
    } finally {
      loading.value = false;
    }
  };
  
  // 解析 OpenAI 返回的数据
  function parseOpenAIResponse(response: string) {
    try {
      const cleanResponse = response.replace(/```json/g, '').replace(/```/g, '');
      return JSON.parse(cleanResponse.trim());
    } catch (error) {
      console.error('解析 OpenAI 响应时发生错误:', error);
      return null;
    }
  }
  
  // 跳转到指定的播放时间
  function seekTo(time: string) {
    const timeParts = time.split(':').map(Number);
    let seekTime = 0;
  
    if (timeParts.length === 3) {
      // 如果格式是 "小时:分钟:秒"
      const [hours, minutes, seconds] = timeParts;
      seekTime = hours * 3600 + minutes * 60 + seconds;
    } else if (timeParts.length === 2) {
      // 如果格式是 "分钟:秒"
      const [minutes, seconds] = timeParts;
      seekTime = minutes * 60 + seconds;
    } else if (timeParts.length === 1) {
      // 如果格式是 "秒"
      const [seconds] = timeParts;
      seekTime = seconds;
    }
  
    const video = document.querySelector('video');
    if (video) {
      video.currentTime = seekTime;
      video.play();
    }
  }
  
  onMounted(generateSummary);
  watch([props.subtitles], generateSummary);
  </script>
  
  <style scoped>
  .video-summary {
    margin-top: 20px;
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
  
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .loading-spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #409eff;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
  
  .loading {
    font-size: 1.2em;
    color: #666;
  }
  
  h3 {
    color: #409eff;
  }
  
  h4 {
    margin-top: 10px;
    color: #333;
  }
  
  ul {
    list-style: none;
    padding: 0;
  }
  
  ul li {
    margin-bottom: 8px;
  }
  
  strong {
    display: block;
    color: #333;
  }
  
  /* 新增滑条的样式 */
  .content {
    max-height: 300px; /* 设定最大高度，超出显示滑条 */
    overflow-y: auto;
    padding-right: 10px; /* 为了不遮挡内容，保留一些右侧空间 */
  }
  
  .pagination {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
  }
  
  .pagination button {
    padding: 10px 20px;
    margin: 0 5px;
    background-color: #409eff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .pagination button.active {
    background-color: #307fcf;
  }
  
  .pagination button:hover {
    background-color: #307fcf;
  }
  </style>
  