<template>
  <div class="site--main">
    <h1>Welcome to ENSURE: The Encyclopedia of Suppressor tRNA Therapeutics with AI Assistant</h1>
    <p>Welcome to ENSURE! Our platform offers extensive data and tools to advance the field of tRNA-therapeutics.</p>
    
    <div class="image-container">
      <img :src="structureImage" @click="openLightbox(0)" class="centered-image" alt="Structure">
    </div>
    
    <div class="image-container">
      <img :src="flowchartImage" @click="openLightbox(1)" class="centered-image" alt="Flowchart ENSURE">
    </div>
    
    <h2>Key Features</h2>
    
    <h3><a :href="geneticVariationUrl">Genetic Variation Database</a></h3>
    <p>Explore variations in genetic diseases and cancers, including missense, nonsense, and frameshift mutations, with potential sup-tRNA therapy applications.</p>
    
    <h3><a :href="naturalSupTRNACatalogUrl">Natural Sup-tRNAs Catalog</a></h3>
    <p>Discover detailed information on natural sup-tRNAs, including their species of origin, sequences, and structures.</p>
    
    <h3><a :href="tRNATherapeuticsDataUrl">tRNA Therapeutics Data</a></h3>
    <p>Access data on existing tRNA therapies, including targeted genes, mutation sites, sup-tRNA sequences, and therapy efficiency and safety.</p>
    
    <h3><a :href="tRNAIdentifyElementsUrl">tRNA Identify Elements</a></h3>
    <p>Understand key elements of tRNA molecules—sequences, structures, and modifications—that influence their function including interaction sites with AARS, EF-Tu and ribosome.</p>
    
    <h2>Research Tools</h2>
    <ul>
      <li><strong>Data Download:</strong> Access downloadable datasets for further research.</li>
      <li><strong>Interactive Visualization:</strong> Explore tRNA structures and functions interactively.</li>
      <li><strong>AI Assistant:</strong> Get expert answers to your tRNA therapeutic questions from Yingying, our AI assistant built on the GPT-4o model.</li>
    </ul>
    
    <h2>Empowering tRNA Research</h2>
    <p>ENSURE is designed to accelerate the discovery and development of tRNA-based therapeutics. Our rich dataset, combined with AI-driven insights, makes ENSURE an invaluable resource for the tRNA research community.</p>
    
    <vue-easy-lightbox
      :visible="showViewer"
      :imgs="[structureImage, flowchartImage]"
      :index="currentIndex"
      @hide="showViewer = false"
    />
  </div>
</template>

<script>
import VueEasyLightbox from 'vue-easy-lightbox';
import structureImage from '/src/data/picture/structure.png';
import flowchartImage from '/src/data/picture/flowchart-ENSURE.png'; 

export default {
  name: 'Home',
  components: {
    VueEasyLightbox
  },
  data() {
    return {
      showViewer: false,
      currentIndex: 0,
      structureImage: structureImage,
      flowchartImage: flowchartImage,
      geneticVariationUrl: '/CodingVariationDisease',
      naturalSupTRNACatalogUrl: '/naturalsuptRNA',
      tRNATherapeuticsDataUrl: '/tRNAtherapeutics',
      tRNAIdentifyElementsUrl: '/tRNAElements'
    };
  },
  methods: {
    openLightbox(index) {
      this.currentIndex = index;
      this.showViewer = true;
    }
  }
}
</script>

<style scoped>
.site--main {
  padding: 20px;
}

.image-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.centered-image {
  width: 800px;
  object-fit: cover; 
  cursor: pointer;
}

h1, h2, h3 {
  color: #333;
}

p, ul {
  color: #555;
}

a {
  color: #1a73e8;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0px 0; /* Add some margin for spacing */
}

.centered-image {
  cursor: pointer;
  max-width: 80%;
}
</style>
