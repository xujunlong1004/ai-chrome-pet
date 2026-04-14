from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from model import qwen_model
from vector_store import vector_store

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
    """应用启动时自动加载宠物基本信息文档"""
    pet_info_doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "宠物基本信息.docx")
    if os.path.exists(pet_info_doc_path):
        result = vector_store.load_document(pet_info_doc_path)
        print(f"宠物基本信息文档加载: {result}")
    else:
        print(f"宠物基本信息文档不存在: {pet_info_doc_path}")

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 聊天接口
@app.post("/api/chat")
def chat(request: ChatRequest):
    """与AI宠物聊天"""
    try:
        # 先在向量存储中搜索相关内容（包括文档和历史对话）
        # 增加 k 值，获取更多相关内容
        relevant_docs = vector_store.search(request.message, k=10)
        
        # 打印检索到的内容（用于调试）
        print(f"向量数据库检索内容: {relevant_docs}")
        
        # 构建更详细的上下文
        context_text = ""
        if relevant_docs and len(relevant_docs) > 0 and "error" not in relevant_docs[0]:
            # 提取相关内容，优先使用文档内容
            for doc in relevant_docs:
                if doc.get("content"):
                    # 区分文档和对话
                    if doc.get("metadata", {}).get("type") == "conversation":
                        context_text += f"对话历史: {doc['content']}\n\n"
                    else:
                        context_text += f"文档信息: {doc['content']}\n\n"
        
        # 打印构建的上下文
        print(f"构建的上下文: {context_text}")
        
        # 使用带上下文的聊天，确保模型能看到完整的上下文
        response = qwen_model.chat_with_context(request.message, relevant_docs)
            
    except Exception as e:
        print(f"错误: {str(e)}")
        response = qwen_model.chat(request.message, request.context)
    
    # 保存对话到向量数据库，实现持久化存储
    save_result = vector_store.save_conversation(request.message, response)
    print(f"保存对话结果: {save_result}")
        
    return {"response": response}

# 搜索接口
@app.post("/api/search")
def search(request: SearchRequest):
    """在向量存储中搜索相关文档"""
    results = vector_store.search(request.query, request.k)
    return {"results": results}

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
