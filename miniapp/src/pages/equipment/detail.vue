<template>
  <view class="container">
    <view class="equip-card" v-if="equipment">
      <image v-if="equipment.photo_url" :src="equipment.photo_url" class="equip-img" mode="aspectFill" />
      <view class="equip-name">{{ equipment.name }}</view>
      <view class="equip-info">编号：{{ equipment.equipment_code }}</view>
      <view class="equip-info">型号：{{ equipment.model || '-' }}</view>
      <view class="equip-info">驾驶员：{{ equipment.driver_name || '-' }} {{ equipment.driver_phone }}</view>
      <view class="equip-info">累计台时：{{ equipment.total_running_hours }} 小时</view>
      <view class="equip-info">状态：<text :class="'status-' + equipment.status">{{ statusText }}</text></view>

      <view v-if="equipment.is_special" class="compliance-card" :class="'compliance-' + specialStatus">
        <view class="compliance-title">特种设备合规状态：{{ complianceText }}</view>
        <view v-if="complianceIssues.length" class="compliance-issues">
          <view v-for="(issue, idx) in complianceIssues" :key="idx">• {{ issue }}</view>
        </view>
      </view>
    </view>

    <view class="menu-title">选择操作</view>
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
      equipment: null,
      token: '',
      menuList: [
        { label: '加油登记', icon: '⛽', path: '/pages/fuel/record' },
        { label: '运转记录', icon: '📋', path: '/pages/operation/log' },
        { label: '交接班', icon: '🔄', path: '/pages/operation/handover' },
        { label: '报修申请', icon: '🔧', path: '/pages/repair/request' },
        { label: '历史记录', icon: '📁', path: '/pages/history/list' },
      ]
    }
  },
  onLoad(options) {
    this.token = options.token || ''
    const cached = uni.getStorageSync('current_equipment')
    if (cached && cached.qr_token === this.token) {
      this.equipment = cached
    } else if (this.token) {
      this.loadEquipment()
    }
  },
  computed: {
    statusText() {
      const map = { 0: '闲置', 1: '使用中', 2: '维修中', 3: '停用', 4: '报废' }
      return map[this.equipment?.status] || '未知'
    },
    specialStatus() {
      return this.equipment?.special_ext?.compliance_status ?? 0
    },
    complianceText() {
      const map = { 0: '不合规', 1: '合规', 2: '即将过期', 3: '已过期' }
      return map[this.specialStatus] || '未配置'
    },
    complianceIssues() {
      try {
        return JSON.parse(this.equipment?.special_ext?.compliance_issues || '{}').issues || []
      } catch {
        return []
      }
    }
  },
  methods: {
    async loadEquipment() {
      uni.showLoading({ title: '加载中' })
      try {
        this.equipment = await scanEquipment(this.token)
        uni.setStorageSync('current_equipment', this.equipment)
      } catch (e) {
        uni.showToast({ title: e.message || '加载失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    goTo(path) {
      uni.navigateTo({ url: path })
    }
  }
}
</script>

<style scoped>
.container { padding: 20rpx; background: #f5f7fa; min-height: 100vh; }
.equip-card { background: #fff; border-radius: 20rpx; padding: 30rpx; }
.equip-img { width: 100%; height: 300rpx; border-radius: 12rpx; margin-bottom: 20rpx; background: #eee; }
.equip-name { font-size: 40rpx; font-weight: bold; color: #303133; margin-bottom: 16rpx; }
.equip-info { font-size: 30rpx; color: #606266; margin-top: 10rpx; }
.status-1 { color: #67C23A; }
.status-2 { color: #E6A23C; }
.compliance-card { margin-top: 20rpx; padding: 20rpx; border-radius: 12rpx; }
.compliance-1 { background: #f0f9eb; color: #67C23A; }
.compliance-2 { background: #fdf6ec; color: #E6A23C; }
.compliance-0, .compliance-3 { background: #fef0f0; color: #F56C6C; }
.compliance-title { font-size: 32rpx; font-weight: bold; }
.compliance-issues { font-size: 28rpx; margin-top: 10rpx; }
.menu-title { font-size: 32rpx; font-weight: bold; margin: 30rpx 0 20rpx; }
.menu-grid { display: flex; flex-wrap: wrap; }
.grid-item { width: 33.33%; text-align: center; padding: 40rpx 0; background: #fff; border: 1rpx solid #f5f7fa; }
.grid-icon { display: block; font-size: 60rpx; margin-bottom: 10rpx; }
.grid-label { font-size: 28rpx; color: #606266; }
</style>
