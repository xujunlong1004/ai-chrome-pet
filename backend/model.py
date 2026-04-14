from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings


class QwenModel:
    """Qwen模型管理类"""
    
    def __init__(self):
        """初始化Qwen模型"""
        # 初始化Qwen模型
        # 使用Qwen的兼容OpenAI接口
        self.model = ChatOpenAI(
            model="qwen3-max",
            api_key=settings.qwen_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 系统提示
        self.system_message = SystemMessage(
            content="你是一个可爱的AI宠物，会用友好、活泼的语气与用户交流。你可以回答用户的问题，讲述有趣的故事，或者只是简单地聊天。"
        )
    
    def chat(self, message: str, context: list = None) -> str:
        """与模型进行聊天"""
        try:
            # 构建消息列表
            messages = [self.system_message]
            
            # 添加上下文（如果有）
            if context:
                for item in context:
                    messages.append(HumanMessage(content=item))
            
            # 添加用户消息
            messages.append(HumanMessage(content=message))
            
            # 调用模型
            response = self.model.invoke(messages)
            
            return response.content
            
        except Exception as e:
            return f"聊天失败: {str(e)}"
    
    def chat_with_context(self, message: str, documents: list) -> str:
        """使用文档上下文与模型聊天"""
        try:
            # 构建上下文
            context_str = "\n".join([doc["content"] for doc in documents[:3]])
            
            # 构建提示
            prompt = f"请根据以下上下文回答问题：\n\n{context_str}\n\n问题：{message}"
            
            # 调用模型
            response = self.chat(prompt)
            
            return response
            
        except Exception as e:
            return f"聊天失败: {str(e)}"


# 创建全局模型实例
qwen_model = QwenModel()
