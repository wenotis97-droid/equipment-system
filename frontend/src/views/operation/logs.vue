<template>
  <div>
    <h2>运转记录</h2>
    <el-card>
      <el-table :data="list" border v-loading="loading">
        <el-table-column prop="equipment_name" label="设备" min-width="160" />
        <el-table-column prop="log_date" label="日期" width="120" />
        <el-table-column label="班次" width="80"><template #default="{row}">{{ row.shift === 1 ? '白班' : '夜班' }}</template></el-table-column>
        <el-table-column prop="start_hours" label="开工台时" width="100" />
        <el-table-column prop="end_hours" label="收工台时" width="100" />
        <el-table-column prop="running_hours" label="运转台时" width="100" />
        <el-table-column prop="work_content" label="工作内容" min-width="160" />
        <el-table-column prop="operator_name" label="操作人" width="100" />
        <el-table-column prop="safety_check" label="安全检查" width="90">
          <template #default="{row}"><el-tag :type="row.safety_check ? 'success' : 'danger'">{{ row.safety_check ? '通过' : '异常' }}</el-tag></template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOperationLogs } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

onMounted(() => loadData())

const loadData = async () => {
  loading.value = true
  try {
    const res = await getOperationLogs({ page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>
