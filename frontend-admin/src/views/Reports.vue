<template>
  <div class="page">
    <div class="page-title">举报审核</div>
    <el-radio-group v-model="status" @change="load" style="margin-bottom:12px;">
      <el-radio-button value="pending">待处理</el-radio-button>
      <el-radio-button value="handled">已处理</el-radio-button>
      <el-radio-button value="rejected">已驳回</el-radio-button>
    </el-radio-group>
    <el-table :data="items" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="类型" width="80">
        <template #default="{row}">{{ row.target_type==='post'?'帖子':'回复' }}</template>
      </el-table-column>
      <el-table-column prop="target_content" label="目标内容" show-overflow-tooltip />
      <el-table-column prop="reason" label="举报理由" />
      <el-table-column prop="created_at" label="时间" width="160">
        <template #default="{row}">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="{row}">
          <template v-if="row.status==='pending'">
            <el-button size="small" type="warning" @click="handle(row,'hide')">隐藏内容</el-button>
            <el-button size="small" type="danger" @click="handle(row,'delete')">删除内容</el-button>
            <el-button size="small" @click="handle(row,'reject')">驳回</el-button>
          </template>
          <el-tag v-else>已处理</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../api'
const status = ref('pending')
const items = ref([])
async function load() { const r = await adminApi.reports(status.value); items.value = r.items }
async function handle(row, action) { await adminApi.handleReport(row.id, action); ElMessage.success('已处理'); load() }
onMounted(load)
</script>
