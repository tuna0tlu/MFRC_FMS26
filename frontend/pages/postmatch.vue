<template>
  <div>
    <h1
      class="absolute w-full text-center text-yellow-500 left-0 top-40 text-7xl font-black tracking-widest"
      v-show="showTieText"
    >
      TIE
    </h1>
    <div class="flex justify-center items-center h-screen w-full">
      <!-- RED TEAMS -->
      <div class="flex flex-col h-2/3 justify-around ml-20 mb-36">
        <template v-for="(team, keyVal) in matchStore.postMatch.redTeams">
          <TeamSignBeforeMatch
            alliance="red"
            :teamName="team.name"
            :teamNumber="'' + team.id"
          ></TeamSignBeforeMatch>
        </template>
      </div>
      <!-- RED TEAMS END -->
      <div
        class="flex flex-col items-center w-2/3 h-1/2 justify-around gap-5 mb-44 lg:h-1/2 lg:mb-36"
      >
<!--        SCORE SHOW INTERFACE-->
        <div
          class="flex w-2/3 flex-row items-center justify-between"
          v-for="(scoreName, index) in matchStore.postMatch.pointTypes"
          :key="index"
          :class="{'anvil-drop': true}"
          :style="{ 'animation-delay': `${index * 0.8}s` }"
        >
          <div
            class="flex bg-frc-red-light h-28 w-24 rounded-lg items-center justify-center translate-x-2 -z-10 anvil-drop red-point"
            :style="{ 'animation-delay': `${index * 0.8 + 0.1}s`, 'height': '7.5rem', 'width': '7rem' }"
          >
            <h1 class="font-bold text-5xl text-white">
              {{ matchStore.postMatch.redPoints[index] }}
            </h1>
          </div>
          <div
            class="flex bg-white h-32 rounded-xl w-full justify-center items-center anvil-drop score-name"
            :style="{ 'animation-delay': `${index * 0.8 + 0.2}s`, 'height': '9rem' }"
          >
            <h1 class="text-5xl text-black text-center w-full font-semibold">
              {{ scoreName }}
            </h1>
          </div>
          <div
            class="flex bg-frc-blue-light h-28 w-24 rounded-lg items-center justify-center -translate-x-2 -z-10 anvil-drop blue-point"
            :style="{ 'animation-delay': `${index * 0.8 + 0.3}s`, 'height': '7.5rem', 'width': '7rem' }"
          >
            <h1 class="font-bold text-5xl text-white">
              {{ matchStore.postMatch.bluePoints[index] }}
            </h1>
          </div>
        </div>
<!--        END SCORE SHOW INTERFACE-->
      </div>
      <!-- BLUE TEAMS -->
      <div class="flex flex-col h-2/3 justify-around mr-20 mb-36">
        <template v-for="(team, keyVal) in matchStore.postMatch.blueTeams">
          <TeamSignBeforeMatch
            alliance="blue"
            :teamName="team.name"
            :teamNumber="'' + team.id"
          ></TeamSignBeforeMatch>
        </template>
      </div>
      <!-- BLUE TEAMS END -->
      <!-- SCORES SECTION  -->
      <div
        class="w-full h-min flex flex-row items-center justify-center absolute bottom-0 shadow-2xl"
      >
        <!-- red team bg -->
        <div
          class="bg-frc-red-light w-1/2 left-0 bottom-0 h-1/3 absolute -z-10"
          ref="redWinnerBg"
        ></div>
        <template>
          <h1
              v-show="matchStore.postMatch.winner !== 0"
              class="winner-text"
              :class="matchStore.postMatch.winner === 1 ? 'winner-red' : 'winner-blue'"
          >
            WINNER
          </h1>
        </template>

        <!-- SCORE/TROPHY ON RED SVG -->
        <div class="absolute bottom-4 w-[367px] flex justify-center items-center z-10" style="left: 33%">
          <Icon 
            icon="mdi:trophy"
            :class="[
              redTrophyClass,
              'text-[7rem] mr-8 anvil-drop',
              'transition-opacity duration-1000'
            ]"
            :style="{ 'animation-delay': `${(matchStore.postMatch.pointTypes.length) * 0.8}s` }"
          />
          <h1
            ref="redScore"
            class="text-9xl text-white font-extrabold anvil-drop"
            :style="{ 'animation-delay': `${(matchStore.postMatch.pointTypes.length) * 0.8}s`, 'font-size': '6.5rem' }"
            :data-final-score="matchStore.postMatch.redScore"
          >
            0
          </h1>
        </div>
        <svg width="367" height="117" viewBox="0 0 367 117" fill="none">
          <path d="M92.3679 0H367V117H0.490967L92.3679 0Z" fill="#EC1D25" />
        </svg>
        <!-- blue team bg -->
        <div
          class="bg-frc-blue-light w-1/2 right-0 bottom-0 h-1/3 absolute -z-10"
          ref="blueWinnerBg"
          :class="{ 'winner-bg': matchStore.postMatch.winner == 2 }"
        ></div>
        <svg width="367" height="117" viewBox="0 0 367 117" fill="none">
          <path d="M274.749 0H0V117H367L274.749 0Z" fill="#0066B3" />
        </svg>
        <!-- SCORE/TROPHY ON BLUE SVG -->
        <div class="absolute bottom-4 w-[367px] flex justify-center items-center z-10" style="right: 33%">
          <h1
            ref="blueScore"
            class="text-9xl text-white font-extrabold anvil-drop"
            :style="{ 'animation-delay': `${(matchStore.postMatch.pointTypes.length + 1) * 0.8}s`, 'font-size': '6.5rem' }"
            :data-final-score="matchStore.postMatch.blueScore"
          >
            0
          </h1>
          <Icon 
            icon="mdi:trophy"
            :class="[
              blueTrophyClass,
              'text-[7rem] ml-8 anvil-drop',
              'transition-opacity duration-1000'
            ]"
            :style="{ 'animation-delay': `${(matchStore.postMatch.pointTypes.length + 1) * 0.8}s` }"
          />
        </div>
      </div>
      <!-- SCORES SECTION END  -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMatchStore } from "@/stores/useMatchStore";
import { onMounted, ref, watch, computed } from 'vue';
import { Icon } from '@iconify/vue';

const matchStore = useMatchStore();
const scoreBlocks = ref<HTMLElement[]>([]);
const redScore = ref<HTMLElement | null>(null);
const blueScore = ref<HTMLElement | null>(null);
const redWinnerBg = ref<HTMLElement | null>(null);
const blueWinnerBg = ref<HTMLElement | null>(null);

// Trophy and TIE reveal states
const showRedTrophy = ref(false);
const showBlueTrophy = ref(false);
const showTieText = ref(false);
const redScoreDone = ref(false);
const blueScoreDone = ref(false);

const redTrophyClass = computed(() => {
  if (!showRedTrophy.value) return 'text-transparent opacity-0';
  return matchStore.postMatch.winner === 1 ? 'text-yellow-500 opacity-100' : 'text-transparent opacity-100';
});
const blueTrophyClass = computed(() => {
  if (!showBlueTrophy.value) return 'text-transparent opacity-0';
  return matchStore.postMatch.winner === 2 ? 'text-yellow-500 opacity-100' : 'text-transparent opacity-100';
});

onMounted(() => {

  console.log("POSTMATCH ONMOUNTED");
  // Generate random animation for winner text
  const winnerAnimationName = generateRandomWinnerAnimation();

  // Winner animation duration (in milliseconds)
  const winnerAnimationDuration = 8000; // 8 seconds

  // Get the winner element
  const winnerElement = document.querySelector('.winner-animation');
  if (winnerElement && winnerElement instanceof HTMLElement) {
    // Apply the random animation
    winnerElement.style.animation = `${winnerAnimationName} ${winnerAnimationDuration}ms ease-in-out forwards`;
  }

  // Calculate when the winner animation will end
  const winnerAnimationStartTime = 500; // Start after a short delay
  const winnerAnimationEndTime = winnerAnimationStartTime + winnerAnimationDuration;

  // Show the winner element when animation starts
  if (winnerElement && winnerElement instanceof HTMLElement) {
    winnerElement.style.opacity = '0'; // Initially hidden
    setTimeout(() => {
      winnerElement.style.opacity = '1'; // Show when animation starts
    }, winnerAnimationStartTime);
  }

  // Get the score elements and their final scores
  const scoreElements = [redScore.value, blueScore.value].filter((el): el is HTMLElement => el !== null);
  let maxScore = 0;

  // Find the maximum score
  scoreElements.forEach(element => {
    const finalScore = parseInt(element.getAttribute('data-final-score') || '0');
    maxScore = Math.max(maxScore, finalScore);
  });

  // Calculate the delay for score animations to end around the same time as the winner animation
  const scoreAnimationDuration = 3000; // 3 seconds for score animation
  const scoreAnimationStartDelay = winnerAnimationEndTime - scoreAnimationDuration - 500; // Start so they end together (with a small buffer)

  // Apply anvil-drop animation to score blocks with calculated delay
  if (scoreBlocks.value && scoreBlocks.value.length > 0) {
    const totalScoreBlocks = scoreBlocks.value.length;
    const blockAnimationDuration = 2000; // 2 seconds for block animation

    scoreBlocks.value.forEach((block, index) => {
      if (block && block instanceof HTMLElement) {
        // Calculate delay for each block to ensure they all finish around the same time as the winner animation
        const blockDelay = scoreAnimationStartDelay - ((totalScoreBlocks - index - 1) * 800);

        // Force reflow to ensure animation works
        void block.offsetWidth;
        // Apply anvil-drop animation with calculated delay
        block.style.animation = `anvil-drop ${blockAnimationDuration}ms cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards`;
        block.style.animationDelay = `${Math.max(0, blockDelay)}ms`;

        // Apply animation to all child elements within the SCORE SHOW INTERFACE
        const redPointElement = block.querySelector('.bg-frc-red-light');
        const scoreNameElement = block.querySelector('.bg-white');
        const bluePointElement = block.querySelector('.bg-frc-blue-light');

        // Apply animation to red point element
        if (redPointElement && redPointElement instanceof HTMLElement) {
          void redPointElement.offsetWidth;
          redPointElement.style.animation = `anvil-drop ${blockAnimationDuration}ms cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards`;
          redPointElement.style.animationDelay = `${Math.max(0, blockDelay + 100)}ms`;
          // Increase size for more impact
          redPointElement.style.height = '7.5rem'; // Increased from h-28 (7rem)
          redPointElement.style.width = '7rem'; // Increased from w-24 (6rem)
        }

        // Apply animation to score name element
        if (scoreNameElement && scoreNameElement instanceof HTMLElement) {
          void scoreNameElement.offsetWidth;
          scoreNameElement.style.animation = `anvil-drop ${blockAnimationDuration}ms cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards`;
          scoreNameElement.style.animationDelay = `${Math.max(0, blockDelay + 200)}ms`;
          // Increase size for more impact
          scoreNameElement.style.height = '9rem'; // Increased from h-32 (8rem)
        }

        // Apply animation to blue point element
        if (bluePointElement && bluePointElement instanceof HTMLElement) {
          void bluePointElement.offsetWidth;
          bluePointElement.style.animation = `anvil-drop ${blockAnimationDuration}ms cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards`;
          bluePointElement.style.animationDelay = `${Math.max(0, blockDelay + 300)}ms`;
          // Increase size for more impact
          bluePointElement.style.height = '7.5rem'; // Increased from h-28 (7rem)
          bluePointElement.style.width = '7rem'; // Increased from w-24 (6rem)
        }
      }
    });
  }

  // Start the score animations after the calculated delay
  setTimeout(() => {
    // Animate red score
    if (redScore.value) {
      const redFinalScore = parseInt(redScore.value.getAttribute('data-final-score') || '0');
      animateValueWithPizazz(redScore.value, 0, redFinalScore, scoreAnimationDuration, () => {
        redScoreDone.value = true;
      });
    }

    // Animate blue score
    if (blueScore.value) {
      const blueFinalScore = parseInt(blueScore.value.getAttribute('data-final-score') || '0');
      animateValueWithPizazz(blueScore.value, 0, blueFinalScore, scoreAnimationDuration, () => {
        blueScoreDone.value = true;
      });
    }
  }, scoreAnimationStartDelay);

  // Reveal trophy/TIE only after both score animations are done
  watch([redScoreDone, blueScoreDone], ([redDone, blueDone]) => {
    if (redDone && blueDone) {
      setTimeout(() => {
        if (matchStore.postMatch.winner === 1) {
          showRedTrophy.value = true;
        } else if (matchStore.postMatch.winner === 2) {
          showBlueTrophy.value = true;
        } else if (matchStore.postMatch.winner === 0) {
          showTieText.value = true;
        }
      }, 500);
    }
  });

  // Delay the yellow bar animation until after all animations including winner animation
  setTimeout(() => {
    // Get winner background elements
    const winnerBgElements = [redWinnerBg.value, blueWinnerBg.value]
      .filter((el): el is HTMLElement => el !== null && el.classList.contains('winner-bg'));

    // Apply background animation
    winnerBgElements.forEach(element => {
      element.classList.add('bg-animation');
    });
  }, winnerAnimationEndTime + 500); // Apply shortly after winner animation completes
});

// Animation function with pizazz - goes to 100 first, then to actual score
function animateValueWithPizazz(element: Element, start: number, end: number, totalDuration: number, onDone?: () => void) {
  if (!(element instanceof HTMLElement)) return;

  const initialDuration = totalDuration * 0.3; // 30% of total time to reach 100
  const finalDuration = totalDuration * 0.7; // 70% of total time to reach final score

  // First phase: animate to 100 quickly
  animateValuePhase(element, start, 100, initialDuration, () => {
    // Second phase: animate to actual final score
    animateValuePhase(element, 100, end, finalDuration, onDone);
  });
}

// Helper function to animate a single phase
function animateValuePhase(element: Element, start: number, end: number, duration: number, callback?: () => void) {
  if (!(element instanceof HTMLElement)) return;

  let startTimestamp: number | null = null;

  const step = (timestamp: number) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);

    // Ensure both scores increment at exactly the same rate
    // Use Math.floor to ensure integer values
    const currentValue = Math.floor(start + (end - start) * progress);

    // Set the text content safely
    if (element.textContent !== null) {
      element.textContent = currentValue.toString();
    }

    if (progress < 1) {
      window.requestAnimationFrame(step);
    } else {
      if (element.textContent !== null) {
        element.textContent = end.toString();
      }
      if (callback) callback();
    }
  };
  window.requestAnimationFrame(step);
}

// Function to generate random animation keyframes for the winner text
function generateRandomWinnerAnimation() {
  // List of vibrant colors for the animation
  const colors = [
    '#FF4500', // OrangeRed
    '#FF1493', // DeepPink
    '#9400D3', // DarkViolet
    '#00BFFF', // DeepSkyBlue
    '#32CD32', // LimeGreen
    '#FF8C00', // DarkOrange
    '#FF00FF', // Magenta
    '#1E90FF', // DodgerBlue
    '#ADFF2F', // GreenYellow
    '#FF6347', // Tomato
    '#DA70D6', // Orchid
    '#00CED1', // DarkTurquoise
    '#FFA500', // Orange
    '#8A2BE2', // BlueViolet
    '#7CFC00', // LawnGreen
    '#FF69B4', // HotPink
    '#20B2AA', // LightSeaGreen
    '#FFD700'  // Gold
  ];

  // Create a style element for the dynamic keyframes
  const styleElement = document.createElement('style');
  document.head.appendChild(styleElement);

  // Generate random keyframes
  let keyframes = `
    @keyframes random-winner {
      0% {
        transform: translateX(50vw) translateY(-50vh) scale(3) rotate(0deg);
        opacity: 0;
        color: #FFD700;
      }
  `;

  // Generate random positions for each keyframe (5% to 95%)
  for (let i = 5; i <= 95; i += 5) {
    const x = Math.floor(Math.random() * 80) + 10; // Random X position (10% to 90% of viewport width)
    const y = Math.floor(Math.random() * 100) - 50; // Random Y position (-50vh to 50vh)
    const scale = (Math.random() * 1.5) + 1; // Random scale (1 to 2.5)
    const rotate = Math.floor(Math.random() * 720) - 360; // Random rotation (-360deg to 360deg)
    const colorIndex = Math.floor(Math.random() * colors.length);

    keyframes += `
      ${i}% {
        transform: translateX(${x}vw) translateY(${y}vh) scale(${scale}) rotate(${rotate}deg);
        opacity: 1;
        color: ${colors[colorIndex]};
      }
    `;
  }

  // Final keyframe - always go to the winning alliance side
  keyframes += `
      100% {
        transform: translateX(var(--settle-x)) translateY(0) scale(1) rotate(0deg);
        opacity: 1;
        color: #FFD700;
      }
    }
  `;

  // Add the keyframes to the style element
  styleElement.textContent = keyframes;

  return 'random-winner';
}
</script>

<style scoped>
/* Prevent scrollbars when elements go out of frame */
html, body {
  overflow-x: hidden;
  overflow-y: hidden;
}
.winner-text {
  position: absolute;
  bottom: 16%;
  left: 50%;
  /* start truly centered and small */
  transform: translateX(-50%) scale(0.5);
  color: #FFD700;
  font-size: 9rem;
  opacity: 0;
  text-shadow: 0 0 10px rgba(255,255,255,0.7);

  /* shorthand: name duration timing‑function delay + fill‑mode */
  animation: slide-winner 1.5s ease-out 5s forwards;
}

/* pick your slide‑out distance (adjust as you like) */
.winner-red  { --offset-x: -40vw; }
.winner-blue { --offset-x:  40vw; }

@keyframes slide-winner {
  0% {
    opacity: 0;
    transform: translateX(-50%) scale(0.5);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) scale(1.2);
  }
  100% {
    opacity: 1;
    /* translateX(-50%) (center) + var(--offset-x) (left or right) */
    transform: translateX(calc(-50% + var(--offset-x))) scale(1);
  }
}

.winner-animation {
  --settle-x: -10px;
  opacity: 0; /* Initially hidden */
  /* Animation is now set dynamically in JavaScript */
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
  transition: color 0.3s ease, opacity 0.3s ease;
}

/* Anvil drop animation - more impactful with stronger bounce and shake effect */
@keyframes anvil-drop {
  0% {
    transform: translateY(-2000px) scale(1.5);
    opacity: 0;
    filter: drop-shadow(0 0 0 rgba(0,0,0,0));
  }
  40% {
    transform: translateY(-1000px) scale(1.3);
    opacity: 0.5;
    filter: drop-shadow(0 0 10px rgba(0,0,0,0.3));
  }
  70% {
    transform: translateY(-300px) scale(1.2);
    opacity: 0.8;
    filter: drop-shadow(0 0 15px rgba(0,0,0,0.4));
  }
  85% {
    transform: translateY(40px) scale(1.1) rotate(2deg);
    opacity: 1;
    filter: drop-shadow(0 0 20px rgba(0,0,0,0.5));
  }
  90% {
    transform: translateY(-20px) scale(1.05) rotate(-1deg);
    opacity: 1;
    filter: drop-shadow(0 0 25px rgba(0,0,0,0.6));
  }
  95% {
    transform: translateY(10px) scale(1.02) rotate(1deg);
    opacity: 1;
    filter: drop-shadow(0 0 20px rgba(0,0,0,0.5));
  }
  98% {
    transform: translateY(-5px) scale(1.01) rotate(-0.5deg);
    opacity: 1;
    filter: drop-shadow(0 0 15px rgba(0,0,0,0.4));
  }
  100% {
    transform: translateY(0) scale(1) rotate(0);
    opacity: 1;
    filter: drop-shadow(0 0 10px rgba(0,0,0,0.3));
  }
}

.anvil-drop {
  opacity: 0; /* Initially hidden */
  animation: anvil-drop 2s cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards;
  transform-origin: center;
}

/* Remove fade-trophy transition, now handled by utility classes */
</style>
