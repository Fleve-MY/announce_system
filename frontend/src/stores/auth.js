// src/stores/auth.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('accessToken') || null,
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
                this.accessToken = response.data.access;
                localStorage.setItem('accessToken', this.accessToken);
                await this.fetchUser();
                router.push('/');
            } catch (error) {
                console.error("Login failed:", error);
                throw error; // 将错误抛出，以便登录页面可以捕获它
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
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
            router.push('/login');
        },
    },
});