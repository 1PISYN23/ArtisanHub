<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <RouterLink to="/" class="brand">ArtisanHub</RouterLink>
      <h1>С возвращением</h1>
      <p class="sub">Войдите в свой аккаунт, чтобы продолжить</p>

      <div v-if="error" class="alert error">{{ error }}</div>

      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label>Email</label>
          <input v-model.trim="email" type="email" required autocomplete="email" placeholder="you@example.com" />
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="password" type="password" required autocomplete="current-password" placeholder="••••••••" />
        </div>

        <div class="row" style="margin-bottom: 20px">
          <RouterLink to="/forgot-password" class="muted" style="font-size: .9rem">Забыли пароль?</RouterLink>
        </div>

        <button class="btn full" type="submit" :disabled="loading">
          {{ loading ? 'Вход…' : 'Войти' }}
        </button>
      </form>

      <div class="auth-footer">
        Нет аккаунта? <RouterLink to="/register">Зарегистрироваться</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    const d = e.response?.data
    error.value =
      d?.detail ||
      d?.non_field_errors?.[0] ||
      d?.message ||
      'Не удалось войти. Проверьте email и пароль.'
  } finally {
    loading.value = false
  }
}
</script>