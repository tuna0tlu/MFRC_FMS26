<template>
  <div v-if="isReconnecting" class="fixed inset-0 z-50">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-md"></div>
    
    <!-- Popup -->
    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-float">
      <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-10 py-6 rounded-xl shadow-2xl flex items-center space-x-6 border border-white/20">
        <div class="animate-spin rounded-full h-10 w-10 border-4 border-white/80 border-t-transparent"></div>
        <span class="text-2xl font-medium tracking-wide">FMS'e bağlanılıyor...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  isReconnecting: boolean
}>()
</script>

<style scoped>
@keyframes float {
  0% {
    transform: translate(-50%, -50%) translateY(0px);
  }
  50% {
    transform: translate(-50%, -50%) translateY(-10px);
  }
  100% {
    transform: translate(-50%, -50%) translateY(0px);
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
</style> 