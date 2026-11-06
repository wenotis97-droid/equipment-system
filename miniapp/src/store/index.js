import { createStore } from 'vuex'

export default createStore({
  state: {
    token: uni.getStorageSync('session_token') || '',
    userInfo: uni.getStorageSync('user_info') || null,
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      uni.setStorageSync('session_token', token)
    },
    SET_USER(state, user) {
      state.userInfo = user
      uni.setStorageSync('user_info', user)
    },
    LOGOUT(state) {
      state.token = ''
      state.userInfo = null
      uni.removeStorageSync('session_token')
      uni.removeStorageSync('user_info')
    }
  },
  getters: {
    isLogin: state => !!state.token,
  }
})
