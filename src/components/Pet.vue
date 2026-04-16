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
          <div class="pet-eye left" :style="leftEyeStyle"></div>
          <div class="pet-eye right" :style="rightEyeStyle"></div>
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

// 计算眼睛样式
const leftEyeStyle = computed(() => {
  // 只有开心和生气表情才应用动态transform
  if (expression.value === "happy" || expression.value === "angry") {
    return {
      transform:
        expression.value === "angry"
          ? `rotate(100deg) scale(${eyeScale.value.left}) translate(${eyeOffset.value.x}px, ${eyeOffset.value.y}px)`
          : `scale(${eyeScale.value.left}) translate(${eyeOffset.value.x}px, ${eyeOffset.value.y}px)`,
      height: isBlinking.value ? blinkHeight.value : "18px",
    };
  }
  // 其他表情使用默认样式
  return {
    height: isBlinking.value ? blinkHeight.value : "18px",
  };
});

const rightEyeStyle = computed(() => {
  // 只有开心和生气表情才应用动态transform
  if (expression.value === "happy" || expression.value === "angry") {
    return {
      transform:
        expression.value === "angry"
          ? `rotate(-100deg) scale(${eyeScale.value.right}) translate(${eyeOffset.value.x}px, ${eyeOffset.value.y}px)`
          : `scale(${eyeScale.value.right}) translate(${eyeOffset.value.x}px, ${eyeOffset.value.y}px)`,
      height: isBlinking.value ? blinkHeight.value : "18px",
    };
  }
  // 其他表情使用默认样式
  return {
    height: isBlinking.value ? blinkHeight.value : "18px",
  };
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
  // 跟踪鼠标位置，用于追逐功能
  window.mouseX = event.clientX;
  window.mouseY = event.clientY;

  // 检测鼠标是否绕着宠物绕圈
  if (petRef.value) {
    const petRect = petRef.value.getBoundingClientRect();
    // 扩展检测区域，以宠物为中心，半径为宠物宽度的2倍
    const detectionRadius = petRect.width * 2;
    const petCenterX = petRect.left + petRect.width / 2;
    const petCenterY = petRect.top + petRect.height / 2;

    // 计算鼠标到宠物中心的距离
    const distance = Math.sqrt(
      Math.pow(event.clientX - petCenterX, 2) +
        Math.pow(event.clientY - petCenterY, 2)
    );

    // 如果鼠标在检测区域内
    if (distance <= detectionRadius) {
      // 计算鼠标相对于宠物中心的角度
      const angle = Math.atan2(
        event.clientY - petCenterY,
        event.clientX - petCenterX
      );

      // 保存鼠标路径点
      mousePathPoints.value.push({ x: event.clientX, y: event.clientY });
      // 限制保存的点数
      if (mousePathPoints.value.length > MAX_PATH_POINTS) {
        mousePathPoints.value.shift();
      }

      // 检测是否完成一圈
      if (lastAngle !== 0) {
        const angleDiff = angle - lastAngle;
        // 检测是否完成了一个完整的圈（角度变化超过2π）
        if (Math.abs(angleDiff) > Math.PI) {
          // 调整角度差，考虑360度循环
          const adjustedDiff =
            angleDiff > 0 ? angleDiff - 2 * Math.PI : angleDiff + 2 * Math.PI;
          if (Math.abs(adjustedDiff) < 1) {
            // 防止误检测
            // 增加圈数计数
            currentCircles++;

            // 检查是否达到了要求的圈数
            if (
              currentCircles >= REQUIRED_CIRCLES &&
              !isChasing.value &&
              !isMoving.value &&
              !isChaseScheduled.value
            ) {
              // 避免在延迟期间重复排队追逐
              currentCircles = 0;
              lastAngle = 0;
              REQUIRED_CIRCLES = Math.floor(Math.random() * 3) + 1;
              startChasing();
            }
          }
        }
      }

      // 更新最后角度
      lastAngle = angle;

      // 只有在开心表情时才触发盯着鼠标的动作
      if (expression.value === "happy") {
        // 眼睛盯着鼠标的动作
        // 计算鼠标相对于宠物中心的位置
        const distanceFromCenterX = event.clientX - petCenterX;
        const distanceFromCenterY = event.clientY - petCenterY;
        const maxDistance = petRect.width / 2;

        // 计算眼睛位置偏移（尺度要小）
        eyeOffset.value.x = (distanceFromCenterX / maxDistance) * 3; // 最大偏移3像素
        eyeOffset.value.y = (distanceFromCenterY / maxDistance) * 2; // 最大偏移2像素

        // 计算眼睛缩放（尺度要小）
        if (distanceFromCenterX > 0) {
          // 鼠标在右侧，右眼不动，左眼稍微放大
          eyeScale.value.right = 1; // 右边眼睛不动
          eyeScale.value.left = Math.min(
            1.1,
            1 + Math.abs(distanceFromCenterX) / (maxDistance * 5)
          ); // 左边眼睛稍微放大
        } else {
          // 鼠标在左侧，左眼不动，右眼稍微放大
          eyeScale.value.left = 1; // 左边眼睛不动
          eyeScale.value.right = Math.min(
            1.1,
            1 + Math.abs(distanceFromCenterX) / (maxDistance * 5)
          ); // 右边眼睛稍微放大
        }
      } else {
        // 其他表情时保持原样
        eyeOffset.value = { x: 0, y: 0 };
        eyeScale.value = { left: 1, right: 1 };
      }
    } else {
      // 鼠标离开检测区域，重置检测
      mousePathPoints.value = [];
      currentCircles = 0;
      lastAngle = 0;
      // 只在开心表情时才重置眼睛状态
      if (expression.value === "happy") {
        eyeOffset.value = { x: 0, y: 0 };
        eyeScale.value = { left: 1, right: 1 };
      }
      // 重新随机所需圈数
      REQUIRED_CIRCLES = Math.floor(Math.random() * 3) + 1;
    }
  }

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

  // 开始自主移动
  startMoving();

  // 添加鼠标移动事件监听器，跟踪鼠标位置
  document.addEventListener("mousemove", handleMouseMove);
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
  if (moveInterval.value) {
    clearTimeout(moveInterval.value);
  }
  // 清除动画帧
  if (chaseAnimationId.value) {
    cancelAnimationFrame(chaseAnimationId.value);
  }
  // 清除鼠标移动事件监听器
  document.removeEventListener("mousemove", handleMouseMove);
});

// 自主移动相关变量
const isMoving = ref(false);
const moveInterval = ref<number | null>(null);
const isChasing = ref(false);
const isChaseScheduled = ref(false);
const chaseTimeoutId = ref<number | null>(null);
const chaseAnimationId = ref<number | null>(null);

// 鼠标绕圈检测相关变量
const mousePathPoints = ref<{ x: number; y: number }[]>([]);
const MAX_PATH_POINTS = 50; // 最多保存50个点
let REQUIRED_CIRCLES = Math.floor(Math.random() * 2) + 2; // 固定2-3圈
let currentCircles = 0;
let lastAngle = 0;

// 开始自主移动
const startMoving = () => {
  if (moveInterval.value) {
    clearInterval(moveInterval.value);
  }

  // 随机时间间隔触发移动
  const scheduleNextMove = () => {
    if (isChasing.value) return; // 如果正在追逐，不安排下一次移动

    // 随机时间间隔 2-5秒
    const randomInterval = 2000 + Math.random() * 3000;

    moveInterval.value = window.setTimeout(() => {
      if (!isMoving.value && !isChasing.value) {
        // 10%的概率触发追逐鼠标
        if (Math.random() < 0.1) {
          startChasing();
        } else {
          isMoving.value = true;
          // 随机移动3-5步
          const stepsToMove = 3 + Math.floor(Math.random() * 3);
          movePetSteps(stepsToMove);
        }
      } else {
        // 如果正在移动或追逐，重新安排
        scheduleNextMove();
      }
    }, randomInterval);
  };

  scheduleNextMove();
};

// 移动宠物（一次移动一步）
const movePet = (onComplete) => {
  // 如果已经在追逐中，直接完成
  if (isChasing.value) {
    if (onComplete) {
      onComplete();
    }
    return;
  }

  // 计算新位置
  const screenWidth = window.innerWidth;
  const screenHeight = window.innerHeight;
  const petWidth = props.petSize;
  const petHeight = props.petSize;

  // 限制移动距离，每次移动不超过80像素，让宠物看起来像是在走而不是在飞
  const maxDistance = 80;
  // 随机移动方向
  const angle = Math.random() * Math.PI * 2;
  // 随机移动距离
  const distance = Math.random() * maxDistance;
  // 计算目标位置
  let targetX = position.value.x + Math.cos(angle) * distance;
  let targetY = position.value.y + Math.sin(angle) * distance;

  // 确保目标位置在屏幕范围内
  targetX = Math.max(0, Math.min(screenWidth - petWidth, targetX));
  targetY = Math.max(0, Math.min(screenHeight - petHeight, targetY));

  // 计算实际移动距离
  const distanceX = targetX - position.value.x;
  const distanceY = targetY - position.value.y;
  const totalDistance = Math.sqrt(
    distanceX * distanceX + distanceY * distanceY
  );

  // 计算移动步数，确保足够多的步数让移动看起来流畅
  const steps = Math.ceil(totalDistance / 3);
  let currentStep = 0;

  // 保存初始位置
  const startX = position.value.x;
  const startY = position.value.y;

  // 移动过程中切换到开心的表情
  expression.value = "happy";

  // 开始移动
  const moveStep = () => {
    // 如果在移动过程中触发了追逐，立即停止移动
    if (isChasing.value) {
      isMoving.value = false;
      return;
    }

    if (currentStep < steps) {
      currentStep++;

      // 计算当前位置
      const progress = currentStep / steps;

      // 使用缓动函数，让移动更自然
      const easeProgress = 1 - Math.pow(1 - progress, 3);

      // 计算当前位置（带跳跃效果）- 增强跳跃感，让宠物duangduang地跳
      const jumpHeight = 20 * Math.sin(progress * Math.PI * 1.5);

      // 从初始位置开始计算，确保一步一步移动
      position.value = {
        x: startX + distanceX * easeProgress,
        y: startY + distanceY * easeProgress - jumpHeight,
      };

      // 继续下一步
      requestAnimationFrame(moveStep);
    } else {
      // 添加落地时的果冻效果
      addJellyEffect();

      // 移动完成，调用回调
      if (onComplete) {
        onComplete();
      }
    }
  };

  // 开始移动
  moveStep();
};

// 移动宠物多步
const movePetSteps = (totalSteps) => {
  let currentStep = 0;

  const stepComplete = () => {
    currentStep++;
    if (currentStep < totalSteps && !isChasing.value) {
      // 继续移动下一步
      setTimeout(() => {
        movePet(stepComplete);
      }, 200); // 两步之间的短暂停顿
    } else {
      // 所有步骤完成
      isMoving.value = false;

      // 随机切换到其他表情
      if (props.randomExpression) {
        setTimeout(() => {
          expression.value =
            expressions[Math.floor(Math.random() * expressions.length)];
        }, 1000);
      }

      // 安排下一次移动
      startMoving();
    }
  };

  // 开始第一步移动
  movePet(stepComplete);
};

// 添加轻微落地效果（减少果冻效果强度）
const addJellyEffect = () => {
  const pet = document.querySelector(".pet");
  if (pet) {
    pet.classList.add("pet-jelly-light");
    setTimeout(() => {
      pet.classList.remove("pet-jelly-light");
    }, 300); // 缩短持续时间
  }
};

// 眼睛位置偏移
const eyeOffset = ref({ x: 0, y: 0 });

// 执行一步追逐（固定距离，确保一致速度）
const performChaseStep = (onComplete) => {
  // 如果已经不在追逐中，直接完成
  if (!isChasing.value) {
    if (onComplete) onComplete();
    return;
  }

  // 获取鼠标位置
  const mousePos = getMousePosition();
  if (!mousePos) {
    if (onComplete) onComplete();
    return;
  }

  // 计算目标位置（鼠标中心）
  const targetX = mousePos.x - props.petSize / 2;
  const targetY = mousePos.y - props.petSize / 2;

  // 计算方向和距离
  const dx = targetX - position.value.x;
  const dy = targetY - position.value.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // 如果距离太近，停止追逐
  if (distance < 10) {
    if (onComplete) onComplete();
    return;
  }

  // 固定每步移动距离（25像素），步子更大
  const stepDistance = 25;
  const moveDistance = Math.min(stepDistance, distance);

  // 计算这一步的目标位置
  const stepX = position.value.x + (dx / distance) * moveDistance;
  const stepY = position.value.y + (dy / distance) * moveDistance;

  // 确保在屏幕范围内
  const screenWidth = window.innerWidth;
  const screenHeight = window.innerHeight;
  const finalX = Math.max(0, Math.min(screenWidth - props.petSize, stepX));
  const finalY = Math.max(0, Math.min(screenHeight - props.petSize, stepY));

  // 保存初始位置
  const startX = position.value.x;
  const startY = position.value.y;

  // 计算这一步的距离
  const stepDx = finalX - startX;
  const stepDy = finalY - startY;

  // 使用更平滑的动画（增加步数，让每步更慢）
  const animationSteps = 12; // 增加步数使动画更慢
  let currentStep = 0;

  const animateStep = () => {
    if (!isChasing.value) {
      if (onComplete) onComplete();
      return;
    }

    currentStep++;
    const progress = currentStep / animationSteps;

    // 使用更平滑的缓动函数
    const easeProgress =
      progress < 0.5
        ? 2 * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 2) / 2;

    // 小幅跳跃效果，更像走路（和走路保持一致的跳跃高度）
    const jumpHeight = 20 * Math.sin(progress * Math.PI);

    // 更新位置
    position.value = {
      x: startX + stepDx * easeProgress,
      y: startY + stepDy * easeProgress - jumpHeight,
    };

    if (currentStep < animationSteps) {
      requestAnimationFrame(animateStep);
    } else {
      // 一步完成，添加轻微落地效果
      addJellyEffect();
      if (onComplete) onComplete();
    }
  };

  // 开始动画
  animateStep();
};

// 开始追逐鼠标
const startChasing = () => {
  // 如果已经在追逐中或已安排过追逐，不要重复触发
  if (isChasing.value || isChaseScheduled.value) return;

  isChaseScheduled.value = true;

  // 清理之前的移动计时器
  if (moveInterval.value) {
    clearTimeout(moveInterval.value);
    moveInterval.value = null;
  }

  // 2秒后开始追逐
  chaseTimeoutId.value = window.setTimeout(() => {
    isChaseScheduled.value = false;
    chaseTimeoutId.value = null;
    isChasing.value = true;
    expression.value = "happy";

    // 追逐持续时间（3-5秒）
    const chaseDuration = 3000 + Math.random() * 2000;
    const startTime = Date.now();

    // 追逐循环，使用固定的时间间隔确保丝滑
    const chaseStep = () => {
      if (!isChasing.value) return;

      // 检查是否到达追逐时间
      if (Date.now() - startTime > chaseDuration) {
        stopChasing();
        return;
      }

      // 执行一步追逐
      performChaseStep(() => {
        // 继续下一歩，使用固定间隔（增加间隔让跳跃不要太快）
        setTimeout(chaseStep, 200); // 每200ms一步，让跳跃更慢
      });
    };

    // 开始追逐循环
    chaseStep();
  }, 2000);
};

// 停止追逐
const stopChasing = () => {
  isChasing.value = false;
  isChaseScheduled.value = false;
  if (chaseTimeoutId.value) {
    clearTimeout(chaseTimeoutId.value);
    chaseTimeoutId.value = null;
  }
  // 重置眼睛偏移
  eyeOffset.value = { x: 0, y: 0 };
  // 取消动画帧
  if (chaseAnimationId.value) {
    cancelAnimationFrame(chaseAnimationId.value);
    chaseAnimationId.value = null;
  }
  // 安排下一次移动
  setTimeout(() => {
    startMoving();
  }, 500);
};

// 获取鼠标位置
const getMousePosition = () => {
  let mouseX = 0;
  let mouseY = 0;

  // 检查是否有鼠标移动事件
  if (window.mouseX && window.mouseY) {
    return { x: window.mouseX, y: window.mouseY };
  }

  // 否则返回null
  return null;
};

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
  position: relative;
  overflow: hidden;
  border: 2px solid #333;
}

/* 机器人头部细节
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
/* .pet::after {
  content: "";
  position: absolute;
  top: -5px;
  left: -10px;
  right: -10px;
  height: 20px;
  background-color: #333;
  border-radius: 10px 10px 0 0;
  z-index: -1;
} */

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
  height: 3px;
  width: 15px;
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
    width: 15px;
  }
  50% {
    width: 15px;
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
  animation: glitch 0.35s infinite;
  border-radius: 14px;
  box-shadow: 0 0 18px rgba(255, 255, 255, 0.15),
    0 0 28px rgba(0, 255, 255, 0.25);
  filter: contrast(1.2) saturate(1.3);
  position: relative;
  overflow: hidden;
}

.pet.glitch::before,
.pet.glitch::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  mix-blend-mode: screen;
  opacity: 0.45;
}

.pet.glitch::before {
  background: rgba(255, 0, 64, 0.25);
  transform: translateX(-3px);
  animation: glitch-red 0.35s infinite;
}

.pet.glitch::after {
  background: rgba(0, 232, 255, 0.2);
  transform: translateX(3px);
  animation: glitch-blue 0.35s infinite;
}

.pet.glitch .pet-eye,
.pet.glitch .pet-mouth {
  animation: glitch-eyes 0.25s infinite;
  position: relative;
  box-shadow: 0 0 16px rgba(255, 0, 128, 0.25), 0 0 16px rgba(0, 232, 255, 0.25);
}

.pet.glitch .pet-eye::before,
.pet.glitch .pet-mouth::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  animation: scan 0.4s linear infinite;
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

@keyframes glitch-red {
  0%,
  100% {
    transform: translateX(-3px) skewX(-6deg);
    clip-path: inset(0 0 70% 0);
  }
  20% {
    transform: translateX(4px) skewX(4deg);
    clip-path: inset(10% 0 45% 0);
  }
  40% {
    transform: translateX(-2px) skewX(-4deg);
    clip-path: inset(50% 0 15% 0);
  }
  60% {
    transform: translateX(3px) skewX(5deg);
    clip-path: inset(15% 0 55% 0);
  }
  80% {
    transform: translateX(-4px) skewX(-5deg);
    clip-path: inset(60% 0 10% 0);
  }
}

@keyframes glitch-blue {
  0%,
  100% {
    transform: translateX(3px) skewX(6deg);
    clip-path: inset(40% 0 20% 0);
  }
  20% {
    transform: translateX(-3px) skewX(-5deg);
    clip-path: inset(5% 0 60% 0);
  }
  40% {
    transform: translateX(2px) skewX(4deg);
    clip-path: inset(30% 0 35% 0);
  }
  60% {
    transform: translateX(-4px) skewX(-6deg);
    clip-path: inset(55% 0 10% 0);
  }
  80% {
    transform: translateX(4px) skewX(5deg);
    clip-path: inset(20% 0 50% 0);
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
  0%,
  100% {
    transform: translate(0);
  }
  15% {
    transform: translate(-3px, 2px) skewX(-3deg);
  }
  30% {
    transform: translate(4px, -2px) skewY(2deg);
  }
  45% {
    transform: translate(-2px, 3px) skewX(4deg);
  }
  60% {
    transform: translate(3px, -3px) skewY(-3deg);
  }
  75% {
    transform: translate(-1px, 2px) skewX(-2deg);
  }
  90% {
    transform: translate(2px, -1px) skewY(2deg);
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

.pet-jelly {
  animation: jelly 0.5s ease-in-out;
}

.pet-jelly-light {
  animation: jelly-light 0.3s ease-in-out;
}

@keyframes jelly {
  0%,
  100% {
    transform: scale(1, 1);
  }
  25% {
    transform: scale(1.1, 0.9);
  }
  50% {
    transform: scale(0.9, 1.1);
  }
  75% {
    transform: scale(1.05, 0.95);
  }
}

@keyframes jelly-light {
  0%,
  100% {
    transform: scale(1, 1);
  }
  50% {
    transform: scale(1.03, 0.97);
  }
}
</style>
