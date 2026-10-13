<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <RouterLink to="/" class="brand">ArtisanHub</RouterLink>
      <h1>Создать аккаунт</h1>
      <p class="sub">Присоединяйтесь к сообществу мастеров</p>

      <div v-if="error" class="alert error">{{ error }}</div>
      <div v-if="success" class="alert success">{{ success }}</div>

      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label>Имя</label>
          <input v-model.trim="form.first_name" type="text" autocomplete="given-name" placeholder="Иван" />
        </div>
        <div class="field">
          <label>Фамилия</label>
          <input v-model.trim="form.last_name" type="text" autocomplete="family-name" placeholder="Иванов" />
        </div>
        <div class="field">
          <label>Email</label>
          <input v-model.trim="form.email" type="email" required autocomplete="email" placeholder="you@example.com" />
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="form.password" type="password" required autocomplete="new-password" minlength="8" placeholder="Минимум 8 символов" />
        </div>
        <div class="field">
          <label>Повторите пароль</label>
          <input v-model="form.password2" type="password" required autocomplete="new-password" placeholder="Ещё раз" />
        </div>

        <button class="btn full" type="submit" :disabled="loading">
          {{ loading ? 'Создание…' : 'Зарегистрироваться' }}
        </button>
      </form>

      <div class="auth-footer">
        Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const form = reactive({ first_name: '', last_name: '', email: '', password: '', password2: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function handleSubmit() {
  error.value = ''
  success.value = ''
  if (form.password !== form.password2) {
    error.value = 'Пароли не совпадают'
    return
  }
  loading.value = true
  try {
    await auth.register({
      email: form.email,
      password: form.password,
      password_confirm: form.password2,   // ← вот тут была ошибка: отправляем password_confirm
      first_name: form.first_name,
      last_name: form.last_name,
    })
    await auth.login(form.email, form.password)
    router.push({ name: 'verify-email', query: { email: form.email } })
  } catch (e) {
    error.value = formatError(e, 'Не удалось зарегистрироваться')
  } finally {
    loading.value = false
  }
}

function formatError(e, fallback) {
  const d = e.response?.data
  if (!d) return e.message || fallback
  if (typeof d === 'string') return d
  if (typeof d === 'object') {
    return Object.entries(d)
      .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
      .join(' · ')
  }
  return fallback
}
</script>