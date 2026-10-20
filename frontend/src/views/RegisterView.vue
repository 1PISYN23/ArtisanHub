<template>
  <div class="card">
    <h2>Создание аккаунта</h2>
    
    <form @submit.prevent="onSubmit" novalidate>
      <div class="form-group">
        <label>Email</label>
        <input v-model.trim="form.email" type="email" required autocomplete="email" />
        <div v-if="fieldError('email')" class="error">{{ fieldError('email') }}</div>
      </div>
      <div class="row-2">
        <div class="form-group"><label>Имя</label><input v-model="form.first_name" /></div>
        <div class="form-group"><label>Фамилия</label><input v-model="form.last_name" /></div>
      </div>
      <div class="form-group"><label>Телефон</label><input v-model.trim="form.phone" type="tel" /></div>
      <div class="form-group">
        <label>Пароль</label>
        <PasswordInput v-model="form.password" required autocomplete="new-password" />
        <div class="pw-strength">
          <div class="pw-bar"><span :style="{ width: strengthPct + '%', background: strengthColor }"></span></div>
          <small>{{ strengthLabel }}</small>
        </div>
        <div v-if="fieldError('password')" class="error">{{ fieldError('password') }}</div>
      </div>
      <div class="form-group">
        <label>Подтверждение пароля</label>
        <PasswordInput v-model="form.password_confirm" required autocomplete="new-password" />
        <div v-if="fieldError('password_confirm')" class="error">{{ fieldError('password_confirm') }}</div>
      </div>
      <div class="form-group">
        <label class="checkbox">
          <input v-model="form.personal_data_consent" type="checkbox" />
          <span class="checkbox-text">Согласен с обработкой персональных данных</span>
        </label>
        <div v-if="fieldError('personal_data_consent')" class="error" style="margin-left: 32px;">
          {{ fieldError('personal_data_consent') }}
        </div>
      </div>
      
      <div class="form-group">
        <label class="checkbox">
          <input v-model="form.marketing_consent" type="checkbox" />
          <span class="checkbox-text">Хочу получать маркетинговые рассылки</span>
        </label>
      </div>

      <!-- ВОТ СЮДА ПЕРЕНЕСЛИ ОБЩУЮ ОШИБКУ -->
      <div v-if="generalError" class="alert alert-error" style="margin-top: 24px;">
        {{ generalError }}
      </div>

      <button class="btn btn-block" :disabled="loading">
        {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
    </form>
    <p class="muted-link"><RouterLink to="/login">Уже есть аккаунт? Войти</RouterLink></p>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import PasswordInput from '../components/PasswordInput.vue'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const form = reactive({
  email: '', first_name: '', last_name: '', phone: '',
  password: '', password_confirm: '',
  personal_data_consent: false, marketing_consent: false
})
const loading = ref(false)
const errors = ref({})

const generalError = computed(() => errors.value.__general || '')
function fieldError(name) {
  const v = errors.value[name]
  return Array.isArray(v) ? v[0] : (typeof v === 'string' ? v : '')
}
const strengthPct = computed(() => {
  const p = form.password || ''
  let s = 0
  if (p.length >= 8) s += 30
  if (/[A-Z]/.test(p)) s += 20
  if (/[a-z]/.test(p)) s += 15
  if (/\d/.test(p)) s += 15
  if (/[^A-Za-z0-9]/.test(p)) s += 20
  return Math.min(s, 100)
})
const strengthLabel = computed(() => strengthPct.value < 40 ? 'Слабый' : strengthPct.value < 70 ? 'Средний' : 'Надёжный')
const strengthColor = computed(() => strengthPct.value < 40 ? '#ef4444' : strengthPct.value < 70 ? '#f59e0b' : '#10b981')

async function onSubmit() {
  errors.value = {}
  loading.value = true
  try {
    await auth.register(form)
    toast.success('Аккаунт создан!')
    router.push({ name: 'verify-email' })
  } catch (e) {
    const d = e.response?.data
    if (d && typeof d === 'object') {
      errors.value = d
      if (!d.email && !d.password && !d.password_confirm && !d.personal_data_consent) {
        errors.value.__general = Object.values(d).flat().join(' ')
      }
    } else {
      errors.value.__general = 'Ошибка регистрации'
    }
  } finally { loading.value = false }
}
</script>