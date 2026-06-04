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
          <h4 style="margin:0 0 12px;">近 7 日发帖趋势</h4>
          <div ref="lineRef" style="height:280px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
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
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import * as echarts from 'echarts'
import { adminApi } from '../api'

const data = ref({ summary: {}, posts_week: [], mood_distribution: [], age_groups: [] })
const lineRef = ref(null)
const pieRef = ref(null)
const selectedAgeGroup = ref('all')
const ageGroups = ref([])

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
  // 折线图
  const line = echarts.init(lineRef.value)
  line.setOption({
    tooltip: {},
    xAxis: { type: 'category', data: data.value.posts_week.map(p => p.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', smooth: true, data: data.value.posts_week.map(p => p.count), areaStyle: {}, itemStyle: { color: '#7c83ff' } }]
  })

  // 饼状图（显示百分比）
  updatePieChart()
}

const updatePieChart = () => {
  const pie = echarts.init(pieRef.value)
  pie.setOption({
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
  })
}

const loadMoodDistribution = async () => {
  const params = selectedAgeGroup.value === 'all' ? {} : { age_group: selectedAgeGroup.value }
  data.value = await adminApi.dashboard(params)
  ageGroups.value = data.value.age_groups || []
  updatePieChart()
}

onMounted(async () => {
  data.value = await adminApi.dashboard()
  ageGroups.value = data.value.age_groups || []
  initCharts()
})
</script>

<style scoped>
.stat .lbl { color: #888; font-size: 13px; }
.stat .val { font-size: 28px; font-weight: 700; margin-top: 6px; }
.el-col { margin-bottom: 12px; }
</style>
