<template>
  <div>
    <h1>Мой магазин</h1>

    <div v-if="state === 'create'" class="card">
      <h2>Создать магазин</h2>
      <form @submit.prevent="create">
        <div class="form-group"><label>Название</label><input v-model.trim="form.name" required maxlength="64" /></div>
        <div class="form-group">
          <label>Описание</label>
          <textarea v-model="form.description" maxlength="528" rows="4" />
          <small class="muted">{{ form.description.length }}/528</small>
        </div>
        <div class="form-group">
          <label>Логотип</label>
          <input type="file" accept="image/*" @change="onFile" />
          <img v-if="preview" :src="preview" class="preview-img" />
        </div>
        <button class="btn btn-block" :disabled="saving">{{ saving ? 'Создание...' : 'Создать магазин' }}</button>
      </form>
    </div>

    <div v-else-if="state === 'view' && shop" class="card shop-view-card">
      <img v-if="shop.logo" :src="shop.logo" class="preview-img-lg" />
      <div v-else class="placeholder-lg">{{ shop.name[0] }}</div>
      <div class="shop-view-body">
        <div class="shop-view-head">
          <div>
            <h2>{{ shop.name }}</h2>
          </div>
          <span :class="['badge', shop.stripe_onboarding_complete ? 'badge-green' : 'badge-red']">
            {{ shop.stripe_onboarding_complete ? 'Stripe активен' : 'Stripe не подключён' }}
          </span>
        </div>
        <p>{{ shop.description || 'Без описания' }}</p>
        <div class="shop-stats">
          <div class="stat"><b>⭐ {{ shop.rating_cached }}</b><small>рейтинг</small></div>
          <div class="stat"><b>{{ shop.reviews_count_cached }}</b><small>отзывов</small></div>
        </div>
        <div class="shop-actions">
          <button class="btn" @click="state = 'edit'">Редактировать</button>
          <RouterLink :to="`/shops/${shop.slug}`" class="btn btn-secondary">Открыть публично</RouterLink>
          <button class="btn btn-danger" @click="showDelete = true">Деактивировать</button>
        </div>
      </div>
    </div>

    <div v-else-if="state === 'edit'" class="card">
      <h2>Редактирование</h2>
      <form @submit.prevent="save">
        <div class="form-group"><label>Название</label><input v-model.trim="form.name" required maxlength="64" /></div>
        <div class="form-group"><label>Описание</label><textarea v-model="form.description" maxlength="528" rows="4" /></div>
        <div class="form-group">
          <label>Логотип</label>
          <input type="file" accept="image/*" @change="onFile" />
          <img v-if="preview" :src="preview" class="preview-img" />
        </div>
        <div class="form-actions">
          <button class="btn" :disabled="saving">{{ saving ? 'Сохранение...' : 'Сохранить' }}</button>
          <button type="button" class="btn btn-secondary" @click="cancelEdit">Отмена</button>
        </div>
      </form>
    </div>

    <ConfirmDialog :open="showDelete" title="Деактивировать магазин?"
      text="Магазин перестанет быть виден покупателям. Данные не удаляются."
      confirm-text="Деактивировать" danger :loading="deleting"
      @cancel="showDelete = false" @confirm="removeShop" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { shopsApi } from '../api/shops'
import { useToastStore } from '../stores/toast'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const toast = useToastStore()
const state = ref('loading')
const shop = ref(null)
const form = reactive({ name: '', description: '' })
const logoFile = ref(null)
const preview = ref(null)
const saving = ref(false)
const showDelete = ref(false)
const deleting = ref(false)

function onFile(e) {
  const f = e.target.files[0]
  logoFile.value = f || null
  preview.value = f ? URL.createObjectURL(f) : null
}
function buildFormData() {
  const fd = new FormData()
  fd.append('name', form.name)
  fd.append('description', form.description)
  if (logoFile.value) fd.append('logo', logoFile.value)
  return fd
}
async function load() {
  try {
    const { data } = await shopsApi.myShop()
    shop.value = data
    form.name = data.name
    form.description = data.description
    state.value = 'view'
  } catch { state.value = 'create' }
}
async function create() {
  saving.value = true
  try {
    await shopsApi.create(buildFormData())
    toast.success('Магазин создан!')
    logoFile.value = null; preview.value = null
    await load()
  } catch (e) {
    const d = e.response?.data
    toast.error(d && typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Ошибка создания')
  } finally { saving.value = false }
}
async function save() {
  saving.value = true
  try {
    await shopsApi.updateMyShop(buildFormData())
    toast.success('Сохранено')
    logoFile.value = null; preview.value = null
    await load()
  } catch { toast.error('Ошибка сохранения') }
  finally { saving.value = false }
}
function cancelEdit() {
  form.name = shop.value.name
  form.description = shop.value.description
  logoFile.value = null; preview.value = null
  state.value = 'view'
}
async function removeShop() {
  deleting.value = true
  try {
    await shopsApi.remove(shop.value.slug)
    toast.success('Магазин деактивирован')
    showDelete.value = false
    shop.value = null
    state.value = 'create'
    form.name = ''; form.description = ''
  } catch { toast.error('Не удалось удалить') }
  finally { deleting.value = false }
}
onMounted(load)
</script>