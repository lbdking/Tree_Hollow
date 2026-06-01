<template>
  <div class="ai-page">
    <van-nav-bar title="树洞 AI" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="cluster-o" size="20" :badge="enabledKbCount || ''" @click="showKb = true" />
        &nbsp;
        <span style="font-size:13px;" @click="showHistory = true">历史</span>
      </template>
    </van-nav-bar>

    <div class="messages" ref="msgRef">
      <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
        <div class="bubble">
          <div v-if="m.ragHits && m.ragHits.length" class="rag-meta">
            <div class="rag-title">📎 引用了 {{ m.ragHits.length }} 个片段</div>
            <div v-for="(h, idx) in m.ragHits" :key="idx" class="rag-hit">
              <strong>{{ h.filename }}</strong> · 相似度 {{ h.score }}
              <div class="rag-preview">{{ h.preview }}…</div>
            </div>
          </div>
          <span>{{ m.content || (m.loading ? '正在思考…' : '') }}</span>
        </div>
      </div>
      <!-- 快捷入口（仅在欢迎消息状态显示） -->
      <div v-if="messages.length === 1 && messages[0].isWelcome" class="quick-prompts">
        <div class="qp-title">💡 你可以试试问我：</div>
        <div class="qp-list">
          <div class="qp-item" v-for="q in quickPrompts" :key="q" @click="quickAsk(q)">{{ q }}</div>
        </div>
      </div>
    </div>

    <div class="rag-toggle">
      <van-switch v-model="useRag" size="18" /> <span>使用知识库</span>
      <span class="kb-link" @click="showKb = true">📁 上传个人文件 ({{ kbFiles.length }})</span>
    </div>

    <div class="input-bar">
      <van-field v-model="text" placeholder="说点什么吧…" @keyup.enter="send" />
      <van-button type="primary" :loading="sending" :disabled="!text.trim()" @click="send">发送</van-button>
    </div>

    <!-- 历史会话抽屉 -->
    <van-popup v-model:show="showHistory" position="left" :style="{ width: '78%', height: '100%' }">
      <div style="padding:14px;">
        <van-button block type="primary" size="small" @click="newSession">＋ 新对话</van-button>
        <div v-for="s in sessions" :key="s.id" class="ses" @click="switchSession(s.id)">
          <div class="title">{{ s.title }}</div>
          <div class="muted">{{ formatTime(s.updated_at) }}</div>
        </div>
      </div>
    </van-popup>

    <!-- 知识库抽屉 -->
    <van-popup v-model:show="showKb" position="right" :style="{ width: '88%', height: '100%' }">
      <div class="kb-panel">
        <div class="kb-head">
          <strong>📚 我的知识库</strong>
          <van-icon name="cross" @click="showKb = false" />
        </div>

        <van-uploader :after-read="onUpload" :max-count="1" accept=".pdf,.docx,.txt,.md">
          <van-button block type="primary" :loading="uploading">上传文件 (PDF/DOCX/TXT/MD)</van-button>
        </van-uploader>
        <div class="muted" style="margin-top:6px;">≤ 20MB · 上传后自动切片 + 向量化</div>

        <div v-if="!kbFiles.length" class="empty" style="padding:30px 0;">
          <div style="font-size:36px;">📂</div>
          <div>还没有知识库文件</div>
          <div class="muted" style="margin-top:6px;">上传后 AI 会优先参考你的资料回答</div>
        </div>

        <div v-for="f in kbFiles" :key="f.id" class="kb-item">
          <div class="kb-info">
            <div class="kb-name">{{ f.filename }}</div>
            <div class="muted">
              {{ formatSize(f.size_bytes) }} · {{ f.chunk_count }} 片段 ·
              <span :class="'st-' + f.status">{{ statusText(f.status) }}</span>
            </div>
            <div v-if="f.error_msg" class="err">{{ f.error_msg }}</div>
          </div>
          <div class="kb-ops">
            <van-switch v-model="f.is_enabled" size="18" @change="onToggle(f)" />
            <van-icon name="delete-o" size="18" color="#d94545" @click="onDelete(f)" />
          </div>
        </div>

        <div v-if="kbFiles.length" class="search-area">
          <div class="muted" style="margin:14px 0 6px;">🔍 检索预览（不发送给 AI）</div>
          <van-field v-model="searchText" placeholder="输入关键词测试检索效果" @keyup.enter="doSearch" />
          <van-button size="small" @click="doSearch" :loading="searching">检索</van-button>
          <div v-for="(h,i) in searchHits" :key="i" class="hit">
            <div><strong>{{ h.filename }}</strong> <span class="muted">相似度 {{ h.score.toFixed(3) }}</span></div>
            <div>{{ h.text }}</div>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { showSuccessToast, showFailToast } from 'vant'
import { aiApi, knowledgeApi } from '../api'

const messages = ref([])
const sessions = ref([])
const text = ref('')
const sending = ref(false)
const sessionId = ref(null)
const showHistory = ref(false)
const showKb = ref(false)
const msgRef = ref(null)
const useRag = ref(true)

// 知识库
const kbFiles = ref([])
const uploading = ref(false)
const searchText = ref('')
const searchHits = ref([])
const searching = ref(false)

const enabledKbCount = computed(() =>
  kbFiles.value.filter(f => f.is_enabled && f.status === 'ready').length
)

const userInfo = JSON.parse(localStorage.getItem('th_user') || '{}')

const quickPrompts = [
  '我最近压力很大，怎么办？',
  '失眠睡不着，有什么建议吗？',
  '怎么和家人沟通让我不开心的事？',
  '介绍一下树洞的功能',
  '帮我做一次呼吸放松引导'
]

function buildWelcomeText() {
  const name = userInfo.real_name || userInfo.student_id || '同学'
  const kbHint = enabledKbCount.value > 0
    ? `\n\n📚 我看到你已经上传了 ${enabledKbCount.value} 份个人资料，聊到相关内容时我会优先参考它们。`
    : ''
  return (
    `嗨，${name} 👋 我是 **树洞 AI**，欢迎来到这里 🌳\n\n` +
    `这是一个属于你的安全树洞，不管是学业焦虑、人际困扰、情绪低落，还是只是想找人说说话——我都会温柔地陪着你 💗\n\n` +
    `🌟 我可以帮你：\n` +
    `• 倾听你的烦恼，给予理解和共情\n` +
    `• 引导你做呼吸练习、情绪疏导\n` +
    `• 推荐校园心理咨询师 / 心理援助热线\n` +
    `• 结合你上传的资料给出更贴切的回答（RAG 检索）\n\n` +
    `💡 提示：我不会做医学诊断，遇到严重困扰请及时寻求专业帮助。` +
    kbHint +
    `\n\n准备好了吗？告诉我，今天发生了什么？`
  )
}

function ensureWelcome() {
  // 仅在「无历史会话 + 没切换到旧会话 + 当前消息为空」时插入欢迎语
  if (sessionId.value || messages.value.length > 0) return
  messages.value = [{ role: 'assistant', content: buildWelcomeText(), isWelcome: true }]
}

function quickAsk(q) {
  text.value = q
  send()
}

function formatTime(s) {
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
function formatSize(b) {
  if (b < 1024) return b + ' B'
  if (b < 1024*1024) return (b/1024).toFixed(1) + ' KB'
  return (b/1024/1024).toFixed(1) + ' MB'
}
function statusText(s){return ({ready:'就绪',processing:'处理中',failed:'失败'})[s]||s}

async function loadSessions() {
  const r = await aiApi.sessions()
  sessions.value = r.items
}

async function loadKb() {
  const r = await knowledgeApi.list()
  kbFiles.value = r.items
}

async function newSession() {
  sessionId.value = null
  messages.value = []
  showHistory.value = false
  ensureWelcome()
}

async function switchSession(sid) {
  sessionId.value = sid
  showHistory.value = false
  const r = await aiApi.messages(sid)
  messages.value = r.items.filter(m => m.role !== 'system')
  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (msgRef.value) msgRef.value.scrollTop = msgRef.value.scrollHeight
}

async function send() {
  const content = text.value.trim()
  if (!content || sending.value) return
  text.value = ''
  sending.value = true
  // 第一次发消息：去掉欢迎语标记
  if (messages.value.length === 1 && messages.value[0].isWelcome) {
    messages.value = []
  }
  messages.value.push({ role: 'user', content })
  const ai = { role: 'assistant', content: '', loading: true, ragHits: [] }
  messages.value.push(ai)
  await scrollToBottom()

  try {
    await aiApi.streamChat(sessionId.value, content, {
      useRag: useRag.value,
      onSession: sid => { sessionId.value = sid },
      onRag: hits => { ai.ragHits = hits || [] },
      onDelta: d => {
        ai.loading = false
        ai.content += d
        scrollToBottom()
      },
      onDone: () => {
        ai.loading = false
        loadSessions()
      },
      onError: e => {
        ai.loading = false
        ai.content = ai.content || ('AI 服务异常: ' + e.message)
      }
    })
  } finally { sending.value = false }
}

// ---------- 知识库操作 ----------
async function onUpload(fileObj) {
  uploading.value = true
  try {
    await knowledgeApi.upload(fileObj.file)
    showSuccessToast('上传成功 ✨')
    await loadKb()
  } catch (e) {
    showFailToast('上传失败')
  } finally { uploading.value = false }
}

async function onToggle(f) {
  await knowledgeApi.toggle(f.id)
}

async function onDelete(f) {
  await knowledgeApi.remove(f.id)
  showSuccessToast('已删除')
  await loadKb()
}

async function doSearch() {
  if (!searchText.value.trim()) return
  searching.value = true
  try {
    const r = await knowledgeApi.search(searchText.value, 4)
    searchHits.value = r.items
  } finally { searching.value = false }
}

onMounted(async () => {
  await loadSessions()
  await loadKb()
  ensureWelcome()
})
</script>

<style scoped>
.ai-page { display: flex; flex-direction: column; height: 100vh; background: #f4f5fa; }
.messages { flex: 1; overflow-y: auto; padding: 14px; }
.welcome { text-align: center; color: #8a90a3; padding-top: 60px; }
.kb-hint { color: #5057ff !important; font-weight: 500; margin-top: 16px; }
.msg { display: flex; margin: 8px 0; }
.msg.user { justify-content: flex-end; }
.bubble { max-width: 80%; padding: 10px 14px; border-radius: 14px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
.msg.user .bubble { background: #7c83ff; color: #fff; border-top-right-radius: 4px; }
.msg.assistant .bubble { background: #fff; color: #2c2f3a; border-top-left-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,.04); }

.rag-meta { background: #f0f4ff; border-radius: 8px; padding: 8px 10px; margin-bottom: 8px; font-size: 12px; }
.rag-title { color: #5057ff; font-weight: 600; margin-bottom: 4px; }
.rag-hit { padding: 4px 0; border-top: 1px dashed #d6dafd; }
.rag-hit:first-of-type { border-top: none; }
.rag-preview { color: #555; margin-top: 2px; }

.quick-prompts { margin: 14px 6px 0; }
.qp-title { color: #8a90a3; font-size: 12px; margin-bottom: 8px; padding-left: 6px; }
.qp-list { display: flex; flex-direction: column; gap: 8px; }
.qp-item { padding: 10px 14px; background: #fff; border-radius: 14px; font-size: 14px; color: #5057ff; box-shadow: 0 1px 4px rgba(124,131,255,.08); border: 1px solid #ecedff; }
.qp-item:active { background: #f4f5fa; }

.rag-toggle { display: flex; align-items: center; gap: 6px; padding: 6px 14px; font-size: 13px; color: #555; background: #fff; border-top: 1px solid #eee; }
.kb-link { margin-left: auto; color: #7c83ff; }

.input-bar { display: flex; gap: 8px; padding: 8px 12px; background: #fff; border-top: 1px solid #eee; }
.input-bar .van-cell { flex: 1; border-radius: 999px; background: #f4f5fa; }

.ses { padding: 12px; border-bottom: 1px solid #f0f0f0; }
.ses .title { font-weight: 500; }

.kb-panel { padding: 16px; height: 100%; overflow-y: auto; }
.kb-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; font-size: 16px; }
.kb-item { display: flex; gap: 10px; align-items: center; padding: 10px; background: #fff; border-radius: 10px; margin-top: 10px; }
.kb-info { flex: 1; min-width: 0; }
.kb-name { font-weight: 500; font-size: 14px; word-break: break-all; }
.kb-ops { display: flex; gap: 12px; align-items: center; }
.st-ready { color: #1ca866; }
.st-processing { color: #b58a00; }
.st-failed { color: #d94545; }
.err { color: #d94545; font-size: 12px; margin-top: 4px; }
.empty { text-align: center; color: #8a90a3; }

.search-area { margin-top: 20px; padding-top: 14px; border-top: 1px dashed #ddd; }
.search-area .van-cell { background: #f4f5fa; border-radius: 8px; }
.hit { padding: 8px 10px; background: #fff; border-radius: 8px; margin-top: 8px; font-size: 13px; line-height: 1.5; }
.muted { color: #8a90a3; font-size: 12px; }
</style>
