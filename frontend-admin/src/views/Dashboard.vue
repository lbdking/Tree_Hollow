<template>
  <div class="page">
    <div class="page-title">数据看板</div>
    <el-row :gutter="16">
      <el-col v-for="c in cards" :key="c.label" :span="6">
        <el-card class="stat" :body-style="{padding:'18px'}">
          <div class="lbl">{{ c.label }}</div>
          <div class="val" :style="{color: c.color}">{{ c.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="14">
        <el-card>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin:0;">发帖趋势</h4>
            <el-radio-group v-model="postsPeriod" @change="loadPostsTrend" size="small">
              <el-radio-button value="day">日</el-radio-button>
              <el-radio-button value="week">周</el-radio-button>
              <el-radio-button value="month">月</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="postsLineRef" style="height:280px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin:0;">用户增长趋势</h4>
            <el-radio-group v-model="usersPeriod" @change="loadUsersTrend" size="small">
              <el-radio-button value="day">日</el-radio-button>
              <el-radio-button value="week">周</el-radio-button>
              <el-radio-button value="month">月</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="usersLineRef" style="height:280px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px;">
      <el-col :span="14">
        <el-card>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin:0;">心情分布</h4>
            <el-select 
              v-model="selectedAgeGroup" 
              placeholder="选择年龄段"
              style="width: 140px;"
              @change="loadMoodDistribution"
            >
              <el-option label="全部" value="all" />
              <el-option 
                v-for="age in ageGroups" 
                :key="age.key" 
                :label="age.group + ' (' + age.count + '人)'" 
                :value="age.key" 
              />
            </el-select>
          </div>
          <div ref="pieRef" style="height:280px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <h4 style="margin:0 0 12px;">年龄段分布</h4>
          <div ref="ageBarRef" style="height:280px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { adminApi } from '../api'

const data = ref({ summary: {}, posts_trend: [], users_trend: [], mood_distribution: [], age_groups: [] })
const postsLineRef = ref(null)
const usersLineRef = ref(null)
const pieRef = ref(null)
const ageBarRef = ref(null)
const selectedAgeGroup = ref('all')
const ageGroups = ref([])
const postsPeriod = ref('day')
const usersPeriod = ref('day')
let postsChart = null
let usersChart = null
let pieChart = null
let ageBarChart = null

const cards = computed(() => {
  const s = data.value.summary
  return [
    { label: '用户总数', value: s.user_total || 0, color: '#5057ff' },
    { label: '树洞总数', value: s.post_total || 0, color: '#7c83ff' },
    { label: '回复总数', value: s.reply_total || 0, color: '#1ca866' },
    { label: '危机预警', value: s.crisis_total || 0, color: '#d94545' },
    { label: '预约总数', value: s.appointment_total || 0, color: '#b58a00' },
    { label: '科普内容', value: s.article_total || 0, color: '#0891b2' },
    { label: '互助小组', value: s.group_total || 0, color: '#9333ea' },
    { label: '待处理举报', value: s.pending_reports || 0, color: '#dc2626' }
  ]
})

const initCharts = () => {
  updatePostsChart()
  updateUsersChart()
  updatePieChart()
  updateAgeBarChart()
}

const updatePostsChart = () => {
  if (!postsChart) {
    postsChart = echarts.init(postsLineRef.value)
  }
  postsChart.setOption({
    tooltip: {},
    xAxis: { type: 'category', data: data.value.posts_trend.map(p => p.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', smooth: true, data: data.value.posts_trend.map(p => p.count), areaStyle: {}, itemStyle: { color: '#7c83ff' } }]
  }, true)
}

const updateUsersChart = () => {
  if (!usersChart) {
    usersChart = echarts.init(usersLineRef.value)
  }
  usersChart.setOption({
    tooltip: {},
    xAxis: { type: 'category', data: data.value.users_trend.map(p => p.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', smooth: true, data: data.value.users_trend.map(p => p.count), areaStyle: {}, itemStyle: { color: '#1ca866' } }]
  }, true)
}

const updatePieChart = () => {
  if (!pieChart) {
    pieChart = echarts.init(pieRef.value)
  }
  pieChart.setOption({
    tooltip: { 
      trigger: 'item',
      formatter: '{b}: {c}次 ({d}%)'
    },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      label: {
        show: true,
        formatter: '{b}\n{c}次 ({d}%)'
      },
      labelLine: {
        show: true
      },
      data: data.value.mood_distribution.map(m => ({ 
        name: m.mood, 
        value: m.count,
        percent: m.percentage 
      }))
    }]
  }, true)
}

const updateAgeBarChart = () => {
  if (!ageBarChart) {
    ageBarChart = echarts.init(ageBarRef.value)
  }
  ageBarChart.setOption({
    tooltip: {},
    xAxis: { 
      type: 'category', 
      data: data.value.age_groups.map(a => a.group) 
    },
    yAxis: { type: 'value' },
    series: [{ 
      type: 'bar', 
      data: data.value.age_groups.map(a => a.count),
      itemStyle: {
        color: '#5057ff',
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }, true)
}

const loadCharts = async () => {
  const params = { 
    posts_period: postsPeriod.value,
    users_period: usersPeriod.value,
    ...(selectedAgeGroup.value !== 'all' ? { age_group: selectedAgeGroup.value } : {})
  }
  data.value = await adminApi.dashboard(params)
  ageGroups.value = data.value.age_groups || []
  updatePostsChart()
  updateUsersChart()
  updatePieChart()
  updateAgeBarChart()
}

const loadPostsTrend = async () => {
  const params = { 
    posts_period: postsPeriod.value,
    users_period: usersPeriod.value,
    ...(selectedAgeGroup.value !== 'all' ? { age_group: selectedAgeGroup.value } : {})
  }
  data.value = await adminApi.dashboard(params)
  ageGroups.value = data.value.age_groups || []
  updatePostsChart()
  updatePieChart()
  updateAgeBarChart()
}

const loadUsersTrend = async () => {
  const params = { 
    posts_period: postsPeriod.value,
    users_period: usersPeriod.value,
    ...(selectedAgeGroup.value !== 'all' ? { age_group: selectedAgeGroup.value } : {})
  }
  data.value = await adminApi.dashboard(params)
  ageGroups.value = data.value.age_groups || []
  updateUsersChart()
}

const loadMoodDistribution = async () => {
  const params = { 
    posts_period: postsPeriod.value,
    users_period: usersPeriod.value,
    ...(selectedAgeGroup.value !== 'all' ? { age_group: selectedAgeGroup.value } : {})
  }
  data.value = await adminApi.dashboard(params)
  ageGroups.value = data.value.age_groups || []
  updatePieChart()
}

onMounted(async () => {
  data.value = await adminApi.dashboard({ posts_period: postsPeriod.value, users_period: usersPeriod.value })
  ageGroups.value = data.value.age_groups || []
  initCharts()
})
</script>

<style scoped>
.stat .lbl { color: #888; font-size: 13px; }
.stat .val { font-size: 28px; font-weight: 700; margin-top: 6px; }
.el-col { margin-bottom: 12px; }
</style>