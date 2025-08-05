<template>
  <header class="header" id="header" :class="{ 'body-pd': isSidebarVisible }">
    <div class="header_toggle" id="header-toggle" @click="$emit('toggle-sidebar')">
      <i class="fa-solid" :class="isSidebarVisible ? 'fa-xmark' : 'fa-bars'" id="header-icon"></i>
    </div>
    <div class="header_user">
      欢迎, {{ authStore.user?.username }}
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
defineProps({
  isSidebarVisible: Boolean,
});
defineEmits(['toggle-sidebar']);
</script>