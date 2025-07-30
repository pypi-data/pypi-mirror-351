import time
from typing import Any, Dict, Iterator, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from zhipuai import ZhipuAI


def _convert_message_to_dict(message: Any) -> Dict[str, Any]:
    """将 LangChain 消息格式或兼容字典转换为 ZhipuAI 支持的消息格式
    Args:
        message (Any): LangChain 消消息对象或包含 'role' 和 'content' 的字典
    Returns:
        dict: ZhipuAI 支持的消息格式
    """
    content_to_process: Any
    role_str: Optional[str] = None
    name_str: Optional[str] = None

    if isinstance(message, BaseMessage):
        content_to_process = message.content
        if (
            name_val := message.name or message.additional_kwargs.get("name")
        ) is not None:
            name_str = str(name_val)

        if isinstance(message, ChatMessage):
            role_str = message.role
        elif isinstance(message, HumanMessage):
            role_str = "user"
        elif isinstance(message, AIMessage):
            role_str = "assistant"
        elif isinstance(message, SystemMessage):
            role_str = "system"
        else:
            raise TypeError(f"Unsupported BaseMessage type: {type(message)}")
    elif isinstance(message, dict):
        if "content" not in message:
            raise ValueError("Input dictionary must have a 'content' key.")
        content_to_process = message["content"]

        if "role" not in message:
            raise ValueError("Input dictionary must have a 'role' key.")
        role_str = str(message["role"])

        name_val = message.get("name")
        if name_val is not None:
            name_str = str(name_val)

    else:
        raise TypeError(
            f"Unsupported message type: {type(message)}. Expected BaseMessage or dict."
        )

    final_content_str: str
    if isinstance(content_to_process, list):
        text_parts = []
        for item in content_to_process:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                text_parts.append(str(item["text"]))
        final_content_str = "".join(text_parts)
    elif isinstance(content_to_process, str):
        final_content_str = content_to_process
    else:
        raise TypeError(
            f"Unsupported content type: {type(content_to_process)}. Content must be str or list of str/dict."
        )

    # 构建 ZhipuAI 消息字典
    if role_str is None:
        raise ValueError("Message role could not be determined.")

    zhipu_message_dict: Dict[str, Any] = {
        "role": role_str,
        "content": final_content_str,
    }
    if name_str is not None:
        zhipu_message_dict["name"] = name_str

    return zhipu_message_dict


class ChatZhipuAI(BaseChatModel):
    """智谱 AI 对话模型"""

    model_name: str = "glm-4-plus"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    stop: Optional[List[str]] = None
    max_retries: int = 3
    api_key: str | None = None

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成对话响应

        示例:
            ```python
            # 使用字典格式的消息列表
            res = chat_model._generate(
                messages=[
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "你好呀"},
                    {"role": "user", "content": "你是谁？"},
                ],
                stop=["你是谁？"],
            )
            # 获取生成的内容
            content = res.generations[0].message.content
            ```

        Args:
            messages: 对话历史消息列表，可以是BaseMessage对象或包含role和content的字典
            stop: 可选的停止词列表，当生成内容包含这些词时会停止生成
            run_manager: 可选的回调管理器，用于处理生成过程中的回调
            **kwargs: 其他关键字参数

        Returns:
            ChatResult: 包含生成结果的对象
        """
        messages = [_convert_message_to_dict(message) for message in messages]
        start_time = time.time()
        response = ZhipuAI(api_key=self.api_key).chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop,
            timeout=self.timeout,
        )
        elaspsed_time = time.time() - start_time
        message = AIMessage(
            content=response.choices[0].message.content,
            additional_kwargs={},
            response_metadata={
                "time_in_seconds": elaspsed_time,
            },
            usage_metadata={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        )
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: CallbackManagerForLLMRun = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """流式生成对话响应

        示例:
            ```python
            # 使用字典格式的消息列表进行流式生成
            for chunk in chat_model._stream(
                messages=[
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "你好呀"},
                    {"role": "user", "content": "你是谁？"},
                ],
                stop=["你是谁？"],
            ):
                # 实时打印每个生成的文本片段
                print(chunk.message.content, end="", flush=True)
            ```

        Args:
            messages: 对话历史消息列表，可以是BaseMessage对象或包含role和content的字典
            stop: 可选的停止词列表，当生成内容包含这些词时会停止生成
            run_manager: 可选的回调管理器，用于处理流式生成过程中的回调
            **kwargs: 其他关键字参数

        Returns:
            Iterator[ChatGenerationChunk]: 生成内容的迭代器，每个元素是一个文本片段
        """
        messages = [_convert_message_to_dict(message) for message in messages]
        start_time = time.time()
        response = ZhipuAI(api_key=self.api_key).chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop,
            timeout=self.timeout,
            stream=True,
        )

        usage_metadata = None
        for chunk in response:
            if chunk.usage:
                usage_metadata = UsageMetadata(
                    {
                        "input_tokens": chunk.usage.prompt_tokens,
                        "output_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    }
                )
            chunk = ChatGenerationChunk(
                message=AIMessageChunk(
                    content=chunk.choices[0].delta.content or "",
                )
            )

            if run_manager:
                run_manager.on_llm_new_token(chunk.message.content, chunk)
            yield chunk
        elaspsed_time = time.time() - start_time
        chunk = ChatGenerationChunk(
            message=AIMessageChunk(
                content="",
                response_metadata={"time_in_sec": round(elaspsed_time, 3)},
                usage_metadata=usage_metadata,
            )
        )
        if run_manager:
            run_manager.on_llm_new_token(chunk.message.content, chunk)
        yield chunk

    @property
    def _llm_type(self) -> str:
        """返回模型类型"""
        return self.model_name

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回模型的标识参数"""
        return {"model_name": self.model_name}
