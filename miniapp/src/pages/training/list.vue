<template>
  <view class="container">
    <view class="list" v-if="list.length">
      <view class="item" v-for="item in list" :key="item.id" @click="viewDetail(item)">
        <view class="item-title">{{ item.plan_name }}</view>
        <view class="item-info">类型：{{ item.training_type }}</view>
        <view class="item-info">计划时间：{{ item.planned_date || '-' }}</view>
        <view class="item-info">培训时长：{{ item.duration_hours }} 小时</view>
        <view class="item-status" :class="'status-' + item.status">{{ statusText(item.status) }}</view>
      </view>
    </view>
    <view v-else class="empty">暂无培训计划</view>
  </view>
</template>

<script>
import { getTrainingList } from '@/api'
export default {
  data() { return { list: [] } },
  onShow() { this.loadData() },
  methods: {
    async loadData() {
      try {
        const res = await getTrainingList()
        this.list = res.list || []
      } catch (e) {
        uni.showToast({ title: e.message || '加载失败', icon: 'none' })
      }
    },
    statusText(s) { return { 0: '计划中', 1: '已发布', 2: '已完成', 3: '已取消' }[s] },
    viewDetail(item) {
      uni.navigateTo({ url: '/pages/training/detail?id=' + item.id })
    }
  }
}
</script>

<style scoped>
.container { padding: 20rpx; background: #f5f7fa; min-height: 100vh; }
.item { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 20rpx; position: relative; }
.item-title { font-size: 34rpx; font-weight: bold; color: #303133; }
.item-info { font-size: 28rpx; color: #606266; margin-top: 8rpx; }
.item-status { position: absolute; right: 24rpx; top: 24rpx; font-size: 26rpx; padding: 4rpx 16rpx; border-radius: 8rpx; }
.status-1 { background: #ecf5ff; color: #409EFF; }
.status-2 { background: #f0f9eb; color: #67C23A; }
.empty { text-align: center; color: #909399; padding: 100rpx 0; }
</style>
