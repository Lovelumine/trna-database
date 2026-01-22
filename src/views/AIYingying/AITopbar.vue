//src/views/AIYingying/AITopbar.vue
<template>
  <div class="topbar">
    <div class="icons">
      <div class="icon profile">
        <img src="https://framerusercontent.com/images/1w0lzT7QXS4SRJgD02kucFjmSL4.png" alt="profile" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Topbar'
};
</script>

<style scoped>
.topbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 12px 16px;
  background-color: transparent;
}

.icons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon img {
  width: 28px;
  height: 28px;
  cursor: pointer;
  border-radius: 50%;
  border: 1px solid var(--app-border);
}

@media screen and (max-width: 768px) {
  .topbar { padding: 8px 12px; }
}
</style>
