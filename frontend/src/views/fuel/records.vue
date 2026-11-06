<template>
  <div>
    <h2>加油记录</h2>
    <el-card>
      <el-button type="primary" @click="openDialog()">新增加油记录</el-button>
      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="equipment_name" label="设备" min-width="160" />
        <el-table-column prop="fuel_date" label="加油时间" min-width="150" />
        <el-table-column prop="fuel_type" label="油品" width="100" />
        <el-table-column prop="volume" label="加油量(L)" width="110" />
        <el-table-column prop="total_amount" label="金额" width="100" />
        <el-table-column prop="running_hours" label="台时读数" width="100" />
        <el-table-column prop="fuel_consumption" label="油耗(L/h)" width="110" />
        <el-table-column prop="operator_name" label="加油人" width="100" />
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增加油记录" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择设备" required>
          <el-select v-model="form.equipment_id" filterable style="width:100%">
            <el-option v-for="e in equipmentList" :key="e.id" :label="`${e.equipment_code} ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="加油时间" required><el-date-picker v-model="form.fuel_date" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" /></el-form-item>
        <el-form-item label="油品"><el-input v-model="form.fuel_type" /></el-form-item>
        <el-form-item label="加油量(L)" required><el-input-number v-model="form.volume" style="width:100%" /></el-form-item>
        <el-form-item label="单价"><el-input-number v-model="form.unit_price" style="width:100%" /></el-form-item>
        <el-form-item label="台时读数"><el-input-number v-model="form.running_hours" style="width:100%" /></el-form-item>
        <el-form-item label="加油人"><el-input v-model="form.operator_name" /></el-form-item>
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
import { getFuelRecords, createFuelRecord, getEquipmentList } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const equipmentList = ref([])
const dialogVisible = ref(false)
const form = reactive({ equipment_id: null, fuel_date: '', fuel_type: '0#柴油', volume: null, unit_price: null, running_hours: null, operator_name: '' })

onMounted(() => {
  loadData()
  getEquipmentList({ page: 1, page_size: 1000 }).then(res => equipmentList.value = res.list)
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getFuelRecords({ page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const openDialog = () => {
  Object.assign(form, { equipment_id: null, fuel_date: '', fuel_type: '0#柴油', volume: null, unit_price: null, running_hours: null, operator_name: '' })
  dialogVisible.value = true
}

const save = async () => {
  try {
    await createFuelRecord(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>
