# AI Chrome Pet
浏览器桌面 AI 宠物

## 项目介绍

AI Chrome Pet 是一个基于浏览器的 AI 宠物应用，它可以：
- 与用户进行自然语言对话
- 学习和记忆用户的信息
- 基于文档内容回答问题
- 提供个性化的交互体验

AI Chrome Pet is a browser-based AI pet application that can:
- Have natural language conversations with users
- Learn and remember user information
- Answer questions based on document content
- Provide personalized interactive experiences

## 产品展示

### 宠物图标

![宠物图标](https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=A%20cute%20black%20pet%20icon%20with%20blue%20eyes%20on%20a%20browser%20extension%20background&image_size=square)

### 设置界面

![设置界面](https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=A%20settings%20panel%20for%20AI%20pet%20with%20emotion%20selection%20buttons%20and%20sliders%20for%20size%20and%20speed%20adjustment&image_size=landscape_16_9)

### 聊天界面

![聊天界面](https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=A%20chat%20interface%20with%20AI%20pet%20showing%20conversation%20history%20with%20bubbles%20for%20user%20and%20pet%20messages&image_size=portrait_4_3)

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- npm 7+

### 安装后端依赖

```bash
cd backend
pip3 install -r requirements.txt
pip3 install dashscope
```

### 安装前端依赖

```bash
npm install
```

### 配置 API 密钥

在 `backend/.env` 文件中配置 Qwen API 密钥：

```
Qwen_API_KEY=your_qwen_api_key
```

### 启动后端服务

```bash
cd backend
python3 main.py
```

后端服务将在 http://127.0.0.1:8888 上运行。

### 构建前端扩展

```bash
npm run build
```

构建后的文件将在 `dist` 目录中。

### 加载 Chrome 扩展

1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/
3. 启用 "开发者模式"
4. 点击 "加载已解压的扩展程序"
5. 选择 `dist` 目录

## 项目结构

```
ai-chrome-pet/
├── backend/              # 后端代码
│   ├── .env              # 环境变量配置
│   ├── config.py         # 配置管理
│   ├── main.py           # 主应用
│   ├── model.py          # 模型管理
│   ├── vector_store.py    # 向量存储管理
│   └── requirements.txt  # 依赖配置
├── src/                  # 前端代码
│   ├── assets/           # 静态资源
│   ├── background/       # 后台脚本
│   ├── components/       # 组件
│   │   ├── Chat.vue      # 聊天组件
│   │   ├── Pet.vue       # 宠物组件
│   │   └── Settings.vue  # 设置组件
│   ├── content/          # 内容脚本
│   └── main.ts           # 主入口
├── public/               # 公共资源
│   └── 宠物基本信息.docx  # 宠物基本信息文档
├── icons/                # 图标资源
├── dist/                 # 构建输出
├── manifest.json         # Chrome 扩展配置
└── package.json          # 前端依赖配置
```

## 核心功能

### 1. AI 宠物聊天

- 与用户进行自然语言对话
- 基于上下文理解用户意图
- 提供个性化的回复

### 2. 文档信息检索

- 自动加载 `public/宠物基本信息.docx` 到向量存储
- 根据用户问题检索相关文档内容
- 基于文档内容生成回答

### 3. 对话历史持久化

- 将用户与宠物的对话保存到向量存储
- 下次对话时自动检索相关历史
- 实现长期记忆功能

### 4. 智能上下文理解

- 结合文档信息和历史对话
- 提供更准确、个性化的回复
- 支持多轮对话

## 技术栈

### 后端

- Python 3.9+
- FastAPI - Web 框架
- LangChain - LLM 应用框架
- Chroma - 向量存储
- DashScopeEmbeddings - 嵌入模型
- Qwen - 大语言模型

### 前端

- Vue 3 - 前端框架
- TypeScript - 类型系统
- Tailwind CSS - 样式框架
- Vite - 构建工具

## API 接口

### 聊天接口

- **POST /api/chat** - 与 AI 宠物聊天
- **POST /api/chat-with-context** - 使用文档上下文聊天
- **POST /api/search** - 搜索向量存储
- **POST /api/upload** - 上传文档

## 使用说明

1. **启动后端服务** - 运行 `python3 main.py`
2. **构建前端扩展** - 运行 `npm run build`
3. **加载扩展** - 在 Chrome 中加载 `dist` 目录
4. **开始聊天** - 点击扩展图标，开始与 AI 宠物对话
5. **上传文档** - 通过 API 上传文档，丰富知识库

## 注意事项

- 确保 `backend/.env` 文件中配置了有效的 Qwen API 密钥
- 首次启动时会自动加载 `public/宠物基本信息.docx`
- 对话历史会自动保存到向量存储中
- 刷新页面后，宠物仍然能够记住之前的对话内容

## 未来计划

- 添加更多宠物角色和个性
- 支持更多文档格式
- 增加语音交互功能
- 实现宠物成长系统
- 添加多语言支持

---

## License

MIT License