from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    # Qwen API 配置
    qwen_api_key: str = ""
    
    # Milvus 配置
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "pet_ai_collection"
    
    # 服务器配置
    server_host: str = "127.0.0.1"
    server_port: int = 8888
    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        case_sensitive = False


# 创建全局配置实例
settings = Settings()
