// src/stores/auth.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api';
import router from '@/router';
// 建议为刷新 token 的请求单独使用一个 axios 实例，以避免循环拦截
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('accessToken') || null,
        // --- 新增 ---
        // 添加 refreshToken 状态
        refreshToken: localStorage.getItem('refreshToken') || null,
        user: JSON.parse(localStorage.getItem('user')) || null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        isAdmin: (state) => state.user?.is_admin || false,
    },
    actions: {
        async login(credentials) {
            try {
                const response = await apiClient.post('/token/', credentials);

                // --- 修改 ---
                // 同时存储 access 和 refresh token
                this.accessToken = response.data.access;
                this.refreshToken = response.data.refresh;
                localStorage.setItem('accessToken', this.accessToken);
                localStorage.setItem('refreshToken', this.refreshToken);

                await this.fetchUser();
                router.push('/');
            } catch (error) {
                console.error("Login failed:", error);
                throw error;
            }
        },
        async fetchUser() {
            try {
                const { data } = await apiClient.get('/users/me/');
                this.user = data;
                localStorage.setItem('user', JSON.stringify(this.user));
            } catch (error) {
                console.error("Failed to fetch user:", error);
                this.logout();
            }
        },
        logout() {
            this.accessToken = null;
            this.user = null;
            // --- 修改 ---
            // 登出时也要清除 refresh token
            this.refreshToken = null;
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            router.push('/login');
        },


        // 核心的 token 刷新 action
        async refreshAccessToken() {
            // 如果没有 refresh token，直接登出
            if (!this.refreshToken) {
                return this.logout();
            }

            try {
                const response = await axios.post('/api/token/refresh/', {
                    refresh: this.refreshToken
                });

                // 刷新成功，更新 access token
                this.accessToken = response.data.access;
                localStorage.setItem('accessToken', this.accessToken);
                console.log("Token refreshed successfully.");

            } catch (error) {
                console.error("Failed to refresh token:", error);
                this.logout();
                throw error;
            }
        },
    },
});