<template>
  <div class="card">
    <h2>Новый пароль</h2>
    <form @submit.prevent="submit">
      <div class="form-group"><label>Email</label><input v-model.trim="email" type="email" required /></div>
      <div class="form-group">
        <label>Новый пароль</label>
        <PasswordInput v-model="new_password" required autocomplete="new-password" />
      </div>
      <div class="form-group">
        <label>Подтверждение</label>
        <PasswordInput v-model="new_password_confirm" required autocomplete="new-password" />
      </div>
      <button class="btn btn-block" :disabled="loading">{{ loading ? 'Сохранение...' : 'Сменить пароль' }}</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import PasswordInput from '../components/PasswordInput.vue'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const email = ref(sessionStorage.getItem('reset_email') || '')
const new_password = ref('')
const new_password_confirm = ref('')
const loading = ref(false)

async function submit() {
  if (new_password.value !== new_password_confirm.value) {
    toast.error('Пароли не совпадают'); return
  }
  loading.value = true
  try {
    const { data } = await authApi.resetPassword({
      email: email.value,
      new_password: new_password.value,
      new_password_confirm: new_password_confirm.value
    })
    localStorage.setItem('access', data.tokens.access)
    localStorage.setItem('refresh', data.tokens.refresh)
    await auth.fetchProfile()
    sessionStorage.removeItem('reset_email')
    toast.success('Пароль изменён — вы вошли')
    router.push({ name: 'shops' })
  } catch (e) {
    const d = e.response?.data
    toast.error(d && typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Ошибка')
  } finally { loading.value = false }
}
</script>