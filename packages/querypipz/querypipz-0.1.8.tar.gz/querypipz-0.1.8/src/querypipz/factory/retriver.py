""" re"""
from enum import Enum
from typing import List, Any

class RetriverType(Enum):
    """Retriver

    Args:
        Enum (_type_): _description_
    """
    Simple = 'Simple'
    Simple2 = 'Simple2'
    # 添加更多选项

class Retriver:
    """_summary_
    """
    def __new__(cls, retriver_type: RetriverType) -> Any:
        assert retriver_type.value in [i.value for i in RetriverType]
        instance = None
        if retriver_type.value == 'Simple':
            pass
        elif retriver_type.value == 'Simple2':
            pass
        else:
            raise TypeError('Unknown type')
        return instance
