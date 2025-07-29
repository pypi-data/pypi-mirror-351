# supertree/node.py 파일을 이 코드로 교체합니다.
from typing import List, Optional, Union, Dict
import numpy as np
import pandas as pd

class Node:
    """Node in a decision tree (modified for N-ary children based on child_indices)."""

    def __init__(
        self,
        feature: Union[int, str],
        threshold: Union[float, list], # 타입 변경
        impurity: float,
        samples: int,
        class_distribution: Optional[List[List[Union[int, float]]]],
        predicted_class: Union[str, int, float],
        is_leaf: bool,
        child_indices: Optional[List[int]] = None, # left/right 대신 사용
        is_categorical: bool = False,
        _children_map: Optional[Dict[str, int]] = None, # 맵 정보는 일단 유지
        treeclass: Optional[Union[str, int, float]] = None
    ):
        self.feature = feature
        self.threshold = threshold
        self.impurity = impurity
        self.samples = samples
        self.class_distribution = class_distribution
        self.predicted_class = predicted_class
        self.is_leaf = is_leaf
        self.child_indices = child_indices if child_indices is not None else [] # 입력된 child_indices 저장

        self.parent: Optional['Node'] = None
        self.children_nodes: List['Node'] = [] # 실제 자식 Node 객체 리스트

        self.is_categorical: bool = is_categorical
        self._children_map: Optional[Dict[str, int]] = _children_map # 카테고리->자식ID 맵 (선택적)
        self.treeclass = treeclass

        self.start_end_x_axis = []

    def add_child(self, node: 'Node'): # add_left/right 대신
        """Add a child node."""
        if node:
            self.children_nodes.append(node)
            node.parent = self

    def to_dict(self):
        """Convert node data to a dictionary (재귀적, JSON 호환, N-ary children)."""

        def convert_to_python_type(value):
            # NumPy 2.0 호환 타입 변환 함수 (이전 답변 내용)
            if isinstance(value, (np.intc, np.intp, np.int8,
                                np.int16, np.int32, np.int64, np.uint8,
                                np.uint16, np.uint32, np.uint64)):
                return int(value)
            elif isinstance(value, (np.float16, np.float32, np.float64)):
                return float(value)
            elif isinstance(value, (np.complex64, np.complex128)):
                return {'real': float(value.real), 'imag': float(value.imag)}
            elif isinstance(value, np.ndarray):
                 return [convert_to_python_type(v) for v in value.tolist()]
            elif isinstance(value, list):
                 return [convert_to_python_type(v) for v in value]
            elif isinstance(value, (np.bool_)):
                 return bool(value)
            elif isinstance(value, (np.bytes_, np.str_)):
                 if isinstance(value, np.bytes_):
                     try: return value.decode('utf-8')
                     except UnicodeDecodeError: return repr(value)
                 else: return str(value)
            elif isinstance(value, bytes):
                 try: return value.decode('utf-8')
                 except UnicodeDecodeError: return repr(value)
            return value

        node_dict = {
            "feature": convert_to_python_type(self.feature),
            "threshold": convert_to_python_type(self.threshold),
            "impurity": convert_to_python_type(self.impurity),
            "samples": convert_to_python_type(self.samples),
            "class_distribution": convert_to_python_type(self.class_distribution),
            "predicted_class": convert_to_python_type(self.predicted_class),
            "is_leaf": self.is_leaf,
            "start_end_x_axis": convert_to_python_type(self.start_end_x_axis),
            "is_categorical": getattr(self, 'is_categorical', False),
            "treeclass": convert_to_python_type(getattr(self, 'treeclass', None)),
            # "child_indices": self.child_indices, # 최종 JSON에는 children 사용
        }

        if self.children_nodes: # DFS에서 채워진 children_nodes 사용
            node_dict["children"] = [child.to_dict() for child in self.children_nodes if child]
        # else: # 리프 노드는 children 키 없음

        return node_dict