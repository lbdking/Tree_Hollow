<template>
  <div class="page">
    <van-nav-bar :title="group?.name || '加载中'" left-arrow @click-left="$router.back()" />
    <div v-if="group" class="card">
      <img v-if="group.cover" :src="group.cover" style="width:100%;border-radius:10px;" />
      <h3 style="margin:10px 0 4px;">{{ group.name }}</h3>
      <div><span class="tag">{{ group.topic }}</span> · {{ group.member_count }} 位伙伴</div>
      <p style="line-height:1.7;color:#555;">{{ group.description }}</p>
      <van-button block :type="group.is_joined ? 'default' : 'primary'" @click="toggle">
        {{ group.is_joined ? '退出小组' : '加入小组' }}
      </van-button>
    </div>

    <div class="section-title">小组活动</div>
    <div v-for="a in activities" :key="a.id" class="card activity">
      <div class="title">{{ a.title }}</div>
      <div class="muted">📍 {{ a.location }} · 🕒 {{ formatTime(a.start_time) }}</div>
      <div style="margin:6px 0;color:#555;">{{ a.description }}</div>
      <div class="muted">{{ a.enrolled_count }} / {{ a.capacity }} 人</div>
      <van-button size="small" :type="a.is_enrolled ? 'default' : 'primary'" @click="toggleEnroll(a)" style="margin-top:6px;">
        {{ a.is_enrolled ? '取消报名' : '我要报名' }}
      </van-button>
    </div>
    <van-empty v-if="!activities.length" description="该小组暂无活动" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showSuccessToast } from 'vant'
import { groupApi } from '../api'

const route = useRoute()
const id = Number(route.params.id)
const group = ref(null)
const activities = ref([])

function formatTime(s) {
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

async function load() {
  group.value = await groupApi.groupDetail(id)
  const r = await groupApi.activities({ group_id: id })
  activities.value = r.items
}
async function toggle() {
  if (group.value.is_joined) await groupApi.leave(id)
  else await groupApi.join(id)
  showSuccessToast('已更新')
  await load()
}
async function toggleEnroll(a) {
  if (a.is_enrolled) await groupApi.cancelEnroll(a.id)
  else await groupApi.enroll(a.id)
  showSuccessToast('已更新')
  await load()
}
onMounted(load)
</script>

<style scoped>
.activity .title { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
</style>
