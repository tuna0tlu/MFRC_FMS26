<template>
  <ReconnectionPopup :is-reconnecting="isReconnecting" />
  <slot></slot>
</template>

<script setup lang="ts">
import { useMatchStore } from "@/stores/useMatchStore";
import type { matchBar, postmatch, prematch, serverData } from "~/types";
import { useWebSocket } from '@/composables/useWebSocket';
import { useBackendEndpoints } from '@/composables/useBackendEndpoints';

const matchStore = useMatchStore();
const { wsUrl } = useBackendEndpoints();
const { isReconnecting, connect, disconnect } = useWebSocket();

onMounted(() => {
  const resetMatchBar = () => {
    matchStore.setMatchBar({
      title: "",
      redTeamIDs: [],
      blueTeamIDs: [],
      redScore: "",
      blueScore: "",
      remainingTime: "",
      scoreCheckInProgress: false,
      matchbarVisible: true,
      attackerAlliance: 0,
      preStartCountdown: null,
    });
  };
  const resetPreMatch = () => {
    matchStore.setPreMatch({
      title: "",
      redTeams: [],
      blueTeams: [],
    });
  };

  const handleData = (data: serverData) => {
    matchStore.setCurrentPage(data.page);
    switch (data.page) {
      case "prematch":
        resetMatchBar();
        matchStore.setPreMatch(data.data as prematch);
        break;
      case "matchbar":
        matchStore.setMatchBar(data.data as matchBar);
        break;
      case "postmatch":
        matchStore.setPostMatch(data.data as postmatch);
        break;
      default:
        resetMatchBar();
        resetPreMatch();
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
html,
body,
#app,
.nuxt-progress {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}
</style>
