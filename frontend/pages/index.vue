<template>
  <div
    class="w-screen h-screen flex flex-col items-center justify-items-center justify-center"
  >
    <img
      src="../public/logo-counting.svg"
      class="w-96 h-96 mb-24 ml-4"
      alt=""
    />
    <h1 class="text-white text-7xl font-black">HOŞGELDINIZ!</h1>
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
