<template>
  <nav class="help-nav" aria-label="Help navigation">
    <div class="help-nav__head">
      <strong>Contents</strong>
    </div>

    <div class="help-nav__list">
      <section v-for="file in files" :key="file.file" class="help-nav__section" :class="{ 'is-active': file.file === activeFile }">
        <button
          class="help-nav__file-button"
          :class="{ 'is-active': file.file === activeFile }"
          type="button"
          @click="handleFileClick(file.file)"
        >
          <span class="help-nav__file-copy">
            <strong>{{ file.name }}</strong>
          </span>
          <span class="help-nav__file-marker" :class="{ 'is-active': file.file === activeFile }"></span>
        </button>

        <div v-if="file.file === activeFile && headings.length" class="help-nav__sublist">
          <button
            v-for="heading in headings"
            :key="heading.id"
            class="help-nav__heading-button"
            :class="{ 'is-active': heading.id === activeHeading }"
            type="button"
            @click="handleHeadingClick(heading.id)"
          >
            <span class="help-nav__heading-dot"></span>
            <span class="help-nav__heading-text">{{ heading.text }}</span>
          </button>
        </div>
      </section>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router';

defineProps({
  files: {
    type: Array,
    required: true,
  },
  headings: {
    type: Array,
    required: true,
  },
  activeFile: {
    type: String,
    default: '',
  },
  activeHeading: {
    type: String,
    default: '',
  },
});

const emits = defineEmits(['navigateToHeading', 'fileSelected']);
const router = useRouter();

const handleFileClick = async (file) => {
  emits('fileSelected', file);
  await router.push({ path: router.currentRoute.value.path, query: { file } });
};

const handleHeadingClick = (id) => {
  emits('navigateToHeading', id);
};
</script>

<style scoped>
.help-nav {
  width: 100%;
  padding-right: 22px;
  border-right: 1px solid var(--farallon-border-color-light);
  box-sizing: border-box;
}

.help-nav__head {
  padding: 2px 0 14px;
}

.help-nav__head strong {
  display: block;
  margin: 0;
  color: var(--farallon-text-color);
  font-size: 1rem;
  font-weight: 700;
}

.help-nav__list {
  display: grid;
  gap: 8px;
  padding: 0;
}

.help-nav__section {
  display: grid;
  gap: 4px;
}

.help-nav__section.is-active {
  margin-bottom: 8px;
}

.help-nav__file-button,
.help-nav__heading-button {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.help-nav__file-button {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 10px;
  align-items: center;
  gap: 14px;
  min-height: 44px;
  padding: 8px 0 8px 12px;
  border-left: 3px solid transparent;
  transition: border-color 0.18s ease, background-color 0.18s ease;
}

.help-nav__file-button:hover {
  background: rgba(148, 163, 184, 0.06);
}

.help-nav__file-button.is-active {
  border-left-color: #2563eb;
  background: rgba(37, 99, 235, 0.06);
}

.help-nav__file-copy {
  min-width: 0;
}

.help-nav__file-copy strong,
.help-nav__file-copy small {
  display: block;
}

.help-nav__file-copy strong {
  color: var(--farallon-text-color);
  font-size: 0.98rem;
  font-weight: 700;
  line-height: 1.3;
}

.help-nav__file-copy small {
  margin-top: 3px;
  color: var(--farallon-text-light);
  font-size: 0.8rem;
}

.help-nav__file-marker {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.55);
  transition: background-color 0.18s ease, box-shadow 0.18s ease;
}

.help-nav__file-marker.is-active {
  background: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.help-nav__sublist {
  display: grid;
  gap: 2px;
  margin: 0 0 0 15px;
  padding: 4px 0 0 18px;
  border-left: 1px solid rgba(148, 163, 184, 0.3);
}

.help-nav__heading-button {
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-radius: 0;
  transition: background-color 0.18s ease, color 0.18s ease;
}

.help-nav__heading-button:hover {
  background: transparent;
}

.help-nav__heading-button.is-active {
  background: transparent;
}

.help-nav__heading-dot {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.7);
}

.help-nav__heading-button.is-active .help-nav__heading-dot {
  background: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.help-nav__heading-text {
  color: var(--farallon-text-light);
  font-size: 0.92rem;
  line-height: 1.45;
}

.help-nav__heading-button.is-active .help-nav__heading-text {
  color: var(--farallon-text-color);
  font-weight: 700;
}

@media (max-width: 768px) {
  .help-nav {
    padding-right: 0;
    border-right: none;
  }

  .help-nav__head {
    padding: 0 0 12px;
  }

  .help-nav__list {
    gap: 6px;
  }

  .help-nav__file-button {
    min-height: 42px;
    padding: 8px 0 8px 12px;
  }

  .help-nav__sublist {
    margin: 0 0 10px 14px;
    padding-left: 12px;
  }
}
</style>
