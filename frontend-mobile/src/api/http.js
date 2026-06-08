import axios from 'axios'
import { showFailToast } from 'vant'
import router from '../router'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

http.interceptors.request.use(cfg => {
  const token = localStorage.getItem('th_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

http.interceptors.response.use(
  resp => resp.data,
  err => {
    const status = err?.response?.status
    const msg = err?.response?.data?.detail || err.message || '请求失败'
    if (status === 401) {
      localStorage.removeItem('th_token')
      localStorage.removeItem('th_user')
      router.replace('/login')
    } else {
      showFailToast(msg)
    }
    return Promise.reject(err)
  }
)

export default http
