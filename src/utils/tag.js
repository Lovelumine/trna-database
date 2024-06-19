import { ref } from 'vue';

// 用于存储标签类型与颜色的映射
const tagTypeMap = ref({});

// 可用的颜色
const tagColors = ['danger', 'success', 'warning', 'primary', 'info'];

// 获取标签类型
export const getTagType = (tag) => {
  if (!tagTypeMap.value[tag]) {
    const randomColor = tagColors[Math.floor(Math.random() * tagColors.length)];
    tagTypeMap.value[tag] = randomColor;
  }
  return tagTypeMap.value[tag];
};
