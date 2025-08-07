<template>
  <div class="content-container">
    <div class="header-with-button">
      <h1>同款检测日志</h1>
      <button @click="fetchLogs" :disabled="isLoading" class="btn-primary refresh-btn">
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
        刷新
      </button>
    </div>

    <div class="list-card">
      <div v-if="isLoading" class="loading-state">
        正在从飞书获取数据...
      </div>
      <div v-else-if="error" class="error-state">
        {{ error }}
      </div>
      <ul v-else-if="logs.length > 0" class="log-list">
        <li class="log-list-header">
          <span v-if="authStore.isAdmin" class="col-user">用户名</span>
          <span class="col-b">日期</span>
          <span class="col-c">店铺</span>
          <span class="col-j">编码</span>
          <span class="col-f">关键字/类目</span>
          <span class="col-h">上架数量</span>
          <span class="col-k">状态</span>
        </li>
        <li v-for="(log, index) in logs" :key="index" class="log-list-item">
          <span v-if="authStore.isAdmin" class="col-user">{{ log.username }}</span>
          <span class="col-b">{{ log.b_col }}</span>
          <span class="col-c">{{ log.c_col }}</span>
          <span class="col-j">{{ log.j_col }}</span>
          <span class="col-f">{{ log.f_col }}</span>
          <span class="col-h">{{ log.h_col }}</span>
          <!-- 动态绑定 class -->
          <span class="col-k" :class="getStatusClass(log.k_col)">
            {{ log.k_col }}
          </span>
        </li>
      </ul>
      <div v-else class="empty-state">
        <!-- 根据用户身份显示不同的提示信息 -->
        <span v-if="authStore.isAdmin">表格中目前没有有效的日志记录。</span>
        <span v-else>没有找到与您用户名匹配的日志记录。</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const logs = ref([]);
const isLoading = ref(false);
const error = ref(null);

const fetchLogs = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/feishu-logs/');
    logs.value = response.data;
  } catch (err) {
    console.error("获取飞书日志失败:", err);
    error.value = "获取数据失败，请稍后再试或联系管理员。";
    logs.value = [];
  } finally {
    isLoading.value = false;
  }
};

// 根据状态文本返回对应的 CSS
const getStatusClass = (status) => {
  if (status === '未完成') {
    return 'status-unfinished';
  }
  // 包含“已”的就是指都完成了的
  if (status && status.includes('已')) {
    return 'status-finished';
  }
  // 其他情况返回默认
  return '';
};

onMounted(fetchLogs);
</script>
