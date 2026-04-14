import { createApp } from 'vue'
import './assets/styles/main.css'
import App from './content/App.vue'

console.log('Chrome AI Pet extension loaded')

// Create a container element if it doesn't exist
let appContainer = document.getElementById('chrome-ai-pet-container')
if (!appContainer) {
  console.log('Creating container element')
  appContainer = document.createElement('div')
  appContainer.id = 'chrome-ai-pet-container'
  document.body.appendChild(appContainer)
  console.log('Container element created:', appContainer)
}

// Mount the Vue app
console.log('Mounting Vue app')
createApp(App).mount(appContainer)
console.log('Vue app mounted')