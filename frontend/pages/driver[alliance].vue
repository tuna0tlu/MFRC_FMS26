<template>
  <div class="min-h-screen w-full text-white relative overflow-hidden bg-black">
    <div class="absolute inset-y-0 left-0 w-1/2 bg-gradient-to-tr from-[#460609] to-frc-red pointer-events-none" />
    <div class="absolute inset-y-0 right-0 w-1/2 bg-gradient-to-tl from-[#061846] to-frc-blue pointer-events-none" />
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.14),transparent_55%)] pointer-events-none" />
    <div class="absolute inset-0 bg-black/15 pointer-events-none" />

    <div v-if="wrongAlliance" class="h-screen flex items-center justify-center px-8 relative z-10">
      <div class="max-w-4xl w-full bg-black/70 border border-red-500 rounded-3xl p-10 text-center shadow-2xl">
        <h1 class="text-6xl md:text-7xl font-black text-red-300 tracking-wide">WRONG ALLIANCE</h1>
        <p class="text-3xl md:text-4xl font-bold text-white mt-6">
          URL sadece <span class="font-mono">/driver/red</span> veya <span class="font-mono">/driver/blue</span> olmalı.
        </p>
      </div>
    </div>

    <div v-else-if="isPrematchInfo" class="h-screen flex items-center justify-center px-6 relative z-10">
      <div class="max-w-6xl w-full bg-black/70 border border-slate-300/60 rounded-3xl p-8 md:p-10 shadow-2xl">
        <h1 class="text-5xl md:text-6xl font-black text-center">{{ matchStore.preMatch.title }}</h1>
        <p class="text-2xl text-center text-slate-200 mt-3">
          Driver Station: {{ ownAllianceLabel }}
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-8">
          <div class="rounded-2xl p-5" :class="ownAlliance === 'red' ? 'bg-red-700/55 ring-2 ring-red-300/80' : 'bg-blue-700/55 ring-2 ring-blue-300/80'">
            <p class="text-2xl font-black mb-3">SENİN İTTİFAKIN</p>
            <div class="space-y-2">
              <div
                v-for="team in ownPrematchTeams"
                :key="`own-${team.id}`"
                class="bg-black/30 rounded-lg px-3 py-2 text-xl font-bold"
              >
                {{ team.id }} - {{ team.name }}
              </div>
            </div>
          </div>

          <div class="rounded-2xl p-5" :class="ownAlliance === 'red' ? 'bg-blue-700/50' : 'bg-red-700/50'">
            <p class="text-2xl font-black mb-3">RAKİP İTTİFAK</p>
            <div class="space-y-2">
              <div
                v-for="team in opponentPrematchTeams"
                :key="`opp-${team.id}`"
                class="bg-black/30 rounded-lg px-3 py-2 text-xl font-bold"
              >
                {{ team.id }} - {{ team.name }}
              </div>
            </div>
          </div>
        </div>

        <p class="text-center text-2xl mt-7 text-amber-200 font-semibold">
          Maç başlatılınca bu ekran canlı skora otomatik geçecek.
        </p>
      </div>
    </div>

    <div v-else-if="!hasLiveMatch" class="h-screen flex items-center justify-center px-8 relative z-10">
      <div class="max-w-4xl w-full bg-black/70 border border-slate-300/60 rounded-3xl p-10 text-center shadow-2xl">
        <h1 class="text-6xl md:text-7xl font-black tracking-wide">MAÇ YOK</h1>
        <p class="text-2xl md:text-3xl text-slate-200 mt-6">Maç Bekleniyor...</p>
      </div>
    </div>

    <div v-else class="h-screen flex flex-col px-4 md:px-8 py-4 md:py-6 gap-4 md:gap-6 relative z-10">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-3 md:gap-4">
        <div
          class="bg-black/45 border border-white/25 rounded-2xl p-4 backdrop-blur-sm shadow-xl"
          :class="ownAlliance === 'red' ? 'ring-2 ring-red-300/50' : 'ring-2 ring-blue-300/50'"
        >
          <p class="text-sm uppercase tracking-wider text-slate-200">Driver Tablet</p>
          <p class="text-3xl font-black mt-1">{{ ownAllianceLabel }}</p>
          <p class="text-lg mt-1" :class="ownRoleClass">{{ ownRoleText }}</p>
          <p class="text-base mt-1 text-slate-200">{{ matchStore.matchBar.title }}</p>
        </div>

        <div class="bg-black/45 border border-white/25 rounded-2xl p-4 text-center backdrop-blur-sm shadow-xl">
          <p class="text-sm uppercase tracking-wider text-slate-200">Match Phase</p>
          <p class="text-3xl font-black mt-1" :class="phasePillClass">{{ phasePillText }}</p>
          <p class="text-lg mt-1 text-slate-100">Alliance: {{ activeAllianceText }}</p>
        </div>

        <div class="bg-[#231E1F]/90 border border-white/25 rounded-2xl p-4 text-center shadow-xl">
          <p class="text-sm uppercase tracking-wider text-slate-200">Remaining Time</p>
          <p class="text-6xl md:text-7xl font-black leading-none mt-2">{{ matchStore.matchBar.remainingTime }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 md:gap-6 flex-1">
        <section class="rounded-3xl border-2 border-red-200/50 bg-gradient-to-br from-frc-red-light via-frc-red-mid to-frc-red-dark p-5 md:p-7 flex flex-col shadow-[0_14px_45px_rgba(236,29,37,0.35)]">
          <div class="flex items-start justify-between gap-4">
            <h2 class="text-4xl md:text-5xl font-black">KIRMIZI</h2>
          </div>
          <p class="text-8xl md:text-9xl font-black leading-none mt-2">{{ matchStore.matchBar.redScore }}</p>
          <div class="h-12 mt-3 flex items-center justify-center">
            <div
              v-if="showRedSwitchIcon"
              class="rounded-md bg-[#f6e327] border-2 border-black/40 p-1.5 shadow-lg"
            >
              <img src="/switch_red.png" alt="Red can score" class="w-10 h-10 md:w-12 md:h-12 object-contain" />
            </div>
          </div>
          <div class="mt-5">
            <p class="text-base uppercase tracking-wide text-red-100">Teams</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="team in matchStore.matchBar.redTeamIDs"
                :key="`red-${team}`"
                class="px-3 py-1 rounded-lg bg-white/20 border border-white/30 text-xl font-bold"
              >
                {{ team }}
              </span>
            </div>
          </div>
        </section>

        <section class="rounded-3xl border-2 border-blue-200/50 bg-gradient-to-br from-frc-blue-light via-frc-blue-mid to-frc-blue-dark p-5 md:p-7 flex flex-col shadow-[0_14px_45px_rgba(0,102,179,0.35)]">
          <div class="flex items-start justify-between gap-4">
            <h2 class="text-4xl md:text-5xl font-black">MAVİ</h2>
          </div>
          <p class="text-8xl md:text-9xl font-black leading-none mt-2">{{ matchStore.matchBar.blueScore }}</p>
          <div class="h-12 mt-3 flex items-center justify-center">
            <div
              v-if="showBlueSwitchIcon"
              class="rounded-md bg-[#f6e327] border-2 border-black/40 p-1.5 shadow-lg"
            >
              <img src="/switch_blue.png" alt="Blue can score" class="w-10 h-10 md:w-12 md:h-12 object-contain" />
            </div>
          </div>
          <div class="mt-5">
            <p class="text-base uppercase tracking-wide text-blue-100">Teams</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="team in matchStore.matchBar.blueTeamIDs"
                :key="`blue-${team}`"
                class="px-3 py-1 rounded-lg bg-white/20 border border-white/30 text-xl font-bold"
              >
                {{ team }}
              </span>
            </div>
          </div>
        </section>
      </div>

      <div class="bg-black/50 border border-white/25 rounded-2xl px-5 py-3 text-center shadow-lg backdrop-blur-sm">
        <p class="text-xl md:text-2xl font-bold">
          Alliance Shift: <span class="font-black">{{ activeAllianceText }}</span>
        </p>
      </div>

      <transition name="shift-pop">
        <div v-if="showShiftAnnouncement" class="absolute inset-x-0 top-4 flex justify-center pointer-events-none">
          <div class="bg-black/85 border border-yellow-300 rounded-2xl px-8 py-4 shadow-2xl">
            <p class="text-yellow-200 text-3xl md:text-4xl font-black">{{ shiftAnnouncement }}</p>
          </div>
        </div>
      </transition>

      <div
        v-if="isCountdownActive"
        class="absolute inset-0 bg-black/70 flex flex-col items-center justify-center text-center z-20"
      >
        <p class="text-3xl md:text-4xl font-bold mb-5 text-slate-100">Maç Başlıyor</p>
        <p class="text-[10rem] md:text-[14rem] leading-none font-black animate-pulse text-white">
          {{ preStartCountdown }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMatchStore } from "@/stores/useMatchStore";

const matchStore = useMatchStore();
const route = useRoute();

const allianceParam = computed(() => String(route.params.alliance || "").toLowerCase());
const wrongAlliance = computed(() => allianceParam.value !== "red" && allianceParam.value !== "blue");

const ownAlliance = computed<"red" | "blue" | null>(() => {
  if (allianceParam.value === "red") return "red";
  if (allianceParam.value === "blue") return "blue";
  return null;
});

const ownAllianceLabel = computed(() => (ownAlliance.value === "red" ? "KIRMIZI" : "MAVİ"));
const ownPrematchTeams = computed(() =>
  ownAlliance.value === "red" ? matchStore.preMatch.redTeams : matchStore.preMatch.blueTeams
);
const opponentPrematchTeams = computed(() =>
  ownAlliance.value === "red" ? matchStore.preMatch.blueTeams : matchStore.preMatch.redTeams
);

const hasLiveMatch = computed(
  () =>
    matchStore.currentPage === "matchbar" &&
    Boolean(matchStore.matchBar.title) &&
    Boolean(matchStore.matchBar.remainingTime)
);
const isPrematchInfo = computed(
  () =>
    matchStore.currentPage === "prematch" &&
    Boolean(matchStore.preMatch.title) &&
    (matchStore.preMatch.redTeams.length > 0 || matchStore.preMatch.blueTeams.length > 0)
);
const preStartCountdown = computed(() => matchStore.matchBar.preStartCountdown ?? null);
const isCountdownActive = computed(
  () => typeof preStartCountdown.value === "number" && preStartCountdown.value > 0
);

const attackerAlliance = computed(() => matchStore.matchBar.attackerAlliance);
const isEndgame = computed(() => attackerAlliance.value === 2 && !isCountdownActive.value);

const isOwnAttacking = computed(() => {
  if (!ownAlliance.value) return false;
  if (isCountdownActive.value) return false;
  if (attackerAlliance.value === 2) return true;
  return (
    (attackerAlliance.value === 0 && ownAlliance.value === "red") ||
    (attackerAlliance.value === 1 && ownAlliance.value === "blue")
  );
});

const ownRoleText = computed(() => {
  if (isCountdownActive.value) return "Hazirlik";
  if (isEndgame.value) return "Endgame: Ikisi de aktif";
  return isOwnAttacking.value ? "Saldiri Modu" : "Savunma Modu";
});

const ownRoleClass = computed(() => {
  if (isCountdownActive.value) return "text-amber-200";
  if (isEndgame.value) return "text-yellow-200";
  return isOwnAttacking.value ? "text-emerald-200" : "text-slate-200";
});

const phasePillText = computed(() => {
  if (!hasLiveMatch.value) return "MATCH OFFLINE";
  if (isCountdownActive.value) return `START IN ${preStartCountdown.value}`;
  if (attackerAlliance.value === 0) return "RED ATTACK";
  if (attackerAlliance.value === 1) return "BLUE ATTACK";
  return "ENDGAME";
});

const phasePillClass = computed(() => {
  if (isCountdownActive.value) return "text-amber-200";
  if (attackerAlliance.value === 0) return "text-red-200";
  if (attackerAlliance.value === 1) return "text-blue-200";
  return "text-yellow-200";
});

const activeAllianceText = computed(() => {
  if (isCountdownActive.value) return "Countdown";
  if (attackerAlliance.value === 0) return "Red";
  if (attackerAlliance.value === 1) return "Blue";
  return "Endgame";
});

const showRedSwitchIcon = computed(
  () => !isCountdownActive.value && (attackerAlliance.value === 0 || attackerAlliance.value === 2)
);
const showBlueSwitchIcon = computed(
  () => !isCountdownActive.value && (attackerAlliance.value === 1 || attackerAlliance.value === 2)
);

const showShiftAnnouncement = ref(false);
const shiftAnnouncement = ref("");
const hasInitializedAttacker = ref(false);
let shiftAnnouncementTimer: ReturnType<typeof setTimeout> | null = null;

watch(
  () => hasLiveMatch.value,
  (isLive) => {
    if (!isLive) {
      hasInitializedAttacker.value = false;
      showShiftAnnouncement.value = false;
      shiftAnnouncement.value = "";
    }
  }
);

watch(
  () => attackerAlliance.value,
  (newVal, oldVal) => {
    if (!hasLiveMatch.value || isCountdownActive.value) return;
    if (!hasInitializedAttacker.value) {
      hasInitializedAttacker.value = true;
      return;
    }
    if (oldVal === undefined || oldVal === null || newVal === oldVal) return;

    if (shiftAnnouncementTimer) {
      clearTimeout(shiftAnnouncementTimer);
    }
    if (newVal === 0) shiftAnnouncement.value = "Alliance Shift: RED";
    else if (newVal === 1) shiftAnnouncement.value = "Alliance Shift: BLUE";
    else shiftAnnouncement.value = "Alliance Shift: ENDGAME";

    showShiftAnnouncement.value = true;
    shiftAnnouncementTimer = setTimeout(() => {
      showShiftAnnouncement.value = false;
      shiftAnnouncementTimer = null;
    }, 1800);
  }
);

onBeforeUnmount(() => {
  if (shiftAnnouncementTimer) {
    clearTimeout(shiftAnnouncementTimer);
    shiftAnnouncementTimer = null;
  }
});

definePageMeta({
  layout: "driver-layout",
});
</script>

<style scoped>
.shift-pop-enter-from,
.shift-pop-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.98);
}

.shift-pop-enter-active,
.shift-pop-leave-active {
  transition: all 0.2s ease;
}

.shift-pop-enter-to,
.shift-pop-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}
</style>
