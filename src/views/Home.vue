<template>
  <div class="site--main">
    <h2>Recent Advances in Suppressor tRNA (sup-tRNA) for the Treatment of Genetic Diseases</h2>
        <!-- Image with Lightbox -->
        <div class="image-container">
      <img :src="imageSrc" @click="showViewer = true" class="centered-image" alt="Structure">
    </div>
    <p>Recent advances in the use of suppressor tRNA (sup-tRNA) for the treatment of genetic diseases have achieved remarkable progress and raised several thought-provoking questions:</p>
    <ul>
      <li><strong>Targeted Mutation Sites in Diseases:</strong> Which mutation sites in which diseases can be targeted by tRNA therapeutics?</li>
      <li><strong>Naturally Occurring sup-tRNAs:</strong> Naturally occurring sup-tRNAs capable of suppressing nonsense mutations and frameshifts are present in certain species. What are their sequences and structures?</li>
      <li><strong>Targeted Diseases and Efficacy:</strong> Which diseases are primarily targeted by existing tRNA therapies, and what is their efficiency and safety?</li>
      <li><strong>Key Sites on tRNA Molecules:</strong> What roles do specific sites on tRNA molecules play, and can they serve as a basis for designing sup-tRNAs?</li>
    </ul>
    <p>To address these questions, we have developed <strong>ENSURE: The Encyclopedia of Suppressor tRNA Therapeutics with AI Assistant</strong>. ENSURE compiles genetic variations occurring in genetic diseases and cancers, including those caused by missense, nonsense, and frameshift mutations. Furthermore, we have cataloged hundreds of natural sup-tRNAs, detailing their source species, sequences, and structures.</p>
    <h3>ENSURE Features:</h3>
    <ul>
      <li><strong>Pathogenic Genes and Mutation Sites:</strong> Information on the pathogenic genes, mutation sites, sequences, and structures of sup-tRNAs. Efficiency and safety data of existing tRNA therapies.</li>
      <li><strong>BLAST Comparisons:</strong> Performed BLAST comparisons of similar sequences of sup-tRNAs.</li>
      <li><strong>Key Elements of tRNA Molecules:</strong> Summarized key elements (including sequences, structures, and modifications) on tRNA molecules critical for their function.</li>
    </ul>
    <p>Based on ENSURE's data, we have trained a virtual assistant named <strong>Yingying</strong>, built on the GPT-4o model. Yingying is capable of answering various questions regarding tRNA therapy. The ENSURE platform aids researchers in quickly identifying the biological mechanisms and application scopes of sup-tRNAs while providing a rich data resource and analytical platform for the design of engineered tRNAs.</p>
        <vue-easy-lightbox
      :visible="showViewer"
      :imgs="[imageSrc]"
      @hide="showViewer = false"
    />
  </div>
</template>

<script>
import VueEasyLightbox from 'vue-easy-lightbox';
import structureImage from '/data/picture/structure.png'; // Correct path to your image

export default {
  name: 'Home',
  components: {
    VueEasyLightbox
  },
  data() {
    return {
      showViewer: false,
      imageSrc: structureImage
    };
  }
}
</script>

<style>
.site--main {
 /* Center text and elements inside this container */
}

.image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0; /* Add some margin for spacing */
}

.centered-image {
  cursor: pointer;
  max-width: 50%;
}
</style>
