# -*- coding: UTF-8 -*-
import matplotlib
matplotlib.use('Agg')
import os
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



def plot_Clonemap(X_clone, C_data, node_size, save_path, 
                  with_labels=False, draw_edges=True, 
                  specified_tree_index=None, specified_node_name=None,
                  plot_clusters=False):
    
    xclone_path = os.path.join(save_path, 'barcode_singlecell')
    xclone_cluster_path = os.path.join(save_path, 'barcode_cluster')
    

    #X_clone是读取h5ad的anndata里的adata.obsm['X_clone']
    #C_data是读取聚类数据csv，也就是pd.read_csv('combined_monocle2.csv')而combined_monocle2.csv是matlab里对count_result_rank直接使用writetable存的文件
    #node_size是所作图像的点的大小
    #save_path是所作图像的存储路径
    sorted_C_data = C_data.sort_values(by='Var3')
    cell_names = sorted_C_data['Var3'].values
    X1 = sorted_C_data['Var1'].values
    X2 = sorted_C_data['Var2'].values
    T = sorted_C_data['Pst'].values

    # 染色方案
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_gray_blue", ["#17324b", "#61ade8"])
    
    index_map = {name: idx for idx, name in enumerate(cell_names)}
    rev_index_map = {idx: name for idx, name in enumerate(cell_names)}
    # 创建伪时间数组
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
    if plot_clusters == True:
        for tree in trees_to_plot:
            nodes_in_tree = [node for node in tree.nodes()]
            node_names_in_tree = [rev_index_map[node] for node in nodes_in_tree if node in rev_index_map]
            #print(node_names_in_tree)
            plot_Pseudotimemap(C_data, node_size, save_path, specified_cell_name=node_names_in_tree,plot_clusters=True,use_pseudotime=True,go_on=1)
    else:
        for i, (index, tree) in enumerate(zip(original_indices, trees_to_plot), start=1):
            print(f"Plotting... ( {i} / {all_trees} )", end='\r')  # 输出当前进度
            plt.figure(figsize=(16, 9))
            plt.scatter(X1, X2, c='lightgray', s=node_size, alpha=0.6)
            pos = {node: (X1[node], X2[node]) for node in tree.nodes() if node < lenT}
            node_colors = [T[node] for node in tree.nodes() if node < lenT]
            labels = {node: rev_index_map[node] for node in tree.nodes() if node in rev_index_map}
            if draw_edges:
                nc = nx.draw(tree.subgraph(pos.keys()), pos, node_color=node_colors, cmap=cmap,
                       labels=labels if with_labels else None, edge_color='gray', node_size=node_size, font_size=8)
            else:
                nc = nx.draw_networkx_nodes(tree.subgraph(pos.keys()), pos, node_color=node_colors, cmap=cmap, node_size=node_size)

            # 使用nc作为mappable对象传递给colorbar
            plt.colorbar(nc, orientation='vertical', label='Pseudotime')
            plt.title(f"Barcode tracing - Tree {index}")
            plt.xlabel('UMAP 1')
            plt.ylabel('UMAP 2')
            plt.savefig(os.path.join(xclone_path, f'Tree_{index}.png'))
            plt.close()




def plot_Pseudotimemap(C_data, node_size, save_path, Color="#618a03",
                 specified_cluster_index=None,specified_cell_name=None,
                 with_labels=False,plot_clusters=True,use_pseudotime=False,go_on=0):
    #C_data是读取聚类数据csv，也就是pd.read_csv('combined_monocle2.csv')
    #而combined_monocle2.csv是matlab里对count_result_rank直接使用writetable存的文件
    #node_size是所作图像的点的大小
    #save_path是所作图像的存储路径
    print('Pseudotimemap')
    pseudotime_path = os.path.join(save_path, 'pseudotime_singlecell')
    pseudotime_cluster_path = os.path.join(save_path, 'pseudotime_cluster')
    xclone_cluster_path = os.path.join(save_path, 'barcode_cluster')
    

    X1 = C_data['Var1'].values
    X2 = C_data['Var2'].values
    T  =  C_data['Pst'].values
    # 染色方案
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_gray_blue", ["#17324b", "#61ade8"])

    cellname = {name: idx for idx, name in enumerate(C_data['Var3'])}
    # 根据MM_new_rank分组细胞名到clusters
    clusters = C_data.groupby('MM_new_rank')['Var3'].apply(set).to_dict()

    plt.figure(figsize=(16, 9))
    # 绘制背景点
    plt.scatter(X1, X2, c='lightgray', s=node_size, alpha=0.6)

    # 处理输入参数，允许单个或多个输入
    if isinstance(specified_cluster_index, int):
        specified_cluster_index = [specified_cluster_index]
    if isinstance(specified_cell_name, int):
        specified_cell_name = [specified_cell_name]
    if isinstance(Color, str):
        Color = [Color]

    # 确定需要绘制的簇
    if specified_cell_name:
        specified_cluster_index = [idx for idx, cells in clusters.items()
                                   if any(node in cells for node in specified_cell_name)]
        filename_suffix = f'_cell{format_suffix(specified_cell_name)}'
    elif specified_cluster_index:
        filename_suffix = f'_cluster{format_suffix(specified_cluster_index)}'
    else:
        specified_cluster_index = list(clusters.keys())
        filename_suffix = '_all'
    #若预先指定的Color不够则扩展 Color 列表
    while len(Color) < len(specified_cluster_index):
        Color.append(f"#{random.randint(0, 0xFFFFFF):06x}")
    # 绘制指定的簇
    if plot_clusters:
        for i, idx in enumerate(specified_cluster_index):
            if idx in clusters:
                node_indices = [cellname[name] for name in clusters[idx]]
                if use_pseudotime:
                    color = T[node_indices]  # 使用伪时间的颜色
                    plt.scatter(X1[node_indices], X2[node_indices], c=color, cmap=cmap, s=node_size, label=f'Cluster {idx}')
                else:                        # 使用Color的颜色
                    plt.scatter(X1[node_indices], X2[node_indices], c=Color[i], s=node_size, label=f'Cluster {idx}')
    # 在图中特别标出 specified_cell_name 对应的节点
    if specified_cell_name:
        special_indices = [cellname[name] for name in specified_cell_name if name in cellname]
        if use_pseudotime:
            color = T[special_indices]  # 使用伪时间颜色
            plt.scatter(X1[special_indices], X2[special_indices], c=color, cmap=cmap, s=node_size+2, linewidths=1)
        else:
            plt.scatter(X1[special_indices], X2[special_indices], c='red', s=node_size+2, linewidths=1)
        if with_labels:
            for idx in special_indices:
                plt.text(X1[idx], X2[idx], f'{C_data["Var3"].iloc[idx]}', fontsize=9, color='black', ha='right')
    # 添加图例
    if plot_clusters:
        plt.legend(title='Clusters')
    plt.title("UMAP Plot" + (" with Cluster Coloring" if plot_clusters else "") + (" using Pseudotime" if use_pseudotime else ""))
    plt.xlabel('UMAP 1')
    plt.ylabel('UMAP 2')
    if plot_clusters == True and go_on == 0:
        plt.savefig(f'{pseudotime_cluster_path}\clusters_plot{filename_suffix}.png')
    if plot_clusters == False and go_on == 0:
        plt.savefig(f'{pseudotime_path}\clusters_plot{filename_suffix}.png')
    if plot_clusters == True and go_on == 1:
        print('Continue from Barcode cluster')
        plt.savefig(f'{xclone_cluster_path}\clusters_plot{filename_suffix}.png')
    plt.close()

def format_suffix(items):
    if len(items) > 4:
        formatted = f'{",".join(map(str, items[:3]))},...,{items[-1]}'
    else:
        formatted = ",".join(map(str, items))
    return formatted



'''
# 路径设置
file_path = 'Hematopoiesis_progenitor.h5ad'
cluster_path = 'combined_monocle2.csv'
# 读取H5AD
adata = anndata.read_h5ad(file_path)
# 获取X_clone矩阵
X_clone = adata.obsm['X_clone']
# 读取CSV
cluster_data = pd.read_csv(cluster_path)
node_size=8
save_path='G:/ASUMDownloads/dataplot2'
plot_Clusters(cluster_data, node_size, save_path,plot_clusters=True,specified_cell_name=9429,use_pseudotime=True)
'''
