# -*- coding: UTF-8 -*-
import matplotlib
matplotlib.use('Agg')
import os
from xml.dom.expatbuilder import InternalSubsetExtractor
import random
import anndata
import numpy as np
import scanpy as sc
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.sparse import find
from scipy.sparse import csr_matrix



def plot_Colormap(X_clone, T_data, X1, X2, node_size, save_path, 
                  with_labels=False, draw_edges=True, 
                  specified_tree_index=None, specified_node_name=None):

    #X_clone是读取h5ad的anndata里的adata.obsm['X_clone']
    #C_data是读取聚类数据csv，也就是pd.read_csv('combined_monocle2.csv')而combined_monocle2.csv是matlab里对count_result_rank直接使用writetable存的文件
    #T_data是读取伪时间数据csv，也就是R语言写的monocle2读取的伪时间存成的pseudotime_data_monocle2.csv
    #X1,X2是每个点的坐标，分别是adata.obsm['X_emb']的第一列和第二列
    #node_size是所作图像的点的大小
    #save_path是所作图像的存储路径

    # 染色方案
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_gray_blue", ["#17324b", "#61ade8"])
    
    index_map = {name: idx for idx, name in enumerate(T_data['cell_name'])}
    rev_index_map = {idx: name for idx, name in enumerate(T_data['cell_name'])}
    # 创建伪时间数组
    T = csv_data['pseudotime']
    lenT = len(T)
    # 创建有向图
    G = nx.DiGraph()

    # 从稀疏矩阵中找出非零元素的位置
    rows, cols, _ = find(X_clone)  

    # 将稀疏矩阵逐点提取，以细胞索引为点，逐个添加有向边
    for row, col in zip(rows, cols):
        if row < lenT and col < lenT:
            if T[row] < T[col]:
                G.add_edge(row, col)
            else:
                G.add_edge(col, row)

    # 识别所有弱连通分量
    weak_components = list(nx.weakly_connected_components(G))
    forest = []

    # 遍历每个弱连通分量
    for component in weak_components:
        subgraph = G.subgraph(component).copy()
        roots = [node for node in subgraph if subgraph.in_degree(node) == 0]
        if not roots:
            roots = [next(iter(component))]

        for root in roots:
            tree = nx.dfs_tree(subgraph, source=root)
            forest.append(tree)

    # 确保保存路径存在
    os.makedirs(save_path, exist_ok=True)

    # 根据指定的参数绘制图像

    trees_to_plot = []
    original_indices = []

    if specified_tree_index is not None:
        if isinstance(specified_tree_index, int):
            specified_tree_index = [specified_tree_index]
        trees_to_plot = [forest[i] for i in specified_tree_index if i < len(forest)]
        original_indices = [i for i in specified_tree_index if i < len(forest)]
    elif specified_node_name is not None:
        if isinstance(specified_node_name, int):
            specified_node_name = [specified_node_name]
        node_indices = [index_map.get(name) for name in specified_node_name if name in index_map]
        for index, tree in enumerate(forest):
            if any(node in tree.nodes for node in node_indices):
                trees_to_plot.append(tree)
                original_indices.append(index)
    else:
        trees_to_plot = forest
        original_indices = list(range(len(forest)))

    all_trees = len(trees_to_plot)
    # 绘制指定的树
    for i, (index, tree) in enumerate(zip(original_indices, trees_to_plot), start=1):
        print(f"Plotting... ( {i} / {all_trees} )", end='\r')  # 输出当前进度
        plt.figure(figsize=(16, 9))
        plt.scatter(X1, X2, c='lightgray', s=node_size, alpha=0.6)
        pos = {node: (X1[node], X2[node]) for node in tree.nodes() if node < lenT}
        node_colors = [T[node] for node in tree.nodes() if node < lenT]
        labels = {node: rev_index_map[node] for node in tree.nodes() if node in rev_index_map}
        if draw_edges:
            nx.draw(tree.subgraph(pos.keys()), pos, node_color=node_colors, cmap=cmap,
                   labels=labels if with_labels else None, edge_color='gray', node_size=node_size, font_size=8)
        else:
            nx.draw_networkx_nodes(tree.subgraph(pos.keys()), pos, node_color=node_colors, cmap=cmap, node_size=node_size)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
        plt.colorbar(sm, orientation='vertical', label='Pseudotime')
        plt.title(f"UMAP Plot with Pseudotime Coloring - Tree {index}")
        plt.xlabel('UMAP 1')
        plt.ylabel('UMAP 2')
        plt.savefig(os.path.join(save_path, f'Tree_{index}.png'))
        plt.close()




def plot_Clusters(C_data, T_data, X1, X2, node_size, save_path, Color="#618a03",
                 specified_cluster_index=None,specified_node_name=None):

    #X_clone是读取h5ad的anndata里的adata.obsm['X_clone']
    
    #C_data是读取聚类数据csv，也就是pd.read_csv('combined_monocle2.csv')
    #而combined_monocle2.csv是matlab里对count_result_rank直接使用writetable存的文件
    
    #T_data是读取伪时间数据csv，也就是R语言写的monocle2读取的伪时间存成的pseudotime_data_monocle2.csv
    #X1,X2是每个点的坐标，分别是adata.obsm['X_emb']的第一列和第二列
    #node_size是所作图像的点的大小
    #save_path是所作图像的存储路径

    # 根据MM_new_rank分组细胞名到clusters
    clusters = C_data.groupby('MM_new_rank')['Var3'].apply(set).to_dict()
    # 创建从细胞名到索引的映射
    index_map = {name: idx for idx, name in enumerate(T_data)}

    plt.figure(figsize=(16, 9))
    # 绘制背景点
    plt.scatter(X1, X2, c='lightgray', s=node_size, alpha=0.6)

    # 处理输入参数，允许单个或多个输入
    if isinstance(specified_cluster_index, int):
        specified_cluster_index = [specified_cluster_index]
    if isinstance(specified_node_name, int):
        specified_node_name = [specified_node_name]


    # 处理颜色输入，允许单个颜色或多颜色输入
    if isinstance(Color, str):
        Color = [Color]

     # 确定需要绘制的簇
    if specified_node_name:
        specified_cluster_index = [idx for idx, cells in clusters.items()
                                   if any(node in cells for node in specified_node_name)]
        filename_suffix = f'_node{",".join(map(str, specified_node_name))}'
    elif specified_cluster_index:
        filename_suffix = f'_cell{",".join(map(str, specified_cluster_index))}'
    else:
        specified_cluster_index = list(clusters.keys())
        filename_suffix = '_all'

    # 绘制指定的簇
    for i, idx in enumerate(specified_cluster_index):
        if idx in clusters:
            node_indices = [index_map[node] for node in clusters[idx] if node in index_map]
            color = Color[i % len(Color)] if i < len(Color) else f"#{random.randint(0, 0xFFFFFF):06x}"
            plt.scatter(X1[node_indices], X2[node_indices], c=color, s=node_size, label=f'Cluster {idx}')
    # 在图中特别标出 specified_node_name 对应的节点
    if specified_node_name:
        special_indices = [index_map[node] for node in specified_node_name if node in index_map]
        plt.scatter(X1[special_indices], X2[special_indices], c='red', s=node_size+2, linewidths=1)
        for idx in special_indices:
            plt.text(X1[idx], X2[idx], f'{T_data[idx]}', fontsize=9, color='black', ha='right')
    # 添加图例
    plt.legend(title='Clusters')
    plt.title("UMAP Plot with Cluster Coloring")
    plt.xlabel('UMAP 1')
    plt.ylabel('UMAP 2')
    plt.savefig(f'{save_path}/clusters_plot{filename_suffix}.png')
    plt.close()

'''
#def get_row_data(sparse_matrix, row_index):
#    if row_index < sparse_matrix.shape[0]:  # 确保行索引有效
#        row_start = sparse_matrix.indptr[row_index]
#        row_end = sparse_matrix.indptr[row_index + 1]
#        columns = sparse_matrix.indices[row_start:row_end]
#        values = sparse_matrix.data[row_start:row_end]
#        return columns, values
#    else:
#        return None, None

# 路径设置
file_path = 'Hematopoiesis_progenitor.h5ad'
csv_path =  'combined_data_monocle3.csv'
cluster_path = 'combined_monocle2.csv'

# 读取H5AD
adata = anndata.read_h5ad(file_path)
# 读取CSV
csv_data = pd.read_csv(csv_path)
cluster_data = pd.read_csv(cluster_path)

# 获取X_clone矩阵
X_clone = adata.obsm['X_clone']

#读取umap坐标 
umap_df = pd.DataFrame(adata.obsm['X_emb'], columns=['X1', 'X2'])
X1 = umap_df['X1']
X2 = umap_df['X2']

node_size=8

save_path='G:/ASUMDownloads/dataplot/'
#indexA = 2097
#indexB = 392
## 获取第2097行和第392行的数据
#columns_A, values_A = get_row_data(X_clone, indexA)
#columns_B, values_B = get_row_data(X_clone, indexB)

## 输出结果
#print(f"Columns and values in row {indexA}:")
#print("Columns:", columns_A)
#print("Values:", values_A)

#print(f"Columns and values in row {indexB}:")
#print("Columns:", columns_B)
#print("Values:", values_B)
# 可以在这里入26个科研常用的颜色
#colors = [
#    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0",
#    "#f032e6", "#bcf60c", "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8",
#    "#800000", "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080",
#    "#ffffff", "#000000", "#fabed4", "#ffd700", "#dcbeff", "#f4901b"
#]

# 示例调用
#plot_Clusters(X_clone,cluster_data, csv_data, X1, X2, node_size, save_path)
#plot_Clusters(X_clone,cluster_data, csv_data, X1, X2, node_size, save_path,specified_node_name=9429)
plot_Clusters(X_clone,cluster_data, csv_data, X1, X2, node_size, save_path,specified_cluster_index=[1,2,10,12,13,19,20,21,22,23,24,25,26 ])

#for i in range(1,27):
#    plot_Clusters(X_clone,cluster_data, csv_data, X1, X2, node_size, save_path,specified_cluster_index=i)

#plot_Clusters(X_clone,cluster_data, csv_data, X1, X2, node_size, save_path, Color="#61ade8",specified_node_name=37803)
# 稀疏矩阵 伪时间 X.Y的UMAP,节点大小,存储路径,是否显示标签,是否显示边
#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=True,draw_edges=True,specified_tree_index=232)

#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=True,draw_edges=True,specified_tree_index=[233,234])

#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=False,draw_edges=False,specified_node_name=32689)

#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=True,draw_edges=True,specified_node_name=[5314,4465])

#plt.ion()
'''