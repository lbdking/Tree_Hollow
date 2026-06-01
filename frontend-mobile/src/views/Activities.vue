<template>
  <div class="page">
    <van-nav-bar title="近期活动" left-arrow @click-left="$router.back()" />
    <div v-for="a in activities" :key="a.id" class="card activity">
      <div class="title">{{ a.title }}</div>
      <div class="muted">{{ a.group_name }} · 📍 {{ a.location }}</div>
      <div class="muted">🕒 {{ formatTime(a.start_time) }}</div>
      <p style="margin:8px 0;color:#555;">{{ a.description }}</p>
      <div class="row">
        <span class="muted">{{ a.enrolled_count }} / {{ a.capacity }}</span>
        <van-button size="small" :type="a.is_enrolled ? 'default' : 'primary'" @click="toggle(a)">
          {{ a.is_enrolled ? '取消报名' : '我要报名' }}
        </van-button>
      </div>
    </div>
    <van-empty v-if="!activities.length" description="暂无活动" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showSuccessToast } from 'vant'
import { groupApi } from '../api'

const activities = ref([])
function formatTime(s) {
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
async function load() {
  const r = await groupApi.activities()
  activities.value = r.items
}
async function toggle(a) {
  if (a.is_enrolled) await groupApi.cancelEnroll(a.id)
  else await groupApi.enroll(a.id)
  showSuccessToast('已更新')
  await load()
}
onMounted(load)
</script>
<style scoped>
.title { font-weight: 600; font-size: 15px; }
.row { display: flex; align-items: center; justify-content: space-between; }
</style>
