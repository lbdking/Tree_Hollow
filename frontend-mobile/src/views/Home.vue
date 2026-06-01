<template>
  <div class="page home">
    <div class="hero">
      <div class="greet">{{ greet }}，{{ user.real_name || user.student_id }} 👋</div>
      <div class="sub">愿你被温柔以待</div>
    </div>

    <div class="quick">
      <div class="quick-item" @click="$router.push('/hollow/post')">
        <div class="ic" style="background:#ffe8ec;">✍️</div>
        <div>写树洞</div>
      </div>
      <div class="quick-item" @click="$router.push('/breathing')">
        <div class="ic" style="background:#e3f4ff;">🫧</div>
        <div>呼吸</div>
      </div>
      <div class="quick-item" @click="$router.push('/mood')">
        <div class="ic" style="background:#fff3d6;">📅</div>
        <div>打卡</div>
      </div>
      <div class="quick-item" @click="$router.push('/ai')">
        <div class="ic" style="background:#ecedff;">🤖</div>
        <div>AI 倾听</div>
      </div>
      <div class="quick-item" @click="$router.push('/counselors')">
        <div class="ic" style="background:#e6fff0;">👩‍⚕️</div>
        <div>预约咨询</div>
      </div>
    </div>

    <div class="section-title">今日心理科普 <span class="more" @click="$router.push('/content')">更多</span></div>
    <div v-for="a in articles" :key="a.id" class="card article" @click="$router.push(`/content/${a.id}`)">
      <img v-if="a.cover" :src="a.cover" class="cover" />
      <div class="info">
        <div class="title">{{ a.title }}</div>
        <div class="muted">{{ a.summary }}</div>
        <div class="meta"><span class="tag">{{ a.category }}</span> · {{ a.author }}</div>
      </div>
    </div>

    <div class="section-title">最新树洞 <span class="more" @click="$router.push('/hollow')">更多</span></div>
    <div v-for="p in posts" :key="p.id" class="card post" @click="$router.push(`/hollow/${p.id}`)">
      <div class="head">
        <div class="nick">{{ p.nickname }}</div>
        <div v-if="p.mood_tag" class="tag">{{ p.mood_tag }}</div>
      </div>
      <div class="content">{{ p.content }}</div>
      <div class="muted">💬 {{ p.reply_count }} · ❤️ {{ p.like_count }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { contentApi, hollowApi } from '../api'
const user = JSON.parse(localStorage.getItem('th_user') || '{}')
const articles = ref([])
const posts = ref([])
const greet = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 11) return '早安'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚安'
})
onMounted(async () => {
  const a = await contentApi.articles({ page: 1, size: 3 })
  articles.value = a.items
  const p = await hollowApi.list({ page: 1, size: 5 })
  posts.value = p.items
})
</script>

<style scoped>
.hero { padding: 24px 18px 16px; background: linear-gradient(135deg,#a8aeff,#7c83ff); color: #fff; border-radius: 0 0 22px 22px; }
.greet { font-size: 20px; font-weight: 600; }
.sub { font-size: 13px; opacity: .85; margin-top: 4px; }
.quick { display: grid; grid-template-columns: repeat(5,1fr); gap: 8px; padding: 16px 14px; }
.quick-item { display: flex; flex-direction: column; align-items: center; gap: 6px; font-size: 12px; color: #2c2f3a; }
.ic { width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 22px; }
.section-title .more { color: #7c83ff; font-size: 13px; font-weight: normal; }
.article { display: flex; gap: 12px; }
.article .cover { width: 86px; height: 86px; border-radius: 10px; object-fit: cover; }
.article .info { flex: 1; min-width: 0; }
.article .title { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
.article .meta { margin-top: 6px; }
.post .head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.post .nick { font-size: 13px; color: #7c83ff; font-weight: 500; }
.post .content { font-size: 14px; line-height: 1.6; margin-bottom: 6px; word-break: break-word; }
</style>
