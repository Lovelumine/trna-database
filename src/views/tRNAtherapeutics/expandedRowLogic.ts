import axios from 'axios';
// import * as $3Dmol from '3dmol';
import * as NGL from 'ngl';

/**
 * 按照换行符分割比对字符串，生成高亮的 HTML
 * @param alignment 比对的字符串，包含用 <br> 分割的多行
 * @returns 格式化后的 HTML 字符串
 */
export function formatAlignment(alignment: string): string {
//   console.log('原始比对数据：', alignment);
  const lines = alignment.split('<br>')
    .map(line => line.trim())
    .filter(line => line.length > 0);
//   console.log('分行后的数据：', lines);

  let html = '';
  if (lines.length % 3 !== 0) {
    console.error("比对数据格式不符合预期！行数不是 3 的倍数");
    return '';
  }

  const labelWidth = 12; // 固定标签宽度
  const originLabel = "origin-tRNA ".padEnd(labelWidth, ' ');
  const supLabel = "Sup-tRNA ".padEnd(labelWidth, ' ');
  const blankLabel = ' '.repeat(labelWidth);

  for (let i = 0; i < lines.length; i += 3) {
    const queryLine = lines[i];
    const matchLine = lines[i + 1];
    const sbjctLine = lines[i + 2];

    // console.log(`处理第 ${i / 3 + 1} 组数据：`);
    // console.log('Query Line:', queryLine);
    // console.log('Match Line:', matchLine);
    // console.log('Sbjct Line:', sbjctLine);

    const querySeq = extractSequence(queryLine);
    const sbjctSeq = extractSequence(sbjctLine);
    const matchSymbols = matchLine.trim().split('');

    // console.log('Query 序列：', querySeq);
    // console.log('Sbjct 序列：', sbjctSeq);
    // console.log('符号行：', matchSymbols);

    const highlightedHTML = generateHighlightedHTML(querySeq, matchSymbols, sbjctSeq);
    const highlightedLines = highlightedHTML.split('\n');
    if (highlightedLines.length >= 3) {
      highlightedLines[0] = originLabel + highlightedLines[0];
      highlightedLines[1] = blankLabel + highlightedLines[1];
      highlightedLines[2] = supLabel + highlightedLines[2];
    }
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

// /**
//  * 加载指定 PDB 文件，并在对应 DOM 容器中创建 3Dmol viewer
//  * @param fileId 用于构造 PDB 文件路径的标识
//  * @param containerId 用于查找 DOM 容器的 id 后缀
//  */
// export async function loadPDBFile(fileId: string, containerId: string): Promise<void> {
//   const pdbFilePath = `https://minio.lumoxuan.cn/ensure/pdb/ensure-${fileId}.pdb`;
//   try {
//     const response = await axios.get(pdbFilePath);
//     const elementId = 'pdb-container-' + containerId;
//     const element = document.getElementById(elementId);
//     if (element) {
//       if ($3Dmol.createViewer) {
//         try {
//           const viewer = $3Dmol.createViewer(element, { backgroundColor: 'white' });
//           viewer.addModel(response.data, 'pdb');
//           viewer.setStyle({}, { cartoon: { color: 'spectrum' } });
//           viewer.zoomTo();
//           viewer.render();
//         } catch (viewerError) {
//           console.error('创建 viewer 或渲染过程中出错:', viewerError);
//         }
//       } else {
//         console.error('错误: 3Dmol.createViewer 不可用');
//       }
//     } else {
//       console.error(`错误: 未找到 id 为 ${elementId} 的 DOM 元素`);
//     }
//   } catch (error) {
//     console.error(`加载 PDB 文件失败, fileId: ${fileId}`, error);
//   }
// }

interface StageMap { [containerId: string]: NGL.Stage; }
const stageMap: StageMap = {};

/**
 * 加载指定 CIF 文件，并在对应 DOM 容器中创建 NGL viewer
 * @param fileId    之前 CSV 的 pdbid 列
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
    console.error(`未找到 id 为 ${elementId} 的 DOM 容器`);
    return;
  }

  let stage = stageMap[containerId];
  if (!stage) {
    stage = new NGL.Stage(element, { backgroundColor: 'white' });
    stageMap[containerId] = stage;
    window.addEventListener('resize', () => stage.handleResize());
  } else {
    stage.removeAllComponents();
  }

  try {
    const comp = await stage.loadFile(cifUrl, { ext: 'cif' }) as NGL.StructureComponent;
    if (comp) {
      // NGL 不支持 spectrum，改为 rainbow
      comp.addRepresentation('cartoon', { color: 'rainbow' });
      stage.autoView();
    }
  } catch (e) {
    console.error(`加载 CIF 失败: ${cifUrl}`, e);
  }
}