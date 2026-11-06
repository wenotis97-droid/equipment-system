<template>
  <div>
    <h2>扩展字段配置</h2>
    <el-card>
      <el-button type="primary" @click="openDialog()">新增字段</el-button>
      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="field_key" label="字段键名" width="140" />
        <el-table-column prop="field_label" label="显示名称" width="140" />
        <el-table-column prop="field_type" label="类型" width="100" />
        <el-table-column prop="category_name" label="所属类别" min-width="140" />
        <el-table-column label="必填" width="80"><template #default="{row}">{{ row.is_required ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" type="danger" @click="del(row)">禁用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增字段" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="字段键名" required><el-input v-model="form.field_key" placeholder="如 insurance_company" /></el-form-item>
        <el-form-item label="显示名称" required><el-input v-model="form.field_label" placeholder="如 保险公司" /></el-form-item>
        <el-form-item label="字段类型">
          <el-select v-model="form.field_type" style="width:100%">
            <el-option label="文本" value="text" />
            <el-option label="数字" value="number" />
            <el-option label="日期" value="date" />
            <el-option label="下拉选择" value="select" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属类别">
          <el-select v-model="form.category_id" clearable style="width:100%">
            <el-option label="全局通用" :value="null" />
            <el-option v-for="c in categories" :key="c.id" :label="c.category_name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选项(JSON)" v-if="form.field_type === 'select'">
          <el-input v-model="optionsJson" type="textarea" :rows="3" placeholder='[{"label":"自有","value":"self"}]' />
        </el-form-item>
        <el-form-item label="必填"><el-switch v-model="form.is_required" :active-value="1" :inactive-value="0" /></el-form-item>
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
import { getEquipmentFieldDefs, createFieldDef, deleteFieldDef, getEquipmentCategories } from '@/api'

const loading = ref(false)
const list = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const optionsJson = ref('')
const form = reactive({ field_key: '', field_label: '', field_type: 'text', field_options: null, category_id: null, is_required: 0 })

onMounted(() => {
  loadData()
  getEquipmentCategories().then(res => categories.value = res)
})

const loadData = async () => {
  loading.value = true
  try {
    list.value = await getEquipmentFieldDefs()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const openDialog = () => {
  Object.assign(form, { field_key: '', field_label: '', field_type: 'text', field_options: null, category_id: null, is_required: 0 })
  optionsJson.value = ''
  dialogVisible.value = true
}

const save = async () => {
  try {
    if (form.field_type === 'select' && optionsJson.value) {
      form.field_options = JSON.parse(optionsJson.value)
    }
    await createFieldDef(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const del = async (row) => {
  try {
    await deleteFieldDef(row.id)
    ElMessage.success('已禁用')
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>
