import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({ baseURL, headers: { 'Content-Type': 'application/json' } })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing = null

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config
    const status = error.response?.status

    if (status === 401 && !original._retry && !original.url.includes('/auth/login/') && !original.url.includes('/auth/token/refresh/')) {
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) {
        clearTokens(); redirectToLogin(); return Promise.reject(error)
      }
      original._retry = true
      try {
        refreshing = refreshing || axios.post(`${baseURL}/auth/token/refresh/`, { refresh })
        const { data } = await refreshing
        refreshing = null
        localStorage.setItem('access_token', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch (e) {
        refreshing = null
        clearTokens(); redirectToLogin()
        return Promise.reject(e)
      }
    }
    return Promise.reject(error)
  }
)

function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}
function redirectToLogin() {
  if (!location.pathname.startsWith('/login')) location.href = '/login'
}

export default api