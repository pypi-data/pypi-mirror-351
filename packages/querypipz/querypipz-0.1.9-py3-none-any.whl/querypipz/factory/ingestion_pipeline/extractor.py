

from enum import Enum
from llmada import BianXieAdapter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
)
from llama_index.core.extractors import BaseExtractor
from llama_index.core.schema import BaseNode
from typing import List, Dict, Any, Sequence
from pydantic import ConfigDict
import re

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
    TitleExtractor = 'TitleExtractor'
    QuestionsAnsweredExtractor = 'QuestionsAnsweredExtractor'
    CustomKeywordExtractor = "CustomKeywordExtractor"
    DeDaoJYRKTitleExtractor = "DeDaoJYRKTitleExtractor"
    HistoryMemoryKeywordExtractor = "HistoryMemoryKeywordExtractor"
    # 添加更多选项

class Extractor:
    def __new__(cls, type: ExtractorType) -> Any:
        assert type.value in [i.value for i in ExtractorType]
        instance = None

        if type.value == 'TitleExtractor':
            instance = TitleExtractor()

        elif type.value =="QuestionsAnsweredExtractor":
            instance = QuestionsAnsweredExtractor()

        elif type.value =="CustomKeywordExtractor":
            instance = CustomKeywordExtractor()

        elif type.value =="DeDaoJYRKTitleExtractor":
            instance = DeDaoJYRKTitleExtractor()

        else:
            raise TypeError('Unknown type')

        return instance

