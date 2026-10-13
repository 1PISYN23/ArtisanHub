<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <RouterLink to="/" class="brand">ArtisanHub</RouterLink>
      <h1>Подтвердите email</h1>
      <p class="sub">
        Мы отправили код на <strong>{{ email || 'ваш email' }}</strong>.
        Введите его ниже.
      </p>

      <div v-if="error" class="alert error">{{ error }}</div>
      <div v-if="info" class="alert info">{{ info }}</div>
      <div v-if="success" class="alert success">{{ success }}</div>

      <form @submit.prevent="handleVerify">
        <div class="field" v-if="!email">
          <label>Email</label>
          <input v-model.trim="emailInput" type="email" required placeholder="you@example.com" />
        </div>

        <div class="field">
          <label>Код подтверждения</label>
          <input v-model.trim="code" type="text" required placeholder="123456" inputmode="numeric" />
        </div>

        <button class="btn full" type="submit" :disabled="loading">
          {{ loading ? 'Проверка…' : 'Подтвердить' }}
        </button>
      </form>

      <div class="auth-footer">
        <a href="#" @click.prevent="resend" :class="{ muted: resending }">
          {{ resending ? 'Отправка…' : 'Отправить код повторно' }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const emailFromQuery = route.query.email || auth.user?.email || ''
const emailInput = ref('')
const email = computed(() => emailFromQuery || emailInput.value)
const code = ref('')
const error = ref('')
const info = ref('')
const success = ref('')
const loading = ref(false)
const resending = ref(false)

onMounted(async () => {
  if (emailFromQuery && !code.value) {
    await resend()
  }
})

async function resend() {
  if (!email.value) return
  resending.value = true
  error.value = ''
  info.value = ''
  try {
    await auth.sendVerificationCode(email.value)
    info.value = 'Код отправлен. Проверьте почту.'
  } catch (e) {
    error.value = 'Не удалось отправить код'
  } finally {
    resending.value = false
  }
}

async function handleVerify() {
  error.value = ''
  info.value = ''
  loading.value = true
  try {
    await auth.verifyVerificationCode(email.value, code.value)
    success.value = 'Email подтверждён! Перенаправляем…'
    setTimeout(() => router.push('/dashboard'), 900)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Неверный код'
  } finally {
    loading.value = false
  }
}
</script>