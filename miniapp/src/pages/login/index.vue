<template>
  <view class="container">
    <view class="login-card">
      <view class="title">设备管理系统</view>
      <view class="subtitle">使用人员登录</view>
      <button class="wx-btn" @click="wxLogin">微信一键登录</button>
      <view class="tip">首次登录将自动创建操作员账号</view>
    </view>
  </view>
</template>

<script>
import { wxLogin, getProfile } from '@/api'
export default {
  methods: {
    wxLogin() {
      uni.login({
        provider: 'weixin',
        success: async (res) => {
          try {
            const data = await wxLogin(res.code)
            uni.setStorageSync('session_token', data.access_token)
            uni.setStorageSync('user_info', data.user)
            uni.showToast({ title: '登录成功', icon: 'success' })
            setTimeout(() => {
              uni.switchTab({ url: '/pages/index/index' })
            }, 800)
          } catch (e) {
            uni.showToast({ title: e.message || '登录失败', icon: 'none' })
          }
        },
        fail: () => {
          uni.showToast({ title: '微信登录失败', icon: 'none' })
        }
      })
    }
  }
}
</script>

<style scoped>
.container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #1e3c72, #2a5298); }
.login-card { background: #fff; width: 80%; border-radius: 20rpx; padding: 60rpx 40rpx; text-align: center; }
.title { font-size: 48rpx; font-weight: bold; color: #303133; }
.subtitle { font-size: 28rpx; color: #909399; margin: 20rpx 0 60rpx; }
.wx-btn { background: #07c160; color: #fff; font-size: 34rpx; border-radius: 12rpx; }
.tip { font-size: 24rpx; color: #909399; margin-top: 30rpx; }
</style>
