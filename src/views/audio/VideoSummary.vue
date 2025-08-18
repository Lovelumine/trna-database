<template>
  <div class="video-summary">
    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
      <h3 style="margin:0;">视频 AI 总结</h3>
      <div style="display:flex;gap:8px;">
        <button class="refresh-btn" @click="generateSummary(true)">刷新分析</button>
        <button class="refresh-btn" @click="clearCacheForCurrent">清缓存</button>
      </div>
    </div>

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
import { ref, watch } from 'vue';
import { fetchOpenAIResponse } from './useOpenAI';

const props = defineProps<{
  subtitles: string;
  title: string;
  language?: string;
}>();

// -------- 状态 --------
const loading = ref(true);
const summary = ref('');
const keyPoints = ref<any[]>([]);
const questions = ref<any[]>([]);
const currentTab = ref<'概览' | '要点' | '问题'>('概览');
const tabs = ['概览', '要点', '问题'] as const;

// -------- 简易缓存 --------
const CACHE_NS = 'videoSummaryCache.v1';
const CACHE_TTL_MS = 1000 * 60 * 60 * 24 * 7; // 7天
const cacheKey = () => `${CACHE_NS}:${props.subtitles}|${props.title}|${props.language ?? '中文'}`;

function saveCache() {
  try {
    const data = {
      v: 1,
      t: Date.now(),
      summary: summary.value,
      keyPoints: keyPoints.value,
      questions: questions.value,
    };
    localStorage.setItem(cacheKey(), JSON.stringify(data));
  } catch {}
}

function loadCache() {
  try {
    const raw = localStorage.getItem(cacheKey());
    if (!raw) return false;
    const data = JSON.parse(raw);
    if (!data || !data.t || Date.now() - data.t > CACHE_TTL_MS) return false;
    summary.value = data.summary || '';
    keyPoints.value = data.keyPoints || [];
    questions.value = data.questions || [];
    return true;
  } catch {
    return false;
  }
}

function clearCacheForCurrent() {
  try {
    localStorage.removeItem(cacheKey());
  } catch {}
}

// -------- 取字幕 --------
async function loadSrtContent(): Promise<string> {
  try {
    const res = await fetch(props.subtitles, { credentials: 'omit' });
    if (!res.ok) throw new Error(res.statusText);
    return await res.text();
  } catch (e) {
    console.error('Error loading SRT file:', e);
    return '';
  }
}

// -------- 并发保护与防抖 --------
let runId = 0;
let debounceTimer: number | null = null;

async function generateSummary(forceRefresh = false) {
  // 先看缓存（除非强制刷新）
  if (!forceRefresh && loadCache()) {
    loading.value = false;
    return;
  }

  loading.value = true;
  const myRun = ++runId;

  const subtitlesContent = await loadSrtContent();

  const summaryPrompt = `
You are a helpful assistant that summarize video subtitle.
Summarize in language '${props.language ?? '中文'}'.
Answer in markdown json format.
example:
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
`.trim();

  const keyPointsPrompt = `
You are a helpful assistant that summarize key points of video subtitle.
Summarize 3 to 8 brief key points in language '${props.language ?? '中文'}'.
Answer in markdown json format. The emoji should be related to the key point and 1 char length.
example:
[
  { "time": "03:00", "emoji": "👍", "key": "key point 1" },
  { "time": "10:05", "emoji": "😊", "key": "key point 2" }
]
The video's title: '''${props.title}'''.
The video's subtitles:
'''
${subtitlesContent}
'''
`.trim();

  const questionsPrompt = `
You are a helpful assistant that skilled at extracting questions from video subtitle.
Accurately extract key questions and their corresponding answers from the video subtitles based on the actual content provided.
Answer in language '${props.language ?? '中文'}'.
Format the output in markdown json format.
example:
{
  "questions": [
    { "question": "问题1？", "answer": "答案1。" },
    { "question": "问题2？", "answer": "答案2。" }
  ]
}
End of response.
The video's title: '''${props.title}'''.
The video's subtitles:
'''
${subtitlesContent}
'''
`.trim();

  try {
    const apiKey = import.meta.env.VITE_OPENAI_API_KEY;

    // 并行请求
    const [summaryResp, keyPointsResp, questionsResp] = await Promise.all([
      fetchOpenAIResponse(apiKey, summaryPrompt),
      fetchOpenAIResponse(apiKey, keyPointsPrompt),
      fetchOpenAIResponse(apiKey, questionsPrompt),
    ]);

    // 若期间 props 已变更，丢弃本次结果
    if (myRun !== runId) return;

    const summaryJson = parseOpenAIResponse(summaryResp);
    summary.value = summaryJson?.摘要 || summaryJson?.summary || summaryJson?.总结 || '未能生成摘要';

    const kpJson = parseOpenAIResponse(keyPointsResp);
    keyPoints.value = Array.isArray(kpJson) ? kpJson : [];

    const qJson = parseOpenAIResponse(questionsResp);
    questions.value = Array.isArray(qJson?.questions) ? qJson.questions : [];

    saveCache();
  } catch (e) {
    console.error('生成总结时发生错误:', e);
  } finally {
    if (myRun === runId) loading.value = false;
  }
}

function parseOpenAIResponse(response: any) {
  try {
    if (typeof response !== 'string') return null;
    const clean = response.replace(/```json/g, '').replace(/```/g, '').trim();
    return JSON.parse(clean);
  } catch {
    return null;
  }
}

// 监听字幕/标题/语言变化，300ms 防抖后生成（先读缓存）
watch(
  [() => props.subtitles, () => props.title, () => props.language],
  () => {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(() => generateSummary(false), 300);
  },
  { immediate: true }
);

// 跳转到指定的播放时间
function seekTo(time: string) {
  const parts = time.split(':').map(Number);
  let t = 0;
  if (parts.length === 3) t = parts[0] * 3600 + parts[1] * 60 + parts[2];
  else if (parts.length === 2) t = parts[0] * 60 + parts[1];
  else if (parts.length === 1) t = parts[0];
  const video = document.querySelector('video') as HTMLVideoElement | null;
  if (video) { video.currentTime = t; video.play(); }
}
</script>

<style scoped>
.video-summary { margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,.1); }
.refresh-btn { padding: 6px 10px; border: none; border-radius: 6px; background: #409eff; color: #fff; cursor: pointer; }
.refresh-btn:hover { background: #307fcf; }
.loading-container { display: flex; flex-direction: column; align-items: center; }
.loading-spinner { border: 4px solid rgba(0,0,0,.1); width: 36px; height: 36px; border-radius: 50%; border-left-color: #409eff; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.content { max-height: 300px; overflow-y: auto; padding-right: 10px; }
.pagination { display: flex; justify-content: center; margin: 12px 0 20px; gap: 8px; }
.pagination button { padding: 10px 20px; background: #409eff; color: #fff; border: none; border-radius: 5px; cursor: pointer; }
.pagination button.active { background: #307fcf; }
.pagination button:hover { background: #307fcf; }
h3 { color: #409eff; }
h4 { margin-top: 10px; color: #333; }
ul { list-style: none; padding: 0; }
ul li { margin-bottom: 8px; }
strong { display: block; color: #333; }
</style>
