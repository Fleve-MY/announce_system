<template>
  <div class="modal-overlay" :class="{ visible: modelValue }" @click.self="$emit('update:modelValue', false)">
    <div class="modal-content-box" v-if="modelValue">
      <button class="modal-close-btn" @click="$emit('update:modelValue', false)">&times;</button>
      <h2 class="modal-title">{{ announcement?.title }}</h2>
      <p class="modal-date">发布于: {{ announcement?.date }}</p>
      <div class="modal-body" v-html="announcement?.content" @click="handleImageClick"></div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean, // v-model
  announcement: Object
});

defineEmits(['update:modelValue']);

function handleImageClick(event) {
  if (event.target.tagName === 'IMG') {
    const imageUrl = event.target.src;
    // 使用全局的 basicLightbox
    window.basicLightbox.create(`<img src="${imageUrl}">`).show();
  }
}
</script>