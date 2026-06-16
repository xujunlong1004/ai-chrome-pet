from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import settings
import os
import hashlib
import json
from datetime import datetime
from typing import Optional


class VectorStore:
    """向量存储管理类"""
    
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".docx", ".pdf", ".json"}
    IGNORED_FILE_NAMES = {"manifest.json"}
    
    def __init__(self):
        """初始化向量存储"""
        # 使用DashScope嵌入模型
        self.embeddings = DashScopeEmbeddings(
            model=settings.qwen_embedding_model,
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
        
        # 已加载资料的记录文件
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
    
    def _record_for(self, key: str) -> Optional[dict]:
        record = self.loaded_docs.get(key)
        if isinstance(record, dict):
            return record
        if isinstance(record, str):
            return {"hash": record, "ids": []}
        return None
    
    def _get_loader(self, file_path: str):
        """根据文件类型选择加载器"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in {".txt", ".md", ".json"}:
            return TextLoader(file_path, encoding="utf-8")
        if ext == ".docx":
            return Docx2txtLoader(file_path)
        if ext == ".pdf":
            return PyPDFLoader(file_path)
        return None
    
    def _delete_document_chunks(self, ids: list):
        if not ids:
            return
        try:
            self.vector_store.delete(ids=ids)
        except Exception as e:
            print(f"删除旧资料片段失败: {str(e)}")
    
    def load_document(self, file_path: str, source_root: str = None) -> str:
        """加载文档并添加到向量存储"""
        try:
            if not os.path.exists(file_path):
                return f"文件不存在: {file_path}"
            
            file_name = os.path.basename(file_path)
            source_root = source_root or os.path.dirname(file_path)
            source_path = os.path.relpath(file_path, source_root)
            doc_key = f"knowledge:{source_path}"
            file_hash = self._get_file_hash(file_path)
            
            legacy_record = doc_key not in self.loaded_docs and file_name in self.loaded_docs
            record = self._record_for(doc_key)
            if not record and legacy_record:
                record = self._record_for(file_name)
            
            if record and record.get("hash") == file_hash and not legacy_record:
                return f"资料 {source_path} 未变化，跳过加载"
            
            loader = self._get_loader(file_path)
            if loader is None:
                return f"不支持的文件类型: {os.path.splitext(file_path)[1]}"
            
            if record and not legacy_record:
                self._delete_document_chunks(record.get("ids", []))
            
            documents = loader.load()
            
            split_docs = self.text_splitter.split_documents(documents)
            chunk_ids = []
            loaded_at = datetime.utcnow().isoformat()
            for index, doc in enumerate(split_docs):
                chunk_id = hashlib.md5(f"{doc_key}:{file_hash}:{index}".encode("utf-8")).hexdigest()
                chunk_ids.append(chunk_id)
                doc.metadata.update({
                    "type": "knowledge",
                    "source": source_path,
                    "source_path": source_path,
                    "file_name": file_name,
                    "file_hash": file_hash,
                    "chunk_index": index,
                    "loaded_at": loaded_at
                })
            
            self.vector_store.add_documents(split_docs, ids=chunk_ids)
            
            if file_name in self.loaded_docs and file_name != doc_key:
                self.loaded_docs.pop(file_name, None)
            self.loaded_docs[doc_key] = {
                "hash": file_hash,
                "ids": chunk_ids,
                "source": source_path,
                "loaded_at": loaded_at
            }
            self._save_loaded_docs()
            
            return f"资料 {source_path} 加载成功，添加了 {len(split_docs)} 个片段"
            
        except Exception as e:
            return f"加载文档失败: {str(e)}"
    
    def load_public_knowledge(self, public_dir: str = None) -> dict:
        """递归加载public目录中的资料文档。"""
        public_dir = public_dir or settings.public_knowledge_dir
        summary = {
            "directory": public_dir,
            "loaded": 0,
            "skipped": 0,
            "unsupported": 0,
            "errors": 0,
            "details": []
        }
        
        if not os.path.isdir(public_dir):
            summary["errors"] += 1
            summary["details"].append(f"资料库目录不存在: {public_dir}")
            return summary
        
        for root, dirs, files in os.walk(public_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file_name in files:
                if file_name.startswith("."):
                    continue
                if file_name in self.IGNORED_FILE_NAMES:
                    summary["unsupported"] += 1
                    continue
                file_path = os.path.join(root, file_name)
                ext = os.path.splitext(file_name)[1].lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    summary["unsupported"] += 1
                    continue
                
                result = self.load_document(file_path, source_root=public_dir)
                summary["details"].append(result)
                if "加载成功" in result:
                    summary["loaded"] += 1
                elif "跳过加载" in result:
                    summary["skipped"] += 1
                else:
                    summary["errors"] += 1
        
        return summary
    
    def save_memory(self, memory: str, user_message: str, assistant_response: str, importance: float, reason: str = "") -> str:
        """保存重要对话提炼出的长期记忆。"""
        try:
            content = f"长期记忆: {memory}"
            memory_id = hashlib.md5(
                f"{memory}:{user_message}:{assistant_response}".encode("utf-8")
            ).hexdigest()
            
            doc = Document(
                page_content=content,
                metadata={
                    "type": "memory",
                    "importance": importance,
                    "reason": reason,
                    "user_message": user_message,
                    "assistant_response": assistant_response,
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            
            self.vector_store.add_documents([doc], ids=[memory_id])
            
            return "重要记忆保存成功"
            
        except Exception as e:
            return f"保存记忆失败: {str(e)}"
    
    def save_conversation(self, user_message: str, assistant_response: str) -> str:
        """兼容旧调用：保存完整对话。新聊天接口优先使用save_memory。"""
        return self.save_memory(
            memory=f"用户说：{user_message}；宠物回复：{assistant_response}",
            user_message=user_message,
            assistant_response=assistant_response,
            importance=0.5,
            reason="legacy conversation save"
        )
    
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
