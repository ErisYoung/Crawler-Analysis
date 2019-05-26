import os

path = os.path.join(os.getcwd(), 'imgs')

def down_to_sub(path):
    os.chdir(path)
    for i in os.listdir(path):
        # 使用绝对路径
        if os.path.isfile(os.path.join(path,i)):
            jpg_path=os.path.join(path,i)
            # 需要先进入该目录
            os.rename(jpg_path,jpg_path+".jpg")
        else:
            next_path = os.path.join(path, i)
            # print("next in " + next_path)
            down_to_sub(next_path)

down_to_sub(path)

