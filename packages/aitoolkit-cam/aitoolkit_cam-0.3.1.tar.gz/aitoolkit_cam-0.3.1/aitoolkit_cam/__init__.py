"""
AIToolkit Camera - 简单易用的摄像头工具包
===========================================

提供本地显示和网页显示功能，支持图像处理

此包提供了使用OpenCV的摄像头工具，它具有以下特点：
1. 简单的API，易于使用
2. 支持本地窗口显示和网页浏览器显示
3. 提供多种图像处理效果
4. 兼容迭代器协议，可用于for循环
5. 自动处理摄像头连接和断开

快速示例:
```python
from aitoolkit_cam import Camera

# 创建摄像头对象
cam = Camera(0)

# 启动网页服务器
url = cam.start()
print(f"请访问: {url}")

# 在网页模式下显示
for frame in cam:
    # 可以进行额外的处理
    pass

try:
    cam.wait_for_exit()
except KeyboardInterrupt:
    pass

# 释放资源
cam.stop()
```
"""

# 版本信息
__version__ = '0.3.1'
__author__ = "aitoolkit_cam"

# 导入主要类和函数
from .camera import Camera
from .processor import Processor, ProcessedCamera, apply_effect
from .simple_web_stream import SimpleWebStream

# 导出的公共接口
__all__ = [
    'Camera',
    'Processor', 
    'ProcessedCamera',
    'apply_effect',
    'SimpleWebStream',
    '__version__',
    '__author__'
]

# 兼容性函数
def cv_show(frame, mode="cv2", wait_key=1):
    """
    全局图像显示函数（兼容性函数）
    
    参数:
        frame: 图像帧
        mode: 显示模式，仅支持"cv2"
        wait_key: cv2.waitKey等待时间
    
    返回:
        bool: 是否按下'q'键
    """
    if mode == "cv2":
        import cv2
        cv2.imshow('AIToolkit Camera', frame)
        key = cv2.waitKey(wait_key) & 0xFF
        return key == ord('q')
    else:
        print("警告: cv_show全局函数仅支持cv2模式，Web模式请使用Camera实例的cv_show方法")
        return False 