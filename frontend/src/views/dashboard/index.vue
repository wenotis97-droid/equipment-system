<template>
  <div>
    <h2>仪表盘</h2>
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="6" v-for="item in statCards" :key="item.title">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-title">{{ item.title }}</div>
          <div class="stat-value" :style="{color: item.color}">{{ item.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card title="设备状态分布">
          <div ref="statusChart" style="height:300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card title="特种设备合规状态">
          <div ref="complianceChart" style="height:300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:20px">
      <template #header>待办提醒</template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="todo-item">
            <div class="todo-label">待处理维保提醒</div>
            <div class="todo-num warning">{{ dashboard.maintenance?.pending_reminders || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="todo-item">
            <div class="todo-label">待处理报修</div>
            <div class="todo-num danger">{{ dashboard.repair?.pending || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="todo-item">
            <div class="todo-label">本月加油量(升)</div>
            <div class="todo-num">{{ dashboard.fuel?.month_volume || 0 }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { getDashboard } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const dashboard = ref({})
const statusChart = ref(null)
const complianceChart = ref(null)

const statCards = computed(() => [
  { title: '设备总数', value: dashboard.value.equipment?.total || 0, color: '#409EFF' },
  { title: '特种设备', value: dashboard.value.special_equipment?.total || 0, color: '#E6A23C' },
  { title: '本月维保', value: dashboard.value.maintenance?.month_count || 0, color: '#67C23A' },
  { title: '维保提醒', value: dashboard.value.maintenance?.pending_reminders || 0, color: '#F56C6C' },
])

const statusLabels = { 0: '闲置', 1: '使用中', 2: '维修中', 3: '停用', 4: '报废' }
const complianceLabels = { 0: '不合规', 1: '合规', 2: '即将过期', 3: '已过期' }

onMounted(async () => {
  loading.value = true
  try {
    dashboard.value = await getDashboard()
    await nextTick()
    initCharts()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
})

const initCharts = () => {
  const statusData = Object.entries(dashboard.value.equipment?.status_distribution || {}).map(([k, v]) => ({ name: k, value: v }))
  const compData = Object.entries(dashboard.value.special_equipment?.compliance_distribution || {}).map(([k, v]) => ({ name: k, value: v }))

  if (statusChart.value) {
    echarts.init(statusChart.value).setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: statusData,
        label: { formatter: '{b}: {c}' }
      }]
    })
  }
  if (complianceChart.value) {
    echarts.init(complianceChart.value).setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: compData,
        color: ['#F56C6C', '#67C23A', '#E6A23C', '#909399'],
        label: { formatter: '{b}: {c}' }
      }]
    })
  }
}
</script>

<style scoped>
.stat-card { margin-bottom: 10px; }
.stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; }
.todo-item { text-align: center; padding: 20px; background: #f5f7fa; border-radius: 8px; }
.todo-label { color: #606266; font-size: 14px; margin-bottom: 8px; }
.todo-num { font-size: 32px; font-weight: bold; color: #409EFF; }
.todo-num.warning { color: #E6A23C; }
.todo-num.danger { color: #F56C6C; }
</style>
