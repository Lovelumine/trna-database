import { ref } from "vue";

export const visible = ref(false);
export const lightboxImgs = ref<string[]>([]);
export const lightboxKey = ref(0);


export const showLightbox = (imgUrl: string) => {
  if (!imgUrl) return;
  lightboxImgs.value = [imgUrl];
  lightboxKey.value += 1;
  visible.value = true;
};
