<template>
  <div class="outer-container">
    <el-tabs class="full-width-tabs">
      <el-tab-pane :label="titleA">
        <div v-if="error" class="error">{{ error }}</div>
        <div v-else id="rna_ss"></div>
      </el-tab-pane>
      <el-tab-pane :label="titleB" :disabled="!modified">
        <div id="rna_ss_m"></div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import * as fornac from "../fornac/fornac.js";

export default {
  name: "TranStructure",
  props: {
    initialName: {
      type: String,
      required: true,
    },
    initialStructure: {
      type: String,
      required: true,
    },
    supStructure: {
      type: String,
      required: true,
    },
    initialSequence: {
      type: String,
      required: true,
    },
    initialModifiedSequence: {
      type: String,
      required: false,
      default: null,
    },
    titleA: {
      type: String,
      required: true,
    },
    titleB: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      modified: true,
      error: null,
      options: {
        name: this.initialName,
        structure: this.initialStructure,
        sequence: this.initialSequence,
        color: '',
      },
    };
  },
  methods: {
    drawPlot(id, structure, sequence, color) {
      let container = new fornac.FornaContainer("#" + id, {
        animation: true,
        zoomable: true,
        editable: false,
      });
      container.displayNumbering(false);
      container.addRNA(structure, { sequence: sequence });
      container.addCustomColorsText(color);
    },
    processModifiedSequence() {
      try {
        if (this.initialModifiedSequence == null) {
          this.modified = false;
          this.drawPlot("rna_ss", this.options.structure, this.options.sequence, '');
        } else {
          if (this.initialSequence.length !== this.initialModifiedSequence.length) {
            this.modified = false;
            this.drawPlot("rna_ss", this.options.structure, this.options.sequence, '');
          } else {
            this.modified = true;
            let color = "";
            for (let i = 0; i < this.initialSequence.length; i++) {
              if (this.initialSequence[i] !== this.initialModifiedSequence[i]) {
                color += `${i + 1}:#ACBFE6 `;
              }
            }
            this.drawPlot("rna_ss_m", this.options.structure, this.initialModifiedSequence, color);
            this.drawPlot("rna_ss", this.options.structure, this.options.sequence, '');
          }
        }
      } catch (e) {
        this.error = 'Temporarily unable to display secondary structure';
        console.error(e);
      }
    },
  },
  mounted() {
    this.processModifiedSequence();
  },
};
</script>

<style>
circle[node_type="nucleotide"] {
  stroke: #ccc;
  stroke-width: 1;
  opacity: 1;
  fill: white;
}

text[label_type="nucleotide"], text[label_type="label"] {
  font-weight: bolder;
  font-family: "Sofia RE", sans-serif;
  font-size: 0.5em;
  color: rgb(100, 100, 100);
  text-anchor: middle;
  alignment-baseline: middle;
  dominant-baseline: central;
  pointer-events: none;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

circle[node_type="label"] {
  stroke: transparent;
  stroke-width: 0;
  fill: white;
  display: none;
}

path[class="fornac-directionArrow"] {
  fill: #777;
  stroke: none;
  stroke-width: 0.8px;
}

line[class="link fornac-link fornac-transparent"] {
  display: none;
}

text[class="fornac-nodeLabel fornac-transparent"] {
  display: none;
}

.full-width-tabs {
  width: 100%;
}

.outer-container {
  display: flex;
  justify-content: center;
  width: 100%;
}

.tabs-wrapper {
  width: auto;
}

.el-tabs__header {
  display: flex;
  justify-content: center;
}

.el-tabs__nav-wrap {
  justify-content: center;
}

.el-tabs__nav {
  display: inline-flex;
}

.error {
  color: red;
  font-weight: bold;
}
</style>
