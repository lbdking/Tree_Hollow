<template>
  <div class="page">
    <van-nav-bar title="互助小组" right-text="活动" @click-right="$router.push('/activities')" />
    <div v-for="g in groups" :key="g.id" class="card group" @click="$router.push(`/group/${g.id}`)">
      <img v-if="g.cover" :src="g.cover" class="cover" />
      <div class="info">
        <div class="name">{{ g.name }}</div>
        <span class="tag">{{ g.topic }}</span>
        <div class="muted">{{ g.description }}</div>
        <div class="meta">{{ g.member_count }} 位伙伴 · {{ g.is_joined ? '已加入' : '未加入' }}</div>
      </div>
    </div>
    <van-empty v-if="!groups.length" description="暂无小组" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { groupApi } from '../api'
const groups = ref([])
onMounted(async () => {
  const r = await groupApi.groups()
  groups.value = r.items
})
</script>
<style scoped>
.group { display: flex; gap: 12px; }
.cover { width: 80px; height: 80px; border-radius: 12px; object-fit: cover; }
.name { font-weight: 600; font-size: 15px; }
.meta { margin-top: 6px; color: #8a90a3; font-size: 12px; }
</style>
