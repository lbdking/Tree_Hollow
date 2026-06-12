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
    <div v-for="r in treeReplies" :key="r.id" class="card reply">
      <div class="head"><strong>{{ r.nickname }}</strong> <span class="muted">{{ formatTime(r.created_at) }}</span></div>
      <div class="content">{{ r.content }}</div>
      <div class="ops">
        <span @click="replyTo(r)">回复</span>
      </div>
      <!-- 嵌套回复 -->
      <div v-if="r.children && r.children.length > 0" class="children">
        <div v-for="child in r.children" :key="child.id" class="card reply child">
          <div class="head"><strong>{{ child.nickname }}</strong> <span class="muted">{{ formatTime(child.created_at) }}</span></div>
          <div class="content">{{ child.content }}</div>
          <div class="ops">
            <span @click="replyTo(child)">回复</span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="replies.length === 0" class="empty">还没有人回复，做第一个温暖他的人 🌟</div>

    <!-- 回复输入框 -->
    <div class="reply-bar">
      <div v-if="replyingTo" class="replying-to">
        回复 {{ replyingTo.nickname }}：
      </div>
      <van-field v-model="replyText" placeholder="回复一句温柔的话…" />
      <van-button type="primary" size="small" :loading="loading" @click="submitReply">发送</van-button>
      <van-button v-if="replyingTo" size="small" @click="cancelReply">取消</van-button>
    </div>

    <!-- 举报弹窗 -->
    <van-popup v-model:show="showReportModal" position="center" :style="{ width: '85%' }">
      <div class="report-modal">
        <div class="title">举报理由</div>
        <div class="desc">请简要说明举报原因（管理员将进行审核）</div>
        <van-field 
          v-model="reportReason" 
          placeholder="请输入举报理由" 
          rows="3" 
          type="textarea"
        />
        <div class="actions">
          <van-button size="small" @click="showReportModal = false">取消</van-button>
          <van-button type="primary" size="small" @click="submitReport">提交</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showSuccessToast, showDialog, Dialog, Popup as VanPopup } from 'vant'
import { hollowApi } from '../api'

const route = useRoute()
const id = route.params.id
const post = ref(null)
const replies = ref([])
const replyText = ref('')
const loading = ref(false)
const replyingTo = ref(null)
const showReportModal = ref(false)
const reportReason = ref('')

function formatTime(s) {
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

const treeReplies = computed(() => {
  const map = new Map()
  const roots = []
  replies.value.forEach(r => {
    map.set(r.id, { ...r, children: [] })
  })
  replies.value.forEach(r => {
    if (r.parent_id && r.parent_id > 0) {
      const parent = map.get(r.parent_id)
      if (parent) {
        parent.children.push(map.get(r.id))
      }
    } else {
      roots.push(map.get(r.id))
    }
  })
  return roots
})

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

function replyTo(reply) {
  replyingTo.value = reply
}

function cancelReply() {
  replyingTo.value = null
  replyText.value = ''
}

async function submitReply() {
  if (!replyText.value.trim()) return
  loading.value = true
  try {
    const data = { 
      content: replyText.value, 
      is_anonymous: true 
    }
    if (replyingTo.value) {
      data.parent_id = replyingTo.value.id
    }
    await hollowApi.reply(id, data)
    replyText.value = ''
    replyingTo.value = null
    showSuccessToast('已送达 💗')
    await load()
  } finally { loading.value = false }
}

function report() {
  showReportModal.value = true
}

async function submitReport() {
  if (!reportReason.value.trim()) {
    await showDialog({ title: '提示', message: '请输入举报理由' })
    return
  }
  await hollowApi.report({ target_type: 'post', target_id: post.value.id, reason: reportReason.value })
  showSuccessToast('已提交')
  showReportModal.value = false
  reportReason.value = ''
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; align-items: center; }
.content { font-size: 15px; line-height: 1.7; margin: 10px 0; word-break: break-word; }
.ops { display: flex; gap: 18px; color: #8a90a3; font-size: 13px; }
.crisis { background: linear-gradient(135deg,#fff1f1,#ffe5e5); color: #b03030; line-height: 1.7; }
.reply .head .muted { margin-left: 8px; font-size: 12px; }
.reply .ops { margin-top: 8px; padding-top: 8px; border-top: 1px solid #f0f0f0; }
.reply .ops span { cursor: pointer; color: #4a90e2; }
.reply.child { margin-left: 16px; background: #fafafa; }
.reply.child .content { font-size: 14px; }
.children { margin-top: 8px; }
.reply-bar { position: fixed; bottom: 0; left: 0; right: 0; padding: 8px 12px; background: #fff; box-shadow: 0 -1px 6px rgba(0,0,0,.05); }
.reply-bar .van-cell { flex: 1; border-radius: 999px; background: #f4f5fa; }
.replying-to { color: #8a90a3; font-size: 13px; margin-bottom: 4px; }
.report-modal { padding: 20px; }
.report-modal .title { font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 8px; }
.report-modal .desc { color: #8a90a3; font-size: 14px; text-align: center; margin-bottom: 16px; }
.report-modal .actions { display: flex; gap: 12px; margin-top: 16px; }
.report-modal .actions button { flex: 1; }
</style>
