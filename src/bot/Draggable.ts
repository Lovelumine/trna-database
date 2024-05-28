// Draggable.ts
import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useDraggable() {
  const isDragging = ref(false);
  const offsetX = ref(0);
  const offsetY = ref(0);
  const element = ref<HTMLElement | null>(null);

  const startDrag = (event: MouseEvent) => {
    if (element.value) {
      isDragging.value = true;
      offsetX.value = event.clientX - element.value.getBoundingClientRect().left;
      offsetY.value = event.clientY - element.value.getBoundingClientRect().top;
      document.addEventListener('mousemove', onDrag);
      document.addEventListener('mouseup', stopDrag);
    }
  };

  const onDrag = (event: MouseEvent) => {
    if (isDragging.value && element.value) {
      element.value.style.left = `${event.clientX - offsetX.value}px`;
      element.value.style.top = `${event.clientY - offsetY.value}px`;
    }
  };

  const stopDrag = () => {
    if (isDragging.value) {
      isDragging.value = false;
      document.removeEventListener('mousemove', onDrag);
      document.removeEventListener('mouseup', stopDrag);
    }
  };

  onMounted(() => {
    document.addEventListener('mouseup', stopDrag);
  });

  onBeforeUnmount(() => {
    document.removeEventListener('mouseup', stopDrag);
    document.removeEventListener('mousemove', onDrag);
  });

  return { element, startDrag };
}
