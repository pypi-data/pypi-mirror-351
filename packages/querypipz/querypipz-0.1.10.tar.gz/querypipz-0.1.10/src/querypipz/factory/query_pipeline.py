from enum import Enum
from typing import List, Any


class QueryType(Enum):
    Simple = 'Simple'
    Simple2 = 'Simple2'
    # 添加更多选项

class Query:
    def __new__(cls, type: QueryType) -> Any:
        assert type.value in [i.value for i in QueryType]
        instance = None

        if type.value == 'Simple':

            # instance = SomeClass(param1=value1, param2=value2)
            pass

        elif type.value == 'Simple2':

            # instance = AnotherClass(param1=value1, param2=value2)
            pass


        else:
            raise Exception('Unknown type')

        return instance


# def build_query_pipeline(self):
#     # configure response synthesizer
#     response_synthesizer = get_response_synthesizer()

#     # assemble query engine
#     query_engine = RetrieverQueryEngine(
#         retriever=self.query.retriver,
#         response_synthesizer=response_synthesizer,
#         node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
#     )
#     self.query_pipeline = query_engine


############ VVVVVV##########
# 定义提示模板字符串
template_str = """
Take a deep breath and work on this problem step-by-step

您是一个Python工程师, 我会提供给您一些已验证可用的代码(防止出现包版本过旧,或者环境不支持的情况),
在代码编写中,如果被验证代码块中存在相关内容,您应该尽可能的使用被验证的代码, 而非经验.
基于用户的需求和提供的已验证代码, 结合自己的经验,编写代码.
您编写的代码应该封装成函数或者类


已验证代码:
---
```python
{safe_code}
```
---

用户的诉求:
{prompt}

输出函数:
"""

# 创建PromptTemplate实例
qa_prompt = PromptTemplate(template=template_str)


class PythonQueryEngine(CustomQueryEngine):
    """RAG String Query Engine."""

    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: OpenAI
    qa_prompt: PromptTemplate
    stream:bool

    def custom_query(self, query_str: str):
        # custom_query(query_str: str) -> STR_OR_RESPONSE_TYPE
        # acustom_query(query_str: str) -> STR_OR_RESPONSE_TYPE

        queries = query_str.split('&')
        nodes = []
        for query_str in queries:
            nodes += self.retriever.retrieve(query_str)
        # nodes = self.retriever.retrieve(query_str)
        print(query_str,'query_str')
        context_str = "\n\n".join([n.node.get_metadata_str() for n in nodes])
        if self.stream:
            response = self.llm.stream_complete(
                qa_prompt.format(safe_code=context_str, prompt=query_str)
            )

            def response_gen():
                i = [0]
                for r in response:
                    i.append(len(str(r)))
                    yield str(r)[i[-2]:]

            return StreamingResponse(response_gen=response_gen(),source_nodes=nodes)
        else:
            response = self.llm.complete(qa_prompt.format(safe_code=context_str, prompt=query_str))
    
            response_obj = self.response_synthesizer.synthesize(response.text, nodes)
            return Response(response=response.text,source_nodes=nodes) # TODO 增加metadata



# 具体生成器
class QueryBuilder3(QueryBuilder):
    '''


    '''
   

    def get_query(self):
        # 例如：
            # instance = AnotherClass(param1=value1, param2=value2)
        
        
        retriever = index.as_retriever(similarity_top_k=similarity_top_k)
        query_engine = PythonQueryEngine(
                retriever=retriever,
                response_synthesizer=get_response_synthesizer(response_mode="compact"),
                llm=Settings.llm,
                qa_prompt=qa_prompt,
                stream = True,
            )

        return query_engine
