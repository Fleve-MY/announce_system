// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Feedback from '@/views/Feedback.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import EditAnnouncement from '@/views/EditAnnouncement.vue'
import EditUser from '@/views/EditUser.vue'

const routes = [
    { path: '/login', name: 'Login', component: Login },
    {
        path: '/',
        component: DefaultLayout,
        meta: { requiresAuth: true },
        children: [
            { path: '', name: 'Home', component: Home },
            { path: 'feedback', name: 'Feedback', component: Feedback },
            {
                path: 'admin',
                name: 'AdminDashboard',
                component: AdminDashboard,
                meta: { requiresAdmin: true }
            },
            {
                path: 'admin/announcement/edit/:id',
                name: 'EditAnnouncement',
                component: EditAnnouncement,
                meta: { requiresAdmin: true },
                props: true
            },
            {
                path: 'admin/user/edit/:id',
                name: 'EditUser',
                component: EditUser,
                meta: { requiresAdmin: true },
                props: true
            }
        ]
    }
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);

    if (requiresAuth && !authStore.isAuthenticated) {
        next({ name: 'Login' });
    } else if (requiresAdmin && !authStore.isAdmin) {
        next({ name: 'Home' }); // 如果不是管理员，重定向到首页
    } else if (to.name === 'Login' && authStore.isAuthenticated) {
        next({ name: 'Home' });
    } else {
        next();
    }
});

export default router