# AI Pet Backend

这是一个为AI宠物提供向量存储、长期记忆和资料库检索能力的后端服务，使用 FastAPI、LangChain、Qwen 模型和本地 Chroma 向量存储。

## 功能特性

- 文档加载：支持 txt、md、docx、pdf、json 格式的文档
- public资料库：启动时递归同步 `public` 目录，可手动触发同步
- 长期记忆：使用低成本 Qwen 模型判断对话是否重要，只保存有长期价值的记忆
- 向量存储：使用本地 Chroma 进行向量存储和检索
- 模型交互：默认使用 Qwen3-max 进行聊天，Qwen Turbo 进行记忆筛选
- RAG功能：结合文档上下文进行智能回答
- RESTful API：提供完整的API接口

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填写相应的配置：

```bash
cp .env.example .env
```

### 3. 启动后端服务

```bash
python main.py
```

服务默认运行在 http://127.0.0.1:8888

## API接口

### 1. 健康检查

- **路径**：`/health`
- **方法**：GET
- **响应**：`{"status": "healthy"}`

### 2. 聊天

- **路径**：`/api/chat`
- **方法**：POST
- **请求体**：
  ```json
  {
    "message": "你好",
    "context": []
  }
  ```
- **响应**：
  ```json
  {
    "response": "你好！我是你的AI宠物，很高兴见到你！"
  }
  ```

### 3. 搜索

- **路径**：`/api/search`
- **方法**：POST
- **请求体**：
  ```json
  {
    "query": "人工智能",
    "k": 3
  }
  ```
- **响应**：
  ```json
  {
    "results": [
      {
        "id": 1,
        "content": "人工智能是...",
        "metadata": {}
      }
    ]
  }
  ```

### 4. 带上下文的聊天

- **路径**：`/api/chat-with-context`
- **方法**：POST
- **请求体**：
  ```json
  {
    "query": "人工智能的应用",
    "k": 3
  }
  ```
- **响应**：
  ```json
  {
    "response": "人工智能的应用包括...",
    "context": [
      {
        "id": 1,
        "content": "人工智能是...",
        "metadata": {}
      }
    ]
  }
  ```

### 5. 文档上传

- **路径**：`/api/upload`
- **方法**：POST
- **请求**：multipart/form-data，包含file字段
- **响应**：
  ```json
  {
    "message": "文档加载成功，添加了 5 个片段"
  }
  ```

### 6. 同步 public 资料库

- **路径**：`/api/knowledge/sync`
- **方法**：POST
- **响应**：
  ```json
  {
    "result": {
      "loaded": 1,
      "skipped": 2,
      "unsupported": 1,
      "errors": 0
    }
  }
  ```

## 技术栈

- FastAPI：Web框架
- LangChain：大语言模型应用框架
- Qwen3-max：大语言模型
- Chroma：本地向量数据库
- DashScopeEmbeddings：文本嵌入
- Pydantic：数据验证

## 注意事项

1. 填写正确的 Qwen API Key
2. `public/manifest.json` 等扩展元数据不会被当作资料库索引
3. 修改或新增 `public` 资料后，可重启服务或调用 `/api/knowledge/sync`
4. 在生产环境中，应该配置 CORS 为具体的域名
