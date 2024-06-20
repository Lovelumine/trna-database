import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'TrnaScanUpload',
  setup() {
    const file = ref<File | null>(null);
    const options = ref<string>(''); // 选项，例如 '-f output.txt'

    const result = ref<string>('');

    const onFileChange = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files) {
        file.value = target.files[0];
      }
    };

    const uploadFile = async () => {
      if (!file.value) return;

      const formData = new FormData();
      formData.append('file', file.value);
      formData.append('options', options.value);

      try {
        const response = await fetch('/scan', {
          method: 'POST',
          body: formData,
        });
        result.value = await response.text();
      } catch (error) {
        console.error(error);
        result.value = '上传失败，请重试。';
      }
    };

    return () => (
      <div>
        <input type="file" onChange={onFileChange} />
        <input type="text" v-model={options.value} placeholder="tRNAscan-SE 选项" />
        <button onClick={uploadFile}>上传</button>
        <pre>{result.value}</pre>
      </div>
    );
  },
});
