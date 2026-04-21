<template>
  <div
    class="flex flex-row rounded-xl h-32 text-white shadow-2xl bg-gradient-to-br teamCard items-center justify-center"
    style="width: 32rem"
    :class="{
      'from-frc-red-light': alliance === 'red',
      'to-[#be0000]': alliance === 'red',
      'from-frc-blue-light': alliance === 'blue',
      'to-[#005698]': alliance === 'blue',
      teamCardRed: alliance === 'red',
      teamCardBlue: alliance === 'blue',
    }"
  >
    <div
      class="flex flex-col rounded-xl w-full h-full text-white shadow-2xl font-bold items-center justify-center"
    >
      <h1 class="mt-1 ml-2 text-4xl text-center font-semibold">{{ teamName }}</h1>
      <h1 class="text-4xl mt-2 ml-2 text-center font-black">{{ teamNumber }}</h1>
    </div>
    <div
      class="w-12 h-12 bg-yellow-500 rounded-2xl mr-8"
      v-for="yellowCardCount in yellowCardCount"
    ></div>
  </div>
</template>

<script setup lang="ts">
type allianceType = "red" | "blue";

const props = defineProps({
  teamName: String,
  teamNumber: String || Number,
  alliance: { type: String as () => allianceType },
  yellowCardCount: Number,
});
</script>

<style scoped>
.teamCardBlue {
  animation: teamCard 3s ease forwards;
}
.teamCardRed {
  animation: teamCardReverse 3s ease forwards;
}
@keyframes teamCard {
  0% {
    transform: translateX(200%);
  }
  100% {
    transform: translateX(0%);
  }
}
@keyframes teamCardReverse {
  0% {
    transform: translateX(-200%);
  }
  100% {
    transform: translateX(0%);
  }
}
</style>
