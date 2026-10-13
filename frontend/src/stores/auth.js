import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const fullName = computed(() => {
    if (!user.value) return ''
    return [user.value.first_name, user.value.last_name].filter(Boolean).join(' ') || user.value.email
  })

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    if (access) localStorage.setItem('access_token', access)
    if (refresh) localStorage.setItem('refresh_token', refresh)
  }

  async function login(email, password) {
    const { data } = await api.post('/auth/login/', { email, password })
    setTokens(data.access, data.refresh)
    await fetchProfile().catch(() => {})
  }

  async function register(payload) {
  // payload уже содержит password_confirm — не трогаем
  return api.post('/auth/register/', payload)
  }


  async function fetchProfile() {
    const { data } = await api.get('/auth/profile/')
    user.value = data
    return data
  }

  async function updateProfile(payload) {
    const { data } = await api.patch('/auth/profile/', payload)
    user.value = data
    return data
  }

  async function logout() {
    try {
      if (refreshToken.value) await api.post('/auth/logout/', { refresh: refreshToken.value })
    } catch { /* ignore */ }
    setTokens(null, null)
    user.value = null
  }

  async function deactivateAccount() {
    await api.post('/auth/deactivate-account/')
    setTokens(null, null)
    user.value = null
  }

  async function changePassword(oldPassword, newPassword, newPasswordConfirm) {
    return api.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    })
  }

  // --- Verification codes ---
  async function sendVerificationCode(email) {
    return api.post('/auth/send-verification-code/', { email })
  }
  async function verifyVerificationCode(email, code) {
    return api.post('/auth/verify-verification-code/', { email, code })
  }

  // --- Password reset flow ---
  async function sendResetCode(email) {
    return api.post('/auth/send-password-reset-code/', { email })
  }
  async function verifyResetCode(email, code) {
    const { data } = await api.post('/auth/verify-password-reset-code/', { email, code })
    return data
  }
  async function resetPassword(email, code, newPassword, passwordConfirm) {
  // Сначала пробуем общепринятые имена. Если бэкенд хочет new_password/new_password_confirm —
  // поменяй ключи на них (см. ниже, как узнать точно)
  return api.post('/auth/password-reset/', {
    email,
    code,
    new_password: newPassword,
    new_password_confirm: passwordConfirm,
    })
  }

  return {
    user, accessToken, refreshToken, isAuthenticated, fullName,
    login, register, fetchProfile, updateProfile, logout,
    deactivateAccount, changePassword,
    sendVerificationCode, verifyVerificationCode,
    sendResetCode, verifyResetCode, resetPassword,
  }
})