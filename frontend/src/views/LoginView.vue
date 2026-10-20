<template>
  <div class="card">
    <h2>Вход в аккаунт</h2>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <form @submit.prevent="onSubmit" novalidate>
      <div class="form-group">
        <label>Email</label>
        <input v-model.trim="form.email" type="email" required autocomplete="email" placeholder="you@example.com" />
      </div>
      <div class="form-group">
        <label>Пароль</label>
        <PasswordInput v-model="form.password" required autocomplete="current-password" />
      </div>
      <button class="btn btn-block" :disabled="loading">{{ loading ? 'Вход...' : 'Войти' }}</button>
    </form>
    <p class="muted-link">
      <RouterLink to="/forgot-password">Забыли пароль?</RouterLink>
      <span> · </span>
      <RouterLink to="/register">Регистрация</RouterLink>
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import PasswordInput from '../components/PasswordInput.vue'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const route = useRoute()
const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form)
    toast.success('Добро пожаловать!')
    router.push(route.query.redirect || { name: 'shops' })
  } catch (e) {
    const d = e.response?.data
    if (Array.isArray(d?.non_field_errors)) error.value = d.non_field_errors[0]
    else if (typeof d?.detail === 'string') error.value = d.detail
    else if (d && typeof d === 'object') error.value = Object.values(d).flat().join(' ')
    else error.value = 'Не удалось войти. Проверьте соединение с сервером.'
  } finally { loading.value = false }
}
</script>