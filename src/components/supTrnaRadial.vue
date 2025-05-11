<template>
  <div class="trna-container" style="position: relative;">
    <!-- Main SVG chart -->
    <svg :width="width" :height="height">
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
              'overflow-node': node.isOverflow,
              'insertion-node': node.type === 'insertion',
              'deletion-node':  node.type === 'deletion',
              'mismatch-node':  node.type === 'mismatch'
            }"
            fill="#fff"
          />
          <text :x="node.x" :y="node.y + 4">{{ node.sup_base }}</text>
        </g>
      </g>
    </svg>

    <!-- Tooltip -->
    <div
      v-if="hoverNode"
      class="tooltip"
      :style="{ top: hoverNode.y - 40 + 'px', left: hoverNode.x + 160 + 'px' }"
    >
    <div><strong>Position:</strong> {{ hoverNode.id }}</div>
      <div><strong>Type:</strong> {{ hoverNode.type }}</div>
      <div><strong>Mapping:</strong> {{ hoverNode.base }} → {{ hoverNode.sup_base }}</div>
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
  r:      { type: Number, default: 12 }
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
const nodes = computed(() => {
  const list = []
  // canonical
  for (const [id, pos] of Object.entries(positions)) {
    const entry = props.data.find(d => d.id === id)
    const sup = entry ? entry.sup_base : '-';
    const type = entry
      ? entry.base === '-' && entry.sup_base === '-'
        ? 'gap'
        :entry.base === entry.sup_base
          ? 'match'
          : entry.base === '-' && entry.sup_base !== '-'
            ? 'insertion'
            : entry.base !== '-' && entry.sup_base === '-'
              ? 'deletion'
              : 'mismatch'
      : 'match';
    list.push({
      id,
      base:       entry ? entry.base : '-',
      sup_base:   sup,
      type:       type,
      x:          pos.x,
      y:          pos.y,
      isOverflow: false
    })
  }
  // insertion
  props.data
    .filter(d => /^\d+i\d+$/.test(d.id))
    .forEach(item => {
      const [, num, idx] = item.id.match(/^(\d+)i(\d+)$/)
      const p1 = positions[num]
      const p2 = positions[String(+num + 1)]
      if (!p1) return console.warn(`no canonical for ${item.id}`)
      let dx, dy, mx, my
      if (p2) {
        dx = p2.x - p1.x; dy = p2.y - p1.y
        mx = (p1.x + p2.x)/2; my = (p1.y + p2.y)/2
      } else {
        const p0 = positions[String(+num - 1)]
        if (!p0) return console.warn(`no neighbor for ${item.id}`)
        dx = p1.x - p0.x; dy = p1.y - p0.y
        mx = p1.x; my = p1.y
      }
      const dist   = Math.hypot(dx, dy) || 1
      const ux     = -dy / dist
      const uy     = dx / dist
      const offset = 20 * +idx
      const type = item.base === '-' && item.sup_base !== '-'
        ? 'insertion'
        : item.base !== '-' && item.sup_base === '-'
          ? 'deletion'
          : item.base === item.sup_base
            ? 'match'
            : 'mismatch';
      list.push({
        id:         item.id,
        base:       item.base,
        sup_base:   item.sup_base,
        type:       type,
        x:          mx + ux * offset,
        y:          my + uy * offset,
        isOverflow: true
      })
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
.insertion-node {
  fill: #dcedc8;
  stroke: #388e3c;
}
.deletion-node {
  fill: #ffcdd2;
  stroke: #d32f2f;
}
.mismatch-node {
  fill: #fff9c4;
  stroke: #fbc02d;
}
</style>

