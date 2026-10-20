<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="modal-backdrop" @click.self="$emit('cancel')">
        <div class="modal">
          <h3 class="modal-title">{{ title }}</h3>
          <p class="modal-text">{{ text }}</p>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="$emit('cancel')" :disabled="loading">Отмена</button>
            <button :class="['btn', danger ? 'btn-danger' : '']" @click="$emit('confirm')" :disabled="loading">
              {{ loading ? '...' : confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  open: Boolean,
  title: { type: String, default: 'Подтверждение' },
  text: { type: String, default: 'Вы уверены?' },
  confirmText: { type: String, default: 'Подтвердить' },
  danger: Boolean,
  loading: Boolean
})
defineEmits(['confirm', 'cancel'])
</script>