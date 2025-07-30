import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from langchain_zhipuai_dev import version
from langchain_zhipuai_dev.chat import ChatZhipuAI


def main():
    print(version())
    zp = ChatZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))

    print("--- Using invoke API ---")
    # 可以使用字典列表或 BaseMessage 对象列表
    messages_input_dict = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好呀"},
        {"role": "user", "content": "你是谁？"},
    ]

    # 或者使用 BaseMessage 对象
    messages_input_lc = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="你好"),
        AIMessage(content="你好呀"),
        HumanMessage(content="你是谁？"),
    ]

    # 调用 invoke API
    # stop 参数可以直接传递给 invoke
    # config 参数可以用于更高级的配置，例如回调
    response_invoke = zp.invoke(messages_input_dict, stop=["你是谁？"])
    print(f"Invoke API response type: {type(response_invoke)}")
    print(f"Invoke API response content: {response_invoke.content}")
    print(f"Invoke API response usage_metadata: {response_invoke.usage_metadata}")
    print(f"Invoke API response response_metadata: {response_invoke.response_metadata}")
    print("-" * 20)

    print("\n--- Using stream API ---")
    # 调用 stream API
    # stop 参数可以直接传递给 stream
    stream_response = zp.stream(messages_input_lc, stop=["你是谁？"])

    full_streamed_content = []
    print("Stream API response content: ", end="", flush=True)
    for chunk in stream_response:
        print(chunk.content, end="", flush=True)
        full_streamed_content.append(chunk.content)
        # AIMessageChunk 包含 content, additional_kwargs, response_metadata, usage_metadata, id
        # 最后一个 chunk 通常包含 usage_metadata
        if chunk.usage_metadata:
            print(f"\nStream API (final chunk) usage_metadata: {chunk.usage_metadata}")
        if chunk.response_metadata:
            print(
                f"\nStream API (final chunk) response_metadata: {chunk.response_metadata}"
            )

    print("\nFull streamed content: ", "".join(full_streamed_content))
    print("-" * 20)

    # 演示 generate API (用于批量处理)
    print("\n--- Using generate API (batch) ---")
    list_of_messages = [
        [HumanMessage(content="Tell me a joke about a cat.")],
        [
            SystemMessage(content="You are a pirate."),
            HumanMessage(content="What's your favorite treasure?"),
        ],
    ]
    generate_response = zp.generate(list_of_messages)
    for i, res_gen in enumerate(generate_response.generations):
        print(f"\nResponse for prompt {i+1}:")
        # ChatGeneration 包含 message (AIMessage) 和 generation_info
        print(f"  Content: {res_gen[0].message.content}")
        print(f"  Usage Metadata: {res_gen[0].message.usage_metadata}")
        print(f"  Response Metadata: {res_gen[0].message.response_metadata}")
        if res_gen[0].generation_info:
            print(f"  Generation Info: {res_gen[0].generation_info}")
    print(f"LLM Output from generate: {generate_response.llm_output}")
    print("-" * 20)


if __name__ == "__main__":
    main()
