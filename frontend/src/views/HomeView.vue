<template>
  <div>
    <section class="hero">
      <div class="hero-badge">✦ Маркетплейс ручной работы</div>
      <h1>Уникальные вещи<br />от независимых мастеров</h1>
      <p class="hero-sub">
        Handmade-товары, digital-продукты и услуги — в одном месте.
        Один заказ из нескольких магазинов, один платёж, автоматическая выплата продавцам.
      </p>
      <div class="hero-actions">
        <RouterLink to="/shops" class="btn">Смотреть магазины</RouterLink>
        <RouterLink v-if="!auth.isAuthenticated" to="/register" class="btn btn-secondary">Стать продавцом</RouterLink>
        <RouterLink v-else-if="!auth.user?.has_shop" to="/my-shop" class="btn btn-secondary">Создать магазин</RouterLink>
      </div>
    </section>

    <section style="margin-bottom:60px">
      <h2>Как это работает</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <span class="feature-icon">🛍</span>
          <h3>Один заказ — много магазинов</h3>
          <p>Покупайте у разных продавцов в одном заказе. Платёж один, доставка — от каждого отдельно.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">💳</span>
          <h3>Автоматические выплаты</h3>
          <p>Stripe Connect распределяет деньги между продавцами за вычетом комиссии платформы.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">💬</span>
          <h3>Прямой чат с мастером</h3>
          <p>Задайте вопрос до покупки, обсудите детали заказа, поделитесь фото результата.</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">⭐</span>
          <h3>Честные отзывы</h3>
          <p>Только после доставленного заказа — рейтинг магазина отражает реальный опыт покупателей.</p>
        </div>
      </div>
    </section>

    <section v-if="featured.length">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px">
        <h2 style="margin:0">Популярные магазины</h2>
        <RouterLink to="/shops" class="btn btn-secondary">Все магазины →</RouterLink>
      </div>
      <div class="grid">
        <ShopCard v-for="shop in featured" :key="shop.id" :shop="shop" />
      </div>
    </section>

    <section v-else-if="loading" class="grid">
      <SkeletonCard v-for="i in 3" :key="i" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ShopCard from '../components/ShopCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import { shopsApi } from '../api/shops'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const featured = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await shopsApi.list({ ordering: '-rating_cached', page: 1 })
    featured.value = (data.results || []).slice(0, 3)
  } catch {} finally { loading.value = false }
})
</script>