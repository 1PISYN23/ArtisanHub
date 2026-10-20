import api from './axios'

export const shopsApi = {
  list: (params) => api.get('/shops/', { params }),
  detail: (slug) => api.get(`/shops/${slug}/`),
  create: (payload) => api.post('/shops/', payload),
  update: (slug, payload) => api.patch(`/shops/${slug}/`, payload),
  remove: (slug) => api.delete(`/shops/${slug}/`),
  myShop: () => api.get('/shops/my-shop/'),
  updateMyShop: (payload) => api.patch('/shops/my-shop/', payload)
}