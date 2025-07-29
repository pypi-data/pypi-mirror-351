""" queryer.py """
import os
from llama_index.core import (
    load_index_from_storage,
    StorageContext,
    VectorStoreIndex,
    PropertyGraphIndex,
    Document,
)
from .abc_ import QueryerABC



class Queryer(QueryerABC):
    """query类

    Args:
        QueryerABC (_type_): _description_
    """
    def __init__(self):
        super().__init__()
        self.persist_path = None
        self.reader = None
        self.ingestion_pipeline = None
        self.storage_context = None
        self.index_type = None
        self.retriever_nest = None
        self.query_pipeline = None
        self.retriever = None
        self.index = None
        self.kg_extractors = None

    def load(self):
        """_summary_
        """
        assert 1==1
        storage_context = StorageContext.from_defaults(persist_dir=self.persist_path)
        self.index = load_index_from_storage(storage_context=storage_context)

    def update(self, prompt: str):
        self.load()
        self.index.insert(Document(text = prompt))
        self.index.storage_context.persist(self.persist_path)

    def build(self):
        if self.reader is None:
            # raise ValueError("Reader is not set. Call build_reader first.")
            if self.index_type == "VectorStoreIndex":
                self.index = VectorStoreIndex.from_documents([Document(text='start')],storage_context=self.storage_context)
                self.index.storage_context.persist(self.persist_path)
                return 'builded'
            else:
                raise ValueError("Reader is not set. Call build_reader first.")

        documents = self.reader.load_data()
        nodes = None
        if self.ingestion_pipeline:
            nodes = self.ingestion_pipeline.run(documents=documents)


        if nodes:
            if self.index_type == "VectorStoreIndex":
                self.index = VectorStoreIndex(nodes,storage_context = self.storage_context)
                # self.index = PropertyGraphIndex(nodes,storage_context = self.storage_context,
                #                                              show_progress=True,)

        else:
            if self.index_type == "VectorStoreIndex":
                self.index = VectorStoreIndex(nodes,storage_context = self.storage_context)

            elif self.index_type == "PropertyGraphIndex":
                self.index = PropertyGraphIndex.from_documents(
                                                            documents=documents,
                                                            show_progress=True,
                                                            kg_extractors = self.kg_extractors,
                                                            # embed_kg_nodes = False,
                                                            )
        self.index.storage_context.persist(self.persist_path)
        
        return 'builded'

    def get_retriever(self, similarity_top_k: int = 5):
        """
        获取检索器（Retriever），如有必要则从持久化目录加载索引。
        """
        if self.retriever is not None:
            return self.retriever

        if not self.persist_path or not os.path.exists(self.persist_path):
            raise ValueError("索引持久化目录不存在，无法构建检索器。")

        storage_context = StorageContext.from_defaults(persist_dir=self.persist_path)
        self.index = load_index_from_storage(storage_context=storage_context)
        self.retriever = self.index.as_retriever(similarity_top_k=similarity_top_k,
                                                 include_text=False,
                                                 )
        return self.retriever

    def retrieve(self, query_text: str, similarity_top_k: int = 5):
        """
        使用检索器进行检索。
        """
        retriever = self.get_retriever(similarity_top_k=similarity_top_k)
        return retriever.retrieve(query_text)

    def get_query_engine(self, similarity_top_k: int = 3):
        """
        获取查询引擎（QueryEngine），如有必要则从持久化目录加载索引。
        """
        if self.query_engine is not None:
            return self.query_engine

        if not self.persist_path or not os.path.exists(self.persist_path):
            raise ValueError("索引持久化目录不存在，无法构建查询引擎。")

        storage_context = StorageContext.from_defaults(persist_dir=self.persist_path)
        self.index = load_index_from_storage(storage_context=storage_context)
        self.query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k,
                                                       include_text=True,)
        return self.query_engine

    def query(self, prompt: str, similarity_top_k: int = 3):
        """
        执行查询。
        """
        query_engine = self.get_query_engine(similarity_top_k=similarity_top_k)
        return query_engine.query(prompt)
