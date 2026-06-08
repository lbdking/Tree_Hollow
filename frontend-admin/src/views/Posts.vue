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
      <el-table-column label="操作" width="200">
        <template #default="{row}">
          <el-button v-if="row.status!=='hidden'" size="small" @click="setStatus(row,'hidden')">隐藏</el-button>
          <el-button v-if="row.status!=='published'" size="small" type="success" @click="setStatus(row,'published')">恢复</el-button>
          <el-button size="small" type="danger" @click="setStatus(row,'deleted')">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next, total" @current-change="load" style="margin-top:14px;"/>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../api'
const items = ref([]), total = ref(0), page = ref(1)
async function load() { const r = await adminApi.posts({ page: page.value, size: 20 }); items.value = r.items; total.value = r.total }
async function setStatus(row, s) { await adminApi.setPostStatus(row.id, s); ElMessage.success('已更新'); load() }
onMounted(load)
</script>
