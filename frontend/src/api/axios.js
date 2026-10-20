import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const baseURL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing = null

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (!original || original._retry) return Promise.reject(error)

    const isRefreshCall = original.url?.includes('/auth/token/refresh')
    if (
      error.response?.status === 401 &&
      localStorage.getItem('refresh') &&
      !isRefreshCall
    ) {
      original._retry = true
      try {
        if (!refreshing) {
          refreshing = axios.post(`${baseURL}/auth/token/refresh/`, {
            refresh: localStorage.getItem('refresh')
          })
        }
        const { data } = await refreshing
        refreshing = null
        localStorage.setItem('access', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch (e) {
        refreshing = null
        const auth = useAuthStore()
        auth.logout()
        router.push({ name: 'login' })
      }
    }
    return Promise.reject(error)
  }
)

export default api