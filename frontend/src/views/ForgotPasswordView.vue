<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <RouterLink to="/" class="brand">ArtisanHub</RouterLink>
      <h1>Забыли пароль?</h1>
      <p class="sub">Укажите email — мы отправим код для сброса пароля</p>

      <div v-if="error" class="alert error">{{ error }}</div>

      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label>Email</label>
          <input v-model.trim="email" type="email" required placeholder="you@example.com" />
        </div>
        <button class="btn full" type="submit" :disabled="loading">
          {{ loading ? 'Отправка…' : 'Отправить код' }}
        </button>
      </form>

      <div class="auth-footer">
        <RouterLink to="/login">← Назад ко входу</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const error = ref('')
const loading = ref(false)
const auth = useAuthStore()
const router = useRouter()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.sendResetCode(email.value)
    router.push({ name: 'reset-password', query: { email: email.value } })
  } catch (e) {
    error.value = 'Не удалось отправить код. Проверьте email.'
  } finally {
    loading.value = false
  }
}
</script>