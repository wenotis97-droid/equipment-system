<template>
  <div>
    <h2>用户管理</h2>
    <el-card>
      <el-button type="primary" @click="openDialog()">新增用户</el-button>
      <el-table :data="list" border v-loading="loading" style="margin-top:15px">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="role_name" label="角色" width="120" />
        <el-table-column prop="last_login_at" label="最后登录" min-width="160" />
        <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.status ? 'success' : 'danger'">{{ row.status ? '启用' : '禁用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{row}">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" @click="toggleStatus(row)">{{ row.status ? '禁用' : '启用' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:15px" background layout="prev, pager, next, total" :total="total" :page-size="pageSize" v-model:current-page="page" @change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名" required><el-input v-model="form.username" :disabled="form.id" /></el-form-item>
        <el-form-item label="密码" :required="!form.id"><el-input v-model="form.password" type="password" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_id" style="width:100%"><el-option v-for="r in roles" :key="r.id" :label="r.role_name" :value="r.id" /></el-select>
        </el-form-item>
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
import { getUsers, createUser, updateUser, toggleUserStatus, getRoles } from '@/api'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const roles = ref([])
const dialogVisible = ref(false)
const form = reactive({ id: null, username: '', password: '', real_name: '', phone: '', role_id: null })

onMounted(() => {
  loadData()
  getRoles().then(res => roles.value = res)
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUsers({ page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  Object.assign(form, row || { id: null, username: '', password: '', real_name: '', phone: '', role_id: null })
  dialogVisible.value = true
}

const save = async () => {
  try {
    if (form.id) {
      const data = { ...form }
      delete data.username
      delete data.password
      if (form.password) data.password = form.password
      await updateUser(form.id, data)
    } else {
      await createUser(form)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const toggleStatus = async (row) => {
  try {
    await toggleUserStatus(row.id)
    ElMessage.success('操作成功')
    loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>
