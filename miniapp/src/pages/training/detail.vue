<template>
  <view class="container">
    <view class="card" v-if="detail">
      <view class="title">{{ detail.plan_name }}</view>
      <view class="info">类型：{{ detail.training_type }}</view>
      <view class="info">讲师：{{ detail.instructor || '-' }}</view>
      <view class="info">地点：{{ detail.location || '-' }}</view>
      <view class="info">时长：{{ detail.duration_hours }} 小时</view>
      <view class="content">{{ detail.content_summary }}</view>

      <view v-if="detail.status === 1" class="exam-area">
        <view class="exam-title">培训考核</view>
        <view class="form-item">
          <text class="label">姓名</text>
          <input v-model="exam.user_name" class="input" placeholder="请输入姓名" />
        </view>
        <view class="form-item">
          <text class="label">考核分数</text>
          <input v-model="exam.exam_score" type="digit" class="input" placeholder="请输入分数" />
        </view>
        <button class="submit-btn" @click="submitExam">提交考核</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getTrainingDetail, submitTrainingExam } from '@/api'
export default {
  data() {
    return {
      detail: null,
      exam: { user_name: '', exam_score: '' }
    }
  },
  onLoad(options) {
    this.loadData(options.id)
    const user = uni.getStorageSync('user_info')
    this.exam.user_name = user?.real_name || ''
  },
  methods: {
    async loadData(id) {
      try {
        this.detail = await getTrainingDetail(id)
      } catch (e) {
        uni.showToast({ title: e.message || '加载失败', icon: 'none' })
      }
    },
    async submitExam() {
      try {
        await submitTrainingExam(this.detail.id, {
          ...this.exam,
          exam_score: Number(this.exam.exam_score),
          exam_passed: Number(this.exam.exam_score) >= 60 ? 1 : 0
        })
        uni.showToast({ title: '提交成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 800)
      } catch (e) {
        uni.showToast({ title: e.message || '提交失败', icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.container { padding: 20rpx; background: #f5f7fa; min-height: 100vh; }
.card { background: #fff; border-radius: 20rpx; padding: 30rpx; }
.title { font-size: 40rpx; font-weight: bold; }
.info { font-size: 30rpx; color: #606266; margin-top: 12rpx; }
.content { margin-top: 30rpx; padding: 20rpx; background: #f5f7fa; border-radius: 12rpx; font-size: 30rpx; color: #303133; }
.exam-area { margin-top: 40rpx; border-top: 1rpx solid #ebeef5; padding-top: 30rpx; }
.exam-title { font-size: 34rpx; font-weight: bold; margin-bottom: 20rpx; }
.form-item { margin-bottom: 20rpx; }
.label { font-size: 30rpx; color: #606266; margin-bottom: 8rpx; display: block; }
.input { border: 1rpx solid #dcdfe6; border-radius: 10rpx; padding: 16rpx; font-size: 30rpx; }
.submit-btn { background: #67C23A; color: #fff; font-size: 34rpx; border-radius: 12rpx; margin-top: 20rpx; }
</style>
