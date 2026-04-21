<template>
  <div
    class="rounded-lg flex items-center justify-center flex-col"
  >
    <input
      :id="modelId"
      type="checkbox"
      class="w-full h-0 text-blue-500 rounded appearance-none"
      v-model="modelValue"
    />
    <label
      :for="modelId"
      class="text-2xl font-extrabold text-center h-full w-full items-center justify-center flex"
      ><slot></slot
    ></label>
  </div>
</template>

<script setup lang="ts">
const modelValue = defineModel();
const props = defineProps({
  modelId: String,
});
</script>

<style scoped></style>
