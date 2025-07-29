import pandas as pd
from supertree import SuperTree
from supertree.model_loader import ModelLoader

df = pd.read_csv('dataset/iris.csv')
target_names = ['Setosa', 'Versicolor', 'Virginica']
feature_names = [col for col in df.columns if col != 'Decision']

X_data = df[feature_names]
y_data_raw = df['Decision']

# child 노드의 인덱스 (leaf 노드일 경우 [-1])
# target 클래스의 샘플 수 (list의 길이는 class 개수랑 반드시 일치해야함)
# 분기의 기준이 되는 feature index (leaf 노드일 경우 -2)
# 시각화에 중요한 key는 아닌 것으로 추측됨
# 노드 index (root는 항상 0)
# 시각화에 중요한 key는 아닌 것으로 추측됨
# leaf 노드는 pi형태로 시각화되고, 분기가 되는 노드는 데이터 분포 표시
# leaf 노드일 때, 예측되는 class 표시
# 현재 노드의 샘플 수
# categorical feature 일 때는 index가 multiple 분기 수만큼이고 continuous는 multiple 분기 수 - 1 (leaf 노드일 경우 -2)
# predicted_class 랑 같은 의미로 추측됨
node_dict = [{'child_indices': [1, 2, 7],
               'class_distribution': [[40, 40, 40]],
               'feature': 2,
               'impurity': 1.585,
               'index': 0,
               'is_categorical': False,
               'is_leaf': False,
               'predicted_class': None,
               'samples': 120,
               'threshold': [2.833333333333332, 4.6],
               'treeclass': None},
              {'child_indices': [-1],
               'class_distribution': [[40, 0, 0]],
               'feature': -2,
               'impurity': 0.0,
               'index': 1,
               'is_categorical': False,
               'is_leaf': True,
               'predicted_class': '0',
               'samples': 40,
               'threshold': -2.0,
               'treeclass': '0'},
              {'child_indices': [3, 4],
               'class_distribution': [[0, 10, 1]],
               'feature': 3,
               'impurity': 0.439,
               'index': 2,
               'is_categorical': False,
               'is_leaf': False,
               'predicted_class': None,
               'samples': 11,
               'threshold': [0.7999999999999996, 1.5333333333333332],
               'treeclass': None},
              {'child_indices': [-1],
               'class_distribution': [[0, 0, 0]],
               'feature': -2,
               'impurity': 0.0,
               'index': 3,
               'is_categorical': False,
               'is_leaf': True,
               'predicted_class': '1',
               'samples': 0,
               'threshold': -2.0,
               'treeclass': '1'},
              {'child_indices': [5, 6],
               'class_distribution': [[0, 1, 1]],
               'feature': 0,
               'impurity': 1.0,
               'index': 4,
               'is_categorical': False,
               'is_leaf': False,
               'predicted_class': None,
               'samples': 2,
               'threshold': [5.366666666666667, 5.833333333333333],
               'treeclass': None},
              {'child_indices': [-1],
               'class_distribution': [[0, 4, 0]],
               'feature': -2,
               'impurity': 0.0,
               'index': 5,
               'is_categorical': False,
               'is_leaf': True,
               'predicted_class': '2',
               'samples': 4,
               'threshold': -2.0,
               'treeclass': '2'},
              {'child_indices': [-1],
               'class_distribution': [[0, 13, 0]],
               'feature': -2,
               'impurity': 0.0,
               'index': 6,
               'is_categorical': False,
               'is_leaf': True,
               'predicted_class': '1',
               'samples': 13,
               'threshold': -2.0,
               'treeclass': '1'},
              {'child_indices': [-1],
               'class_distribution': [[0, 11, 40]],
               'feature': -2,
               'impurity': 0.752,
               'index': 7,
               'is_categorical': False,
               'is_leaf': True,
               'predicted_class': '2',
               'samples': 51,
               'threshold': -2.0,
               'treeclass': '2'}]

model_loader_custom = ModelLoader("classification", node_dict)
super_tree_custom = SuperTree(
    model=model_loader_custom,
    feature_data=X_data,
    target_data=y_data_raw,
    feature_names=feature_names,
    target_names=target_names
)

super_tree_custom.save_html(filename="custom_tree_output.html")