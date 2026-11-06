<template>
  <view class="container">
    <view class="tabs">
      <view class="tab" :class="{active: activeTab === 'fuel'}" @click="activeTab = 'fuel'">加油记录</view>
      <view class="tab" :class="{active: activeTab === 'operation'}" @click="activeTab = 'operation'">运转记录</view>
      <view class="tab" :class="{active: activeTab === 'repair'}" @click="activeTab = 'repair'">报修记录</view>
    </view>

    <view v-if="activeTab === 'fuel'" class="list">
      <view class="item" v-for="item in fuelList" :key="item.id">
        <view class="item-title">{{ item.equipment_name || '设备' }}</view>
        <view class="item-info">{{ item.fuel_date }} · {{ item.volume }}L · ¥{{ item.total_amount }}</view>
      </view>
      <view v-if="!fuelList.length" class="empty">暂无记录</view>
    </view>

    <view v-if="activeTab === 'operation'" class="list">
      <view class="item" v-for="item in operationList" :key="item.id">
        <view class="item-title">{{ item.equipment_name || '设备' }}</view>
        <view class="item-info">{{ item.log_date }} · 运转 {{ item.running_hours }} 小时</view>
      </view>
      <view v-if="!operationList.length" class="empty">暂无记录</view>
    </view>

    <view v-if="activeTab === 'repair'" class="list">
      <view class="item" v-for="item in repairList" :key="item.id">
        <view class="item-title">{{ item.equipment_name || '设备' }}</view>
        <view class="item-info">{{ item.fault_type }} · {{ statusText(item.status) }}</view>
      </view>
      <view v-if="!repairList.length" class="empty">暂无记录</view>
    </view>
  </view>
</template>

<script>
import { getFuelHistory, getTodayLogs, getMyRepairs } from '@/api'
export default {
  data() {
    return {
      activeTab: 'fuel',
      fuelList: [],
      operationList: [],
      repairList: []
    }
  },
  onShow() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      try {
        const fuel = await getFuelHistory()
        this.fuelList = fuel.list || []
      } catch (e) {}
      try {
        const op = await getTodayLogs()
        this.operationList = op || []
      } catch (e) {}
      try {
        const repair = await getMyRepairs()
        this.repairList = repair || []
      } catch (e) {}
    },
    statusText(s) { return { 0: '待审批', 1: '待维修', 2: '维修中', 3: '已完成', 4: '已驳回' }[s] }
  }
}
</script>

<style scoped>
.container { padding: 20rpx; background: #f5f7fa; min-height: 100vh; }
.tabs { display: flex; background: #fff; border-radius: 12rpx; overflow: hidden; margin-bottom: 20rpx; }
.tab { flex: 1; text-align: center; padding: 24rpx 0; font-size: 30rpx; color: #606266; }
.tab.active { background: #409EFF; color: #fff; }
.list { background: #fff; border-radius: 16rpx; padding: 20rpx; }
.item { padding: 20rpx 0; border-bottom: 1rpx solid #ebeef5; }
.item-title { font-size: 32rpx; color: #303133; }
.item-info { font-size: 26rpx; color: #909399; margin-top: 6rpx; }
.empty { text-align: center; color: #909399; padding: 60rpx 0; }
</style>
