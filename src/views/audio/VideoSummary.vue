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
import { initializeChatIdentity } from '@/utils/chatIdentity';

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
// Bump the namespace whenever the response contract changes so a transient
// malformed model response cannot leave a stale failure cached for a week.
const CACHE_NS = 'videoSummaryCache.v3';
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

  const analysisPrompt = `
Analyze the following video subtitles in language '${props.language ?? '中文'}'.
Return JSON only, using this exact structure:
{
  "summary": "A concise overview",
  "keyPoints": [
    { "time": "03:00", "emoji": "•", "key": "A concise key point" }
  ],
  "questions": [
    { "question": "A useful question?", "answer": "An answer grounded in the subtitles." }
  ]
}
Include 3 to 8 key points and no more than 5 questions. Do not add markdown fences.
The video's title: '''${props.title}'''.
The video's subtitles:
'''
${subtitlesContent}
'''
`.trim();

  try {
    await initializeChatIdentity();
    const analysisResp = await fetchOpenAIResponse(analysisPrompt);

    // 若期间 props 已变更，丢弃本次结果
    if (myRun !== runId) return;

    const analysisJson = parseOpenAIResponse(analysisResp);
    const parsedSummary = analysisJson?.摘要 || analysisJson?.summary || analysisJson?.总结;
    if (typeof parsedSummary !== 'string' || !parsedSummary.trim()) {
      throw new Error('AI analysis returned an invalid summary');
    }

    summary.value = parsedSummary.trim();
    keyPoints.value = Array.isArray(analysisJson?.keyPoints) ? analysisJson.keyPoints : [];
    questions.value = Array.isArray(analysisJson?.questions) ? analysisJson.questions : [];

    saveCache();
  } catch {
    summary.value = 'AI analysis is temporarily unavailable.';
    keyPoints.value = [];
    questions.value = [];
  } finally {
    if (myRun === runId) loading.value = false;
  }
}

function parseOpenAIResponse(response: any) {
  if (response && typeof response === 'object') return response;
  if (typeof response !== 'string') return null;

  const clean = response
    .replace(/^\uFEFF/, '')
    .replace(/```(?:json)?\s*/gi, '')
    .replace(/```/g, '')
    .trim();

  const candidates = [clean];
  const firstBrace = clean.indexOf('{');
  const lastBrace = clean.lastIndexOf('}');
  if (firstBrace >= 0 && lastBrace > firstBrace) {
    candidates.push(clean.slice(firstBrace, lastBrace + 1));
  }

  for (const candidate of candidates) {
    try {
      const parsed = JSON.parse(candidate);
      if (parsed && typeof parsed === 'object') return parsed;
    } catch {
      // Try the next candidate; models occasionally wrap JSON in a sentence.
    }
  }
  return null;
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
.video-summary { margin-top: 20px; padding: 15px; background: var(--app-surface); border: 1px solid var(--app-border-light); border-radius: 8px; color: var(--app-text); }
.refresh-btn { padding: 6px 10px; border: none; border-radius: 6px; background: var(--app-accent); color: #fff; cursor: pointer; }
.refresh-btn:hover { background: var(--app-accent-strong); }
.loading-container { display: flex; flex-direction: column; align-items: center; }
.loading-spinner { border: 4px solid rgba(0,0,0,.1); width: 36px; height: 36px; border-radius: 50%; border-left-color: #409eff; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.content { max-height: 300px; overflow-y: auto; padding-right: 10px; }
.pagination { display: flex; justify-content: center; margin: 12px 0 20px; gap: 8px; }
.pagination button { padding: 10px 20px; background: var(--app-accent); color: #fff; border: none; border-radius: 5px; cursor: pointer; }
.pagination button.active { background: var(--app-accent-strong); }
.pagination button:hover { background: var(--app-accent-strong); }
h3 { color: var(--app-accent); }
h4 { margin-top: 10px; color: var(--app-text); }
ul { list-style: none; padding: 0; }
ul li { margin-bottom: 8px; }
strong { display: block; color: var(--app-text); }
</style>
