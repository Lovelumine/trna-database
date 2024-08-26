<template>
    <div class="ai-assistant">
      <h3>AI Assistant</h3>
      <div class="chat-container">
        <div class="chat-history">
          <div v-for="(msg, index) in chatHistory" :key="index" class="chat-message">
            <p class="user-message"><strong>User:</strong> {{ msg.user }}</p>
            <p class="ai-message"><strong>AI:</strong> {{ msg.ai }}</p>
          </div>
        </div>
        <div class="input-container">
          <textarea v-model="inputText" placeholder="Ask me something..."></textarea>
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  
  const inputText = ref('');
  const chatHistory = ref<{ user: string; ai: string }[]>([]);
  
  const sendMessage = () => {
    if (inputText.value.trim()) {
      // 假设有一个方法 fetchAIResponse 可以返回 AI 的回答
      const aiResponse = `Response to: ${inputText.value}`; // 简单模拟
      chatHistory.value.push({ user: inputText.value, ai: aiResponse });
      inputText.value = '';
    }
  };
  </script>
  
  <style scoped>
  .ai-assistant {
    margin-top: 20px;
    padding: 20px;
    background-color: #f0f4f8;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  h3 {
    font-size: 1.5em;
    color: #409eff;
    margin-bottom: 20px;
    text-align: center;
  }
  
  .chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .chat-history {
    max-height: 300px;
    overflow-y: auto;
    padding: 10px;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
  }
  
  .chat-message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 8px;
    background-color: #e6f7ff;
    transition: background-color 0.3s;
  }
  
  .user-message {
    color: #333;
    margin-bottom: 5px;
  }
  
  .ai-message {
    color: #007bff;
  }
  
  .input-container {
    display: flex;
    gap: 10px;
  }
  
  textarea {
    flex: 1;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
    resize: none;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
  }
  
  textarea:focus {
    border-color: #409eff;
    outline: none;
  }
  
  button {
    padding: 10px 20px;
    background-color: #409eff;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  button:hover {
    background-color: #307fcf;
  }
  </style>
  