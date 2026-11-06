<template>
  <view class="container">
    <view class="form-card">
      <view class="form-title">加油登记</view>
      <view class="form-item">
        <text class="label">加油时间</text>
        <picker mode="multiSelector" :range="dateRange" :value="dateIndex" @change="onDateChange">
          <view class="picker">{{ form.fuel_date }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">油品</text>
        <input v-model="form.fuel_type" class="input" placeholder="如 0#柴油" />
      </view>
      <view class="form-item">
        <text class="label">加油量（升）</text>
        <input v-model="form.volume" type="digit" class="input" placeholder="请输入加油量" />
      </view>
      <view class="form-item">
        <text class="label">单价</text>
        <input v-model="form.unit_price" type="digit" class="input" placeholder="请输入单价" />
      </view>
      <view class="form-item">
        <text class="label">当前台时读数</text>
        <input v-model="form.running_hours" type="digit" class="input" placeholder="请输入台时读数" />
      </view>
      <view class="form-item">
        <text class="label">加油人</text>
        <input v-model="form.operator_name" class="input" placeholder="请输入姓名" />
      </view>
      <view class="form-item">
        <text class="label">小票照片</text>
        <button class="photo-btn" @click="choosePhoto">选择照片</button>
        <image v-if="form.photo_url" :src="form.photo_url" class="preview" mode="aspectFit" />
      </view>
      <button class="submit-btn" @click="submit">提 交</button>
    </view>
  </view>
</template>

<script>
import { submitFuel, uploadFile } from '@/api'
export default {
  data() {
    return {
      form: {
        equipment_id: null,
        fuel_date: '',
        fuel_type: '0#柴油',
        volume: '',
        unit_price: '',
        running_hours: '',
        operator_name: '',
        photo_url: ''
      },
      dateRange: [[], [], [], [], [], []],
      dateIndex: [0, 0, 0, 0, 0, 0]
    }
  },
  onShow() {
    const eq = uni.getStorageSync('current_equipment')
    if (eq) this.form.equipment_id = eq.id
    this.initDateTime()
  },
  methods: {
    initDateTime() {
      const now = new Date()
      this.form.fuel_date = this.formatDate(now)
    },
    formatDate(d) {
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}:${String(d.getSeconds()).padStart(2,'0')}`
    },
    onDateChange(e) {
      // 简化：实际可用完整日期选择
    },
    choosePhoto() {
      uni.chooseImage({
        count: 1,
        success: async (res) => {
          try {
            const url = await uploadFile(res.tempFilePaths[0])
            this.form.photo_url = url
          } catch (e) {
            uni.showToast({ title: '上传失败', icon: 'none' })
          }
        }
      })
    },
    async submit() {
      if (!this.form.equipment_id) return uni.showToast({ title: '请先扫码选择设备', icon: 'none' })
      if (!this.form.volume) return uni.showToast({ title: '请输入加油量', icon: 'none' })
      try {
        await submitFuel({
          ...this.form,
          volume: Number(this.form.volume),
          unit_price: this.form.unit_price ? Number(this.form.unit_price) : null,
          running_hours: this.form.running_hours ? Number(this.form.running_hours) : null,
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
.input, .picker { border: 1rpx solid #dcdfe6; border-radius: 10rpx; padding: 20rpx; font-size: 32rpx; background: #fff; }
.photo-btn { background: #ecf5ff; color: #409EFF; font-size: 28rpx; margin-top: 10rpx; }
.preview { width: 200rpx; height: 200rpx; margin-top: 20rpx; border-radius: 10rpx; }
.submit-btn { background: #409EFF; color: #fff; font-size: 36rpx; border-radius: 12rpx; margin-top: 40rpx; }
</style>
