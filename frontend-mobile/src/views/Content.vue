<template>
  <div class="page">
    <van-nav-bar title="心理科普" left-arrow @click-left="$router.back()" />
    <van-tabs v-model:active="cat" sticky animated @change="reload">
      <van-tab name="" title="全部" />
      <van-tab name="焦虑" title="焦虑" />
      <van-tab name="抑郁" title="抑郁" />
      <van-tab name="睡眠" title="睡眠" />
      <van-tab name="冥想" title="冥想" />
      <van-tab name="自我成长" title="成长" />
    </van-tabs>
    <div v-for="a in items" :key="a.id" class="card article" @click="$router.push(`/content/${a.id}`)">
      <img v-if="a.cover" :src="a.cover" class="cover" />
      <div class="info">
        <div class="title">{{ a.title }}<span v-if="a.content_type==='video'" class="tag" style="margin-left:6px;">🎬</span></div>
        <div class="muted">{{ a.summary }}</div>
        <div class="meta"><span class="tag">{{ a.category }}</span> · 浏览 {{ a.view_count }}</div>
      </div>
    </div>
    <van-empty v-if="!items.length" description="暂无内容" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { contentApi } from '../api'
const cat = ref('')
const items = ref([])

async function load() {
  const res = await contentApi.articles({ page: 1, size: 30, category: cat.value || undefined })
  items.value = res.items
}
function reload() { load() }
onMounted(load)
</script>

<style scoped>
.article { display: flex; gap: 12px; }
.cover { width: 96px; height: 96px; border-radius: 10px; object-fit: cover; }
.title { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
.meta { margin-top: 8px; }
</style>
