<template>
  <view class="container">
    <view class="form-card">
      <view class="form-title">运转记录</view>
      <view class="form-item">
        <text class="label">日期</text>
        <picker mode="date" :value="form.log_date" @change="e => form.log_date = e.detail.value">
          <view class="picker">{{ form.log_date }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">班次</text>
        <radio-group @change="e => form.shift = Number(e.detail.value)">
          <label><radio value="1" :checked="form.shift === 1" />白班</label>
          <label style="margin-left: 30rpx;"><radio value="2" :checked="form.shift === 2" />夜班</label>
        </radio-group>
      </view>
      <view class="form-item">
        <text class="label">开工台时</text>
        <input v-model="form.start_hours" type="digit" class="input" placeholder="开工时台时读数" />
      </view>
      <view class="form-item">
        <text class="label">收工台时</text>
        <input v-model="form.end_hours" type="digit" class="input" placeholder="收工时台时读数" />
      </view>
      <view class="form-item">
        <text class="label">工作内容</text>
        <textarea v-model="form.work_content" class="textarea" placeholder="简要描述工作内容" />
      </view>
      <view class="form-item">
        <text class="label">作业地点</text>
        <input v-model="form.work_location" class="input" placeholder="作业地点" />
      </view>
      <view class="form-item">
        <text class="label">操作人</text>
        <input v-model="form.operator_name" class="input" placeholder="操作人姓名" />
      </view>
      <view class="form-item">
        <text class="label">设备状况</text>
        <textarea v-model="form.equipment_condition" class="textarea" placeholder="设备状况说明" />
      </view>
      <view class="form-item">
        <text class="label">安全检查</text>
        <switch :checked="form.safety_check === 1" @change="e => form.safety_check = e.detail.value ? 1 : 0" />
      </view>
      <view class="form-item" v-if="!form.safety_check">
        <text class="label">安全问题</text>
        <textarea v-model="form.safety_issues" class="textarea" placeholder="如发现安全问题请填写" />
      </view>
      <button class="submit-btn" @click="submit">提 交</button>
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
        work_content: '',
        work_location: '',
        operator_name: '',
        equipment_condition: '正常',
        safety_check: 1,
        safety_issues: ''
      }
    }
  },
  onShow() {
    const eq = uni.getStorageSync('current_equipment')
    if (eq) this.form.equipment_id = eq.id
    this.form.log_date = new Date().toISOString().slice(0, 10)
  },
  methods: {
    async submit() {
      if (!this.form.equipment_id) return uni.showToast({ title: '请先扫码选择设备', icon: 'none' })
      if (!this.form.start_hours || !this.form.end_hours) return uni.showToast({ title: '请输入台时读数', icon: 'none' })
      try {
        await submitOperation({
          ...this.form,
          start_hours: Number(this.form.start_hours),
          end_hours: Number(this.form.end_hours),
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
.form-card { background: #fff; border-radius: 20rpx; padding: 30rpx; }
.form-title { font-size: 40rpx; font-weight: bold; margin-bottom: 30rpx; }
.form-item { margin-bottom: 30rpx; }
.label { display: block; font-size: 30rpx; color: #606266; margin-bottom: 10rpx; }
.input, .picker, .textarea { border: 1rpx solid #dcdfe6; border-radius: 10rpx; padding: 20rpx; font-size: 32rpx; background: #fff; }
.textarea { width: 100%; height: 140rpx; }
.submit-btn { background: #409EFF; color: #fff; font-size: 36rpx; border-radius: 12rpx; margin-top: 40rpx; }
</style>
