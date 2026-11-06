import { get, post } from './request'

export const wxLogin = (code) => post('/api/miniapp/auth/login', { code })
export const getProfile = () => get('/api/miniapp/auth/profile')

export const scanEquipment = (token) => get('/api/miniapp/equipment/by-qr/' + token)
export const getEquipmentDetail = (id) => get('/api/miniapp/equipment/' + id)

export const submitFuel = (data) => post('/api/miniapp/fuel/records', data)
export const getFuelHistory = () => get('/api/miniapp/fuel/history')

export const submitOperation = (data) => post('/api/miniapp/operation/logs', data)
export const getTodayLogs = () => get('/api/miniapp/operation/today')

export const submitRepair = (data) => post('/api/miniapp/repair/requests', data)
export const getMyRepairs = () => get('/api/miniapp/repair/my')

export const getTrainingList = () => get('/api/miniapp/training/list')
export const getTrainingDetail = (id) => get('/api/miniapp/training/' + id)
export const submitTrainingExam = (id, data) => post('/api/miniapp/training/' + id + '/exam', data)

export const uploadFile = (filePath) => {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: 'http://localhost:8000/api/miniapp/upload',
      filePath,
      name: 'file',
      header: { 'X-Session-Token': uni.getStorageSync('session_token') || '' },
      success: (res) => {
        const data = JSON.parse(res.data)
        if (data.code === 200) resolve(data.data.url)
        else reject(new Error(data.message))
      },
      fail: reject
    })
  })
}
