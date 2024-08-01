<template>
  <div class="blast-search">
    <h1>BLAST Search</h1>
    <form @submit.prevent="runBlast">
      <div class="form-group">
        <label for="expect">Expect</label>
        <input type="number" id="expect" v-model="formData.expect" step="0.01" />
      </div>
      <div class="form-group">
        <label for="wordSize">Word Size</label>
        <input type="number" id="wordSize" v-model="formData.wordSize" />
      </div>
      <div class="form-group">
        <label for="database">Database</label>
        <select id="database" v-model="formData.database">
          <option value="All eukaryotic tRNAs">All eukaryotic tRNAs</option>
        </select>
      </div>
      <div class="form-group">
        <label for="sequenceFormat">Query Sequence Format</label>
        <select id="sequenceFormat" v-model="formData.sequenceFormat">
          <option value="formatted">Formatted (FASTA, GenBank)</option>
          <option value="unformatted">Unformatted</option>
        </select>
      </div>

      <div class="form-group">
        <label>Query Sequence</label>
        <div class="form-group">
        <button type="button" @click="addExampleSequences">Example</button>
      </div>
        <textarea v-model="formData.querySequence" placeholder="Enter your sequence here"></textarea>
      </div>
      <div class="form-group">
        <label for="sequenceFile">OR Load query from file:</label>
        <input type="file" id="sequenceFile" @change="handleFileUpload" />
      </div>
      <button type="submit">Run BLAST</button>
      <button type="reset" @click="clearForm">Clear Form</button>
    </form>
  </div>
  <div v-if="blastResult">
    <BlastResults :blastResult="blastResult" />
  </div>
</template>

<script>
import BlastResults from './BlastResults.vue';

export default {
  components: {
    BlastResults
  },
  data() {
    return {
      formData: {
        expect: 0.01,
        wordSize: 11,
        database: 'All eukaryotic tRNAs',
        sequenceFormat: 'formatted',
        querySequence: ''
      },
      blastResult: null
    };
  },
  methods: {
    async runBlast() {
      try {
        const response = await fetch('/run-blast', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.formData)
        });
        const result = await response.text();
        this.blastResult = result;
      } catch (error) {
        console.error('Error running BLAST:', error);
      }
    },
    clearForm() {
      this.formData = {
        expect: 0.01,
        wordSize: 11,
        database: 'All eukaryotic tRNAs',
        sequenceFormat: 'formatted',
        querySequence: ''
      };
      this.blastResult = null;
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.formData.querySequence = e.target.result;
      };
      reader.readAsText(file);
    },
    addExampleSequences() {
      this.formData.querySequence = `>sequence_A
GTAGTCGTGGCCGAGTGGTTAAGGCGGCAGGCTTTAAACCTGTTGGGGTTTCCCCGCACGGGTTCGAATCCCGTCGACTACGCCA
>sequence_B
GTAGTCGTGGCCGAGTGGTTAAGGCGGCAGGCTTTAAACCTGTTGGGGTTTCCCCGCACGGGTTCGAATCCCGTCGACTACGCCA`;
    }
  }
};
</script>

<style scoped>
.blast-search {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

form label {
  display: block;
  margin-bottom: 0.5rem;
}

form input,
form select,
form textarea {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

form button {
  padding: 0.5rem 1rem;
  margin-top: 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

form button[type="submit"] {
  background: #007bff;
  color: #fff;
}

form button[type="reset"] {
  background: #6c757d;
  color: #fff;
  margin-left: 0.5rem;
}
</style>
