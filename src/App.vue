<template>
  <div>
    <nav-bar />
    <router-view />
    <footer-comp />
    <<bot-component />
  </div>
</template>

<script lang="tsx">
import { defineComponent } from 'vue';
import NavBar from './components/NavBar.vue';
import FooterComp from './components/Footer.vue';
import BotComponent from './bot/BotComponent.vue';

export default defineComponent({
  components: {
    NavBar,
    FooterComp,
    BotComponent
  }
});
</script>

<style>
/* Add global styles here */
</style>
