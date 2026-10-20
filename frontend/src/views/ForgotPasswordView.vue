<template>
  <div class="card">
    <h2>Восстановление пароля</h2>
    <div v-if="!codeSent">
      <p class="muted" style="margin-bottom:16px">Введите email — отправим код для сброса.</p>
      <form @submit.prevent="sendCode">
        <div class="form-group">
          <label>Email</label>
          <input v-model.trim="email" type="email" required autocomplete="email" />
        </div>
        <button class="btn btn-block" :disabled="loading">{{ loading ? 'Отправка...' : 'Отправить код' }}</button>
      </form>
    </div>
    <div v-else>
      <p class="muted" style="margin-bottom:16px">Код отправлен на <b>{{ email }}</b></p>
      <form @submit.prevent="verify">
        <div class="form-group">
          <label>Код из письма</label>
          <input v-model.trim="code" maxlength="6" inputmode="numeric" required class="code-input" />
        </div>
        <button class="btn btn-block" :disabled="loading || code.length !== 6">
          {{ loading ? 'Проверка...' : 'Подтвердить' }}
        </button>
      </form>
    </div>
    <p class="muted-link"><RouterLink to="/login">← Вернуться ко входу</RouterLink></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/auth'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const toast = useToastStore()
const email = ref('')
const code = ref('')
const codeSent = ref(false)
const loading = ref(false)

async function sendCode() {
  loading.value = true
  try {
    await authApi.sendResetCode(email.value)
    codeSent.value = true
    toast.success('Код отправлен')
  } catch (e) {
    toast.error(e.response?.data?.email?.[0] || e.response?.data?.error || 'Ошибка')
  } finally { loading.value = false }
}
async function verify() {
  loading.value = true
  try {
    await authApi.verifyResetCode({ email: email.value, code: code.value })
    sessionStorage.setItem('reset_email', email.value)
    toast.success('Код подтверждён')
    router.push({ name: 'reset-password' })
  } catch (e) {
    toast.error(e.response?.data?.code?.[0] || 'Неверный код')
  } finally { loading.value = false }
}
</script>