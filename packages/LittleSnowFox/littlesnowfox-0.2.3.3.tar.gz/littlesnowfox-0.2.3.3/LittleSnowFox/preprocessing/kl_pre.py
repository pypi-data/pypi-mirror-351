"""KAILINss - dynamic inference by integrating transcriptome and lineage information"""

#计算稀疏矩阵matrix
#如果输入draw，就转变成非稀疏矩阵并开始画图

def merge_tissue_with_singlecell(
    current_folder,
    h5ad_filename,
    csv_filename,
    sample_choose,
    num_samples,
    ):
        import numpy as np
        import os
        import kailin as kl
        current_folder_filter = os.path.join(current_folder, sample_choose)
        current_folder_filter_1 = os.path.join(current_folder_filter, 'data')
        filter_sample = os.path.join(current_folder_filter_1, h5ad_filename)


        csv_sample = os.path.join(current_folder_filter_1, csv_filename)

        import scanpy as sc
        import anndata as ad
        # 假设 filter_sample 是 AnnData 文件路径
        adata_path = filter_sample
        # 使用 anndata 读取文件
        adata_singlecell = ad.read_h5ad(adata_path)

        row_names_cell = adata_singlecell.obs_names

        # 读取列名（基因名）
        column_names_gene = adata_singlecell.var_names
        
        import pandas as pd
        csv_data = pd.read_csv(csv_sample)
        print(csv_data)

        #读取csv_data有多少列
        num_columns = csv_data.shape[1]

        # 将 gene_name 列存储到变量 tissue_gene 中
        tissue_gene = csv_data['gene_name']


        # 确保两者都是集合（去重处理）
        common_elements = set(column_names_gene).intersection(set(tissue_gene))

        # 计算共有元素数量
        num_common_elements = len(common_elements)


        # 转换为列表（如果是 Pandas Series）
        singecell_gene = list(column_names_gene)
        tissue_gene = list(tissue_gene)

        # 找出共有元素
        common_elements = set(singecell_gene).intersection(set(tissue_gene))

        # 找出共有元素在 column_names_gene 和 tissue_gene 中的行号
        singlecell_indices = [i for i, gene in enumerate(singecell_gene) if gene in common_elements]
        tissue_indices = [i for i, gene in enumerate(tissue_gene) if gene in common_elements]


        #过滤adata
        adata_singlecell_filter = adata_singlecell[:,singlecell_indices]


        #过滤tissue
        data_tissue_filter = csv_data.iloc[tissue_indices, :]


        # 将基因名设置为索引，方便排序
        data_tissue_filter = data_tissue_filter.set_index('gene_name')

        # 按照 adata_singlecell.var_names 的顺序重新排序
        data_tissue_filter = data_tissue_filter.reindex(adata_singlecell_filter.var_names)

        data_tissue_filter_t = data_tissue_filter.T

        import scipy.sparse as sp

        adata_singlecell_filter_to = adata_singlecell_filter.X.toarray()

        #合并表达矩阵
        from scipy.sparse import csr_matrix
        merged_X = np.vstack((adata_singlecell_filter_to, data_tissue_filter_t.values))
        merged_X = csr_matrix(merged_X)

        #合并var cell_name
        merged_varname = adata_singlecell_filter.var_names


        #存储obs gene_name
        #merged_varname = [adata_singlecell_filter.var_names,data_tissue_filter_t.index]
        merged_obsname = pd.Index(adata_singlecell_filter.obs_names).append(data_tissue_filter_t.index)

        import pandas as pd
        import anndata as ad
        merged_obsname_df = pd.DataFrame(index=merged_obsname, columns=[])  # 空 DataFrame 仅带索引
        merged_varname_df = pd.DataFrame(index=merged_varname, columns=[])

        # 创建 AnnData 对象
        adata_merged = ad.AnnData(X=merged_X, obs=merged_obsname_df, var=merged_varname_df)

        print(adata_merged)

        return adata_merged
    




