from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """应用配置类"""
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Qwen API 配置
    qwen_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("Qwen_API_KEY", "QWEN_API_KEY", "qwen_api_key")
    )
    qwen_chat_model: str = "qwen3-max"
    qwen_memory_judge_model: str = "qwen-turbo"
    qwen_embedding_model: str = "text-embedding-v2"
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 记忆与资料库配置
    memory_importance_threshold: float = 0.6
    public_knowledge_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
    public_knowledge_enabled: bool = True
    
    # Milvus 配置
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "pet_ai_collection"
    
    # 服务器配置
    server_host: str = "127.0.0.1"
    server_port: int = 8888
    

# 创建全局配置实例
settings = Settings()
