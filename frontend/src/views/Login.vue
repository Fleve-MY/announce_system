<template>
  <div class="login-body">
    <div class="container" :class="{ 'sign-up-mode': isSignUpMode }">
      <div class="forms-container">
        <div class="signin-signup">
          <form @submit.prevent="handleLogin" class="sign-in-form">
            <h2 class="title">登录</h2>
            <div v-if="errorMessage" class="flash-message" style="position: static; transform: none; margin-bottom: 1rem;">
              {{ errorMessage }}
            </div>
            <div class="input-field">
              <i class="fas fa-user"></i>
              <input type="text" v-model="username" placeholder="用户名" required autocomplete="username" />
            </div>
            <div class="input-field">
              <i class="fas fa-lock"></i>
              <input type="password" v-model="password" placeholder="密码" required autocomplete="current-password" />
            </div>
            <input type="submit" value="登 录" class="btn solid" />
          </form>

          <form action="#" method="GET" class="sign-up-form">
            <h2 class="title">注册已关闭</h2>
            <div class="info-panel-content">
              <i class="fas fa-info-circle"></i>
              <p>本系统为内部使用，账户需由管理员统一创建。</p>
              <p>如需申请账户或重置密码，请联系管理员。</p>
            </div>
          </form>
        </div>
      </div>

      <div class="panels-container">
        <div class="panel left-panel">
          <div class="content">
            <h3>新用户?</h3>
            <p>欢迎打开！点击下方查看注册说明。</p>
            <button type="button" class="btn transparent" id="sign-up-btn" @click="isSignUpMode = true">
              注册说明
            </button>
          </div>
          <img src="https://i.ibb.co/6HXL6q1/log.svg" class="image" alt="" />
        </div>
        <div class="panel right-panel">
          <div class="content">
            <h3>已经是我们的一员?</h3>
            <p>点击下方登录</p>
            <button type="button" class="btn transparent" id="sign-in-btn" @click="isSignUpMode = false">
              去登录
            </button>
          </div>
          <img src="https://i.ibb.co/nP8H853/register.svg" class="image" alt="" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router'; // 2. 导入 useRouter 以修复登录跳转功能

const authStore = useAuthStore();
const router = useRouter(); // 获取 router 实例

const isSignUpMode = ref(false);
const username = ref('');
const password = ref('');
const errorMessage = ref('');

async function handleLogin() {
  errorMessage.value = '';
  try {
    await authStore.login({ username: username.value, password: password.value });
    // 3. 添加手动跳转逻辑
    router.push('/');
  } catch (error) {
    errorMessage.value = '用户名或密码错误！';
  }
}
</script>

<style scoped>
.login-body {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f2f5;

  /* 确保它在最上层 */
  z-index: 999;
}
</style>