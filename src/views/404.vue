<template>
    <div class="page-404">
      <h1>404</h1>
      <p>Oops! The page you are looking for has been removed or relocated.</p>
      <router-link to="/">Go back home</router-link>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  export default defineComponent({
    name: 'PageNotFound'
  });
  </script>
  
  <style scoped>
  .page-404 {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 80vh;
    text-align: center;
  }
  
  .page-404 h1 {
    font-size: 6rem;
    font-weight: bold;
  }
  
  .page-404 p {
    font-size: 1.5rem;
    margin-bottom: 20px;
  }
  </style>
  