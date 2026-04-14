<template>
  <div class="settings-container">
    <div class="settings-header" @click="toggleSettings">
      <h3>设置</h3>
      <button class="toggle-btn">{{ isOpen ? '−' : '+' }}</button>
    </div>
    <div class="settings-content" v-if="isOpen">
      <div class="setting-item">
        <label>表情选择</label>
        <div class="expression-buttons">
          <button 
            v-for="exp in expressions" 
            :key="exp"
            :class="['expression-btn', { active: localSettings.currentExpression === exp }]"
            @click="selectExpression(exp)"
          >
            {{ getExpressionLabel(exp) }}
          </button>
        </div>
      </div>
      <div class="setting-item">
        <button class="random-btn" @click="toggleRandom">
          {{ localSettings.randomExpression ? '停止随机' : '随机表情' }}
        </button>
      </div>
      <div class="setting-item">
        <label for="pet-size">宠物大小</label>
        <input 
          type="range" 
          id="pet-size" 
          v-model.number="localSettings.petSize" 
          min="50" 
          max="150" 
          step="10"
          @input="updateSettings"
        />
        <span>{{ localSettings.petSize }}px</span>
      </div>
      <div class="setting-item">
        <label for="pet-color">宠物颜色</label>
        <input 
          type="color" 
          id="pet-color" 
          v-model="localSettings.petColor"
          @input="updateSettings"
        />
      </div>
      <div class="setting-item">
        <label for="animation-speed">动画速度</label>
        <input 
          type="range" 
          id="animation-speed" 
          v-model.number="localSettings.animationSpeed" 
          min="0.5" 
          max="3" 
          step="0.5"
          @input="updateSettings"
        />
        <span>{{ localSettings.animationSpeed }}x</span>
      </div>
      <div class="setting-item">
        <label for="expression-frequency">表情变化频率</label>
        <input 
          type="range" 
          id="expression-frequency" 
          v-model.number="localSettings.expressionFrequency" 
          min="1" 
          max="10" 
          step="1"
          @input="updateSettings"
        />
        <span>{{ localSettings.expressionFrequency }}秒</span>
      </div>
      <button class="reset-btn" @click="resetSettings">恢复默认</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

// 接收父组件传递的设置
const props = defineProps({
  settings: {
    type: Object,
    required: true
  }
})

// 定义事件
const emit = defineEmits(['update:settings'])

const isOpen = ref(false)
const localSettings = ref({ ...props.settings })

// 表情列表
const expressions = ['happy', 'sad', 'angry', 'surprised', 'tired', 'disdain', 'cute', 'cute-angry']

// 获取表情标签
const getExpressionLabel = (exp: string) => {
  const labels: Record<string, string> = {
    'happy': '开心',
    'sad': '悲伤',
    'angry': '生气',
    'surprised': '惊讶',
    'tired': '疲惫',
    'disdain': '鄙视',
    'cute': '可爱',
    'cute-angry': '可爱生气'
  }
  return labels[exp] || exp
}

// 选择表情
const selectExpression = (exp: string) => {
  localSettings.value.currentExpression = exp
  localSettings.value.randomExpression = false
  updateSettings()
}

// 切换随机表情
const toggleRandom = () => {
  localSettings.value.randomExpression = !localSettings.value.randomExpression
  updateSettings()
}

// 监听props变化，更新本地设置
watch(() => props.settings, (newSettings) => {
  localSettings.value = { ...newSettings }
}, { deep: true })

const toggleSettings = () => {
  isOpen.value = !isOpen.value
}

const resetSettings = () => {
  localSettings.value = {
    petSize: 100,
    petColor: '#000000', // 黑色，与宠物本体颜色一致
    animationSpeed: 1,
    expressionFrequency: 5,
    currentExpression: 'happy',
    randomExpression: true
  }
  updateSettings()
}

const updateSettings = () => {
  // 保存设置到Chrome存储
  console.log('Settings updated:', localSettings.value)
  // 实际项目中会使用Chrome存储API
  // chrome.storage.local.set({ settings: localSettings.value })
  // 向父组件发出更新事件
  emit('update:settings', { ...localSettings.value })
}

onMounted(() => {
  // 加载设置
  console.log('Settings loaded:', props.settings)
  // 初始化表情相关设置
  if (!localSettings.value.currentExpression) {
    localSettings.value.currentExpression = 'happy'
  }
  if (localSettings.value.randomExpression === undefined) {
    localSettings.value.randomExpression = true
  }
})
</script>

<style scoped>
.settings-container {
  background-color: #F1FAEE;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 300px;
}

.expression-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 5px;
}

.expression-btn {
  padding: 6px 12px;
  border: 2px solid #A8DADC;
  border-radius: 6px;
  background-color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.expression-btn:hover {
  background-color: #A8DADC;
}

.expression-btn.active {
  background-color: #457B9D;
  color: white;
  border-color: #457B9D;
}

.random-btn {
  width: 100%;
  padding: 10px 15px;
  border: none;
  border-radius: 6px;
  background-color: #A8DADC;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
}

.random-btn:hover {
  background-color: #457B9D;
  color: white;
}

.random-btn.active {
  background-color: #457B9D;
  color: white;
}

.settings-header {
  background-color: #A8DADC;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.settings-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.toggle-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #333;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-content {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.setting-item label {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.setting-item input[type="range"] {
  width: 100%;
  margin: 5px 0;
}

.setting-item input[type="color"] {
  width: 100%;
  height: 40px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.setting-item span {
  font-size: 12px;
  color: #666;
  text-align: right;
}

.reset-btn {
  background-color: #FFADAD;
  border: none;
  border-radius: 5px;
  padding: 10px 15px;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.reset-btn:hover {
  background-color: #FFD6A5;
  transform: translateY(-2px);
}
</style>
