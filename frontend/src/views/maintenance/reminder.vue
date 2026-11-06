<template>
  <div>
    <h2>维保提醒</h2>
    <el-card>
      <el-table :data="list" border v-loading="loading">
        <el-table-column prop="equipment_name" label="设备名称" min-width="160" />
        <el-table-column prop="plan_name" label="维保计划" min-width="140" />
        <el-table-column label="提醒类型" width="100">
          <template #default="{row}">
            <el-tag :type="row.reminder_type === 1 ? 'warning' : 'primary'">{{ row.reminder_type === 1 ? '台时' : '日历' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_date" label="目标日期" width="120" />
        <el-table-column prop="target_hours" label="目标台时" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status === 2 ? 'success' : row.status === 3 ? 'info' : 'danger'">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{row}">
            <el-button size="small" type="success" @click="handle(row, 'done')">已维保</el-button>
            <el-button size="small" @click="handle(row, 'ignore')">忽略</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMaintenanceReminders, actionReminder } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

onMounted(() => loadData())

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMaintenanceReminders({ page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const statusText = (s) => ({ 0: '待处理', 1: '已通知', 2: '已维保', 3: '已忽略' }[s])

const handle = async (row, action) => {
  try {
    await actionReminder(row.id, action)
    ElMessage.success('操作成功')
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>
