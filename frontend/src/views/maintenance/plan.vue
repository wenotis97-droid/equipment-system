<template>
  <div>
    <h2>维保计划</h2>
    <el-card>
      <el-button type="primary" @click="openDialog()">新增计划</el-button>
      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="equipment_name" label="设备" min-width="160" />
        <el-table-column prop="plan_name" label="计划名称" min-width="140" />
        <el-table-column prop="maintain_type" label="类型" width="100" />
        <el-table-column label="触发方式" width="120">
          <template #default="{row}">
            {{ {1:'台时',2:'日历',3:'两者'}[row.trigger_type] }}
          </template>
        </el-table-column>
        <el-table-column prop="trigger_hours" label="触发台时" width="100" />
        <el-table-column prop="trigger_days" label="触发天数" width="100" />
        <el-table-column prop="advance_notify_days" label="提前天数" width="100" />
        <el-table-column label="状态" width="80">
          <template #default="{row}">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑计划' : '新增计划'" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择设备" required>
          <el-select v-model="form.equipment_id" filterable style="width:100%">
            <el-option v-for="e in equipmentList" :key="e.id" :label="`${e.equipment_code} ${e.name}`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划名称" required><el-input v-model="form.plan_name" /></el-form-item>
        <el-form-item label="维保类型"><el-input v-model="form.maintain_type" /></el-form-item>
        <el-form-item label="触发方式">
          <el-radio-group v-model="form.trigger_type">
            <el-radio :label="1">按台时</el-radio>
            <el-radio :label="2">按日历</el-radio>
            <el-radio :label="3">两者皆可</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="触发台时"><el-input-number v-model="form.trigger_hours" style="width:100%" /></el-form-item>
        <el-form-item label="触发天数"><el-input-number v-model="form.trigger_days" style="width:100%" /></el-form-item>
        <el-form-item label="提前提醒天数"><el-input-number v-model="form.advance_notify_days" style="width:100%" /></el-form-item>
        <el-form-item label="提前提醒台时"><el-input-number v-model="form.advance_notify_hours" style="width:100%" /></el-form-item>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMaintenancePlans, createMaintenancePlan, updateMaintenancePlan, deleteMaintenancePlan, getEquipmentList } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const equipmentList = ref([])
const dialogVisible = ref(false)
const form = reactive({ equipment_id: null, plan_name: '', maintain_type: 'periodic', trigger_type: 2, trigger_hours: null, trigger_days: null, advance_notify_days: 7, advance_notify_hours: null })

onMounted(() => {
  loadData()
  getEquipmentList({ page: 1, page_size: 1000 }).then(res => equipmentList.value = res.list)
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMaintenancePlans({ page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  dialogVisible.value = true
  Object.assign(form, row || { equipment_id: null, plan_name: '', maintain_type: 'periodic', trigger_type: 2, trigger_hours: null, trigger_days: null, advance_notify_days: 7, advance_notify_hours: null })
}

const save = async () => {
  try {
    if (form.id) {
      await updateMaintenancePlan(form.id, form)
    } else {
      await createMaintenancePlan(form)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const del = (row) => {
  ElMessageBox.confirm('确定删除该维保计划吗？', '提示', { type: 'warning' }).then(async () => {
    await deleteMaintenancePlan(row.id)
    ElMessage.success('删除成功')
    loadData()
  }).catch(() => {})
}
</script>
