<template>
  <div class="content-container">
    <h1>管理员后台</h1>

    <div v-if="flashMessage" class="flash-success">{{ flashMessage }}</div>

    <div class="admin-grid">
      <div class="form-card">
        <h2>发布新公告</h2>
        <form @submit.prevent="addAnnouncement">
          <label for="title">公告标题:</label>
          <input type="text" id="title" v-model="newAnnouncement.title" required>
          <label for="content">公告内容:</label>

          <MyCKEditor v-model="newAnnouncement.content" />

          <button type="submit" class="btn-primary" style="margin-top: 1rem;">立即发布</button>
        </form>
      </div>

      <div class="form-card">
        <h2>创建新用户</h2>
        <form @submit.prevent="addUser">
          <label for="username">用户名:</label>
          <input type="text" id="username" v-model="newUser.username" required autocomplete="off">
          <label for="password">密码:</label>
          <input type="password" id="password" v-model="newUser.password" required>
          <div class="checkbox-wrapper">
            <input type="checkbox" id="is_superuser" v-model="newUser.is_superuser">
            <label for="is_superuser" class="checkbox-label">设为管理员</label>
          </div>
          <button type="submit" class="btn-primary">创建用户</button>
        </form>
      </div>

      <div class="list-card full-width">
        <h2>公告管理</h2>
        <ul class="admin-data-list">
          <li v-for="ann in announcements" :key="ann.id">
            <span class="item-main-content">
              <strong>{{ ann.title }}</strong> - <small>{{ formatDate(ann.date) }}</small>
            </span>
            <span class="item-actions">
              <router-link :to="{ name: 'EditAnnouncement', params: { id: ann.id } }" class="btn-edit">编辑</router-link>
              <form @submit.prevent="deleteAnnouncement(ann.id)">
                <button type="submit" class="btn-delete">删除</button>
              </form>
            </span>
          </li>
        </ul>
      </div>

      <div class="list-card full-width">
        <h2>用户管理</h2>
        <ul class="admin-data-list">
            <li v-for="user in users" :key="user.id">
                <span class="item-main-content">
                    <strong>{{ user.username }}</strong> (ID: {{ user.id }})
                    <strong v-if="user.is_admin">(管理员)</strong>
                </span>
                <span class="item-actions">
                    <router-link :to="{ name: 'EditUser', params: { id: user.id } }" class="btn-edit">编辑</router-link>
                    <form v-if="user.id !== authStore.user.id && user.id !== 1" @submit.prevent="deleteUser(user.id, user.username)">
                        <button type="submit" class="btn-delete">删除</button>
                    </form>
                </span>
            </li>
        </ul>
      </div>

      <div class="list-card full-width">
        <h2>用户反馈</h2>
        <ul class="admin-data-list">
            <li v-for="fb in feedbacks" :key="fb.id">
                <span class="item-main-content">
                    <strong>{{ fb.user_name }}:</strong> {{ fb.message }} <small>({{ formatDate(fb.date) }})</small>
                </span>
                <span class="item-actions">
                    <form @submit.prevent="deleteFeedback(fb.id)">
                        <button type="submit" class="btn-delete">删除</button>
                    </form>
                </span>
            </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from '@/stores/auth';

// 2. 移除所有旧的 CKEditor 导入，只导入我们自己的组件
import MyCKEditor from '@/components/MyCKEditor.vue';

const authStore = useAuthStore();
const flashMessage = ref('');

const announcements = ref([]);
const users = ref([]);
const feedbacks = ref([]);

const newAnnouncement = reactive({ title: '', content: '' });
const newUser = reactive({ username: '', password: '', is_superuser: false });

const fetchData = async () => {
  try {
    const results = await Promise.allSettled([
      apiClient.get('/announcements/'),
      apiClient.get('/users/'),
      apiClient.get('/feedback/')
    ]);

    if (results[0].status === 'fulfilled') announcements.value = results[0].value.data;
    if (results[1].status === 'fulfilled') users.value = results[1].value.data;
    if (results[2].status === 'fulfilled') feedbacks.value = results[2].value.data;

    results.forEach(result => {
        if(result.status === 'rejected') console.error("获取数据失败:", result.reason);
    });

  } catch (error) {
    console.error("获取后台数据时发生未知错误:", error);
  }
};

const showFlash = (message) => {
    flashMessage.value = message;
    setTimeout(() => flashMessage.value = '', 3000);
}

const formatDate = (dateString) => new Date(dateString).toISOString().split('T')[0];

const addAnnouncement = async () => {
  await apiClient.post('/announcements/', newAnnouncement);
  showFlash("公告发布成功！");
  newAnnouncement.title = ''; newAnnouncement.content = '';
  fetchData();
};

const addUser = async () => {
  await apiClient.post('/users/', newUser);
  showFlash("用户创建成功！");
  newUser.username = ''; newUser.password = ''; newUser.is_superuser = false;
  fetchData();
};

const deleteAnnouncement = async (id) => {
  if (confirm('确定要删除这条公告吗？')) {
    await apiClient.delete(`/announcements/${id}/`);
    showFlash("公告删除成功！");
    fetchData();
  }
};

const deleteUser = async (id, username) => {
    if (confirm(`确定要删除用户 ${username} 吗？此操作不可恢复！`)) {
        await apiClient.delete(`/users/${id}/`);
        showFlash("用户删除成功！");
        fetchData();
    }
};

const deleteFeedback = async (id) => {
    if (confirm('确定要删除这条反馈吗？')) {
        await apiClient.delete(`/feedback/${id}/`);
        showFlash("反馈删除成功！");
        fetchData();
    }
};

onMounted(fetchData);
</script>