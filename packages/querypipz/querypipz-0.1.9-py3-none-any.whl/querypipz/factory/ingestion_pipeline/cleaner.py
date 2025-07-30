
from enum import Enum
from typing import List, Any
from llama_index.core.node_parser import SentenceSplitter
from llmada import BianXieAdapter
from llama_index.core.schema import TransformComponent
from promptlibz import Templates,TemplateType
from llama_index.core.text_splitter import SentenceSplitter

import re


class DeDaoCleaner(TransformComponent):
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
    DeDaoCleaner = 'DeDaoCleaner'
    Simple2 = 'Simple2'
    # 添加更多选项

class Cleaner:
    def __new__(cls, type: CleanerType) -> Any:
        assert type.value in [i.value for i in CleanerType]
        instance = None

        if type.value == 'DeDaoCleaner':
            instance = DeDaoCleaner()

        elif type.value == 'Simple2':
            instance = SentenceSplitter(chunk_size=512, chunk_overlap=10)
        else:
            raise Exception('Unknown type')

        return instance
