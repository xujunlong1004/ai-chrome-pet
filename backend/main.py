from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from model import qwen_model

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

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 聊天接口
@app.post("/api/chat")
def chat(request: ChatRequest):
    """与AI宠物聊天"""
    # 调用真正的Qwen模型
    response = qwen_model.chat(request.message, request.context)
    return {"response": response}

# 搜索接口（简化版）
@app.post("/api/search")
def search(request: SearchRequest):
    """在向量存储中搜索相关文档"""
    # 模拟搜索结果
    results = [
        {
            "id": 1,
            "content": "这是一个模拟的搜索结果1",
            "metadata": {}
        },
        {
            "id": 2,
            "content": "这是一个模拟的搜索结果2",
            "metadata": {}
        },
        {
            "id": 3,
            "content": "这是一个模拟的搜索结果3",
            "metadata": {}
        }
    ]
    return {"results": results}

# 带上下文的聊天接口（简化版）
@app.post("/api/chat-with-context")
def chat_with_context(request: SearchRequest):
    """使用文档上下文与AI宠物聊天"""
    # 模拟搜索结果
    documents = [
        {
            "id": 1,
            "content": "这是一个模拟的文档上下文1",
            "metadata": {}
        },
        {
            "id": 2,
            "content": "这是一个模拟的文档上下文2",
            "metadata": {}
        }
    ]
    # 模拟回复
    response = f"根据上下文，我对'{request.query}'的回答是：这是一个基于模拟上下文的回复。"
    return {"response": response, "context": documents}

# 文档上传接口（简化版）
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
        
        # 模拟文档加载
        result = f"文档 {file.filename} 上传成功，添加了 5 个片段"
        
        # 删除临时文件
        os.remove(file_path)
        
        return {"message": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)
