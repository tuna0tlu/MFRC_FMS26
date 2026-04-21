<template>
  <div class="flex w-full h-screen justify-center">
    <div
        class="mt-8 grid grid-cols-2 w-5/6 h-min gap-y-8 justify-items-center justify-start grid-flow-col"
        :style="`grid-template-rows: repeat(${numRows}, minmax(0, 1fr));`"
    >
      <template v-for="row in numRows" :key="row">
        <TransitionGroup name="list">
          <div v-if="getTeamByRowCol(row-1, 0)"
              class="w-5/6 h-20 bg-gradient-to-br rounded-2xl flex relative items-center justify-items-center shadow-2xl transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl"
              :class="{
              'from-[#F4B61C] to-amber-600 first-place': (row-1)*2+1 === 1,
              'from-[#ffb580] to-amber-800': (row-1)*2+1 === 2,
              'from-gray-200 to-gray-700': (row-1)*2+1 === 3,
              'from-slate-700 to-slate-950': (row-1)*2+1 > 3,
              'team-card2': (row-1)*2+1 > 1,
            }"
          >
            <div
                class="flex flex-row w-3/4 p-2 h-full justify-start items-center z-10 gap-5"
                :class="{
                'text-white': (row-1)*2+1 > 3,
                'text-indigo-950': (row-1)*2+1 < 4,
              }"
            >
              <h1
                  class="ml-2 text-3xl font-extrabold"
                  :class="{
                  'text-white': (row-1)*2+1 > 3,
                  'text-indigo-950': (row-1)*2+1 < 4,
                }"
              >
                {{ (row-1)*2+1 }}.
              </h1>
              <h1
                  class="text-2xl font-semibold text-center w-full"
                  :class="{
                  'text-slate-300': (row-1)*2+1 > 3,
                  'text-indigo-950': (row-1)*2+1 < 4,
                }"
              >
                {{ getTeamByRowCol(row-1, 0).name }}
              </h1>
            </div>
            <div class=" absolute right-36 z-20 flex items-center justify-center w-min">
              <h1 class="text-white text-2xl font-light mr-4 text-right ">{{getTeamByRowCol(row-1, 0).id}}</h1>
            </div>
            <div
                class="w-32 h-16 rounded-lg bg-white/90 backdrop-blur-sm absolute right-2 flex justify-center items-center z-10 shadow-lg"
            >
              <div class="flex flex-row">
                <h2 class="text-3xl text-center">{{ getTeamByRowCol(row-1, 0).score }}</h2>
                <p class="mt-3">rp</p>
              </div>
            </div>
            <div
                class="absolute w-full h-full bg-gradient-to-br from-[#F4B61C] to-amber-600 rounded-xl z-0"
                v-if="(row-1)*2+1 === 1"
            ></div>
          </div>
        </TransitionGroup>
        <TransitionGroup name="list">
          <div v-if="getTeamByRowCol(row-1, 1)"
              class="w-5/6 h-20 bg-gradient-to-br rounded-2xl flex relative items-center justify-items-center shadow-2xl"
              :class="{
              'from-[#F4B61C] to-amber-600 first-place': (row-1)*2+2 === 1,
              'from-[#ffb580] to-amber-800': (row-1)*2+2 === 2,
              'from-gray-200 to-gray-700': (row-1)*2+2 === 3,
              'from-slate-700 to-slate-950': (row-1)*2+2 > 3,
              'team-card2': (row-1)*2+2 > 1,
            }"
          >
            <div
                class="flex flex-row w-3/4 p-2 h-full justify-start items-center z-10 gap-5"
                :class="{
                'text-white': (row-1)*2+2 > 3,
                'text-indigo-950': (row-1)*2+2 < 4,
              }"
            >
              <h1
                  class="ml-2 text-3xl font-extrabold"
                  :class="{
                  'text-white': (row-1)*2+2 > 3,
                  'text-indigo-950': (row-1)*2+2 < 4,
                }"
              >
                {{ (row-1)*2+2 }}.
              </h1>
              <h1
                  class="text-2xl font-semibold text-center w-full"
                  :class="{
                  'text-slate-300': (row-1)*2+2 > 3,
                  'text-indigo-950': (row-1)*2+2 < 4,
                }"
              >
                {{ getTeamByRowCol(row-1, 1).name }}
              </h1>
            </div>
            <div class=" absolute right-36 z-20 flex items-center justify-center w-min">
              <h1 class="text-white text-2xl font-light mr-4 text-right ">{{getTeamByRowCol(row-1, 1).id}}</h1>
            </div>
            <div
                class="w-32 h-16 rounded-lg bg-white absolute right-2 flex justify-center  items-center z-10"
            >
              <div class="flex flex-row">
                <h2 class="text-3xl text-center">{{ getTeamByRowCol(row-1, 1).score }}</h2>
                <p class="mt-3">rp</p>
              </div>
            </div>
            <div
                class="absolute w-full h-full bg-gradient-to-br from-[#F4B61C] to-amber-600 rounded-xl z-0"
                v-if="(row-1)*2+2 === 1"
            ></div>
          </div>
        </TransitionGroup>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import {useMatchStore} from "@/stores/useMatchStore";
import type {leaderboardTeam} from "@/types"
import { computed } from 'vue';

const matchStore = useMatchStore();
const leaderboardTeams = computed<leaderboardTeam[]>(() => matchStore.leaderboard.teams);

const numRows = computed(() => Math.ceil(leaderboardTeams.value.length / 2));
const getTeamByRowCol = (row: number, col: number) => {
  const idx = row * 2 + col;
  return leaderboardTeams.value[idx];
};
</script>

<style scoped>
.team-card2 {
  opacity: 0;
  animation: fade-in 1s ease forwards;
  transition: all 0.3s ease;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

.first-place {
  --border-angle: 0turn;
  --main-bg: conic-gradient(
      from var(--border-angle),
      #ed1c24,
      #ed1c24 5%,
      #3300a1 60%,
      #0066b3 95%
  );

  border: solid 5px transparent;
  --gradient-border: conic-gradient(
      from var(--border-angle),
      transparent 25%,
      #0066b3,
      #0066b3 99%,
      transparent
  );

  background: var(--main-bg) padding-box, var(--gradient-border) border-box,
  var(--main-bg) border-box;
  background-position: center center;
  animation: bg-spin 5s cubic-bezier(0.1, 0.2, 0.2, 0.1) infinite, glow 2s ease-in-out infinite alternate;
  box-shadow: 0 0 20px rgba(244, 182, 28, 0.3);
}

@keyframes glow {
  from {
    box-shadow: 0 0 20px rgba(244, 182, 28, 0.3);
  }
  to {
    box-shadow: 0 0 30px rgba(244, 182, 28, 0.6);
  }
}
</style>
