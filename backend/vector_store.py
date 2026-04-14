from langchain_community.vectorstores import Milvus
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings
import os


class VectorStore:
    """向量存储管理类"""
    
    def __init__(self):
        """初始化向量存储"""
        # 使用HuggingFace嵌入模型
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # 初始化Milvus向量存储
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            collection_name=settings.milvus_collection,
            connection_args={
                "host": settings.milvus_host,
                "port": settings.milvus_port
            }
        )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def load_document(self, file_path: str) -> str:
        """加载文档并添加到向量存储"""
        try:
            # 根据文件类型选择合适的加载器
            if file_path.endswith('.txt'):
                loader = TextLoader(file_path)
            elif file_path.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
            elif file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                return f"不支持的文件类型: {os.path.splitext(file_path)[1]}"
            
            # 加载文档
            documents = loader.load()
            
            # 分割文档
            split_docs = self.text_splitter.split_documents(documents)
            
            # 添加到向量存储
            self.vector_store.add_documents(split_docs)
            
            return f"文档加载成功，添加了 {len(split_docs)} 个片段"
            
        except Exception as e:
            return f"加载文档失败: {str(e)}"
    
    def search(self, query: str, k: int = 3) -> list:
        """根据查询在向量存储中搜索相关文档"""
        try:
            # 搜索相关文档
            results = self.vector_store.similarity_search(query, k=k)
            
            # 格式化结果
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
