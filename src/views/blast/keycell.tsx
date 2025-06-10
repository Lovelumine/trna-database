import { ref } from "vue";
import VueEasyLightbox from 'vue-easy-lightbox';

export const visible = ref(false);
export const lightboxImgs = ref<string[]>([]);
export const lightboxKey = ref(0);


export const showLightbox = (pictureid: string) => {
      const imgUrl = `https://minio.lumoxuan.cn/ensure/picture/${pictureid}.png`;
      lightboxImgs.value = [imgUrl];
      lightboxKey.value += 1;  // 更新key以重新渲染组件
      visible.value = true;
    };