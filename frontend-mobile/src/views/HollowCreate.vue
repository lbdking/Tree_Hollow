<template>
  <div class="page">
    <van-nav-bar title="写下心事" left-arrow @click-left="$router.back()" />
    <div class="card">
      <van-field
        v-model="form.content"
        type="textarea"
        rows="6"
        autosize
        maxlength="2000"
        show-word-limit
        placeholder="把烦恼写下来，会有人陪你 🫶"
      />
    </div>
    <div class="card">
      <div class="muted" style="margin-bottom:8px;">心情标签</div>
      <div class="moods">
        <div v-for="m in moods" :key="m" class="mood" :class="{active: form.mood_tag === m}" @click="form.mood_tag = form.mood_tag === m ? '' : m">{{ m }}</div>
      </div>
      <div style="margin-top:14px; display:flex; align-items:center; justify-content:space-between;">
        <span>匿名发布</span>
        <van-switch v-model="form.is_anonymous" />
      </div>
    </div>
    <div style="padding: 14px;">
      <van-button block type="primary" :loading="loading" @click="submit">发 布</van-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { hollowApi } from '../api'

const router = useRouter()
const moods = ['焦虑','失眠','孤独','开心','悲伤','紧张','疲惫','迷茫']
const form = reactive({ content: '', mood_tag: '', is_anonymous: true })
const loading = ref(false)

async function submit() {
  if (!form.content.trim()) return showFailToast('内容不能为空')
  loading.value = true
  try {
    await hollowApi.create(form)
    showSuccessToast('已发布 🌟')
    router.replace('/hollow')
  } finally { loading.value = false }
}
</script>

<style scoped>
.moods { display: flex; flex-wrap: wrap; gap: 8px; }
.mood { padding: 6px 14px; border-radius: 999px; background: #f0f1f7; color: #2c2f3a; font-size: 13px; }
.mood.active { background: #7c83ff; color: #fff; }
</style>
