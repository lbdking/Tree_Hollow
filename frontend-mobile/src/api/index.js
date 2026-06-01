import http from './http'

export const authApi = {
  register: data => http.post('/auth/register', data),
  login: data => http.post('/auth/login', data),
  me: () => http.get('/auth/me'),
  updateMe: data => http.put('/auth/me', data)
}

export const hollowApi = {
  list: params => http.get('/hollow/posts', { params }),
  detail: id => http.get(`/hollow/posts/${id}`),
  create: data => http.post('/hollow/posts', data),
  remove: id => http.delete(`/hollow/posts/${id}`),
  replies: id => http.get(`/hollow/posts/${id}/replies`),
  reply: (id, data) => http.post(`/hollow/posts/${id}/replies`, data),
  like: (target_type, target_id) => http.post('/hollow/like', null, { params: { target_type, target_id } }),
  report: data => http.post('/hollow/report', data),
  myPosts: () => http.get('/hollow/my-posts')
}

export const contentApi = {
  articles: params => http.get('/content/articles', { params }),
  article: id => http.get(`/content/articles/${id}`),
  saveMood: data => http.post('/content/mood', data),
  listMood: params => http.get('/content/mood', { params }),
  saveBreathing: data => http.post('/content/breathing', data),
  breathingStats: () => http.get('/content/breathing/stats')
}

export const groupApi = {
  groups: params => http.get('/group/groups', { params }),
  groupDetail: id => http.get(`/group/groups/${id}`),
  join: id => http.post(`/group/groups/${id}/join`),
  leave: id => http.post(`/group/groups/${id}/leave`),
  activities: params => http.get('/group/activities', { params }),
  enroll: id => http.post(`/group/activities/${id}/enroll`),
  cancelEnroll: id => http.post(`/group/activities/${id}/cancel`)
}

export const appointmentApi = {
  counselors: () => http.get('/appointment/counselors'),
  counselor: id => http.get(`/appointment/counselors/${id}`),
  create: data => http.post('/appointment/appointments', data),
  myAppointments: () => http.get('/appointment/appointments/my')
}

export const notificationApi = {
  list: params => http.get('/notification/list', { params }),
  unread: () => http.get('/notification/unread-count'),
  read: id => http.post(`/notification/read/${id}`),
  readAll: () => http.post('/notification/read-all')
}

export const aiApi = {
  sessions: () => http.get('/ai/sessions'),
  createSession: () => http.post('/ai/sessions'),
  messages: id => http.get(`/ai/sessions/${id}/messages`),
  removeSession: id => http.delete(`/ai/sessions/${id}`),
  // 流式：直接 fetch
  streamChat: async (sessionId, content, { onDelta, onSession, onRag, onDone, onError, useRag = true, fileIds = null } = {}) => {
    const token = localStorage.getItem('th_token')
    const resp = await fetch('/api/v1/ai/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ session_id: sessionId, content, use_rag: useRag, file_ids: fileIds })
    })
    if (!resp.ok || !resp.body) {
      onError && onError(new Error('AI 服务异常'))
      return
    }
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const parts = buf.split('\n\n')
      buf = parts.pop() || ''
      for (const part of parts) {
        const line = part.replace(/^data:\s?/, '').trim()
        if (!line) continue
        try {
          const obj = JSON.parse(line)
          if (obj.type === 'session') onSession && onSession(obj.session_id)
          else if (obj.type === 'rag') onRag && onRag(obj.hits)
          else if (obj.type === 'delta') onDelta && onDelta(obj.content)
          else if (obj.type === 'done') onDone && onDone(obj.content)
          else if (obj.type === 'error') onError && onError(new Error(obj.content))
        } catch (e) {}
      }
    }
  }
}

export const knowledgeApi = {
  list: () => http.get('/knowledge/files'),
  upload: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return http.post('/knowledge/files', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  remove: id => http.delete(`/knowledge/files/${id}`),
  toggle: id => http.put(`/knowledge/files/${id}/toggle`),
  search: (query, top_k = 4) => http.post('/knowledge/search', null, { params: { query, top_k } })
}
