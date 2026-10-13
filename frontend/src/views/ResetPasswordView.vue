<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <RouterLink to="/" class="brand">ArtisanHub</RouterLink>
      <h1>Сброс пароля</h1>

      <div class="steps">
        <span :class="{ active: step >= 1 }" />
        <span :class="{ active: step >= 2 }" />
        <span :class="{ active: step >= 3 }" />
      </div>

      <p class="sub">
        {{ step === 1 ? 'Введите код из письма' : 'Придумайте новый пароль' }}
      </p>

      <div v-if="error" class="alert error">{{ error }}</div>

      <!-- Step 1: verify code -->
      <form v-if="step === 1" @submit.prevent="handleVerify">
        <div class="field">
          <label>Код из письма</label>
          <input v-model.trim="code" type="text" required inputmode="numeric" placeholder="123456" />
        </div>
        <button class="btn full" type="submit" :disabled="loading">
          {{ loading ? 'Проверка…' : 'Продолжить' }}
        </button>
      </form>

      <!-- Step 2: new password -->
      <form v-else @submit.prevent="handleReset">
        <div class="field">
          <label>Новый пароль</label>
          <input v-model="newPassword" type="password" required minlength="8" placeholder="Минимум 8 символов" />
        </div>
        <div class="field">
          <label>Повторите пароль</label>
          <input v-model="confirm" type="password" required placeholder="Ещё раз" />
        </div>
        <button class="btn full" type="submit" :disabled="loading">
          {{ loading ? 'Сохранение…' : 'Сбросить пароль' }}
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
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const email = route.query.email || ''
const step = ref(1)
const code = ref('')
const newPassword = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)

async function handleVerify() {
  error.value = ''
  loading.value = true
  try {
    await auth.verifyResetCode(email, code.value)
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.detail || 'Неверный код'
  } finally {
    loading.value = false
  }
}

async function handleReset() {
  error.value = ''
  if (newPassword.value !== confirm.value) {
    error.value = 'Пароли не совпадают'
    return
  }
  loading.value = true
  try {
    await auth.resetPassword(email, code.value, newPassword.value, confirm.value)
    router.push({ name: 'login', query: { reset: '1' } })
  } catch (e) {
    // Печатаем реальный ответ Django: и field-ошибки, и detail
    const d = e.response?.data
    console.error('password-reset failed:', e.response?.status, d)
    if (typeof d === 'string') {
      error.value = d
    } else if (d && typeof d === 'object') {
      error.value = Object.entries(d)
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        .join(' · ')
    } else {
      error.value = e.message || 'Не удалось сбросить пароль'
    }
  } finally {
    loading.value = false
  }
}
</script>