// Draggable.ts
import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useDraggable() {
  const isDragging = ref(false);
  const offsetX = ref(0);
  const offsetY = ref(0);
  const element = ref<HTMLElement | null>(null);

  const startDrag = (event: MouseEvent | TouchEvent) => {
    if (element.value) {
      console.log('Drag started');
      isDragging.value = true;
      let clientX = event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
      let clientY = event instanceof MouseEvent ? event.clientY : event.touches[0].clientY;
      offsetX.value = clientX - element.value.getBoundingClientRect().left;
      offsetY.value = clientY - element.value.getBoundingClientRect().top;
      document.addEventListener('mousemove', onDrag);
      document.addEventListener('mouseup', stopDrag);
      document.addEventListener('touchmove', onDrag);
      document.addEventListener('touchend', stopDrag);
    }
  };

  const onDrag = (event: MouseEvent | TouchEvent) => {
    if (isDragging.value && element.value) {
      let clientX = event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
      let clientY = event instanceof MouseEvent ? event.clientY : event.touches[0].clientY;
      element.value.style.left = `${clientX - offsetX.value}px`;
      element.value.style.top = `${clientY - offsetY.value}px`;
    }
  };

  const stopDrag = () => {
    if (isDragging.value) {
      isDragging.value = false;
      document.removeEventListener('mousemove', onDrag);
      document.removeEventListener('mouseup', stopDrag);
      document.removeEventListener('touchmove', onDrag);
      document.removeEventListener('touchend', stopDrag);
    }
  };

  onMounted(() => {
    document.addEventListener('mouseup', stopDrag);
    document.addEventListener('touchend', stopDrag);
  });

  onBeforeUnmount(() => {
    document.removeEventListener('mouseup', stopDrag);
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('touchmove', onDrag);
    document.removeEventListener('touchend', stopDrag);
  });

  return { element, startDrag };
}
