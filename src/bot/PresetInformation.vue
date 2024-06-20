<template>
    <div>
      <p>{{ systemInformation }}</p>
      <p>{{ projectBackground }}</p>
      <p>{{ projectObjectives }}</p>
      <p>{{ projectContent }}</p>
      <p>{{ QA }}</p>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import { systemInformation, projectBackground, projectObjectives, projectContent ,QA} from './presetInformation';
  
  export default defineComponent({
    name: 'PresetInformation',
    setup() {
      return {
        systemInformation,
        projectBackground,
        projectObjectives,
        projectContent,
        QA
      };
    }
  });
  </script>
  