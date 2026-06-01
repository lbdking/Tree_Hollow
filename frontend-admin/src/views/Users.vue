<template>
  <div class="page">
    <div class="page-title">用户管理</div>
    <el-table :data="items" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="student_id" label="学号" width="160" />
      <el-table-column prop="real_name" label="姓名" />
      <el-table-column label="角色" width="160">
        <template #default="{row}">
          <el-tag :type="tagType(row.role)">{{ roleText(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="180">
        <template #default="{row}">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template #default="{row}">
          <el-select v-model="row.role" size="small" style="width:140px;" @change="changeRole(row)">
            <el-option value="student" label="学生" />
            <el-option value="counselor" label="咨询师" />
            <el-option value="admin" label="管理员" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      style="margin-top:14px;"
      v-model:current-page="page"
      :page-size="20"
      :total="total"
      @current-change="load"
      layout="prev, pager, next, total"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
function roleText(r){return ({student:'学生',counselor:'咨询师',admin:'管理员'})[r]||r}
function tagType(r){return ({student:'',counselor:'success',admin:'danger'})[r]||''}
function formatTime(s){const d=new Date(s);return d.toLocaleString('zh-CN')}
async function load() {
  const r = await adminApi.users({ page: page.value, size: 20 })
  items.value = r.items
  total.value = r.total
}
async function changeRole(row) {
  await adminApi.setRole(row.id, row.role)
  ElMessage.success('已更新')
}
onMounted(load)
</script>
