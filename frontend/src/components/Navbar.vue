<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <RouterLink to="/" class="navbar-brand">
        <span class="navbar-brand-mark">✦</span>
        <span class="navbar-brand-text">ArtisanHub</span>
      </RouterLink>

      <div class="navbar-center">
        <RouterLink to="/catalog" class="navbar-link">Каталог</RouterLink>
        <RouterLink to="/shops" class="navbar-link">Магазины</RouterLink>
        <RouterLink v-if="auth.isAuthenticated" to="/orders" class="navbar-link">Заказы</RouterLink>
      </div>

      <div class="navbar-right">
        <template v-if="auth.isAuthenticated">
          <RouterLink to="/favorites" class="icon-btn" aria-label="Избранное">♥</RouterLink>
          <RouterLink to="/cart" class="icon-btn" aria-label="Корзина">🛒</RouterLink>

          <div class="user-menu" ref="userMenuRef">
            <button class="user-menu-trigger" @click="menuOpen = !menuOpen">
              <img v-if="auth.user?.avatar" :src="auth.user.avatar" class="user-menu-avatar" />
              <span v-else class="user-menu-avatar user-menu-avatar-text">{{ initials }}</span>
              <span class="user-menu-name">{{ shortName }}</span>
              <span class="user-menu-chevron" :class="{ open: menuOpen }">▾</span>
            </button>

            <Transition name="dropdown">
              <div v-if="menuOpen" class="user-menu-dropdown">
                <RouterLink to="/profile" class="user-menu-item" @click="menuOpen = false">
                  <span>👤</span> Профиль
                </RouterLink>
                <RouterLink to="/my-shop" class="user-menu-item" @click="menuOpen = false">
                  <span>🏪</span> Мой магазин
                </RouterLink>
                <RouterLink to="/chat" class="user-menu-item" @click="menuOpen = false">
                  <span>💬</span> Сообщения
                </RouterLink>
                <RouterLink to="/notifications" class="user-menu-item" @click="menuOpen = false">
                  <span>🔔</span> Уведомления
                </RouterLink>
                <div class="user-menu-divider"></div>
                <button class="user-menu-item user-menu-item-danger" @click="onLogout">
                  <span>⏻</span> Выйти
                </button>
              </div>
            </Transition>
          </div>
        </template>
        <template v-else>
          <RouterLink to="/login" class="navbar-link">Вход</RouterLink>
          <RouterLink to="/register" class="btn">Регистрация</RouterLink>
        </template>
      </div>

      <button class="nav-burger" @click="open = !open" aria-label="Меню">☰</button>
    </div>

    <div v-if="open" class="nav-mobile" @click="open = false">
      <RouterLink to="/">Главная</RouterLink>
      <RouterLink to="/catalog">Каталог</RouterLink>
      <RouterLink to="/shops">Магазины</RouterLink>
      <template v-if="auth.isAuthenticated">
        <RouterLink to="/my-shop">Мой магазин</RouterLink>
        <RouterLink to="/favorites">Избранное</RouterLink>
        <RouterLink to="/cart">Корзина</RouterLink>
        <RouterLink to="/orders">Заказы</RouterLink>
        <RouterLink to="/chat">Чат</RouterLink>
        <RouterLink to="/notifications">Уведомления</RouterLink>
        <RouterLink to="/profile">Профиль</RouterLink>
        <button @click.stop="onLogout">Выйти</button>
      </template>
      <template v-else>
        <RouterLink to="/login">Вход</RouterLink>
        <RouterLink to="/register">Регистрация</RouterLink>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const router = useRouter()
const toast = useToastStore()
const open = ref(false)
const menuOpen = ref(false)
const userMenuRef = ref(null)

const shortName = computed(() => {
  const u = auth.user
  if (!u) return 'Профиль'
  return u.first_name || u.email?.split('@')[0] || 'Профиль'
})

const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  const a = (u.first_name?.[0] || '') + (u.last_name?.[0] || '')
  return a.toUpperCase() || (u.email?.[0] || '?').toUpperCase()
})

async function onLogout() {
  menuOpen.value = false
  try { await authApi.logout(auth.refresh) } catch {}
  auth.logout()
  toast.info('Вы вышли из системы')
  router.push({ name: 'login' })
}

function onClickOutside(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    menuOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>