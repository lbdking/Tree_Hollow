<template>
  <div class="page me">
    <div class="card profile">
      <div class="avatar">{{ (user.real_name || user.student_id || '?')[0] }}</div>
      <div>
        <div class="name">{{ user.real_name || user.student_id }}</div>
        <div class="muted">{{ user.student_id }} · {{ roleText(user.role) }}</div>
      </div>
    </div>

    <van-cell-group inset>
      <van-cell title="我的预约" icon="clock-o" is-link to="/appointments" />
      <van-cell title="我的通知" icon="envelop-o" is-link to="/notifications" :value="unread > 0 ? unread + ' 条未读' : ''" />
      <van-cell title="心理科普" icon="bookmark-o" is-link to="/content" />
      <van-cell title="活动报名" icon="flag-o" is-link to="/activities" />
      <van-cell title="呼吸训练" icon="like-o" is-link to="/breathing" />
      <van-cell title="情绪打卡" icon="smile-o" is-link to="/mood" />
      <van-cell title="AI 倾听" icon="chat-o" is-link to="/ai" />
      <van-cell title="预约咨询" icon="contact" is-link to="/counselors" />
    </van-cell-group>

    <div style="padding:18px 16px;">
      <van-button block @click="logout">退出登录</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { notificationApi } from '../api'

const router = useRouter()
const user = JSON.parse(localStorage.getItem('th_user') || '{}')
const unread = ref(0)
function roleText(r){return ({student:'学生',counselor:'咨询师',admin:'管理员'})[r]||r}
function logout() {
  localStorage.removeItem('th_token')
  localStorage.removeItem('th_user')
  router.replace('/login')
}
onMounted(async () => {
  try { unread.value = (await notificationApi.unread()).count } catch {}
})
</script>

<style scoped>
.me { padding-top: 20px; }
.profile { display: flex; gap: 14px; align-items: center; padding: 18px; }
.avatar { width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg,#a8aeff,#7c83ff); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; }
.name { font-weight: 600; font-size: 17px; }
</style>
