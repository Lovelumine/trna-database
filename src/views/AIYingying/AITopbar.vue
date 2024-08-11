//src/views/AIYingying/AITopbar.vue
<template>
  <div class="topbar">
    <div class="scenes">
      <div class="scenes-label">Model Selection：</div>
      <div
        class="scene-item"
        v-for="scene in scenes"
        :key="scene.id"
        :class="{ active: scene.id === selectedSceneId, special: scene.text === '傲娇' }"
        @click="selectScene(scene.id)"
        v-wave
      >
        {{ scene.text }}
      </div>
    </div>
    <div class="icons">
      <div class="icon profile">
        <img src="https://framerusercontent.com/images/1w0lzT7QXS4SRJgD02kucFjmSL4.png" alt="profile" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Topbar',
  data() {
    return {
      scenes: [
        { id: 1, text: 'AY-GLM4.0' },
        // { id: 2, text: 'Others' }
      ],
      selectedSceneId: 1 // 默认选择的性格 ID
    };
  },
  methods: {
    selectScene(id) {
      this.selectedSceneId = id;
      this.$emit('scene-selected', id);
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&display=swap'); /* 确保可商用 */

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px; /* 调整内边距 */
  background-color: #ffffff;
  height: 48px; /* 确保高度适中 */
  position: absolute;
  left: 240px; /* 确保与侧边栏对齐 */
  right: 0;
  z-index: 1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
}

.scenes {
  display: flex;
  align-items: center;
  gap: 10px;
}

.scenes-label {
  font-weight: bold;
  margin-right: 8px;
}

.scene-item {
  padding: 5px 10px;
  border-radius: 16px;
  background-color: #f0f0f5;
  color: #888;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}

.scene-item.active {
  background-color: #e6eaff;
  color: #570df5;
}

.scene-item.special {
  font-family: 'ZCOOL KuaiLe', cursive;
}

.scene-item:hover::before {
  width: 100%;
}

.icons {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon img {
  width: 24px;
  height: 24px;
  cursor: pointer;
}

/* 手机端适配 */
@media screen and (max-width: 768px) {
  .topbar {
    left: 62px; /* 确保与侧边栏对齐 */
  }
}
</style>
