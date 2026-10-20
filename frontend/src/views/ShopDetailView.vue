<template>
  <div v-if="loading" class="card" style="max-width:860px">
    <div class="skeleton" style="height:280px; margin-bottom:16px; border-radius:8px"></div>
    <div class="skeleton skeleton-line" style="width:60%"></div>
    <div class="skeleton skeleton-line" style="width:90%"></div>
  </div>
  <div v-else-if="error" class="empty-state">
    <div class="empty-icon">😕</div>
    <h3>{{ error }}</h3>
    <RouterLink to="/shops" class="btn">К магазинам</RouterLink>
  </div>
  <div v-else-if="shop" class="shop-detail">
    <div class="shop-detail-hero">
      <img v-if="shop.logo" :src="shop.logo" :alt="shop.name" />
      <div v-else class="placeholder-lg">{{ shop.name[0] }}</div>
    </div>
    <div class="shop-detail-body">
      <div class="shop-detail-head">
        <h1>{{ shop.name }}</h1>
        <div class="shop-stats">
          <div class="stat">
            <b>⭐ {{ shop.rating_cached }}</b>
            <small>рейтинг</small>
          </div>
          <div class="stat">
            <b>{{ shop.reviews_count_cached }}</b>
            <small>отзывов</small>
          </div>
        </div>
      </div>
      <p class="shop-desc">{{ shop.description || 'Описание не заполнено.' }}</p>
      <div class="muted small" style="margin-bottom:20px">
        Создан: {{ formatDate(shop.created_at) }}
      </div>
      <div class="shop-actions">
        <RouterLink to="/catalog" class="btn">Товары магазина (скоро)</RouterLink>
        <RouterLink v-if="auth.isAuthenticated" to="/chat" class="btn btn-secondary">Написать продавцу</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { shopsApi } from '../api/shops'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()
const shop = ref(null)
const loading = ref(true)
const error = ref('')

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'
}

onMounted(async () => {
  try {
    const { data } = await shopsApi.detail(route.params.slug)
    shop.value = data
  } catch { error.value = 'Магазин не найден или неактивен' }
  finally { loading.value = false }
})
</script>