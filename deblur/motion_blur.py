import numpy as np
import cv2
import matplotlib.pyplot as plt


# 创建一个强烈的运动模糊卷积核
def strong_motion_blur_kernel(size, angle):
    # 初始化一个空的卷积核
    kernel = np.zeros((size, size))

    # 计算角度的弧度
    angle = angle * np.pi / 180

    # 填充卷积核的非零元素
    center = (size - 1) // 2
    for i in range(size):
        for j in range(size):
            # 使用公式计算每个位置的值
            x = i - center
            y = j - center
            # 根据角度决定模糊方向
            if np.abs(x * np.cos(angle) + y * np.sin(angle)) <= 0.5:
                kernel[i, j] = 1.0

    # 归一化卷积核
    kernel = kernel / kernel.sum()

    return kernel


# 加载图像
image = cv2.imread('demo.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 设置更大的模糊核尺寸，增加模糊强度
size = 20  # 增加模糊核的大小
angle = 45  # 可以尝试其他角度，增加多样性

# 获取更强烈的运动模糊卷积核
kernel = strong_motion_blur_kernel(size, angle)

# 使用卷积核对图像进行模糊
blurred_image = cv2.filter2D(image, -1, kernel)[..., ::-1]
cv2.imwrite("blurred/1.png", blurred_image)

# # 显示原始图像与模糊后的图像
# plt.figure(figsize=(10, 5))
# plt.subplot(1, 2, 1)
# plt.imshow(image)
# plt.title("Original Image")
#
# plt.subplot(1, 2, 2)
# plt.imshow(blurred_image)
# plt.title("Strong Motion Blurred Image")
#
# # plt.show()
# plt.savefig("blurred/1.png")
