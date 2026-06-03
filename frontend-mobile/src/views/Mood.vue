<template>
  <div class="page">
    <van-nav-bar title="情绪打卡" left-arrow @click-left="$router.back()" />
    <div class="card">
      <div class="muted" style="margin-bottom:8px;">今天感觉如何？</div>
      <div class="emojis">
        <div v-for="m in moods" :key="m.emoji" class="m" :class="{active: form.mood===m.emoji}" @click="select(m)">
          <div style="font-size:32px;">{{ m.emoji }}</div>
          <div class="muted" style="font-size:12px;">{{ m.label }}</div>
        </div>
      </div>
      <van-field v-model="form.note" rows="3" type="textarea" maxlength="200" show-word-limit placeholder="想说点什么吗？" />
      <van-button block type="primary" :loading="loading" @click="save" style="margin-top:14px;">保存今日心情</van-button>
    </div>

    <div class="section-title">本月心情日历</div>
    <div class="card calendar">
      <div class="cal-grid">
        <div v-for="d in calendar" :key="d.key" class="cell" :class="{today: d.isToday, empty: !d.day}">
          <div class="d">{{ d.day || '' }}</div>
          <div class="emoji">{{ d.mood || '' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import { showSuccessToast } from 'vant'
import { contentApi } from '../api'

const moods = [
  { emoji: '🥰', label: '幸福', score: 5 },
  { emoji: '😀', label: '开心', score: 5 },
  { emoji: '😌', label: '平静', score: 4 },
  { emoji: '😐', label: '一般', score: 3 },
  { emoji: '😴', label: '疲惫', score: 3 },
  { emoji: '😣', label: '焦虑', score: 2 },
  { emoji: '😢', label: '难过', score: 2 },
  { emoji: '😡', label: '愤怒', score: 1 }
]
const form = reactive({ mood: '😀', score: 5, note: '' })
const loading = ref(false)
const records = ref([])

function select(m) { form.mood = m.emoji; form.score = m.score }

async function save() {
  loading.value = true
  try {
    await contentApi.saveMood({ mood: form.mood, score: form.score, note: form.note })
    showSuccessToast('打卡成功 🌟')
    await loadCalendar()
  } finally { loading.value = false }
}

async function loadCalendar() {
  const now = new Date()
  const res = await contentApi.listMood({ year: now.getFullYear(), month: now.getMonth() + 1 })
  records.value = res.items
}

const calendar = computed(() => {
  const now = new Date()
  const y = now.getFullYear(), m = now.getMonth()
  const first = new Date(y, m, 1)
  const last = new Date(y, m + 1, 0)
  const arr = []
  for (let i = 0; i < first.getDay(); i++) arr.push({ key: 'e' + i, day: null, mood: '' })
  const map = {}
  records.value.forEach(r => { map[r.record_date] = r.mood })
  for (let d = 1; d <= last.getDate(); d++) {
    const ds = `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    arr.push({ key: ds, day: d, mood: map[ds] || '', isToday: d === now.getDate() })
  }
  return arr
})

onMounted(loadCalendar)
</script>

<style scoped>
.emojis { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; margin-bottom: 14px; }
.m { padding: 8px 0; text-align: center; border-radius: 12px; background: #f4f5fa; }
.m.active { background: #ecedff; box-shadow: 0 0 0 2px #7c83ff inset; }
.cal-grid { display: grid; grid-template-columns: repeat(7, minmax(40px, 1fr)); grid-auto-rows: 48px; gap: 4px; max-width: 100%; }
.cell { display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; background: #f7f8fc; font-size: 12px; }
.cell.empty { background: transparent; }
.cell.today { background: #ecedff; box-shadow: 0 0 0 2px #7c83ff inset; }
.cell .emoji { font-size: 18px; }
.cell .d { color: #8a90a3; }
</style>
