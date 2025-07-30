""" embedding """
from enum import Enum
from typing import Any
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

class EmbeddingType(Enum):
    """enum
    """
    DefaultEmbedding = "DefaultEmbedding"
    OpenAIEmbedding = 'OpenAIEmbedding'
    Similaritytext3sEmbedding = "Similaritytext3sEmbedding"
    Similaritytext3lEmbedding = "Similaritytext3lEmbedding"
    Searchtext3sEmbedding = "Searchtext3sEmbedding"
    Searchtext3lEmbedding = "Searchtext3lEmbedding"

    # 添加更多选项

class Embedding:
    """embedding 方案
    """
    def __new__(cls, emb_type: EmbeddingType | str) -> Any:
        if isinstance(emb_type,EmbeddingType):
            assert emb_type.value in [i.value for i in EmbeddingType]
            key_name = emb_type.value
        else:
            assert emb_type in [i.value for i in EmbeddingType]
            key_name = emb_type

        instance = None

        if key_name == 'DefaultEmbedding':
            instance = Settings.embed_model

        elif key_name == 'Similaritytext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-small',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)

        elif key_name == 'Similaritytext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-large',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)

        elif key_name == 'Searchtext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search',
                 model='text-embedding-3-small',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)

        elif key_name == 'Searchtext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search',
                 model='text-embedding-3-large',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)


        elif key_name == 'OpenAIEmbedding':
            instance = OpenAIEmbedding(api_base=Settings.api_base,
                                       api_key=Settings.api_key)

        else:
            raise TypeError('Unknown type')

        return instance
