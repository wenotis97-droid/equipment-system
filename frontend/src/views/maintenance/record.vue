<template>
  <div>
    <h2>维保记录</h2>
    <el-card>
      <el-button type="primary" @click="openDialog()">新增维保记录</el-button>
      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="equipment_name" label="设备" min-width="160" />
        <el-table-column prop="maintain_date" label="维保日期" width="120" />
        <el-table-column prop="maintainer" label="维保人" width="120" />
        <el-table-column prop="running_hours" label="台时读数" width="100" />
        <el-table-column prop="cost" label="费用" width="100" />
        <el-table-column prop="description" label="维保内容" min-width="200" />
        <el-table-column label="结果" width="90">
          <template #default="{row}">
            <el-tag :type="row.result === 1 ? 'success' : 'danger'">{{ row.result === 1 ? '完成' : '异常' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增维保记录" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择设备" required>
          <el-select v-model="form.equipment_id" filterable style="width:100%">
            <el-option v-for="e in equipmentList" :key="e.id" :label="`${e.equipment_code} ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="维保日期" required><el-date-picker v-model="form.maintain_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="维保类型"><el-input v-model="form.maintain_type" /></el-form-item>
        <el-form-item label="台时读数"><el-input-number v-model="form.running_hours" style="width:100%" /></el-form-item>
        <el-form-item label="维保费用"><el-input-number v-model="form.cost" style="width:100%" /></el-form-item>
        <el-form-item label="维保人"><el-input v-model="form.maintainer" /></el-form-item>
        <el-form-item label="更换配件"><el-input v-model="form.parts_replaced" type="textarea" /></el-form-item>
        <el-form-item label="维保内容"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getMaintenanceRecords, createMaintenanceRecord, getEquipmentList } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const equipmentList = ref([])
const dialogVisible = ref(false)
const form = reactive({ equipment_id: null, maintain_date: '', maintain_type: 'periodic', running_hours: null, cost: null, maintainer: '', parts_replaced: '', description: '', result: 1 })

onMounted(() => {
  loadData()
  getEquipmentList({ page: 1, page_size: 1000 }).then(res => equipmentList.value = res.list)
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMaintenanceRecords({ page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const openDialog = () => {
  Object.assign(form, { equipment_id: null, maintain_date: '', maintain_type: 'periodic', running_hours: null, cost: null, maintainer: '', parts_replaced: '', description: '', result: 1 })
  dialogVisible.value = true
}

const save = async () => {
  try {
    await createMaintenanceRecord(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>
