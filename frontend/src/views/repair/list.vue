<template>
  <div>
    <h2>报修管理</h2>
    <el-card>
      <el-radio-group v-model="filter.status" @change="loadData" style="margin-bottom:15px">
        <el-radio-button :label="null">全部</el-radio-button>
        <el-radio-button :label="0">待审批</el-radio-button>
        <el-radio-button :label="1">待维修</el-radio-button>
        <el-radio-button :label="2">维修中</el-radio-button>
        <el-radio-button :label="3">已完成</el-radio-button>
        <el-radio-button :label="4">已驳回</el-radio-button>
      </el-radio-group>

      <el-table :data="list" border v-loading="loading">
        <el-table-column prop="request_no" label="报修单号" width="150" />
        <el-table-column prop="equipment_name" label="设备" min-width="160" />
        <el-table-column prop="reporter_name" label="报修人" width="100" />
        <el-table-column prop="fault_type" label="故障类型" width="100" />
        <el-table-column label="等级" width="90"><template #default="{row}"><el-tag :type="row.fault_level === 3 ? 'danger' : row.fault_level === 2 ? 'warning' : 'info'">{{ {1:'一般',2:'严重',3:'紧急'}[row.fault_level] }}</el-tag></template></el-table-column>
        <el-table-column prop="fault_description" label="故障描述" min-width="200" />
        <el-table-column label="状态" width="110"><template #default="{row}"><el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" v-if="row.status === 0" @click="doAction(row, 'approve')">审批</el-button>
            <el-button size="small" v-if="row.status === 1" @click="doAction(row, 'start_repair')">开始维修</el-button>
            <el-button size="small" v-if="row.status === 2" @click="doAction(row, 'complete')">完成</el-button>
            <el-button size="small" v-if="row.status === 0" type="danger" @click="doAction(row, 'reject')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="actionTitle" width="600px">
      <el-form :model="actionForm" label-width="100px">
        <el-form-item label="维修人" v-if="actionType === 'start_repair'"><el-input v-model="actionForm.repairer" /></el-form-item>
        <el-form-item label="维修说明" v-if="actionType === 'complete'"><el-input v-model="actionForm.repair_description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="更换配件" v-if="actionType === 'complete'"><el-input v-model="actionForm.repair_parts" type="textarea" /></el-form-item>
        <el-form-item label="维修费用" v-if="actionType === 'complete'"><el-input-number v-model="actionForm.repair_cost" style="width:100%" /></el-form-item>
        <el-form-item label="审批意见" v-if="['approve','reject'].includes(actionType)"><el-input v-model="actionForm.approve_remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAction">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getRepairRequests, actionRepair } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filter = reactive({ status: null })
const dialogVisible = ref(false)
const currentId = ref(null)
const actionType = ref('')
const actionForm = reactive({ repairer: '', repair_description: '', repair_parts: '', repair_cost: null, approve_remark: '' })

onMounted(() => loadData())

const actionTitle = computed(() => ({ approve: '审批', start_repair: '开始维修', complete: '完成维修', reject: '驳回' }[actionType.value]))

const loadData = async () => {
  loading.value = true
  try {
    const res = await getRepairRequests({ status: filter.status, page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const statusText = (s) => ({ 0: '待审批', 1: '待维修', 2: '维修中', 3: '已完成', 4: '已驳回' }[s])
const statusType = (s) => ({ 0: 'warning', 1: 'primary', 2: 'danger', 3: 'success', 4: 'info' }[s])

const doAction = (row, action) => {
  currentId.value = row.id
  actionType.value = action
  Object.assign(actionForm, { repairer: '', repair_description: '', repair_parts: '', repair_cost: null, approve_remark: '' })
  dialogVisible.value = true
}

const submitAction = async () => {
  try {
    await actionRepair(currentId.value, { action: actionType.value, ...actionForm })
    ElMessage.success('操作成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>
