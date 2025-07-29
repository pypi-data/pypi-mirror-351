""" builderlib """
import os

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import Settings

from llama_index.core import (
    load_index_from_storage,
    StorageContext,
    SimpleDirectoryReader,
    get_response_synthesizer,
)

from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
from llama_index.core.indices.property_graph.transformations import ImplicitPathExtractor,SimpleLLMPathExtractor,SchemaLLMPathExtractor, DynamicLLMPathExtractor

from .abc_ import QueryBuilder
from .factory.reader import Reader,ReaderType
from .factory.ingestion_pipeline import Splitter,SplitterType
from .factory.ingestion_pipeline import Cleaner,CleanerType, Embedding, EmbeddingType
from .factory.store import VectorStore,VectorStoreType

from .queryer import Queryer




# index.property_graph_store.save_networkx_graph(name="./kg3.html") # for debug

class ObsidianDateBuilder(QueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/date'):
        self.query = Queryer()
        self.query.persist_path = persist_path

    def build_reader(self):
        file_path= '/Users/zhaoxuefeng/GitHub/obsidian/工作/日记'
        self.query.reader = SimpleDirectoryReader(input_dir=file_path,
                                          file_extractor = {".md": Reader(ReaderType.ObsidianReaderCus)},
                                          recursive=True,
                                          )
    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(transformations=[Splitter(SplitterType.TokenTextSplitter),
                                                                           Embedding(EmbeddingType.OpenAIEmbedding),
                                                                           ])

    def build_storage_context(self):
        self.query.storage_context = StorageContext.from_defaults(vector_store=VectorStore(VectorStoreType.SimpleVectorStore))

    def build_index(self):
        self.query.index_type = "VectorStoreIndex"

    def build_retriver(self):
        self.query.retriever_Nest = None

    def build_query_pipeline(self):
        self.query.query_engine = None
        
    def get_queryer(self):
        return self.query
    
    def build_tools(self):
        pass

class ObsidianHabitBuilder(ObsidianDateBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/habit'):
        self.query = Queryer()
        self.query.persist_path = persist_path

    def build_reader(self):
        file_path= '/Users/zhaoxuefeng/GitHub/obsidian/工作/习惯'
        self.query.reader = SimpleDirectoryReader(input_dir=file_path,
                                          file_extractor = {".md": Reader(ReaderType.ObsidianReaderCus)},
                                          recursive=True,
                                          )
    def build_tools(self):
        pass

class DeDaoJYRKBuilder(QueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/JYRK'):
        self.query = Queryer()
        self.query.persist_path = persist_path

    def build_reader(self):
        file_path= '/Users/zhaoxuefeng/本地文稿/百度空间/实验广场/实验/work1'
        self.query.reader = SimpleDirectoryReader(input_dir=file_path,
                                          file_extractor = {".md": Reader(ReaderType.PDFFileReader)},
                                          recursive=True,
                                        #   exclude=["*.mp3"],
                                          )
    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(transformations=[Cleaner(CleanerType.DeDaoCleaner),
                                                                           Embedding(EmbeddingType.OpenAIEmbedding),
                                                                           ])

    def build_storage_context(self):
        self.query.storage_context = StorageContext.from_defaults(vector_store=VectorStore(VectorStoreType.FAISS))

    def build_index(self):
        self.query.index_type = "VectorStoreIndex"


    def build_retriver(self):
        self.query.retriever_Nest = None


    def build_query_pipeline(self):
        self.query.query_engine = None
        

    def get_queryer(self):
        return self.query
    
    def build_tools(self):
        pass

class TestGraphBuilder(QueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/TestGraph'):
        self.query = Queryer()
        self.query.persist_path = persist_path


    def set_llm(self):
        load_dotenv()
        api_key = os.getenv("BIANXIE_API_KEY")
        api_base = os.getenv("BIANXIE_BASE")
        Settings.llm = OpenAI(model="gpt-4.1",api_base=api_base,api_key=api_key)

    def build_reader(self):
        file_path= '/Users/zhaoxuefeng/本地文稿/百度空间/实验广场/实验/data/chat_history_demo_dongsheng'
        self.query.reader = SimpleDirectoryReader(input_dir=file_path,
                                          file_extractor = {".md": Reader(ReaderType.PDFFileReader)},
                                          recursive=True,
                                        #   exclude=["*.mp3"],
                                          )
    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(transformations=[])

    def build_storage_context(self):
        self.query.storage_context = StorageContext.from_defaults(vector_store=VectorStore(VectorStoreType.FAISS))

    def build_index(self):
        self.query.index_type = "PropertyGraphIndex"


    def build_retriver(self):
        self.query.retriever_Nest = None


    def build_query_pipeline(self):
        self.query.query_engine = None
        

    def get_queryer(self):
        return self.query
    
    def build_tools(self):
        def dynamic_method(self, name_path:str):
            return self.index.property_graph_store.save_networkx_graph(name=name_path) # for debug
        self.query.tools = dynamic_method.__get__(self.query,Queryer)



class Test2GraphBuilder(TestGraphBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/TestGraph2'):
        self.query = Queryer()
        self.query.persist_path = persist_path
        

    def build_kg_extractors(self):
        self.query.kg_extractors = [SimpleLLMPathExtractor(),
                                    ImplicitPathExtractor(),]
        

class HistoryMemoryBuilder(QueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/HistoryMemory'):
        self.query = Queryer()
        self.query.persist_path = persist_path

    def set_llm(self):
        pass

    def build_reader(self):
        self.query.reader = None

    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = None

    def build_storage_context(self):
        self.query.storage_context = None

    def build_index(self):
        self.query.index_type = "VectorStoreIndex"

    def build_retriver(self):
        self.query.retriever_Nest = None

    def build_query_pipeline(self):
        self.query.query_engine = None
        

    def get_queryer(self):
        return self.query
    
    def build_tools(self):
        self.query.tools = None

    def build_kg_extractors(self):
        self.query.kg_extractors = None
