from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
import json
import re


class QwenModel:
    """Qwen模型管理类"""
    
    def __init__(self):
        """初始化Qwen模型"""
        self.model = ChatOpenAI(
            model=settings.qwen_chat_model,
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url
        )
        self.memory_judge_model = ChatOpenAI(
            model=settings.qwen_memory_judge_model,
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
            temperature=0
        )
        
        # 系统提示
        self.system_message = SystemMessage(
            content=(
                "你是一个可爱的AI宠物，会用友好、活泼的语气与用户交流。"
                "你可以根据资料库和长期记忆回答问题，也可以正常陪用户聊天。"
                "如果资料或记忆不足，请自然说明不确定，不要编造。"
            )
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
            context_parts = []
            for i, doc in enumerate(documents[:8]):  # 使用前8个文档
                if doc.get("content"):
                    if doc.get("metadata", {}).get("type") in {"conversation", "memory"}:
                        context_parts.append(f"[长期记忆 {i+1}]: {doc['content']}")
                    else:
                        source = doc.get("metadata", {}).get("source", "资料库")
                        context_parts.append(f"[资料 {i+1} | {source}]: {doc['content']}")
            
            context_str = "\n\n".join(context_parts)
            
            prompt = (
                "你可以参考以下资料库片段和长期记忆来回答。"
                "资料相关时优先使用资料；记忆相关时自然融入。"
                "上下文不相关时，不要硬套。\n\n"
                f"{context_str}\n\n"
                f"用户：{message}\n\n"
                "回答："
            )
            
            response = self.chat(prompt)
            
            return response
            
        except Exception as e:
            return f"聊天失败: {str(e)}"
    
    def judge_memory_importance(self, user_message: str, assistant_response: str) -> dict:
        """判断一轮对话是否值得保存为长期记忆。"""
        default_result = {
            "should_save": False,
            "importance": 0.0,
            "memory": "",
            "reason": "memory judge failed"
        }
        
        try:
            prompt = (
                "你是AI宠物的长期记忆筛选器。判断以下对话是否值得保存到向量数据库。"
                "只保存会影响未来个性化对话的信息，例如：用户身份、偏好、长期目标、项目背景、反复强调的事实、"
                "宠物设定、重要决定、资料库/skill 使用规则。"
                "不要保存寒暄、一次性问题、临时情绪、纯事实问答、无长期价值内容。\n\n"
                "请只输出JSON，不要Markdown，不要解释。格式："
                '{"should_save": boolean, "importance": 0到1数字, "memory": "可独立理解的一句话记忆", "reason": "简短原因"}'
                "\n\n"
                f"用户消息：{user_message}\n"
                f"宠物回复：{assistant_response}"
            )
            
            response = self.memory_judge_model.invoke([
                SystemMessage(content="你只输出可解析的JSON。"),
                HumanMessage(content=prompt)
            ])
            content = response.content.strip()
            match = re.search(r"\{.*\}", content, re.S)
            if not match:
                return default_result
            
            data = json.loads(match.group(0))
            importance = float(data.get("importance", 0))
            memory = str(data.get("memory", "")).strip()
            should_save = bool(data.get("should_save")) and importance >= settings.memory_importance_threshold and len(memory) > 0
            
            return {
                "should_save": should_save,
                "importance": importance,
                "memory": memory,
                "reason": str(data.get("reason", "")).strip()
            }
        except Exception as e:
            return {
                **default_result,
                "reason": f"memory judge failed: {str(e)}"
            }


# 创建全局模型实例
qwen_model = QwenModel()
