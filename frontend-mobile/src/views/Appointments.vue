<template>
  <div class="page">
    <van-nav-bar title="我的预约" left-arrow @click-left="$router.back()" />
    <div v-for="a in items" :key="a.id" class="card appt">
      <div class="row">
        <strong>{{ a.counselor_name }}</strong>
        <span class="tag" :class="statusClass(a.status)">{{ statusText(a.status) }}</span>
      </div>
      <div class="muted">🕒 {{ formatTime(a.appointment_time) }} · {{ a.duration_minutes }} 分钟</div>
      <div v-if="a.topic" style="margin-top:6px;">主题：{{ a.topic }}</div>
      <div v-if="a.description" class="muted">{{ a.description }}</div>
      <div v-if="a.counselor_note" style="margin-top:6px;color:#5057ff;">老师留言：{{ a.counselor_note }}</div>
    </div>
    <van-empty v-if="!items.length" description="暂无预约" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { appointmentApi } from '../api'
const items = ref([])
function formatTime(s) {
  const d = new Date(s)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
function statusText(s){return ({pending:'待确认',confirmed:'已确认',cancelled:'已取消',completed:'已完成',rejected:'已拒绝'})[s]||s}
function statusClass(s){return s}
onMounted(async () => {
  const r = await appointmentApi.myAppointments()
  items.value = r.items
})
</script>
<style scoped>
.row { display: flex; align-items: center; }
.tag.pending { background:#fff3d6;color:#b58a00; }
.tag.confirmed { background:#e6fff0;color:#1ca866; }
.tag.cancelled { background:#f0f1f7;color:#8a90a3; }
.tag.rejected { background:#ffe2e2;color:#d94545; }
.tag { margin-left:auto; }
</style>
