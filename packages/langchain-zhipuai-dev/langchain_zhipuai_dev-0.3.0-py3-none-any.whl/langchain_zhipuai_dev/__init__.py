from importlib.metadata import version as get_version

from .chat import ChatZhipuAI
from .embedding import ZhipuAIEmbeddings


def version() -> str:
    return get_version("langchain-zhipuai-dev")
