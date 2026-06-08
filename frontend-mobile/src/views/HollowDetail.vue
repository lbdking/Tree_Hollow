<template>
  <div class="page">
    <van-nav-bar title="树洞详情" left-arrow @click-left="$router.back()" />
    <div v-if="post" class="card">
      <div class="head">
        <strong>{{ post.nickname }}</strong>
        <span v-if="post.mood_tag" class="tag" style="margin-left:8px;">{{ post.mood_tag }}</span>
      </div>
      <div class="content">{{ post.content }}</div>
      <div class="ops">
        <span @click="like">{{ post.is_liked ? '❤️' : '🤍' }} {{ post.like_count }}</span>
        <span>💬 {{ post.reply_count }}</span>
        <span style="margin-left:auto;color:#d94545;" @click="report">举报</span>
      </div>
    </div>

    <div v-if="post && post.is_crisis" class="card crisis">
      💗 我们注意到你提到了一些困难话题。如果你正在经历强烈痛苦，请记住你不是一个人：<br/>
      • 全国心理援助热线 400-161-9995<br/>
      • 也可以去【预约咨询】，校园老师随时陪伴你。
    </div>

    <div class="section-title">温暖的回复</div>
    <div v-for="r in rootReplies" :key="r.id" class="card reply">
      <div class="head">
        <strong>{{ r.nickname }}</strong> 
        <span class="muted">{{ formatTime(r.created_at) }}</span>
        <span class="reply-btn" @click="replyTo(r)">回复</span>
      </div>
      <div class="content">{{ r.content }}</div>
      <div class="ops-bar">
        <span @click="likeReply(r)">🤍 {{ r.like_count }}</span>
      </div>
      <div v-if="getChildren(r.id).length > 0" class="children">
        <div v-for="child in getChildren(r.id)" :key="child.id" class="card reply child">
          <div class="head">
            <strong>{{ child.nickname }}</strong> 
            <span class="muted">{{ formatTime(child.created_at) }}</span>
            <span class="reply-btn" @click="replyTo(child)">回复</span>
          </div>
          <div class="content">{{ child.content }}</div>
          <div class="ops-bar">
            <span @click="likeReply(child)">🤍 {{ child.like_count }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="replies.length === 0" class="empty">还没有人回复，做第一个温暖他的人 🌟</div>

    <div class="reply-bar">
      <van-field v-model="replyText" :placeholder="replyTarget ? `回复 ${replyTarget.nickname}…` : '回复一句温柔的话…'" />
      <van-button type="primary" size="small" :loading="loading" @click="submitReply">发送</van-button>
      <van-button v-if="replyTarget" size="small" @click="cancelReply">取消</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showSuccessToast, showDialog } from 'vant'
import { hollowApi } from '../api'

const route = useRoute()
const id = route.params.id
const post = ref(null)
const replies = ref([])
const replyText = ref('')
const replyTarget = ref(null)
const loading = ref(false)

function formatTime(s) {
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

const rootReplies = computed(() => {
  return replies.value.filter(r => r.parent_id === 0)
})

function getChildren(parentId) {
  return replies.value.filter(r => r.parent_id === parentId)
}

async function load() {
  post.value = await hollowApi.detail(id)
  const res = await hollowApi.replies(id)
  replies.value = res.items
}

async function like() {
  const r = await hollowApi.like('post', post.value.id)
  post.value.is_liked = r.liked
  post.value.like_count += r.delta
}

async function likeReply(r) {
  const res = await hollowApi.like('reply', r.id)
  r.like_count += res.delta
}

function replyTo(r) {
  replyTarget.value = r
}

function cancelReply() {
  replyTarget.value = null
  replyText.value = ''
}

async function submitReply() {
  if (!replyText.value.trim()) return
  loading.value = true
  try {
    await hollowApi.reply(id, { 
      content: replyText.value, 
      is_anonymous: true,
      parent_id: replyTarget.value ? replyTarget.value.id : 0
    })
    replyText.value = ''
    replyTarget.value = null
    showSuccessToast('已送达 💗')
    await load()
  } finally { loading.value = false }
}

async function report() {
  const reason = await showDialog({ title: '举报理由', message: '请简要说明（管理员将进行审核）', showCancelButton: true, confirmButtonText: '提交' }).then(()=>'内容不当').catch(()=>null)
  if (!reason) return
  await hollowApi.report({ target_type: 'post', target_id: post.value.id, reason })
  showSuccessToast('已提交')
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; align-items: center; }
.content { font-size: 15px; line-height: 1.7; margin: 10px 0; word-break: break-word; }
.ops { display: flex; gap: 18px; color: #8a90a3; font-size: 13px; }
.crisis { background: linear-gradient(135deg,#fff1f1,#ffe5e5); color: #b03030; line-height: 1.7; }
.reply .head .muted { margin-left: 8px; font-size: 12px; }
.reply-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; gap: 8px; padding: 8px 12px; background: #fff; box-shadow: 0 -1px 6px rgba(0,0,0,.05); }
.reply-bar .van-cell { flex: 1; border-radius: 999px; background: #f4f5fa; }
.reply-btn { margin-left: auto; color: #7c83ff; font-size: 12px; }
.ops-bar { display: flex; gap: 12px; color: #8a90a3; font-size: 12px; margin-top: 8px; }
.children { margin-left: 20px; margin-top: 8px; }
.children .reply.child { background: #f8f9fc; border-radius: 8px; }
</style>
