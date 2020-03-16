# 主函数Preprocess.py
# 功能：将逻辑分析仪采集得到的.csv数据转化为图像

# 涉及到的子函数：

# 1、GetSpiData：提取出.csv文件中的SPI总线数据
# 2、GetFlashData：提取出SPI总线数据中写入Flash芯片的数据
# 3、GetRawData：将Flash芯片中的数据按节点提取出来
# 4、Transpic：将节点补长度并转化为图像

# 使用到的变量：

# 路径变量：
# Data_dir：逻辑分析仪导出的.csv文件地址
# Raw_dir：预处理后所有类型节点图像输出地址
# InodeData_dir：预处理后inode类型节点图像输出地址
# InodeContent_dir：预处理后有内容的inode类型节点的图像输出地址


# 关键中间过程变量：
# CsvData：.csv中的文件内容
# SpiData：SPI总线数据
# FlashData：写入Flash芯片的数据
# DirentData：dirent类型节点数据
# InodeData：inode类型节点数据
# MaxLengthData：补至最大长度后的节点数据
# PicData：转化生成的图像数据
#


import os
import csv
from PIL import Image
import numpy as np




# CalculateStr：计算小端字符串代表的值
def CalculateStr(str):
    result = 0
    i = 0
    maxlength = len(str)
    while i < maxlength:
        result += int(str[i],16) * pow(256, i)
        i += 1
    return result


# GetSpiData：提取出.csv文件中的SPI总线数据
def GetSpiData(FILE):
    f = open(FILE)
    CsvData = f.read()
    #CsvData = pd.read_csv(FILE)
    Spi = []
    index = 0
    maxlength = len(CsvData) - 5

    count = 0
    while index < maxlength:
        '''
        if CsvData[index:index+4] == 'MISO':
            index += 9
            while CsvData[index:index+2] != '0x':
                index += 1
            Spi.append(CsvData[index+2:index+4])
            index += 47
        else:
            index += 1
        '''
        ##
        if CsvData[index:index + 3] == '(0x':
            count += 1
            if count % 2 == 0:
                index += 3
                Spi.append(CsvData[index:index+2])
            else:
                index += 9
        else:
            index += 1
    print('GetSpiData Success')
    #print(Spi)
    return Spi


# GetFlashData：提取出SPI总线数据中写入Flash芯片的数据
def GetFlashData(Spi):
    Flash = []
    index = 0
    maxlength = len(Spi) - 4
    while index < maxlength:
        if Spi[index:index+4] == ['06', '05', '00', '02']:
        #if (Spi[index:index + 4] == ['06', '05', '00', '02']) | (Spi[index:index + 4] == ['06', '04', '00', '02']):
            index += 7
            while (Spi[index:index+3] != ['04', '05', '00']) & (Spi[index:index+3] != ['05', '00', '05']) & (Spi[index:index+3] != ['05', '00', '06']):
                Flash.append(Spi[index])
                #print(index)
                index += 1
                if index == maxlength:
                    Flash.append(Spi[index])
                    Flash.append(Spi[index + 1])
                    Flash.append(Spi[index + 2])
                    #print(index)
                    break
        else:
            index += 1
    print('GetFlashData Success')
    #print(Flash)
    return Flash


# Transpic：将节点补长度并转化为图像
def Transpic(raw, dir, name):
    MAXLENGTH = 16 * 16
    MAX_i = 65  # 最大行数
    MAX_j = 65  # 最大列数

    result = np.zeros((MAX_i,MAX_j,3))
    for i in range(MAX_i):
        for j in range(MAX_j):
            if (i * MAX_i + j < len(raw)):
                result[i][j][0] = int(raw[i * MAX_i + j], 16)
                result[i][j][1] = int(raw[i * MAX_i + j], 16)
                result[i][j][2] = int(raw[i * MAX_i + j], 16)

    im = Image.fromarray(result.astype(np.uint8))
    im.save(dir + '\\' + name)
    return result


def Transcsv(jffs2_raw_inode, csv_file):
    MAXLENGTH = 65 * 65
    with open(csv_file, 'a+', newline='') as f:
        csv_write = csv.writer(f)
        destination = []
        for item in jffs2_raw_inode:
            destination.append(int(item, 16))
        destination = list([ ] + destination + [0] * (MAXLENGTH - len(destination)))
        csv_write.writerow(destination)


# GetRawData：将Flash芯片中的数据按节点提取出来
def GetRawData(Flash, save_dir, csv_file, work_mode1=0, work_mode2=0, init_number=0):
    index = 0
    dirent_num = 0
    inode_num = 0
    picversion = init_number
    maxlength = len(Flash) - 4
    while index < maxlength:
        if Flash[index:index + 4] == ['85', '19', '01', 'E0']:
            dirent_num += 1

            nodetype = Flash[index:index + 4]
            index += 4
            totlen = Flash[index:index + 4]
            index += 4
            hdr_crc = Flash[index:index + 4]
            index += 4
            pio = Flash[index:index + 4]
            index += 4
            version = Flash[index:index + 4]
            index += 4
            ino = Flash[index:index + 4]
            index += 4
            mctime = Flash[index:index + 4]
            index += 4
            unuseds = Flash[index:index + 4]
            index += 4
            node_crc = Flash[index:index + 4]
            index += 4
            name_crc = Flash[index:index + 4]
            index += 4
            name_length = CalculateStr(totlen) - 40
            name = Flash[index:index + name_length]
            index += name_length
            jffs2_raw_dirent = nodetype + totlen + hdr_crc + pio + version + ino + mctime + unuseds + node_crc + name_crc + name

            print('Found a jffs2_raw_dirent', dirent_num, ', length:', len(jffs2_raw_dirent))
            print(jffs2_raw_dirent)

        elif Flash[index:index + 4] == ['85', '19', '02', 'E0']:
            inode_num += 1
            nodetype = Flash[index:index + 4]
            index += 4
            totlen = Flash[index:index + 4]
            index += 4
            hdr_crc = Flash[index:index + 4]
            index += 4
            ino = Flash[index:index + 4]
            index += 4
            version = Flash[index:index + 4]
            index += 4
            mode = Flash[index:index + 4]
            index += 4
            ugid = Flash[index:index + 4]
            index += 4
            isize = Flash[index:index + 4]
            index += 4
            atime = Flash[index:index + 4]
            index += 4
            mtime = Flash[index:index + 4]
            index += 4
            ctime = Flash[index:index + 4]
            index += 4
            offset = Flash[index:index + 4]
            index += 4
            csize = Flash[index:index + 4]
            index += 4
            dsize = Flash[index:index + 4]
            index += 4
            comprs = Flash[index:index + 4]
            index += 4
            data_crc = Flash[index:index + 4]
            index += 4
            node_crc = Flash[index:index + 4]
            index += 4
            data_length = CalculateStr(totlen) - 68
            data = Flash[index:index + data_length]
            index += data_length
            jffs2_raw_inode = nodetype + totlen + hdr_crc + ino + version + mode + ugid + isize + atime + mtime + ctime + offset + csize + dsize + comprs + data_crc + node_crc + data

            print('Found a jffs2_raw_inode',inode_num, ', length:', len(jffs2_raw_inode))
            print(jffs2_raw_inode)

            if data_length !=  0:
                picversion += 1
                print('Found a jffs2_raw_inode', inode_num, ', length:', len(jffs2_raw_inode))
                print(jffs2_raw_inode)
                if work_mode1:
                    Transpic(jffs2_raw_inode, save_dir, str(picversion)+'.jpg')
                if work_mode2:
                    Transcsv(jffs2_raw_inode, csv_file)
        else:
            index += 1
    return picversion


# 对单个file处理
def Preprocess(file, init_number, path, csv_file, work_mode1=0, work_mode2=0):
    SpiData = GetSpiData(file)  # 提取出.csv文件中的SPI总线数据
    FlashData = GetFlashData(SpiData)  # 提取出SPI总线数据中写入Flash芯片的数据
    init_number = GetRawData(FlashData, path, csv_file, work_mode1, work_mode2, init_number)  # GetRawData：将Flash芯片中的数据按节点提取出来

    print('COMPLETE!')
    return init_number


# 主函数
def work():
    path = os.getcwd()
    init_number = 0

    Data_dir = path + "\\Data" # 数据路径

    Raw_dir = path + "\\Raw"
    InodeData_dir = path + "\\InodeData"
    InodeContent_dir = path + "\\InodeContent"

    Test_dir = path + "\\Test" # 图像输出目标路径
    csv_file = Test_dir + "\\test.csv" # 节点输出目标csv

    fileList = os.listdir(Data_dir)
    for file in fileList:
        print(file)
        init_number = Preprocess(Data_dir+"\\"+file, init_number, Test_dir, csv_file, work_mode1=1, work_mode2=1)


if __name__ == '__main__':
    work()
    #Preprocess("C:\\Users\\tonym\\Desktop\\Preprocess\\test_data\\Data.csv", 0, 0, 0, work_mode1=0, work_mode2=0)


