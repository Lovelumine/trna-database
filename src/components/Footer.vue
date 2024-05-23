<template>
  <footer class="site--footer">
    <div class="footer-content">
      <div class="copyright">
        © Copyright 2024 Zheng Lab. School of Life Science, Sun Yat-sen University, China.
      </div>
      <div class="beian-source-code">
        <a href="https://beian.miit.gov.cn/#/Integrated/index" target="_blank" class="beian-link">赣ICP备2024033025号</a>
        <span class="separator">|</span>
        <a href="https://github.com/Lovelumine/trna-database" target="_blank" class="source-code-link">
          <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" class="github-logo" />
          Source Code
        </a>
      </div>
      <div class="hosted-by">
        Server provided by Yongxin County Aiying Technology Co., Ltd.
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'FooterComp'
}
</script>

<style>
.site--footer {
  position: relative;
  bottom: 0;
  width: 100%;
  text-align: center;
  font-size: 14px;
  padding: 20px 80px;
  border-top: 1px dotted var(--farallon-border-color);
  color: var(--farallon-text-light);
  background-color: var(--farallon-background-white); 
  display: flex;
  align-items: center;
  justify-content: center;
}

.site--footer .footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.site--footer .footer-content .copyright,
.site--footer .footer-content .hosted-by {
  margin: 5px 0;
}

.site--footer .footer-content .beian-source-code {
  display: flex;
  align-items: center;
  margin: 5px 0;
}

.site--footer .footer-content .beian-source-code .separator {
  margin: 0 10px;
  color: var(--farallon-text-light);
}

.site--footer .footer-content .beian-link {
  color: var(--farallon-text-light);
  text-decoration: none;
  border-bottom: 1px dashed var(--farallon-text-light);
}

.site--footer .footer-content .beian-link:hover {
  color: var(--farallon-text-light-hover);
}

.site--footer .footer-content .source-code-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--farallon-text-light);
}

.site--footer .footer-content .source-code-link:hover {
  color: var(--farallon-text-light-hover);
}

.site--footer .footer-content .source-code-link .github-logo {
  width: 20px;
  height: 20px;
  margin-right: 5px;
}
</style>
