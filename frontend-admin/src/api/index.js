import http from './http'

export const authApi = {
  login: data => http.post('/auth/login', data),
  me: () => http.get('/auth/me')
}

export const adminApi = {
  dashboard: params => http.get('/admin/dashboard', { params }),
  users: params => http.get('/admin/users', { params }),
  setRole: (uid, role) => http.put(`/admin/users/${uid}/role`, null, { params: { role } }),
  reports: status => http.get('/admin/reports', { params: { status_filter: status } }),
  handleReport: (rid, action) => http.post(`/admin/reports/${rid}/handle`, null, { params: { action } }),
  posts: params => http.get('/admin/posts', { params }),
  setPostStatus: (pid, status_v) => http.put(`/admin/posts/${pid}/status`, null, { params: { status_v } }),
  postDetail: pid => http.get(`/admin/posts/${pid}/detail`),
  setReplyStatus: (rid, status_v) => http.put(`/admin/replies/${rid}/status`, null, { params: { status_v } })
}

export const articleApi = {
  list: params => http.get('/content/articles', { params }),
  create: data => http.post('/content/articles', data),
  update: (id, data) => http.put(`/content/articles/${id}`, data),
  remove: id => http.delete(`/content/articles/${id}`)
}

export const counselorApi = {
  list: () => http.get('/appointment/counselors'),
  create: data => http.post('/appointment/counselors', data),
  update: (id, data) => http.put(`/appointment/counselors/${id}`, data),
  remove: id => http.delete(`/appointment/counselors/${id}`)
}
