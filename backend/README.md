# AI Pet Backend

这是一个为AI宠物提供向量存储和模型交互功能的后端服务，使用FastAPI、LangChain、Qwen3-max模型和Milvus向量存储。

## 功能特性

- 文档加载：支持txt、docx、pdf格式的文档
- 向量存储：使用Milvus进行向量存储和检索
- 模型交互：使用Qwen3-max模型进行聊天
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

### 3. 启动Milvus

确保Milvus服务已经启动，默认监听在localhost:19530。

### 4. 启动后端服务

```bash
python main.py
```

服务默认运行在 http://localhost:8000

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

## 技术栈

- FastAPI：Web框架
- LangChain：大语言模型应用框架
- Qwen3-max：大语言模型
- Milvus：向量数据库
- HuggingFace Embeddings：文本嵌入
- Pydantic：数据验证

## 注意事项

1. 确保Milvus服务已经启动
2. 填写正确的Qwen API Key
3. 文档上传大小限制为默认值，可根据需要调整
4. 在生产环境中，应该配置CORS为具体的域名
