<template>
  <div class="content-container">
    <div class="form-card" style="max-width: 800px; margin: auto;">
      <h2>编辑公告</h2>
      <form v-if="announcement" @submit.prevent="saveChanges">
        <label for="title">公告标题:</label>
        <input type="text" id="title" v-model="announcement.title" required>

        <label for="content">公告内容:</label>

        <MyCKEditor v-model="announcement.content" />

        <button type="submit" class="btn-primary" style="margin-top: 1rem;">保存更改</button>
        <router-link to="/admin" class="btn-secondary">取消</router-link>
      </form>
      <div v-else>
        正在加载公告数据...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';



// 导入 CDN 封装组件
import MyCKEditor from '@/components/MyCKEditor.vue';

const props = defineProps({
  id: {
    type: String,
    required: true
  }
});

const router = useRouter();
const announcement = ref(null);

// 获取公告逻辑
onMounted(async () => {
  try {
    const response = await apiClient.get(`/announcements/${props.id}/`);
    announcement.value = response.data;
  } catch (error) {
    console.error("获取公告详情失败:", error);
    alert("无法加载公告数据。");
    router.push('/admin');
  }
});

async function saveChanges() {
  if (!announcement.value) return;

  try {
    await apiClient.put(`/announcements/${props.id}/`, announcement.value);
    alert('公告更新成功！');
    router.push('/admin');
  } catch (error)
{
    console.error("更新公告失败:", error);
    alert('更新失败，请检查输入内容。');
  }
}
</script>

<style scoped>
.btn-secondary {
    display: block;
    text-align: center;
    margin-top: 1rem;
}
:deep(.ck-editor__main) {
  min-height: 200px;
}
:deep(.ck.ck-editor__main>.ck-editor__editable) {
    min-height: 200px;
}
</style>