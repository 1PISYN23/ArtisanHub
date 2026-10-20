<template>
  <div class="pw-wrap">
    <input :type="visible ? 'text' : 'password'" :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder" :autocomplete="autocomplete" :required="required"
      class="pw-input" />
    <button type="button" class="pw-toggle" @click="visible = !visible" tabindex="-1">
      {{ visible ? '🙈' : '👁' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineProps({ modelValue: String, placeholder: String, autocomplete: String, required: Boolean })
defineEmits(['update:modelValue'])
const visible = ref(false)
</script>