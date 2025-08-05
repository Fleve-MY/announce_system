<template>
  <div id="body-pd" :class="{ 'body-pd': isSidebarVisible }">
    <Sidebar :is-visible="isSidebarVisible" />
    <main class="main-content">
      <Header @toggle-sidebar="toggleSidebar" :is-sidebar-visible="isSidebarVisible" />

      <router-view v-slot="{ Component }">
        <transition name="fade-transform" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
      </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import Header from '@/components/Header.vue';

const isSidebarVisible = ref(true);

function toggleSidebar() {
  isSidebarVisible.value = !isSidebarVisible.value;
}
</script>