// src/services/api.js
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const apiClient = axios.create({
    baseURL: '/api', // Django API 地址
    headers: {
        'Content-Type': 'application/json'
    }
});

// 请求拦截器，自动添加 Authorization 头
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

export default apiClient;