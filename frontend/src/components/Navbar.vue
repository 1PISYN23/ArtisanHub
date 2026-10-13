<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <RouterLink to="/" class="logo">Artisan<span>Hub</span></RouterLink>
      <div class="nav-links">
        <template v-if="auth.isAuthenticated">
          <RouterLink to="/dashboard">Кабинет</RouterLink>
          <RouterLink to="/profile">Профиль</RouterLink>
          <button class="btn secondary" style="padding: 8px 16px; font-size: .9rem" @click="handleLogout">
            Выйти
          </button>
        </template>
        <template v-else>
          <RouterLink to="/login">Войти</RouterLink>
          <RouterLink to="/register" class="btn" style="padding: 8px 16px; font-size: .9rem">
            Регистрация
          </RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>