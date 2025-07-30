
from enum import Enum
from typing import List, Any
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core.node_parser import CodeSplitter
import re


class CustomTextSplitter(SentenceSplitter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, **kwargs):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )
    
    def split_text(self, text: str) -> List[str]:
        """
        自定义分割逻辑
        """
        chunks = []
        
        # 按段落分割
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # 保留重叠部分
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_text + paragraph
                else:
                    current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


class DeDaoJYRKTextSplitter(SentenceSplitter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, **kwargs):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        _Split incoming text and return chunks with overlap size.

        Has a preference for complete sentences, phrases, and minimal overlap.
        """
        # text : str
        if text == "":
            return [text]

#         with self.callback_manager.event(
#             CBEventType.CHUNKING, payload={EventPayload.CHUNKS: [text]}
#         ) as event:
#             splits = self._split(text, chunk_size)
#             chunks = self._merge(splits, chunk_size)

#             event.on_end(payload={EventPayload.CHUNKS: chunks})
        chunks = text.split('\n\n')        
        return chunks# list[str]

class HistoryMemorySplitter(SentenceSplitter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, **kwargs):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )

    def split_qa_strings(self,text):
        """
        将包含 user: 和 assistant: 标记的文本拆分成一对一对的问答对字符串。

        Args:
        text: 包含问答对的字符串。

        Returns:
        一个列表，其中每个元素都是一个字符串，包含一个完整的问答对
        （从 user: 开始到其对应的 assistant: 结束）。
        如果存在不成对的 user 或 assistant，它们将被忽略。
        """
        # 使用正则表达式找到所有 user: ... assistant: ... 的完整对
        # non-greedy match for user: content, followed by assistant: and its content
        pattern = re.compile(r"user:.*?assistant:.*?(?=user:|$)", re.S)
        matches = pattern.findall(text)

        qa_strings = []
        for match in matches:
            qa_strings.append(match.strip()) # 将匹配到的完整问答对字符串添加到列表中

        return qa_strings
   
    def split_text(self, text: str) -> List[str]:
        """
        自定义分割逻辑
        """
        if text == "":
            return [text]
        
        # 按段落分割
        chunks = self.split_qa_strings(text)
     
        return chunks# list[str]
        

class SplitterType(Enum):
    Simple = 'Simple'
    CodeSplitter = 'CodeSplitter'
    TokenTextSplitter = "TokenTextSplitter"
    CustomTextSplitter = "CustomTextSplitter"
    DeDaoJYRKTextSplitter = "DeDaoJYRKTextSplitter"
    HistoryMemorySplitter = "HistoryMemorySplitter"
    # 添加更多选项

class Splitter:
    def __new__(cls, type: SplitterType) -> Any:
        assert type.value in [i.value for i in SplitterType]
        instance = None

        if type.value == 'Simple':
            instance = SentenceSplitter(chunk_size=4096)

        elif type.value =="CustomTextSplitter":
            instance = CustomTextSplitter()

        elif type.value =="DeDaoJYRKTextSplitter":
            instance = DeDaoJYRKTextSplitter()


        elif type.value == 'CodeSplitter':
            splitter = CodeSplitter(
                language="python",
                chunk_lines=40,  # lines per chunk
                chunk_lines_overlap=15,  # lines overlap between chunks
                max_chars=1500,  # max chars per chunk
            )
            instance = splitter

        elif type.value == 'TokenTextSplitter':
            instance = TokenTextSplitter()

        elif type.value == "HistoryMemorySplitter":
            instance = HistoryMemorySplitter()
            
        else:
            raise Exception('Unknown type')

        return instance
