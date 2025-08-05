<template>
  <div ref="editorElement"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
});
const emit = defineEmits(['update:modelValue']);

const editorElement = ref(null);
let ckEditor = null;

onMounted(() => {
  if (window.CKEDITOR) { // Superbuild 加载的是 CKEDITOR 对象
    CKEDITOR.ClassicEditor
      .create(editorElement.value, {
        // 配置 Superbuild，移除不需要的付费插件
        removePlugins: [
            'RealTimeCollaborativeComments', 'RealTimeCollaborativeTrackChanges', 'RealTimeCollaborativeRevisionHistory',
            'PresenceList', 'Comments', 'TrackChanges', 'TrackChangesData', 'RevisionHistory', 'Pagination',
            'WProofreader', 'DocumentOutline', 'TableOfContents', 'AIAssistant', 'MultiLevelList',
            'FormatPainter', 'Template', 'SlashCommand', 'PasteFromOfficeEnhanced', 'CaseChange'
        ],
        // VVVV 添加图片上传配置 VVVV
        simpleUpload: {
            // 后端 Django API 的上传接口地址
            uploadUrl: 'http://127.0.0.1:8000/api/upload/image/',
            // 如果需要，可以添加 headers，例如 JWT token
            // headers: {
            //     'Authorization': 'Bearer ' + localStorage.getItem('accessToken')
            // }
        }
      })
      .then(editor => {
        ckEditor = editor;
        editor.setData(props.modelValue || '');
        editor.model.document.on('change:data', () => {
          const data = editor.getData();
          if (data !== props.modelValue) {
            emit('update:modelValue', data);
          }
        });
      })
      .catch(error => {
        console.error('CKEditor initialization error:', error);
      });
  } else {
    console.error('CKEditor Superbuild is not available. Check the CDN script in index.html.');
  }
});

watch(() => props.modelValue, (newValue) => {
  if (ckEditor && newValue !== ckEditor.getData()) {
    ckEditor.setData(newValue);
  }
});

onUnmounted(() => {
  if (ckEditor) {
    ckEditor.destroy();
    ckEditor = null;
  }
});
</script>