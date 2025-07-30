from typing import List, Optional

from langchain_core.embeddings import Embeddings
from pydantic import SecretStr
from zhipuai import ZhipuAI


class ZhipuAIEmbeddings(Embeddings):
    """智谱 AI Embeddings.
    该类使用智谱 AI 的嵌入模型来生成文本的嵌入向量。
    Attributes:
        model (str): 嵌入模型的名称，默认为 "embedding-3"。
        client (ZhipuAI): ZhipuAI 客户端实例，用于调用嵌入 API。
    """

    model: str
    client: ZhipuAI

    def __init__(self, api_key: Optional[SecretStr], model: str = "embedding-3"):
        self.model = model
        self.client = ZhipuAI(api_key=api_key.get_secret_value() if api_key else None)

    def embed_documents(self, texts: List[str]):
        """嵌入一组文档。
        Args:
            texts (List[str]): 要嵌入的文本列表。
        Returns:
            List[List[float]]: 每个文本的嵌入向量列表。
        """
        result = []
        for i in range(0, len(texts), 64):
            embeddings = self.client.embeddings.create(
                model=self.model, input=texts[i : i + 64]
            )
            result.extend([embeddings.embedding for embeddings in embeddings.data])
        return result

    def embed_query(self, text: str):
        """嵌入查询文本。
        Args:
            text (str): 要嵌入的查询文本。
        Returns:
            List[float]: 查询文本的嵌入向量。
        """
        return self.embed_documents([text])[0]
