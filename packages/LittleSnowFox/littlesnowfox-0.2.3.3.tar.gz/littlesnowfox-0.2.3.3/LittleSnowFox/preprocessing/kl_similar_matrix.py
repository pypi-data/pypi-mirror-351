"""KAILINss - dynamic inference by integrating transcriptome and lineage information"""

#计算稀疏矩阵matrix
#如果输入draw，就转变成非稀疏矩阵并开始画图

def kl_sparse_matrix_sample(
    sample_name,
    data_name,
    if_draw,
    current_folder_input,
    round_of_smooth,
    neighbor_N,
    beta,
    truncation_threshold,
    save_subset,
    use_existing_KNN_graph=False,
    compute_new_Smatrix=True,
    use_full_Smatrix = True
    ):

    global test_chosen_first_time_or_not #这个部分让计算matrix只运行一次。如果启用调试，则每个
    global loading_directory

    import os
    import anndata
    import cospar as cs
    import os
    import sys
    from LittleSnowFox.omic_functions import matrix                           
    import numpy as np
    import pandas as pd
    import scanpy as sc
    import scipy.sparse as ssp
    from cospar.tmap import _tmap_core as tmap_core
    from cospar.tmap import _utils as tmap_util
    from cospar import help_functions as hf
    from cospar import logging as logg
    from cospar import settings
    from cospar import tool as tl

    current_folder = current_folder_input

    if 1:
        sample_name = sample_name
        print("Sample: ",sample_name)
        current_dir = os.getcwd()
        print("Changing the working directory from:", current_dir)
        #eng.run()
        loading_directory = os.path.join(current_folder, sample_name)
        kl_data_menu = "data"
        data_directory = os.path.join(loading_directory, kl_data_menu)
    
    print() 
    print("---------------------------------------------------------------------------------------")
    print("Please put the data at: ",loading_directory,"\data")
    print("---------------------------------------------------------------------------------------")
    print()
    print("Current working directory is:", data_directory)

    # 构建data.h5ad文件的完整路径
    h5ad_file_path = os.path.join(data_directory, data_name)
    adata_using = anndata.read_h5ad(h5ad_file_path)
    import scipy.sparse as sp
    # 将adata.X转换为稀疏矩阵类型
    sparse_X = sp.csr_matrix(adata_using.X.astype(float))
    adata_using.X=sparse_X
    import scipy.sparse as sp


    if sample_name == "Reprogramming":
        distance_matrix = matrix.Reprogramming_distance_matrix(adata_using)
    if sample_name == "Hematopoiesis":
        distance_matrix = matrix.Hematopoiesis_distance_matrix(adata_using)
    else:
        distance_matrix = matrix.distance_matrix(
                            adata_using,
                            round_of_smooth,
                            neighbor_N,
                            beta,
                            truncation_threshold,
                            save_subset,
                            use_existing_KNN_graph=False,
                            compute_new_Smatrix=True,
                            use_full_Smatrix = True,
                            )

    if sp.issparse(distance_matrix):
        print("adata.X is changed as sparse matrix")
    else:
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")


    if if_draw == "draw":
       
        import seaborn as sns
        import matplotlib.pyplot as plt
        import numpy as np
        from scipy import sparse
        # 假设 similarity_matrix 是你的稀疏矩阵数据
        # 将稀疏矩阵转换为非稀疏矩阵
        dense_matrix = distance_matrix.toarray()
        if sp.issparse(adata_using.X):
            print("adata.X is changed as sparse matrix")
        else:
            print("adata.X is changed as dense matrix")
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues')
        # 添加标题和标签
        plt.title('Distance Matrix')
        plt.xlabel('Samples')
        plt.ylabel('Samples')
        # 显示热图
        plt.show()
        import seaborn as sns
        # 假设你已经有了一个稠密矩阵 dense_matrix
        # 设置热图的上下限
        vmin = 0  # 最小值
        vmax = 0.004  # 最大值
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues', vmin=vmin, vmax=vmax)
        # 显示图形
        plt.show()


    return adata_using,loading_directory,distance_matrix
    





#计算非稀疏matrix：
#如果输入draw，开始画图

def kl_dense_matrix_sample(
    sample_name,
    data_name,
    if_draw,
    current_folder_input,
    round_of_smooth=15,
    neighbor_N=20,
    beta=0.1,
    truncation_threshold=0.001,
    save_subset=True,
    use_existing_KNN_graph=False,
    compute_new_Smatrix=True,
    use_full_Smatrix = True,
    ):

    global test_chosen_first_time_or_not #这个部分让计算matrix只运行一次。如果启用调试，则每个
    global loading_directory

    import os
    import anndata
    import cospar as cs
    import os
    import sys
    from LittleSnowFox.omic_functions import matrix                           
    import numpy as np
    import pandas as pd
    import scanpy as sc
    import scipy.sparse as ssp
    from cospar.tmap import _tmap_core as tmap_core
    from cospar.tmap import _utils as tmap_util
    from cospar import help_functions as hf
    from cospar import logging as logg
    from cospar import settings
    from cospar import tool as tl

    current_folder = current_folder_input

    if 1:
        sample_name = sample_name
        print("Sample: ",sample_name)
        current_dir = os.getcwd()
        print("Changing the working directory from:", current_dir)
        #eng.run()
        loading_directory = os.path.join(current_folder, sample_name)
        kl_data_menu = "data"
        data_directory = os.path.join(loading_directory, kl_data_menu)
    
    print() 
    print("---------------------------------------------------------------------------------------")
    print("Please put the data at: ",loading_directory,"\data")
    print("---------------------------------------------------------------------------------------")
    print()
    print("Current working directory is:", data_directory)

    # 构建data.h5ad文件的完整路径
    h5ad_file_path = os.path.join(data_directory, data_name)
    adata_using = anndata.read_h5ad(h5ad_file_path)
    import scipy.sparse as sp
    # 将adata.X转换为稀疏矩阵类型
    sparse_X = sp.csr_matrix(adata_using.X.astype(float))
    adata_using.X=sparse_X
    import scipy.sparse as sp

    if sample_name == "Reprogramming":
        distance_matrix = matrix.Reprogramming_distance_matrix(adata_using)
    elif sample_name == "Hematopoiesis":
        distance_matrix = matrix.Hematopoiesis_distance_matrix(adata_using)
    else:
        distance_matrix = matrix.distance_matrix(
                            adata_using,
                            round_of_smooth,
                            neighbor_N,
                            beta,
                            truncation_threshold,
                            save_subset,
                            use_existing_KNN_graph=False,
                            compute_new_Smatrix=True,
                            use_full_Smatrix = True,
                            )

    dense_matrix = distance_matrix.toarray()

    if sp.issparse(dense_matrix):
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
    else:
        print("adata.X is not a sparse matrix")


    if if_draw == "draw":
       
        import seaborn as sns
        import matplotlib.pyplot as plt
        import numpy as np
        from scipy import sparse
        # 假设 similarity_matrix 是你的稀疏矩阵数据
        # 将稀疏矩阵转换为非稀疏矩阵
        
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues')
        # 添加标题和标签
        plt.title('Distance Matrix')
        plt.xlabel('Samples')
        plt.ylabel('Samples')
        # 显示热图
        plt.show()
        import seaborn as sns
        # 假设你已经有了一个稠密矩阵 dense_matrix
        # 设置热图的上下限
        vmin = 0  # 最小值
        vmax = 0.004  # 最大值
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues', vmin=vmin, vmax=vmax)
        # 显示图形
        plt.show()


    return adata_using,loading_directory,dense_matrix


#------------------------------------------------------------------------------------------------------------------------------
'''
def Reprogramming_distance_matrix(
    adata,
    round_of_smooth,
    neighbor_N,
    beta,
    truncation_threshold,
    save_subset,
    use_existing_KNN_graph=False,
    compute_new_Smatrix=True,
    use_full_Smatrix = True,
):
'''

def kl_sparse_matrix(
        sample_name,
        data_name,
        if_draw,
        current_folder_input,
        adata,
        round_of_smooth,
        neighbor_N,
        beta,
        truncation_threshold,
        save_subset,
        use_existing_KNN_graph=False,
        compute_new_Smatrix=True,
        use_full_Smatrix = True
    ):

    global test_chosen_first_time_or_not #这个部分让计算matrix只运行一次。如果启用调试，则每个
    global loading_directory

    import os
    import anndata
    import cospar as cs
    import os
    import sys
    from LittleSnowFox.omic_functions import matrix                           
    import numpy as np
    import pandas as pd
    import scanpy as sc
    import scipy.sparse as ssp
    from cospar.tmap import _tmap_core as tmap_core
    from cospar.tmap import _utils as tmap_util
    from cospar import help_functions as hf
    from cospar import logging as logg
    from cospar import settings
    from cospar import tool as tl

    current_folder = current_folder_input

    if 1:
        sample_name = sample_name
        print("Sample: ",sample_name)
        current_dir = os.getcwd()
        print("Changing the working directory from:", current_dir)
        #eng.run()
        loading_directory = os.path.join(current_folder, sample_name)
        kl_data_menu = "data"
        data_directory = os.path.join(loading_directory, kl_data_menu)
    
    print() 
    print("---------------------------------------------------------------------------------------")
    print("Please put the data at: ",loading_directory,"\data")
    print("---------------------------------------------------------------------------------------")
    print()
    print("Current working directory is:", data_directory)

    # 构建data.h5ad文件的完整路径
    h5ad_file_path = os.path.join(data_directory, data_name)
    adata_using = anndata.read_h5ad(h5ad_file_path)
    import scipy.sparse as sp
    # 将adata.X转换为稀疏矩阵类型
    sparse_X = sp.csr_matrix(adata_using.X.astype(float))
    adata_using.X=sparse_X
    import scipy.sparse as sp


    distance_matrix = matrix.distance_matrix(
        adata_using,
        round_of_smooth,
        neighbor_N,
        beta,
        truncation_threshold,
        save_subset,
        use_existing_KNN_graph=False,
        compute_new_Smatrix=True,
        use_full_Smatrix = True,
    )

    if sp.issparse(distance_matrix):
        print("adata.X is changed as sparse matrix")
    else:
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")
        print("!!!ERROR!!!: adata.X is not a sparse matrix")


    if if_draw == "draw":
       
        import seaborn as sns
        import matplotlib.pyplot as plt
        import numpy as np
        from scipy import sparse
        # 假设 similarity_matrix 是你的稀疏矩阵数据
        # 将稀疏矩阵转换为非稀疏矩阵
        dense_matrix = distance_matrix.toarray()
        if sp.issparse(adata_using.X):
            print("adata.X is changed as sparse matrix")
        else:
            print("adata.X is changed as dense matrix")
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues')
        # 添加标题和标签
        plt.title('Distance Matrix')
        plt.xlabel('Samples')
        plt.ylabel('Samples')
        # 显示热图
        plt.show()
        import seaborn as sns
        # 假设你已经有了一个稠密矩阵 dense_matrix
        # 设置热图的上下限
        vmin = 0  # 最小值
        vmax = 0.004  # 最大值
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues', vmin=vmin, vmax=vmax)
        # 显示图形
        plt.show()


    return adata_using,loading_directory,distance_matrix
    





#计算非稀疏matrix：
#如果输入draw，开始画图

def kl_dense_matrix(
        sample_name,
        data_name,
        if_draw,
        current_folder_input,
        round_of_smooth,
        neighbor_N,
        beta,
        truncation_threshold,
        save_subset,
        use_existing_KNN_graph=False,
        compute_new_Smatrix=True,
        use_full_Smatrix = True
    ):

    global test_chosen_first_time_or_not #这个部分让计算matrix只运行一次。如果启用调试，则每个
    global loading_directory

    import os
    import anndata
    import cospar as cs
    import os
    import sys
    from LittleSnowFox.omic_functions import matrix                           
    import numpy as np
    import pandas as pd
    import scanpy as sc
    import scipy.sparse as ssp
    from cospar.tmap import _tmap_core as tmap_core
    from cospar.tmap import _utils as tmap_util
    from cospar import help_functions as hf
    from cospar import logging as logg
    from cospar import settings
    from cospar import tool as tl

    current_folder = current_folder_input

    if 1:
        sample_name = sample_name
        print("Sample: ",sample_name)
        current_dir = os.getcwd()
        print("Changing the working directory from:", current_dir)
        #eng.run()
        loading_directory = os.path.join(current_folder, sample_name)
        kl_data_menu = "data"
        data_directory = os.path.join(loading_directory, kl_data_menu)
    
    print() 
    print("---------------------------------------------------------------------------------------")
    print("Please put the data at: ",loading_directory,"\data")
    print("---------------------------------------------------------------------------------------")
    print()
    print("Current working directory is:", data_directory)

    # 构建data.h5ad文件的完整路径
    h5ad_file_path = os.path.join(data_directory, data_name)
    adata_using = anndata.read_h5ad(h5ad_file_path)
    import scipy.sparse as sp
    # 将adata.X转换为稀疏矩阵类型
    sparse_X = sp.csr_matrix(adata_using.X.astype(float))
    adata_using.X=sparse_X
    import scipy.sparse as sp


    distance_matrix = matrix.distance_matrix(
        adata_using,
        round_of_smooth,
        neighbor_N,
        beta,
        truncation_threshold,
        save_subset,
        use_existing_KNN_graph=False,
        compute_new_Smatrix=True,
        use_full_Smatrix = True,
    )




    dense_matrix = distance_matrix.toarray()

    if sp.issparse(dense_matrix):
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
        print("!!!ERROR!!!: adata.X is changed as sparse matrix")
    else:
        print("adata.X is not a sparse matrix")


    if if_draw == "draw":
       
        import seaborn as sns
        import matplotlib.pyplot as plt
        import numpy as np
        from scipy import sparse
        # 假设 similarity_matrix 是你的稀疏矩阵数据
        # 将稀疏矩阵转换为非稀疏矩阵
        
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues')
        # 添加标题和标签
        plt.title('Distance Matrix')
        plt.xlabel('Samples')
        plt.ylabel('Samples')
        # 显示热图
        plt.show()
        import seaborn as sns
        # 假设你已经有了一个稠密矩阵 dense_matrix
        # 设置热图的上下限
        vmin = 0  # 最小值
        vmax = 0.004  # 最大值
        # 绘制热图
        sns.heatmap(dense_matrix, cmap='Blues', vmin=vmin, vmax=vmax)
        # 显示图形
        plt.show()


    return adata_using,loading_directory,dense_matrix


