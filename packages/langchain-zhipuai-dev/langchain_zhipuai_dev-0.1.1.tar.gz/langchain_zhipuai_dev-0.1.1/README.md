# langchain-zhipuai

[![PyPI version](https://badge.fury.io/py/langchain-zhipuai-dev.svg)](https://badge.fury.io/py/langchain-zhipuai-dev)

`langchain-zhipuai` 是一个为 LangChain 实现的 ZhipuAI (智谱 AI) 大模型接口包。它允许用户在 LangChain 框架内方便地使用智谱AI提供的各种强大的语言模型。
这个项目最初是作为一个编码练习，但旨在提供一个功能完整且易于使用的集成。

## 特性

- 支持智谱 AI 的多种模型 (例如 `glm-4`, `glm-4-air`, `glm-3-turbo` 等，默认 `glm-4-plus`)。
- 支持标准的 LangChain `invoke`, `stream`, 和 `generate` (批量) API。
- 灵活的消息输入格式 (字典列表或 `BaseMessage` 对象列表)。
- 可配置的参数，如 `temperature`, `max_tokens`, `stop` 序列等。
- 自动处理API密钥。
- 返回包含 `usage_metadata` 和 `response_metadata` 的标准 LangChain 输出对象。

## 安装

你可以使用 `uv` 或 `pip` 来安装这个包：

使用 `uv`:

```bash
uv add langchain-zhipuai-dev
```

或者使用 `pip`:

```bash
pip install langchain-zhipuai-dev
```

## 环境配置

在使用之前，你需要设置你的智谱 AI API 密钥。可以通过设置环境变量 `ZHIPUAI_API_KEY` 来完成：

```bash
export ZHIPUAI_API_KEY="YOUR_ZHIPUAI_API_KEY"
```

或者，你也可以在代码中初始化 `ChatZhipuAI` 类时直接传递 `api_key` 参数。

## 使用方法

下面是一些如何使用 `langchain-zhipuai` 的基本示例。

### 1. 初始化

首先，导入并初始化 `ChatZhipuAI` 类：

```python
import os
from langchain_zhipuai_dev.chat import ChatZhipuAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# 从环境变量加载 API Key
llm = ChatZhipuAI(
    model_name="glm-4",  # 可选，默认为 "glm-4-plus"
    temperature=0.7,     # 可选，默认为 None (使用智谱AI的默认值)
    # api_key="YOUR_ZHIPUAI_API_KEY" # 如果没有设置环境变量，可以在这里提供
)
```

### 2. 使用 `invoke` API (单次调用)

`invoke` 方法用于发送一次请求并获取单个完整的响应。

```python
messages = [
    SystemMessage(content="你是一个乐于助人的 AI 助手。"),
    HumanMessage(content="你好，请介绍一下你自己。")
]

response = llm.invoke(messages)

print("Invoke API Response:")
print(f"Type: {type(response)}")
print(f"Content: {response.content}")
if response.usage_metadata:
    print(f"Usage: {response.usage_metadata}")
if response.response_metadata:
    print(f"Response Metadata: {response.response_metadata}")
```

### 3. 使用 `stream` API (流式响应)

`stream` 方法用于获取流式响应，逐步接收模型生成的内容。

```python
messages = [
    HumanMessage(content="给我讲一个关于编程的笑话。")
]

print("\nStream API Response:")
full_streamed_content = []
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
    full_streamed_content.append(chunk.content)
    # AIMessageChunk 包含 content, additional_kwargs, response_metadata, usage_metadata, id
    # 最后一个 chunk 通常包含 usage_metadata 和 response_metadata
    if chunk.usage_metadata:
        print(f"\nStream (final chunk) Usage: {chunk.usage_metadata}")
    if chunk.response_metadata:
        print(f"Stream (final chunk) Response Metadata: {chunk.response_metadata}")

print("\n--- End of Stream ---")
print("Full streamed content:", "".join(full_streamed_content))
```

### 4. 使用 `generate` API (批量处理)

`generate` 方法用于一次性处理多个消息列表（提示）。

```python
list_of_prompts = [
    [HumanMessage(content="天空为什么是蓝色的？")],
    [
        SystemMessage(content="你是一只猫。"),
        HumanMessage(content="你最喜欢吃什么？")
    ]
]

batch_response = llm.generate(list_of_prompts)

print("\nGenerate API (Batch) Response:")
for i, generation_result in enumerate(batch_response.generations):
    # ChatGeneration 包含 message (AIMessage) 和 generation_info
    chat_generation = generation_result[0] # 通常每个提示只有一个生成结果
    print(f"\nResponse for prompt {i+1}:")
    print(f"  Content: {chat_generation.message.content}")
    if chat_generation.message.usage_metadata:
        print(f"  Usage: {chat_generation.message.usage_metadata}")
    if chat_generation.message.response_metadata:
        print(f"  Response Metadata: {chat_generation.message.response_metadata}")
    if chat_generation.generation_info:
         print(f"  Generation Info: {chat_generation.generation_info}")

if batch_response.llm_output:
    print(f"\nLLM Output from generate: {batch_response.llm_output}")
```

### 消息格式

`ChatZhipuAI` 支持两种主要的消息输入格式：

- **字典列表**: 例如 `[{"role": "user", "content": "你好"}]`
- **`BaseMessage` 对象列表**: 例如 `[HumanMessage(content="你好")]` (推荐，更符合LangChain生态)

支持的角色包括 `system`, `user`, `assistant`, 以及通用的 `ChatMessage` (需要指定 `role`)。

## `ChatZhipuAI` 参数

初始化 `ChatZhipuAI` 时可以传递以下参数：

- `model_name` (str, 可选): 指定要使用的智谱AI模型名称。默认为 `"glm-4-plus"`。
- `temperature` (float, 可选): 控制生成文本的随机性。默认为 `None` (使用API的默认值)。
- `max_tokens` (int, 可选): 生成文本的最大长度。默认为 `None`。
- `timeout` (int, 可选): API请求的超时时间（秒）。默认为 `None`。
- `stop` (List[str], 可选): 一个或多个停止序列。默认为 `None`。
- `max_retries` (int, 可选): API请求失败时的最大重试次数。默认为 `3`。
- `api_key` (str, 可选): 你的智谱AI API密钥。如果未提供，则会尝试从环境变量 `ZHIPUAI_API_KEY` 中读取。

## 贡献

欢迎为此项目做出贡献！如果你发现任何bug或有改进建议，请随时提交Issue或Pull Request。

## 许可证

该项目使用 MIT 许可证。详情请参阅 `LICENSE` 文件 (如果存在)。
