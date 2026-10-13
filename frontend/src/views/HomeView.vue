<template>
  <main class="container page">
    <section class="hero">
      <span class="eyebrow">Ремесло · Сообщество · Мастерство</span>
      <h1>Площадка для мастеров<br />и ценителей ручной работы</h1>
      <p>
        ArtisanHub объединяет ремесленников и покупателей, которые ценят вещи,
        сделанные с душой и вниманием к деталям.
      </p>
      <div class="hero-actions">
        <RouterLink v-if="!auth.isAuthenticated" to="/register" class="btn">Создать аккаунт</RouterLink>
        <RouterLink v-else to="/dashboard" class="btn">Перейти в кабинет</RouterLink>
        <RouterLink to="/login" class="btn secondary" v-if="!auth.isAuthenticated">У меня есть аккаунт</RouterLink>
      </div>
    </section>

    <section class="grid">
      <div class="card">
        <h3>🏺 Мастерам</h3>
        <p>Витрина, история мастерской, управление заказами и прямая связь с покупателями.</p>
      </div>
      <div class="card">
        <h3>🎁 Покупателям</h3>
        <p>Уникальные изделия напрямую от авторов — керамика, текстиль, дерево, украшения.</p>
      </div>
      <div class="card">
        <h3>🤝 Сообщество</h3>
        <p>Отзывы, обмен опытом и совместные проекты внутри ремесленной среды.</p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
</script>