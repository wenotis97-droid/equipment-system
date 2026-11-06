<template>
  <view class="container">
    <view class="header-card">
      <view class="title">设备管理系统</view>
      <view class="subtitle">扫码即可操作设备</view>
    </view>

    <view class="scan-area" @click="handleScan">
      <view class="scan-icon">
        <text class="iconfont">&#xe601;</text>
      </view>
      <view class="scan-text">点击扫描二维码</view>
      <view class="scan-tip">请对准设备上的二维码</view>
    </view>

    <view class="manual-input">
      <input v-model="manualCode" placeholder="或输入设备编号" class="code-input" />
      <button class="mini-btn" @click="searchByCode">查询</button>
    </view>

    <view class="todo-area">
      <view class="todo-title">待办事项</view>
      <view class="todo-list">
        <view class="todo-item" @click="goTo('/pages/maintenance/reminder')">
          <text class="num">{{ todo.maintenance || 0 }}</text>
          <text class="label">维保提醒</text>
        </view>
        <view class="todo-item">
          <text class="num">{{ todo.repair || 0 }}</text>
          <text class="label">我的报修</text>
        </view>
        <view class="todo-item">
          <text class="num">{{ todo.training || 0 }}</text>
          <text class="label">待培训</text>
        </view>
      </view>
    </view>

    <view class="menu-grid">
      <view class="grid-item" v-for="item in menuList" :key="item.path" @click="goTo(item.path)">
        <text class="grid-icon">{{ item.icon }}</text>
        <text class="grid-label">{{ item.label }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { scanEquipment } from '@/api'
export default {
  data() {
    return {
      manualCode: '',
      todo: { maintenance: 0, repair: 0, training: 0 },
      menuList: [
        { label: '加油登记', icon: '⛽', path: '/pages/fuel/record' },
        { label: '运转记录', icon: '📋', path: '/pages/operation/log' },
        { label: '交接班', icon: '🔄', path: '/pages/operation/handover' },
        { label: '报修申请', icon: '🔧', path: '/pages/repair/request' },
        { label: '安全培训', icon: '📚', path: '/pages/training/list' },
        { label: '我的记录', icon: '📁', path: '/pages/history/list' },
      ]
    }
  },
  onShow() {
    this.checkLogin()
  },
  methods: {
    checkLogin() {
      const token = uni.getStorageSync('session_token')
      if (!token) {
        uni.navigateTo({ url: '/pages/login/index' })
      }
    },
    handleScan() {
      uni.scanCode({
        onlyFromCamera: true,
        scanType: ['qrCode'],
        success: (res) => {
          const token = this.extractToken(res.result)
          this.loadEquipment(token)
        },
        fail: () => {
          uni.showToast({ title: '扫码失败', icon: 'none' })
        }
      })
    },
    extractToken(result) {
      if (result.startsWith('http')) {
        const match = result.match(/token=([^&]+)/)
        return match ? match[1] : result
      }
      return result
    },
    async loadEquipment(token) {
      uni.showLoading({ title: '加载中' })
      try {
        const detail = await scanEquipment(token)
        uni.setStorageSync('current_equipment', detail)
        uni.navigateTo({ url: '/pages/equipment/detail?token=' + token })
      } catch (e) {
        uni.showToast({ title: e.message || '设备加载失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    searchByCode() {
      if (!this.manualCode) return
      uni.showToast({ title: '请输入二维码扫码或后台查询', icon: 'none' })
    },
    goTo(path) {
      uni.navigateTo({ url: path })
    }
  }
}
</script>

<style scoped>
.container { padding: 20rpx; background: #f5f7fa; min-height: 100vh; }
.header-card { background: linear-gradient(135deg, #1e3c72, #2a5298); color: #fff; padding: 40rpx; border-radius: 20rpx; text-align: center; }
.title { font-size: 48rpx; font-weight: bold; }
.subtitle { font-size: 28rpx; margin-top: 10rpx; opacity: 0.9; }
.scan-area { background: #fff; margin-top: 30rpx; padding: 60rpx 0; border-radius: 20rpx; text-align: center; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.05); }
.scan-icon { font-size: 120rpx; color: #409EFF; margin-bottom: 20rpx; }
.scan-text { font-size: 40rpx; color: #303133; font-weight: bold; }
.scan-tip { font-size: 26rpx; color: #909399; margin-top: 10rpx; }
.manual-input { display: flex; margin-top: 20rpx; background: #fff; padding: 20rpx; border-radius: 12rpx; }
.code-input { flex: 1; border: 1rpx solid #dcdfe6; border-radius: 8rpx; padding: 16rpx; font-size: 30rpx; }
.mini-btn { margin-left: 20rpx; background: #409EFF; color: #fff; font-size: 28rpx; padding: 0 30rpx; border-radius: 8rpx; line-height: 76rpx; }
.todo-area { background: #fff; margin-top: 30rpx; padding: 30rpx; border-radius: 20rpx; }
.todo-title { font-size: 32rpx; font-weight: bold; margin-bottom: 20rpx; }
.todo-list { display: flex; justify-content: space-around; }
.todo-item { text-align: center; }
.todo-item .num { display: block; font-size: 44rpx; color: #409EFF; font-weight: bold; }
.todo-item .label { font-size: 26rpx; color: #606266; }
.menu-grid { display: flex; flex-wrap: wrap; margin-top: 30rpx; }
.grid-item { width: 33.33%; text-align: center; padding: 40rpx 0; background: #fff; border: 1rpx solid #f5f7fa; }
.grid-icon { display: block; font-size: 60rpx; margin-bottom: 10rpx; }
.grid-label { font-size: 28rpx; color: #606266; }
</style>
