<template>
  <div class="page">
    <van-nav-bar title="预约咨询" left-arrow @click-left="$router.back()" />
    <div v-if="c" class="card counselor-card">
      <div class="row">
        <div class="avatar">{{ c.name[0] }}</div>
        <div>
          <div class="name">{{ c.name }}</div>
          <div class="muted">{{ c.title }}</div>
        </div>
      </div>
      <div style="margin-top:10px;line-height:1.7;color:#555;">{{ c.introduction }}</div>
      <div style="margin-top:10px;"><span class="tag">擅长</span> {{ c.expertise }}</div>
    </div>

    <div v-if="c" class="section-title">选择时段</div>
    <div v-if="c" class="card">
      <div v-for="d in c.available_slots" :key="d.date" class="day">
        <div class="dlabel">{{ d.date }}</div>
        <div class="times">
          <span v-for="t in d.times" :key="t" class="slot" :class="{active: pickedSlot===d.date+' '+t}" @click="pickedSlot = d.date+' '+t">{{ t }}</span>
        </div>
      </div>
    </div>

    <div class="card" v-if="c">
      <van-field v-model="topic" label="主题" placeholder="例如：学业焦虑" />
      <van-field v-model="desc" rows="3" type="textarea" label="情况" maxlength="500" show-word-limit placeholder="简单描述一下你想聊的内容（可选）" />
      <van-field v-model="contact" label="联系方式" placeholder="可留微信/邮箱（可选）" />
    </div>

    <div style="padding:14px;">
      <van-button block type="primary" :loading="loading" @click="submit">提交预约</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { appointmentApi } from '../api'

const route = useRoute()
const router = useRouter()
const c = ref(null)
const pickedSlot = ref('')
const topic = ref('')
const desc = ref('')
const contact = ref('')
const loading = ref(false)

onMounted(async () => {
  c.value = await appointmentApi.counselor(route.params.id)
})

async function submit() {
  if (!pickedSlot.value) return showFailToast('请选择时段')
  loading.value = true
  try {
    const [date, time] = pickedSlot.value.split(' ')
    await appointmentApi.create({
      counselor_id: c.value.id,
      appointment_time: `${date}T${time}:00`,
      topic: topic.value,
      description: desc.value,
      contact: contact.value
    })
    showSuccessToast('已提交，等待老师确认')
    router.replace('/appointments')
  } finally { loading.value = false }
}
</script>
<style scoped>
.row { display: flex; gap: 12px; align-items: center; }
.avatar { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg,#a8aeff,#7c83ff); color:#fff; display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:600; }
.name { font-weight: 600; font-size: 16px; }
.day { padding: 8px 0; border-bottom: 1px dashed #eee; }
.day:last-child { border-bottom: none; }
.dlabel { font-weight: 600; margin-bottom: 6px; }
.times { display: flex; gap: 8px; flex-wrap: wrap; }
.slot { padding: 6px 14px; border-radius: 999px; background: #f4f5fa; font-size: 13px; }
.slot.active { background: #7c83ff; color: #fff; }
</style>
