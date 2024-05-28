<template>
    <div>
      <p>{{ systemInformation }}</p>
      <p>{{ projectBackground }}</p>
      <p>{{ projectObjectives }}</p>
      <p>{{ projectContent }}</p>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import { systemInformation, projectBackground, projectObjectives, projectContent } from './presetInformation.ts';
  
  export default defineComponent({
    name: 'PresetInformation',
    setup() {
      return {
        systemInformation,
        projectBackground,
        projectObjectives,
        projectContent
      };
    }
  });
  </script>
  