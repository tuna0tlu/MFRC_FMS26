<template>
  <div
    class="flex flex-col w-svw h-screen items-center justify-between transition-colors duration-500"
    :class="{
      'bg-frc-red-dark': alliance === 'red',
      'bg-frc-blue-dark': alliance === 'blue',
      'bg-black': wrongAlliance,
    }"
  >
    <!-- Remaining Time at Top Center -->
    <div v-if="hasLiveMatch" class="w-full flex justify-center mt-6">
      <div class="bg-slate-900/90 rounded-2xl px-8 py-3 shadow-lg flex items-center">
        <icon class="text-2xl text-white mr-2 animate-pulse" name="material-symbols:nest-clock-farsight-analog" />
        <span class="text-3xl font-bold text-white">Kalan Süre: {{ matchStore.matchBar.remainingTime }}</span>
      </div>
    </div>

    <h1
      class="text-6xl font-bold text-white animate-pulse mt-10"
      v-if="wrongAlliance"
    >
      PLEASE CHOOSE CORRECT ALLIANCE
    </h1>

    <div
      v-else-if="isPrematchInfo"
      class="flex flex-1 w-full items-center justify-center px-4"
    >
      <div class="w-11/12 max-w-5xl bg-slate-900/80 border border-slate-500 rounded-3xl p-8 shadow-2xl">
        <h1 class="text-5xl font-black text-white text-center">{{ matchStore.preMatch.title }}</h1>
        <p class="text-2xl text-slate-200 text-center mt-3">
          Hakem Tablet: {{ ownAllianceLabel }}
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
          <div class="rounded-2xl p-4 text-white" :class="ownAlliance === 'red' ? 'bg-red-700/60 ring-2 ring-red-300' : 'bg-blue-700/60 ring-2 ring-blue-300'">
            <p class="text-xl font-black mb-2">SORUMLU OLDUĞUN İTTİFAK</p>
            <div class="space-y-2">
              <div
                v-for="team in ownPrematchTeams"
                :key="`own-${team.id}`"
                class="bg-black/25 rounded-lg px-3 py-2 text-lg font-bold text-white"
              >
                {{ team.id }} - {{ team.name }}
              </div>
            </div>
          </div>
          <div class="rounded-2xl p-4 text-white" :class="opponentAlliance === 'red' ? 'bg-red-700/50' : 'bg-blue-700/50'">
            <p class="text-xl font-black mb-2">KARŞI İTTİFAK
            </p>
            <div class="space-y-2">
              <div
                v-for="team in opponentPrematchTeams"
                :key="`opp-${team.id}`"
                class="bg-black/25 rounded-lg px-3 py-2 text-lg font-bold text-white"
              >
                {{ team.id }} - {{ team.name }}
              </div>
            </div>
          </div>
        </div>
        <p class="text-center text-xl mt-6 text-amber-200 font-semibold">
          Maç başlatılınca canlı hakem ekranı otomatik açılacak.
        </p>
      </div>
    </div>

    <div
      v-else-if="!hasLiveMatch"
      class="flex flex-1 w-full items-center justify-center"
    >
      <div class="bg-slate-900/85 border border-slate-500 rounded-3xl px-12 py-10 shadow-2xl text-center">
        <h1 class="text-7xl font-black text-white tracking-wide">MAÇ YOK</h1>
        <p class="text-2xl text-slate-200 mt-4">MAÇ BEKLENİYOR...</p>
      </div>
    </div>

    <div
      v-else-if="isCountdownActive"
      class="flex flex-1 w-full items-center justify-center"
    >
      <div class="bg-slate-900/85 border border-slate-500 rounded-3xl px-16 py-12 shadow-2xl text-center">
        <p class="text-3xl font-bold text-slate-200 mb-5">Maç Başlıyor</p>
        <h1 class="text-[10rem] leading-none font-black text-white">{{ preStartCountdown }}</h1>
      </div>
    </div>

    <div v-else-if="isMatchRunning" class="flex flex-1 flex-col items-center justify-center w-full">
      <div class="w-11/12 max-w-5xl mb-6 bg-slate-900/70 backdrop-blur-sm rounded-2xl p-4 border border-slate-500">
        <h2 class="text-2xl font-black text-white text-center mb-3">
          Bu Tablet: {{ ownAllianceLabel }} | Puan Dağılımı
        </h2>
        <div
          class="rounded-xl px-4 py-3 text-center text-xl font-black mb-3"
          :class="canScore ? 'bg-emerald-700/70 text-white' : 'bg-amber-600/80 text-black'"
        >
          {{ phaseText }}
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-white">
          <div class="rounded-xl p-3" :class="ownAlliance === 'red' ? 'bg-red-700/60' : 'bg-blue-700/60'">
            <p class="text-xl font-bold mb-1">
              {{ ownAllianceLabel }} ittifakına yazılır
              <span class="font-black">{{ canScore ? '(Açık)' : '(Kapalı)' }}</span>
            </p>
            <p class="text-lg">FUEL: +{{ fuelCount * 3 }}</p>
            <p class="text-lg">CLIMB: +{{ climbPoints }}</p>
            <p class="text-2xl font-black mt-1">TOPLAM: +{{ ownDelta }}</p>
          </div>
          <div class="rounded-xl p-3" :class="opponentAlliance === 'red' ? 'bg-red-700/60' : 'bg-blue-700/60'">
            <p class="text-xl font-bold mb-1">{{ opponentAllianceLabel }} ittifakına yazılır</p>
            <p class="text-lg">MINOR FAUL: +{{ minorPenaltyCount * 5 }}</p>
            <p class="text-lg">MAJOR FAUL: +{{ majorPenaltyCount * 15 }}</p>
            <p class="text-2xl font-black mt-1">TOPLAM: +{{ foulDelta }}</p>
          </div>
        </div>
        <p class="text-center text-slate-100 mt-3 text-lg font-semibold">
          Bu gönderimde net skor etkisi: KIRMIZI +{{ redDelta }} | MAVİ +{{ blueDelta }}
        </p>
      </div>

      <div class="w-11/12 max-w-5xl mb-8 bg-slate-900/50 backdrop-blur-sm rounded-2xl p-5 border border-slate-600">
        <h1 class="text-2xl font-bold text-white mb-3 text-center">CLIMB LEVEL SEÇİMİ</h1>
        <div class="grid grid-cols-4 gap-2 text-white">
          <div class="rounded-lg bg-slate-700/80 px-3 py-2 font-bold text-center">ROBOT</div>
          <div class="rounded-lg bg-slate-700/80 px-3 py-2 font-bold text-center">L1</div>
          <div class="rounded-lg bg-slate-700/80 px-3 py-2 font-bold text-center">L2</div>
          <div class="rounded-lg bg-slate-700/80 px-3 py-2 font-bold text-center">L3</div>

          <template v-for="(_, robotIndex) in climbSelections" :key="`climb-row-${robotIndex}`">
            <div class="rounded-lg bg-slate-800/90 px-3 py-3 font-bold text-center">
              Robot {{ robotIndex + 1 }}
            </div>
            <button
              v-for="level in climbLevels"
              :key="`climb-${robotIndex}-${level}`"
              @click="setRobotClimbLevel(robotIndex, level)"
              class="rounded-lg px-3 py-3 font-black transition-all duration-150 border"
              :class="
                climbSelections[robotIndex] === level
                  ? 'bg-emerald-600 text-white border-emerald-300'
                  : 'bg-slate-700/70 text-slate-100 border-slate-500 hover:bg-slate-600'
              "
            >
              {{ level }}
            </button>
          </template>
        </div>
        <p class="text-slate-200 text-lg font-semibold text-center mt-3">
          Seçimler: L1 {{ stageCounts.L1 }} | L2 {{ stageCounts.L2 }} | L3 {{ stageCounts.L3 }}
        </p>
      </div>

      <!-- Penalties Section -->
      <div class="flex flex-row items-center justify-center gap-16 w-full">
        <!-- Minor Penalties -->
        <div class="flex flex-col items-center justify-around bg-slate-900/50 backdrop-blur-sm p-6 rounded-xl shadow-lg min-w-[220px]">
          <div class="flex flex-col items-center justify-around mb-2">
            <h1 class="text-2xl font-bold text-white">MINOR PENALTIES</h1>
            <icon class="flex relative text-5xl text-white transform hover:scale-110 transition-transform duration-200" name="mdi:whistle" />
          </div>
          <button
            @click="minorPenaltyCount++"
            class="bg-lime-700 hover:bg-lime-500 active:bg-lime-600 font-bold text-xl text-white px-6 py-2 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl mb-2"
          >
            ARTTIR
          </button>
          <h1 class="text-3xl font-bold text-white text-center mb-2">
            {{ minorPenaltyCount }}
          </h1>
          <button
            @click="minorPenaltyCount > 0 ? minorPenaltyCount-- : minorPenaltyCount"
            class="bg-purple-700 hover:bg-purple-500 active:bg-purple-600 font-bold text-xl text-white px-6 py-2 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            AZALT
          </button>
        </div>
        <!-- Major Penalties -->
        <div class="flex flex-col items-center justify-around bg-slate-900/50 backdrop-blur-sm p-6 rounded-xl shadow-lg min-w-[220px]">
          <div class="flex flex-col items-center justify-around mb-2">
            <h1 class="text-2xl font-bold text-white">MAJOR PENALTIES</h1>
            <icon class="text-5xl text-red-300 transform hover:scale-110 transition-transform duration-200" name="mdi:whistle" />
          </div>
          <button
            @click="majorPenaltyCount++"
            class="bg-lime-700 hover:bg-lime-500 active:bg-lime-600 font-bold text-xl text-white px-6 py-2 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl mb-2"
          >
            ARTTIR
          </button>
          <h1 class="text-3xl font-bold text-white text-center mb-2">
            {{ majorPenaltyCount }}
          </h1>
          <button
            @click="majorPenaltyCount > 0 ? majorPenaltyCount-- : majorPenaltyCount"
            class="bg-purple-700 hover:bg-purple-500 active:bg-purple-600 font-bold text-xl text-white px-6 py-2 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            AZALT
          </button>
        </div>
        <!-- Fuel -->
        <div
          class="flex flex-col items-center justify-around bg-slate-900/50 backdrop-blur-sm p-6 rounded-xl shadow-lg min-w-[220px] transition"
          :class="canScore ? '' : 'opacity-50'"
        >
          <div class="flex flex-col items-center justify-around mb-2">
            <h1 class="text-2xl font-bold text-white">FUEL {{ canScore ? '' : '(KAPALI)' }}</h1>
            <icon class="text-5xl text-red-300 transform hover:scale-110 transition-transform duration-200" name="mdi:gas-station" />
          </div>
          <button
            @click="canScore ? fuelCount++ : fuelCount"
            :disabled="!canScore"
            class="bg-lime-700 hover:bg-lime-500 active:bg-lime-600 disabled:bg-slate-600 disabled:cursor-not-allowed font-bold text-xl text-white px-6 py-2 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl mb-2"
          >
            ARTTIR
          </button>
          <h1 class="text-3xl font-bold text-white text-center mb-2">
            {{ fuelCount }}
          </h1>
          <button
            @click="canScore ? (fuelCount > 0 ? fuelCount-- : fuelCount) : null"
            :disabled="!canScore"
            class="bg-purple-700 hover:bg-purple-500 active:bg-purple-600 disabled:bg-slate-600 disabled:cursor-not-allowed font-bold text-xl text-white px-6 py-2 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            AZALT
          </button>
        </div>
      </div>

    </div>

    <div
      v-else
      class="flex flex-1 w-full items-center justify-center"
    >
      <div class="bg-slate-900/85 border border-slate-500 rounded-3xl px-12 py-10 shadow-2xl text-center">
        <h1 class="text-6xl font-black text-white">MAÇ BİTTİ</h1>
        <p class="text-2xl text-slate-200 mt-4">Yeni maç başlayana kadar giriş kapalı.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMatchStore } from "@/stores/useMatchStore";

const matchStore = useMatchStore();
const route = useRoute();
const { httpBase } = useBackendEndpoints();

const minorPenaltyCount = ref(0);
const majorPenaltyCount = ref(0);
const fuelCount = ref(0);
const climbLevels = ["L1", "L2", "L3"] as const;
type ClimbLevel = (typeof climbLevels)[number] | null;
const climbSelections = ref<ClimbLevel[]>([null, null, null]);
const CLIMB_POINTS_BY_LEVEL: Record<Exclude<ClimbLevel, null>, number> = {
  L1: 10,
  L2: 10,
  L3: 10,
};

definePageMeta({
  layout: "referee-layout",
});

const alliance = route.params.alliance;
const wrongAlliance = ref(false);

if (alliance !== "red" && alliance !== "blue") {
  wrongAlliance.value = true;
}

const ownAlliance = computed<"red" | "blue">(() =>
  alliance === "blue" ? "blue" : "red"
);
const opponentAlliance = computed<"red" | "blue">(() =>
  ownAlliance.value === "red" ? "blue" : "red"
);
const ownAllianceLabel = computed(() =>
  ownAlliance.value === "red" ? "KIRMIZI" : "MAVİ"
);
const opponentAllianceLabel = computed(() =>
  opponentAlliance.value === "red" ? "KIRMIZI" : "MAVİ"
);
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
const currentAttacker = computed(() => matchStore.matchBar.attackerAlliance);
const isMatchRunning = computed(
  () => hasLiveMatch.value && !isCountdownActive.value && !matchStore.matchBar.scoreCheckInProgress
);
const canScore = computed(() => {
  if (!hasLiveMatch.value) return false;
  if (isCountdownActive.value) return false;
  if (currentAttacker.value === 2) return true;
  if (currentAttacker.value === 0) return ownAlliance.value === "red";
  if (currentAttacker.value === 1) return ownAlliance.value === "blue";
  return false;
});

const phaseText = computed(() => {
  if (!hasLiveMatch.value) {
    return "Maç başlamadı: sadece faul girişi beklemede";
  }
  if (currentAttacker.value === 2) {
    return "ENDGAME: iki ittifak da puan + faul girebilir";
  }
  if (canScore.value) {
    return `${ownAllianceLabel.value} saldırıyor: puan + faul girişi açık`;
  }
  return `${opponentAllianceLabel.value} saldırıyor: sadece faul girişi açık`;
});

const stageCounts = computed(() => {
  const counts = { L1: 0, L2: 0, L3: 0 };
  for (const level of climbSelections.value) {
    if (level) {
      counts[level] += 1;
    }
  }
  return counts;
});
const climbCount = computed(() =>
  climbSelections.value.filter((level) => level !== null).length
);
const climbPoints = computed(() =>
  climbSelections.value.reduce((sum, level) => {
    if (!level) return sum;
    return sum + CLIMB_POINTS_BY_LEVEL[level];
  }, 0)
);
const ownDelta = computed(() => (fuelCount.value * 3) + climbPoints.value);
const foulDelta = computed(() => (minorPenaltyCount.value * 5) + (majorPenaltyCount.value * 15));
const redDelta = computed(() =>
  ownAlliance.value === "red" ? ownDelta.value : foulDelta.value
);
const blueDelta = computed(() =>
  ownAlliance.value === "blue" ? ownDelta.value : foulDelta.value
);

const resetAll = () => {
  minorPenaltyCount.value = 0;
  majorPenaltyCount.value = 0;
  fuelCount.value = 0;
  climbSelections.value = [null, null, null];
};

const setRobotClimbLevel = (robotIndex: number, level: Exclude<ClimbLevel, null>) => {
  const current = climbSelections.value[robotIndex];
  climbSelections.value[robotIndex] = current === level ? null : level;
};

let syncTimer: ReturnType<typeof setTimeout> | null = null;
let activeController: AbortController | null = null;
const isApplyingRemoteState = ref(false);

const parseError = (error: any): string =>
  error?.data?.detail || error?.data?.message || error?.message || "Bilinmeyen hata";

const queueLiveSync = () => {
  if (isApplyingRemoteState.value) return;
  if (wrongAlliance.value) return;
  if (!hasLiveMatch.value) return;
  if (isCountdownActive.value) return;
  if (matchStore.matchBar.scoreCheckInProgress) return;

  if (syncTimer) {
    clearTimeout(syncTimer);
  }
  syncTimer = setTimeout(() => {
    void pushLiveUpdate();
  }, 120);
};

const pushLiveUpdate = async () => {
  const sendingData = {
    alliance: ownAlliance.value,
    minorFaul: minorPenaltyCount.value,
    majorFaul: majorPenaltyCount.value,
    seasonSpecificValues: [fuelCount.value, climbCount.value],
    climbSelections: climbSelections.value,
  };

  if (activeController) {
    activeController.abort();
  }
  const controller = new AbortController();
  activeController = controller;

  const requestUrl = `${httpBase}/game/referee`;
  try {
    await $fetch(requestUrl, {
      method: "POST",
      body: sendingData,
      signal: controller.signal,
    });
  } catch (error: any) {
    if (error?.name === "AbortError") return;
    console.error("Referee live update failed:", parseError(error));
  } finally {
    if (activeController === controller) {
      activeController = null;
    }
  }
};

const normalizeClimbSelections = (raw: unknown): ClimbLevel[] => {
  if (!Array.isArray(raw) || raw.length !== 3) return [null, null, null];
  return raw.map((level) => (level === "L1" || level === "L2" || level === "L3" ? level : null)) as ClimbLevel[];
};

const ownRefereeState = computed(() => {
  const state = matchStore.matchBar.refereeState;
  if (!state) return null;
  return ownAlliance.value === "red" ? state.red : state.blue;
});

watch(
  () => ownRefereeState.value,
  (state) => {
    if (!state) return;

    const nextMinor = Number(state.minorFaul || 0);
    const nextMajor = Number(state.majorFaul || 0);
    const nextFuel = Number(state.fuelCount || 0);
    const nextClimbSelections = normalizeClimbSelections(state.climbSelections);

    const isSame =
      minorPenaltyCount.value === nextMinor &&
      majorPenaltyCount.value === nextMajor &&
      fuelCount.value === nextFuel &&
      JSON.stringify(climbSelections.value) === JSON.stringify(nextClimbSelections);
    if (isSame) return;

    isApplyingRemoteState.value = true;
    minorPenaltyCount.value = nextMinor;
    majorPenaltyCount.value = nextMajor;
    fuelCount.value = nextFuel;
    climbSelections.value = nextClimbSelections;
    setTimeout(() => {
      isApplyingRemoteState.value = false;
    }, 0);
  },
  { deep: true, immediate: true }
);

watch(
  [minorPenaltyCount, majorPenaltyCount, fuelCount, climbSelections],
  () => {
    queueLiveSync();
  },
  { deep: true }
);

watch(
  () => matchStore.matchBar.title,
  (newVal, oldVal) => {
    if (!newVal) return;
    if (oldVal === undefined || newVal === oldVal) return;
    resetAll();
  }
);

onBeforeUnmount(() => {
  if (syncTimer) {
    clearTimeout(syncTimer);
    syncTimer = null;
  }
  if (activeController) {
    activeController.abort();
    activeController = null;
  }
});
</script>

<style>
html,
body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}

body {
  background-color: #000000;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active {
  animation: fadeIn 0.3s ease-out;
}

.fade-leave-active {
  animation: fadeIn 0.3s ease-out reverse;
}
</style>
