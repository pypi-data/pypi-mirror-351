# supertree/model_loader.py 파일을 아래 내용으로 수정합니다.

import pandas as pd
import numpy as np

class ModelLoader():
    """
    Load model that is in list of dicts format.
    Modified to accept 'child_indices' instead of left/right child indices
    and list-based 'threshold'.
    """
    def __init__(self, model_type, model_dict_list):
        self.model_type = model_type
        # self.model_dict = model_dict_list # 검증 후 할당하도록 변경

        # 변경된 필수 키 정의: left/right 대신 child_indices 포함
        required_keys = {"index", "feature", "impurity", "threshold",
                         "class_distribution", "predicted_class",
                         "samples", "is_leaf", "child_indices"}

        # 선택적 키 (있어도 되고 없어도 됨)
        optional_keys = {"treeclass", "is_categorical", "_children_map"}

        # model_dict_list 타입 검증
        if not isinstance(model_dict_list, list):
            raise TypeError("model_dict_list must be a list of dictionaries.")

        validated_list = []
        # 각 딕셔너리 아이템 검증
        for i, item in enumerate(model_dict_list):
            if not isinstance(item, dict):
                raise TypeError(f"Item at index {i} in model_dict_list must be a dictionary.")

            # 수정된 필수 키 확인
            if not required_keys.issubset(item.keys()):
                missing_keys = required_keys - item.keys()
                raise ValueError(f"Dictionary at index {i} is missing required keys: {missing_keys}")

            # --- (선택 사항) 추가적인 타입 및 값 검증 ---
            # 예: threshold 타입 검증 (숫자 또는 리스트)
            if not isinstance(item['threshold'], (int, float, list, np.number)):
                 raise TypeError(f"Node {item.get('index')}: 'threshold' must be a number or a list, got {type(item['threshold'])}.")
            # 예: child_indices 타입 검증 (정수 리스트)
            if not isinstance(item['child_indices'], list) or not all(isinstance(idx, (int, np.integer)) for idx in item['child_indices']):
                 raise TypeError(f"Node {item.get('index')}: 'child_indices' must be a list of integers, got {item['child_indices']}.")
            # 예: 리프 노드 child_indices 값 검증
            if item['is_leaf'] and item.get('child_indices') != [-1]:
                 print(f"Warning: Leaf node {item.get('index')} has child_indices {item.get('child_indices')}. Should contain only -1.")
                 # item['child_indices'] = [-1] # 자동으로 수정할 수도 있음
            # --- 선택적 검증 끝 ---

            validated_list.append(item) # 검증 통과한 아이템 추가

        # 검증된 리스트를 저장
        self.model_dict = validated_list