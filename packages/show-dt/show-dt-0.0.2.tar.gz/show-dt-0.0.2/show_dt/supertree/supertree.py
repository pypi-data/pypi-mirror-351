import json
from copy import deepcopy
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from IPython.display import HTML, display

import supertree.templatehtml as templatehtml
from supertree.node import Node
from supertree.treedata import TreeData

import importlib.metadata
import ipywidgets as widgets


class SuperTree:
    def __init__(
        self,
        model: object,
        feature_data: Optional[Union[List, np.ndarray,
                                     pd.DataFrame, pd.Series]] = None,
        target_data: Optional[Union[List, np.ndarray,
                                    pd.DataFrame, pd.Series]] = None,
        feature_names: Optional[List[str]] = None,
        target_names: Optional[Union[str, List[str]]] = None,
        license_key: str = "key",
    ):

        valid_model_classes = [
            "DecisionTreeClassifier",
            "ExtraTreeClassifier",
            "ExtraTreesClassifier",
            "RandomForestClassifier",
            "GradientBoostingClassifier",
            "DecisionTreeRegressor",
            "ExtraTreeRegressor",
            "ExtraTreesRegressor",
            "RandomForestRegressor",
            "GradientBoostingRegressor",
            "HistGradientBoostingClassifier",
            "HistGradientBoostingRegressor",
            "Booster",
            "LGBMClassifier",
            "LGBMRegressor",
            "XGBoostBooster",
            "XGBClassifier",
            "XGBRegressor",
            "XGBRFClassifier",
            "XGBRFRegressor",
            "ModelLoader",
            "ModelProto"
        ]

        if model.__class__.__name__ not in valid_model_classes:
            raise TypeError(
                f"Invalid model type. Expected one of {valid_model_classes}, but got {type(model).__name__}"
            )

        if feature_data is not None:
            if not isinstance(feature_data, (list, np.ndarray, pd.DataFrame, pd.Series)):
                raise TypeError(
                    "Invalid feature_data type. Expected a list, numpy array, or pandas DataFrame."
                )

        if target_data is not None:
            if not isinstance(target_data, (list, np.ndarray, pd.DataFrame, pd.Series)):
                raise TypeError(
                    "Invalid target_data type. Expected a list, numpy array, or pandas DataFrame."
                )

        if target_names is not None:
            if isinstance(target_names, (str, list)):
                if isinstance(target_names, list) and not all(isinstance(name, str) for name in target_names):
                    raise TypeError(
                        "Invalid target_names type. Expected a list of strings.")
            elif not isinstance(target_names, (np.ndarray)):
                raise TypeError(
                    "Invalid target_names type. Expected a string, list of strings, numpy array, or pandas DataFrame.")

        self.nodes = []
        self.node_list = []
        self.model = model
        self.model_name = model.__class__.__name__
        self.model_type = self.which_model()
        self.which_tree = None
        self.which_iteration = 0
        self.feature_names = feature_names
        self.target_names = target_names
        if not self.is_model_fitted() and self.model_name not in ("ModelProto") and self.model_name not in ("ModelLoader"):
            raise TypeError("Model is not fitted")

        if feature_names is None:
            if isinstance(feature_data, pd.DataFrame):
                self.feature_names = feature_data.columns.tolist()
            elif (
                isinstance(feature_data, (list, np.ndarray))
                and len(feature_data) > 0
                and isinstance(feature_data[0], (list, np.ndarray))
            ):
                self.feature_names = [
                    f"feature{i}" for i in range(len(feature_data[0]))
                ]
            else:
                self.feature_names = []
        else:
            self.feature_names = feature_names

        if target_names is None:
            if isinstance(target_data, pd.DataFrame):
                self.target_names = target_data.columns.tolist()
            elif isinstance(target_data, pd.Series):
                if self.model_type == "classification":
                    unique_values = target_data.unique()
                    if np.issubdtype(unique_values.dtype, np.integer):
                        self.target_names = [
                            f"target{i+1}" for i in range(len(unique_values))
                        ]
                    else:
                        self.target_names = unique_values.tolist()
                else:
                    self.target_names = "target_names"
            elif isinstance(target_data, (list, np.ndarray)):
                if self.model_type == "classification":
                    unique_values = np.unique(target_data)
                    if np.issubdtype(unique_values.dtype, np.integer):
                        self.target_names = [
                            f"target{i+1}" for i in range(len(unique_values))
                        ]
                    else:
                        self.target_names = unique_values.tolist()
                elif self.model_type == "regression":
                    self.target_names = ["target"]
                else:
                    self.target_names = "target"
            else:
                self.target_names = ["target"]
        else:
            self.target_names = target_names

        if isinstance(self.target_names, str):
            self.target_names = [self.target_names]

        self.feature_data = feature_data
        self.target_data = target_data
        if (self.feature_data is None and self.target_data is None):
            self.feature_data = [0]
            self.target_data = [0]
            self.model_type = "nodata" + self.model_type
            pass
        elif (feature_data is not None and self.target_data is not None):
            pass
        else:
            raise ValueError(
                "Target Data and Feature data should both exist or not")

        if isinstance(self.feature_data, pd.DataFrame):
            self.feature_data = self.feature_data.values
        if isinstance(self.target_data, pd.DataFrame):
            self.target_data = self.target_data.values.flatten()
        
        self.target_len = len(self.target_names)
        self.tree_data = TreeData(
            self.model_type,
            self.feature_names,
            self.target_names,
            self.feature_data,
            self.target_data,
            self.model_name
        )

        self.target_data = self.tree_data.data_target
    

        if self.which_model == "classification" and len(self.target_names) != np.unique(self.target_data):
            raise TypeError(
                "Invalid target_names length"
            )
        if self.which_model == "regression" and len(self.target_names) != 1:
            raise TypeError(
                "Invalid target_names length"
            )

        self.license_key = license_key

    def show_tree(self, which_tree=0, which_iteration=0, start_depth=5, max_samples=7500, show_sample=None, widgets=False):
        """
        Displaying model HTMl template and create json tree model.
        """
        if not isinstance(which_tree, int) or which_tree < 0:
            raise TypeError("Invalid which_tree type. Expected an integer.")

        if not isinstance(which_iteration, int) or which_iteration < 0:
            raise TypeError(
                "Invalid which_iteration type. Expected an integer.")

        if not isinstance(start_depth, int) or start_depth < 0:
            raise TypeError("Invalid start_depth type. Expected an integer.")

        start_depth = start_depth + 1

        if not isinstance(max_samples, int) or max_samples < 1:
            raise ValueError("Invalid max_samples value. Expected an integer greater than or equal to 1.")

        if show_sample is not None:
            self.tree_data.set_show_sample(show_sample)
        else:
            self.tree_data.reset_sample()

        self.tree_data.max_samples = max_samples
        self.which_tree = which_tree
        self.which_iteration = which_iteration
        self.tree_data.set_which_tree(self.which_tree)

        if self.model_type == "uknown_model":
            return 0

        if(widgets==True):
            self.ipy_widget(start_depth)
        else:
            combined_data_str = self._get_combined_data()

            display(HTML(templatehtml.get_d3_html(
                combined_data_str, start_depth, self.license_key)))

            self.node_list = []
            self.nodes = []

    def save_html(self, filename="output", which_tree=0, which_iteration=0, start_depth=5, max_samples=7500, show_sample=None):
        """
        Saving HTML file and create json tree model.
        """

        if not filename.endswith(".html"):
            filename += ".html"

        if not isinstance(which_tree, int) or which_tree < 0:
            raise TypeError("Invalid which_tree type. Expected an integer.")

        if not isinstance(start_depth, int) or start_depth < 0:
            raise TypeError("Invalid start_depth type. Expected an integer.")

        start_depth = start_depth + 1

        if not isinstance(which_iteration, int) or which_iteration < 0:
            raise TypeError(
                "Invalid which_iteration type. Expected an integer.")

        if filename is not None and not isinstance(filename, str):
            raise TypeError("Invalid filename type. Expected a string.")

        if not isinstance(max_samples, int) or max_samples < 1:
            raise ValueError("Invalid max_samples value. Expected an integer greater than or equal to 1.")


        if show_sample is not None:
            self.tree_data.set_show_sample(show_sample)
        else:
            self.tree_data.reset_sample()

        self.tree_data.max_samples = max_samples

        self.which_tree = which_tree
        self.which_iteration = which_iteration
        self.tree_data.set_which_tree(self.which_tree)

        d3script = """
    <script src="https://cdn.jsdelivr.net/npm/d3@7" charset="utf-8"></script>
    <script src="https://cdn.jsdelivr.net/npm/tweetnacl@1.0.3/nacl.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/tweetnacl-util@0.15.1/nacl-util.min.js"></script>
"""

        combined_data_str = self._get_combined_data()

        html = d3script + \
            templatehtml.get_d3_html(
                combined_data_str, start_depth, self.license_key)

        with open(filename, "w", encoding="utf-8") as file:
            file.write(html)

        print(f"HTML saved to {filename}")

        self.node_list = []
        self.nodes = []

    def save_json_tree(self, filename="treedata", which_tree=0, which_iteration=0, max_samples=7500, show_sample=None):
        """
        Save tree to json tree.
        """
        if not filename.endswith(".json"):
            filename += ".json"

        if not isinstance(which_tree, int) or which_tree < 0:
            raise TypeError("Invalid which_tree type. Expected an integer.")

        if filename is not None and not isinstance(filename, str):
            raise TypeError("Invalid filename type. Expected a string.")

        if not isinstance(which_iteration, int) or which_iteration < 0:
            raise TypeError(
                "Invalid which_iteration type. Expected an integer.")

        if not isinstance(max_samples, int) or max_samples < 1:
            raise ValueError("Invalid max_samples value. Expected an integer greater than or equal to 1.")

        if show_sample is not None:
            self.tree_data.set_show_sample(show_sample)
        else:
            self.tree_data.reset_sample()

        self.tree_data.max_samples = max_samples

        self.which_tree = which_tree
        self.which_iteration = which_iteration

        combined_data_str = self._get_combined_data()

        with open((filename), "w", encoding="utf-8") as file:
            file.write(combined_data_str)

        print(f"JSON data saved to {filename}")

        self.node_list = []
        self.nodes = []

    def _get_combined_data(self):
        """
        Combine node and tree data as one json file.
        """
        self.convert_model_to_dict_array()
        json_node_data_str = self._get_json_nodes()
        json_tree_data_str = self._get_json_tree_data()

        json_node_data = json.loads(json_node_data_str)
        json_tree_data = json.loads(json_tree_data_str)

        combined_data = {
            "node_data": json_node_data,
            "tree_data": json_tree_data,
        }
        combined_data_str = json.dumps(combined_data)

        return combined_data_str

    def _get_json_tree_data(self):
        """
        Save Tree Data to Json
        """
        tree_data_dict = self.tree_data.to_dict()
        tree_data_json = json.dumps(tree_data_dict, indent=4)
        return tree_data_json

    def _get_json_nodes(self):
        """
        Node 리스트로부터 Node 객체 리스트를 생성하고, DFS로 트리 구조를 만든 후,
        루트 노드를 딕셔너리로 변환하여 JSON 문자열을 반환합니다. (N-ary Node 사용)
        """
        self.nodes = []
        if not self.node_list:
            return "{}"

        # 1. self.node_list -> self.nodes (Node 객체 리스트) 변환
        for node_info in list(self.node_list):
            num_defined_classes = len(self.target_names) if self.target_names else 0
            raw_class_dist = node_info.get("class_distribution")
            processed_class_dist = [[]]
            feature_value_from_info = node_info.get("feature")
            processed_feature = feature_value_from_info
            if isinstance(raw_class_dist, list) and len(raw_class_dist) > 0 and num_defined_classes > 0:
                first_element = raw_class_dist[0]
                if isinstance(first_element, list):  # 일반적인 경우: [[c0, c1, c2]]
                    inner_dist = list(first_element)  # 복사
                    if len(inner_dist) < num_defined_classes:
                        inner_dist.extend([0] * (num_defined_classes - len(inner_dist)))
                    processed_class_dist = [inner_dist[:num_defined_classes]]
                elif all(isinstance(x, (int, float)) for x in raw_class_dist):  # 예외적인 경우: [count] 또는 [c0, c1]
                    # 이 경우, 어떤 클래스의 count인지 명확하지 않으므로,
                    # predicted_class를 기반으로 채우거나, 순서대로 채우고 나머지는 0으로.
                    # 가장 안전한 방법은 입력 node_dict 자체를 완전한 형태로 만드는 것이지만,
                    # 여기서 최대한 보정한다면:
                    temp_dist = [0] * num_defined_classes
                    # 예를 들어, predicted_class가 "2.0"이고 raw_class_dist가 [29] 라면, class 2에 29를 할당
                    # 또는 raw_class_dist가 [1, 29]이고 predicted_class가 "2.0" (index 2)이면,
                    # 어떤 값이 클래스 0, 1, 2에 해당하는지 규칙이 필요함.
                    # 여기서는 일단 길이만 맞추는 것으로 단순화 (실제로는 MAPSDT 출력 수정이 더 좋음)
                    for i in range(len(raw_class_dist)):
                        if i < num_defined_classes:
                            temp_dist[i] = raw_class_dist[i]
                    processed_class_dist = [temp_dist]

            node = Node(
                feature=processed_feature,
                threshold=node_info.get("threshold"),
                impurity=round(node_info.get("impurity", 0.0), 3),
                samples=node_info.get("samples"),
                class_distribution=processed_class_dist,  # 정규화된 class_distribution 사용
                predicted_class=node_info.get("predicted_class"),  # 문자열 "0.0", "1.0", "2.0" 유지
                is_leaf=node_info.get("is_leaf", False),
                child_indices=node_info.get("child_indices"),
                is_categorical=node_info.get("is_categorical", False),
                _children_map=node_info.get("_children_map"),
                treeclass=node_info.get("treeclass")  # 문자열 "0.0", "1.0", "2.0" 유지
            )
            self.nodes.append(node)

        if not self.nodes:
            return "{}"

        self._create_node_dfs(0, "ROOT", None, None, None)
        root = self.nodes[0]
        if root.class_distribution is None and (self.model_type == "classification" or
                                                (self.model_name == "GradientBoostingClassifier" and self.model_type.startswith("nodata"))):
            self.count_class_distribution(root)
        if self.model_name == "ModelProto" and "nodata" not in self.model_type:
            self.count_samples(root)

        tree_dict = root.to_dict()
        try:
            tree_json = json.dumps(tree_dict, indent=4)
        except TypeError as e:
            print(f"JSON 직렬화 오류: {e}. 순환 참조 또는 처리 불가 타입 확인 필요.")
            tree_json = "{}"  # 오류 시 빈 JSON
        return tree_json

    def _create_node_dfs(self, node_index, parent_branch_info, parent_threshold, parent_feature_idx, x_axis):
        """
        Using DFS algorithm to create tree structure (N-ary children from child_indices).
        """
        if not isinstance(node_index, (int, np.integer)) or node_index < 0 or node_index >= len(self.nodes):
            # print(f"Warning: Invalid node_index ({node_index}). _create_node_dfs skipping.")
            return

        node = self.nodes[node_index]

        # --- start_end_x_axis 설정 로직 (단순화/수정) ---
        if parent_branch_info == "ROOT":
            # 루트 노드 초기화
            node.start_end_x_axis = []
            feature_names_size = len(self.feature_names) if self.feature_names else 0
            for _ in range(feature_names_size):
                node.start_end_x_axis.append(["notexist", "notexist"])
        elif isinstance(x_axis, list):
             # 부모로부터 복사
             node.start_end_x_axis = deepcopy(x_axis)
             # 부모가 숫자형 이진 분기였을 경우에만 업데이트 시도
             if isinstance(parent_feature_idx, (int, np.integer)) and parent_feature_idx >= 0 and \
                isinstance(parent_threshold, (float, int, np.number)) and \
                parent_feature_idx < len(node.start_end_x_axis):
                     if parent_branch_info == "R": # 오른쪽 자식 (feature > threshold)
                         if node.start_end_x_axis[parent_feature_idx][0] == "notexist" or parent_threshold > node.start_end_x_axis[parent_feature_idx][0]:
                              node.start_end_x_axis[parent_feature_idx][0] = parent_threshold
                     elif parent_branch_info == "L": # 왼쪽 자식 (feature <= threshold)
                         if node.start_end_x_axis[parent_feature_idx][1] == "notexist" or parent_threshold < node.start_end_x_axis[parent_feature_idx][1]:
                              node.start_end_x_axis[parent_feature_idx][1] = parent_threshold
             # 다중 분기 숫자형/범주형에 대한 start_end_x_axis 업데이트 로직은 복잡하여 여기서는 생략
             # -> 즉, 다중 분기 시에는 부모의 axis 정보가 그대로 전달됨
        else:
            # x_axis가 리스트가 아닌 예외적 상황 처리
            node.start_end_x_axis = [] # Fallback
            feature_names_size = len(self.feature_names) if self.feature_names else 0
            for _ in range(feature_names_size):
                node.start_end_x_axis.append(["notexist", "notexist"])
        # --- start_end_x_axis 설정 로직 끝 ---

        # --- 수정된 재귀 로직 ---
        if not node.is_leaf:
            node.children_nodes = [] # 자식 Node 객체 리스트 초기화
            child_indices = getattr(node, 'child_indices', [])

            if child_indices and child_indices != [-1]:
                # 각 자식 인덱스에 대해 재귀 호출
                num_children = len(child_indices)
                thresholds = node.threshold

                for i, child_idx in enumerate(child_indices):
                    if isinstance(child_idx, (int, np.integer)) and 0 <= child_idx < len(self.nodes):
                        branch_info = f"CHILD_{i}" # 기본 브랜치 정보
                        child_parent_threshold = node.threshold # 기본적으로 부모 임계값 전달
                        child_parent_feature = node.feature # 기본적으로 부모 특성 전달

                        # 분기 유형에 따라 정보 조정 (개선 필요)
                        if isinstance(thresholds, list) and len(thresholds) == num_children - 1:
                             # 다중 분기 숫자형 (threshold: [t1, t2...])
                             if i == 0: branch_info = f"LE_{thresholds[0]}"
                             elif i == num_children - 1: branch_info = f"GT_{thresholds[-1]}"
                             else: branch_info = f"BT_{thresholds[i-1]}_{thresholds[i]}"
                             child_parent_threshold = None # 다중분기는 단일 임계값 의미 없음
                        elif isinstance(thresholds, (float, int, np.number)) and num_children == 2:
                             # 이진 분기 숫자형
                             branch_info = "L" if i == 0 else "R"
                        elif getattr(node, 'is_categorical', False):
                            # 범주형 (category 값 필요 - _children_map 등 활용)
                            # category_value = find_category_for_child(node, child_idx) # 이런 함수 필요
                            # branch_info = f"CAT_{category_value}"
                            child_parent_threshold = None
                            pass


                        self._create_node_dfs(
                            child_idx,
                            branch_info, # 분기 정보 전달 시도
                            child_parent_threshold, # 부모 임계값
                            child_parent_feature, # 부모 분기 특성
                            node.start_end_x_axis # 현재 노드의 axis 정보 전달
                        )
                        # 자식 Node 객체를 children_nodes에 추가 및 부모 설정
                        if child_idx < len(self.nodes): # 인덱스 유효성 재확인
                             child_node_obj = self.nodes[child_idx]
                             node.children_nodes.append(child_node_obj)
                             child_node_obj.parent = node

        # --- 수정된 재귀 로직 끝 ---


    def which_model(self):
        """
        Recognize which model is used.
        """
        if self.model_name in (
            "DecisionTreeClassifier",
            "ExtraTreeClassifier",
            "ExtraTreesClassifier",
            "RandomForestClassifier",
            "GradientBoostingClassifier",
            "LGBMClassifier",
            "XGBClassifier",
            "XGBRFClassifier",
            "HistGradientBoostingClassifier",
        ):
            return "classification"
        elif self.model_name in (
            "DecisionTreeRegressor",
            "ExtraTreeRegressor",
            "ExtraTreesRegressor",
            "RandomForestRegressor",
            "GradientBoostingRegressor",
            "LGBMRegressor",
            "XGBRegressor",
            "XGBRFRegressor",
            "HistGradientBoostingRegressor",
        ):
            return "regression"

        elif self.model_name in ("ModelLoader"):
            if self.model.model_type == "classification":
                return "classification"
            elif self.model.model_type == "regression":
                return "regression"
            else:
                print("Uknown Model")
                return "uknown_model"

        elif self.model_name in ("Booster"):
            if hasattr(self.model, "get_dump"):
                self.model_name = "XGBoostBooster"
                config_str = self.model.save_config()
                config = json.loads(config_str)
                objective = (
                    config.get("learner", {}).get(
                        "objective", {}).get("name", "")
                )
                if "binary:logistic" in objective or "multi:" in objective:
                    return "classification"
                elif "reg:" in objective:
                    return "regression"
                else:
                    print("Uknown model type")
            elif hasattr(self.model, "dump_model"):
                self.model_name = "LightGBMBooster"
                model_dict = self.model.dump_model()
                if model_dict["objective"] == "regression":
                    return "regression"
                else:
                    return "classification"
        elif self.model_name in ("ModelProto"):
            graph_name = self.model.graph.node[0].op_type
            if "Classifier" in graph_name:
                return "classification"
            else:
                return "regression"
        else:
            print("Uknown Model")
            return "uknown_model"

    def count_class_distribution(self, node):
        """
        Count class distribution if model data about samples is not in model.
        """
        target_len = self.target_len
        node.class_distribution = [0] * target_len
        index_set = set()

        
        for j in range(len(self.feature_data)):
            for i in range(len(node.start_end_x_axis)):
                if node.start_end_x_axis[i][0] != "notexist":
                    if node.start_end_x_axis[i][0] <= self.feature_data[j][i]:
                        index_set.add(j)

                if node.start_end_x_axis[i][1] != "notexist":
                    if node.start_end_x_axis[i][1] > self.feature_data[j][i]:
                        index_set.add(j)
                        


        samples = 0
        for i in range(len(self.target_data)):
            if i not in index_set:
                node.class_distribution[self.target_data[i]] += 1
                samples += 1
        if node.samples is None:
            node.samples = samples
        node.class_distribution = [node.class_distribution]

        if node.left_node is not None:
            self.count_class_distribution(node.left_node)

        if node.right_node is not None:
            self.count_class_distribution(node.right_node)

    def is_model_fitted(self):

        """
        Check is model fitted.
        """
        try:
            if self.model_name in [
                "DecisionTreeClassifier",
                "ExtraTreeClassifier",
                "ExtraTreesClassifier",
                "RandomForestClassifier",
                "GradientBoostingClassifier",
                "DecisionTreeRegressor",
                "ExtraTreeRegressor",
                "ExtraTreesRegressor",
                "RandomForestRegressor",
                "GradientBoostingRegressor",
                "HistGradientBoostingClassifier",
                "HistGradientBoostingRegressor"
            ]:
                return hasattr(self.model, "tree_") or hasattr(self.model, "estimators_") or hasattr(self.model,"_predictors")

            elif self.model_name in ["LGBMClassifier", "LGBMRegressor"]:
                if hasattr(self.model, 'booster_'):
                    return True
                else:
                    return False

            elif self.model_name in ["XGBClassifier", "XGBRegressor", "XGBRFClassifier", "XGBRFRegressor"]:
                try:
                    self.model.get_booster()
                    return True
                except NotFittedError:
                    return False


            elif self.model_name == "XGBoostBooster":
                return True

            elif self.model_name == "LightGBMBooster":
                if hasattr(self.model, 'num_trees') and self.model.num_trees() > 0:
                    return True
                else:
                    return False

            return False

        except Exception:
            return False

    def count_samples(self, node):
        """
        Count samples if model doesnt have info about samples.
        """
        index_set = set()
        for i in range(len(node.start_end_x_axis)):
            for j in range(len(self.feature_data)):
                if node.start_end_x_axis[i][0] != "notexist":
                    if node.start_end_x_axis[i][0] < self.feature_data[j][i]:
                        index_set.add(j)

                if node.start_end_x_axis[i][1] != "notexist":
                    if node.start_end_x_axis[i][1] > self.feature_data[j][i]:
                        index_set.add(j)

        samples = 0
        for i in range(len(self.target_data)):
            if i not in index_set:
                samples += 1
        if node.samples == -1:
            node.samples = samples
        if node.left_node is not None:
            self.count_samples(node.left_node)

        if node.right_node is not None:
            self.count_samples(node.right_node)

    def convert_model_to_dict_array(self):
        """
        Converting model to my structure
        """
        model_name = self.model_name
        if model_name in (
            "DecisionTreeClassifier",
            "ExtraTreeClassifier",
            "ExtraTreesClassifier",
            "DecisionTreeRegressor",
            "ExtraTreeRegressor",
            "ExtraTreesRegressor",
            "RandomForestClassifier",
            "RandomForestRegressor",
            "GradientBoostingRegressor",
            "GradientBoostingClassifier",
        ):
            if model_name in (
                "RandomForestClassifier",
                "RandomForestRegressor",
                "ExtraTreesClassifier",
                "ExtraTreesRegressor",
            ):
                if 0 <= self.which_tree < len(self.model.estimators_):
                    super_tree = self.model.estimators_[self.which_tree].tree_
                else:
                    raise IndexError("Out of trees range")
            elif model_name in (
                "GradientBoostingRegressor",
                "GradientBoostingClassifier",
            ):
                if (0 <= self.which_iteration < len(self.model.estimators_)
                        and 0 <= self.which_tree < len(self.model.estimators_[self.which_tree])):
                    super_tree = self.model.estimators_[
                        self.which_iteration, self.which_tree].tree_
                else:
                    raise IndexError(
                        "Value of 'which_tree' or 'which_iteration' is out of range.")
            else:
                super_tree = self.model.tree_

            sklearn_version = importlib.metadata.version('scikit-learn')

            for i in range(super_tree.node_count):
                samples = super_tree.n_node_samples[i]
                class_distribution = ["No data"]
                class_distribution_from_model = None
                if (self.model_name not in ("GradientBoostingClassifier")):
                    if (sklearn_version > "1.4.0" and self.model_type in "classification"):
                        class_distribution_from_model = super_tree.value[i] * samples
                        class_distribution_from_model = np.round(class_distribution_from_model)
                    elif (self.model_type == "nodataclassification"):
                        class_distribution_from_model = np.round(super_tree.value[i] * samples)
                    else:
                        class_distribution_from_model = super_tree.value[i]


                    if(class_distribution_from_model is not None):
                        class_distribution = class_distribution_from_model

                    if(self.model_type == "classification"):
                        class_distribution = None


                    predicted_class_index = class_distribution_from_model.argmax()
                else:
                    class_distribution = None
                    predicted_class_index = "nodata"
                is_leaf = False
                if not self.model_type.startswith("nodata") and self.model_name not in ("GradientBoostingClassifier"):
                    predicted_class = self.target_names[predicted_class_index]
                else:
                    if (self.model_name == "GradientBoostingClassifier"):
                        predicted_class = "No data"
                    else:
                        predicted_class = predicted_class_index
                left_children = super_tree.children_left[i]
                right_children = super_tree.children_right[i]
                if right_children == -1 and left_children == -1:
                    is_leaf = True

                node_info = {
                    "index": i,
                    "feature": super_tree.feature[i],
                    "impurity": super_tree.impurity[i],
                    "threshold": super_tree.threshold[i],
                    "class_distribution": class_distribution,
                    "predicted_class": predicted_class,
                    "samples": samples,
                    "is_leaf": is_leaf,
                    "left_child_index": left_children,
                    "right_child_index": right_children,
                }
                self.node_list.append(node_info)
        if model_name == "LightGBMBooster" or model_name in ("LGBMRegressor", "LGBMClassifier"):
            if model_name != "LightGBMBooster":
                booster = self.model.booster_
                model_dict = booster.dump_model()
            else:
                model_dict = self.model.dump_model()

            if 0 <= self.which_tree < len(model_dict["tree_info"]):
                tree = model_dict["tree_info"][self.which_tree]
            else:
                raise IndexError("Tree index out of range")
            tree = model_dict["tree_info"][self.which_tree]
            self.collect_node_info_lgbm(tree["tree_structure"])
        if model_name in ("XGBoostBooster", "XGBClassifier", "XGBRegressor", "XGBRFClassifier", "XGBRFRegressor"):
            if model_name != "XGBoostBooster":
                booster = self.model.get_booster()
                model_dict = booster.get_dump(
                    with_stats=True, dump_format="json")
            else:
                model_dict = self.model.get_dump(
                    with_stats=True, dump_format="json")

            if 0 <= self.which_tree < len(model_dict):
                json_tree = model_dict[self.which_tree]
            else:
                raise IndexError(f"Value 'which_tree' ({self.which_tree}) it is not correct key in 'model_dict'.")
            dict_tree = json.loads(json_tree)
            self.collect_node_info_xgboost(dict_tree)
        if model_name in ("ModelLoader"):
            self.node_list = self.model.model_dict

        if model_name in ("HistGradientBoostingClassifier", "HistGradientBoostingRegressor"):

            if not (0 <= self.which_iteration < len(self.model._predictors)):
                raise IndexError(f"which_iteration {self.which_iteration} is out of range. Valid range is 0 to {len(self.model._predictors) - 1}.")

            if not (0 <= self.which_tree < len(self.model._predictors[self.which_iteration])):
                raise IndexError(f"which_tree {self.which_tree} is out of range for iteration {self.which_iteration}. Valid range is 0 to {len(self.model._predictors[self.which_iteration]) - 1}.")
            nodes = self.model._predictors[self.which_iteration][self.which_tree].nodes
            self.collect_node_info_histgb(nodes)
        if model_name in ("ModelProto"):
            self.collect_node_info_onnx(self.model)

    def collect_node_info_lgbm(self, node, depth=0):
        """
        Converting lgbm model to my structure
        """
        node_index = len(self.node_list)
        if "split_index" in node:
            predicted_data = None
            if self.model_type.startswith("nodata"):
                predicted_data = "No data"
                class_dist = "no data"
            else:
                predicted_data = self.target_names[0]

            class_dist = [["No data"]]
            if self.model_type == "classification":
                class_dist = None
            node_info = {
                "index": node_index,
                "feature": node["split_feature"],
                "impurity": node["split_gain"],
                "threshold": node["threshold"],
                "class_distribution": class_dist,
                "predicted_class": predicted_data,
                "samples": node["internal_count"],
                "is_leaf": False,
                "left_child_index": None,
                "right_child_index": None,
            }
            self.node_list.append(node_info)
            left_child_index = self.collect_node_info_lgbm(
                node["left_child"], depth + 1
            )
            right_child_index = self.collect_node_info_lgbm(
                node["right_child"], depth + 1
            )
            self.node_list[node_index]["left_child_index"] = left_child_index
            self.node_list[node_index]["right_child_index"] = right_child_index
        else:
            predicted_data = None
            if self.model_type.startswith("nodata"):
                predicted_data = "No data"
            else:
                predicted_data = self.target_names[0]
            class_dist = [[node["leaf_value"]]]
            if self.model_type == "classification":
                class_dist = None
            node_info = {
                "index": node_index,
                "feature": -1,
                "impurity": 0,
                "threshold": -1,
                "class_distribution": class_dist,
                "predicted_class": predicted_data,
                "samples": node["leaf_count"],
                "is_leaf": True,
                "left_child_index": -1,
                "right_child_index": -1,
            }

            self.node_list.append(node_info)

        return node_index

    def collect_node_info_xgboost(self, node, depth=0):
        """
        Converting xgb models to my structure
        """
        node_index = len(self.node_list)

        if "split" in node:
            feature_index = 0
            feature = node["split"]
            if feature.startswith("f") and len(feature) <= 3:
                feature_index = int(feature[1:])
            else:
                try:
                    feature_index = self.feature_names.index(feature)
                except ValueError:
                    raise ValueError(
                        f"Feature {feature} not found in feature_names.")
            class_dist = ["No data"]
            predicted_data = None
            if self.model_type.startswith("nodata"):
                predicted_data = "No data"
            else:
                predicted_data = self.target_names[0]

            if self.model_type == "classification":
                class_dist = None
            node_info = {
                "index": node_index,
                "feature": int(feature_index),
                "impurity": node.get("gain", 0),
                "threshold": node["split_condition"],
                "class_distribution": class_dist,
                "predicted_class": predicted_data,
                "samples": node.get("cover", 0),
                "is_leaf": False,
                "left_child_index": None,
                "right_child_index": None,
            }
            self.node_list.append(node_info)
            left_child_index = self.collect_node_info_xgboost(
                node["children"][0], depth + 1
            )
            right_child_index = self.collect_node_info_xgboost(
                node["children"][1], depth + 1
            )
            self.node_list[node_index]["left_child_index"] = left_child_index
            self.node_list[node_index]["right_child_index"] = right_child_index
        else:
            class_dist = ["No data"]
            if self.model_type == "classification":
                class_dist = None
            else:
                class_dist = [[node["leaf"]]]

            predicted_data = None
            if self.model_type.startswith("nodata"):
                predicted_data = "No data"
            else:
                predicted_data = self.target_names[0]
            node_info = {
                "index": node_index,
                "feature": -1,
                "impurity": 0,
                "threshold": -1,
                "class_distribution": class_dist,
                "predicted_class": predicted_data,
                "samples": node.get("cover", 0),
                "is_leaf": True,
                "left_child_index": -1,
                "right_child_index": -1,
            }
            self.node_list.append(node_info)

        return node_index

    def collect_node_info_histgb(self, nodes):
        """
        Converting histgb model to my structure
        """
        for i, node in enumerate(nodes):
            feature_index = int(node[2])
            threshold = node[3]
            left_child = int(node[5])
            right_child = int(node[6])
            samples = int(node[1])
            impurity = node[8]
            if (not self.model_type.startswith("nodata")):
                if (self.model_name == "HistGradientBoostingRegressor"):
                    class_dist = [[node[0]]]
                    predicted_class = self.target_names[0]
                else:
                    class_dist = None
                    predicted_class_index = node[9]
                    predicted_class = self.target_names[predicted_class_index]
            if (self.model_type.startswith("nodata")):
                class_dist = ["No Data"]
                predicted_class = node[9]
            if (self.model_type == "nodataregression"):
                class_dist = [[node[0]]]

            if left_child == 0:
                left_child = -1
            if right_child == 0:
                right_child = -1

            if left_child == -1 and right_child == -1:
                is_leaf = True
            else:
                is_leaf = False

            node_info = {
                "index": i,
                "feature": feature_index,
                "impurity": impurity,
                "threshold": threshold,
                "class_distribution": class_dist,
                "predicted_class": predicted_class,
                "samples": samples,
                "is_leaf": is_leaf,
                "left_child_index": left_child,
                "right_child_index": right_child,
            }
            self.node_list.append(node_info)

    def collect_node_info_onnx(self, onnx_model):
        """
        Converting onnx to my structure
        """
        for node in onnx_model.graph.node:

                attributes = {attr.name: attr for attr in node.attribute}

                if 'nodes_treeids' in attributes and 'nodes_nodeids' in attributes:
                    tree_ids = list(attributes['nodes_treeids'].ints)
                    node_ids = list(attributes['nodes_nodeids'].ints)
                    feature_ids = list(attributes.get('nodes_featureids', []).ints)
                    thresholds = list(attributes.get('nodes_values', []).floats)
                    left_children = list(attributes.get('nodes_truenodeids', []).ints)
                    right_children = list(attributes.get('nodes_falsenodeids', []).ints)
                    node_modes = list(attributes.get("nodes_modes", []).strings)

                    if "regression" in self.model_type:
                        class_ids = []
                    else:
                        class_ids = list(attributes.get("class_ids", []).ints)
                    if "regression" in self.model_type:
                        target_weights = list(attributes.get("target_weights", []).floats)
                    else:
                        target_weights = []

                    trees = {}
                    leaf_index = 0

                    for i, tree_id in enumerate(tree_ids):
                        if tree_id not in trees:
                            trees[tree_id] = []

                        is_leaf = node_modes[i] == b'LEAF'
                        if is_leaf:
                            current_target_weight = target_weights[leaf_index] if leaf_index < len(target_weights) else None
                            current_class = class_ids[leaf_index] if leaf_index < len(class_ids) else None
                            leaf_index += 1
                        else:
                            current_target_weight = None
                            current_class = None

                        trees[tree_id].append({
                            'node_id': node_ids[i],
                            'class_id': class_ids[i] if i < len(class_ids) else None,
                            'feature_id': feature_ids[i] if i < len(feature_ids) else None,
                            'threshold': thresholds[i] if i < len(thresholds) else None,
                            'left_child': left_children[i] if left_children[i] != 0 else -1,
                            'right_child': right_children[i] if right_children[i] != 0 else -1,
                            'node_modes': current_class,
                            'target_weights': current_target_weight,
                        })

                    if self.which_tree in trees:
                        for node in trees[self.which_tree]:
                            if self.model_type == "nodataclassification":
                                predicted_class = node["class_id"]
                                class_dist = [["No data"]]
                            elif self.model_type == "classification":
                                predicted_class = self.target_names[node["class_id"]]
                                class_dist = None
                            elif "regression" in self.model_type:
                                if node['left_child'] == -1 and node['right_child'] == -1:
                                    class_dist = [[node["target_weights"]]]
                                    predicted_class = "No data"
                                else:
                                    class_dist = [[0]]
                                    predicted_class = "No data"
                            else:
                                class_dist = [[0]]
                                predicted_class = "No data"

                            node_info = {
                                "index": node['node_id'],
                                "feature": node['feature_id'],
                                "impurity": 1,
                                "threshold": node['threshold'],
                                "class_distribution": class_dist,
                                "predicted_class": predicted_class if node['left_child'] == -1 and node['right_child'] == -1 else "NoData",
                                "samples": -1,
                                "is_leaf": True if node['left_child'] == -1 and node['right_child'] == -1 else False,
                                "left_child_index": node['left_child'],
                                "right_child_index": node['right_child'],
                            }

                            self.node_list.append(node_info)
                    else:
                        raise IndexError(f"Key '{self.which_tree}' not found in trees")



    def ipy_widget(self, start_depth):
        """
        Navigate to the next tree using ipy widgets
        """

        output = widgets.Output()

        number_input = widgets.BoundedIntText(
            value=0,
            min=0,
            max=self.get_max_tree_size()-1,
            step=1,
            description='',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='60px')
        )

        def next_button_click(b):
            with output:
                output.clear_output()
                if(self.which_tree + 1 > (self.get_max_tree_size())-1):
                    self.which_tree=0
                else:
                    self.which_tree = self.which_tree+1
                
                
                self.tree_data.set_which_tree(self.which_tree)
                combined_data_str = self._get_combined_data()
                display(HTML(templatehtml.get_d3_html(
                combined_data_str, start_depth, self.license_key)))
                self.node_list = []
                self.nodes = []


        def previous_button_click(b):
            with output:
                output.clear_output()

                if(self.which_tree - 1 < 0):
                    self.which_tree=self.get_max_tree_size()-1
                else:
                    self.which_tree = self.which_tree-1

                self.tree_data.set_which_tree(self.which_tree)
                combined_data_str = self._get_combined_data()
                display(HTML(templatehtml.get_d3_html(
                combined_data_str, start_depth, self.license_key)))
                self.node_list = []
                self.nodes = []

        def number_input_change(change):
            with output:
                output.clear_output()
                self.which_tree = change['new']
                self.tree_data.set_which_tree(self.which_tree)
                combined_data_str = self._get_combined_data()
                display(HTML(templatehtml.get_d3_html(
                    combined_data_str, start_depth, self.license_key)))
                self.node_list = []
                self.nodes = []

        next_button = widgets.Button(description="→", layout=widgets.Layout(width='60px'),
                                 button_style='info')

        next_button.on_click(next_button_click)


        number_input.observe(number_input_change, names='value')


        previous_button = widgets.Button(description="←", layout=widgets.Layout(width='60px'),
                                     button_style='info')

        previous_button.on_click(previous_button_click)

        widgets_box = widgets.HBox([previous_button,number_input, next_button], layout=widgets.Layout(align_items='center'))

        display(widgets.VBox([widgets_box, output], layout=widgets.Layout(align_items='center')))

        with output:
            combined_data_str = self._get_combined_data()
            display(HTML(templatehtml.get_d3_html(
                    combined_data_str, start_depth, self.license_key)))


        self.node_list = []
        self.nodes = []


    def get_max_tree_size(self):
        model_name = self.model_name
        if model_name in (
            "DecisionTreeClassifier",
            "ExtraTreeClassifier",
            "ExtraTreesClassifier",
            "DecisionTreeRegressor",
            "ExtraTreeRegressor",
            "ExtraTreesRegressor",
            "RandomForestClassifier",
            "RandomForestRegressor",
            "GradientBoostingRegressor",
            "GradientBoostingClassifier",
        ):
            if model_name in (
                "RandomForestClassifier",
                "RandomForestRegressor",
                "ExtraTreesClassifier",
                "ExtraTreesRegressor",
            ):
                return len(self.model.estimators_)
            elif model_name in (
                "GradientBoostingRegressor",
                "GradientBoostingClassifier",
            ):
                return len(self.model.estimators_[0])

        if model_name == "LightGBMBooster" or model_name in ("LGBMRegressor", "LGBMClassifier"):
            if model_name != "LightGBMBooster":
                booster = self.model.booster_
                model_dict = booster.dump_model()
            else:
                model_dict = self.model.dump_model()

            return len(model_dict["tree_info"])
        
        if model_name in ("XGBoostBooster", "XGBClassifier", "XGBRegressor", "XGBRFClassifier", "XGBRFRegressor"):
            if model_name != "XGBoostBooster":
                booster = self.model.get_booster()
                model_dict = booster.get_dump(
                    with_stats=True, dump_format="json")
            else:
                model_dict = self.model.get_dump(
                    with_stats=True, dump_format="json")

            return len(model_dict)

        if model_name in ("HistGradientBoostingClassifier", "HistGradientBoostingRegressor"):
           return len(self.model._predictors[0])

        return 1
