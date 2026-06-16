from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from model import qwen_model
from vector_store import vector_store
from config import settings

# 创建FastAPI应用
app = FastAPI(
    title="AI Pet Backend API",
    description="为AI宠物提供向量存储和模型交互功能的后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求模型
class ChatRequest(BaseModel):
    message: str
    context: list = None

class SearchRequest(BaseModel):
    query: str
    k: int = 3

# 根路径
@app.get("/")
def read_root():
    return {"message": "AI Pet Backend API"}


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时自动同步public资料库"""
    if settings.public_knowledge_enabled:
        result = vector_store.load_public_knowledge()
        print(f"public资料库同步: {result}")

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 聊天接口
@app.post("/api/chat")
def chat(request: ChatRequest):
    """与AI宠物聊天"""
    memory_result = None
    try:
        relevant_docs = vector_store.search(request.message, k=10)
        
        print(f"向量数据库检索内容: {relevant_docs}")
        
        response = qwen_model.chat_with_context(request.message, relevant_docs)
            
    except Exception as e:
        print(f"错误: {str(e)}")
        response = qwen_model.chat(request.message, request.context)
    
    try:
        memory_result = qwen_model.judge_memory_importance(request.message, response)
        print(f"记忆重要性判断: {memory_result}")
        if memory_result.get("should_save"):
            save_result = vector_store.save_memory(
                memory=memory_result["memory"],
                user_message=request.message,
                assistant_response=response,
                importance=memory_result["importance"],
                reason=memory_result.get("reason", "")
            )
            print(f"保存记忆结果: {save_result}")
        else:
            print("本轮对话未达到长期记忆阈值，跳过保存")
    except Exception as e:
        print(f"记忆处理失败: {str(e)}")
        
    return {"response": response, "memory": memory_result}

# 搜索接口
@app.post("/api/search")
def search(request: SearchRequest):
    """在向量存储中搜索相关文档"""
    results = vector_store.search(request.query, request.k)
    return {"results": results}

@app.post("/api/knowledge/sync")
def sync_public_knowledge():
    """手动同步public目录中的资料库文档"""
    result = vector_store.load_public_knowledge()
    return {"result": result}

# 带上下文的聊天接口
@app.post("/api/chat-with-context")
def chat_with_context(request: SearchRequest):
    """使用文档上下文与AI宠物聊天"""
    documents = vector_store.search(request.query, request.k)
    response = qwen_model.chat_with_context(request.query, documents)
    return {"response": response, "context": documents}

# 文档上传接口
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文档并添加到向量存储"""
    try:
        # 确保上传目录存在
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 保存文件
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 加载文档到向量存储
        result = vector_store.load_document(file_path)
        
        # 删除临时文件
        os.remove(file_path)
        
        return {"message": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)
