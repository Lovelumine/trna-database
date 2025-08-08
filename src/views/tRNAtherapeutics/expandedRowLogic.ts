import axios from 'axios';
import * as NGL from 'ngl';

/**
 * 按照换行符分割比对字符串，生成高亮的 HTML
 * @param alignment 比对的字符串，包含用 <br> 分割的多行
 * @returns 格式化后的 HTML 字符串
 */
export function formatAlignment(alignment?: string): string {
  // 如果没有 alignment，直接返回空串
  if (!alignment) {
    return '';
  }

  // 把 <br> 当行分隔符
  const lines = alignment
    .split('<br>')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  if (lines.length % 3 !== 0) {
    console.error("比对数据格式不符合预期！行数不是 3 的倍数");
    return '';
  }

  const labelWidth = 12;
  const originLabel = "origin-tRNA ".padEnd(labelWidth, ' ');
  const supLabel    = "sup-tRNA    ".padEnd(labelWidth, ' ');
  const blankLabel  = ' '.repeat(labelWidth);

  let html = '';
  for (let i = 0; i < lines.length; i += 3) {
    const queryLine = lines[i];
    const matchLine = lines[i + 1];
    const sbjctLine = lines[i + 2];

    const querySeq    = extractSequence(queryLine);
    const sbjctSeq    = extractSequence(sbjctLine);
    const matchSymbols = matchLine.trim().split('');

    const highlightedHTML = generateHighlightedHTML(querySeq, matchSymbols, sbjctSeq);
    const highlightedLines = highlightedHTML.split('\n');

    // 添加行首标签
    highlightedLines[0] = originLabel + highlightedLines[0];
    highlightedLines[1] = blankLabel  + highlightedLines[1];
    highlightedLines[2] = supLabel    + highlightedLines[2];

    html += highlightedLines.join('\n');
  }

  return html;
}

/**
 * 从一行字符串中提取碱基序列
 * @param line 输入字符串
 * @returns 碱基序列
 */
export function extractSequence(line: string): string {
  const parts = line.split(/\s+/);
  return parts.slice(2, parts.length - 1).join('');
}

/**
 * 根据查询、符号和目标序列生成高亮 HTML
 * @param query 查询序列
 * @param symbols 比对符号数组
 * @param sbjct 目标序列
 * @returns 高亮 HTML 字符串
 */
export function generateHighlightedHTML(query: string, symbols: string[], sbjct: string): string {
  let html = '';
  let queryIndex = 0;
  let sbjctIndex = 0;

  // 处理 Query 行
  for (let i = 0; i < symbols.length; i++) {
    const symbol = symbols[i];
    if (symbol === '-') {
      html += `<span class="gap">${symbol}</span>`;
      continue;
    }
    const queryChar = query[queryIndex++];
    const sbjctChar = sbjct[sbjctIndex++];
    // console.log(`Query Char: ${queryChar}, Sbjct Char: ${sbjctChar}, Symbol: ${symbol}`);
    html += `<span class="${getCharClass(queryChar, sbjctChar, symbol)}">${queryChar}</span>`;
  }
  html += '\n';

  // 处理符号行
  symbols.forEach((symbol) => {
    html += `<span class="${getSymbolClass(symbol)}">${symbol}</span>`;
  });
  html += '\n';

  // 处理 Sbjct 行
  sbjctIndex = 0;
  for (let i = 0; i < symbols.length; i++) {
    const symbol = symbols[i];
    if (symbol === '-') {
      html += `<span class="gap">${symbol}</span>`;
      continue;
    }
    const sbjctChar = sbjct[sbjctIndex++];
    const queryChar = query[i];
    // console.log(`Sbjct Char: ${sbjctChar}, Query Char: ${queryChar}, Symbol: ${symbol}`);
    html += `<span class="${getCharClass(queryChar, sbjctChar, symbol)}">${sbjctChar}</span>`;
  }
  html += '\n';
  return html;
}

/**
 * 根据比对符号返回对应的字符样式类名
 */
export function getCharClass(char: string, otherChar: string, symbol: string): string {
//   console.log(`字符比对 - Char: ${char}, OtherChar: ${otherChar}, Symbol: ${symbol}`);
  if (char === '-' || otherChar === '-') return 'gap';
  return symbol === '|' ? 'match' : 'mismatch';
}

/**
 * 根据比对符号返回对应的符号样式类名
 */
export function getSymbolClass(symbol: string): string {
//   console.log(`符号行比对 - Symbol: ${symbol}`);
  if (symbol === '|') return 'match-symbol';
  if (symbol === '-') return 'gap-symbol';
  return 'mismatch-symbol';
}

interface StageMap { [containerId: string]: NGL.Stage; }
const stageMap: StageMap = {};

/**
 * 加载指定 CIF 文件，并在对应 DOM 容器中创建 NGL viewer
 * @param fileId     CSV 里的 pdbid 列
 * @param containerId  ENSURE_ID
 * @param sampleIndex 样本索引 (0–4)
 */
export async function loadCIFFile(
  fileId: string,
  containerId: string,
  sampleIndex: number = 0
): Promise<void> {
  const lowerId = fileId.toLowerCase();
  const baseUrl = `https://minio.lumoxuan.cn/ensure/ensure-af3/${lowerId}fold`;
  const cifUrl  = `${baseUrl}/seed-1_sample-${sampleIndex}/model.cif`;

  const elementId = 'pdb-container-' + containerId;
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`❌ 未找到 id 为 ${elementId} 的 DOM 容器`);
    return;
  }

  // 如果已经有 Stage，就复用；否则新建一个
  let stage = stageMap[containerId];
  if (!stage) {
    stage = new NGL.Stage(element, { backgroundColor: 'white' });
    stageMap[containerId] = stage;
    window.addEventListener('resize', () => stage.handleResize());
  } else {
    stage.removeAllComponents();
  }

  try {
    const comp = await stage.loadFile(cifUrl, { ext: 'cif' }) as NGL.StructureComponent | undefined;

    // —— 空值保护 —— 
    if (!comp || !comp.structure) {
      console.warn(`⚠️ 加载后没有获得组件或结构，文件可能不存在：${cifUrl}`);
      return;
    }

    // 1. 彩带：按链 ID 上色，取 NGL 自带的 nucleotide 方案
    comp.addRepresentation('cartoon', {
      sele: 'nucleic',
      color: 'chainname',
      colorScheme: 'nucleotide',
      aspectRatio: 3,
      quality: 'high',
    });

    // 2. 半透明分子表面（如果你不想要，就注释掉或者删掉下面这块）
    // comp.addRepresentation('surface', {
    //   sele: 'nucleic',
    //   opacity: 0.4,
    //   color: 'element',
    // });

    // 3. 骨架细条：backbone 用 ball+stick 强调
    comp.addRepresentation('ball+stick', {
      sele: 'backbone',
      color: 'element',
      radius: 0.15,
    });

    // 4. 碱基平面：base 表示碱基平面
    comp.addRepresentation('base', {
      sele: 'nucleic',
      colorScheme: 'nucleotide',
    });

    // 调整视角
    stage.autoView();

  } catch (e) {
    console.error(`🔴 加载 CIF 失败: ${cifUrl}`, e);
  }
}