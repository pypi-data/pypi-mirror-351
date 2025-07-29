"""
Camera 模块 - 提供简洁的摄像头接口
"""
import threading
import time
import cv2
import asyncio
import numpy as np
import logging
import sys
import queue  # Added for queue.Queue
from .simple_web_stream import SimpleWebStream

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("aitoolkit_cam")

# Sentinel object to signal the end of the queue
_QUEUE_SENTINEL = object()

class _CameraReaderThread(threading.Thread):
    """
    专用线程，负责从摄像头硬件读取帧并将其放入队列。
    """
    def __init__(self, source, width, height, fps, raw_frame_queue, initialized_event, stop_event, target_fps):
        super().__init__(daemon=True)
        self.name = "_CameraReaderThread"
        self.source = source
        self.target_width = width
        self.target_height = height
        self.target_fps_setting = fps # FPS setting for camera
        self.raw_frame_queue = raw_frame_queue # Renamed
        self.initialized_event = initialized_event
        self.stop_event = stop_event
        self.cap = None
        
        # Actual FPS for frame reading loop
        self.actual_read_fps = target_fps if target_fps is not None else 30  # Default to 30 if not specified
        self.frame_interval = 1.0 / self.actual_read_fps if self.actual_read_fps > 0 else 0

    def run(self):
        try:
            logger.info(f"[{self.name}] Initializing camera source: {self.source}...")
            if sys.platform.startswith('win'):
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(self.source)

            if not self.cap.isOpened():
                logger.error(f"[{self.name}] Failed to open video source: {self.source}")
                self.initialized_event.set() # Signal completion (even if failed)
                return

            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if self.target_width and self.target_height:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
            if self.target_fps_setting is not None:
                self.cap.set(cv2.CAP_PROP_FPS, self.target_fps_setting)

            # Pre-read some frames
            for _ in range(5):
                if not self.cap.isOpened() or self.stop_event.is_set(): break
                self.cap.read()
                time.sleep(0.05)
            
            if not self.cap.isOpened(): # Check again after pre-read
                 logger.error(f"[{self.name}] Camera became unavailable after pre-read: {self.source}")
                 self.initialized_event.set()
                 return

            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps_val = self.cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"[{self.name}] Camera configured to: {actual_width}x{actual_height} @ {actual_fps_val}fps (Target read FPS: {self.actual_read_fps})")
            
            self.initialized_event.set() # Signal that initialization is complete
            
            last_frame_read_time = time.time()

            while not self.stop_event.is_set():
                current_time = time.time()
                if self.frame_interval > 0 and (current_time - last_frame_read_time < self.frame_interval):
                    sleep_time = self.frame_interval - (current_time - last_frame_read_time)
                    if sleep_time > 0.001: # Only sleep if meaningful
                        time.sleep(sleep_time * 0.8) # Sleep a bit less to catch up if needed
                    continue # Re-check stop event and time

                ret, frame = self.cap.read()
                last_frame_read_time = time.time()

                if not ret:
                    logger.warning(f"[{self.name}] Failed to read frame from source.")
                    # Wait a bit before retrying or breaking
                    time.sleep(0.1)
                    if not self.cap.isOpened(): # If camera closed itself
                        logger.error(f"[{self.name}] Camera disconnected.")
                        break
                    continue
                
                try:
                    # Put frame in queue, block if full (provides backpressure)
                    self.raw_frame_queue.put(frame, timeout=1.0) 
                except queue.Full:
                    logger.warning(f"[{self.name}] Raw frame queue is full. Dropping frame.")
                    # Optionally, clear older frames:
                    # try: self.raw_frame_queue.get_nowait() except queue.Empty: pass
                except Exception as e:
                    logger.error(f"[{self.name}] Error putting frame to raw_frame_queue: {e}")
                    break


        except Exception as e:
            logger.error(f"[{self.name}] Error in camera reader thread: {e}", exc_info=True)
            self.initialized_event.set() # Ensure main thread is not blocked if init fails here
        finally:
            if self.cap:
                self.cap.release()
            self.raw_frame_queue.put(_QUEUE_SENTINEL) # Signal consumers that reading has stopped
            logger.info(f"[{self.name}] Camera reader thread stopped.")


class Camera:
    """摄像头类，实现迭代器接口和显示功能"""

    @staticmethod
    def find_available_cameras(max_test=10, timeout=2.0):
        """
        检测系统中可用的摄像头
        
        参数:
            max_test: 最大测试的摄像头索引数量
            timeout: 每个摄像头的测试超时时间(秒)
        
        返回:
            list: 可用的摄像头索引列表
        """
        available_cameras = []
        logger.info(f"正在检测可用摄像头 (测试索引 0-{max_test-1})...")
        
        for i in range(max_test):
            cap = None
            try:
                # 在Windows上使用DSHOW后端，其他平台使用默认
                if sys.platform.startswith('win'):
                    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                else:
                    cap = cv2.VideoCapture(i)
                
                # 设置较短的超时时间
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # 尝试读取一帧来验证摄像头是否真正可用
                if cap.isOpened():
                    # 设置一个较小的分辨率来加快测试
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                    
                    # 尝试读取几帧
                    success_count = 0
                    for _ in range(3):  # 尝试读取3帧
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            success_count += 1
                        time.sleep(0.1)  # 短暂等待
                    
                    if success_count >= 2:  # 至少成功读取2帧
                        available_cameras.append(i)
                        logger.info(f"检测到可用摄像头: 索引 {i}")
                    else:
                        logger.debug(f"摄像头索引 {i} 无法稳定读取帧")
                else:
                    logger.debug(f"摄像头索引 {i} 无法打开")
                    
            except Exception as e:
                logger.debug(f"测试摄像头索引 {i} 时出错: {e}")
            finally:
                if cap:
                    cap.release()
                    
        logger.info(f"摄像头检测完成，找到 {len(available_cameras)} 个可用摄像头: {available_cameras}")
        return available_cameras

    @staticmethod 
    def get_default_camera():
        """
        获取默认可用的摄像头索引
        
        返回:
            int: 第一个可用的摄像头索引，如果没有找到则返回0
        """
        available = Camera.find_available_cameras(max_test=5)  # 只测试前5个索引
        if available:
            logger.info(f"使用默认摄像头: 索引 {available[0]}")
            return available[0]
        else:
            logger.warning("未检测到可用摄像头，使用索引 0")
            return 0

    def __init__(self, source='auto', width=640, height=480, fps=None, web_enabled=False, port=8090):
        """
        初始化摄像头
        
        参数:
            source: 视频源，可以是：
                   - 'auto': 自动检测第一个可用的摄像头
                   - int: 摄像头索引 (0, 1, 2, ...)
                   - str: 视频文件路径
            width: 输出视频帧宽度
            height: 输出视频帧高度
            fps: 摄像头目标帧率 (用于摄像头设置和读取控制)
            web_enabled: 是否启用网页流服务
            port: 网页服务端口号(默认8090)
        """
        # 处理source参数
        if source == 'auto':
            logger.info("自动检测摄像头模式")
            self.source = self.get_default_camera()
        elif isinstance(source, str) and source.isdigit():
            # 如果传入的是数字字符串，转换为整数
            self.source = int(source)
        else:
            self.source = source
            
        # 基本参数
        self.width = width
        self.height = height
        self.fps_setting = fps # FPS to request from camera
        
        # Web流相关
        self.web_enabled = web_enabled
        self.port = port
        self.web_stream = None
        
        # 状态变量
        self.is_running = False
        self._camera_reader_thread = None
        self._reader_stop_event = threading.Event()
        self._reader_initialized_event = threading.Event() # Signals when _CameraReaderThread has initialized cap
        
        # Frame queue
        self.raw_frame_queue = queue.Queue(maxsize=30) # Buffer up to ~1 second of frames at 30fps
        
        # 资源保护 (used for critical sections in Camera class, less for frame data itself now)
        self._lock = threading.RLock() 
        
        # If web_enabled, prepare SimpleWebStream instance
        if self.web_enabled:
            self._init_web_stream_instance()

        # For Notebook mode
        self._notebook_mode_thread = None
        self._notebook_mode_stop_event = threading.Event()
        
        # Web帧更新线程
        self._web_frame_thread = None
        self._web_frame_stop_event = threading.Event()
        
        logger.info(f"Camera初始化完成: source={self.source}, size={width}x{height}, fps={fps}")

    def _init_web_stream_instance(self):
        """初始化SimpleWebStream实例"""
        if self.web_stream is None:
            self.web_stream = SimpleWebStream(
                host="0.0.0.0",  # 支持局域网访问
                port=self.port
            )
            logger.info(f"SimpleWebStream instance created for port {self.port}")

    def start(self):
        """启动摄像头 - 使用非阻塞方式，快速返回"""
        with self._lock:
            if self.is_running:
                logger.info("摄像头已经在运行中")
                return True
            
            self.is_running = True # Set state early
            self._reader_stop_event.clear()
            self._reader_initialized_event.clear()

            # Clear any old items from queue, including potential sentinels
            while not self.raw_frame_queue.empty():
                try:
                    self.raw_frame_queue.get_nowait()
                except queue.Empty:
                    break
            
            logger.info("Starting _CameraReaderThread...")
            self._camera_reader_thread = _CameraReaderThread(
                source=self.source,
                width=self.width,
                height=self.height,
                fps=self.fps_setting, # FPS for camera config
                raw_frame_queue=self.raw_frame_queue,
                initialized_event=self._reader_initialized_event,
                stop_event=self._reader_stop_event,
                target_fps=self.fps_setting # FPS for reader loop control
            )
            self._camera_reader_thread.start()
        
        # Wait briefly for reader to signal initialization attempt (success or failure)
        # This helps make get_web_url more robust if called immediately
        self._reader_initialized_event.wait(timeout=5.0) # Max 5s for camera to open
        if not self._reader_initialized_event.is_set():
            logger.warning("Camera reader thread did not signal initialization within timeout.")

        if self.web_enabled:
            logger.info("Starting Web service...")
            # Ensure instance exists if web_enabled was set after __init__
            if not self.web_stream:
                 self._init_web_stream_instance()
            self._start_web_stream() # This is synchronous for web server thread start
        
        logger.info("Camera start() method finished.")
        return True
    
    def _start_web_stream(self):
        """启动Web流服务"""
        try:
            if not self.web_stream:
                logger.warning("Web stream instance not found, cannot start.")
                return None

            logger.info("Starting SimpleWebStream...")
            url = self.web_stream.start()
            if url:
                logger.info(f"Web stream service started: {url}")
                # 启动帧更新线程
                self._start_web_frame_thread()
                return url
            else:
                logger.error("Failed to start web stream service")
                return None
                
        except Exception as e:
            logger.error(f"Failed to start Web stream service: {e}", exc_info=True)
            return None
    
    def _start_web_frame_thread(self):
        """启动Web帧更新线程"""
        if self._web_frame_thread and self._web_frame_thread.is_alive():
            return
            
        self._web_frame_stop_event.clear()
        
        def web_frame_loop():
            """Web帧更新循环"""
            logger.info("Web帧更新线程启动")
            while not self._web_frame_stop_event.is_set() and self.is_running:
                try:
                    # 从队列获取帧
                    frame = self.raw_frame_queue.get(timeout=0.1)
                    if frame is _QUEUE_SENTINEL:
                        logger.info("Web帧更新线程收到停止信号")
                        self.raw_frame_queue.put(_QUEUE_SENTINEL)  # 放回给其他消费者
                        break
                    
                    # 更新Web流帧
                    if self.web_stream:
                        self.web_stream.update_frame(frame)
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Web帧更新线程错误: {e}")
                    break
            
            logger.info("Web帧更新线程结束")
        
        self._web_frame_thread = threading.Thread(target=web_frame_loop, daemon=True)
        self._web_frame_thread.start()
    
    def stop(self):
        """停止摄像头并释放资源"""
        with self._lock:
            if not self.is_running and not (self._notebook_mode_thread and self._notebook_mode_thread.is_alive()):
                logger.info("Camera and Notebook mode already stopped.")
                return
            
            logger.info("Stopping camera and any active modes (Notebook, etc.)...")
            
            # --- Notebook mode cleanup ---
            if self._notebook_mode_thread and self._notebook_mode_thread.is_alive():
                logger.info("Stopping active Notebook mode thread...")
                self._notebook_mode_stop_event.set()
                self._notebook_mode_thread.join(timeout=1.0) # Shorter timeout, main stop will continue
                if self._notebook_mode_thread.is_alive():
                    logger.warning("Notebook mode thread did not join quickly during main stop.")
            self._notebook_mode_thread = None # Ensure it's cleared
            
            # --- Web frame thread cleanup ---
            if self._web_frame_thread and self._web_frame_thread.is_alive():
                logger.info("Stopping web frame thread...")
                self._web_frame_stop_event.set()
                self._web_frame_thread.join(timeout=1.0)
                if self._web_frame_thread.is_alive():
                    logger.warning("Web frame thread did not join quickly during main stop.")
            self._web_frame_thread = None

            self.is_running = False # Signal all loops to stop

            # Stop Web流服务 first
            if self.web_stream and self.web_stream.is_running:
                try:
                    logger.info("Stopping Web stream service...")
                    self.web_stream.stop()
                    logger.info("Web stream service stopped.")
                except Exception as e:
                    logger.error(f"Error stopping Web stream service: {e}")

            # Stop camera reader thread
            if self._camera_reader_thread and self._camera_reader_thread.is_alive():
                logger.info("Signaling _CameraReaderThread to stop...")
                self._reader_stop_event.set()
                # The reader thread will put a sentinel in the queue.
                # Wait for the reader thread to finish
                self._camera_reader_thread.join(timeout=5.0)
                if self._camera_reader_thread.is_alive():
                    logger.warning("_CameraReaderThread did not stop in time.")
            self._camera_reader_thread = None
            
            # Clear the queue of any remaining items
            logger.info("Clearing raw_frame_queue...")
            while not self.raw_frame_queue.empty():
                try:
                    item = self.raw_frame_queue.get_nowait()
                    if item is _QUEUE_SENTINEL:
                        logger.debug("Found sentinel in raw_frame_queue during stop cleanup.")
                except queue.Empty:
                    break
            
            self._reader_initialized_event.clear()
            
        logger.info("Camera stopped successfully.")
        
    def get_web_url(self):
        """获取网页流服务的访问URL"""
        if not self.web_enabled:
            logger.info("Web service is not enabled.")
            return None
            
        if not self.web_stream:
            logger.warning("Web_stream instance not initialized in get_web_url.")
            if self.is_running:
                self._init_web_stream_instance()
                self._start_web_stream()
            else:
                return None

        if not self.web_stream or not self.web_stream.is_running:
            logger.warning("Web stream is not running or URL not yet available.")
            return None
            
        return self.web_stream.get_url()
    
    def cv_show(self, frame, mode="cv2", wait_key=1, window_name="预览"):
        """
        显示图像并处理按键
        
        参数:
            frame: 要显示的图像帧
            mode: 显示模式，"cv2"表示本地显示
            wait_key: cv2.waitKey的等待时间(毫秒)，仅cv2模式有效
            window_name: 窗口名称，仅cv2模式有效
        
        返回:
            cv2模式下，如果按下'q'或'ESC'则返回True
        """
        if frame is None:
            return False
        
        display_frame = frame
        if len(frame.shape) == 2: # Grayscale
            display_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
        cv2.imshow(window_name, display_frame)
        key = cv2.waitKey(wait_key) & 0xFF
        return key == ord('q') or key == 27
    
    def read(self, timeout=1.0):
        """
        读取一帧（OpenCV兼容接口）
        
        参数:
            timeout: Max time to wait for a frame in seconds.
        返回:
            (ret, frame) 元组，ret表示是否成功，frame为读取的帧 or None
        """
        if not self.is_running and self.raw_frame_queue.empty():
            return False, None
            
        # Wait for camera initialization signal before trying to get from queue
        if not self._reader_initialized_event.is_set():
             initialized = self._reader_initialized_event.wait(timeout=0.05) # Brief wait
             if not initialized and not self.raw_frame_queue.qsize() > 0 : # Check queue size as fallback
                logger.debug("Read called before camera fully initialized, no frame in raw_frame_queue yet.")
                return False, None # Not ready yet

        try:
            frame = self.raw_frame_queue.get(block=True, timeout=timeout)
            if frame is _QUEUE_SENTINEL:
                # Put it back for other consumers if any, then return failure
                self.raw_frame_queue.put(_QUEUE_SENTINEL) 
                return False, None
            return True, frame
        except queue.Empty:
            return False, None
        except Exception as e:
            logger.error(f"Error reading frame from raw_frame_queue: {e}")
            return False, None
    
    def __iter__(self):
        """返回迭代器自身"""
        if not self.is_running:
            logger.info("Iterator accessed before explicit start(), attempting to start camera...")
            self.start()
        return self
    
    def __next__(self):
        """获取下一帧 for iteration"""
        if not self.is_running and self.raw_frame_queue.empty():
            logger.debug("__next__: Not running and raw_frame_queue empty, raising StopIteration.")
            raise StopIteration
        
        # Wait for initialization, but with a timeout to prevent indefinite block if init fails
        if not self._reader_initialized_event.is_set():
            initialized = self._reader_initialized_event.wait(timeout=1.0) # Wait up to 1s
            if not initialized and self.raw_frame_queue.empty():
                 logger.warning("__next__: Camera not initialized after 1s, and raw_frame_queue empty. StopIteration.")
                 if not self.is_running: # If start() failed to keep it running
                    raise StopIteration
        
        try:
            # Blocking get, but _CameraReaderThread puts a sentinel on stop.
            frame = self.raw_frame_queue.get(block=True, timeout=2.0) # Timeout to prevent permanent block
            if frame is _QUEUE_SENTINEL:
                logger.info("__next__: Sentinel received from raw_frame_queue, raising StopIteration.")
                raise StopIteration
            return frame
        except queue.Empty:
            logger.warning("__next__: raw_frame_queue empty after timeout. Raising StopIteration as camera might be stuck or stopped.")
            self.is_running = False # Ensure loop terminates
            raise StopIteration
        except Exception as e:
            logger.error(f"__next__: Error getting frame from raw_frame_queue: {e}")
            self.is_running = False # Ensure loop terminates
            raise StopIteration
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.is_running:
            self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
        
    def __del__(self):
        """析构函数，确保资源释放"""
        if self.is_running or (self._camera_reader_thread and self._camera_reader_thread.is_alive()):
            logger.debug(f"Camera __del__ called on a potentially running instance. Attempting to stop.")
            self.stop()

    def set_port(self, port):
        """设置Web服务端口，如果服务已启动会重启服务使用新端口"""
        with self._lock:
            old_port = self.port
            if old_port == port:
                logger.info(f"Port already set to {port}.")
                return self.port
            
            self.port = port
            logger.info(f"Web service port changed from {old_port} to {port}.")

            if self.web_enabled:
                if self.web_stream and self.web_stream.is_running:
                    logger.info("Restarting Web service to apply new port...")
                    self.web_stream.stop()
                    
                    # Create a new instance
                    self._init_web_stream_instance()
                    if self.is_running:
                         self._start_web_stream()
                    else:
                        logger.info("Camera is not running, web service will start with new port on next Camera.start()")
                elif self.web_stream:
                    self.web_stream.port = port 
                    logger.info(f"Web service instance port updated to {port}. Will be used on next start.")
                else:
                    logger.info(f"Port set to {port}. Will be used when web service is initialized.")
            else:
                logger.info(f"Port set to {port}, but web service is not enabled.")
        return self.port 

    def start_notebook_mode(self, width=None, height=None, fps=None, port=None, loop_interval=0.02):
        """
        启动适合Jupyter Notebook的模式
        自动获取帧并更新Web流

        Args:
            width (int, optional): Override camera width.
            height (int, optional): Override camera height.
            fps (int, optional): Override camera FPS.
            port (int, optional): Override web service port.
            loop_interval (float, optional): Interval in seconds for the frame fetching loop. Defaults to 0.02.

        Returns:
            str: The URL to access the web stream, or None if failed.
        """
        with self._lock:
            if self._notebook_mode_thread and self._notebook_mode_thread.is_alive():
                logger.info("Notebook mode is already running.")
                return self.get_web_url()

            self.web_enabled = True # Notebook mode implies web is enabled

            # Apply overrides if provided
            if width is not None: self.width = width
            if height is not None: self.height = height
            if fps is not None: self.fps_setting = fps
            if port is not None:
                self.set_port(port) 
            
            # Ensure web stream instance uses the potentially updated port
            if self.web_stream is None or (port is not None and self.web_stream.port != port):
                self._init_web_stream_instance()

            logger.info("Starting camera for Notebook mode...")
            if not self.start():
                logger.error("Failed to start camera in Notebook mode.")
                return None
            
            # Ensure web service is actually started by self.start()
            if not self.web_stream or not self.web_stream.is_running:
                logger.info("Notebook mode: Ensuring web stream is started...")
                self._start_web_stream()
                if not self.web_stream or not self.web_stream.is_running:
                    logger.error("Notebook mode: Failed to start web stream service.")
                    self.stop()
                    return None

            # Wait a brief moment for the URL to become available
            url = None
            for _ in range(10): # Try for up to 1 second
                url = self.get_web_url()
                if url:
                    break
                time.sleep(0.1)
            
            if not url:
                 logger.warning("Notebook mode: Web URL not available after timeout. Service might be slow to start.")
            
            return url

    def stop_notebook_mode(self):
        """
        停止notebook模式并停止摄像头
        """
        logger.info("Stopping Notebook mode...")
        self.stop()
        logger.info("Notebook mode stopped successfully.")
        