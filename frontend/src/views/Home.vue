<template>
  <div>
    <div class="content-container">
      <h1>公告</h1>
      <ul class="announcement-list" id="announcement-list">
        <li v-for="announcement in announcements" :key="announcement.id"
            class="announcement-item clickable"
            @click="openModal(announcement)">
          <div class="announcement-header">
            <strong class="announcement-title">{{ announcement.title }}</strong>
            <span class="announcement-date">{{ formatDate(announcement.date) }}</span>
          </div>
          <p class="announcement-content" v-html="truncate(stripTags(announcement.content), 100)"></p>
        </li>
        <li v-if="!announcements.length" class="announcement-item">暂无公告</li>
      </ul>
    </div>

    <AnnouncementModal v-model="isModalVisible" :announcement="selectedAnnouncement" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import AnnouncementModal from '@/components/AnnouncementModal.vue';

const announcements = ref([]);
const isModalVisible = ref(false);
const selectedAnnouncement = ref(null);

const fetchAnnouncements = async () => {
  try {
    const { data } = await apiClient.get('/announcements/');
    announcements.value = data;
  } catch (error) {
    console.error("获取公告失败:", error);
  }
};

const openModal = (announcement) => {
  selectedAnnouncement.value = {
    ...announcement,
    date: formatDate(announcement.date)
  };
  isModalVisible.value = true;
};

const formatDate = (dateString) => {
  return new Date(dateString).toISOString().split('T')[0];
};

const stripTags = (html) => {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return doc.body.textContent || "";
}

const truncate = (text, length) => {
    if (text.length <= length) {
        return text;
    }
    return text.substring(0, length) + '...';
}

onMounted(fetchAnnouncements);
</script>