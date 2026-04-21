<template>
  <div class="h-screen w-screen relative flex flex-col overflow-hidden bg-black">
    <transition name="slide-top">
    <div class="relative z-10 flex w-full flex-row h-60 text-white"
         v-if="!matchStore.matchBar.scoreCheckInProgress && matchStore.matchBar.matchbarVisible">
      <!-- RED -->
      <div class="flex flex-row items-center h-full w-1/2 bg-frc-red-light teamScore2 justify-end">
        <div class="flex flex-row h-full flex-1">
          <div v-for="(team, index) in matchStore.matchBar.redTeamIDs"
               class="flex-1 h-full flex items-center justify-center"
               :class="{
                'bg-frc-red-mid': index % 2 === 0,
                'bg-frc-red-dark': index % 2 !== 0
               }">
            <h1 class="text-7xl font-bold">{{ team }}</h1>
          </div>
        </div>
        <div class="w-48 h-full flex flex-col items-center justify-center ml-4 mr-8">
          <h1 class="text-center w-full font-bold text-3xl">KIRMIZI</h1>
          <h1 class="text-8xl font-black leading-none mt-1">{{ matchStore.matchBar.redScore }}</h1>
          <div class="h-10 mt-2 flex items-center justify-center">
            <div
              v-if="showRedSwitchIcon"
              class="rounded-md bg-[#f6e327] border-2 border-black/40 p-1.5 shadow-lg"
            >
              <img src="/switch_red.png" alt="Red can score" class="w-7 h-7 object-contain" />
            </div>
          </div>
        </div>
      </div>

      <!-- TIMER -->
      <div class="bg-[#231E1F] w-64 h-full flex flex-col items-center justify-center teamScore z-10">
        <div class="flex items-center justify-between w-full px-5 text-white">
          <p class="text-3xl font-black">{{ shiftCounterLabel }}</p>
          <p class="text-3xl font-black tabular-nums">{{ switchCountdownLabel }}</p>
        </div>
        <icon class="text-7xl text-white mt-1" name="material-symbols:nest-clock-farsight-analog"/>
        <h1 class="text-5xl text-white font-bold mt-2">{{ matchStore.matchBar.remainingTime }}</h1>
      </div>

      <!-- BLUE -->
      <div class="flex flex-row items-center h-full w-1/2 bg-frc-blue-light teamScore2 justify-start">
        <div class="w-48 h-full flex flex-col items-center justify-center ml-8 mr-4">
          <h1 class="text-center w-full font-bold text-3xl">MAVİ</h1>
          <h1 class="text-8xl font-black leading-none mt-1">{{ matchStore.matchBar.blueScore }}</h1>
          <div class="h-10 mt-2 flex items-center justify-center">
            <div
              v-if="showBlueSwitchIcon"
              class="rounded-md bg-[#f6e327] border-2 border-black/40 p-1.5 shadow-lg"
            >
              <img src="/switch_blue.png" alt="Blue can score" class="w-7 h-7 object-contain" />
            </div>
          </div>
        </div>
        <div class="flex flex-row h-full flex-1">
          <div v-for="(team, index) in matchStore.matchBar.blueTeamIDs"
               class="flex-1 h-full flex items-center justify-center"
               :class="{
                'bg-frc-blue-mid': index % 2 === 0,
                'bg-frc-blue-dark': index % 2 !== 0
               }">
            <h1 class="text-7xl font-bold">{{ team }}</h1>
          </div>
        </div>
      </div>
    </div>
    </transition>
    <!-- SCORE CHECK -->
    <transition name="slide-top">
      <div v-if="delayedVisibleCounting && matchStore.matchBar.matchbarVisible"
           class="flex w-full flex-row h-48 bg-[#C9C200] items-center justify-center">
        <icon class="text-7xl text-black -rotate-12 scale-x-100 mr-8" name="mdi:whistle"/>
        <h1 class="text-6xl text-black font-black">Puan Sayımı Yapılıyor...</h1>
        <icon class="text-7xl text-black rotate-12 -scale-x-100 ml-8" name="mdi:whistle"/>
      </div>
    </transition>
    <div class="w-full flex-1 min-h-0 bg-black">
      <iframe
        v-if="streamEnabled && streamEmbedUrl"
        :src="streamEmbedUrl"
        class="w-full h-full border-0"
        allow="autoplay; fullscreen; picture-in-picture; camera; microphone"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-slate-300 font-semibold tracking-wide"
      >
        YAYIN KAPALI
      </div>
    </div>
    <transition name="countdown-pop">
      <div
        v-if="countdownValue !== null"
        class="absolute inset-0 flex items-center justify-center bg-black/45 z-20"
      >
        <div class="text-center">
          <p class="text-white font-black text-4xl tracking-wide mb-6">MAÇ BAŞLIYOR</p>
          <h1 class="text-white font-black text-[12rem] leading-none">{{ countdownValue }}</h1>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useMatchStore } from '@/stores/useMatchStore'
const matchStore = useMatchStore()
const { streamEmbedUrl: defaultStreamEmbedUrl } = useBackendEndpoints()
const streamEnabled = computed(() => matchStore.matchBar.streamEnabled ?? true)
const streamEmbedUrl = computed(() => {
  const wsValue = matchStore.matchBar.streamUrl
  if (typeof wsValue === 'string' && wsValue.trim().length > 0) return wsValue.trim()
  return defaultStreamEmbedUrl
})
const countdownValue = computed<number | null>(() => matchStore.matchBar.preStartCountdown ?? null)
const TOTAL_MATCH_SECONDS = 210
const ACTIVE_PHASE_SECONDS = 180
const SHIFT_SECONDS = 30
const TOTAL_SHIFTS = ACTIVE_PHASE_SECONDS / SHIFT_SECONDS

const delayedVisibleCounting = ref(false)
const hasPlayedMatchStart = ref(false)
const suppressSwitchUntilMs = ref(0)

let matchStartAudio: HTMLAudioElement | null = null
let switchAudio: HTMLAudioElement | null = null
let endgameAudio: HTMLAudioElement | null = null
let endAudio: HTMLAudioElement | null = null
let unlockHandler: (() => void) | null = null

const safePlay = (audio: HTMLAudioElement | null) => {
  if (!audio) return
  audio.currentTime = 0
  const playPromise = audio.play()
  if (playPromise) {
    playPromise.catch(() => {
      // Browser may block autoplay until user interaction.
    })
  }
}

const markStartSoundPlayed = () => {
  suppressSwitchUntilMs.value = Date.now() + 1500
}

const parseRemainingTimeToSeconds = (value: string): number | null => {
  const [minRaw, secRaw] = value.split(':')
  const minutes = Number(minRaw)
  const seconds = Number(secRaw)
  if (!Number.isFinite(minutes) || !Number.isFinite(seconds)) return null
  return (minutes * 60) + seconds
}

const remainingSeconds = computed<number | null>(() =>
  parseRemainingTimeToSeconds(matchStore.matchBar.remainingTime)
)

const currentShiftIndex = computed(() => {
  const rem = remainingSeconds.value
  if (rem === null) return null
  const elapsed = TOTAL_MATCH_SECONDS - rem
  if (elapsed < 0 || elapsed >= ACTIVE_PHASE_SECONDS) return null
  const shift = Math.floor(elapsed / SHIFT_SECONDS) + 1
  return Math.min(Math.max(shift, 1), TOTAL_SHIFTS)
})

const secondsToShiftSwitch = computed(() => {
  const rem = remainingSeconds.value
  if (rem === null) return 0
  const elapsed = TOTAL_MATCH_SECONDS - rem
  if (elapsed < 0 || elapsed >= ACTIVE_PHASE_SECONDS) return 0
  const secondsIntoCurrentShift = elapsed % SHIFT_SECONDS
  if (secondsIntoCurrentShift === 0) return SHIFT_SECONDS
  return SHIFT_SECONDS - secondsIntoCurrentShift
})

const isImpactPhase = computed(
  () => countdownValue.value === null && matchStore.matchBar.attackerAlliance === 2
)

const shiftCounterLabel = computed(() => {
  if (countdownValue.value !== null) return 'START'
  if (matchStore.matchBar.scoreCheckInProgress) return 'CHECK'
  if (isImpactPhase.value) return 'ENDGAME'
  if (currentShiftIndex.value === null) return '-'
  return `${currentShiftIndex.value} / ${TOTAL_SHIFTS}`
})

const switchCountdownLabel = computed(() => {
  if (countdownValue.value !== null) return String(countdownValue.value).padStart(2, '0')
  const rem = remainingSeconds.value
  if (rem === null) return ':--'
  if (isImpactPhase.value) return `:${String(Math.max(rem, 0)).padStart(2, '0')}`
  return `:${String(secondsToShiftSwitch.value).padStart(2, '0')}`
})

const showRedSwitchIcon = computed(
  () =>
    countdownValue.value === null &&
    !matchStore.matchBar.scoreCheckInProgress &&
    (matchStore.matchBar.attackerAlliance === 0 || matchStore.matchBar.attackerAlliance === 2)
)

const showBlueSwitchIcon = computed(
  () =>
    countdownValue.value === null &&
    !matchStore.matchBar.scoreCheckInProgress &&
    (matchStore.matchBar.attackerAlliance === 1 || matchStore.matchBar.attackerAlliance === 2)
)

onMounted(() => {
  matchStartAudio = new Audio('/match_start.wav')
  matchStartAudio.preload = 'auto'
  matchStartAudio.volume = 0.8

  switchAudio = new Audio('/switch.mp3')
  switchAudio.preload = 'auto'
  switchAudio.volume = 0.8

  endgameAudio = new Audio('/endgame.mp3')
  endgameAudio.preload = 'auto'
  endgameAudio.volume = 0.9

  endAudio = new Audio('/ENDMATCH.mp3')
  endAudio.preload = 'auto'
  endAudio.volume = 0.9

  // Unlock audio context on first user interaction for browser autoplay policies.
  unlockHandler = () => {
    const primeAudio = (audio: HTMLAudioElement | null) => {
      if (!audio) return
      const promise = audio.play()
      if (promise) {
        promise
          .then(() => {
            audio.pause()
            audio.currentTime = 0
          })
          .catch(() => {})
      }
    }
    primeAudio(matchStartAudio)
    primeAudio(switchAudio)
    primeAudio(endgameAudio)
    primeAudio(endAudio)

    window.removeEventListener('pointerdown', unlockHandler as EventListener)
    window.removeEventListener('keydown', unlockHandler as EventListener)
    unlockHandler = null
  }

  window.addEventListener('pointerdown', unlockHandler, { passive: true })
  window.addEventListener('keydown', unlockHandler)
})

onBeforeUnmount(() => {
  if (unlockHandler) {
    window.removeEventListener('pointerdown', unlockHandler as EventListener)
    window.removeEventListener('keydown', unlockHandler as EventListener)
    unlockHandler = null
  }
  matchStartAudio = null
  switchAudio = null
  endgameAudio = null
  endAudio = null
})

watch(
    () => matchStore.matchBar.scoreCheckInProgress,
    (newVal, oldVal) => {
      if (newVal) {
        if (!oldVal) {
          safePlay(endAudio)
        }
        setTimeout(() => {
          delayedVisibleCounting.value = true
        }, 700)
      } else {
          delayedVisibleCounting.value = false
      }
    },
    { immediate: true }
)

watch(
  () => matchStore.matchBar.remainingTime,
  (newVal) => {
    if (hasPlayedMatchStart.value) return
    if (!matchStartAudio) return
    if (!newVal || matchStore.matchBar.scoreCheckInProgress) return
    if (countdownValue.value !== null) return
    hasPlayedMatchStart.value = true
    markStartSoundPlayed()
    safePlay(matchStartAudio)
  }
)

watch(
  () => countdownValue.value,
  (newVal, oldVal) => {
    if (hasPlayedMatchStart.value) return
    if (!matchStartAudio) return
    if (oldVal === null || newVal !== null) return
    if (!matchStore.matchBar.remainingTime || matchStore.matchBar.scoreCheckInProgress) return
    hasPlayedMatchStart.value = true
    markStartSoundPlayed()
    safePlay(matchStartAudio)
  }
)

watch(
  () => matchStore.matchBar.attackerAlliance,
  (newVal, oldVal) => {
    if (oldVal === undefined || oldVal === null) return
    if (newVal === oldVal) return
    if (matchStore.matchBar.scoreCheckInProgress) return
    if (countdownValue.value !== null) return
    if (Date.now() < suppressSwitchUntilMs.value) return
    if (newVal === 2) {
      const remainingSeconds = parseRemainingTimeToSeconds(matchStore.matchBar.remainingTime)
      // Endgame sesi sadece endgame başlangıcında (yaklaşık son 30 saniye) çalsın.
      if (remainingSeconds === null || remainingSeconds > 30 || remainingSeconds < 27) return
      safePlay(endgameAudio)
      return
    }
    safePlay(switchAudio)
  }
)
</script>

<style scoped>
.teamScore {
  animation: teamScorePull 1.5s ease-in-out forwards, appear 2s ease forwards;
  box-shadow: 0 0 15px rgba(0, 0, 0, 1);
}
.teamScore2 {
  animation: teamScorePull 2s ease-in-out forwards, appear 3s ease forwards;
}

/* Transition for slide-top */
.slide-top-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}
.slide-top-enter-active {
  transition: transform 1s ease-in-out, opacity 2s ease-in-out;
}
.slide-top-enter-to {
  transform: translateY(0);
  opacity: 1;
}
.slide-top-leave-from {
  transform: translateY(0);
  opacity: 1;
}
.slide-top-leave-active {
  transition: transform 0.5s ease-in-out, opacity 0.5s ease-in-out;
}
.slide-top-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

@keyframes teamScorePull {
  0% {
    transform: translateY(-100%);
  }
  100% {
    transform: translateY(0%);
  }
}

@keyframes appear {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

/* Ensure icon aligns vertically with score label */
.icon-align {
  line-height: 1;
  vertical-align: middle;
  display: flex;
  align-items: center;
}

.icon-score-row {
  align-items: center;
  display: flex;
}

.countdown-pop-enter-from,
.countdown-pop-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.countdown-pop-enter-active,
.countdown-pop-leave-active {
  transition: all 0.22s ease;
}

.countdown-pop-enter-to,
.countdown-pop-leave-from {
  opacity: 1;
  transform: scale(1);
}
</style>
