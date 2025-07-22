<template>
  <div class="trna-container" style="position: relative;">
    <!-- Main SVG chart -->
    <svg :width="width" :height="height">
            <g :transform="`translate(0, ${yOffset})`">
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
            :class="{
              'base-hovered': hoverNode && hoverNode.id === node.id,
              'overflow-node': node.isOverflow
            }"
            fill="#fff"
          />
          <text :x="node.x" :y="node.y + 4">{{ node.base }}</text>
        </g>
      </g></g>
    </svg>

    <!-- Tooltip -->
    <div
      v-if="hoverNode"
      class="tooltip"
      :style="{ top: hoverNode.y - 40 + 'px', left: hoverNode.x + 160 + 'px' }"
    >
      <div><strong>Position:</strong> {{ hoverNode.id }}</div>
      <div><strong>Base:</strong> {{ hoverNode.base }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 接收外部传入的 JSON 已解析数组：[{ id, base }, ...]
const props = defineProps({
  data:   { type: Array,  default: () => [] },
  width:  { type: Number, default: 520 },
  height: { type: Number, default: 900 },
  r:      { type: Number, default: 12 },
    yOffset: { type: Number, default: 40 }
})

// 1. 固定的 canonical 坐标
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

// 2. nodes 计算：
//   - 遍历所有 canonical positions，map.get(id)||'-'
//   - 再把所有 insertion (`\d+i\d+`) 也加进来

/* ---------- 手动“下一位”映射 ---------- */
const nextMap = {
  V17: "V1",
  45: "V11",
  V5: "V27",
  V21: "46",
  20: "20a",
  "20a": "20b",
  "20b": "21",
  "-1": "1",
  17: "17a",
  "17a": "18",
};

const nodes = computed(() => {
  const list = []
  // canonical
  for (const [id, pos] of Object.entries(positions)) {
    const entry = props.data.find(d => d.id === id)
    list.push({ id, base: entry ? entry.base : '-', x: pos.x, y: pos.y, isOverflow: false })
  }

  // insertion
  props.data
    .filter(d => /^\d+i\d+$/.test(d.id))
    .forEach(item => {
      const [, num, idx] = item.id.match(/^(\d+)i(\d+)$/)
      console.log(`[Insertion] id=${item.id}, num=${num}, idx=${idx}`)

      const p1 = positions[num]
      console.log(`[Insertion ${item.id}] p1=`, p1)
      if (!p1) return console.warn(`no canonical for ${item.id}`)

      const nextKey = nextMap[num] ?? String(+num + 1)
      const p2 = positions[nextKey]
      console.log(`[Insertion ${item.id}] nextKey=${nextKey}, p2=`, p2)

      let dx, dy, mx, my
      if (p2) {
        dx = p2.x - p1.x; dy = p2.y - p1.y
        mx = (p1.x + p2.x) / 2; my = (p1.y + p2.y) / 2
        console.log(`[Insertion ${item.id}] midpoint used: mx=${mx}, my=${my}`)
      } else {
        const p0 = positions[String(+num - 1)]
        console.log(`[Insertion ${item.id}] fallback p0=`, p0)
        if (!p0) return console.warn(`no neighbor for ${item.id}`)
        dx = p1.x - p0.x; dy = p1.y - p0.y
        mx = p1.x; my = p1.y
        console.log(`[Insertion ${item.id}] base p1 used: mx=${mx}, my=${my}`)
      }

      const dist = Math.hypot(dx, dy) || 1
      const ux = -dy / dist, uy = dx / dist
      console.log(`[Insertion ${item.id}] dx=${dx}, dy=${dy}, dist=${dist}, ux=${ux}, uy=${uy}`)

      const offset = 20 * +idx
      console.log(`[Insertion ${item.id}] offset=${offset}`)

      let x = mx + ux * offset, y = my + uy * offset
      console.log(`[Insertion ${item.id}] pre-collision x=${x}, y=${y}`)

      // 碰撞检测
      const thresholdSq = 25 * 25
      const minDistSq = Math.min(...Object.values(positions).map(p => (x - p.x) ** 2 + (y - p.y) ** 2))
      const collision = minDistSq < thresholdSq
      console.log(`[Insertion ${item.id}] minDistSq=${minDistSq}, collision=${collision}`)
      // if (collision) {
      //   x = mx - ux * offset
      //   y = my - uy * offset
      //   console.warn(`[Insertion ${item.id}] reversed to x=${x}, y=${y}`)
      // }

      list.push({ id: item.id, base: item.base, x, y, isOverflow: true })
    })

  return list
})


 
const hoverNode = ref(null)
</script>

<style scoped>
svg {
  display: block;
  margin: 0 auto;
  background: #f9f9f9;
}
.base-group {
  cursor: pointer;
}
.base-hovered {
  stroke: #ff9800;
  stroke-width: 2;
  fill: #fff5e6;
}
.overflow-node {
  fill: yellow;
  stroke: goldenrod;
  stroke-width: 1.5;
}
.tooltip {
  position: absolute;
  background: rgba(0,0,0,0.7);
  color: #fff;
  padding: 6px 10px;
  pointer-events: none;
  font-size: 14px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  white-space: nowrap;
  z-index: 10;
}
</style>