<template>
  <div>
    <h2>安全培训</h2>
    <el-card>
      <el-button type="primary" @click="openDialog()">新增培训计划</el-button>
      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="plan_name" label="培训名称" min-width="180" />
        <el-table-column prop="training_type" label="类型" width="120" />
        <el-table-column prop="planned_date" label="计划时间" min-width="150" />
        <el-table-column prop="duration_hours" label="时长(h)" width="90" />
        <el-table-column prop="instructor" label="讲师" width="120" />
        <el-table-column prop="participant_count" label="参训人数" width="100" />
        <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑培训' : '新增培训'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="培训名称" required><el-input v-model="form.plan_name" /></el-form-item>
        <el-form-item label="培训类型"><el-input v-model="form.training_type" /></el-form-item>
        <el-form-item label="计划时间"><el-date-picker v-model="form.planned_date" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" /></el-form-item>
        <el-form-item label="培训时长"><el-input-number v-model="form.duration_hours" style="width:100%" /></el-form-item>
        <el-form-item label="讲师"><el-input v-model="form.instructor" /></el-form-item>
        <el-form-item label="培训地点"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="内容摘要"><el-input v-model="form.content_summary" type="textarea" :rows="3" /></el-form-item>
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
import { getTrainingPlans, createTrainingPlan, updateTrainingPlan } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const form = reactive({ id: null, plan_name: '', training_type: '', planned_date: '', duration_hours: null, instructor: '', location: '', content_summary: '' })

onMounted(() => loadData())

const loadData = async () => {
  loading.value = true
  try {
    const res = await getTrainingPlans({ page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const statusText = (s) => ({ 0: '计划中', 1: '已发布', 2: '已完成', 3: '已取消' }[s])
const statusType = (s) => ({ 0: 'info', 1: 'primary', 2: 'success', 3: 'danger' }[s])

const openDialog = (row = null) => {
  Object.assign(form, row || { id: null, plan_name: '', training_type: '', planned_date: '', duration_hours: null, instructor: '', location: '', content_summary: '' })
  dialogVisible.value = true
}

const save = async () => {
  try {
    if (form.id) await updateTrainingPlan(form.id, form)
    else await createTrainingPlan(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const viewDetail = (row) => {
  // 简化：可扩展详情弹窗
  ElMessage.info(`培训：${row.plan_name}，参训${row.participant_count}人`)
}
</script>
