<template>
  <view class="container">
    <view class="form-card">
      <view class="form-title">报修申请</view>
      <view class="form-item">
        <text class="label">故障类型</text>
        <picker :range="faultTypes" :value="faultTypeIndex" @change="e => form.fault_type = faultTypes[e.detail.value]">
          <view class="picker">{{ form.fault_type }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">严重程度</text>
        <radio-group @change="e => form.fault_level = Number(e.detail.value)">
          <label><radio value="1" :checked="form.fault_level === 1" />一般</label>
          <label style="margin-left: 30rpx;"><radio value="2" :checked="form.fault_level === 2" />严重</label>
          <label style="margin-left: 30rpx;"><radio value="3" :checked="form.fault_level === 3" />紧急</label>
        </radio-group>
      </view>
      <view class="form-item">
        <text class="label">故障描述</text>
        <textarea v-model="form.fault_description" class="textarea" placeholder="请描述故障现象" />
      </view>
      <view class="form-item">
        <text class="label">拍照</text>
        <button class="photo-btn" @click="choosePhoto">选择故障照片</button>
        <image v-if="faultPhoto" :src="faultPhoto" class="preview" mode="aspectFit" />
      </view>
      <button class="submit-btn" @click="submit">提 交</button>
    </view>
  </view>
</template>

<script>
import { submitRepair, uploadFile } from '@/api'
export default {
  data() {
    return {
      faultTypes: ['发动机', '液压', '电气', '结构', '其他'],
      faultTypeIndex: 4,
      form: {
        equipment_id: null,
        fault_type: '其他',
        fault_level: 1,
        fault_description: '',
        fault_photos: ''
      },
      faultPhoto: ''
    }
  },
  onShow() {
    const eq = uni.getStorageSync('current_equipment')
    if (eq) this.form.equipment_id = eq.id
  },
  methods: {
    choosePhoto() {
      uni.chooseImage({
        count: 1,
        success: async (res) => {
          try {
            const url = await uploadFile(res.tempFilePaths[0])
            this.faultPhoto = url
            this.form.fault_photos = JSON.stringify([url])
          } catch (e) {
            uni.showToast({ title: '上传失败', icon: 'none' })
          }
        }
      })
    },
    async submit() {
      if (!this.form.equipment_id) return uni.showToast({ title: '请先扫码选择设备', icon: 'none' })
      if (!this.form.fault_description) return uni.showToast({ title: '请描述故障', icon: 'none' })
      try {
        await submitRepair(this.form)
        uni.showToast({ title: '报修成功', icon: 'success' })
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
.picker, .textarea { border: 1rpx solid #dcdfe6; border-radius: 10rpx; padding: 20rpx; font-size: 32rpx; background: #fff; }
.textarea { width: 100%; height: 180rpx; }
.photo-btn { background: #ecf5ff; color: #409EFF; font-size: 28rpx; margin-top: 10rpx; }
.preview { width: 200rpx; height: 200rpx; margin-top: 20rpx; border-radius: 10rpx; }
.submit-btn { background: #F56C6C; color: #fff; font-size: 36rpx; border-radius: 12rpx; margin-top: 40rpx; }
</style>
