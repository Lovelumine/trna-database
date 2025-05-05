<template>
  <div class="trna-container" style="position: relative;">
    <!-- Error message -->
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Main SVG chart -->
    <svg v-else :width="width" :height="height">
      <g font-size="12" text-anchor="middle" stroke="#333" stroke-width="1">
        <g
          v-for="node in nodes"
          :key="node.id"
          class="base-group"
          @mouseenter="hoverNode = node"
          @mouseleave="hoverNode = null"
        >
          <circle
            :cx="node.x"
            :cy="node.y"
            :r="r"
            :class="{ 'base-hovered': hoverNode && hoverNode.id === node.id }"
            fill="#fff"
          />
          <text
            :x="node.x"
            :y="node.y + 4"
          >{{ node.base }}</text>
        </g>
      </g>
    </svg>

    <!-- Tooltip -->
    <div
      v-if="hoverNode"
      class="tooltip"
      :style="{ top: hoverNode.y + 10 + 'px', left: hoverNode.x + 10 + 'px' }"
    >
      <div><strong>Position:</strong> {{ hoverNode.id }}</div>
      <div><strong>Base:</strong> {{ hoverNode.base }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'



// 全量 mock 数据（99 个编号，碱基 A/C/G/U 循环）
const mockData = [
    { id: '-1', base: 'A' },
    { id: '1', base: 'C' },
    { id: '2', base: 'G' },
    { id: '3', base: 'U' },
    { id: '4', base: 'A' },
    { id: '5', base: 'C' },
    { id: '6', base: 'G' },
    { id: '7', base: 'U' },
    { id: '8', base: 'A' },
    { id: '9', base: 'C' },
    { id: '10', base: 'G' },
    { id: '11', base: 'U' },
    { id: '12', base: 'A' },
    { id: '13', base: 'C' },
    { id: '14', base: 'G' },
    { id: '15', base: 'U' },
    { id: '16', base: 'A' },
    { id: '17', base: 'C' },
    { id: '17a', base: 'G' },
    { id: '18', base: 'U' },
    { id: '19', base: 'A' },
    { id: '20', base: 'C' },
    { id: '20a', base: 'G' },
    { id: '20b', base: 'U' },
    { id: '21', base: 'A' },
    { id: '22', base: 'C' },
    { id: '23', base: 'G' },
    { id: '24', base: 'U' },
    { id: '25', base: 'A' },
    { id: '26', base: 'C' },
    { id: '27', base: 'G' },
    { id: '28', base: 'U' },
    { id: '29', base: 'A' },
    { id: '30', base: 'C' },
    { id: '31', base: 'G' },
    { id: '32', base: 'U' },
    { id: '33', base: 'A' },
    { id: '34', base: 'C' },
    { id: '35', base: 'G' },
    { id: '36', base: 'U' },
    { id: '37', base: 'A' },
    { id: '38', base: 'C' },
    { id: '39', base: 'G' },
    { id: '40', base: 'U' },
    { id: '41', base: 'A' },
    { id: '42', base: 'C' },
    { id: '43', base: 'G' },
    { id: '44', base: 'U' },
    { id: '45', base: 'A' },
    { id: 'V11', base: 'C' },
    { id: 'V12', base: 'G' },
    { id: 'V13', base: 'U' },
    { id: 'V14', base: 'A' },
    { id: 'V15', base: 'C' },
    { id: 'V16', base: 'G' },
    { id: 'V17', base: 'U' },
    { id: 'V1', base: 'A' },
    { id: 'V2', base: 'C' },
    { id: 'V3', base: 'G' },
    { id: 'V4', base: 'U' },
    { id: 'V5', base: 'A' },
    { id: 'V27', base: 'C' },
    { id: 'V26', base: 'G' },
    { id: 'V25', base: 'U' },
    { id: 'V24', base: 'A' },
    { id: 'V23', base: 'C' },
    { id: 'V22', base: 'G' },
    { id: 'V21', base: 'U' },
    { id: '46', base: 'A' },
    { id: '47', base: 'C' },
    { id: '48', base: 'G' },
    { id: '49', base: 'U' },
    { id: '50', base: 'A' },
    { id: '51', base: 'C' },
    { id: '52', base: 'G' },
    { id: '53', base: 'U' },
    { id: '54', base: 'A' },
    { id: '55', base: 'C' },
    { id: '56', base: 'G' },
    { id: '57', base: 'U' },
    { id: '58', base: 'A' },
    { id: '59', base: 'C' },
    { id: '60', base: 'G' },
    { id: '61', base: 'U' },
    { id: '62', base: 'A' },
    { id: '63', base: 'C' },
    { id: '64', base: 'G' },
    { id: '65', base: 'U' },
    { id: '66', base: 'A' },
    { id: '67', base: 'C' },
    { id: '68', base: 'G' },
    { id: '69', base: 'U' },
    { id: '70', base: 'A' },
    { id: '71', base: 'C' },
    { id: '72', base: 'G' },
    { id: '73', base: 'U' },
    { id: '74', base: 'A' },
    { id: '75', base: 'C' },
    { id: '76', base: 'G' }
]


const props = defineProps({
  data: { type: Array, default: null},
  width: { type: Number, default: 520 },
  height: { type: Number, default: 900 },
  r: { type: Number, default: 12 }
})
// 2. 列出“必须出现”的所有位点 ID
const requiredIds = mockData.map(n => n.id)

// 3. 静态坐标表（圆周均匀分布，仅示例）
const positions = {
  '-1':  { x: 220.0, y: 20.0 },
  '1':   { x: 245.0, y: 20.0 },
  '2':   { x: 245.0, y: 45.0 },
  '3':   { x: 245.0, y: 70.0 },
  '4':   { x: 245.0, y: 95.0 },
  '5':   { x: 245.0, y: 120.0 },
  '6':   { x: 245.0, y: 145.0 },
  '7':   { x: 245.0, y: 170.0 },
  '8':   { x: 225.0, y: 185.0 },
  '9':   { x: 205.0, y: 200.0 },
  '10':  { x: 185.0, y: 215.0 },
  '11':  { x: 160.0, y: 215.0 },
  '12':  { x: 135.0, y: 215.0 },
  '13':  { x: 110, y: 215.0 },
  '14':  { x: 92, y: 198 },
  '15':  { x: 76, y: 179 },
  '16':  { x: 51, y: 179 },
  '17':  { x: 33, y: 196 },
  '17a': { x: 18, y: 215 },
  '18':  { x: 18, y: 240 },
  '19':  { x: 18, y: 265 },
  '20':  { x: 33, y: 285 },
  '20a': { x: 51, y: 302 },
  '20b': { x: 76, y: 302 },
  '21':  { x: 94, y: 285 },
  '22':  { x: 110, y: 265 },
  '23':  { x: 135, y: 265},
  '24':  { x: 160, y: 265 },
  '25':  { x: 185, y: 265 },
  '26':  { x: 205, y: 280 },
  '27':  { x: 205, y: 305 },
  '28':  { x: 205, y: 330 },
  '29':  { x: 205, y: 355 },
  '30':  { x: 205, y: 380 },
  '31':  { x: 205, y: 405 },
  '32':  { x: 195, y: 428 },
  '33':  { x: 195, y: 453 },
  '34':  { x: 210, y: 473 },
  '35':  { x: 232, y: 485 },
  '36':  { x: 254, y: 473 },
  '37':  { x: 268, y: 453 },
  '38':  { x: 268, y: 428 },
  '39':  { x: 258, y: 405 },
  '40':  { x: 258, y: 380 },
  '41':  { x: 258, y: 355 },
  '42':  { x: 258, y: 330 },
  '43':  { x: 258, y: 305 },
  '44':  { x: 258, y: 280 },
  '45':  { x: 283, y: 280 },
  'V11': { x: 290, y: 304 },
  'V12': { x: 310, y: 319 },
  'V13': { x: 330, y: 334 },
  'V14': { x: 350, y: 349 },
  'V15': { x: 370, y: 364 },
  'V16': { x: 390, y: 379 },
  'V17': { x: 410, y: 394 },
  'V1':  { x: 430, y: 409 },
  'V2':  { x: 450, y: 424 },
  'V3':  { x: 472, y: 437 },
  'V4':  { x: 490, y: 420 },
  'V5':  { x: 500, y: 397},
  'V27': { x: 480, y: 382 },
  'V26': { x: 460, y: 367 },
  'V25': { x: 440, y: 352 },
  'V24': { x: 420, y: 337 },
  'V23': { x: 400, y: 322 },
  'V22': { x: 380, y: 307 },
  'V21': { x: 360, y: 292 },
  '46':  { x: 340, y: 277 },
  '47':  { x: 320, y: 262 },
  '48':  { x: 300, y: 247 },
  '49':  { x: 320, y: 232 },
  '50':  { x: 345, y: 232 },
  '51':  { x: 370, y: 232 },
  '52':  { x: 395, y: 232 },
  '53':  { x: 420, y: 232 },
  '54':  { x: 440, y: 246 },
  '55':  { x: 464, y: 249 },
  '56':  { x: 480, y: 230 },
  '57':  { x: 490, y: 207 },
  '58':  { x: 480, y: 184 },
  '59':  { x: 464, y: 165 },
  '60':  { x: 440, y: 168 },
  '61':  { x: 420, y: 182 },
  '62':  { x: 395, y: 182},
  '63':  { x: 370, y: 182 },
  '64':  { x: 345, y: 182 },
  '65':  { x: 320, y: 182 },
  '66':  { x: 298, y: 170 },
  '67':  { x: 298, y: 145 },
  '68':  { x: 298, y: 120 },
  '69':  { x: 298, y: 95 },
  '70':  { x: 298, y: 70 },
  '71':  { x: 298, y: 45 },
  '72':  { x: 298, y: 20 },
  '73':  { x: 323, y: 20 },
  '74':  { x: 348, y: 20 },
  '75':  { x: 373, y: 20 },
  '76':  { x: 398, y: 20 }
}

// 4. 校验：必需的位点如果有缺，就在页面和控制台报错
const error = ref('')

watch(
  () => props.data,
  (arr) => {
    const src   = Array.isArray(arr) ? arr : mockData
    const got   = src.map(n => n.id.toString())
    const miss  = requiredIds.filter(id => !got.includes(id))
    error.value = miss.length
      ? `Missing positions: ${miss.join(', ')}`
      : ''
  },
  { immediate: true }
)

// 5. 过滤：只画在 positions 里定义过的
const nodes = computed(() => {
  const src = Array.isArray(props.data) && props.data.length
    ? props.data
    : mockData

  return src
    .filter(n => positions.hasOwnProperty(n.id.toString()))
    .map(n => ({
      id:   n.id,
      base: n.base,
      x:    positions[n.id.toString()].x,
      y:    positions[n.id.toString()].y
    }))
})

// —— 7. Hover 状态 ——
const hoverNode = ref(null)
</script>

<style scoped>
svg {
  display: block;
  margin: 0 auto;
  background: #f9f9f9;
}
.error {
  color: red;
  font-weight: bold;
  text-align: center;
  padding: 16px;
}

.base-group {
  cursor: pointer;
}
.base-hovered {
  stroke: #ff9800;
  stroke-width: 2;
  fill: #fff5e6;
}
.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 6px 10px;
  pointer-events: none;
  font-size: 14px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  white-space: nowrap;
  transition: opacity 0.2s ease-in-out;
  z-index: 10;
}
</style>