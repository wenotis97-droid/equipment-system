<template>
  <div>
    <h2>油耗分析</h2>
    <el-card v-loading="loading">
      <el-row :gutter="20">
        <el-col :span="6"><div class="stat-box"><div class="label">总加油量</div><div class="value">{{ data.total_volume }} L</div></div></el-col>
        <el-col :span="6"><div class="stat-box"><div class="label">总金额</div><div class="value">¥{{ data.total_amount }}</div></div></el-col>
        <el-col :span="6"><div class="stat-box"><div class="label">平均油耗</div><div class="value">{{ data.avg_consumption || '-' }} L/h</div></div></el-col>
        <el-col :span="6"><div class="stat-box"><div class="label">记录数</div><div class="value">{{ data.record_count }}</div></div></el-col>
      </el-row>

      <div ref="chart" style="height:300px; margin-top:20px"></div>

      <el-table :data="data.by_equipment" border style="margin-top:20px">
        <el-table-column prop="name" label="设备" />
        <el-table-column prop="volume" label="加油量(L)" />
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="count" label="加油次数" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getFuelAnalysis } from '@/api'

const loading = ref(false)
const data = ref({ total_volume: 0, total_amount: 0, avg_consumption: null, record_count: 0, by_equipment: [] })
const chart = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    data.value = await getFuelAnalysis()
    await nextTick()
    if (chart.value) {
      echarts.init(chart.value).setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: data.value.by_equipment.map(i => i.name) },
        yAxis: { type: 'value', name: '加油量(L)' },
        series: [{ type: 'bar', data: data.value.by_equipment.map(i => i.volume), itemStyle: { color: '#409EFF' } }]
      })
    }
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-box { background: #f5f7fa; border-radius: 8px; padding: 20px; text-align: center; }
.stat-box .label { color: #909399; font-size: 14px; margin-bottom: 8px; }
.stat-box .value { font-size: 24px; font-weight: bold; color: #409EFF; }
</style>
