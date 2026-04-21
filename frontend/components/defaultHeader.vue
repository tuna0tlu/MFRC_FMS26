<template>
  <div
    class="w-screen h-20 relative flex justify-center items-center justify-items-center z-50"
  >
    <div class="w-full h-20 absolute shadow-xl bg-black"></div>
    <NuxtImg
      src="/navbar-right.svg"
      alt="Logo background"
      class="h-48 absolute right-0 top-0"
      v-if="!isMatchHeader"
    />
    <NuxtImg
      src="/logo-color.svg"
      alt="Logo"
      class="absolute right-8 top-2 w-36"
      v-if="!isMatchHeader"
    />
    <h1
      class="header-title z-10 text-4xl tracking-widest text-white"
    >
      {{ headingText }}
    </h1>
  </div>
</template>
<script setup lang="ts">
import { useMatchStore } from "@/stores/useMatchStore";
const route = useRoute();
let currentRoute = ref(route.path);
const matchStore = useMatchStore();
const normalizedRoute = computed(() => currentRoute.value.replace(/\/+$/, "") || "/");
const isMatchRoute = computed(() => normalizedRoute.value === "/match");
const isMatchHeader = computed(() => isMatchRoute.value || matchStore.currentPage === "matchbar");

// make the heading text reactive
const headingTextFunc = () => {
  switch (normalizedRoute.value) {
    case "/counting":
      return "MAÇ SONUCU YÜKLENİYOR...";
    case "/":
      return "MFRC`26 | COSMOS ROBOT WORKS";
    case "/scores":
      return "SKOR TABLOSU";
    case "/postmatch":
      return matchStore.postMatch.title;
    case "/driverred":
      return "KIRMIZI İTTİFAK SÜRÜCÜ EKRANI";
    case "/driverblue":
      return "MAVİ İTTİFAK SÜRÜCÜ EKRANI";
    case "/bottombar":
      return "MFRC`26 | COSMOS ROBOT WORKS";
    case "/scoresshow":
      return "SKOR TABLOSU";
    case "/match":
      if(!matchStore.matchBar.matchbarVisible)
        return "";
      return matchStore.matchBar.title;
    case "/prematch":
      return matchStore.preMatch.title;
    default:
      return normalizedRoute.value.substring(1).toUpperCase();
  }
};

const headingText = ref(headingTextFunc());

watchEffect(() => {
  currentRoute.value = route.path;
  matchStore.matchBar.matchbarVisible
  headingText.value = headingTextFunc();
});
</script>

<style scoped>
.header-title {
  font-family: "Cosima", "Cosmima", "Inter", sans-serif;
  font-weight: 700;
}
</style>
