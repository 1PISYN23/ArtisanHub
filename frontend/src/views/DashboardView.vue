<template>
  <main class="container page">
    <div class="row" style="margin-bottom: 28px">
      <div>
        <h1>Здравствуйте, {{ auth.user?.first_name || 'мастер' }} 👋</h1>
        <p class="muted">Это ваш личный кабинет ArtisanHub</p>
      </div>
      <RouterLink to="/profile" class="btn secondary">Настройки профиля</RouterLink>
    </div>

    <div class="grid">
      <div class="card">
        <h3>📦 Мои заказы</h3>
        <p>Здесь появятся заказы, когда модуль маркетплейса будет подключён.</p>
      </div>
      <div class="card">
        <h3>🏺 Мои изделия</h3>
        <p>Управление товарами и витриной мастерской — в разработке.</p>
      </div>
      <div class="card">
        <h3>💬 Сообщения</h3>
        <p>Переписка с покупателями и мастерами — скоро.</p>
      </div>
      <div class="card">
        <h3>⭐ Отзывы</h3>
        <p>Собирайте обратную связь от клиентов.</p>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
onMounted(() => auth.fetchProfile().catch(() => {}))
</script>