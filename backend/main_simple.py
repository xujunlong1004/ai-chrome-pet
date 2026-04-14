from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 创建FastAPI应用
app = FastAPI(
    title="AI Pet Backend API",
    description="为AI宠物提供向量存储和模型交互功能的后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求模型
class ChatRequest(BaseModel):
    message: str
    context: list = None

# 根路径
@app.get("/")
def read_root():
    return {"message": "AI Pet Backend API"}

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 聊天接口（简化版）
@app.post("/api/chat")
def chat(request: ChatRequest):
    """与AI宠物聊天"""
    return {
        "response": f"你好！我收到了你的消息222：{request.message}。这是一个简化版的回复，完整功能需要配置Qwen API和Milvus向量数据库。"
    }

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)
