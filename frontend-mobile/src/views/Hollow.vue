<template>
  <div class="page">
    <van-nav-bar title="树洞" right-text="发布" @click-right="$router.push('/hollow/post')" />

    <van-tabs v-model:active="active" sticky animated @change="reload">
      <van-tab v-for="t in tabs" :key="t.key" :title="t.label" :name="t.key" />
    </van-tabs>

    <van-pull-refresh v-model="refreshing" @refresh="reload">
      <van-list v-model:loading="loading" :finished="finished" finished-text="到底啦~" @load="loadMore">
        <div v-for="p in items" :key="p.id" class="card post" @click="$router.push(`/hollow/${p.id}`)">
          <div class="head">
            <div class="nick">{{ p.nickname }}</div>
            <span v-if="p.mood_tag" class="tag">{{ p.mood_tag }}</span>
            <span v-if="p.is_crisis" class="tag" style="background:#ffe2e2;color:#d94545;">需关注</span>
            <span class="time">{{ formatTime(p.created_at) }}</span>
          </div>
          <div class="content">{{ p.content }}</div>
          <div class="ops">
            <span @click.stop="like(p)">{{ p.is_liked ? '❤️' : '🤍' }} {{ p.like_count }}</span>
            <span>💬 {{ p.reply_count }}</span>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <van-empty v-if="!loading && items.length === 0" description="还没有树洞，写下第一句吧" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { hollowApi } from '../api'
import { showSuccessToast } from 'vant'

const tabs = [
  { key: 'all', label: '全部' },
  { key: '焦虑', label: '焦虑' },
  { key: '失眠', label: '失眠' },
  { key: '孤独', label: '孤独' },
  { key: '开心', label: '开心' }
]
const active = ref('all')
const items = ref([])
const page = ref(1)
const total = ref(0)
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)

function formatTime(s) {
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

async function load(reset = false) {
  if (reset) {
    page.value = 1
    items.value = []
    finished.value = false
  }
  loading.value = true
  try {
    const params = { page: page.value, size: 10 }
    if (active.value !== 'all') params.mood_tag = active.value
    const res = await hollowApi.list(params)
    items.value.push(...res.items)
    total.value = res.total
    if (items.value.length >= total.value) finished.value = true
    page.value++
  } finally {
    loading.value = false
    refreshing.value = false
  }
}
function loadMore() { load() }
function reload() { load(true) }

async function like(p) {
  const r = await hollowApi.like('post', p.id)
  p.is_liked = r.liked
  p.like_count += r.delta
}

onMounted(() => load(true))
</script>

<style scoped>
.post .head { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
.post .nick { font-size: 13px; color: #7c83ff; font-weight: 500; }
.post .time { margin-left: auto; font-size: 12px; color: #8a90a3; }
.post .content { font-size: 14px; line-height: 1.6; margin: 6px 0; word-break: break-word; }
.post .ops { display: flex; gap: 18px; color: #8a90a3; font-size: 13px; }
</style>
