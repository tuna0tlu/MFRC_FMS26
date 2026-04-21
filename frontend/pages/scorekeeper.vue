<template>
  <div class="flex flex-col w-svw h-screen items-center justify-center bg-yellow-600">
    <!-- Remaining Time at Top Center (sticky/fixed) -->
    <div class="fixed top-4 left-0 w-full flex justify-center z-50">
      <div class="bg-slate-900/90 rounded-2xl px-8 py-3 shadow-lg flex items-center">
        <icon class="text-2xl text-white mr-2 animate-pulse" name="material-symbols:nest-clock-farsight-analog" />
        <span class="text-3xl font-bold text-white">Kalan Süre: {{ matchStore.matchBar.remainingTime }}sn</span>
      </div>
    </div>
    <div class="flex flex-col items-center">
      <div class="mb-10 flex items-center justify-center">
        <icon v-if="status === 'loading'" name="mdi:loading" class="text-8xl text-white animate-spin p-3 drop-shadow-lg" />
        <icon v-else-if="status === 'success'" name="mdi:check-circle" class="text-8xl text-green-500 p-3 drop-shadow-lg" />
        <icon v-else-if="status === 'error'" name="mdi:close-circle" class="text-8xl text-red-500 p-3 drop-shadow-lg" />
        <icon v-else name="mdi:gamepad-variant" class="text-8xl text-white p-3 drop-shadow-lg" />
      </div>
      <div class="flex flex-col items-center justify-center bg-slate-900/50 backdrop-blur-sm p-12 rounded-3xl shadow-2xl min-w-[340px] min-h-[340px]">
        <h1 class="text-5xl font-bold text-white mb-8 text-center">FUEL</h1>
        <div class="flex items-center gap-10 justify-center w-full">
          <button
            @click="decrementCounter"
            class="bg-purple-700 hover:bg-purple-500 active:bg-purple-600 font-bold text-3xl text-white px-8 py-4 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
            :disabled="counter === 0"
          >
            -
          </button>
          <h1 class="text-7xl font-extrabold text-white text-center min-w-[80px]">
            {{ counter }}
          </h1>
          <button
            @click="incrementCounter"
            class="bg-lime-700 hover:bg-lime-500 active:bg-lime-600 font-bold text-3xl text-white px-8 py-4 rounded-2xl transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            +
          </button>
        </div>
      </div>
      <button
        @click="resetCounter"
        class="mt-10 flex items-center gap-3 bg-red-700 hover:bg-red-600 active:bg-red-800 text-white font-extrabold text-3xl px-14 py-6 rounded-3xl shadow-lg hover:shadow-xl transition-all duration-200"
      >
        <icon name="mdi:close" class="text-4xl text-white" />
        RESET
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMatchStore } from "@/stores/useMatchStore";
const matchStore = useMatchStore();
const { httpBase } = useBackendEndpoints();
const counter = ref(0);
const status = ref<'idle' | 'loading' | 'success' | 'error'>('idle');
let currentRequest: AbortController | null = null;

definePageMeta({
  layout: "referee-layout",
});

const incrementCounter = () => {
  counter.value++;
  sendRequest();
};

const decrementCounter = () => {
  if (counter.value > 0) {
    counter.value--;
    sendRequest();
  }
};

const resetCounter = () => {
  counter.value = 0;
  status.value = 'idle';
};

const sendRequest = async () => {
  // Cancel any ongoing request
  if (currentRequest) {
    currentRequest.abort();
  }

  // Create new abort controller for this request
  currentRequest = new AbortController();
  status.value = 'loading';

  try {
    const requestUrl = `${httpBase}/game/scorekeeper?fuel=${counter.value}`;
    const { data, error } = await useFetch(requestUrl, {
      method: 'POST',
      signal: currentRequest.signal
    });

    if (error.value) {
      throw error.value;
    }

    status.value = 'success';
  } catch (err: any) {
    if (err.name === 'AbortError') {
      // Request was cancelled, do nothing
      return;
    }
    status.value = 'error';
  } finally {
    currentRequest = null;
  }
};
</script>

<style>
html,
body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}
</style> 
