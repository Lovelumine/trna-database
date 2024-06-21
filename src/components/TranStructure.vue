<template>
  <div>
    <el-tabs>
      <el-tab-pane label="Secondary Structure">
        <div id="rna_ss"></div>
      </el-tab-pane>
      <el-tab-pane label="Modification Annotation" :disabled="!modified">
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
    initialSequence: {
      type: String,
      required: true,
    },
    initialModifiedSequence: {
      type: String,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      modified: true,
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
      function arrayRemove(arr, value) {
        return arr.filter((ele) => ele !== value);
      }

      if (this.initialModifiedSequence == null) {
        this.modified = false;
        this.drawPlot("rna_ss", this.options.structure, this.options.sequence, '');
      } else {
        this.modified = true;
        let arr = this.initialModifiedSequence.split(";");
        let arr_rm = arrayRemove(arr, "-");
        let text = arr_rm.join(";");
        let color = "";
        for (let i = 0; i < arr_rm.length; i++) {
          if (!["A", "C", "G", "U"].includes(arr_rm[i])) {
            color += `${i + 1}:#ACBFE6 `;
          }
        }
        this.drawPlot("rna_ss_m", this.options.structure, text, color);
        this.drawPlot("rna_ss", this.options.structure, this.options.sequence, '');
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
</style>
