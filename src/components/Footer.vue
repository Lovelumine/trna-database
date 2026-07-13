<template>
  <footer class="site--footer">
    <div class="footer-content">
      <div class="copyright">
        © Copyright 2024 Zheng Lab. School of Life Science, Sun Yat-sen University, China.
        <br />
        ⚠️ The ENSURE database is provided for academic and non-commercial research use only.
        <br />
        Commercial use requires prior written permission from the authors and Sun Yat-sen University.
      </div>
      <div class="beian-source-code">
        <a href="https://beian.miit.gov.cn" target="_blank" class="beian-link">赣ICP备2024033025号</a>
        <span class="separator">|</span>
        <a href="https://github.com/Lovelumine/trna-database" target="_blank" class="source-code-link">
          <svg class="github-logo" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M12 .5C5.73.5.68 5.57.68 11.84c0 5.01 3.44 9.26 8.21 10.76.6.11.82-.26.82-.58 0-.29-.01-1.05-.02-2.06-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.33-1.76-1.33-1.76-1.09-.74.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.34-5.47-5.95 0-1.31.47-2.39 1.24-3.23-.12-.3-.54-1.53.12-3.18 0 0 1.01-.32 3.3 1.23A11.5 11.5 0 0 1 12 6.54c1.02 0 2.05.14 3.01.41 2.29-1.55 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.77.84 1.24 1.92 1.24 3.23 0 4.62-2.81 5.64-5.49 5.94.43.37.81 1.1.81 2.22 0 1.6-.01 2.89-.01 3.29 0 .32.22.69.82.57a11.35 11.35 0 0 0 8.2-10.76C23.32 5.57 18.27.5 12 .5z" />
          </svg>
          Source Code
        </a>
        <span class="separator">|</span>
        <a href="/about" class="about-link">About</a>
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
  flex: 0 0 auto;
}

.site--footer .footer-content .about-link {
  color: var(--farallon-text-light);
  text-decoration: none;
  border-bottom: 1px dashed var(--farallon-text-light);
}

.site--footer .footer-content .about-link:hover {
  color: var(--farallon-text-light-hover);
}

@media (max-width: 640px) {
  .site--footer {
    padding: 18px 20px 22px;
    font-size: 13px;
    line-height: 1.55;
  }

  .site--footer .footer-content {
    max-width: 340px;
  }

  .site--footer .footer-content .beian-source-code {
    justify-content: center;
    flex-wrap: wrap;
    gap: 6px 12px;
    line-height: 1.35;
  }

  .site--footer .footer-content .beian-source-code .separator {
    display: none;
  }

  .site--footer .footer-content .beian-link,
  .site--footer .footer-content .source-code-link,
  .site--footer .footer-content .about-link {
    white-space: nowrap;
  }
}
</style>
