<template>
  <div class="page">
    <div class="page-title">咨询师管理 <el-button type="primary" @click="openNew" style="margin-left:14px;">新建咨询师</el-button></div>
    <el-table :data="items" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="title" label="职称" width="180" />
      <el-table-column prop="expertise" label="擅长" />
      <el-table-column prop="rating" label="评分" width="80" />
      <el-table-column label="可约时段数" width="120">
        <template #default="{row}">{{ row.available_slots.length }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{row}">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">下架</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="show" :title="form.id?'编辑咨询师':'新建咨询师'" width="640px">
      <el-form :model="form" label-width="100px">
        <el-form-item v-if="!form.id" label="绑定用户ID">
          <el-input v-model.number="form.user_id" placeholder="先在用户管理把对应账号设为咨询师" />
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="职称"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="头像"><el-input v-model="form.avatar" /></el-form-item>
        <el-form-item label="擅长"><el-input v-model="form.expertise" placeholder="逗号分隔" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="form.introduction" type="textarea" rows="3" /></el-form-item>
        <el-form-item label="可约时段">
          <div style="width:100%;">
            <div v-for="(s,i) in form.available_slots" :key="i" style="display:flex;gap:6px;margin-bottom:6px;">
              <el-input v-model="s.date" placeholder="2026-06-05" style="width:160px;" />
              <el-input v-model="timesStr[i]" placeholder="10:00,14:00,16:00" @blur="updateTimes(i)" style="flex:1;" />
              <el-button type="danger" plain @click="form.available_slots.splice(i,1); timesStr.splice(i,1)">×</el-button>
            </div>
            <el-button @click="addSlot">+ 增加日期</el-button>
          </div>
        </el-form-item>
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
import { counselorApi } from '../api'

const items = ref([])
const show = ref(false)
const timesStr = ref([])
const empty = () => ({ id:null, user_id:null, name:'', title:'校园心理老师', avatar:'', expertise:'', introduction:'', available_slots:[] })
const form = reactive(empty())

async function load() { const r = await counselorApi.list(); items.value = r.items }
function openNew() { Object.assign(form, empty()); timesStr.value = []; show.value = true }
function openEdit(row) {
  Object.assign(form, JSON.parse(JSON.stringify(row)))
  timesStr.value = form.available_slots.map(s => (s.times||[]).join(','))
  show.value = true
}
function addSlot() { form.available_slots.push({ date:'', times:[] }); timesStr.value.push('') }
function updateTimes(i) {
  form.available_slots[i].times = timesStr.value[i].split(',').map(s=>s.trim()).filter(Boolean)
}
async function save() {
  for (let i=0; i<timesStr.value.length; i++) updateTimes(i)
  if (form.id) await counselorApi.update(form.id, form)
  else await counselorApi.create(form)
  ElMessage.success('已保存')
  show.value = false
  load()
}
async function remove(row) {
  await ElMessageBox.confirm(`下架咨询师 ${row.name}？`, '提示', { type:'warning' })
  await counselorApi.remove(row.id)
  ElMessage.success('已下架')
  load()
}
onMounted(load)
</script>
