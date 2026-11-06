import request from './request'

export const login = (data) => request.post('/api/admin/auth/login', data)
export const getProfile = () => request.get('/api/admin/auth/profile')
export const changePassword = (data) => request.put('/api/admin/auth/password', data)

export const getDashboard = () => request.get('/api/admin/statistics/dashboard')

export const getEquipmentList = (params) => request.get('/api/admin/equipment', { params })
export const getEquipmentDetail = (id) => request.get(`/api/admin/equipment/${id}`)
export const createEquipment = (data) => request.post('/api/admin/equipment', data)
export const updateEquipment = (id, data) => request.put(`/api/admin/equipment/${id}`, data)
export const deleteEquipment = (id) => request.delete(`/api/admin/equipment/${id}`)
export const changeEquipmentStatus = (id, status) => request.put(`/api/admin/equipment/${id}/status`, { status })
export const getQrcode = (id) => request.get(`/api/admin/equipment/${id}/qrcode`)
export const regenerateQrcode = (id) => request.post(`/api/admin/equipment/${id}/qrcode/regenerate`)
export const getEquipmentCategories = () => request.get('/api/admin/equipment/categories/all')
export const getEquipmentFieldDefs = () => request.get('/api/admin/equipment/field-defs/all')
export const createFieldDef = (data) => request.post('/api/admin/equipment/field-defs', data)
export const updateFieldDef = (id, data) => request.put(`/api/admin/equipment/field-defs/${id}`, data)
export const deleteFieldDef = (id) => request.delete(`/api/admin/equipment/field-defs/${id}`)
export const getEquipmentInsurance = (id) => request.get(`/api/admin/equipment/${id}/insurance`)
export const addInsurance = (id, data) => request.post(`/api/admin/equipment/${id}/insurance`, data)

export const getSpecialEquipmentList = (params) => request.get('/api/admin/special-equipment', { params })
export const getSpecialEquipmentDetail = (id) => request.get(`/api/admin/special-equipment/${id}`)
export const saveSpecialEquipment = (id, data) => request.post(`/api/admin/special-equipment/${id}`, data)
export const checkCompliance = (id) => request.post(`/api/admin/special-equipment/${id}/check`)

export const getMaintenancePlans = (params) => request.get('/api/admin/maintenance/plans', { params })
export const createMaintenancePlan = (data) => request.post('/api/admin/maintenance/plans', data)
export const updateMaintenancePlan = (id, data) => request.put(`/api/admin/maintenance/plans/${id}`, data)
export const deleteMaintenancePlan = (id) => request.delete(`/api/admin/maintenance/plans/${id}`)
export const getMaintenanceRecords = (params) => request.get('/api/admin/maintenance/records', { params })
export const createMaintenanceRecord = (data) => request.post('/api/admin/maintenance/records', data)
export const getMaintenanceReminders = (params) => request.get('/api/admin/maintenance/reminders', { params })
export const actionReminder = (id, action) => request.put(`/api/admin/maintenance/reminders/${id}`, { action })

export const getFuelRecords = (params) => request.get('/api/admin/fuel/records', { params })
export const createFuelRecord = (data) => request.post('/api/admin/fuel/records', data)
export const getFuelAnalysis = (params) => request.get('/api/admin/fuel/analysis', { params })

export const getOperationLogs = (params) => request.get('/api/admin/operation/logs', { params })

export const getRepairRequests = (params) => request.get('/api/admin/repair/requests', { params })
export const getRepairDetail = (id) => request.get(`/api/admin/repair/requests/${id}`)
export const actionRepair = (id, data) => request.put(`/api/admin/repair/requests/${id}/action`, data)

export const getTrainingPlans = (params) => request.get('/api/admin/training/plans', { params })
export const getTrainingDetail = (id) => request.get(`/api/admin/training/plans/${id}`)
export const createTrainingPlan = (data) => request.post('/api/admin/training/plans', data)
export const updateTrainingPlan = (id, data) => request.put(`/api/admin/training/plans/${id}`, data)
export const addParticipant = (id, data) => request.post(`/api/admin/training/plans/${id}/participants`, data)

export const getProjects = () => request.get('/api/admin/projects')
export const createProject = (data) => request.post('/api/admin/projects', data)

export const getUsers = (params) => request.get('/api/admin/users', { params })
export const createUser = (data) => request.post('/api/admin/users', data)
export const updateUser = (id, data) => request.put(`/api/admin/users/${id}`, data)
export const deleteUser = (id) => request.delete(`/api/admin/users/${id}`)
export const toggleUserStatus = (id) => request.put(`/api/admin/users/${id}/status`)
export const getRoles = () => request.get('/api/admin/users/roles/all')
export const getDepartments = () => request.get('/api/admin/users/departments/all')

export const getNotifications = (params) => request.get('/api/admin/notifications', { params })
export const getUnreadCount = () => request.get('/api/admin/notifications/unread-count')
export const readAllNotifications = () => request.put('/api/admin/notifications/read-all')

export const uploadFile = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request.post('/api/miniapp/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
