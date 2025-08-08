<template>
  <div class="content-container">
    <div class="form-card">
      <h2>提交反馈</h2>
      <p>在此填写有关功能实际操作和功能通知的反馈</p>

      <div v-if="flashMessage" class="flash-success">{{ flashMessage }}</div>

      <form @submit.prevent="submitFeedback">
        <label for="message">反馈内容:</label>
        <textarea
          id="message"
          v-model="message"
          rows="6"
          required
          placeholder="请详细描述您的问题或建议..."
        ></textarea>
        <button type="submit" class="btn-primary">提交反馈</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '@/services/api';

const message = ref('');
const flashMessage = ref('');

// 提交反馈的处理函数
async function submitFeedback() {
  if (!message.value.trim()) {
    alert('反馈内容不能为空！');
    return;
  }

  try {
    // 调用 API 创建反馈
    await apiClient.post('/feedback/', { message: message.value });

    // 显示成功消息
    flashMessage.value = '反馈提交成功，感谢您的意见！';

    // 清空输入框
    message.value = '';

    // 3秒后自动隐藏成功消息
    setTimeout(() => {
      flashMessage.value = '';
    }, 3000);

  } catch (error) {
    console.error("提交反馈失败:", error);
    alert('提交失败，请稍后再试。');
  }
}
</script>

<style scoped>
.form-card {
  max-width: 800px;
  margin: auto;
}
</style>