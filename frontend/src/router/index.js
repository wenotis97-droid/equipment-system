import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/login/index.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      { path: '/dashboard', component: () => import('@/views/dashboard/index.vue'), meta: { title: '仪表盘' } },
      { path: '/equipment/list', component: () => import('@/views/equipment/list.vue'), meta: { title: '设备档案' } },
      { path: '/equipment/form/:id?', component: () => import('@/views/equipment/form.vue'), meta: { title: '设备编辑' } },
      { path: '/special-equipment', component: () => import('@/views/special-equipment/index.vue'), meta: { title: '特种设备' } },
      { path: '/maintenance/plan', component: () => import('@/views/maintenance/plan.vue'), meta: { title: '维保计划' } },
      { path: '/maintenance/record', component: () => import('@/views/maintenance/record.vue'), meta: { title: '维保记录' } },
      { path: '/maintenance/reminder', component: () => import('@/views/maintenance/reminder.vue'), meta: { title: '维保提醒' } },
      { path: '/fuel/records', component: () => import('@/views/fuel/records.vue'), meta: { title: '加油记录' } },
      { path: '/fuel/analysis', component: () => import('@/views/fuel/analysis.vue'), meta: { title: '油耗分析' } },
      { path: '/operation/logs', component: () => import('@/views/operation/logs.vue'), meta: { title: '运转记录' } },
      { path: '/repair/list', component: () => import('@/views/repair/list.vue'), meta: { title: '报修管理' } },
      { path: '/training/list', component: () => import('@/views/training/list.vue'), meta: { title: '安全培训' } },
      { path: '/statistics', component: () => import('@/views/statistics/index.vue'), meta: { title: '统计报表' } },
      { path: '/system/users', component: () => import('@/views/system/users.vue'), meta: { title: '用户管理' } },
      { path: '/system/field-defs', component: () => import('@/views/system/field-defs.vue'), meta: { title: '扩展字段' } },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (!to.meta.public && !authStore.isLogin) {
    next('/login')
  } else {
    next()
  }
})

export default router
