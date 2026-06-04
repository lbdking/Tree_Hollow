<template>
  <div class="page me">
    <div class="card profile">
      <div class="avatar">{{ (user.real_name || user.student_id || '?')[0] }}</div>
      <div>
        <div class="name">{{ user.real_name || user.student_id }}</div>
        <div class="muted">{{ user.student_id }} · {{ roleText(user.role) }} · {{ user.age || '-' }}岁</div>
      </div>
      <van-icon name="edit" class="edit-icon" @click="showEditModal = true" />
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

    <!-- 编辑个人信息弹窗 -->
    <van-dialog v-model:show="showEditModal" title="编辑个人信息" width="85%" @confirm="handleUpdate">
      <van-form @submit="handleUpdate">
        <van-field 
          v-model="form.real_name" 
          label="姓名" 
          placeholder="请输入姓名" 
          :disabled="loading"
        />
        <van-field 
          v-model="form.age" 
          label="年龄" 
          type="number" 
          placeholder="请输入年龄" 
          :disabled="loading"
        />
        <van-field 
          v-model="form.student_id" 
          label="学号" 
          placeholder="请输入学号" 
          :disabled="loading"
        />
      </van-form>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi, notificationApi } from '../api'

const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('th_user') || '{}'))
const unread = ref(0)
const showEditModal = ref(false)
const loading = ref(false)

const form = reactive({
  real_name: '',
  age: '',
  student_id: ''
})

function roleText(r){return ({student:'学生',counselor:'咨询师',admin:'管理员'})[r]||r}

function logout() {
  localStorage.removeItem('th_token')
  localStorage.removeItem('th_user')
  router.replace('/login')
}

function openEditModal() {
  form.real_name = user.value.real_name || ''
  form.age = user.value.age || ''
  form.student_id = user.value.student_id || ''
  showEditModal.value = true
}

async function handleUpdate() {
  loading.value = true
  try {
    const data = {}
    if (form.real_name) data.real_name = form.real_name
    if (form.age) data.age = parseInt(form.age)
    if (form.student_id) data.student_id = form.student_id
    
    const result = await authApi.updateMe(data)
    user.value = result
    localStorage.setItem('th_user', JSON.stringify(result))
    
    showEditModal.value = false
    showToast('更新成功')
  } catch (error) {
    showToast('更新失败')
  } finally {
    loading.value = false
  }
}

function showToast(msg) {
  if (window.$toast) {
    window.$toast(msg)
  } else {
    alert(msg)
  }
}

onMounted(async () => {
  try { unread.value = (await notificationApi.unread()).count } catch {}
})
</script>

<style scoped>
.me { padding-top: 20px; }
.profile { display: flex; gap: 14px; align-items: center; padding: 18px; position: relative; }
.avatar { width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg,#a8aeff,#7c83ff); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; }
.name { font-weight: 600; font-size: 17px; }
.edit-icon { position: absolute; right: 18px; font-size: 20px; color: #999; }
</style>