<template>
  <div class="page">
    <van-nav-bar :title="article?.title || '加载中…'" left-arrow @click-left="$router.back()" />
    <div v-if="article" class="card">
      <img v-if="article.cover" :src="article.cover" style="width:100%;border-radius:12px;margin-bottom:12px;" />
      <h2 style="margin:0 0 6px;">{{ article.title }}</h2>
      <div class="muted">{{ article.author }} · 浏览 {{ article.view_count }}</div>
      <video v-if="article.content_type==='video' && article.video_url" :src="article.video_url" controls style="width:100%;margin-top:12px;border-radius:10px;" />
      <div class="content">{{ article.content }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { contentApi } from '../api'
const route = useRoute()
const article = ref(null)
onMounted(async () => {
  article.value = await contentApi.article(route.params.id)
})
</script>

<style scoped>
.content { white-space: pre-wrap; line-height: 1.8; margin-top: 12px; font-size: 15px; }
</style>
