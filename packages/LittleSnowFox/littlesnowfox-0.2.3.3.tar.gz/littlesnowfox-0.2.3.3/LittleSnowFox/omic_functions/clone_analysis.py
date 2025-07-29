def Clone_path(
    sample_name,
    data_name,
    current_folder_input,
    combined_data_monocle_name,
    time_compute_data,
    ):
    import os
    import anndata
    current_folder = current_folder_input
    if 1:
        sample_name = sample_name
        print("Sample: ",sample_name)
        current_dir = os.getcwd()
        print("Changing the working directory from:", current_dir)
        #eng.run()
        loading_directory = os.path.join(current_folder, sample_name)
        kl_data_menu = "data"
        kl_result_menu = "result"
        data_directory = os.path.join(loading_directory, kl_data_menu)
        result_directory = os.path.join(loading_directory, kl_result_menu)
    print() 
    print("---------------------------------------------------------------------------------------")
    print("Please put the data at: ",loading_directory,"\data")
    print("---------------------------------------------------------------------------------------")
    print()
    print("Current working directory is:", data_directory)
    # 构建data.h5ad文件的完整路径
    h5ad_file_path = os.path.join(data_directory, data_name)
    combined_data_monocle_path = os.path.join(result_directory, combined_data_monocle_name)
    print(h5ad_file_path)
    print(combined_data_monocle_path)
    file_path = h5ad_file_path
    csv_path = combined_data_monocle_path
    h5ad_file_path = os.path.join(data_directory, data_name)
    T_data = os.path.join(data_directory, time_compute_data)
    pseudotime_map = os.path.join(result_directory, 'pseudotime_map.csv')
    

    
    
    return file_path,csv_path,result_directory,T_data,pseudotime_map

'''
    file_path, csv_path = Clone_data(
    sample_name,
    data_name,
    current_folder_input,
    combined_data_monocle_name
    )
'''

    
#Singlecell_barcode( )
def Singlecell_barcode__all(X_clone, T_data, X1, X2, node_size, save_path, 
    file_path, csv_path, 
    with_labels=False, draw_edges=True,
    specified_tree_index=None, 
    specified_node_name=None):
        
    #X_clone是那个稀疏矩阵，T是存伪时间的数组，X1，X2是从emb里提取出的坐标,node_size是画出来的点的直径
    #save_path是要将画出来的每个细胞所属的cluster图的存储路径，with_labels是否加细胞编号, draw_edges是否画箭头
    
    # -*- coding: UTF-8 -*-
    import os
    from re import X
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



    #######################################################################################################
    
    # 路径设置
    #file_path = 'Hematopoiesis_progenitor.h5ad'
    #csv_path = 'G:/ASUMDownloads/combined_data_monocle3.csv'
        
    ####################################################################################################

    
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


        
        
def Cluster_barcode(
                X_clone, C_data, T_data, 
                  X1, X2, node_size, save_path, 
                  Color="#618a03",
                 specified_cluster_index=None,
                 specified_node_name=None
                 ):

    plt.figure(figsize=(16, 9))
    # 绘制背景点
    plt.scatter(X1, X2, c='lightgray', s=node_size, alpha=0.6)

    # 处理输入参数，允许单个或多个输入
    if isinstance(specified_cluster_index, int):
        specified_cluster_index = [specified_cluster_index]
    if isinstance(specified_node_name, int):
        specified_node_name = [specified_node_name]

    # 创建集合和索引映射
    clusters = {col: set(C_data[col].dropna()) for col in C_data.columns}
    index_map = {name: idx for idx, name in enumerate(T_data['cell_name'])}

    # 处理颜色输入，允许单个颜色或多颜色输入
    if isinstance(Color, str):
        Color = [Color]

    # 确定需要绘制的簇
    if specified_node_name:
        specified_cluster_index = [i for i, cluster in enumerate(clusters.values())
                                   if any(node in cluster for node in specified_node_name)]
    if specified_cluster_index is None:
        specified_cluster_index = range(len(clusters))  # 如果未指定，选择所有簇

    # 绘制指定的簇
    for i, (cluster_name, cluster_set) in enumerate(clusters.items()):
        if i in specified_cluster_index:
            # 获取此簇的节点索引
            node_indices = [index_map[node] for node in cluster_set if node in index_map]
            # 选择颜色，如果颜色不够则随机生成新颜色
            color = Color[i % len(Color)] if i < len(Color) else f"#{random.randint(0, 0xFFFFFF):06x}"
            # 绘制簇
            plt.scatter(X1[node_indices], X2[node_indices], c=color, s=node_size, label=f'Cluster {cluster_name}')
    
    # 添加图例
    plt.legend(title='Clusters')
    plt.title("UMAP Plot with Cluster Coloring")
    plt.xlabel('UMAP 1')
    plt.ylabel('UMAP 2')
    plt.savefig(f'{save_path}/clusters_plot.png')
    plt.close()



    
    
    
    
    
def draw_embedding(
    sample_name,
    data_name,
    current_folder_input,
    combined_data_monocle_name
    
    ):
    
    print()
    
    
    
    
    
def get_row_data(sparse_matrix, row_index):
    if row_index < sparse_matrix.shape[0]:  # 确保行索引有效
        row_start = sparse_matrix.indptr[row_index]
        row_end = sparse_matrix.indptr[row_index + 1]
        columns = sparse_matrix.indices[row_start:row_end]
        values = sparse_matrix.data[row_start:row_end]
        return columns, values
    else:
        return None, None


'''
# 路径设置
file_path = 'Hematopoiesis_progenitor.h5ad'
csv_path = 'G:/ASUMDownloads/combined_data_monocle3.csv'

# 读取H5AD文件
adata = anndata.read_h5ad(file_path)
# 读取CSV
csv_data = pd.read_csv(csv_path)
# 读取 CSV 文件
cluster_data = pd.read_csv('G:/ASUMDownloads/var3_intervals.csv')

# 获取X_clone矩阵
X_clone = adata.obsm['X_clone']

#读取umap坐标 
umap_df = pd.DataFrame(adata.obsm['X_emb'], columns=['X1', 'X2'])
X1 = umap_df['X1']
X2 = umap_df['X2']

node_size=4

save_path='G:/ASUMDownloads/dataplot/'
indexA = 2097
indexB = 392
# 获取第2097行和第392行的数据
columns_A, values_A = get_row_data(X_clone, indexA)
columns_B, values_B = get_row_data(X_clone, indexB)

# 输出结果
print(f"Columns and values in row {indexA}:")
print("Columns:", columns_A)
print("Values:", values_A)

print(f"Columns and values in row {indexB}:")
print("Columns:", columns_B)
print("Values:", values_B)

# 示例调用
plot_Clusters(X_clone,cluster_data, csv_data, X1, X2, node_size, save_path, Color="#61ade8",specified_node_name=37803)
# 稀疏矩阵 伪时间 X.Y的UMAP,节点大小,存储路径,是否显示标签,是否显示边
#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=True,draw_edges=True,specified_tree_index=232)
#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=True,draw_edges=True,specified_tree_index=[233,234])
#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=False,draw_edges=False,specified_node_name=32689)
#plot_Colormap(X_clone,csv_data,X1,X2,node_size,save_path,with_labels=True,draw_edges=True,specified_node_name=[5314,4465])
#plt.ion()
'''