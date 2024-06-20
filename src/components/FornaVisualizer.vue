<template>
  <div>
    <el-tabs>
      <el-tab-pane label="Secondary Structure">
        <div id='rna_ss'></div>
      </el-tab-pane>
      <el-tab-pane label="Modification Annotation" :disabled="!this.modified">
        <div id='rna_ss_m'></div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import * as fornac from "../fornac/fornac.js";
import axios from "axios";
export default {
  name: "TranStructure",
  data() {
    return {
      modified: true,
      comment: '',
      options: {
        name: 'tRNA-Ala-AGC-8-1',
        structure: '(((((((....((.((.........)).))...((.............))))))))).',
        sequence: 'GAGAAAGCTCACAAGAACTGCTAACTCATGCCCCCATGTCTAACACATGGCTTTCTCA', 
        color: ''
      }
    }
  },
  methods: {
    drawPlot(id) {
      let container = new fornac.FornaContainer(("#"+id), {
        animation: true,
        zoomable: true,
        editable: false
      });
      container.displayNumbering(false);
      container.addRNA(this.options.structure, this.options);
      container.addCustomColorsText(this.options.color);
    },
    async get_structure() {
      const url = 'https://43.138.148.56:20004/get-hg38/tRNA_Ala_AGC_8/';
      let res = await axios.get(url);
      res = res.data;

      function arrayRemove(arr, value) {
        return arr.filter(ele => ele !== value);
      }

      if (res[0].modified_sequence == null) {
        this.modified = false;
      } else {
        this.modified = true;
        let arr = res[0].modified_sequence.split(";");
        let arr_rm = arrayRemove(arr, '-');
        let text = arr_rm.join(";");
        let color = '';
        for (let i = 0; i < arr_rm.length; i++) {
          if (!["A", "C", "G", "U"].includes(arr_rm[i])) {
            color += `${i + 1}:#ACBFE6 `;
          }
        }
        this.options.name = res[0].name;
        this.options.structure = res[0].structure;
        this.options.sequence = text;
        this.options.color = color;
        this.drawPlot("rna_ss_m");
      }
      this.options.name = res[0].name;
      this.options.structure = res[0].structure;
      this.options.color = '';
      this.options.sequence = res[0].sequence_db.replace(/[a-z]+/g, "_");
      this.drawPlot("rna_ss");
    }
  },
  mounted() {
    this.get_structure();
  }
}
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
line[class="link fornac-link fornac-transparent"]{
  display: none;
}
text[class="fornac-nodeLabel fornac-transparent"]{
  display: none;
}
</style>
