<template>
  <div
      class="w-screen h-screen flex flex-col items-center justify-items-center"
  >
    <img
        src="../public/logo-counting.svg"
        class="w-96 h-96 mt-24"
        alt=""
    />
    <div
        class="mt-24 bg-gradient-to-br from-[#0066B3] to-[#ED1C24] w-3/4 h-32 flex justify-center items-center justify-items-center rounded-2xl translate-y-0 bop"
    >
      <div class="absolute bg-white inset-4 rounded-2xl -z-10"></div>
      <h1 class="text-5xl font-black text-red-600">SONUÇLAR AÇIKLANIYOOR!!!</h1>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
<style>
.bop {
  --border-angle: 0turn;
  --main-bg: conic-gradient(
      from var(--border-angle),
      #ed1c24,
      #ed1c24 5%,
      #3300a1 60%,
      #0066b3 95%
  );

  border: solid 5px transparent;
  border-radius: 2em;
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

  animation: bg-spin 5s cubic-bezier(0.1, 0.2, 0.2, 0.1) infinite,
  bop 3s infinite;
}

@keyframes bg-spin {
  to {
    --border-angle: 1turn;
  }
}

@property --border-angle {
  syntax: "<angle>";
  inherits: true;
  initial-value: 0turn;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes bop {
  0% {
    transform: translateY(-50px);
  }
  50% {
    transform: translateY(80px);
  }
  100% {
    transform: translateY(-50px);
  }
}
</style>
