<template>
  <div
      class="flex flex-col justify-around justify-items-center items-center h-2/3 mt-20"
  >
    <div class="flex flex-row items-center justify-between w-2/3 h-5/6">
      <!-- RED ALLIANCE -->
      <div class="flex flex-col h-full justify-around">
        <template v-for="(team, keyVal) in matchStore.preMatch.redTeams">
          <TeamSignBeforeMatch
              alliance="red"
              :teamName="team.name"
              :teamNumber="'' + team.id"
          ></TeamSignBeforeMatch>
        </template>
      </div>
      <!-- RED ALLIANCE END -->
      <!-- VS TEXT -->
      <div
          class="w-20 h-20 bg-white shadow-2xl rounded-3xl flex justify-center items-center text-5xl font-extrabold vsText lg:text-7xl lg:w-40 lg:h-40"
      >
        <h1>VS</h1>
      </div>
      <!-- VS TEXT END -->
      <!-- BLUE ALLIANCE -->
      <div class="flex-col h-full justify-around flex">
        <template v-for="(team, index) in matchStore.preMatch.blueTeams">
          <TeamSignBeforeMatch
              alliance="blue"
              :teamName="team.name"
              :teamNumber="'' + team.id"
          ></TeamSignBeforeMatch>
        </template>
      </div>
      <!-- BLUE ALLIANCE END -->
    </div>
  </div>
</template>

<script setup lang="ts">
import {useMatchStore} from "@/stores/useMatchStore";

const matchStore = useMatchStore();
</script>

<style scoped>

</style>