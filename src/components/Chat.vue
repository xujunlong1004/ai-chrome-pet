<template>
  <div class="chat-container">
    <div class="chat-header">
      <h3>与AI宠物聊天</h3>
      <button class="close-btn" @click="toggleChat">×</button>
    </div>
    <div class="chat-messages" v-if="isOpen">
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        class="message" 
        :class="message.role"
      >
        <div class="message-content">
          {{ message.content }}
        </div>
      </div>
      <div class="loading" v-if="isLoading">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
      </div>
    </div>
    <div class="chat-input" v-if="isOpen">
      <input 
        type="text" 
        v-model="inputMessage" 
        placeholder="输入消息..."
        @keyup.enter="sendMessage"
      />
      <button class="send-btn" @click="sendMessage">→</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isOpen = ref(true)
const inputMessage = ref('')
const messages = ref([
  { role: 'assistant', content: '你好！我是你的AI宠物。今天我能帮你什么忙吗？' }
])
const isLoading = ref(false)

const toggleChat = () => {
  isOpen.value = !isOpen.value
}

const sendMessage = async () => {
  if (inputMessage.value.trim() === '') return

  // 添加用户消息
  messages.value.push({ role: 'user', content: inputMessage.value })
  const userMessage = inputMessage.value
  inputMessage.value = ''

  isLoading.value = true

  try {
    // 模拟API调用
    const response = await getAIResponse(userMessage)
    // 添加AI响应
    messages.value.push({ role: 'assistant', content: response })
  } catch (error) {
    messages.value.push({ role: 'assistant', content: '抱歉，我遇到了错误。请再试一次。' })
  } finally {
    isLoading.value = false
  }
}

const getAIResponse = async (message: string): Promise<string> => {
  return new Promise((resolve) => {
    // 使用chrome.runtime.sendMessage与background script通信
    chrome.runtime.sendMessage(
      { type: 'chat', content: message },
      (response) => {
        if (response && response.response) {
          resolve(response.response)
        } else {
          console.error('Background script response error:', response)
          // 备用响应逻辑
          const responses = [
            '这很有趣！告诉我更多。',
            '我理解。你对此感觉如何？',
            '听起来很有趣！你还想做什么？',
            '我在这里帮助你。你需要什么帮助？',
            '这是个好观点。我没有那样想过。'
          ]
          resolve(responses[Math.floor(Math.random() * responses.length)])
        }
      }
    )
  })
}

onMounted(() => {
  // 初始化聊天界面
  console.log('Chat component mounted')
})
</script>

<style scoped>
.chat-container {
  background-color: #F1FAEE;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background-color: #A8DADC;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.close-btn {
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

.chat-messages {
  padding: 15px;
  overflow-y: auto;
  flex: 1;
  max-height: 300px;
}

.message {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.assistant {
  align-items: flex-start;
}

.message-content {
  padding: 10px 15px;
  border-radius: 18px;
  max-width: 80%;
  word-wrap: break-word;
}

.message.user .message-content {
  background-color: #9BF6FF;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background-color: #FFD6A5;
  border-bottom-left-radius: 4px;
}

.chat-input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #E5E7EB;
}

.chat-input input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #E5E7EB;
  border-radius: 20px;
  outline: none;
  font-family: 'Comic Sans MS', cursive;
}

.send-btn {
  background-color: #A8DADC;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  margin-left: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: #333;
  transition: all 0.3s ease;
}

.send-btn:hover {
  background-color: #9BF6FF;
  transform: scale(1.1);
}

.loading {
  display: flex;
  gap: 5px;
  padding: 10px 15px;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background-color: #333;
  border-radius: 50%;
  animation: pulse 1.5s infinite ease-in-out;
}

.loading-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
