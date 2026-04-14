<template>
  <div class="app">
    <Pet 
      :petSize="settings.petSize"
      :petColor="settings.petColor"
      :animationSpeed="settings.animationSpeed"
      :expressionFrequency="settings.expressionFrequency"
      :currentExpression="settings.currentExpression"
      :randomExpression="settings.randomExpression"
    />
    <Chat />
    <Settings 
      :settings="settings"
      @update:settings="updateSettings"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Pet from '../components/Pet.vue'
import Chat from '../components/Chat.vue'
import Settings from '../components/Settings.vue'

// 定义设置状态
const settings = ref({
  petSize: 100,
  petColor: '#000000', // 黑色，与宠物本体颜色一致
  animationSpeed: 1,
  expressionFrequency: 5,
  currentExpression: 'happy',
  randomExpression: true
})

// 更新设置的方法
const updateSettings = (newSettings: any) => {
  settings.value = { ...newSettings }
}
</script>

<style scoped>
.app {
  position: relative;
  width: 100%;
  height: 100vh;
}
</style>
