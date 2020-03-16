1、所有文件存放于同一路径
2、zip文件夹存放测试用数据和输出路径
3、函数Preprocess(file, init_number, path, csv_file, work_mode1=0, work_mode2=0)：
  file为待处理文件
  init_number标志生成的第几幅图，用于编号
  work_mode1 = 1时，将有内容的inode节点转为图像输出到路径path下
  work_mode2 = 1时，将有内容的inode节点补充到目标csv_file中
