# coding=utf-8
from re import match


def download_database_cigarettes():

    import os
    import urllib.request
    
    # 获取当前工作目录
    current_path = os.getcwd()
    print("Package located at:", current_path)
    
    
    database_path = os.path.join(parent_directory, "database")
    
    
    Clustering_sample_path = os.path.join(database_path, "Clustering_sample")
    Tracing_sample_path = os.path.join(database_path, "Tracing_sample")
    
    
    e_cigarettes_difference_expression_path = os.path.join(Clustering_sample_path, "e_cigarettes_difference_expression")
    e_cigarettes_path = os.path.join(Clustering_sample_path, "e_cigarettes_path")
    
    #e_cigarettes
    url = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/9f85370b854946d18f82e7f45b19b298.xlsx?auth_key=1735889508-ee437713875e450187468f998959eca2-0-f2b5984d89f3b346ba283a4854ed39fd&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx%3Bfilename*%3Dutf-8%27%27%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx&user_id=1028920560074189860&x-verify=1"
    ur2 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/bc0d55baad7a407590a14266486ac2f0.xlsx?auth_key=1735889524-84a3688312ff4160bf1ade60524401e8-0-0448ce55456a71ae459d2b69336b4456&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx&user_id=1028920560074189860&x-verify=1"
    ur3 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/356b1df4e3e747fdb3f3e978cb29c3da.xlsx?auth_key=1735889537-23b1631552904c7f9535e55a658f14f9-0-032faae20f248c1e2f58de3390a9c98b&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx&user_id=1028920560074189860&x-verify=1"
    ur4 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/0de7ca7580094a8298f2a892abd01a3c.xlsx?auth_key=1735889547-4c903664004f4c62afc4ea48187e2824-0-4d264a0321bfc5159779cca5ebefc3c2&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx&user_id=1028920560074189860&x-verify=1"
    ur5 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/43a06b502b2b495087b99fa981d4a7c5.xlsx?auth_key=1735889556-76f8a46444da47d8a7018343125dc65b-0-5a6221ae49ac57f9326de8de70d750b1&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx%3Bfilename*%3Dutf-8%27%27%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx&user_id=1028920560074189860&x-verify=1"
    ur6 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/587539c1ed594855a47fa82334ecef6a.xlsx?auth_key=1735889565-cc7c9233264b427c8f3e269e4fc8ab92-0-5b43eba51c590f380b519be0401e4c6c&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx%3Bfilename*%3Dutf-8%27%27%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx&user_id=1028920560074189860&x-verify=1"
   
    
    file_path_1 = os.path.join(e_cigarettes_path, "成年小鼠-尼古丁.xlsx")
    file_path_2 = os.path.join(e_cigarettes_path, "幼年小鼠-新鲜空气.xlsx")
    file_path_3 = os.path.join(e_cigarettes_path, "幼年小鼠-电子烟.xlsx")
    file_path_4 = os.path.join(e_cigarettes_path, "幼年小鼠-尼古丁.xlsx")
    file_path_5 = os.path.join(e_cigarettes_path, "成年小鼠-电子烟.xlsx")
    file_path_6 = os.path.join(e_cigarettes_path, "成年小鼠-新鲜空气.xlsx")
    
    urllib.request.urlretrieve(url, file_path_1)
    urllib.request.urlretrieve(ur2, file_path_2)
    urllib.request.urlretrieve(ur3, file_path_3)
    urllib.request.urlretrieve(ur4, file_path_4)
    urllib.request.urlretrieve(ur5, file_path_5)
    urllib.request.urlretrieve(ur6, file_path_6)
    
    print("Successful of e_cigarettes")
    
    #e_cigarettes_difference_expression_data
    
    e_cigarettes_difference_expression_data_path = os.path.join(e_cigarettes_difference_expression_path, "data")
    
    ur7  = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/87330bc70c3a48bfb892312b2b51339c.xlsx?auth_key=1735890482-ac81cd4ba5984cc1b9644433899b53b8-0-916ad7219eb94cc8e343866325df461e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx&user_id=1028920560074189860&x-verify=1"
    ur8  = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/b900f9c3b88b430089628495de330c85.xlsx?auth_key=1735890553-a3cf94a6cdcd4430ba672d157cd5bbf7-0-a091fc8ec3600c6261386c5bb1f643ab&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx&user_id=1028920560074189860&x-verify=1"
    ur9  = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/1ae6a4209f614fbe80702929f461d59b.xlsx?auth_key=1735890605-c1f41ffc16234643baf15c09de37a0d8-0-5e889922c48224504524e6f7a8972308&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx&user_id=1028920560074189860&x-verify=1"
    ur10 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/6d3ea69abd044af18c50652ff9fd365c.xlsx?auth_key=1735890632-887ea5f09fcc427f9560a750bb358774-0-29d325c8ad09e40e118f8d4b1b36906c&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4vs%25E6%2588%2590%25E5%25B9%25B4%25E7%259A%2584%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F-%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4vs%25E6%2588%2590%25E5%25B9%25B4%25E7%259A%2584%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F-%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx&user_id=1028920560074189860&x-verify=1"
    ur11 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/6787653e7298483996c7ea4ecbfbbb71.xlsx?auth_key=1735890666-dc579eb62e65410cb10e4e210f191e0e-0-3c40b6969546bdc65dc5922aec0cf6b0&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25B9%25BC%25E5%25B9%25B4vs%25E6%2588%2590%25E5%25B9%25B4%25E7%259A%2584%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594-%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx%3Bfilename*%3Dutf-8%27%27%25E5%25B9%25BC%25E5%25B9%25B4vs%25E6%2588%2590%25E5%25B9%25B4%25E7%259A%2584%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594-%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx&user_id=1028920560074189860&x-verify=1"
    ur12 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/86929fea50814848a601c4dc60fde4ae.xlsx?auth_key=1735890697-5e3a1468a498495d93694dd17bc48197-0-e9089694b5f58efa6065f786fcc55bcd&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259Fvs%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594-%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx%3Bfilename*%3Dutf-8%27%27%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259Fvs%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594-%25E5%25B9%25BC%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx&user_id=1028920560074189860&x-verify=1"
    ur13 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/fc90078fa2bd4b9185559244ea87a7a5.xlsx?auth_key=1735892531-0f70f42863614302a637c32de27536e8-0-db444e8e115f8ae32e7d683ab8b81e20&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx%3Bfilename*%3Dutf-8%27%27%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F.xlsx&user_id=1028920560074189860&x-verify=1"
    ur14 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/5f7b01d13c3c4d68b675436651228b4d.xlsx?auth_key=1735892570-9cf251ed744e4294888703016ac95b79-0-82a4a548905af81de6dbe2422dd1eb81&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx%3Bfilename*%3Dutf-8%27%27%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E6%2596%25B0%25E9%25B2%259C%25E7%25A9%25BA%25E6%25B0%2594.xlsx&user_id=1028920560074189860&x-verify=1"
    ur15 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/dbacaf8bf46a4ede8d967f89c959ea1c.xlsx?auth_key=1735892615-ed0ac75a19854d06ab0fbf9295362b67-0-ada622e6cbd135e75197c14e2fe3b94b&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx%3Bfilename*%3Dutf-8%27%27%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%25B0%25BC%25E5%258F%25A4%25E4%25B8%2581.xlsx&user_id=1028920560074189860&x-verify=1"
    ur16 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/87a00a55cb454787bc598e5edef9ce06.xlsx?auth_key=1735892644-34fbad59442c4f15a4ed8ba0fd396228-0-cc414ecf47cf03315fca39bdfdfcd27a&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%258F%25AA%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F%25E5%2592%258C%25E7%25A9%25BA%25E6%25B0%2594.xlsx%3Bfilename*%3Dutf-8%27%27%25E6%2588%2590%25E5%25B9%25B4%25E5%25B0%258F%25E9%25BC%25A0-%25E5%258F%25AA%25E7%2594%25B5%25E5%25AD%2590%25E7%2583%259F%25E5%2592%258C%25E7%25A9%25BA%25E6%25B0%2594.xlsx&user_id=1028920560074189860&x-verify=1"
    
    file_path_7  = os.path.join(e_cigarettes_difference_expression_data_path, "幼年小鼠-电子烟.xlsx")
    file_path_8  = os.path.join(e_cigarettes_difference_expression_data_path, "幼年小鼠_新鲜空气.xlsx")
    file_path_9  = os.path.join(e_cigarettes_difference_expression_data_path, "幼年小鼠-尼古丁.xlsx")
    file_path_10 = os.path.join(e_cigarettes_difference_expression_data_path, "幼年vs成年的电子烟-幼年小鼠-电子烟.xlsx")
    file_path_11 = os.path.join(e_cigarettes_difference_expression_data_path, "幼年vs成年的新鲜空气-幼年小鼠-电子烟.xlsx")
    file_path_12 = os.path.join(e_cigarettes_difference_expression_data_path, "电子烟vs新鲜空气-幼年小鼠-电子烟.xlsx")
    file_path_13 = os.path.join(e_cigarettes_difference_expression_data_path, "成年小鼠-电子烟.xlsx")
    file_path_14 = os.path.join(e_cigarettes_difference_expression_data_path, "成年小鼠-新鲜空气.xlsx")
    file_path_15 = os.path.join(e_cigarettes_difference_expression_data_path, "成年小鼠-尼古丁.xlsx")
    file_path_16 = os.path.join(e_cigarettes_difference_expression_data_path, "成年小鼠-只电子烟和空气.xlsx")
    
    urllib.request.urlretrieve(ur7, file_path_7)
    urllib.request.urlretrieve(ur8, file_path_8)
    urllib.request.urlretrieve(ur9, file_path_9)
    urllib.request.urlretrieve(ur10, file_path_10)
    urllib.request.urlretrieve(ur11, file_path_11)
    urllib.request.urlretrieve(ur12, file_path_12)
    urllib.request.urlretrieve(ur13, file_path_13)
    urllib.request.urlretrieve(ur14, file_path_14)
    urllib.request.urlretrieve(ur15, file_path_15)
    urllib.request.urlretrieve(ur16, file_path_16)
    
    
    print("Successful of e_cigarettes_difference_expression(data)")
    
    #e_cigarettes_difference_expression_result
    
    e_cigarettes_difference_expression_result_path = os.path.join(e_cigarettes_difference_expression_path, "result")
    
    ur17 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/5627ce617b72461f8ac58c73754a3c3d.mat?auth_key=1735900825-55dcae5c71d548fbb054ee4d2da50511-0-69d06629cb8a9823282b6eda99f4e003&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix_merged.mat%3Bfilename*%3Dutf-8%27%27distance_matrix_merged.mat&user_id=1028920560074189860&x-verify=1"
    ur18 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/fd910a88563945e8a0d53ee0b52c4b88.mat?auth_key=1735900917-439d1b3654fe40d7aedf9451b47b9c57-0-9c3866eb10ebaa3e72f1e81d690f9ad9&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix_all.mat%3Bfilename*%3Dutf-8%27%27distance_matrix_all.mat&user_id=1028920560074189860&x-verify=1"
    ur19 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/a06824afc669402c9a2e0c85a6e59a59.mat?auth_key=1735901073-8cc14d2ac08d4637961674de039e0e95-0-53648e2f8876f2cc0b0e1498310a4ae1&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix.mat%3Bfilename*%3Dutf-8%27%27distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur20 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/180c14c5b16b4ceaa5a5f2d9df647f70.csv?auth_key=1735901278-2318fb6e6cca4028a60f28450f3ca242-0-1acffd56ce2dc840aed9b4516395cc27&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_%25E5%2585%25A8%25E5%259F%25BA%25E5%259B%25A0.csv%3Bfilename*%3Dutf-8%27%27result_%25E5%2585%25A8%25E5%259F%25BA%25E5%259B%25A0.csv&user_id=1028920560074189860&x-verify=1"
    ur21 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/b379d4dd433b49d9bb3da8738a940224.mat?auth_key=1735901344-b65a273146274f02bc6f216fc846f081-0-4b2e78ab3b3f25b2a3f1eab7344a296a&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix_RNA.mat%3Bfilename*%3Dutf-8%27%27distance_matrix_RNA.mat&user_id=1028920560074189860&x-verify=1"
    ur22 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/3b871a22e9374e6dabdd1d47a4320365.csv?auth_key=1735901374-305467a9a5f748e0877b6fbc9f8ed577-0-daf18d665af33ea6593717465d26adb8&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_%25E6%25B7%25B7%25E5%2590%2588%25E6%2598%25A0%25E5%25B0%2584.csv%3Bfilename*%3Dutf-8%27%27result_%25E6%25B7%25B7%25E5%2590%2588%25E6%2598%25A0%25E5%25B0%2584.csv&user_id=1028920560074189860&x-verify=1"
    ur23 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/f3aecfaee7ab419fa0c0e1cf0b7f3030.csv?auth_key=1735901425-a9aa5c3c9c4e4887a88caf4f21c47513-0-872f3d1b7f1890d4ee10ebb54149e73a&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_%25E5%25B7%25AE%25E5%25BC%2582.csv%3Bfilename*%3Dutf-8%27%27result_%25E5%25B7%25AE%25E5%25BC%2582.csv&user_id=1028920560074189860&x-verify=1"
    ur24 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/37c7cb1b25a94586b58015cd9677d4af.csv?auth_key=1735901450-255bbf815d9441379fdc6fb616ca6a02-0-63c6d040226d9c361755399375b13428&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_RNA.csv%3Bfilename*%3Dutf-8%27%27result_RNA.csv&user_id=1028920560074189860&x-verify=1"
    ur25 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/9eba1c7712764d06852e26689acddaaa.csv?auth_key=1735901478-13c4063b91f641ec8599cc4d5f1c2885-0-d90787324ab8695d2c92702a1fa4c9f5&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_group.csv%3Bfilename*%3Dutf-8%27%27result_group.csv&user_id=1028920560074189860&x-verify=1"
    ur26 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/1c310df9ed664bc9b8e7162858059142.csv?auth_key=1735901500-cb4e14fd01744858ad14f3dc068c421a-0-4e4d875dc17de304cf8cc13c19610179&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident_RNA.csv%3Bfilename*%3Dutf-8%27%27orig_ident_RNA.csv&user_id=1028920560074189860&x-verify=1"
    ur27 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/35a83f9169d2412197317e9af0c1aa38.csv?auth_key=1735901558-f7dfe0beb8724313bbd8f843ce6c79c7-0-12d7114241e27f26a3353f6985339e8e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident_merged.csv%3Bfilename*%3Dutf-8%27%27orig_ident_merged.csv&user_id=1028920560074189860&x-verify=1"
    ur28 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/6aff47573d7b4f0db69e9c9791fb02dc.csv?auth_key=1735901579-313e422f159649f8855cb62b414fee7f-0-996ddb21cbdadee298bb1dd23b255b1d&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident_all.csv%3Bfilename*%3Dutf-8%27%27orig_ident_all.csv&user_id=1028920560074189860&x-verify=1"
    ur29 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/f07c1ce9923f485d929683137c591b62.csv?auth_key=1735901595-e6e8fa6f76b640f48bc8a50a46c01b9a-0-6e2b57b5839c62d383f8b73b728faa4a&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident.csv%3Bfilename*%3Dutf-8%27%27orig_ident.csv&user_id=1028920560074189860&x-verify=1"
  
    
    file_path_17 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix_merged.mat")
    file_path_18 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix_all.mat")
    file_path_19 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix.mat")
    file_path_20 = os.path.join(e_cigarettes_difference_expression_result_path, "result_全基因.csv")
    file_path_21 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix_RNA.mat")
    file_path_22 = os.path.join(e_cigarettes_difference_expression_result_path, "result_混合映射.csv")
    file_path_23 = os.path.join(e_cigarettes_difference_expression_result_path, "result_差异.csv")
    file_path_24 = os.path.join(e_cigarettes_difference_expression_result_path, "result_RNA.csv")
    file_path_25 = os.path.join(e_cigarettes_difference_expression_result_path, "result_group.csv")
    file_path_26 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident_RNA.csv")
    file_path_27 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident_merged.csv")
    file_path_28 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident_all.csv")
    file_path_29 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident.csv")


    urllib.request.urlretrieve(ur17, file_path_17)
    urllib.request.urlretrieve(ur18, file_path_18)
    urllib.request.urlretrieve(ur19, file_path_19)
    urllib.request.urlretrieve(ur20, file_path_20)
    urllib.request.urlretrieve(ur21, file_path_21)
    urllib.request.urlretrieve(ur22, file_path_22)
    urllib.request.urlretrieve(ur23, file_path_23)
    urllib.request.urlretrieve(ur24, file_path_24)
    urllib.request.urlretrieve(ur25, file_path_25)
    urllib.request.urlretrieve(ur26, file_path_26)
    urllib.request.urlretrieve(ur27, file_path_27)
    urllib.request.urlretrieve(ur28, file_path_28)
    urllib.request.urlretrieve(ur29, file_path_29)
    print("Successful of e_cigarettes_difference_expression_result")
    
    
def download_database_fibroblasts():
    
    import os
    import urllib.request
    
    # 获取当前工作目录
    current_path = os.getcwd()
    print("Package located at:", current_path)
    
    
    database_path = os.path.join(parent_directory, "database")
    
    
    Clustering_sample_path = os.path.join(database_path, "Clustering_sample")
    Tracing_sample_path = os.path.join(database_path, "Tracing_sample")
    
    fibroblasts_path = os.path.join(Clustering_sample_path, "fibroblasts")
    fibroblasts_data_path = os.path.join(fibroblasts_path, "data")
    fibroblasts_result_path = os.path.join(fibroblasts_path, "result")
    
    #fibroblasts_data
    
    ur30 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/cd73cee2a897427fae3a61660fe89f02.h5ad?auth_key=1735906043-8d1032b34aa740ec9dc0b18d9baea4cd-0-b3bc0a0f24c997ee28b4ba4db51e6f0e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DMI-%25E9%25AB%2598%25E5%258F%2598%25E5%259F%25BA%25E5%259B%25A0.h5ad%3Bfilename*%3Dutf-8%27%27MI-%25E9%25AB%2598%25E5%258F%2598%25E5%259F%25BA%25E5%259B%25A0.h5ad&user_id=1028920560074189860&x-verify=1"
    ur31 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/1c2297e9683f44deb40d2697ccc6d3a9.h5ad?auth_key=1735906167-7ec59c317a13452ca1c6b1260fc8d553-0-ca9acd907b286d9c6f56d785557dc26b&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25BF%2583%25E6%25A2%2597-%25E6%2588%2590%25E7%25BA%25A4%25E7%25BB%25B4%25E7%25BB%2586%25E8%2583%259E-%25E9%25AB%2598%25E5%258F%2598%25E5%259F%25BA%25E5%259B%25A0.h5ad%3Bfilename*%3Dutf-8%27%27%25E5%25BF%2583%25E6%25A2%2597-%25E6%2588%2590%25E7%25BA%25A4%25E7%25BB%25B4%25E7%25BB%2586%25E8%2583%259E-%25E9%25AB%2598%25E5%258F%2598%25E5%259F%25BA%25E5%259B%25A0.h5ad&user_id=1028920560074189860&x-verify=1"
    ur32 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/ee12846c1c694effa18910f1de4aa3c9.h5ad?auth_key=1735906245-2c0675b0974a41aeacfb5961640fc33a-0-bc71e6784f625d04252151745ce95c8d&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25BF%2583%25E6%25A2%2597-%25E6%2588%2590%25E7%25BA%25A4%25E7%25BB%25B4%25E7%25BB%2586%25E8%2583%259E-%25E6%2589%2580%25E6%259C%2589%25E5%259F%25BA%25E5%259B%25A0.h5ad%3Bfilename*%3Dutf-8%27%27%25E5%25BF%2583%25E6%25A2%2597-%25E6%2588%2590%25E7%25BA%25A4%25E7%25BB%25B4%25E7%25BB%2586%25E8%2583%259E-%25E6%2589%2580%25E6%259C%2589%25E5%259F%25BA%25E5%259B%25A0.h5ad&user_id=1028920560074189860&x-verify=1"
    ur33 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/74eff92a199646b9937ff4e3c56f3ce3.h5ad?auth_key=1735906260-c20c328f46514f52ae9f345fcdabc208-0-3e14ff9aae4139e802f7dfc25127227e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%258A%25BD%25E6%25A0%25B7_%25E5%2585%25A8%25E5%259F%25BA_8000.h5ad%3Bfilename*%3Dutf-8%27%27%25E6%258A%25BD%25E6%25A0%25B7_%25E5%2585%25A8%25E5%259F%25BA_8000.h5ad&user_id=1028920560074189860&x-verify=1"
    ur34 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/8ff258b53ba841bb93f5f4e9a667f738.h5ad?auth_key=1735906337-65edddc4375b4ae79fa28d44ef50a7a4-0-c501d388c2e6e6f1235db808a060a560&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DMI_fiberRNA.h5ad%3Bfilename*%3Dutf-8%27%27MI_fiberRNA.h5ad&user_id=1028920560074189860&x-verify=1"
    ur35 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/363eafeef7684f2294d7939d50324933.csv?auth_key=1735906355-4a513c562ad04781afb533d6230655c0-0-295351dd32c1ed46f632e979242cdd57&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E5%25BF%2583%25E8%2582%258C%25E6%25A2%2597%25E6%25AD%25BB%25E6%2599%25AE%25E9%2580%259A%25E8%25BD%25AC%25E5%25BD%2595%25E7%25BB%2584.csv%3Bfilename*%3Dutf-8%27%27%25E5%25BF%2583%25E8%2582%258C%25E6%25A2%2597%25E6%25AD%25BB%25E6%2599%25AE%25E9%2580%259A%25E8%25BD%25AC%25E5%25BD%2595%25E7%25BB%2584.csv&user_id=1028920560074189860&x-verify=1"
    ur36 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/ab0ac0b0d5434f5883630faed35e6196.h5ad?auth_key=1735906378-6cba50e6f6384f2b98c83b9d03f55f3a-0-7deb0a43e15c2661f99a54ec0a0a0728&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dtissue_and_sc.h5ad%3Bfilename*%3Dutf-8%27%27tissue_and_sc.h5ad&user_id=1028920560074189860&x-verify=1"
    ur37 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/aaefe015e1214822966668975b2b586c.h5ad?auth_key=1735906436-c10c86818289488b9ac06a8bb398eeea-0-fe0ccad5690e06b49ff40ac210cec777&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E6%258A%25BD%25E6%25A0%25B7_%25E9%25AB%2598%25E5%258F%2598_8000.h5ad%3Bfilename*%3Dutf-8%27%27%25E6%258A%25BD%25E6%25A0%25B7_%25E9%25AB%2598%25E5%258F%2598_8000.h5ad&user_id=1028920560074189860&x-verify=1"
    
    
    file_path_30 = os.path.join(fibroblasts_data_path, "MI-高变基因.h5ad")
    file_path_31 = os.path.join(fibroblasts_data_path, "心梗-成纤维细胞-高变基因.h5ad")
    file_path_32 = os.path.join(fibroblasts_data_path, "心梗-成纤维细胞-所有基因.h5ad")
    file_path_33 = os.path.join(fibroblasts_data_path, "抽样_全基_8000.h5ad")
    file_path_34 = os.path.join(fibroblasts_data_path, "MI_fiberRNA.h5ad")
    file_path_35 = os.path.join(fibroblasts_data_path, "心肌梗死普通转录组.csv")
    file_path_36 = os.path.join(fibroblasts_data_path, "tissue_and_sc.h5ad")
    file_path_37 = os.path.join(fibroblasts_data_path, "抽样_高变_8000.h5ad")
    
    
    urllib.request.urlretrieve(ur30, file_path_30)
    urllib.request.urlretrieve(ur31, file_path_31)
    urllib.request.urlretrieve(ur32, file_path_32)
    urllib.request.urlretrieve(ur33, file_path_33)
    urllib.request.urlretrieve(ur34, file_path_34)
    urllib.request.urlretrieve(ur35, file_path_35)
    urllib.request.urlretrieve(ur36, file_path_36)
    urllib.request.urlretrieve(ur37, file_path_37)
    
    print("Successful of fibroblasts(data)")
    
    
    #fibroblasts_result
    ur38 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/dc3412a093634baca507e972d445686e.mat?auth_key=1735911408-3091b6c1ec0d432e99b794c238e27a2d-0-4bb98c17e81ec032c991a1478f6fe2f5&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix_merged.mat%3Bfilename*%3Dutf-8%27%27distance_matrix_merged.mat&user_id=1028920560074189860&x-verify=1"
    ur39 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/9b4d05ca2d97407fba283b93b7aef472.mat?auth_key=1735911440-8f8acb5480ce45099c9e713400090d07-0-c233899e4685a2b5bd21630efa1ba484&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix_all.mat%3Bfilename*%3Dutf-8%27%27distance_matrix_all.mat&user_id=1028920560074189860&x-verify=1"
    ur40 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/a3e40578a23b4d549c49a5e58961ea82.mat?auth_key=1735911454-f4bcd93c6a044545ade3273fa1ff48a6-0-5beeaac3ae7bf484a0d00d6ee7152a20&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix.mat%3Bfilename*%3Dutf-8%27%27distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur41 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/7c6dbeaf6eea4a65b3ff68f3575646a9.csv?auth_key=1735911478-c9eb3457ed624508b6f05e25e5022e3c-0-1abc9dd1d6772d4ae0bf354a6c30683b&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_%25E5%2585%25A8%25E5%259F%25BA%25E5%259B%25A0.csv%3Bfilename*%3Dutf-8%27%27result_%25E5%2585%25A8%25E5%259F%25BA%25E5%259B%25A0.csv&user_id=1028920560074189860&x-verify=1"
    ur42 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/0af15eb2097747ac961d1ac42bbbd896.mat?auth_key=1735911495-89634b966a254a598f6ba355e41e51a7-0-fb6a1b85678bea688082fc112527078f&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix_RNA.mat%3Bfilename*%3Dutf-8%27%27distance_matrix_RNA.mat&user_id=1028920560074189860&x-verify=1" 
    ur43 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/8f3d420b9cfa4fe9ab66f05d23f6c924.csv?auth_key=1735911512-3b9e6528c97c4939987ac97cf7793542-0-bb9bf0b5c55034aa079b82eb46543015&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_%25E6%25B7%25B7%25E5%2590%2588%25E6%2598%25A0%25E5%25B0%2584.csv%3Bfilename*%3Dutf-8%27%27result_%25E6%25B7%25B7%25E5%2590%2588%25E6%2598%25A0%25E5%25B0%2584.csv&user_id=1028920560074189860&x-verify=1"   
    ur44 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/339eddaa2a3d48fc94ef51ebc2897c8c.csv?auth_key=1735911533-0a46c6162cdf41af9951608f1c77d673-0-f11d05838c2b402e1603bd08398bd11e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_%25E5%25B7%25AE%25E5%25BC%2582.csv%3Bfilename*%3Dutf-8%27%27result_%25E5%25B7%25AE%25E5%25BC%2582.csv&user_id=1028920560074189860&x-verify=1"    
    ur45 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/d28010aee2d34d7a8a4be2a10b6f727d.csv?auth_key=1735911550-d375da50f0274c379475a1766faf38b2-0-458e7ae2335372aa3adb99bfc2ec8c1d&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_RNA.csv%3Bfilename*%3Dutf-8%27%27result_RNA.csv&user_id=1028920560074189860&x-verify=1"    
    ur46 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/bec0c04a55824f6ea01124de020729eb.csv?auth_key=1735911607-7cf529b4c7c043e1928e2e9f6a5a9728-0-2f4ce2d0e9c5d3dd0252ea4af1b54052&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_group.csv%3Bfilename*%3Dutf-8%27%27result_group.csv&user_id=1028920560074189860&x-verify=1"    
    ur47 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/6822ee99e51149148e2c77b4a5f83599.csv?auth_key=1735911629-2627abcd3e964bffb9399f49c482ccfc-0-4101f091abf63e09020602c1595d03b8&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident_RNA.csv%3Bfilename*%3Dutf-8%27%27orig_ident_RNA.csv&user_id=1028920560074189860&x-verify=1"    
    ur48 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/dab7df6109e34498bdd9e15f5cb33fde.csv?auth_key=1735911645-afedbaa819734a7db9a69579cffa7710-0-c5c2c98be08e121b7effccb8ba8ae92e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident_merged.csv%3Bfilename*%3Dutf-8%27%27orig_ident_merged.csv&user_id=1028920560074189860&x-verify=1"    
    ur49 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/6e3eab7232d04a049701e0f45a291a66.csv?auth_key=1735911661-d9bd7d3f9c8a46909f81497f01bd26da-0-dac8d941b0389d776c94bb6143c95246&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident_all.csv%3Bfilename*%3Dutf-8%27%27orig_ident_all.csv&user_id=1028920560074189860&x-verify=1"    
    ur50 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/ca31f010c5394ac98360eab15a4ee880.csv?auth_key=1735911679-9966b0953de445a2bb5703b075579dd7-0-aba5e8c279f54a79e0237709e49b34b2&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dorig_ident.csv%3Bfilename*%3Dutf-8%27%27orig_ident.csv&user_id=1028920560074189860&x-verify=1"  
    
    file_path_38 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix_merged.mat")
    file_path_39 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix_all.mat")
    file_path_40 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix.mat")
    file_path_41 = os.path.join(e_cigarettes_difference_expression_result_path, "result_全基因.csv")
    file_path_42 = os.path.join(e_cigarettes_difference_expression_result_path, "distance_matrix_RNA.mat")
    file_path_43 = os.path.join(e_cigarettes_difference_expression_result_path, "result_混合映射.csv")
    file_path_44 = os.path.join(e_cigarettes_difference_expression_result_path, "result_差异.csv")
    file_path_45 = os.path.join(e_cigarettes_difference_expression_result_path, "result_RNA.csv")
    file_path_46 = os.path.join(e_cigarettes_difference_expression_result_path, "result_group.csv")
    file_path_47 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident_RNA.csv")
    file_path_48 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident_merged.csv")
    file_path_49 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident_all.csv")
    file_path_50 = os.path.join(e_cigarettes_difference_expression_result_path, "orig_ident.csv")


    urllib.request.urlretrieve(ur38, file_path_38)
    urllib.request.urlretrieve(ur39, file_path_39)
    urllib.request.urlretrieve(ur40, file_path_40)
    urllib.request.urlretrieve(ur41, file_path_41)
    urllib.request.urlretrieve(ur42, file_path_42)
    urllib.request.urlretrieve(ur43, file_path_43)
    urllib.request.urlretrieve(ur44, file_path_44)
    urllib.request.urlretrieve(ur45, file_path_45)
    urllib.request.urlretrieve(ur46, file_path_46)
    urllib.request.urlretrieve(ur47, file_path_47)
    urllib.request.urlretrieve(ur48, file_path_48)
    urllib.request.urlretrieve(ur49, file_path_49)
    urllib.request.urlretrieve(ur50, file_path_50)
    
    print("Successful of fibroblasts_result")
    

def download_database_Hematopoiesis():
    
    import os
    import urllib.request
    
    # 获取当前工作目录
    current_path = os.getcwd()
    print("Package located at:", current_path)
    
    database_path = os.path.join(parent_directory, "database")
    
    Clustering_sample_path = os.path.join(database_path, "Clustering_sample")
    Tracing_sample_path = os.path.join(database_path, "Tracing_sample")
    
    Hematopoiesis_path = os.path.join(Tracing_sample_path, "Hematopoiesis")
    Hematopoiesis_data_path = os.path.join(Hematopoiesis_path, "data")
    Hematopoiesis_result_path = os.path.join(Hematopoiesis_path, "result")
    
    #Hematopoiesis_data
    url = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/88f930658bec4b00827b74b7f5b5f93b.h5ad?auth_key=1735912053-0b6b062d25f94dd6a222312a7d3abd18-0-15ca84300dfee023e5e0cab402404453&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DHematopoiesis_progenitor.h5ad%3Bfilename*%3Dutf-8%27%27Hematopoiesis_progenitor.h5ad&user_id=1028920560074189860&x-verify=1"
    file_path_1 = os.path.join(Hematopoiesis_data_path, "Hematopoiesis_progenitor.h5ad") 
    urllib.request.urlretrieve(url, file_path_1) 
    print("Successful of Hematopoiesis(data)")
    
    #Hematopoiesis_result
    ur51 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/aa4d35f70fcd477692b219fbbf4a5e48.mat?auth_key=1735912274-9ef7e4dbc80a4f218f3736915cf68445-0-5a92d6c1a33325420163eb5b3e162eed&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dr1n30distance_matrix.mat%3Bfilename*%3Dutf-8%27%27r1n30distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur52 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/3f5e35776152442dadb34e5bee23079e.csv?auth_key=1735912337-5bb2c00c346c40e2bb10f0259732ec84-0-2968f443da56c2128cbcc33da3c7438b&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dumap_blood.csv%3Bfilename*%3Dutf-8%27%27umap_blood.csv&user_id=1028920560074189860&x-verify=1"
    ur53 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/84d92ee5285d4838ae261b124bf26a91.csv?auth_key=1735912350-f8212509e4014537882e92691f11187d-0-758efc9933333cf89e36774a0cb1dceb&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dtest_umap_blood.csv%3Bfilename*%3Dutf-8%27%27test_umap_blood.csv&user_id=1028920560074189860&x-verify=1"
    ur54 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/a0869949416f4c2c958d3090203c5307.csv?auth_key=1735912358-9506b854bdb940ad8277607f8778d005-0-db0e43ca21508959a640ab5b7ceb8101&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dtest_Figure_c_matrix_blood.csv%3Bfilename*%3Dutf-8%27%27test_Figure_c_matrix_blood.csv&user_id=1028920560074189860&x-verify=1"
    ur55 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/d2d8eb80a12b473d8705543f1995028b.csv?auth_key=1735912371-054aef6a9f354c2982b4f875d74d87d9-0-b762dfdb48453178789d72df77badc77&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dtest_Figure_c_label_blood.csv%3Bfilename*%3Dutf-8%27%27test_Figure_c_label_blood.csv&user_id=1028920560074189860&x-verify=1"
    ur56 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/3ef744256f9e4f619fffb771f5736dbb.csv?auth_key=1735912386-f7193057ecba4f99aa06ef4a9bc7011b-0-bfb0694541b52ced6798d3635fdfab91&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dpseudotime_monocle3.csv%3Bfilename*%3Dutf-8%27%27pseudotime_monocle3.csv&user_id=1028920560074189860&x-verify=1"
    ur57 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/2c4d972f574e4e90a6d07a8244cfafa7.csv?auth_key=1735912398-0becbd0ab0e5427e854f2047f468b4d6-0-0ed17d62b88641de13ed60dc13f1ead4&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dpseudotime_monocle2.csv%3Bfilename*%3Dutf-8%27%27pseudotime_monocle2.csv&user_id=1028920560074189860&x-verify=1"
    ur58 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/6ce8446015b9489c92c1d41bc29d0fed.csv?auth_key=1735912407-a1ee9a960e6445d0b65ccebf9feaa57d-0-3acfee28f832394b93813adfa5e5fa11&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dmerged_data.csv%3Bfilename*%3Dutf-8%27%27merged_data.csv&user_id=1028920560074189860&x-verify=1"
    ur59 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/fbec216615bb474ebcb1437dfa1d9999.csv?auth_key=1735912416-9a284719214a4aec8d81850e3da96dea-0-aa8c30fc9a101179b158d443a5c21cdb&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DFigure_c_matrix_blood.csv%3Bfilename*%3Dutf-8%27%27Figure_c_matrix_blood.csv&user_id=1028920560074189860&x-verify=1"
    ur60 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/26d88bb9a9944be1a1becffbc2f3b524.csv?auth_key=1735912426-a74a15321102492c99142b1a6103f292-0-3900b8a76fa61c55ae7767c4e7d6d5e2&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DFigure_c_label_blood.csv%3Bfilename*%3Dutf-8%27%27Figure_c_label_blood.csv&user_id=1028920560074189860&x-verify=1"
    ur61 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/8a226cc135a9429280b5e62b0a9a1d60.csv?auth_key=1735912438-a04e2a1b950f4cca965816534b43fc3d-0-119a90bbdd6a0e8db689a7fc81ff7b1a&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dcombined_monocle2.csv%3Bfilename*%3Dutf-8%27%27combined_monocle2.csv&user_id=1028920560074189860&x-verify=1"
    ur62 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/14f3f5248326443d94edd81550770cb9.csv?auth_key=1735912457-79010b6982bb4a9bb142cfc916babfd9-0-e85929ffaa4124357445633280197c33&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dr1n30merged_data.csv%3Bfilename*%3Dutf-8%27%27r1n30merged_data.csv&user_id=1028920560074189860&x-verify=1"
    
    
    file_path_51 = os.path.join(Hematopoiesis_result_path, "r1n30distance_matrix.mat")
    file_path_52 = os.path.join(Hematopoiesis_result_path, "umap_blood.csv")
    file_path_53 = os.path.join(Hematopoiesis_result_path, "test_umap_blood.csv")
    file_path_54 = os.path.join(Hematopoiesis_result_path, "Figure_c_matrix_blood.csv")
    file_path_55 = os.path.join(Hematopoiesis_result_path, "Figure_c_label_blood.csv")
    file_path_56 = os.path.join(Hematopoiesis_result_path, "pseudotime_monocle2.csv")
    file_path_57 = os.path.join(Hematopoiesis_result_path, "pseudotime_monocle3.csv")
    file_path_58 = os.path.join(Hematopoiesis_result_path, "merged_data.csv")
    file_path_59 = os.path.join(Hematopoiesis_result_path, "Figure_c_matrix_blood.csv")
    file_path_60 = os.path.join(Hematopoiesis_result_path, "Figure_c_label_blood.csv")
    file_path_61 = os.path.join(Hematopoiesis_result_path, "combined_monocle2.csv")
    file_path_62 = os.path.join(Hematopoiesis_result_path, "r1n30merged_data.csv")
    
    urllib.request.urlretrieve(ur51, file_path_51)
    urllib.request.urlretrieve(ur52, file_path_52)
    urllib.request.urlretrieve(ur53, file_path_53)
    urllib.request.urlretrieve(ur54, file_path_54)
    urllib.request.urlretrieve(ur55, file_path_55)
    urllib.request.urlretrieve(ur56, file_path_56)
    urllib.request.urlretrieve(ur57, file_path_57)
    urllib.request.urlretrieve(ur58, file_path_58)
    urllib.request.urlretrieve(ur59, file_path_59)
    urllib.request.urlretrieve(ur60, file_path_60)
    urllib.request.urlretrieve(ur61, file_path_61)
    urllib.request.urlretrieve(ur62, file_path_62)

    print("Successful of Hematopoiesis_result")
    
    
def download_database_Reprogramming():
    
    import os
    import urllib.request
    
    # 获取当前工作目录
    current_path = os.getcwd()
    print("Package located at:", current_path)
    
    database_path = os.path.join(parent_directory, "database")
    
    Clustering_sample_path = os.path.join(database_path, "Clustering_sample")
    Tracing_sample_path = os.path.join(database_path, "Tracing_sample")
    
    Reprogramming_path = os.path.join(Tracing_sample_path, "Reprogramming")
    Reprogramming_data_path = os.path.join(Reprogramming_path, "data")
    Reprogramming_result_path = os.path.join(Reprogramming_path, "result")
    
    #Reprogramming_data
    url = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/88f930658bec4b00827b74b7f5b5f93b.h5ad?auth_key=1735912053-0b6b062d25f94dd6a222312a7d3abd18-0-15ca84300dfee023e5e0cab402404453&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DHematopoiesis_progenitor.h5ad%3Bfilename*%3Dutf-8%27%27Hematopoiesis_progenitor.h5ad&user_id=1028920560074189860&x-verify=1"
    file_path_1 = os.path.join(Reprogramming_data_path, "reprogramming_1.h5ad") 
    urllib.request.urlretrieve(url, file_path_1) 
    print("Successful of Reprogramming(data)")
    
    #Reprogramming_result
    ur63 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/0bdce026da4a4af98ce782f39b496514.mat?auth_key=1735913836-4d05965a93be4564965f1fb5e073fac9-0-ea1a86cfd0cb815e0f16fd8bffe58324&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dr3n100distance_matrix.mat%3Bfilename*%3Dutf-8%27%27r3n100distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur64 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/79a74e14c4c143a789b186cf4ca4d956.mat?auth_key=1735913852-af51c74a22a6476f9dba3c3dd9679831-0-3afbc4754cd928c22e29acebe78f8fcb&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dr1n100distance_matrix.mat%3Bfilename*%3Dutf-8%27%27r1n100distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur65 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/fd60f32076f54d9797d05903b1b077b6.mat?auth_key=1735913870-605294d76d6448588b063b40276556cb-0-0dec54783ee0f7fa560cccb9135c8e14&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dreprogamming.mat%3Bfilename*%3Dutf-8%27%27reprogamming.mat&user_id=1028920560074189860&x-verify=1" 
    ur66 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/f447d8ca10474490b08862721b4c9c3b.mat?auth_key=1735913893-72632d69e995405db36def64f88d748b-0-c27b1635b31ff8e70d4e29962ffc8dfa&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dmatlab.mat%3Bfilename*%3Dutf-8%27%27matlab.mat&user_id=1028920560074189860&x-verify=1"
    ur67 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/409cecd983554f84a9bdef2a81e342ae.csv?auth_key=1735913905-7e469ee4f21049959d6dde715d7a2a85-0-68cacf693a45c9e0aa3f2abcd9446f08&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dumap_reprog.csv%3Bfilename*%3Dutf-8%27%27umap_reprog.csv&user_id=1028920560074189860&x-verify=1"   
    ur68 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/d5b1e18a621e4a6b86b1f98f76b832be.csv?auth_key=1735913942-b33a2689a3614a62b6f207c86beda1ac-0-3468f5b38908ec2a2b19ca43c9b02e69&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dr3n100merged_data.csv%3Bfilename*%3Dutf-8%27%27r3n100merged_data.csv&user_id=1028920560074189860&x-verify=1"   
    ur69 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/ed6aabca90f742c490158cac860b2a92.csv?auth_key=1735914360-614fc88ba6b44e5fa28d330d6a911cff-0-30533ea26269bcd9c6ba7fbfce362a54&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DFigure_c_matrix_reprog.csv%3Bfilename*%3Dutf-8%27%27Figure_c_matrix_reprog.csv&user_id=1028920560074189860&x-verify=1"   
    ur70 =  "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/a1e38e9928ad405189970eb90092c301.csv?auth_key=1735914378-790a8c73436b4c5489de418d52e37b21-0-d47887dfa15c1997f2cd785144778cf3&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DFigure_c_label_reprog.csv%3Bfilename*%3Dutf-8%27%27Figure_c_label_reprog.csv&user_id=1028920560074189860&x-verify=1"   

    
    file_path_63 = os.path.join(Reprogramming_result_path, "r3n100distance_matrix.mat")
    file_path_64 = os.path.join(Reprogramming_result_path, "r1n100distance_matrix.mat")
    file_path_65 = os.path.join(Reprogramming_result_path, "reprogamming.mat")
    file_path_66 = os.path.join(Reprogramming_result_path, "matlab.mat")
    file_path_67 = os.path.join(Reprogramming_result_path, "umap_reprog.csv")
    file_path_68 = os.path.join(Reprogramming_result_path, "r3n100merged_data.csv")
    file_path_69 = os.path.join(Reprogramming_result_path, "Figure_c_matrix_reprog.csv")
    file_path_70 = os.path.join(Reprogramming_result_path, "Figure_c_label_reprog.csv")

    
    urllib.request.urlretrieve(ur63, file_path_63)
    urllib.request.urlretrieve(ur64, file_path_64)
    urllib.request.urlretrieve(ur65, file_path_65)
    urllib.request.urlretrieve(ur66, file_path_66)
    urllib.request.urlretrieve(ur67, file_path_67)
    urllib.request.urlretrieve(ur68, file_path_68)
    urllib.request.urlretrieve(ur69, file_path_69)
    urllib.request.urlretrieve(ur70, file_path_70)


    print("Successful of Reprogramming_result")
    
      
def download_database_Nerveferroptosis():
    
    import os
    import urllib.request
    
    # 获取当前工作目录
    current_path = os.getcwd()
    print("Package located at:", current_path)
    
    database_path = os.path.join(parent_directory, "database")
    
    Clustering_sample_path = os.path.join(database_path, "Clustering_sample")
    Tracing_sample_path = os.path.join(database_path, "Tracing_sample")
    
    #Tracing_sample文件夹下的path
    Nerveferroptosis_remove_R1_3_4_path = os.path.join(Tracing_sample_path, "Nerveferroptosis_remove_R1_3_4")
    Nerveferroptosis_15_21_path = os.path.join(Tracing_sample_path, "Nerveferroptosis_15_21")
    Nerveferroptosis_path = os.path.join(Tracing_sample_path, "Nerveferroptosis")
    
    #Nerveferroptosis文件夹下的data
    Nerveferroptosis_remove_R1_3_4_data_path = os.path.join(Nerveferroptosis_remove_R1_3_4_path, "data")
    Nerveferroptosis_15_21_data_path = os.path.join(Nerveferroptosis_15_21_path, "data")
    Nerveferroptosis_data_path = os.path.join(Nerveferroptosis_path, "data")
    
    #Nerveferroptosis文件夹下的result
    Nerveferroptosis_remove_R1_3_4_result_path = os.path.join(Nerveferroptosis_remove_R1_3_4_path, "result")
    Nerveferroptosis_15_21_result_path = os.path.join(Nerveferroptosis_15_21_path, "result")
    Nerveferroptosis_result_path = os.path.join(Nerveferroptosis_path, "result")
    
    #Nerveferroptosis文件夹下的Rdata
    Nerveferroptosis_Rdata_path = os.path.join(Nerveferroptosis_path, "Rdata")
    
    
    
    #Nerveferroptosis_Rdata

    ur71 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/095fd0ed278448c2b6458208c6e8b578.rdata?auth_key=1735937114-ee9a469a7b384b9caeea470e19c61ac7-0-fbf1626675fe949a2ece80127b236063&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DGSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4.rdata%3Bfilename*%3Dutf-8%27%27GSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4.rdata&user_id=1028920560074189860&x-verify=1"
    ur72 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/a4324b2f41ef458ca49e094d68d38f18.rdata?auth_key=1735937393-fdb7ec8b7cfb4ed4a1c95703818c06de-0-318d0f412e6b016765220a718ae2296e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DGSE232429deatd_%2520%25E7%25B2%25BE%25E7%25BB%2586%25E8%25BF%2587%25E6%25BB%25A4.rdata%3Bfilename*%3Dutf-8%27%27GSE232429deatd_%2520%25E7%25B2%25BE%25E7%25BB%2586%25E8%25BF%2587%25E6%25BB%25A4.rdata&user_id=1028920560074189860&x-verify=1"
    ur73 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/8e830d79ce8644568bafc77e5c1861cb.r?auth_key=1735937426-66afa6fc4fd442faadadbfa0a5416d36-0-6d33bd262a7d377319591f27fb91a34e&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DGSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4.r%3Bfilename*%3Dutf-8%27%27GSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4.r&user_id=1028920560074189860&x-verify=1"
    ur74 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/36c4cb9c761f4d28a2484c61ae4bbc4e.r?auth_key=1735937458-44b2f4a4ba124f96853860c03e9dff8a-0-d3f755ea6b92a90092568a4cded03cbe&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DGSE232429deatd_%2520%25E7%25B2%25BE%25E7%25BB%2586%25E8%25BF%2587%25E6%25BB%25A4.r%3Bfilename*%3Dutf-8%27%27GSE232429deatd_%2520%25E7%25B2%25BE%25E7%25BB%2586%25E8%25BF%2587%25E6%25BB%25A4.r&user_id=1028920560074189860&x-verify=1"

    file_path71 = os.path.join(Nerveferroptosis_Rdata_path, "GSE232429deatd_粗糙过滤.rdata") 
    file_path72 = os.path.join(Nerveferroptosis_Rdata_path, "GSE232429deatd_精细过滤.rdata")
    file_path73 = os.path.join(Nerveferroptosis_Rdata_path, "GSE232429deatd_粗糙过滤.r")
    file_path74 = os.path.join(Nerveferroptosis_Rdata_path, "GSE232429deatd_精细过滤.r")

    urllib.request.urlretrieve(ur71, file_path71) 
    urllib.request.urlretrieve(ur72, file_path72)
    urllib.request.urlretrieve(ur73, file_path73)
    urllib.request.urlretrieve(ur74, file_path74)

    print("Successful of Nerveferroptosis(data)")
    
    
    
    #Nerveferroptosis_remove_R1_3_4_data
    
    ur75 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/ec5497f7d9204d499dae3715727a90a8.rdata?auth_key=1735937861-21f34c3e2211449aa71b15e1942a856a-0-4548e28a347a9a6bbd58d980618092cc&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E9%2587%258D%25E7%2594%25BB%25E7%259F%25A9%25E9%2598%25B5GSE232429.rdata%3Bfilename*%3Dutf-8%27%27%25E9%2587%258D%25E7%2594%25BB%25E7%259F%25A9%25E9%2598%25B5GSE232429.rdata&user_id=1028920560074189860&x-verify=1"
    ur76 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/5691e294fdcc415680e0e812cd9c2c18.h5seurat?auth_key=1735937898-8a22f2d5bff4458fa40d0b7e04ee0f8e-0-eeeb9739708f9f1bb46bbcb457939832&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E9%2587%258D%25E7%2594%25BB%25E7%259F%25A9%25E9%2598%25B5GSE232429_testAB.integrated.h5seurat%3Bfilename*%3Dutf-8%27%27%25E9%2587%258D%25E7%2594%25BB%25E7%259F%25A9%25E9%2598%25B5GSE232429_testAB.integrated.h5seurat&user_id=1028920560074189860&x-verify=1"
    ur77 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/426b0fe3333a48708c11e225a5851d9d.h5ad?auth_key=1735937933-654ac49868954023a09c19e61a564735-0-8d8ead5f2161bdac5ac4f0cf29282826&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E9%2587%258D%25E7%2594%25BB%25E7%259F%25A9%25E9%2598%25B5GSE232429_testAB.integrated.h5ad%3Bfilename*%3Dutf-8%27%27%25E9%2587%258D%25E7%2594%25BB%25E7%259F%25A9%25E9%2598%25B5GSE232429_testAB.integrated.h5ad&user_id=1028920560074189860&x-verify=1"

    file_path75 = os.path.join(Nerveferroptosis_remove_R1_3_4_data_path, "重画矩阵GSE232429.rdata") 
    file_path76 = os.path.join(Nerveferroptosis_remove_R1_3_4_data_path, "重画矩阵GSE232429_testAB.integrated.h5seurat") 
    file_path77 = os.path.join(Nerveferroptosis_remove_R1_3_4_data_path, "重画矩阵GSE232429_testAB.integrated.h5ad") 

    urllib.request.urlretrieve(ur75, file_path75) 
    urllib.request.urlretrieve(ur76, file_path76)
    urllib.request.urlretrieve(ur77, file_path77)
    
    print("Successful of Nerveferroptosis_remove_R1_3_4_data")
    
    
    
    #Nerveferroptosis_remove_R1_3_4_result
    
    ur78 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/5f397faeb7594c5eba828a6664d9772a.mat?auth_key=1735938280-87d41472d526453e9e8031286f391a90-0-c1fc85f7ae3ddf1df05ebbf96d8e49b2&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dr1n13000distance_matrix.mat%3Bfilename*%3Dutf-8%27%27r1n13000distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur79 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/1a3c6041c86b4ef487a80b735240a38e.csv?auth_key=1735938308-c8420e1843134b7f948e55725b2c04ac-0-5fb28c3fbbe1328b140b38c4f6105fb2&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dr1n13000merged_data.csv%3Bfilename*%3Dutf-8%27%27r1n13000merged_data.csv&user_id=1028920560074189860&x-verify=1"
    ur80 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/255e146842a44945bf9b56c8cc1d8ca9.csv?auth_key=1735938330-c97f6ad336f34dddaeade84fad46a46a-0-cec6b204a5b34583f789a8442ded65c1&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dpseudotime_map.csv%3Bfilename*%3Dutf-8%27%27pseudotime_map.csv&user_id=1028920560074189860&x-verify=1"

    file_path78 = os.path.join(Nerveferroptosis_remove_R1_3_4_result_path, "r1n13000distance_matrix.mat") 
    file_path79 = os.path.join(Nerveferroptosis_remove_R1_3_4_result_path, "r1n13000merged_data.csv") 
    file_path80 = os.path.join(Nerveferroptosis_remove_R1_3_4_result_path, "pseudotime_map.csv") 
    
    urllib.request.urlretrieve(ur78, file_path78) 
    urllib.request.urlretrieve(ur79, file_path79)
    urllib.request.urlretrieve(ur80, file_path80)

    
    print("Successful of Reprogramming_Nerveferroptosis_remove_R1_3_4_result")
    
    
    
    #Nerveferroptosis_15_21_data
    
    ur81 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/80b105abf5254b7ca4eaddebc7ae1340.h5ad?auth_key=1735939244-e41fc487c1be4041b320323e0edb6a32-0-7c0534150088dbf8a4102876fb637764&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D2024.10.28%25E7%259A%258415-21%25E6%2595%25B0%25E6%258D%25AE.h5ad%3Bfilename*%3Dutf-8%27%272024.10.28%25E7%259A%258415-21%25E6%2595%25B0%25E6%258D%25AE.h5ad&user_id=1028920560074189860&x-verify=1"

    file_path81 = os.path.join(Nerveferroptosis_15_21_data_path, "Nerveferroptosis_15_21_data_path.h5ad") 
    
    urllib.request.urlretrieve(ur81, file_path81) 
    
    print("Successful of Nerveferroptosis_15_21_data")
    
    
    
    #Nerveferroptosis_15_21_result
    
    ur82 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/a78a9009812c401ab21fe65ec19f5d6b.mat?auth_key=1735939456-b35060927b9340e8b9ee15682f4871e9-0-411063850e49e53d7a9b0be674ea6ca9&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Ddistance_matrix.mat%3Bfilename*%3Dutf-8%27%27distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur83 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/4ae9dd52fe8b4d59826c61248d94db29.csv?auth_key=1735939481-c88dd47a9aa34feeaebb3467a2537fd6-0-8712e481383ace7329b7951b865c2f61&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_group.csv%3Bfilename*%3Dutf-8%27%27result_group.csv&user_id=1028920560074189860&x-verify=1"
    ur84 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/01ca80c960e3493b9b27f2306e3a58ab.csv?auth_key=1735939502-f30b212683904df89d3695bea03f8ebf-0-eff56ccca66f70c107e06f59740d7fc4&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dmerged_data.csv%3Bfilename*%3Dutf-8%27%27merged_data.csv&user_id=1028920560074189860&x-verify=1"
    ur85 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/c3b5a41c93074d0983d4968996df8c3e.csv?auth_key=1735939524-8ebbc22c687b4f878ea823939afb4a3f-0-2ae5a16cd8998dd80e49e0a6c83291ba&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dresult_group%2520-%25205.csv%3Bfilename*%3Dutf-8%27%27result_group%2520-%25205.csv&user_id=1028920560074189860&x-verify=1"

    file_path82 = os.path.join(Nerveferroptosis_15_21_result_path, "distance_matrix.mat") 
    file_path83 = os.path.join(Nerveferroptosis_15_21_result_path, "result_group.csv") 
    file_path84 = os.path.join(Nerveferroptosis_15_21_result_path, "merged_data.csv") 
    file_path85 = os.path.join(Nerveferroptosis_15_21_result_path, "result_group-5.csv") 
    
    urllib.request.urlretrieve(ur82, file_path82) 
    urllib.request.urlretrieve(ur83, file_path83)
    urllib.request.urlretrieve(ur84, file_path84)
    urllib.request.urlretrieve(ur85, file_path85)


    print("Successful of Nerveferroptosis_15_21_result")    
    
    #Nerveferroptosis_data
    
    ur86 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/5c86d3da437848189c45a4fa9a5a8166.h5seurat?auth_key=1735939739-89edce44656247bc81ff7679a15c57d7-0-112be5f6cbdaa3a9dd8899a76f18b851&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DGSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4_testAB.integrated.h5seurat%3Bfilename*%3Dutf-8%27%27GSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4_testAB.integrated.h5seurat&user_id=1028920560074189860&x-verify=1"
    ur87 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/2bfd551b451a43368a19c9a222f2d672.h5ad?auth_key=1735939767-030aa0af2aca4cddb7d61f42bbed1b13-0-84fe24b85a030e19220dbe25ba0fc00c&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3DGSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4_testAB.integrated.h5ad%3Bfilename*%3Dutf-8%27%27GSE232429deatd_%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4_testAB.integrated.h5ad&user_id=1028920560074189860&x-verify=1"

    file_path86 = os.path.join(Nerveferroptosis_data_path, "Nerveferroptosis_15_21_result_path.h5seurat") 
    file_path87 = os.path.join(Nerveferroptosis_data_path, "GSE232429deatd_粗糙过滤_testAB.integrated.h5ad") 
    
    urllib.request.urlretrieve(ur86, file_path86) 
    urllib.request.urlretrieve(ur87, file_path87)
    
    print("Successful of Nerveferroptosis_data")
    
    
    #Nerveferroptosis_result
    
    ur88 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/5c2154f5258f4de4b71c8d3a3839bc59.mat?auth_key=1735940068-8a3671803d2c431ebe8d557cb8c74ebb-0-ccacaa944d140f1070256e820bc8c7b8&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3Dworkend.mat%3Bfilename*%3Dutf-8%27%27workend.mat&user_id=1028920560074189860&x-verify=1"
    ur89 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/daea096f34364ca48e05e339af3552c7.mat?auth_key=1735940088-03e5f91d3337440da6b8f5367e98dbbe-0-89b463d051681f5342c857f41be1d4eb&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4r1n13000distance_matrix.mat%3Bfilename*%3Dutf-8%27%27%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4r1n13000distance_matrix.mat&user_id=1028920560074189860&x-verify=1"
    ur90 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/89c77cbc7f7e453982d62d8f3c5cb836.csv?auth_key=1735940110-d9d7c0954b664b6d816ab1db588df175-0-a34a8a8909772087904ca9366869d8ab&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4r1n13000merged_data.csv%3Bfilename*%3Dutf-8%27%27%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A4r1n13000merged_data.csv&user_id=1028920560074189860&x-verify=1"
    ur91 = "https://download-obs.cowcs.com/cowtransfer/cowtransfer/89860/f70484eafa384496aecffa33afe648f9.csv?auth_key=1735940129-3c74cb05765442688d9dca8efee0ca15-0-ef07d949f2fa7eab4caf55c698bf2663&biz_type=1&business_code=COW_TRANSFER&channel_code=COW_CN_WEB&response-content-disposition=attachment%3B%20filename%3D%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A41n13000_result.csv%3Bfilename*%3Dutf-8%27%27%25E7%25B2%2597%25E7%25B3%2599%25E8%25BF%2587%25E6%25BB%25A41n13000_result.csv&user_id=1028920560074189860&x-verify=1"

    file_path88 = os.path.join(Nerveferroptosis_result_path, "workend.mat") 
    file_path89 = os.path.join(Nerveferroptosis_result_path, "粗糙过滤r1n13000distance_matrix.mat") 
    file_path90 = os.path.join(Nerveferroptosis_result_path, "粗糙过滤r1n13000merged_data.csv") 
    file_path91 = os.path.join(Nerveferroptosis_result_path, "粗糙过滤1n13000_result.csv") 
    
    urllib.request.urlretrieve(ur88, file_path88) 
    urllib.request.urlretrieve(ur89, file_path89)
    urllib.request.urlretrieve(ur90, file_path90)
    urllib.request.urlretrieve(ur91, file_path91)
    
    print("Successful of Nerveferroptosis_result")

   