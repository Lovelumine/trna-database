<template>
    <div class="site--main">
      <div class="container-fluid">
        <el-card shadow="hover" class="box-card">
          <h2>Contact US</h2>
          <p><strong>ENSURE v1.0 is under constant maintenance and improvement. Any questions about the usage, comments or suggestions are appreciated.</strong></p>
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
        </el-card>
        <br>
        <el-card shadow="hover" class="box-card">
          <h2>Our Tools</h2>
          <p><strong>In addition to RMBase v3.0, we have developed several databases and softwares to investigate the biological functions and mechanisms of various RNA in biological processes.</strong></p>
          <div class="tools-grid">
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/rmBaseLogo.png" fit="contain" alt="RMBase Logo"></el-image>
              <h4>RMBase V2.0</h4>
              <p>Deciphering the Map of RNA Modifications from Epitranscriptome Sequencing Data. (Xuan et al. Nucleic Acids Res. 2018 Jan 4;46(D1):D327-34.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/starBase_logo.png" fit="contain" alt="StarBase Logo"></el-image>
              <h4>ENCORI</h4>
              <p>A database for exploring miRNA-mRNA and miRNA-ncRNA interaction maps from Argonaute and other RBP CLIP-Seq data. (Li et al. Nucleic Acids Res. 2014;42:D92-7.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-chipbase-logo.png" fit="contain" alt="ChIPBase Logo"></el-image>
              <h4>ChIPBase v2.0</h4>
              <p>Decoding transcriptional regulatory networks of non-coding RNAs and protein-coding genes from ChIP-seq data. (Zhou et al. Nucleic Acids Res. 2017 Jan 04;45(D1):D43-D50.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-dreambase-logo.png" fit="contain" alt="dreamBase Logo"></el-image>
              <h4>dreamBase</h4>
              <p>DNA modification, RNA regulation and protein binding of expressed pseudogenes in human health and disease. (Zheng et al. Nucleic Acids Res. 2018 Jan 4;46(D1):D85-D91.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/deepbase3.png" fit="contain" alt="deepBase Logo"></el-image>
              <h4>deepBase v3.0</h4>
              <p>deepBase v3.0: expression atlas and interactive analysis of ncRNAs from thousands of deep-sequencing data. (Xie et al. Nucleic Acids Res. 2021 Jan 8;49(D1):D877-D883.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-tRF2Cancer-logo.png" fit="contain" alt="tRF2Cancer Logo"></el-image>
              <h4>tRF2Cancer</h4>
              <p>A web server to detect tRNA-derived small RNA fragments (tRFs) and their expression in multiple cancers. (Zheng et al. Nucleic Acids Res. 2016 Jul 8;44(W1):W185-93.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-starscan-logo.png" fit="contain" alt="StarScan Logo"></el-image>
              <h4>StarScan</h4>
              <p>A web server for scanning small RNA targets from degradome sequencing data. (Liu et al. Nucleic Acids Res. 2015 May 18.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/contact-snoseeker-logo.png" fit="contain" alt="snoSeeker Logo"></el-image>
              <h4>snoSeeker</h4>
              <p>An advanced computational package for screening of guide and orphan snoRNA genes in the human genome. (Yang et al. Nucleic Acids Res. 2006;34:5112-5123.)</p>
            </el-card>
            <el-card shadow="always" class="tool-card">
              <el-image src="https://rna.sysu.edu.cn/rmbase3/pictures/contact/pol3base_logo.svg" fit="contain" alt="Pol3Base Logo"></el-image>
              <h4>Pol3Base</h4>
              <p>Pol3Base: a resource for decoding the interactome, expression, evolution, epitranscriptome and disease variations of Pol III-transcribed ncRNAs. (Li Cai, Jiajia Xuan, et al. Nucleic Acids Res. 2021 Oct 15.)</p>
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
    background-color: #f5f5f5;
    padding: 30px;
    text-align: justify;
    color: #333366;
  }
  
  .box-card {
    margin-bottom: 20px;
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
  }
  
  .tool-card h4 {
    margin: 10px 0;
  }
  
  .mail a {
    text-decoration: none;
  }
  
  @media (max-width: 768px) {
    .tool-card {
      width: 100%;
    }
  }
  </style>
  