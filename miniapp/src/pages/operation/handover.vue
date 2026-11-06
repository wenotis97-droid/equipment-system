<template>
  <view class="container">
    <view class="form-card">
      <view class="form-title">交接班</view>
      <view class="tip">交接班登记将创建一条运转记录，并标记交接状态</view>
      <view class="form-item">
        <text class="label">接收人</text>
        <input v-model="form.handover_to" class="input" placeholder="接收人姓名" />
      </view>
      <view class="form-item">
        <text class="label">开工台时</text>
        <input v-model="form.start_hours" type="digit" class="input" placeholder="开工台时读数" />
      </view>
      <view class="form-item">
        <text class="label">收工台时</text>
        <input v-model="form.end_hours" type="digit" class="input" placeholder="收工台时读数" />
      </view>
      <view class="form-item">
        <text class="label">设备状况</text>
        <textarea v-model="form.equipment_condition" class="textarea" placeholder="设备状况说明" />
      </view>
      <button class="submit-btn" @click="submit">确认交接</button>
    </view>
  </view>
</template>

<script>
import { submitOperation } from '@/api'
export default {
  data() {
    return {
      form: {
        equipment_id: null,
        log_date: '',
        shift: 1,
        start_hours: '',
        end_hours: '',
        work_content: '交接班',
        operator_name: '',
        handover_to: '',
        equipment_condition: '正常',
        safety_check: 1
      }
    }
  },
  onShow() {
    const eq = uni.getStorageSync('current_equipment')
    if (eq) this.form.equipment_id = eq.id
    this.form.log_date = new Date().toISOString().slice(0, 10)
    const user = uni.getStorageSync('user_info')
    this.form.operator_name = user?.real_name || ''
  },
  methods: {
    async submit() {
      if (!this.form.handover_to) return uni.showToast({ title: '请输入接收人', icon: 'none' })
      try {
        await submitOperation({
          ...this.form,
          start_hours: Number(this.form.start_hours),
          end_hours: Number(this.form.end_hours),
        })
        uni.showToast({ title: '交接成功', icon: 'success' })
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
.form-card { background: #fff; border-radius: 20rpx; padding: 30rpx; }
.form-title { font-size: 40rpx; font-weight: bold; margin-bottom: 10rpx; }
.tip { font-size: 26rpx; color: #909399; margin-bottom: 30rpx; }
.form-item { margin-bottom: 30rpx; }
.label { display: block; font-size: 30rpx; color: #606266; margin-bottom: 10rpx; }
.input, .textarea { border: 1rpx solid #dcdfe6; border-radius: 10rpx; padding: 20rpx; font-size: 32rpx; }
.textarea { width: 100%; height: 140rpx; }
.submit-btn { background: #409EFF; color: #fff; font-size: 36rpx; border-radius: 12rpx; margin-top: 40rpx; }
</style>
