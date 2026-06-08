<template>
  <div class="login-page">
    <el-card class="card">
      <h2 style="text-align:center;margin:0 0 8px;">🌳 树洞管理后台</h2>
      <p style="text-align:center;color:#888;margin:0 0 20px;">仅限管理员登录</p>
      <el-form :model="form" @submit.prevent="onSubmit">
        <el-form-item><el-input v-model="form.student_id" placeholder="管理员账号" /></el-form-item>
        <el-form-item><el-input v-model="form.password" type="password" placeholder="密码" /></el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" style="width:100%">登 录</el-button>
      </el-form>
      <p style="text-align:center;color:#aaa;font-size:12px;margin-top:16px;">默认账号 admin / admin123</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../api'

const router = useRouter()
const form = reactive({ student_id: '', password: '' })
const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    const res = await authApi.login(form)
    if (res.user.role !== 'admin') {
      return ElMessage.error('需要管理员账号')
    }
    localStorage.setItem('th_admin_token', res.access_token)
    localStorage.setItem('th_admin_user', JSON.stringify(res.user))
    router.replace('/')
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; height: 100vh; background: linear-gradient(135deg,#a8aeff,#7c83ff); }
.card { width: 380px; padding: 30px 30px 24px; }
</style>
