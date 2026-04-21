<template>
  <button
    class="rounded-2xl"
    :class="{
      'bg-frc-blue-light': alliance === 'blue',
      'hover:bg-frc-blue': alliance === 'blue',
      'bg-frc-red-light': alliance === 'red',
      'hover:bg-frc-red': alliance === 'red',
      'w-64 h-32': size === 'large',
      'w-48 h-16': size === 'medium',
      'w-32 h-16': size === 'small',
      'text-4xl': size === 'large',
      'text-3xl': size === 'medium',
      'text-2xl': size === 'small',
      'bg-yellow-600': priority === 2 && !alliance,
      'hover:bg-yellow-700': priority === 2 && !alliance,
      'bg-red-800': priority === 1 && !alliance,
      'hover:bg-red-900': priority === 1 && !alliance,
      'text-white': textColor === 'white',
      'text-black': textColor === 'black',
    }"
    @click="$emit('clickFunction')"
  >
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
type allianceType = "red" | "blue" | null;
type sizeType = "small" | "medium" | "large";
type priorityType = 0 | 1 | 2 | 3 | 4 | 5;
type textColorType = "white" | "black";

const props = defineProps({
  alliance: { type: String as () => allianceType },
  size: { type: String as () => sizeType, default: "large" },
  priority: { type: Number, default: 0 },
  textColor: { type: String as () => textColorType, default: "white" },
});
</script>

<style scoped></style>
