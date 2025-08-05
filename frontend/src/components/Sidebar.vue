<template>
  <nav class="sidebar" id="sidebar" :class="{ show: isVisible }">
    <div>
      <div class="sidebar_logo">
        <i class="fa-solid fa-bullhorn sidebar_logo-icon"></i>
        <span class="sidebar_logo-name">Whole_night</span>
      </div>
      <div class="sidebar_list">
        <router-link to="/" class="sidebar_link" active-class="active">
          <i class="fa-solid fa-house-chimney sidebar_icon"></i>
          <span class="sidebar_name">首页</span>
        </router-link>
        <router-link to="/feedback" class="sidebar_link" active-class="active">
          <i class="fa-solid fa-comment-dots sidebar_icon"></i>
          <span class="sidebar_name">提交反馈</span>
        </router-link>
        <router-link v-if="authStore.isAdmin" to="/admin" class="sidebar_link" active-class="active">
          <i class="fa-solid fa-user-shield sidebar_icon"></i>
          <span class="sidebar_name">后台管理</span>
        </router-link>
      </div>
    </div>
    <a href="#" @click.prevent="handleLogout" class="sidebar_link">
      <i class="fa-solid fa-right-from-bracket sidebar_icon"></i>
      <span class="sidebar_name">退出登录</span>
    </a>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

defineProps({
  isVisible: Boolean
});

function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>