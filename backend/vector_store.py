from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import settings
import os
import hashlib
import json


class VectorStore:
    """向量存储管理类"""
    
    def __init__(self):
        """初始化向量存储"""
        # 使用DashScope嵌入模型
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v2",
            dashscope_api_key=settings.qwen_api_key
        )
        
        # 初始化Chroma向量存储（本地文件系统）
        self.vector_store_path = os.path.join(os.path.dirname(__file__), "chroma_db")
        
        # 创建或加载Chroma向量存储
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.vector_store_path
        )
        
        # 初始化文本分割器，调整参数以获得更好的分割效果
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 已加载文档的记录文件
        self.loaded_docs_file = os.path.join(os.path.dirname(__file__), "loaded_documents.json")
        self.loaded_docs = self._load_loaded_docs()
    
    def _load_loaded_docs(self) -> dict:
        """加载已加载文档的记录"""
        if os.path.exists(self.loaded_docs_file):
            try:
                with open(self.loaded_docs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_loaded_docs(self):
        """保存已加载文档的记录"""
        try:
            with open(self.loaded_docs_file, 'w', encoding='utf-8') as f:
                json.dump(self.loaded_docs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存已加载文档记录失败: {str(e)}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """计算文件的哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def load_document(self, file_path: str) -> str:
        """加载文档并添加到向量存储"""
        try:
            if not os.path.exists(file_path):
                return f"文件不存在: {file_path}"
            
            file_name = os.path.basename(file_path)
            file_hash = self._get_file_hash(file_path)
            
            if file_name in self.loaded_docs:
                if self.loaded_docs[file_name] == file_hash:
                    return f"文档 {file_name} 已加载，跳过重复加载"
            
            if file_path.endswith('.txt'):
                loader = TextLoader(file_path)
            elif file_path.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
            elif file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                return f"不支持的文件类型: {os.path.splitext(file_path)[1]}"
            
            documents = loader.load()
            
            split_docs = self.text_splitter.split_documents(documents)
            
            self.vector_store.add_documents(split_docs)
            
            self.loaded_docs[file_name] = file_hash
            self._save_loaded_docs()
            
            return f"文档加载成功，添加了 {len(split_docs)} 个片段"
            
        except Exception as e:
            return f"加载文档失败: {str(e)}"
    
    def save_conversation(self, user_message: str, assistant_response: str) -> str:
        """保存对话到向量存储"""
        try:
            # 使用更清晰的格式，便于检索
            conversation_content = f"Q: {user_message}\nA: {assistant_response}"
            
            doc = Document(
                page_content=conversation_content,
                metadata={
                    "type": "conversation",
                    "user_message": user_message,
                    "assistant_response": assistant_response
                }
            )
            
            # 添加文档到向量存储
            self.vector_store.add_documents([doc])
            
            return "对话保存成功"
            
        except Exception as e:
            return f"保存对话失败: {str(e)}"
    
    def search(self, query: str, k: int = 3) -> list:
        """根据查询在向量存储中搜索相关文档"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "id": i + 1,
                    "content": result.page_content,
                    "metadata": result.metadata
                })
            
            return formatted_results
            
        except Exception as e:
            return [{"error": f"搜索失败: {str(e)}"}]


# 创建全局向量存储实例
vector_store = VectorStore()
