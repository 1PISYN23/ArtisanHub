<template>
  <div class="card">
    <h2>Подтверждение email</h2>
    <div v-if="auth.user?.is_email_verified" class="alert alert-success">
      ✅ Email уже подтверждён. <RouterLink to="/shops">К магазинам →</RouterLink>
    </div>
    <template v-else>
      <p class="muted" style="margin-bottom:16px">Мы отправим 6-значный код на <b>{{ auth.user?.email }}</b></p>
      <button class="btn btn-secondary btn-block" style="margin-bottom:16px"
              @click="sendCode" :disabled="sending || cooldown > 0">
        {{ cooldown > 0 ? `Повторно через ${cooldown}с` : sending ? 'Отправка...' : 'Отправить код' }}
      </button>
      <form @submit.prevent="verify" v-if="codeSent">
        <div class="form-group">
          <label>Код из письма</label>
          <input v-model.trim="code" maxlength="6" inputmode="numeric" pattern="\d{6}"
                 required placeholder="000000" class="code-input" />
        </div>
        <button class="btn btn-block" :disabled="loading || code.length !== 6">
          {{ loading ? 'Проверка...' : 'Подтвердить' }}
        </button>
      </form>
    </template>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const code = ref('')
const codeSent = ref(false)
const sending = ref(false)
const loading = ref(false)
const cooldown = ref(0)
let timer = null

function startCooldown(sec = 60) {
  cooldown.value = sec
  timer = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) clearInterval(timer)
  }, 1000)
}

async function sendCode() {
  sending.value = true
  try {
    await authApi.sendVerificationCode()
    codeSent.value = true
    toast.success('Код отправлен на email')
    startCooldown(60)
  } catch (e) {
    toast.error(e.response?.data?.error || 'Не удалось отправить код')
  } finally { sending.value = false }
}

async function verify() {
  loading.value = true
  try {
    await authApi.verifyEmail(code.value)
    await auth.fetchProfile()
    toast.success('Email подтверждён!')
  } catch (e) {
    toast.error(e.response?.data?.code?.[0] || 'Неверный код')
  } finally { loading.value = false }
}
onUnmounted(() => clearInterval(timer))
</script>