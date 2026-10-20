import api from './axios'

export const authApi = {
  login: (payload) => api.post('/auth/login/', payload),
  register: (payload) => api.post('/auth/register/', payload),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  profile: () => api.get('/auth/profile/'),
  updateProfile: (payload) => api.patch('/auth/profile/', payload),
  changePassword: (payload) => api.post('/auth/change-password/', payload),
  sendVerificationCode: () => api.post('/auth/send-verification-code/'),
  verifyEmail: (code) => api.post('/auth/verify-verification-code/', { code }),
  sendResetCode: (email) => api.post('/auth/send-password-reset-code/', { email }),
  verifyResetCode: (payload) => api.post('/auth/verify-password-reset-code/', payload),
  resetPassword: (payload) => api.post('/auth/password-reset/', payload),
  deactivateAccount: () => api.post('/auth/deactivate-account/')
}