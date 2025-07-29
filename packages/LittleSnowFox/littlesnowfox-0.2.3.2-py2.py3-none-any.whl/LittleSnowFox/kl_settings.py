#初始化函数，将kailin转至工作目录。如果此前初始化过，那么在再次运行def kl_initialize(0)时，
#则拒绝初始化，避免套娃。运行def kl_initialize(1)时，强制重新初始化。

print('kailin has been initialized')
def kl_initialize(reset):

    import os
    import LittleSnowFox
    global empty_key
    global parent_directory_origin
    
    
    #初始化的具体内容
    def first_time():
        global empty_key
        global parent_directory_origin
        empty_key = 0
        print('set empty_key = ' + str(empty_key))

        # 获取 kailin 模块所在的目录
        kailin_directory = os.path.dirname(os.path.abspath(LittleSnowFox.__file__))
        print(f"The directory of the kailin module is: {kailin_directory}")
        parent_directory_origin = kailin_directory
        print('work address = ' + str(parent_directory_origin))
        print()
        print()
        print('Note--If you want use your data, please put your data.h5ad in: ' + parent_directory_origin + '\database')
        print()
        print()



        

    #如果此前初始化过，则拒绝初始化，避免套娃
    if 'empty_key' in locals() or 'empty_key' in globals():
        print("You have initialized before, the current parameter is:")
        #print('empty_key = ' + str(empty_key))
        print('work address = ' + str(parent_directory_origin))
        print()
        print()
        print('Note--If you want use your data, please put your data.h5ad in: ' + parent_directory_origin + '\database')
        print()
        print()

        #重设模式，初始化参数重设到当前工作区
        if reset == 1:
            print("reset mode")
            first_time()

    #没有初始化过，进行初始化
    else:
        print("empty_key does not exist")
        first_time()

    return empty_key
    return parent_directory_origin

