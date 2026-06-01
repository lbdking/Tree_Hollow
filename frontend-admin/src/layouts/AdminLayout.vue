<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">🌳 树洞 · 后台</div>
      <el-menu :default-active="$route.path" router class="menu" background-color="transparent" text-color="#fff" active-text-color="#fff">
        <el-menu-item index="/dashboard">📊 数据看板</el-menu-item>
        <el-menu-item index="/posts">🌲 树洞内容</el-menu-item>
        <el-menu-item index="/reports">⚠️ 举报审核</el-menu-item>
        <el-menu-item index="/articles">📚 心理科普</el-menu-item>
        <el-menu-item index="/counselors">👩‍⚕️ 咨询师</el-menu-item>
        <el-menu-item index="/users">👥 用户管理</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div></div>
        <div class="user">
          <span>{{ userName }}</span>
          <el-button text @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const user = JSON.parse(localStorage.getItem('th_admin_user') || '{}')
const userName = user.real_name || user.student_id || '管理员'
function logout() {
  localStorage.removeItem('th_admin_token')
  localStorage.removeItem('th_admin_user')
  router.replace('/login')
}
</script>

<style scoped>
.layout { height: 100vh; }
.aside { background: linear-gradient(180deg,#5057ff,#7c83ff); color: #fff; }
.logo { padding: 22px 18px; font-size: 18px; font-weight: 700; }
.menu { border-right: none; }
.header { display: flex; justify-content: space-between; align-items: center; background: #fff; box-shadow: 0 1px 6px rgba(0,0,0,.05); }
.user { display: flex; gap: 12px; align-items: center; }
:deep(.el-menu-item) { color: #fff !important; }
:deep(.el-menu-item.is-active) { background: rgba(255,255,255,.15) !important; }
:deep(.el-menu-item:hover) { background: rgba(255,255,255,.1) !important; }
</style>
