<template>
  <div
    class="pet-container"
    :style="{ top: position.y + 'px', left: position.x + 'px' }"
    @mousedown="startDrag"
    @click="handleClick"
    @mousemove="handleMouseMove"
  >
    <div
      class="pet animate-float"
      :class="[expressionClass, { glitch: isGlitching }]"
      :style="{
        width: petSize + 'px',
        height: petSize + 'px',
        backgroundColor: petColor,
      }"
      ref="petRef"
    >
      <div class="pet-face">
        <div class="pet-eyes">
          <div
            class="pet-eye left"
            :style="{
              transform: `rotate(100deg) scale(${eyeScale.left})`,
              height: isBlinking ? blinkHeight : '18px',
            }"
          ></div>
          <div
            class="pet-eye right"
            :style="{
              transform: `rotate(-100deg) scale(${eyeScale.right})`,
              height: isBlinking ? blinkHeight : '18px',
            }"
          ></div>
        </div>
        <!-- <div 
          class="pet-mouth" 
          :class="expression"
          :style="{
            transform: expression === 'angry' ? `rotate(180deg) rotate(${mouthRotation}deg)` : ''
          }"
        ></div> -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from "vue";

// 接收父组件传递的设置
const props = defineProps({
  petSize: {
    type: Number,
    default: 100,
  },
  petColor: {
    type: String,
    default: "#000000",
  },
  animationSpeed: {
    type: Number,
    default: 1,
  },
  expressionFrequency: {
    type: Number,
    default: 5,
  },
  currentExpression: {
    type: String,
    default: "happy",
  },
  randomExpression: {
    type: Boolean,
    default: true,
  },
});

const position = ref({ x: 20, y: 20 });
const expression = ref("happy");
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const isGlitching = ref(false);
const clickCount = ref(0);
const maxClicks = 5; // 最大点击次数，超过后触发故障效果
const expressionInterval = ref<number | null>(null);
const petRef = ref<HTMLElement | null>(null);
const eyeScale = ref({ left: 1, right: 1 });
const mouthRotation = ref(0);
const isBlinking = ref(false);
const blinkHeight = ref("3px");
const blinkInterval = ref<number | null>(null);

const expressions = [
  "happy",
  "sad",
  "angry",
  "surprised",
  "tired",
  "disdain",
  "cute",
  "cute-angry",
];

const expressionClass = computed(() => {
  return `pet-${expression.value}`;
});

const startDrag = (event: MouseEvent) => {
  isDragging.value = true;
  dragStart.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y,
  };
  document.addEventListener("mousemove", onDrag);
  document.addEventListener("mouseup", stopDrag);
};

const onDrag = (event: MouseEvent) => {
  if (isDragging.value) {
    position.value = {
      x: event.clientX - dragStart.value.x,
      y: event.clientY - dragStart.value.y,
    };
  }
};

const stopDrag = () => {
  isDragging.value = false;
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", stopDrag);
  // 只有在随机模式下才会在拖拽结束时切换表情
  if (props.randomExpression) {
    expression.value =
      expressions[Math.floor(Math.random() * expressions.length)];
  }
};

const handleClick = () => {
  // 增加点击计数
  clickCount.value++;

  // 只有在随机模式下才会在点击时切换表情
  if (props.randomExpression) {
    expression.value =
      expressions[Math.floor(Math.random() * expressions.length)];
  }

  // 检查是否超过最大点击次数
  if (clickCount.value > maxClicks) {
    // 触发故障效果
    isGlitching.value = true;

    // 3秒后恢复正常
    setTimeout(() => {
      isGlitching.value = false;
      clickCount.value = 0; // 重置点击计数
    }, 3000);
  }

  // 添加弹跳动画
  const pet = document.querySelector(".pet");
  if (pet) {
    pet.classList.add("pet-bounce");
    setTimeout(() => {
      pet.classList.remove("pet-bounce");
    }, 1000);
  }
};

const handleMouseMove = (event: MouseEvent) => {
  if (expression.value === "angry" && petRef.value) {
    const petRect = petRef.value.getBoundingClientRect();
    const petCenterX = petRect.left + petRect.width / 2;

    // 计算鼠标相对于宠物中心的位置
    const mouseX = event.clientX;
    const distanceFromCenter = mouseX - petCenterX;
    const maxDistance = petRect.width / 2;

    // 计算眼睛缩放比例
    if (distanceFromCenter > 0) {
      // 鼠标在右侧，右眼小，左眼大
      eyeScale.value.right = Math.max(
        0.8,
        1 - distanceFromCenter / (maxDistance * 2)
      );
      eyeScale.value.left = Math.min(
        1.2,
        1 + distanceFromCenter / (maxDistance * 2)
      );
    } else {
      // 鼠标在左侧，左眼小，右眼大
      eyeScale.value.left = Math.max(
        0.8,
        1 + distanceFromCenter / (maxDistance * 2)
      );
      eyeScale.value.right = Math.min(
        1.2,
        1 - distanceFromCenter / (maxDistance * 2)
      );
    }

    // 计算嘴巴旋转角度
    // 鼠标在右侧，嘴巴向右旋转；鼠标在左侧，嘴巴向左旋转
    mouthRotation.value = (distanceFromCenter / maxDistance) * 10; // 最大旋转10度
  }
};

const updateExpression = () => {
  // 定期更新表情，只有在随机模式下才会随机切换
  if (props.randomExpression) {
    expression.value =
      expressions[Math.floor(Math.random() * expressions.length)];
  }
};

const startBlinkAnimation = () => {
  // 清除旧的眨眼定时器
  if (blinkInterval.value) {
    clearInterval(blinkInterval.value);
  }

  // 设置新的眨眼定时器
  blinkInterval.value = window.setInterval(() => {
    if (expression.value === "angry") {
      // 开始眨眼
      isBlinking.value = true;

      // 300ms后结束眨眼
      setTimeout(() => {
        isBlinking.value = false;
      }, 300);
    }
  }, 3000); // 每3秒眨一次眼
};

// 监听currentExpression的变化
watch(
  () => props.currentExpression,
  (newExp) => {
    // 当currentExpression变化时，更新表情
    if (!props.randomExpression) {
      expression.value = newExp;
    }
  }
);

// 监听randomExpression的变化
watch(
  () => props.randomExpression,
  (isRandom) => {
    if (isRandom) {
      // 随机模式，随机设置一个表情
      expression.value =
        expressions[Math.floor(Math.random() * expressions.length)];
    } else {
      // 固定模式，使用设置的表情
      expression.value = props.currentExpression;
    }
  }
);

// 监听表情变化频率的变化
watch(
  () => props.expressionFrequency,
  (newFrequency) => {
    // 清除旧的定时器
    if (expressionInterval.value) {
      clearInterval(expressionInterval.value);
    }
    // 设置新的定时器
    expressionInterval.value = window.setInterval(
      updateExpression,
      newFrequency * 1000
    );
  },
  { immediate: true }
);

onMounted(() => {
  // 初始化表情
  if (props.randomExpression) {
    expression.value =
      expressions[Math.floor(Math.random() * expressions.length)];
  } else {
    expression.value = props.currentExpression;
  }

  // 每expressionFrequency秒更新表情
  expressionInterval.value = window.setInterval(
    updateExpression,
    props.expressionFrequency * 1000
  );

  // 启动眨眼动画
  startBlinkAnimation();
});

onUnmounted(() => {
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", stopDrag);
  // 清除定时器
  if (expressionInterval.value) {
    clearInterval(expressionInterval.value);
  }
  if (blinkInterval.value) {
    clearInterval(blinkInterval.value);
  }
});

// 计算属性需要导入
import { computed } from "vue";
</script>

<style scoped>
.pet {
  width: 100px;
  height: 100px;
  background-color: #000000;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), 0 0 15px rgba(0, 153, 255, 0.5);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border: 2px solid #333;
}

/* 机器人头部细节 */
.pet::before {
  content: "";
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  height: 10px;
  background-color: #333;
  border-radius: 5px;
}

/* 机器人耳机效果 */
.pet::after {
  content: "";
  position: absolute;
  top: -5px;
  left: -10px;
  right: -10px;
  height: 20px;
  background-color: #333;
  border-radius: 10px 10px 0 0;
  z-index: -1;
}

.pet-face {
  width: 80px;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.pet-eyes {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.pet-eye {
  width: 12px;
  height: 18px;
  background-color: #0099ff;
  border-radius: 2px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  animation: eye-blink 3s infinite;
  box-shadow: 0 0 10px rgba(0, 153, 255, 0.8);
}

/* 不同表情的眼睛效果 */
/* 开心表情：两个矩形 */
.pet-happy .pet-eye {
  height: 14px;
  transform: scaleY(0.9);
  animation: eye-happy 2s ease-in-out infinite;
}

/* 悲伤表情：下垂矩形 */
.pet-sad .pet-eye {
  height: 12px;
  transform: translateY(3px) rotate(-5deg);
}

/* 生气表情：旋转椭圆眼睛 */
.pet-angry .pet-eye {
  width: 22px;
  height: 18px;
  background-color: #0099ff;
  border-radius: 18px;
  box-shadow: 0 0 10px rgba(0, 153, 255, 0.8);
  position: relative;
  overflow: hidden;
}

/* 左眼：顺时针 100° */
.pet-angry .pet-eye.left {
  transform: rotate(100deg);
  -webkit-mask: linear-gradient(100deg, transparent 11px, black 12px);
  mask: linear-gradient(100deg, transparent 11px, black 12px);
}

/* 右眼：逆时针 100° */
.pet-angry .pet-eye.right {
  transform: rotate(-100deg);
  -webkit-mask: linear-gradient(-100deg, transparent 11px, black 12px);
  mask: linear-gradient(-100deg, transparent 11px, black 12px);
}

/* 火苗 */
.pet-angry .pet-eye.left::before {
  content: "🔥";
  position: absolute;
  top: -15px;
  left: -12px;
  font-size: 12px;
  z-index: 2;
}

/* 怒气符号 */
.pet-angry .pet-eye.right::before {
  content: "✖";
  position: absolute;
  top: -12px;
  right: -12px;
  color: red;
  font-size: 12px;
  z-index: 2;
}

/* 惊讶表情：大矩形 */
.pet-surprised .pet-eye {
  width: 15px;
  height: 20px;
  animation: eye-surprised 1s ease-in-out infinite;
}

/* 疲惫表情：扁矩形 */
.pet-tired .pet-eye {
  height: 5px;
  opacity: 0.7;
  animation: eye-tired 2s ease-in-out infinite;
}

/* 鄙视表情：斜线条 */
.pet-disdain .pet-eye {
  height: 3px;
  transform: rotate(-30deg);
  animation: eye-disdain 3s ease-in-out infinite;
}

/* 可爱表情：圆形眼睛 */
.pet-cute .pet {
  animation: cute-float 2s ease-in-out infinite;
  border-radius: 15px;
}

.pet-cute .pet-eye {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  animation: eye-cute 2s ease-in-out infinite;
}

/* 可爱生气表情：斜眼 */
.pet-cute-angry .pet {
  animation: cute-angry-shake 0.5s ease-in-out infinite;
  border-radius: 15px;
}

.pet-cute-angry .pet-eye {
  width: 14px;
  height: 10px;
  transform: rotate(20deg);
  animation: eye-cute-angry 1s ease-in-out infinite;
}

/* 眼睛动画 */
@keyframes eye-blink {
  0%,
  90%,
  100% {
    height: 18px;
  }
  95% {
    height: 3px;
  }
}

@keyframes eye-happy {
  0%,
  100% {
    transform: scaleY(0.8) rotate(0deg);
  }
  50% {
    transform: scaleY(1) rotate(5deg);
  }
}

@keyframes eye-angry {
  0%,
  100% {
    transform: scale(1);
  }
  25% {
    transform: scale(1.05);
  }
  75% {
    transform: scale(1.05);
  }
}

@keyframes eye-surprised {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

@keyframes eye-tired {
  0%,
  100% {
    height: 5px;
  }
  50% {
    height: 3px;
  }
}

@keyframes eye-disdain {
  0%,
  100% {
    transform: rotate(-10deg);
  }
  50% {
    transform: rotate(10deg);
  }
}

/* 可爱表情动画 */
@keyframes cute-float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-5px) rotate(2deg);
  }
  75% {
    transform: translateY(-5px) rotate(-2deg);
  }
}

@keyframes eye-cute {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

/* 可爱生气表情动画 */
@keyframes cute-angry-shake {
  0%,
  100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(2deg);
  }
  75% {
    transform: rotate(-2deg);
  }
}

@keyframes eye-cute-angry {
  0%,
  100% {
    transform: rotate(15deg) scale(1);
  }
  50% {
    transform: rotate(15deg) scale(1.1);
  }
}

/* 嘴巴动画 */
@keyframes mouth-cute {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes mouth-cute-angry {
  0%,
  100% {
    transform: rotate(10deg) scale(1);
  }
  50% {
    transform: rotate(10deg) scale(1.1);
  }
}

.pet-mouth {
  width: 25px;
  height: 8px;
  background-color: #0099ff;
  border-radius: 2px;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 0 8px rgba(0, 153, 255, 0.6);
}

.pet-mouth.happy {
  border-radius: 0 0 8px 8px;
  height: 10px;
}

.pet-mouth.sad {
  border-radius: 8px 8px 0 0;
  height: 8px;
}

.pet-mouth.angry {
  width: 20px;
  height: 3px;
  background-color: #0099ff;
  transform: rotate(180deg);
}

.pet-mouth.surprised {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.pet-mouth.tired {
  width: 20px;
  height: 2px;
  background-color: #0099ff;
  border-radius: 1px;
  opacity: 0.6;
}

.pet-mouth.disdain {
  width: 15px;
  height: 3px;
  transform: rotate(-10deg);
}

.pet-mouth.cute {
  width: 18px;
  height: 8px;
  border-radius: 4px;
  animation: mouth-cute 2s ease-in-out infinite;
}

.pet-mouth.cute-angry {
  width: 15px;
  height: 3px;
  transform: rotate(10deg);
  animation: mouth-cute-angry 1s ease-in-out infinite;
}

.pet-happy {
  animation: float 3s ease-in-out infinite;
}

.pet-sad {
  animation: float 4s ease-in-out infinite;
  opacity: 0.8;
}

.pet-angry {
  animation: wiggle 1s ease-in-out infinite;
}

.pet-surprised {
  animation: bounce 1s ease-in-out;
}

.pet-tired {
  animation: float 5s ease-in-out infinite;
  opacity: 0.7;
}

/* 电子故障效果 */
.pet.glitch {
  animation: glitch 0.3s infinite;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 153, 255, 0.7);
}

.pet.glitch::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(0, 153, 255, 0.3),
    transparent
  );
  animation: scan-horizontal 0.5s linear infinite;
}

.pet.glitch::after {
  content: "";
  position: absolute;
  top: -100%;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    180deg,
    transparent,
    rgba(0, 153, 255, 0.3),
    transparent
  );
  animation: scan-vertical 0.7s linear infinite;
}

.pet.glitch .pet-eye,
.pet.glitch .pet-mouth {
  animation: glitch-eyes 0.3s infinite;
  position: relative;
  box-shadow: 0 0 10px rgba(0, 153, 255, 0.8);
}

.pet.glitch .pet-eye::before,
.pet.glitch .pet-mouth::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, #0099ff, transparent);
  animation: scan 0.5s linear infinite;
  opacity: 0.7;
  border-radius: inherit;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes wiggle {
  0%,
  100% {
    transform: rotate(-3deg);
  }
  50% {
    transform: rotate(3deg);
  }
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

@keyframes glitch {
  0% {
    transform: translate(0);
  }
  20% {
    transform: translate(-2px, 2px);
  }
  40% {
    transform: translate(-2px, -2px);
  }
  60% {
    transform: translate(2px, 2px);
  }
  80% {
    transform: translate(2px, -2px);
  }
  100% {
    transform: translate(0);
  }
}

@keyframes glitch-eyes {
  0% {
    transform: translate(0);
    background-color: #0099ff;
  }
  25% {
    transform: translate(-1px, 1px);
    background-color: #ff0000;
  }
  50% {
    transform: translate(0);
    background-color: #00ff00;
  }
  75% {
    transform: translate(1px, -1px);
    background-color: #ffff00;
  }
  100% {
    transform: translate(0);
    background-color: #0099ff;
  }
}

@keyframes scan {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes scan-horizontal {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(200%);
  }
}

@keyframes scan-vertical {
  0% {
    transform: translateY(-100%);
  }
  100% {
    transform: translateY(200%);
  }
}

.pet-bounce {
  animation: bounce 1s ease-in-out;
}
</style>
