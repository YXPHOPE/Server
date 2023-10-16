import cv2
import numpy as np
from PIL import ImageGrab
import struct
from time import sleep,gmtime
HOST = '0.0.0.0'
PORT = 8088
i = 0
LF = []
BW = 128
BH = 24
BWidth = int(1920/BW)
BHeight = int(1080/BH)
print(0,end='')
sleep(2)
i1 = ImageGrab.grab()
i1.save('1.png')
Shape = (24,128,45,15,3)
Strides = (259200,45,5760,3,1)
LF = np.lib.stride_tricks.as_strided(np.asarray(i1,dtype = np.uint8),shape=Shape,strides=Strides)
# print(LF.size,LF.shape,LF[0][0].shape)

print(1,end='')
# LF.__abs__()
sleep(2)
print(2,end='')
def getFrame():
    global LF
    i2 = ImageGrab.grab()
    i2.save()
    cur = np.lib.stride_tricks.as_strided(np.asarray(i2,dtype = np.uint8),shape=Shape,strides=Strides)
    det = cur-LF
    LF = cur
    res = []
    i = 0
    # l = len(bimg)
    # 比较帧，竖向下x，横向右y
    for i in range(BH):
        for j in range(BW):
            if det[i][j].sum():res.append([i,j])
    if len(res)>255:
        # 发送完整帧，png压缩
        pass
    b = b''
    for i in res:
        b+=det[i[0]][i[1]].tobytes()
    return b
            
n = 0
fr = b''
while n<30:
    fr+=getFrame()
    sleep(0.04)
print(len(fr))

"""
|flag|blocks|h|w| 0|0|block......

a = [
    [[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18]],
    [[19,20,21],[22,23,24],[25,26,27],[28,29,30],[31,32,33],[34,35,36]],
    [[1,2,3],[4,4,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18]],
    [[19,20,21],[22,23,24],[25,26,27],[28,29,30],[31,32,33],[34,35,36]]]
print(np.lib.stride_tricks.as_strided(np.asarray(a,dtype = np.uint8),shape=(2,3,2,2,3)))

# 创建一个示例的RGB图像矩阵，假设形状为(480, 640, 3)
image = np.random.randint(0, 256, size=(48, 64, 3), dtype=np.uint8)

# 定义块的大小
block_size = (12, 16, 3)  # 每个块的大小为12x16像素，3表示RGB通道

# 计算图像矩阵的步幅
image_shape = image.shape
block_shape = block_size
strides = image.strides

# 使用np.lib.stride_tricks.as_strided创建视图以获取图像块
blocks = np.lib.stride_tricks.as_strided(image, shape=(
    4,
    4,
    block_shape[0],
    block_shape[1],
    block_shape[2]
), strides=(
    strides[0] * block_shape[0], # 192/12 1920*3/
    strides[1] * block_shape[1],
    strides[0],
    strides[1],
    strides[2]
))
print(image)
print(blocks)
"""