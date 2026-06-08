<template>
  <div class="page">
    <van-nav-bar title="通知" left-arrow @click-left="$router.back()" right-text="全部已读" @click-right="readAll" />
    <div v-for="n in items" :key="n.id" class="card noti" :class="{unread: !n.is_read}" @click="open(n)">
      <div class="row">
        <span class="tag" :class="n.type">{{ typeText(n.type) }}</span>
        <span class="muted">{{ formatTime(n.created_at) }}</span>
      </div>
      <div class="title">{{ n.title }}</div>
      <div class="muted" style="white-space:pre-wrap;">{{ n.content }}</div>
    </div>
    <van-empty v-if="!items.length" description="暂无通知" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { notificationApi } from '../api'

const router = useRouter()
const items = ref([])
function formatTime(s) {
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
function typeText(t){return ({reply:'回复',like:'点赞',appointment:'预约',activity:'活动',system:'系统'})[t]||t}
async function load() {
  const r = await notificationApi.list({ page: 1, size: 50 })
  items.value = r.items
}
async function open(n) {
  if (!n.is_read) await notificationApi.read(n.id)
  if (n.link) router.push(n.link)
  else load()
}
async function readAll() {
  await notificationApi.readAll()
  load()
}
onMounted(load)
</script>
<style scoped>
.row { display: flex; justify-content: space-between; }
.title { font-weight: 600; margin: 6px 0; }
.noti.unread { border-left: 3px solid #7c83ff; }
.tag.reply { background:#ecedff;color:#5057ff; }
.tag.system { background:#fff1f1;color:#d94545; }
.tag.appointment { background:#e6fff0;color:#1ca866; }
.tag.activity { background:#fff3d6;color:#b58a00; }
.tag.like { background:#ffe8ec;color:#d94560; }
</style>
