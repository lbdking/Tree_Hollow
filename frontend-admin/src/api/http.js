import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const http = axios.create({ baseURL: '/api/v1', timeout: 30000 })
http.interceptors.request.use(cfg => {
  const t = localStorage.getItem('th_admin_token')
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})
http.interceptors.response.use(
  r => r.data,
  err => {
    const status = err?.response?.status
    const msg = err?.response?.data?.detail || err.message
    if (status === 401) {
      localStorage.removeItem('th_admin_token')
      router.replace('/login')
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(err)
  }
)
export default http
