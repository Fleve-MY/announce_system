<template>
  <div class="content-container">
    <div class="form-card" style="max-width: 800px; margin: auto;">
      <h2 v-if="user">编辑用户 - {{ user.username }}</h2>
      <form v-if="user" @submit.prevent="saveChanges">
        <label for="username">用户名:</label>
        <input type="text" id="username" v-model="userData.username" required>

        <label for="password">新密码 (留空则不修改):</label>
        <input type="password" id="password" v-model="userData.password" placeholder="输入新密码">

        <div class="checkbox-wrapper">
          <input type="checkbox" id="is_admin" v-model="userData.is_admin">
          <label for="is_admin" class="checkbox-label">设为管理员</label>
        </div>

        <button type="submit" class="btn-primary">保存更改</button>
        <router-link to="/admin" class="btn-secondary">取消</router-link>
      </form>
      <div v-else>
        正在加载用户数据...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

// 定义 props 来接收路由参数中的 id
const props = defineProps({
  id: {
    type: String,
    required: true
  }
});

const router = useRouter();
const user = ref(null);
const userData = reactive({
  username: '',
  password: '', // 密码字段默认为空
  is_admin: false,
});

// 在组件挂载后，根据 id 获取用户数据
onMounted(async () => {
  try {
    const response = await apiClient.get(`/users/${props.id}/`);
    user.value = response.data;
    // 将获取到的数据填充到响应式对象 userData 中
    userData.username = user.value.username;
    userData.is_admin = user.value.is_admin;
  } catch (error) {
    console.error("获取用户详情失败:", error);
    alert("无法加载用户数据。");
    router.push('/admin');
  }
});

// 保存更改的处理函数
async function saveChanges() {
  if (!user.value) return;

  // 准备要发送到 API 的数据
  const payload = {
    username: userData.username,
    is_admin: userData.is_admin,
  };

  // 只有当用户输入了新密码时，才将其包含在请求中
  if (userData.password) {
    payload.password = userData.password;
  }

  try {
    // 调用 API 更新用户（使用 PATCH 更合适，只更新变化的字段）
    await apiClient.patch(`/users/${props.id}/`, payload);
    alert('用户信息更新成功！');
    // 成功后返回管理员后台
    router.push('/admin');
  } catch (error) {
    console.error("更新用户失败:", error.response.data);
    // 构造更详细的错误提示
    const errorMessages = Object.entries(error.response.data).map(([key, value]) => `${key}: ${value}`).join('\n');
    alert(`更新失败:\n${errorMessages}`);
  }
}
</script>

<style scoped>
.btn-secondary {
    display: block;
    text-align: center;
    margin-top: 1rem;
}
</style>