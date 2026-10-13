<template>
  <main class="container page">
    <h1>Профиль</h1>
    <p class="muted" style="margin-bottom: 28px">Управляйте личными данными и безопасностью</p>

    <div class="stack" style="max-width: 640px">
      <!-- Personal info -->
      <div class="card">
        <h3 style="margin-bottom: 20px">Личные данные</h3>

        <div v-if="msg.info" class="alert success">{{ msg.info }}</div>
        <div v-if="msg.infoErr" class="alert error">{{ msg.infoErr }}</div>

        <form @submit.prevent="saveProfile">
          <div class="field">
            <label>Email</label>
            <input :value="form.email" disabled />
          </div>
          <div class="field">
            <label>Имя</label>
            <input v-model.trim="form.first_name" type="text" />
          </div>
          <div class="field">
            <label>Фамилия</label>
            <input v-model.trim="form.last_name" type="text" />
          </div>
          <button class="btn" type="submit" :disabled="saving">
            {{ saving ? 'Сохранение…' : 'Сохранить' }}
          </button>
        </form>
      </div>

      <!-- Change password -->
      <div class="card">
        <h3 style="margin-bottom: 20px">Смена пароля</h3>

        <div v-if="msg.pw" class="alert success">{{ msg.pw }}</div>
        <div v-if="msg.pwErr" class="alert error">{{ msg.pwErr }}</div>

        <form @submit.prevent="submitPassword">
          <div class="field">
            <label>Текущий пароль</label>
            <input v-model="pw.old_password" type="password" required />
          </div>
          <div class="field">
            <label>Новый пароль</label>
            <input v-model="pw.new_password" type="password" required minlength="8" />
          </div>
          <div class="field">
            <label>Повторите новый пароль</label>
            <input v-model="pw.confirm" type="password" required />
          </div>
          <button class="btn" type="submit" :disabled="changing">
            {{ changing ? 'Сохранение…' : 'Сменить пароль' }}
          </button>
        </form>
      </div>

      <!-- Danger zone -->
      <div class="card" style="border-color: #f3c7c7">
        <h3 style="margin-bottom: 8px; color: var(--danger)">Опасная зона</h3>
        <p class="muted" style="margin-bottom: 16px">
          Деактивация аккаунта отключит доступ к сервису. Это действие можно отменить только через поддержку.
        </p>
        <button class="btn danger" @click="confirmDeactivate = true" v-if="!confirmDeactivate">
          Деактивировать аккаунт
        </button>
        <div v-else class="stack">
          <div class="alert error">Вы уверены? Это действие немедленно завершит сессию.</div>
          <div class="row">
            <button class="btn danger" @click="deactivate" :disabled="deactivating">
              {{ deactivating ? 'Деактивация…' : 'Да, деактивировать' }}
            </button>
            <button class="btn secondary" @click="confirmDeactivate = false">Отмена</button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', first_name: '', last_name: '' })
const pw = reactive({ old_password: '', new_password: '', confirm: '' })
const msg = reactive({ info: '', infoErr: '', pw: '', pwErr: '' })

const saving = ref(false)
const changing = ref(false)
const confirmDeactivate = ref(false)
const deactivating = ref(false)

onMounted(async () => {
  try {
    const u = await auth.fetchProfile()
    form.email = u.email || ''
    form.first_name = u.first_name || ''
    form.last_name = u.last_name || ''
  } catch { /* ignore */ }
})

async function saveProfile() {
  msg.info = ''
  msg.infoErr = ''
  saving.value = true
  try {
    await auth.updateProfile({ first_name: form.first_name, last_name: form.last_name })
    msg.info = 'Профиль обновлён'
  } catch (e) {
    msg.infoErr = e.response?.data?.detail || 'Не удалось сохранить'
  } finally {
    saving.value = false
  }
}

async function submitPassword() {
  msg.pw = ''
  msg.pwErr = ''
  if (pw.new_password !== pw.confirm) {
    msg.pwErr = 'Пароли не совпадают'
    return
  }
  changing.value = true
  try {
    await auth.changePassword(pw.old_password, pw.new_password)
    msg.pw = 'Пароль успешно изменён'
    pw.old_password = pw.new_password = pw.confirm = ''
  } catch (e) {
    const d = e.response?.data
    msg.pwErr = d?.detail || d?.old_password?.[0] || 'Не удалось сменить пароль'
  } finally {
    changing.value = false
  }
}

async function deactivate() {
  deactivating.value = true
  try {
    await auth.deactivateAccount()
    router.push('/login')
  } catch (e) {
    msg.infoErr = 'Не удалось деактивировать аккаунт'
  } finally {
    deactivating.value = false
  }
}
</script>