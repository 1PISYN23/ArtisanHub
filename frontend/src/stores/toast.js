import { defineStore } from 'pinia'
import { ref } from 'vue'

let id = 0

export const useToastStore = defineStore('toast', () => {
  const items = ref([])
  function push(message, type = 'info', timeout = 3500) {
    const t = { id: ++id, message, type }
    items.value.push(t)
    if (timeout) setTimeout(() => remove(t.id), timeout)
  }
  function remove(tid) { items.value = items.value.filter(t => t.id !== tid) }
  const success = (m) => push(m, 'success')
  const error = (m) => push(m, 'error', 5000)
  const info = (m) => push(m, 'info')
  return { items, push, remove, success, error, info }
})