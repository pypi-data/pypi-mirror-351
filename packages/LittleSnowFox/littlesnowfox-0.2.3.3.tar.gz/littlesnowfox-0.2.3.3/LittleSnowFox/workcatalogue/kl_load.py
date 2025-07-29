
def choosemode_kl(parent_directory_origin,choosemode,debug):
    import os
    global empty_key
    #global current_folder

    current_folder = parent_directory_origin
 

    if choosemode ==  'Lineage':
        print('Current mode is Lineage tracing')
        folder_name = "database"
        new_directory = os.path.join(current_folder, folder_name)
        os.chdir(new_directory)
        current_folder = os.getcwd()
        print("Current folder:", current_folder)
        folder_name = "Tracing_sample"
        new_directory = os.path.join(current_folder, folder_name)
        os.chdir(new_directory)
        current_folder = os.getcwd()
        print("Current folder:", current_folder)
        



    if choosemode ==  'Clustering':
        print('Current mode is Lineage tracing')
        folder_name = "database"
        new_directory = os.path.join(current_folder, folder_name)
        os.chdir(new_directory)
        current_folder = os.getcwd()
        print("Current folder:", current_folder)
        folder_name = "Clustering_sample"
        new_directory = os.path.join(current_folder, folder_name)
        os.chdir(new_directory)
        current_folder = os.getcwd()
        print("Current folder:", current_folder)

    print('Current' + choosemode + ' sample list:')
    print(os.listdir(current_folder))
        
    return current_folder
    empty_key = 1


#需要增加：存稀疏矩阵还是非稀疏矩阵

def kl_save(
    Rep_data_folder,
    choosen_sample_name,
    distance_matrix,
    save_list,
    orig_adata
    ):

    import pandas as pd
    choosen_sample = choosen_sample_name
    print(Rep_data_folder)
    import scipy.io
    import anndata
    
    import os
    # 检查当前路径是否存在 'result' 文件夹
    if not os.path.exists('result'):
    # 如果不存在，则创建 'result' 文件夹
        os.makedirs('result')
    
    folder_name = "result"
    result_directory = os.path.join(Rep_data_folder, folder_name)
    
   
    '''
    for item in save_list:
        save_csv_sample = pd.DataFrame(item)
        save_csv_filename = item + ".csv"
        save_csv_sample.to_csv(save_csv_filename, index=False)

        
         #这里要加一个标题检测，即第一行不是label时，需要自动位移。此处设计成操作限定的形式，即matlab只认第一行的固定标签字样
         #并且只认固定的格式，不然就报错，避免导致错误输入。
    '''


    merged_csv = pd.DataFrame()

    for item in save_list:
        # 使用 eval 动态评估字符串以获取相应的数据
        data = eval(item)
        print(item)
        df = pd.DataFrame(data)
        if 'obsm' in item:
            df = pd.DataFrame(data)
        elif 'obs' in item:
            df = pd.DataFrame(data).reset_index()

        merged_csv = pd.concat([merged_csv, df], axis=1)


        
    
    # 生成变量名列表
    var_names = [f"Var{i+1}" for i in range(len(merged_csv.columns))]

    # 重命名列
    merged_csv.columns = var_names


    folder_name = "result"
    result_directory = os.path.join(Rep_data_folder, folder_name)
    mat_file_path = os.path.join(result_directory, 'distance_matrix.mat')
    scipy.io.savemat(mat_file_path, {'distance_matrix': distance_matrix})
    merged_csv.to_csv(os.path.join(result_directory, "merged_data.csv"), index=False)

    # 输出 DataFrame
    print(merged_csv.head())  # 打印前几行查看数据



    return merged_csv,result_directory




def kl_autosave(
    Rep_data_folder,
    choosen_sample_name,
    distance_matrix,
    save_list,
    orig_adata,
    round_of_smooth,
    neighbor_N
    ):

    import pandas as pd
    choosen_sample = choosen_sample_name
    print(Rep_data_folder)
    import scipy.io
    import anndata
    
    import os
    # 检查当前路径是否存在 'result' 文件夹
    if not os.path.exists('result'):
    # 如果不存在，则创建 'result' 文件夹
        os.makedirs('result')
    
    folder_name = "result"
    result_directory = os.path.join(Rep_data_folder, folder_name)
    
   
    '''
    for item in save_list:
        save_csv_sample = pd.DataFrame(item)
        save_csv_filename = item + ".csv"
        save_csv_sample.to_csv(save_csv_filename, index=False)

        
         #这里要加一个标题检测，即第一行不是label时，需要自动位移。此处设计成操作限定的形式，即matlab只认第一行的固定标签字样
         #并且只认固定的格式，不然就报错，避免导致错误输入。
    '''


    merged_csv = pd.DataFrame()

    for item in save_list:
        # 使用 eval 动态评估字符串以获取相应的数据
        data = eval(item)
        print(item)
        df = pd.DataFrame(data)
        if 'obsm' in item:
            df = pd.DataFrame(data)
        elif 'obs' in item:
            df = pd.DataFrame(data).reset_index()

        merged_csv = pd.concat([merged_csv, df], axis=1)


        
    
    # 生成变量名列表
    var_names = [f"Var{i+1}" for i in range(len(merged_csv.columns))]

    # 重命名列
    merged_csv.columns = var_names

    folder_name = "result"
    result_directory = os.path.join(Rep_data_folder, folder_name)
    mat_file_path = os.path.join(result_directory, 'r' + str(round_of_smooth) + 'n' + str(neighbor_N) + 'distance_matrix.mat')
    scipy.io.savemat(mat_file_path, {'distance_matrix': distance_matrix})
    merged_csv.to_csv(os.path.join(result_directory, 'r' + str(round_of_smooth) + 'n' + str(neighbor_N) + "merged_data.csv"), index=False)

    # 输出 DataFrame
    print(merged_csv.head())  # 打印前几行查看数据



    return merged_csv,result_directory
