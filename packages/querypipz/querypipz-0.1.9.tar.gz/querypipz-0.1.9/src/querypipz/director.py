''' 指挥者与建造者'''
from enum import Enum
from typing import Any

from .abc_ import QueryBuilder
from .builderlib import *

# 指挥者
class Director:
    """指挥者
    """
    def __init__(self, builder:QueryBuilder):
        self.builder = builder

    def construct(self):
        """开始建造

        Returns:
            返回queryer: 建造成功的产品
        """
        self.builder.set_llm()
        self.builder.build_reader()
        self.builder.build_ingestion_pipeline()
        self.builder.build_storage_context()
        self.builder.build_index()
        self.builder.build_retriver()
        self.builder.build_query_pipeline()
        self.builder.build_tools()
        self.builder.build_kg_extractors()
        return self.builder.get_queryer()

class BuilderType(Enum):
    """构造者清单

    Args:
        Enum (_type_): 选择构造者
    """
    ObsidianDateBuilder = 'ObsidianDateBuilder'
    ObsidianHabitBuilder = "ObsidianHabitBuilder"
    DeDaoJYRKBuilder = "DeDaoJYRKBuilder"
    DeDaoJYRK2Builder = "DeDaoJYRK2Builder"
    DeDaoJYRK6Builder = "DeDaoJYRK6Builder"
    TestGraphBuilder = "TestGraphBuilder"
    Test2GraphBuilder = "Test2GraphBuilder"
    HistoryMemoryBuilder = "HistoryMemoryBuilder"
    HistoryMemory2Builder = "HistoryMemory2Builder"
    simple = 'simple'
    # 添加更多选项

class BuilderFactory:
    """构造者工厂

    Raises:
        ValueError: _description_

    Returns:
        builder: 构造者
    """
    _builders = {
        BuilderType.ObsidianDateBuilder: ObsidianDateBuilder,
        BuilderType.ObsidianHabitBuilder: ObsidianHabitBuilder,
        BuilderType.DeDaoJYRKBuilder: DeDaoJYRKBuilder,
        BuilderType.DeDaoJYRK2Builder: DeDaoJYRK2Builder,
        BuilderType.DeDaoJYRK6Builder: DeDaoJYRK6Builder,
        BuilderType.TestGraphBuilder: TestGraphBuilder,
        BuilderType.Test2GraphBuilder: Test2GraphBuilder,
        BuilderType.HistoryMemoryBuilder: HistoryMemoryBuilder,
        BuilderType.HistoryMemory2Builder: HistoryMemory2Builder,
    }

    def __new__(cls, builder_type: BuilderType,persist_path=None) -> Any:
        if builder_type not in cls._builders:
            raise ValueError(f"Unknown builder type: {builder_type}")
        builder_class = cls._builders[builder_type]
        if persist_path:
            instance = builder_class(persist_path = persist_path)
        else:
            instance = builder_class()
        return instance
