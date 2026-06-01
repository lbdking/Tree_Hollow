<template>
  <div class="layout">
    <router-view />
    <van-tabbar v-model="active" route active-color="#7c83ff" inactive-color="#8a90a3" :safe-area-inset-bottom="true">
      <van-tabbar-item to="/home" icon="wap-home-o">首页</van-tabbar-item>
      <van-tabbar-item to="/hollow" icon="like-o">树洞</van-tabbar-item>
      <van-tabbar-item to="/group" icon="friends-o">小组</van-tabbar-item>
      <van-tabbar-item to="/me" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const active = ref(0)
</script>
