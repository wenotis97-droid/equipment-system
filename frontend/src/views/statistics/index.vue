<template>
  <div>
    <h2>统计报表</h2>
    <el-card v-loading="loading">
      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="statusChart" style="height:320px"></div>
        </el-col>
        <el-col :span="12">
          <div ref="complianceChart" style="height:320px"></div>
        </el-col>
      </el-row>
      <el-table :data="tableData" border style="margin-top:20px">
        <el-table-column prop="name" label="指标" />
        <el-table-column prop="value" label="数值" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getDashboard } from '@/api'

const loading = ref(false)
const data = ref({})
const statusChart = ref(null)
const complianceChart = ref(null)
const tableData = ref([])

onMounted(async () => {
  loading.value = true
  try {
    data.value = await getDashboard()
    tableData.value = [
      { name: '设备总数', value: data.value.equipment?.total },
      { name: '特种设备数', value: data.value.special_equipment?.total },
      { name: '待处理维保提醒', value: data.value.maintenance?.pending_reminders },
      { name: '待处理报修', value: data.value.repair?.pending },
      { name: '本月加油量', value: data.value.fuel?.month_volume + ' L' },
    ]
    await nextTick()
    if (statusChart.value) {
      echarts.init(statusChart.value).setOption({
        title: { text: '设备状态分布', left: 'center' },
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: '60%', data: Object.entries(data.value.equipment?.status_distribution || {}).map(([k, v]) => ({ name: k, value: v })) }]
      })
    }
    if (complianceChart.value) {
      echarts.init(complianceChart.value).setOption({
        title: { text: '特种设备合规状态', left: 'center' },
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: '60%', data: Object.entries(data.value.special_equipment?.compliance_distribution || {}).map(([k, v]) => ({ name: k, value: v })) }]
      })
    }
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
})
</script>
