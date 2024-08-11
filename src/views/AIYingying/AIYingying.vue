<template>
    <div id="ai-app">
      <Sidebar @menu-selected="handleMenuSelected" />
      <div class="content-wrapper">
        <Topbarbar @scene-selected="handleSceneSelected" />
        <div class="main-content">
          <ChatBox :selectedMenuId="selectedMenuId" :selectedSceneId="selectedSceneId" />
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent, ref } from 'vue';
  import Sidebar from './AISidebar.vue';
  import Topbarbar from './AITopbar.vue';
  import ChatBox from './ChatBox/ChatBox.vue';
  
  export default {
    name: 'App',
    components: {
      Sidebar,
      Topbarbar,
      ChatBox
    },  setup() {
    const selectedMenuId = ref(1);
    const selectedSceneId = ref(1);

    const handleMenuSelected = (id) => {
      selectedMenuId.value = id;
    };

    const handleSceneSelected = (id) => {
      selectedSceneId.value = id;
    };

    return {
      selectedMenuId,
      selectedSceneId,
      handleMenuSelected,
      handleSceneSelected
    };
  }
  };
  </script>
  
  <style>
  #ai-app {
    display: flex;
    height: calc(100vh - 80px); 
  }
  
  .content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
  </style>
  