<template>
  <div>
    <h2>设备档案</h2>
    <el-card>
      <div class="toolbar">
        <el-input v-model="search.keyword" placeholder="搜索设备编号/名称/型号" clearable style="width:240px" />
        <el-select v-model="search.category_id" placeholder="设备类别" clearable style="width:150px; margin-left:10px">
          <el-option v-for="c in categories" :key="c.id" :label="c.category_name" :value="c.id" />
        </el-select>
        <el-select v-model="search.status" placeholder="状态" clearable style="width:120px; margin-left:10px">
          <el-option label="闲置" :value="0" />
          <el-option label="使用中" :value="1" />
          <el-option label="维修中" :value="2" />
          <el-option label="停用" :value="3" />
          <el-option label="报废" :value="4" />
        </el-select>
        <el-button type="primary" style="margin-left:10px" @click="loadData">查询</el-button>
        <el-button type="success" @click="$router.push('/equipment/form')">新增设备</el-button>
      </div>

      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="equipment_code" label="设备编号" width="130" />
        <el-table-column prop="name" label="设备名称" min-width="160" />
        <el-table-column prop="model" label="规格型号" min-width="140" />
        <el-table-column prop="category_name" label="类别" width="100" />
        <el-table-column label="是否特种" width="90">
          <template #default="{row}">
            <el-tag :type="row.is_special ? 'danger' : 'info'">{{ row.is_special ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{row}">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="driver_name" label="驾驶员" width="100" />
        <el-table-column prop="total_running_hours" label="累计台时" width="100" />
        <el-table-column prop="location" label="地点" min-width="140" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="$router.push('/equipment/form/' + row.id)">编辑</el-button>
            <el-button size="small" type="primary" @click="showQrcode(row)">二维码</el-button>
            <el-button size="small" type="danger" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="qrDialog" title="设备二维码" width="360px" center>
      <div style="text-align:center" v-if="qrInfo">
        <img :src="qrInfo.qr_image_url" style="width:280px; height:280px; border:1px solid #eee" />
        <p>设备编号：{{ currentRow.equipment_code }}</p>
        <p style="font-size:12px; color:#999; word-break:break-all">{{ qrInfo.qr_url }}</p>
        <a :href="`/api/admin/equipment/${currentRow.id}/qrcode/download`" target="_blank">
          <el-button type="primary" size="small">下载打印</el-button>
        </a>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEquipmentList, deleteEquipment, getQrcode, getEquipmentCategories } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const categories = ref([])
const search = reactive({ keyword: '', category_id: null, status: null })
const qrDialog = ref(false)
const qrInfo = ref(null)
const currentRow = ref({})

onMounted(() => {
  loadData()
  getEquipmentCategories().then(res => categories.value = res)
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getEquipmentList({ page: page.value, page_size: pageSize.value, ...search })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const statusText = (s) => ({ 0: '闲置', 1: '使用中', 2: '维修中', 3: '停用', 4: '报废' }[s] || '未知')
const statusType = (s) => ({ 0: 'info', 1: 'success', 2: 'warning', 3: 'danger', 4: '' }[s] || 'info')

const showQrcode = async (row) => {
  currentRow.value = row
  qrInfo.value = await getQrcode(row.id)
  qrDialog.value = true
}

const del = (row) => {
  ElMessageBox.confirm(`确定删除设备 ${row.name} 吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteEquipment(row.id)
    ElMessage.success('删除成功')
    loadData()
  }).catch(() => {})
}
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
</style>
