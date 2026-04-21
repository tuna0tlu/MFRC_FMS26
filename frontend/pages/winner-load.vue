<template>
  <div>
    <div class="flex w-full h-full ">

    <h1 class="text-9xl font-black mt-16 ml-16 text-white winner-load-anim">VE <br>KAZANAN...</h1>
    </div>

  </div>
</template>

<script lang="ts" setup>
import {navigateTo} from "#app";

onMounted(()=>{
  setTimeout(()=>{navigateTo("/postmatch");},2000)
})
</script>

<style scoped>
.winner-load-anim{
animation: winner-load 5s ease-in-out forwards;
}

@keyframes winner-load {
  0% {
    transform: translateX(-800px);
  }
  50% {
    transform: translateX(200px);
  }
  100% {
    transform: translateX(8000px);
  }
}
</style>