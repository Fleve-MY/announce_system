// src/services/api.js
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const apiClient = axios.create({
    baseURL: '/api', // Vite 代理会将 /api 转发到您的 Django 后端
    headers: {
        'Content-Type': 'application/json'
    }
});

// 请求拦截器
// 在每个请求发送前，自动在请求头中添加 Access Token
apiClient.interceptors.request.use(config => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});


// 响应拦截器
// 处理API响应，特别是当后端返回 401 Unauthorized 错误时
apiClient.interceptors.response.use(
    response => {
        return response;
    },
    async error => {
        const originalRequest = error.config;
        const authStore = useAuthStore();

        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true; // 标记我们已经重试过一次，防止无限循环

            // 检查是否存在 refresh token
            if (authStore.refreshToken) {
                try {
                    // 把刷新逻辑封装在 store 中是最佳实践
                    await authStore.refreshAccessToken();

                    // 自动使用新的 token 重新发送原始失败的请求
                    return apiClient(originalRequest);

                } catch (refreshError) {
                    // store 中的 logout action 应该负责清除 token 并重定向到登录页
                    authStore.logout();
                    return Promise.reject(refreshError);
                }
            } else {
              // 如果没有 refresh token，直接登出
              authStore.logout();
            }
        }

        // 对于非 401 错误，或者没有 refresh token 的情况，直接将错误抛出
        return Promise.reject(error);
    }
);


export default apiClient;