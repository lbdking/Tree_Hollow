<template>
  <div class="page breath">
    <van-nav-bar title="呼吸训练" left-arrow @click-left="$router.back()" :border="false" />
    <div class="hint">{{ phaseText }}</div>
    <div class="circle-wrap">
      <div class="circle" :style="circleStyle"></div>
    </div>
    <div class="counter">{{ count }} 秒</div>
    <div class="cycles">已完成 <strong>{{ cycles }}</strong> 个循环 · 总时长 {{ totalSec }} 秒</div>
    <div class="actions">
      <van-button v-if="!running" round type="primary" size="large" @click="start">{{ totalSec > 0 ? '再来一次' : '开始训练' }}</van-button>
      <van-button v-else round type="warning" size="large" @click="stop">结束训练</van-button>
    </div>
    <div class="card tips">
      <strong>4-4-4 呼吸法</strong>
      <p>· 吸气 4 秒（让小球变大）</p>
      <p>· 屏息 4 秒</p>
      <p>· 呼气 4 秒（让小球变小）</p>
      <p>每个完整循环 12 秒，建议持续 5-10 分钟 🌿</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { contentApi } from '../api'
import { showSuccessToast, showFailToast } from 'vant'

const PHASES = [
  { name: '吸 气', dur: 4, scale: 1.6 },
  { name: '屏 息', dur: 4, scale: 1.6 },
  { name: '呼 气', dur: 4, scale: 1.0 }
]
const running = ref(false)
const phaseIdx = ref(0)
const count = ref(4)
const cycles = ref(0)
const totalSec = ref(0)
let timer = null

const phase = computed(() => PHASES[phaseIdx.value])
const phaseText = computed(() => running.value ? phase.value.name : (cycles.value > 0 ? `本次完成 ${cycles.value} 个循环` : '准备好了吗？'))
const circleStyle = computed(() => ({
  transform: `scale(${running.value ? phase.value.scale : 1})`,
  transition: `transform ${running.value ? phase.value.dur : 0.4}s ease-in-out`
}))

function start() {
  cycles.value = 0
  totalSec.value = 0
  phaseIdx.value = 0
  count.value = PHASES[0].dur
  running.value = true
  if (timer) clearInterval(timer)
  timer = setInterval(tick, 1000)
}

function tick() {
  if (!running.value) return
  totalSec.value++
  count.value--
  if (count.value <= 0) {
    const next = phaseIdx.value + 1
    if (next >= PHASES.length) {
      cycles.value++
      phaseIdx.value = 0
    } else {
      phaseIdx.value = next
    }
    count.value = PHASES[phaseIdx.value].dur
  }
}

async function stop() {
  if (timer) { clearInterval(timer); timer = null }
  running.value = false
  if (totalSec.value <= 0) return
  try {
    await contentApi.saveBreathing({ duration_seconds: totalSec.value, cycles: cycles.value })
    showSuccessToast(`本次 ${totalSec.value}s · ${cycles.value} 循环 已记录 🌟`)
  } catch (e) {
    showFailToast('保存失败')
  }
}

onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.breath { background: linear-gradient(180deg,#ecedff,#fff); min-height: 100vh; text-align: center; }
.hint { font-size: 22px; font-weight: 600; margin-top: 30px; color: #5057ff; letter-spacing: 4px; }
.circle-wrap { height: 280px; display: flex; align-items: center; justify-content: center; }
.circle { width: 140px; height: 140px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #b8bcff, #7c83ff); box-shadow: 0 0 60px rgba(124,131,255,.45); }
.counter { font-size: 38px; font-weight: 600; color: #2c2f3a; margin-top: -12px; }
.cycles { color: #5057ff; margin-top: 4px; font-size: 14px; }
.cycles strong { color: #d94560; font-size: 18px; }
.actions { padding: 24px; }
.tips { line-height: 1.9; font-size: 13px; }
.tips p { margin: 4px 0; color: #555; }
</style>
