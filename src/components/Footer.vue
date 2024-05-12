<template>
  <footer class="site--footer">
    <div class="copyright">
      © Copyright 2024 Zheng Lab. School of Life Science, Sun Yat-sen University, China.
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

/* 用于确保内容在页脚内水平居中 */
.site--footer .copyright {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
