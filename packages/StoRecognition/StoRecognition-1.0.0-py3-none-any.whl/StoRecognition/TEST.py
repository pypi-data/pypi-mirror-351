import os
def batch_images():
    source_dir = r"D:\我的文件\sto项目\pic\ori\Supplementary"
    target_dir = r"D:\我的文件\sto项目\pic\ori\Supplementary\result"
    for root, dirs, files in os.walk(source_dir):
        # 构建目标目录的对应路径
        relative_path = os.path.relpath(root, source_dir)
        target_sub_dir = os.path.join(target_dir, relative_path)

        if(len(files)!=0):
            # 如果目标子目录不存在，则创建它
            if not os.path.exists(target_sub_dir):
                os.makedirs(target_sub_dir)

        # 遍历当前目录下的文件
        for file in files:

            # 检查文件是否为图片文件
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                source_file_path = os.path.join(root, file)
                target_file_path = os.path.join(target_sub_dir, file)

                try:
                    # image = cv_imread(path)
                    # self.batch_frame_process(image)
                    # self.batch_toggle_saveFile(target_file_path)
                    # self.saved_images = []
                    print("123")
                except Exception as e:
                    print(f"Error copying {source_file_path}: {e}")

if __name__ == '__main__':  # 确保该模块被直接运行时才执行以下代码
    batch_images()