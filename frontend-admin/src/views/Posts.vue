<template>
  <div class="page">
    <div class="page-title">树洞内容</div>
    <el-table :data="items" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="content" label="内容" show-overflow-tooltip />
      <el-table-column prop="mood_tag" label="心情" width="100" />
      <el-table-column label="状态" width="120">
        <template #default="{row}">
          <el-tag :type="row.status==='published'?'success':row.status==='hidden'?'warning':'danger'">
            {{ ({published:'已发布',hidden:'已隐藏',deleted:'已删除'})[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="危机" width="80">
        <template #default="{row}"><el-tag v-if="row.is_crisis" type="danger" size="small">⚠️</el-tag></template>
      </el-table-column>
      <el-table-column prop="like_count" label="点赞" width="70" />
      <el-table-column prop="reply_count" label="回复" width="70" />
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{row}">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="{row}">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button v-if="row.status!=='hidden'" size="small" @click="setStatus(row,'hidden')">隐藏</el-button>
          <el-button v-if="row.status!=='published'" size="small" type="success" @click="setStatus(row,'published')">恢复</el-button>
          <el-button size="small" type="danger" @click="setStatus(row,'deleted')">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next, total" @current-change="load" style="margin-top:14px;"/>

    <!-- 帖子详情弹窗 -->
    <el-dialog title="帖子详情" v-model="detailVisible" width="700px" @close="clearDetail">
      <div v-if="postDetail" class="post-detail">
        <div class="post-header">
          <div class="post-info">
            <span class="label">发布者：</span>
            <span>{{ postDetail.is_anonymous ? '匿名用户' : (postDetail.real_name || postDetail.student_id) }}</span>
          </div>
          <div class="post-info">
            <span class="label">心情：</span>
            <span>{{ postDetail.mood_tag || '无' }}</span>
          </div>
          <div class="post-info">
            <span class="label">状态：</span>
            <el-tag :type="postDetail.status==='published'?'success':postDetail.status==='hidden'?'warning':'danger'">
              {{ ({published:'已发布',hidden:'已隐藏',deleted:'已删除'})[postDetail.status] }}
            </el-tag>
          </div>
          <div class="post-info">
            <span class="label">时间：</span>
            <span>{{ new Date(postDetail.created_at).toLocaleString('zh-CN') }}</span>
          </div>
          <div v-if="postDetail.is_crisis" class="post-info crisis">
            <el-tag type="danger">⚠️ 危机预警</el-tag>
          </div>
        </div>
        <div class="post-content">
          {{ postDetail.content }}
        </div>
        <div class="post-meta">
          <span>点赞：{{ postDetail.like_count }}</span>
          <span>回复：{{ postDetail.reply_count }}</span>
        </div>

        <div class="replies-section">
          <h4>评论列表 ({{ postDetail.replies.length }})</h4>
          <div v-if="postDetail.replies.length === 0" class="empty">暂无评论</div>
          <el-table v-else :data="postDetail.replies" border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
            <el-table-column prop="like_count" label="点赞" width="70" />
            <el-table-column label="匿名" width="70">
              <template #default="{row}">{{ row.is_anonymous ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="160">
              <template #default="{row}">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{row}">
                <el-button v-if="row.status!=='hidden'" size="small" @click="setReplyStatus(row,'hidden')">隐藏</el-button>
                <el-button v-if="row.status!=='published'" size="small" type="success" @click="setReplyStatus(row,'published')">恢复</el-button>
                <el-button size="small" type="danger" @click="setReplyStatus(row,'deleted')">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../api'
const items = ref([]), total = ref(0), page = ref(1)
const detailVisible = ref(false)
const postDetail = ref(null)

async function load() { 
  const r = await adminApi.posts({ page: page.value, size: 20 })
  items.value = r.items
  total.value = r.total 
}

async function setStatus(row, s) { 
  await adminApi.setPostStatus(row.id, s)
  ElMessage.success('已更新')
  load() 
}

async function viewDetail(row) {
  const r = await adminApi.postDetail(row.id)
  postDetail.value = r
  detailVisible.value = true
}

function clearDetail() {
  postDetail.value = null
}

async function setReplyStatus(row, s) {
  await adminApi.setReplyStatus(row.id, s)
  ElMessage.success('已更新')
  if (postDetail.value) {
    const idx = postDetail.value.replies.findIndex(r => r.id === row.id)
    if (idx !== -1) {
      postDetail.value.replies[idx].status = s
    }
  }
}

onMounted(load)
</script>

<style scoped>
.post-detail {
  padding: 10px 0;
}
.post-header {
  margin-bottom: 16px;
}
.post-info {
  margin-bottom: 8px;
}
.post-info .label {
  color: #888;
  margin-right: 8px;
}
.post-info.crisis {
  margin-top: 12px;
}
.post-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
  line-height: 1.8;
  white-space: pre-wrap;
}
.post-meta {
  color: #888;
  font-size: 14px;
  margin-bottom: 16px;
}
.post-meta span {
  margin-right: 16px;
}
.replies-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
.replies-section h4 {
  margin: 0 0 12px;
}
.empty {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style>