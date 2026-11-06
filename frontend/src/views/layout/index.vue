<template>
  <el-container class="layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">设备管理系统</div>
      <el-menu :default-active="$route.path" router class="menu" background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-sub-menu index="/equipment">
          <template #title>
            <el-icon><Truck /></el-icon>
            <span>设备管理</span>
          </template>
          <el-menu-item index="/equipment/list">设备档案</el-menu-item>
          <el-menu-item index="/special-equipment">特种设备</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/maintenance">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>维保管理</span>
          </template>
          <el-menu-item index="/maintenance/plan">维保计划</el-menu-item>
          <el-menu-item index="/maintenance/record">维保记录</el-menu-item>
          <el-menu-item index="/maintenance/reminder">维保提醒</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/fuel">
          <template #title>
            <el-icon><CreditCard /></el-icon>
            <span>燃油管理</span>
          </template>
          <el-menu-item index="/fuel/records">加油记录</el-menu-item>
          <el-menu-item index="/fuel/analysis">油耗分析</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/operation/logs">
          <el-icon><Timer /></el-icon>
          <span>运转记录</span>
        </el-menu-item>
        <el-menu-item index="/repair/list">
          <el-icon><Warning /></el-icon>
          <span>报修管理</span>
        </el-menu-item>
        <el-menu-item index="/training/list">
          <el-icon><Reading /></el-icon>
          <span>安全培训</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><PieChart /></el-icon>
          <span>统计报表</span>
        </el-menu-item>
        <el-sub-menu index="/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
          <el-menu-item index="/system/field-defs">扩展字段</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="bell">
            <el-icon size="20"><Bell /></el-icon>
          </el-badge>
          <span class="username">{{ authStore.user.real_name }}</span>
          <el-button type="danger" size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getUnreadCount } from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const unreadCount = ref(0)

onMounted(async () => {
  try {
    unreadCount.value = (await getUnreadCount()).count || 0
  } catch (e) {}
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { height: 100vh; }
.sidebar { background: #304156; color: #fff; }
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; font-weight: bold; border-bottom: 1px solid #1f2d3d; }
.menu { border-right: none; }
.header { background: #fff; display: flex; align-items: center; justify-content: flex-end; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.header-right { display: flex; align-items: center; gap: 16px; }
.bell { cursor: pointer; }
.username { font-size: 14px; color: #606266; }
.main { background: #f5f7fa; padding: 20px; overflow-y: auto; }
</style>
