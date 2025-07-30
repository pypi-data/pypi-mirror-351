# AIToolkit Camera - 简易摄像头工具包

![版本](https://img.shields.io/badge/版本-0.2.2-blue)
![Python 版本](https://img.shields.io/badge/Python-3.7+-brightgreen)
![许可证](https://img.shields.io/badge/许可证-MIT-green)

`aitoolkit_cam` 是一个针对Python的简单易用的摄像头工具包，让摄像头开发变得轻松简单。无论您是教育工作者还是学生，都可以通过几行代码轻松实现摄像头功能。

## 核心特点

- 🌟 **简单易用**：几行代码即可启动摄像头和网页服务
- 🌐 **网页实时查看**：支持通过浏览器远程查看摄像头画面
- 🔄 **迭代器接口**：兼容Python迭代器，可在for循环中使用
- 🖼️ **图像处理**：支持在将帧发送到Web流之前进行处理
- 🔌 **资源管理**：自动释放摄像头资源
- 🛠️ **帧控制**：应用可以精确控制哪些帧被发送到Web流

## 安装方法

```bash
pip install aitoolkit-cam
```

## 基础用法

### 简单示例

```python
from aitoolkit_cam import Camera
import time
import cv2 # 用于在帧上绘制信息

# 创建摄像头对象
cam = Camera(width=640, height=480)
cam.web_enabled = True  # 启用网页服务

# 启动摄像头
cam.start()

# 获取访问地址 (增加一些延时和重试，因为Web服务启动可能需要一点时间)
url = None
for _ in range(5):
    url = cam.get_web_url()
    if url:
        break
    time.sleep(0.5)

print(f"访问地址: {url if url else 'Web服务启动失败或URL不可用'}")
print("请在浏览器中访问上述地址 (如果可用)")
print("按Ctrl+C退出程序...")

try:
    # 循环获取视频帧
    for frame_count, frame in enumerate(cam):
        if frame is None:
            time.sleep(0.01)
            continue

        # 示例：在帧上添加一些文本信息
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"Time: {current_time_str}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Frame: {frame_count}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 更新要在Web流上显示的帧
        cam.update_web_stream_frame(frame)
        
        # 如果需要在本地也显示，可以这样做:
        # if cam.cv_show(frame, mode="cv2", wait_key=1):
        #     break

        time.sleep(0.01) # 控制循环速率

except KeyboardInterrupt:
    print("\n用户中断，正在退出...")
finally:
    # 释放资源
    print("正在停止摄像头...")
    cam.stop()
    print("程序已退出")
```

### Jupyter Notebook中使用

现在，在Jupyter Notebook中使用`aitoolkit_cam`变得更加简单。库内置了对Notebook环境的优化支持，您无需编写额外的线程和循环管理代码。

```python
from aitoolkit_cam import Camera
import time

# 全局摄像头实例变量 (可选，但方便在不同单元格操作)
cam_notebook_instance = None

def run_camera_in_notebook():
    global cam_notebook_instance
    
    # 如果已有实例在运行，先停止它
    if cam_notebook_instance and cam_notebook_instance.is_running:
        print("发现正在运行的旧摄像头实例，正在停止它...")
        cam_notebook_instance.stop_notebook_mode()
        cam_notebook_instance = None
        time.sleep(1) # 给点时间完全停止

    # 创建并启动摄像头 Notebook 模式
    # 您可以在这里指定分辨率、FPS、端口等参数
    # loop_interval 控制内部帧抓取和Web更新的频率
    cam_notebook_instance = Camera() # 使用默认参数，或 Camera(width=320, height=240, port=8091) 等
    
    print("正在以Notebook模式启动摄像头和网页服务...")
    start_time = time.time()
    
    # start_notebook_mode 会自动处理摄像头启动、Web服务启动以及后台帧的拉取和Web更新
    # 参数可以包括: width, height, fps, port, loop_interval
    url = cam_notebook_instance.start_notebook_mode(width=320, height=240, fps=20, loop_interval=0.05)
    
    elapsed_time = time.time() - start_time
    print(f"启动耗时: {elapsed_time:.2f}秒")

    if url:
        print(f"摄像头已在后台运行，请在浏览器中访问: {url}")
        print("图像会自动推送到此URL。")
    else:
        print("启动Notebook模式失败，或未能获取到Web流地址。请检查日志。")
        # 如果启动失败，cam_notebook_instance.is_running 可能已经是 False
        # 或者 _notebook_mode_thread 可能没有启动
        if cam_notebook_instance and cam_notebook_instance.is_running:
             cam_notebook_instance.stop() # 尝试清理
        cam_notebook_instance = None # 清理实例
    
    return url

def shutdown_camera_in_notebook():
    global cam_notebook_instance
    if cam_notebook_instance and cam_notebook_instance.is_running:
        print("正在停止Notebook模式下的摄像头...")
        cam_notebook_instance.stop_notebook_mode() # 这个方法会处理所有相关的停止操作
        print("Notebook模式摄像头已停止。")
        cam_notebook_instance = None # 清理实例
    elif cam_notebook_instance:
        print("摄像头实例存在但未在运行。正在尝试清理...")
        cam_notebook_instance.stop() # 尝试通用停止
        cam_notebook_instance = None
    else:
        print("没有正在运行的Notebook摄像头实例可停止。")
    return "Notebook摄像头已停止并清理。"

# --- Jupyter Notebook 使用方法 ---
#
# 1. 在一个单元格中运行:
#    url = run_camera_in_notebook()
#    if url: print(f"Web流地址: {url}")
#
# 2. 摄像头将在后台运行，自动将帧推送到Web流。
#    您可以在浏览器中打开返回的URL查看。
#
# 3. 您可以执行其他单元格，进行数据分析、模型推理等，
#    如果需要当前摄像头帧进行处理，可以像这样获取 (但通常不直接在Notebook模式下这么做，因为它已自动推流):
#    # if cam_notebook_instance and cam_notebook_instance.is_running:
#    #     ret, frame = cam_notebook_instance.read(timeout=0.1) # 从内部队列读取
#    #     if ret and frame is not None:
#    #         # 在这里处理 frame
#    #         # cv2.imshow("Frame for processing", frame) # 如果有GUI环境
#    #         # cv2.waitKey(1)
#    #         pass 
#
# 4. 当您完成操作后，在另一个单元格中运行:
#    shutdown_camera_in_notebook()
#
# --- 注意事项 ---
# - `start_notebook_mode()` 会启用Web服务。帧将自动从摄像头读取并推送到Web流。
# - `loop_interval` 参数控制后台线程抓取和更新Web帧的频率。
# - `stop_notebook_mode()` 会妥善停止后台线程、摄像头硬件和Web服务。
# - 如果在 `start_notebook_mode` 时传入 `width`, `height`, `fps`, `port`，它们会覆盖 `Camera` 初始化时的设置。

## 高级用法

### 使用反向代理解决端口变化问题

当需要在前端页面或其他应用中嵌入摄像头画面时，可以使用反向代理保持URL稳定：

#### 1. 安装Nginx

```bash
# 在Ubuntu/Debian上
sudo apt install nginx

# 在CentOS/RHEL上
sudo yum install nginx

# 在Windows上可以下载安装包
# http://nginx.org/en/download.html
```

#### 2. 配置Nginx反向代理

创建或编辑Nginx配置文件（例如`/etc/nginx/conf.d/camera.conf`）：

```nginx
server {
    listen 80; # 或其他您想使用的前端端口
    server_name your_server_ip_or_domain;  # 修改为您的服务器名称或IP

    location /livecamera/ { # 定义一个路径，例如 /livecamera/
        proxy_pass http://localhost:8090/; # 假设aitoolkit_cam运行在默认的8090端口
                                         # 如果您在Python中更改了端口，这里也要相应更改
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持 (如果WebGear/Starlette内部使用了WebSocket，则需要)
        # 对于MJPEG流通常不是必需的，但保留也没坏处
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置 (根据需要调整)
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s; # 对于长连接的流，可能需要更长
        proxy_send_timeout 60s;
        # 如果流路径不是根路径，可能需要rewrite
        # proxy_buffering off; # 对于流媒体，关闭缓冲可能更好
    }
}
```
**注意**: 上述Nginx配置中的`proxy_pass http://localhost:8090/;`，这里的`8090`是`aitoolkit_cam`的默认端口。如果您在Python代码中通过`cam.port = XXXX`或`Camera(port=XXXX)`设置了其他端口，请确保Nginx配置中的端口与之一致。

#### 3. 启动摄像头服务和Nginx

```bash
# 重启Nginx应用配置
sudo systemctl restart nginx # 或者 nginx -s reload

# 启动摄像头服务（例如，使用默认的8090端口）
# python -c "
from aitoolkit_cam import Camera
import time

cam = Camera() # 默认端口 8090
cam.web_enabled = True
# cam.port = 8000 # 如果要修改端口，在这里设置，并确保Nginx配置一致

if cam.start():
    url = None
    for _ in range(5): # 重试获取URL
        url = cam.get_web_url()
        if url: break
        time.sleep(0.2)
    print(f'摄像头服务已启动: {url if url else "URL不可用"}')
    print('按Ctrl+C或关闭此窗口来退出...')
    try:
        while True: # 保持Python脚本运行，直到手动停止
            # 在这个循环里，我们只是让主摄像头读取和Web服务运行
            # 实际的帧更新是在Web流的内部生产者中处理的
            # 如果想从这里控制发送到web的帧，可以像其他示例一样迭代cam并调用update_web_stream_frame
            frame_obj = cam.read(timeout=0.1) # 从原始队列读一帧，但不一定做什么
            if frame_obj[0]: # 如果成功读到
                 cam.update_web_stream_frame(frame_obj[1]) # 将原始帧更新到web
            else: # 如果没读到或超时
                 pass # 可以选择发送一个特定的"无信号"帧或什么都不做

            time.sleep(0.03) # 大约30fps
    except KeyboardInterrupt:
        print("\n正在停止摄像头...")
    finally:
        cam.stop()
        print("摄像头服务已停止。")
# "
```

现在可以通过 `http://your_server_ip_or_domain/livecamera/` (或者您在Nginx中配置的`location`) 访问摄像头，这个URL是稳定的。WebGearStream内部的`/video`路径会被Nginx代理。例如，如果WebGear的流地址是 `http://localhost:8090/video`，那么通过Nginx访问的完整流地址将是 `http://your_server_ip_or_domain/livecamera/video`。

### 在前端页面中嵌入摄像头画面

使用反向代理后，可以在HTML页面中嵌入摄像头画面：

```html
<!DOCTYPE html>
<html>
<head>
    <title>摄像头画面</title>
    <style>
        .camera-container {
            width: 640px; /* 或您期望的显示宽度 */
            height: 480px; /* 或您期望的显示高度 */
            margin: 0 auto;
            border: 1px solid #ccc;
            overflow: hidden;
            background-color: #333; /* 加个背景色，如果图像加载慢 */
        }
        .camera-feed {
            width: 100%;
            height: 100%;
            object-fit: contain; /* 'contain' 保持宽高比, 'cover' 填满容器可能裁剪 */
        }
    </style>
</head>
<body>
    <h1>摄像头实时画面</h1>
    <div class="camera-container">
        <!-- 假设Nginx配置的location是 /livecamera/ 并且WebGear的流路径是 /video -->
        <img src="http://your_server_ip_or_domain/livecamera/video" class="camera-feed" alt="摄像头画面加载中...">
    </div>

    <script>
        // 可选：如果图像加载失败，可以显示错误信息
        const img = document.querySelector('.camera-feed');
        img.onerror = function() {
            this.alt = '摄像头画面加载失败。请检查服务是否运行或URL是否正确。';
            // 可以在这里尝试重新加载或显示更详细的错误
        };
    </script>
</body>
</html>
```

## 进阶功能

### 图像处理

```python
from aitoolkit_cam import Camera
# 假设您有一个 apply_effect 函数，例如:
# def apply_effect(frame, effect_name):
#     if effect_name == "grayscale":
#         return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     # 其他效果...
#     return frame
import cv2 # for cvtColor if apply_effect uses it

# 创建摄像头对象
cam = Camera()
cam.web_enabled = True
cam.start()

url = cam.get_web_url() # 同样，最好加重试
print(f"访问地址: {url}")

try:
    for frame in cam:
        if frame is None: continue
        # 应用灰度效果 (示例)
        # processed = apply_effect(frame, "grayscale") 
        # 注意: 如果apply_effect返回灰度图，而Web流期望BGR，可能需要转换
        # WebGearStream的默认生产者通常处理BGR帧并编码为JPEG
        
        # 简单的处理：转为灰度图，再转回BGR给Web流（JPEG通常是彩色的）
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_for_web = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
        
        # 更新Web流帧
        cam.update_web_stream_frame(processed_for_web)

        # 如果想在本地也看到灰度图
        # cv2.imshow("Grayscale Local", gray_frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        time.sleep(0.01)
except KeyboardInterrupt:
    print("用户中断...")
finally:
    cam.stop()
```

### 使用上下文管理器

```python
from aitoolkit_cam import Camera
import time
import cv2 # 用于绘制

# 使用with语句自动管理资源
with Camera(width=320, height=240) as cam:
    cam.web_enabled = True
    cam.start() # start() 应该在with内部显式调用，如果web_enabled=True
    
    url = None
    for _ in range(5): # 重试获取URL
        url = cam.get_web_url()
        if url: break
        time.sleep(0.2)
    print(f"访问地址: {url if url else 'URL不可用'}")
    
    # 处理约5秒的帧后退出 (假设摄像头约20-30fps)
    max_frames = 150 
    count = 0
    try:
        for frame in cam:
            if frame is None: continue

            # 示例处理
            cv2.putText(frame, f"Count: {count}", (5,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

            # 更新Web流帧
            cam.update_web_stream_frame(frame)
            
            count += 1
            if count >= max_frames:
                print(f"已处理 {max_frames} 帧, 退出循环。")
                break
            time.sleep(0.01) # 控制循环速率
    except KeyboardInterrupt:
        print("用户在with块内中断...")

# with语句结束后自动调用cam.stop()释放资源
print("已退出with语句块，摄像头应已停止。")
```

## 开发者信息

- 作者：[AI校પ્อัน Toolkit]
- 版本：0.2.3 (假设因这些修改而更新)
- 许可证：MIT

## 贡献

欢迎提交问题和贡献代码以改进这个项目！ 