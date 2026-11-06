const BASE_URL = 'http://localhost:8000'
const MAX_RETRY = 2

function request(options) {
  return new Promise((resolve, reject) => {
    const doRequest = (retryCount = 0) => {
      uni.request({
        url: BASE_URL + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: {
          'Content-Type': 'application/json',
          'X-Session-Token': uni.getStorageSync('session_token') || ''
        },
        timeout: 10000,
        success: (res) => {
          if (res.statusCode === 200 && res.data.code === 200) {
            resolve(res.data.data)
          } else {
            if (res.statusCode === 401) {
              uni.removeStorageSync('session_token')
              uni.showToast({ title: '登录已过期', icon: 'none' })
            }
            reject(new Error(res.data.message || '请求失败'))
          }
        },
        fail: (err) => {
          if (retryCount < MAX_RETRY) {
            setTimeout(() => doRequest(retryCount + 1), 1000 * (retryCount + 1))
          } else {
            // 写操作缓存到本地待提交
            if ((options.method || 'GET') !== 'GET') {
              cachePending(options.url, options.method, options.data)
              uni.showToast({ title: '网络异常，已缓存待提交', icon: 'none' })
            }
            reject(new Error('网络请求失败'))
          }
        }
      })
    }
    doRequest()
  })
}

function cachePending(url, method, data) {
  const pending = uni.getStorageSync('pending_requests') || []
  pending.push({ url, method, data, timestamp: Date.now() })
  uni.setStorageSync('pending_requests', pending)
}

export function get(url, params) { return request({ url, method: 'GET', data: params }) }
export function post(url, data) { return request({ url, method: 'POST', data }) }
export function put(url, data) { return request({ url, method: 'PUT', data }) }

export default request
