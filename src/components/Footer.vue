<template>
  <footer class="site--footer">
    <div class="footer-content">
      <div class="copyright">
        © Copyright 2024 Zheng Lab. School of Life Science, Sun Yat-sen University, China.
      </div>
      <div class="beian">
        <a href="https://beian.miit.gov.cn/#/Integrated/index" target="_blank">赣ICP备2024033025号</a>
      </div>
      <div class="hosted-by">
        Hosted by Yongxin County Aiying Technology Co., Ltd.
      </div>
      <div class="source-code">
        <a href="https://github.com/Lovelumine/trna-database" target="_blank">
          <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" class="github-logo" />
          Source Code
        </a>
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
.site--footer .footer-content .beian,
.site--footer .footer-content .hosted-by,
.site--footer .footer-content .source-code {
  margin: 5px 0;
}

.site--footer .footer-content .source-code a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--farallon-text-light);
}

.site--footer .footer-content .source-code .github-logo {
  width: 20px;
  height: 20px;
  margin-right: 5px;
}
</style>
