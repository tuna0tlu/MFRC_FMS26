<template>
  <DefaultHeader/>
  <div
      class="bg-gradient-to-tr from-[#460609] to-frc-red w-1/2 h-full absolute left-0 top-0 -z-30"
      v-if="!isMatchRoute"
  ></div>
  <div
      class="bg-frc-blue bg-gradient-to-tl from-[#061846] to-frc-blue w-1/2 h-full absolute right-0 top-0 -z-30"
      v-if="!isMatchRoute"
  ></div>
  <ReconnectionPopup :is-reconnecting="isReconnecting" />
  <slot></slot>
</template>

<script setup lang="ts">
import type {serverData, prematch, matchBar, postmatch, leaderboard} from '@/types';
import {useMatchStore} from '@/stores/useMatchStore';
import {navigateTo} from "#app";
import { useWebSocket } from '@/composables/useWebSocket';
import { useBackendEndpoints } from '@/composables/useBackendEndpoints';

const matchStore = useMatchStore();
const route = useRoute()
const { wsUrl } = useBackendEndpoints();
let currentRoute = ref(useRoute().path);
const normalizedRoute = computed(() => currentRoute.value.replace(/\/+$/, "") || "/");
const isMatchRoute = computed(() => normalizedRoute.value === "/match" || matchStore.currentPage === "matchbar");

const { isReconnecting, connect, disconnect } = useWebSocket();

watchEffect(() => {
  console.log("Current route path:", route.path);
  currentRoute.value = route.path;
});

onMounted(() => {
  console.log("DEFAULT ONMOUNTED");

  //Server data handler
  const handleData = (data: serverData) => {
    matchStore.setCurrentPage(data.page);
    switch (data.page) {
      case "welcome":
        navigateTo("/");
        break;
      case "prematch":
        matchStore.setPreMatch(data.data as prematch);
        navigateTo("/prematch");
        break;
      case "matchbar":
        matchStore.setMatchBar(data.data as matchBar);
        navigateTo("/match")
        break;
      case "postmatch":
        matchStore.setPostMatch(data.data as postmatch);
        navigateTo("/winner-load");
        break;
      case "leaderboard":
        matchStore.setLeaderboard(data.data as leaderboard);
        navigateTo("/leaderboard");
        break;
    }
  }

  connect(wsUrl, handleData);
});

onBeforeUnmount(() => {
  disconnect();
});
</script>
<style>
html {
  font-size: 12px; /* 1rem = 14px */
}
</style>
