<template>
    <div class="site--main">
      <div class="container-fluid">
        <el-card shadow="hover" class="box-card contact-card">
          <h2>Contact Us</h2>
          <p class="info-text">ENSURE v1.0 is under constant maintenance and improvement. Any questions about the usage, comments or suggestions are appreciated.</p>
          <div class="contact-info">
            <p class="mail">
              <strong>Lingling Zheng:</strong>
              <el-link href="mailto:zhengll33@mail.sysu.edu.cn">zhengll33@mail.sysu.edu.cn</el-link>
              <br>RNA Information Center, State Key Laboratory for Biocontrol, Sun Yat-sen University, Guangzhou 510275, P. R. China
            </p>
            <p class="mail">
              <strong>Zhuo Ouyang:</strong>
              <el-link href="mailto:shendekoudai@lovelumine.com">shendekoudai@lovelumine.com</el-link>
              <br>RNA Information Center, State Key Laboratory for Biocontrol, Sun Yat-sen University, Guangzhou 510275, P. R. China
            </p>
          </div>
        </el-card>
        <br>
        <el-card shadow="hover" class="box-card tools-card">
          <h2>Our Tools</h2>
          <p class="info-text">In addition to ENSURE v1.0, we have developed several databases and software to investigate the biological functions and mechanisms of various RNA in biological processes.</p>
          <div class="tools-grid">
            <el-card shadow="always" class="tool-card">
              <a href="http://rna.sysu.edu.cn/rmbase/" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/rmBaseLogo.png" fit="contain" alt="RMBase Logo"></el-image>
              </a>
              <h4>RMBase V2.0</h4>
              <p class="info-text">Deciphering the Map of RNA Modifications from Epitranscriptome Sequencing Data. (Xuan et al. Nucleic Acids Res. 2018 Jan 4;46(D1):D327-34.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="http://starbase.sysu.edu.cn/index.php" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/starBase_logo.png" fit="contain" alt="StarBase Logo"></el-image>
              </a>
              <h4>ENCORI</h4>
              <p class="info-text">A database for exploring miRNA-mRNA and miRNA-ncRNA interaction maps from Argonaute and other RBP CLIP-Seq data. (Li et al. Nucleic Acids Res. 2014;42:D92-7.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="http://rna.sysu.edu.cn/chipbase" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-chipbase-logo.png" fit="contain" alt="ChIPBase Logo"></el-image>
              </a>
              <h4>ChIPBase v2.0</h4>
              <p class="info-text">Decoding transcriptional regulatory networks of non-coding RNAs and protein-coding genes from ChIP-seq data. (Zhou et al. Nucleic Acids Res. 2017 Jan 04;45(D1):D43-D50.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="http://rna.sysu.edu.cn/dreamBase/" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-dreambase-logo.png" fit="contain" alt="dreamBase Logo"></el-image>
              </a>
              <h4>StarScan</h4>
              <p class="info-text">A web server for scanning small RNA targets from degradome sequencing data. (Liu et al. Nucleic Acids Res. 2015 May 18.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="http://deepbase.sysu.edu.cn/SnoSeekerNGS.php" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-snoseeker-logo.png" fit="contain" alt="snoSeeker Logo"></el-image>
              </a>
              <h4>deepBase v3.0</h4>
              <p class="info-text">deepBase v3.0: expression atlas and interactive analysis of ncRNAs from thousands of deep-sequencing data. (Xie et al. Nucleic Acids Res. 2021 Jan 8;49(D1):D877-D883.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="http://rna.sysu.edu.cn/tRFfinder/" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-tRF2Cancer-logo.png" fit="contain" alt="tRF2Cancer Logo"></el-image>
              </a>
              <h4>tRF2Cancer</h4>
              <p class="info-text">A web server to detect tRNA-derived small RNA fragments (tRFs) and their expression in multiple cancers. (Zheng et al. Nucleic Acids Res. 2016 Jul 8;44(W1):W185-93.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="http://mirlab.sysu.edu.cn/starscan/index.php" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-starscan-logo.png" fit="contain" alt="StarScan Logo"></el-image>
              </a>
              <h4>dreamBase</h4>
              <p class="info-text">DNA modification, RNA regulation and protein binding of expressed pseudogenes in human health and disease. (Zheng et al. Nucleic Acids Res. 2018 Jan 4;46(D1):D85-D91.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="http://rna.sysu.edu.cn/deepbase3/" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/deepbase3.png" fit="contain" alt="deepBase Logo"></el-image>
              </a>
              <h4>snoSeeker</h4>
              <p class="info-text">An advanced computational package for screening of guide and orphan snoRNA genes in the human genome. (Yang et al. Nucleic Acids Res. 2006;34:5112-5123.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <a href="https://rna.sysu.edu.cn/pol3base/index.php" target="_blank">
                <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/pol3base_logo.svg" fit="contain" alt="Pol3Base Logo"></el-image>
              </a>
              <h4>Pol3Base</h4>
              <p class="info-text">Pol3Base: a resource for decoding the interactome, expression, evolution, epitranscriptome and disease variations of Pol III-transcribed ncRNAs. (Li Cai, Jiajia Xuan, et al. Nucleic Acids Res. 2021 Oct 15.)</p>
            </el-card>
          </div>
        </el-card>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ContactPage'
  }
  </script>
  
  <style scoped>
  .site--main {
    padding: 20px;
  }
  
  .container-fluid {
    background-color: #e1f5fe;
    padding: 30px;
    text-align: justify;
    color: #0d47a1;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .box-card {
    margin-bottom: 20px;
    border-radius: 10px;
  }
  
  .contact-card {
    background-color: #ffffff;
  }
  
  .tools-card {
    background-color: #ffffff;
  }
  
  .tools-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: space-between;
  }
  
  .tool-card {
    width: calc(33% - 20px);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    background-color: #e3f2fd;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
  }
  
  .tool-card:hover {
    transform: scale(1.05);
  }
  
  .tool-card h4 {
    margin: 10px 0;
    font-size: 16px;
  }
  
  .info-text {
    font-size: 14px;
  }
  
  .mail a {
    text-decoration: none;
    color: #0d47a1;
    font-weight: bold;
  }
  
  @media (max-width: 768px) {
    .tool-card {
      width: 100%;
    }
  }
  </style>
  