<template>
  <div>
    <h2>{{ isEdit ? '编辑设备' : '新增设备' }}</h2>
    <el-card v-loading="loading">
      <el-form :model="form" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="设备编号" required>
              <el-input v-model="form.equipment_code" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设备名称" required>
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="规格型号">
              <el-input v-model="form.model" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设备类别">
              <el-select v-model="form.category_id" style="width:100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.category_name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="品牌/厂家">
              <el-input v-model="form.brand" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="是否特种设备">
              <el-radio-group v-model="form.is_special">
                <el-radio :label="0">否</el-radio>
                <el-radio :label="1">是</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="当前状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option label="闲置" :value="0" />
                <el-option label="使用中" :value="1" />
                <el-option label="维修中" :value="2" />
                <el-option label="停用" :value="3" />
                <el-option label="报废" :value="4" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="所属项目">
              <el-select v-model="form.project_id" style="width:100%">
                <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="存放地点">
              <el-input v-model="form.location" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="驾驶员姓名">
              <el-input v-model="form.driver_name" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="驾驶员电话">
              <el-input v-model="form.driver_phone" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="投用日期">
              <el-date-picker v-model="form.put_use_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>扩展字段（可在系统设置中配置）</el-divider>
        <el-row :gutter="20">
          <el-col :span="8" v-for="fd in fieldDefs" :key="fd.field_key">
            <el-form-item :label="fd.field_label">
              <el-input v-if="fd.field_type === 'text'" v-model="form.extra_attributes[fd.field_key]" />
              <el-input-number v-else-if="fd.field_type === 'number'" v-model="form.extra_attributes[fd.field_key]" style="width:100%" />
              <el-date-picker v-else-if="fd.field_type === 'date'" v-model="form.extra_attributes[fd.field_key]" type="date" value-format="YYYY-MM-DD" style="width:100%" />
              <el-select v-else-if="fd.field_type === 'select'" v-model="form.extra_attributes[fd.field_key]" style="width:100%">
                <el-option v-for="opt in parseOptions(fd.field_options)" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="save">保 存</el-button>
          <el-button @click="$router.back()">返 回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getEquipmentDetail, createEquipment, updateEquipment, getEquipmentCategories, getEquipmentFieldDefs, getProjects } from '@/api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const categories = ref([])
const projects = ref([])
const fieldDefs = ref([])

const defaultForm = {
  equipment_code: '', name: '', model: '', brand: '', category_id: null,
  is_special: 0, status: 1, project_id: null, location: '',
  driver_name: '', driver_phone: '', put_use_date: null,
  extra_attributes: {},
}
const form = ref({ ...defaultForm })

onMounted(async () => {
  categories.value = await getEquipmentCategories()
  projects.value = await getProjects()
  fieldDefs.value = await getEquipmentFieldDefs()
  if (isEdit.value) {
    loading.value = true
    try {
      const detail = await getEquipmentDetail(route.params.id)
      form.value = { ...defaultForm, ...detail, extra_attributes: detail.extra_attributes || {} }
      fieldDefs.value = detail.extra_field_defs || fieldDefs.value
    } catch (e) {
      ElMessage.error(e.message)
    } finally {
      loading.value = false
    }
  }
})

const parseOptions = (opts) => {
  if (!opts) return []
  if (typeof opts === 'string') {
    try { return JSON.parse(opts) } catch { return [] }
  }
  return opts
}

const save = async () => {
  try {
    if (isEdit.value) {
      await updateEquipment(route.params.id, form.value)
    } else {
      await createEquipment(form.value)
    }
    ElMessage.success('保存成功')
    router.push('/equipment/list')
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>
