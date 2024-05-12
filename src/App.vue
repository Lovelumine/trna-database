<template>
  <div>
    <nav-bar />
    <router-view />
    <footer-comp />
  </div>
</template>

<script lang="tsx">
import { defineComponent } from 'vue';
import NavBar from './components/NavBar.vue';
import FooterComp from './components/Footer.vue';

export default defineComponent({
  components: {
    NavBar,
    FooterComp
  }
});
</script>

<style>
/* Add global styles here */
</style>
