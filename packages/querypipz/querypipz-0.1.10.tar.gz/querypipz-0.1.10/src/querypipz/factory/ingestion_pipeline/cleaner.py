""" cleaner 文本清洗"""
import re
from enum import Enum
from typing import Any
from promptlibz import Templates,TemplateType
from llama_index.core.schema import TransformComponent
from llmada import BianXieAdapter

class DeDaoCleaner(TransformComponent):
    """专为得到设计的清理类

    Args:
        TransformComponent (_type_): _description_
    """
    def __call__(self, nodes, **kwargs):
        prompt = Templates(TemplateType.DedaoExtract)
        bx = BianXieAdapter()
        # bx = GoogleAdapter("AIzaSyBH4ut1plgB95fEiBlBXq1S-VrdYY5xPU4")
        for node in nodes:
            result = bx.product(prompt.format(text = node.text))
            node.set_content(self._extract_n_code(result))
        return nodes

    def _extract_n_code(self,text: str)->str:
        """从文本中提取python代码

        Args:
            text (str): 输入的文本。

        Returns:
            str: 提取出的python文本
        """
        pattern = r'```原文摘抄([\s\S]*?)```'
        matches = re.findall(pattern, text)
        return matches[0]

class CleanerType(Enum):
    """types
    """
    DE_DAO_CLEANER = 'DeDaoCleaner'
    # 添加更多选项

class Cleaner:
    """文本清洗
    """
    def __new__(cls, clean_type: CleanerType | str) -> Any:
        if isinstance(clean_type,CleanerType):
            assert clean_type.value in [i.value for i in CleanerType]
            key_name = clean_type.value
        else:
            assert clean_type in [i.value for i in CleanerType]
            key_name = clean_type
        instance = None

        if key_name == 'DeDaoCleaner':
            instance = DeDaoCleaner()

        else:
            raise TypeError('Unknown type')

        return instance
