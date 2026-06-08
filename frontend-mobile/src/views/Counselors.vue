<template>
  <div class="page">
    <van-nav-bar title="心理咨询师" left-arrow @click-left="$router.back()" right-text="我的预约" @click-right="$router.push('/appointments')" />
    <div v-for="c in counselors" :key="c.id" class="card counselor" @click="$router.push(`/counselors/${c.id}`)">
      <div class="avatar">{{ c.name[0] }}</div>
      <div class="info">
        <div class="name">{{ c.name }} <span class="muted">· {{ c.title }}</span></div>
        <div class="muted" style="margin:4px 0;">擅长：{{ c.expertise }}</div>
        <div class="muted">{{ c.introduction }}</div>
        <div style="margin-top:6px;">⭐ {{ c.rating }}.0</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { appointmentApi } from '../api'
const counselors = ref([])
onMounted(async () => {
  const r = await appointmentApi.counselors()
  counselors.value = r.items
})
</script>
<style scoped>
.counselor { display: flex; gap: 12px; }
.avatar { width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg,#a8aeff,#7c83ff); color:#fff; display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:600; }
.name { font-weight: 600; font-size: 15px; }
</style>
