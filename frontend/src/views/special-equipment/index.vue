<template>
  <div>
    <h2>特种设备管理</h2>
    <el-card>
      <div class="toolbar">
        <el-radio-group v-model="filter.compliance_status" @change="loadData">
          <el-radio-button :label="null">全部</el-radio-button>
          <el-radio-button :label="1">合规</el-radio-button>
          <el-radio-button :label="2">即将过期</el-radio-button>
          <el-radio-button :label="3">已过期</el-radio-button>
          <el-radio-button :label="0">不合规</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="equipment_code" label="设备编号" width="130" />
        <el-table-column prop="name" label="设备名称" min-width="160" />
        <el-table-column prop="category_name" label="类别" width="120" />
        <el-table-column prop="location" label="地点" min-width="140" />
        <el-table-column label="合规状态" width="110">
          <template #default="{row}">
            <el-tag :type="complianceType(row.compliance_status)">{{ complianceText(row.compliance_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="next_inspection_date" label="下次检验" width="120" />
        <el-table-column prop="operator_cert_expiry" label="作业证到期" width="120" />
        <el-table-column label="操作" width="180">
          <template #default="{row}">
            <el-button size="small" type="primary" @click="openDetail(row)">合规详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="特种设备合规信息" width="700px">
      <div v-if="detail" v-loading="detailLoading">
        <el-alert v-if="detail.compliance_status !== 1" :title="complianceAlertTitle" :type="complianceType(detail.compliance_status)" :closable="false" style="margin-bottom:15px" />
        <el-form :model="detail" label-width="140px">
          <el-divider>使用登记证</el-divider>
          <el-row :gutter="10">
            <el-col :span="12"><el-form-item label="登记证号"><el-input v-model="detail.registration_number" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="有效期"><el-date-picker v-model="detail.registration_expiry" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          </el-row>
          <el-form-item label="登记证照片"><el-input v-model="detail.registration_cert_url" placeholder="上传文件URL" /></el-form-item>

          <el-divider>定期检验</el-divider>
          <el-row :gutter="10">
            <el-col :span="8"><el-form-item label="上次检验"><el-date-picker v-model="detail.last_inspection_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="下次检验"><el-date-picker v-model="detail.next_inspection_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="检验状态">
              <el-select v-model="detail.inspection_status" style="width:100%">
                <el-option label="未检" :value="0" /><el-option label="合格" :value="1" />
                <el-option label="不合格" :value="2" /><el-option label="待检" :value="3" />
              </el-select>
            </el-form-item></el-col>
          </el-row>
          <el-form-item label="检验报告"><el-input v-model="detail.inspection_report_url" placeholder="上传文件URL" /></el-form-item>

          <el-divider>操作人员</el-divider>
          <el-row :gutter="10">
            <el-col :span="8"><el-form-item label="姓名"><el-input v-model="detail.operator_name" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="作业证号"><el-input v-model="detail.operator_cert_number" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="证有效期"><el-date-picker v-model="detail.operator_cert_expiry" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          </el-row>
          <el-form-item label="作业证照片"><el-input v-model="detail.operator_cert_url" placeholder="上传文件URL" /></el-form-item>

          <el-divider>安拆方案与验收</el-divider>
          <el-row :gutter="10">
            <el-col :span="12"><el-form-item label="安拆方案"><el-input v-model="detail.install_dismantle_plan_url" placeholder="上传文件URL" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="验收状态">
              <el-select v-model="detail.acceptance_status" style="width:100%">
                <el-option label="未验收" :value="0" /><el-option label="合格" :value="1" /><el-option label="不合格" :value="2" />
              </el-select>
            </el-form-item></el-col>
          </el-row>
          <el-form-item label="验收记录"><el-input v-model="detail.acceptance_record_url" placeholder="上传文件URL" /></el-form-item>

          <el-form-item label="监管机构"><el-input v-model="detail.supervision_agency" /></el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="saveDetail">保存并校验</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSpecialEquipmentList, getSpecialEquipmentDetail, saveSpecialEquipment, checkCompliance } from '@/api'

const loading = ref(false)
const detailLoading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filter = reactive({ compliance_status: null })
const dialogVisible = ref(false)
const detail = ref(null)
const currentEqId = ref(null)

onMounted(() => loadData())

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSpecialEquipmentList({ page: page.value, page_size: pageSize.value, compliance_status: filter.compliance_status })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const complianceText = (s) => ({ 0: '不合规', 1: '合规', 2: '即将过期', 3: '已过期' }[s] || '未知')
const complianceType = (s) => ({ 0: 'danger', 1: 'success', 2: 'warning', 3: 'danger' }[s] || 'info')
const complianceAlertTitle = computed(() => complianceText(detail.value?.compliance_status))

const openDetail = async (row) => {
  currentEqId.value = row.id
  dialogVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await getSpecialEquipmentDetail(row.id)
  } catch (e) {
    detail.value = {
      registration_number: '', registration_expiry: null, registration_cert_url: '',
      last_inspection_date: null, next_inspection_date: null, inspection_status: 0, inspection_report_url: '',
      operator_name: '', operator_cert_number: null, operator_cert_expiry: null, operator_cert_url: '',
      install_dismantle_plan_url: '', acceptance_status: 0, acceptance_record_url: '', supervision_agency: '',
    }
  } finally {
    detailLoading.value = false
  }
}

const saveDetail = async () => {
  try {
    await saveSpecialEquipment(currentEqId.value, detail.value)
    const result = await checkCompliance(currentEqId.value)
    detail.value.compliance_status = result.status
    ElMessage.success('保存并校验成功')
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>

<style scoped>
.toolbar { margin-bottom: 10px; }
</style>
