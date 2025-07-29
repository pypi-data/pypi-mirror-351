""" abc """
from typing import Optional
from abc import ABC, abstractmethod
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex


class QueryerABC(ABC):
    """问答

    Args:
        ABC (_type_): query
    """
    def __init__(self):
        self.persist_path = None
        self.reader: Optional[SimpleDirectoryReader] = None
        self.ingestion_pipeline: Optional[IngestionPipeline] = None
        self.storage_context = None
        self.index_type = None
        self.retriever_nest = None
        self.query_pipeline = None
        self.retriever = None
        self.index: Optional[VectorStoreIndex] = None
        self.kg_extractors = None

    @abstractmethod
    def build(self):
        """Build the queryer components"""
        raise NotImplementedError

    @abstractmethod
    def query(self, prompt: str, similarity_top_k: int = 3):
        """Query the index with prompt"""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, query_text: str, similarity_top_k: int = 5):
        """Retrieve relevant documents"""
        raise NotImplementedError

    @abstractmethod
    def update(self, prompt: str):
        """Update the index"""
        raise NotImplementedError


class QueryBuilder(ABC):
    """QueryBuilder

    Args:
        ABC (_type_): _description_

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
    """
    @abstractmethod
    def set_llm(self):
        """Set the language model"""
        raise NotImplementedError

    @abstractmethod
    def build_reader(self):
        """Build document reader"""
        raise NotImplementedError

    @abstractmethod
    def build_ingestion_pipeline(self):
        """Build ingestion pipeline"""
        raise NotImplementedError

    @abstractmethod
    def build_storage_context(self):
        """Build storage context"""
        raise NotImplementedError

    @abstractmethod
    def build_index(self):
        """Build index"""
        raise NotImplementedError

    @abstractmethod
    def build_retriver(self):
        """Build retriever"""
        raise NotImplementedError

    @abstractmethod
    def build_query_pipeline(self):
        """Build query pipeline"""
        raise NotImplementedError

    @abstractmethod
    def get_queryer(self):
        """Get the built queryer"""
        raise NotImplementedError

    @abstractmethod
    def build_tools(self):
        """Build tools"""
        raise NotImplementedError

    @abstractmethod
    def build_kg_extractors(self):
        """Build knowledge graph extractors"""
        raise NotImplementedError
