<template>
  <div class="login-page">
    <div class="brand">
      <div class="logo">🌳</div>
      <div class="title">树洞</div>
      <div class="slogan">在这里，每个心事都被温柔接住</div>
    </div>

    <van-tabs v-model:active="tab" sticky animated>
      <van-tab title="登录">
        <van-form @submit="onLogin">
          <van-cell-group inset>
            <van-field v-model="form.student_id" label="学号" placeholder="请输入学号" :rules="[{required:true}]" />
            <van-field v-model="form.password" type="password" label="密码" placeholder="请输入密码" :rules="[{required:true}]" />
          </van-cell-group>
          <div class="btn-wrap">
            <van-button block type="primary" native-type="submit" :loading="loading">登 录</van-button>
          </div>
        </van-form>
      </van-tab>
      <van-tab title="注册">
        <van-form @submit="onRegister">
          <van-cell-group inset>
            <van-field v-model="reg.student_id" label="学号" placeholder="请输入学号" :rules="[{required:true}]" />
            <van-field v-model="reg.real_name" label="姓名" placeholder="可选" />
            <van-field v-model="reg.password" type="password" label="密码" placeholder="至少 6 位" :rules="[{required:true,min:6}]" />
          </van-cell-group>
          <div class="btn-wrap">
            <van-button block type="primary" native-type="submit" :loading="loading">注 册</van-button>
          </div>
        </van-form>
      </van-tab>
    </van-tabs>

    <div class="hint">测试账号：2024001 / 123456</div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast } from 'vant'
import { authApi } from '../api'

const router = useRouter()
const tab = ref(0)
const loading = ref(false)
const form = reactive({ student_id: '', password: '' })
const reg = reactive({ student_id: '', password: '', real_name: '' })

async function save(token, user) {
  localStorage.setItem('th_token', token)
  localStorage.setItem('th_user', JSON.stringify(user))
}

async function onLogin() {
  loading.value = true
  try {
    const res = await authApi.login(form)
    await save(res.access_token, res.user)
    showSuccessToast('欢迎回来')
    router.replace('/home')
  } finally { loading.value = false }
}

async function onRegister() {
  loading.value = true
  try {
    const res = await authApi.register(reg)
    await save(res.access_token, res.user)
    showSuccessToast('注册成功')
    router.replace('/home')
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page { min-height: 100vh; padding: 60px 0 40px; background: linear-gradient(160deg,#ecedff,#fff); }
.brand { text-align: center; margin-bottom: 24px; }
.logo { font-size: 56px; }
.title { font-size: 28px; font-weight: 700; margin-top: 8px; color: #2c2f3a; }
.slogan { color: #8a90a3; font-size: 13px; margin-top: 4px; }
.btn-wrap { padding: 18px 16px 0; }
.hint { text-align: center; color: #8a90a3; font-size: 12px; margin-top: 24px; }
</style>
