import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const access = ref(localStorage.getItem('access') || '')
  const refresh = ref(localStorage.getItem('refresh') || '')
  const isAuthenticated = computed(() => !!access.value)
  const isSeller = computed(() => user.value?.has_shop === true)

  function setTokens(data) {
    access.value = data.access
    refresh.value = data.refresh
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
  }

  function setUser(u) {
    user.value = u
    localStorage.setItem('user', JSON.stringify(u))
  }

  async function login(credentials) {
    const { data } = await authApi.login(credentials)
    setTokens({ access: data.access, refresh: data.refresh })
    setUser(data.user)
    return data
  }

  async function register(payload) {
    const { data } = await authApi.register(payload)
    setTokens(data.tokens)
    setUser(data.user)
    return data
  }

  async function fetchProfile() {
    const { data } = await authApi.profile()
    setUser(data)
    return data
  }

  function logout() {
    user.value = null
    access.value = ''
    refresh.value = ''
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('user')
  }

  return {
    user, access, refresh, isAuthenticated, isSeller,
    login, register, fetchProfile, logout, setUser
  }
})