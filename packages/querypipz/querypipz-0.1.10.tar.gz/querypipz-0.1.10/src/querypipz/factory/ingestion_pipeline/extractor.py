""" extractor """
import re
from enum import Enum
from typing import List, Dict, Any, Sequence
from llmada import BianXieAdapter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
)
from llama_index.core.extractors import BaseExtractor
from llama_index.core.schema import BaseNode

from pydantic import ConfigDict

class CustomKeywordExtractor(BaseExtractor):
    """自定义关键词提取器"""
    model_config = ConfigDict(extra='allow')

    def __init__(self, keywords: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.keywords = keywords or [
            "习惯化", "快乐", "痛苦", "幸福感", "满足", 
            "间隔", "集中", "游戏", "度假", "结婚"
        ]

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """异步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """同步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """从单个节点提取信息"""
        text = node.get_content()
        print(text,'text')
        # 提取关键词
        found_keywords = []
        for keyword in self.keywords:
            if keyword in text:
                found_keywords.append(keyword)

        # 统计关键词频率
        keyword_freq = {}
        for keyword in found_keywords:
            keyword_freq[keyword] = text.count(keyword)

        # 提取数字信息
        numbers = re.findall(r'\d+', text)

        return {
            "keywords_found": found_keywords,
            "keyword_frequency": keyword_freq,
            "numbers_mentioned": numbers,
            "keyword_density": len(found_keywords) / len(text.split()) if text.split() else 0
        }

class DeDaoJYRKTitleExtractor(BaseExtractor):
    """自定义关键词提取器"""

    model_config = ConfigDict(extra='allow')

    def __init__(self, keywords: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.keywords = keywords or [
            "习惯化", "快乐", "痛苦", "幸福感", "满足", 
            "间隔", "集中", "游戏", "度假", "结婚"
        ]

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """异步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """同步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """从单个节点提取信息"""
        text = node.get_content()
        # print(text,'text')
        p = text.replace('\n','', 1) if text.startswith('\n') else text
        cal = p.split('\n',1)[0]
        return {
            "titie_cal": cal}

class HistoryMemoryKeywordExtractor(BaseExtractor):
    """自定义关键词提取器"""

    model_config = ConfigDict(extra='allow')

    def __init__(self, keywords: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.keywords = keywords or [
            "习惯化", "快乐", "痛苦", "幸福感", "满足", 
            "间隔", "集中", "游戏", "度假", "结婚"
        ]

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """异步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """同步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """从单个节点提取信息"""
        text = node.get_content()
        print(text,'text')
        # 提取关键词
        found_keywords = []
        for keyword in self.keywords:
            if keyword in text:
                found_keywords.append(keyword)

        bx = BianXieAdapter()
        result = bx.product(f"""
帮我从下列文本中提取出关键词,并输出
{text}

关键词:
""")
        return {
            "keywords_found": found_keywords,
            "keywords":result,
        }

class ExtractorType(Enum):
    """ extra """
    TitleExtractor = 'TitleExtractor'
    QuestionsAnsweredExtractor = 'QuestionsAnsweredExtractor'
    CustomKeywordExtractor = "CustomKeywordExtractor"
    DeDaoJYRKTitleExtractor = "DeDaoJYRKTitleExtractor"
    HistoryMemoryKeywordExtractor = "HistoryMemoryKeywordExtractor"
    # 添加更多选项

class Extractor:
    """extractor
    """
    def __new__(cls, extra_type: ExtractorType | str) -> Any:

        if isinstance(extra_type,ExtractorType):
            assert extra_type.value in [i.value for i in ExtractorType]
            key_name = extra_type.value
        else:
            assert extra_type in [i.value for i in ExtractorType]
            key_name = extra_type
        instance = None

        if key_name == 'TitleExtractor':
            instance = TitleExtractor()

        elif key_name =="QuestionsAnsweredExtractor":
            instance = QuestionsAnsweredExtractor()

        elif key_name =="CustomKeywordExtractor":
            instance = CustomKeywordExtractor()

        elif key_name =="DeDaoJYRKTitleExtractor":
            instance = DeDaoJYRKTitleExtractor()

        elif key_name =="HistoryMemoryKeywordExtractor":
            instance = HistoryMemoryKeywordExtractor()

        else:
            raise TypeError('Unknown type')

        return instance




########


from llama_index.core.graph_store.types import (
    EntityNode,
    Relation,
    KG_NODES_KEY,
    KG_RELATIONS_KEY,
)
from llama_index.core.schema import BaseNode, TransformComponent

from enum import Enum
from typing import Any
from llama_index.core.indices.property_graph.transformations import ImplicitPathExtractor,SchemaLLMPathExtractor,SimpleLLMPathExtractor, DynamicLLMPathExtractor




class MyGraphExtractor(TransformComponent):
    # the init is optional
    # def __init__(self, ...):
    #     ...

    def __call__(
        self, llama_nodes: list[BaseNode], **kwargs
    ) -> list[BaseNode]:
        for llama_node in llama_nodes:
            # be sure to not overwrite existing entities/relations

            existing_nodes = llama_node.metadata.pop(KG_NODES_KEY, [])
            existing_relations = llama_node.metadata.pop(KG_RELATIONS_KEY, [])

            existing_nodes.append(
                EntityNode(
                    name="llama", label="ANIMAL", properties={"key": "val"}
                )
            )
            existing_nodes.append(
                EntityNode(
                    name="index", label="THING", properties={"key": "val"}
                )
            )

            existing_relations.append(
                Relation(
                    label="HAS",
                    source_id="llama",
                    target_id="index",
                    properties={},
                )
            )

            # add back to the metadata

            llama_node.metadata[KG_NODES_KEY] = existing_nodes
            llama_node.metadata[KG_RELATIONS_KEY] = existing_relations

        return llama_nodes

    # optional async method
    # async def acall(self, llama_nodes: list[BaseNode], **kwargs) -> list[BaseNode]:
    #    ...



class GraphExtractorType(Enum):
    MyGraphExtractor = 'MyGraphExtractor'
    DynamicLLMPathExtractor = "DynamicLLMPathExtractor"
    DynamicLLMPathExtractor2 = "DynamicLLMPathExtractor2"
    SchemaLLMPathExtractor = "SchemaLLMPathExtractor"
    SimpleLLMPathExtractor = "SimpleLLMPathExtractor"
    ImplicitPathExtractor = "ImplicitPathExtractor"
    # Add more options as needed


class GraphExtractor:
    def __new__(cls, type: GraphExtractorType) -> Any:
        assert type.value in [i.value for i in GraphExtractorType]
        instance = None

        if type.value == 'MyGraphExtractor':
            instance = MyGraphExtractor()

        elif type.value == 'MyGraphExtractor':
            instance = MyGraphExtractor()
        elif type.value == 'MyGraphExtractor':
            instance = MyGraphExtractor()

        elif type.value == 'SimpleLLMPathExtractor':
            instance = SimpleLLMPathExtractor()
        elif type.value == 'ImplicitPathExtractor':
            instance = ImplicitPathExtractor()
            
        elif type.value == 'DynamicLLMPathExtractor':
            instance = DynamicLLMPathExtractor(
                                                max_triplets_per_chunk=20,
                                                num_workers=4,
                                                allowed_entity_types=["POLITICIAN", "POLITICAL_PARTY"],
                                                allowed_relation_types=["PRESIDENT_OF", "MEMBER_OF"],
                                                allowed_relation_props=["description"],
                                                allowed_entity_props=["description"],
                                            )
            
        elif type.value == 'DynamicLLMPathExtractor2':
            instance  = DynamicLLMPathExtractor(
                                                max_triplets_per_chunk=20,
                                                num_workers=4,
                                                # Let the LLM infer entities and their labels (types) on the fly
                                                allowed_entity_types=None,
                                                # Let the LLM infer relationships on the fly
                                                allowed_relation_types=None,
                                                # LLM will generate any entity properties, set `None` to skip property generation (will be faster without)
                                                allowed_relation_props=[],
                                                # LLM will generate any relation properties, set `None` to skip property generation (will be faster without)
                                                allowed_entity_props=[],
                                            )
        elif type.value == 'SchemaLLMPathExtractor':
            instance = SchemaLLMPathExtractor(
                                            llm = llm,
                                            max_triplets_per_chunk=20,
                                            strict=False,  # Set to False to showcase why it's not going to be the same as DynamicLLMPathExtractor
                                            possible_entities=None,  # USE DEFAULT ENTITIES (PERSON, ORGANIZATION... etc)
                                            possible_relations=None,  # USE DEFAULT RELATIONSHIPS
                                            possible_relation_props=[
                                                "extra_description"
                                            ],  # Set to `None` to skip property generation
                                            possible_entity_props=[
                                                "extra_description"
                                            ],  # Set to `None` to skip property generation
                                            num_workers=4,
                                            )
            
        else:
            raise Exception('Unknown type')

        return instance









