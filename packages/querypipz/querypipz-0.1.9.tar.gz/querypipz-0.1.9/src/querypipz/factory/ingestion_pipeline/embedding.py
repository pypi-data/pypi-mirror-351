
from enum import Enum
from typing import List, Any
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter


class EmbeddingType(Enum):
    DefaultEmbedding = "DefaultEmbedding"
    OpenAIEmbedding = 'OpenAIEmbedding'
    Similaritytext3sEmbedding = "Similaritytext3sEmbedding"
    Similaritytext3lEmbedding = "Similaritytext3lEmbedding"
    Searchtext3sEmbedding = "Searchtext3sEmbedding"
    Searchtext3lEmbedding = "Searchtext3lEmbedding"

    Simple2 = 'Simple2'
    # 添加更多选项

class Embedding:
    def __new__(cls, type: EmbeddingType) -> Any:
        assert type.value in [i.value for i in EmbeddingType]
        instance = None

        if type.value == 'DefaultEmbedding':
            instance = Settings.embed_model

        elif type.value == 'Similaritytext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-small',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)

        elif type.value == 'Similaritytext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-large',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)
            
        elif type.value == 'Searchtext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search', 
                 model='text-embedding-3-small',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)

        elif type.value == 'Searchtext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search', 
                 model='text-embedding-3-large',
                 api_base=Settings.api_base,
                 api_key=Settings.api_key)


        elif type.value == 'OpenAIEmbedding':
            instance = OpenAIEmbedding(api_base=Settings.api_base,
                                       api_key=Settings.api_key)

        elif type.value == 'Simple2':
            instance = SentenceSplitter(chunk_size=512, chunk_overlap=10)
        else:
            raise Exception('Unknown type')

        return instance

