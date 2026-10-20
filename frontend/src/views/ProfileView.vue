<template>
  <div>
    <h1>Профиль</h1>
    <div class="card">
      <div class="profile-head">
        <img v-if="profile.avatar" :src="profile.avatar" class="avatar" />
        <div v-else class="avatar avatar-placeholder">👤</div>
        <div>
          <div class="profile-name">{{ profile.first_name }} {{ profile.last_name }}</div>
          <div class="muted small">{{ profile.email }}</div>
          <span :class="['badge', profile.is_email_verified ? 'badge-green' : 'badge-red']">
            {{ profile.is_email_verified ? 'Email подтверждён' : 'Email не подтверждён' }}
          </span>
        </div>
      </div>
      <div class="tabs">
        <button :class="['tab', tab === 'profile' && 'active']" @click="tab = 'profile'">Данные</button>
        <button :class="['tab', tab === 'password' && 'active']" @click="tab = 'password'">Пароль</button>
        <button :class="['tab', tab === 'danger' && 'active']" @click="tab = 'danger'">Опасная зона</button>
      </div>
      <div v-if="tab === 'profile'">
        <div v-if="!profile.is_email_verified" class="alert alert-info">
          Подтвердите email, чтобы создавать магазины.
          <RouterLink to="/verify-email">Подтвердить →</RouterLink>
        </div>
        <form @submit.prevent="updateProfile">
          <div class="form-group"><label>Имя</label><input v-model="profile.first_name" /></div>
          <div class="form-group"><label>Фамилия</label><input v-model="profile.last_name" /></div>
          <div class="form-group"><label>Телефон</label><input v-model="profile.phone" type="tel" /></div>
          <div class="form-group">
            <label>Аватар</label>
            <input type="file" accept="image/*" @change="onAvatar" />
            <img v-if="avatarPreview" :src="avatarPreview" class="preview-img" />
          </div>
          <button class="btn" :disabled="saving">{{ saving ? 'Сохранение...' : 'Сохранить' }}</button>
        </form>
      </div>
      <div v-if="tab === 'password'">
        <form @submit.prevent="changePassword">
          <div class="form-group"><label>Текущий пароль</label><PasswordInput v-model="pw.old_password" required autocomplete="current-password" /></div>
          <div class="form-group"><label>Новый пароль</label><PasswordInput v-model="pw.new_password" required autocomplete="new-password" /></div>
          <div class="form-group"><label>Подтверждение</label><PasswordInput v-model="pw.new_password_confirm" required autocomplete="new-password" /></div>
          <button class="btn" :disabled="pwSaving">{{ pwSaving ? 'Смена...' : 'Сменить пароль' }}</button>
        </form>
      </div>
      <div v-if="tab === 'danger'">
        <div class="alert alert-error">
          <b>Деактивация аккаунта</b>
          <p style="margin-top:8px">Аккаунт будет деактивирован. Восстановление только через поддержку.</p>
        </div>
        <button class="btn btn-danger" @click="showDeactivate = true">Деактивировать аккаунт</button>
      </div>
    </div>
    <ConfirmDialog :open="showDeactivate" title="Деактивировать аккаунт?"
      text="Вы выйдете из системы. Восстановление только через поддержку."
      confirm-text="Деактивировать" danger :loading="deactivating"
      @cancel="showDeactivate = false" @confirm="deactivate" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import PasswordInput from '../components/PasswordInput.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const tab = ref('profile')
const profile = reactive({})
const avatarFile = ref(null)
const avatarPreview = ref(null)
const saving = ref(false)
const pw = reactive({ old_password: '', new_password: '', new_password_confirm: '' })
const pwSaving = ref(false)
const showDeactivate = ref(false)
const deactivating = ref(false)

function onAvatar(e) {
  const f = e.target.files[0]
  avatarFile.value = f || null
  avatarPreview.value = f ? URL.createObjectURL(f) : null
}
onMounted(async () => {
  Object.assign(profile, await authApi.profile().then(r => r.data))
})
async function updateProfile() {
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('first_name', profile.first_name || '')
    fd.append('last_name', profile.last_name || '')
    fd.append('phone', profile.phone || '')
    if (avatarFile.value) fd.append('avatar', avatarFile.value)
    const { data } = await authApi.updateProfile(fd)
    Object.assign(profile, data)
    await auth.fetchProfile()
    avatarFile.value = null; avatarPreview.value = null
    toast.success('Профиль обновлён')
  } catch { toast.error('Ошибка обновления') }
  finally { saving.value = false }
}
async function changePassword() {
  if (pw.new_password !== pw.new_password_confirm) { toast.error('Пароли не совпадают'); return }
  pwSaving.value = true
  try {
    await authApi.changePassword(pw)
    pw.old_password = pw.new_password = pw.new_password_confirm = ''
    toast.success('Пароль изменён')
  } catch (e) {
    const d = e.response?.data
    toast.error(d && typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Ошибка')
  } finally { pwSaving.value = false }
}
async function deactivate() {
  deactivating.value = true
  try {
    await authApi.deactivateAccount()
    auth.logout()
    toast.info('Аккаунт деактивирован')
    router.push({ name: 'login' })
  } catch { toast.error('Не удалось деактивировать') }
  finally { deactivating.value = false }
}
</script>