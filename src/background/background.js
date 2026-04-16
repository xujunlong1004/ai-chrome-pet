// background.js
// Chrome扩展的后台脚本，用于处理与后端API的通信

// 监听来自content script的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'chat') {
    // 调用后端API
    fetch('http://127.0.0.1:8888/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: message.content })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('API调用失败');
      }
      return response.json();
    })
    .then(data => {
      sendResponse({ response: data.response });
    })
    .catch(error => {
      console.error('API调用错误:', error);
      sendResponse({ error: error.message });
    });
    
    // 必须返回true以表示使用异步响应
    return true;
  }
});

// 后台脚本初始化
console.log('Chrome AI Pet background script initialized');