<template>
  <div class="page">
    <div class="page-title">心理科普管理 <el-button type="primary" @click="openNew" style="margin-left:14px;">新建</el-button></div>
    <el-table :data="items" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column label="类型" width="100">
        <template #default="{row}">{{ row.content_type==='video'?'视频':'文章' }}</template>
      </el-table-column>
      <el-table-column prop="author" label="作者" width="120" />
      <el-table-column prop="view_count" label="浏览" width="80" />
      <el-table-column label="操作" width="180">
        <template #default="{row}">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="show" :title="form.id?'编辑科普':'新建科普'" width="640px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类">
            <el-option v-for="c in categories" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.content_type">
            <el-radio value="article">文章</el-radio>
            <el-radio value="video">视频</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="封面"><el-input v-model="form.cover" placeholder="图片 URL" /></el-form-item>
        <el-form-item v-if="form.content_type==='video'" label="视频"><el-input v-model="form.video_url" placeholder="视频 URL" /></el-form-item>
        <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" rows="2" /></el-form-item>
        <el-form-item label="正文"><el-input v-model="form.content" type="textarea" rows="6" /></el-form-item>
        <el-form-item label="作者"><el-input v-model="form.author" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="show=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { articleApi } from '../api'
const items = ref([])
const show = ref(false)
const categories = ['焦虑','抑郁','睡眠','冥想','自我成长','学业','人际']
const empty = () => ({ id:null, title:'', category:'焦虑', content_type:'article', cover:'', video_url:'', summary:'', content:'', author:'树洞编辑部', is_published:true })
const form = reactive(empty())

async function load() { const r = await articleApi.list({ page:1, size:100 }); items.value = r.items }
function openNew() { Object.assign(form, empty()); show.value = true }
function openEdit(row) { Object.assign(form, row); show.value = true }
async function save() {
  if (form.id) await articleApi.update(form.id, form)
  else await articleApi.create(form)
  ElMessage.success('已保存')
  show.value = false
  load()
}
async function remove(row) {
  await ElMessageBox.confirm(`确认删除《${row.title}》？`, '提示', { type: 'warning' })
  await articleApi.remove(row.id)
  ElMessage.success('已删除')
  load()
}
onMounted(load)
</script>
