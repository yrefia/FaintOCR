## 注意：该版本需要在python3.12下运行

# 新增了正则表达式计算token数；更改了prefix的limits

# 新增独立计算截图耗时的算法
# OCR前新增注释掉的二值化处理及图像保存(无效)
# 限制了最大边长及最大并发线程数 !!限制最大边长会导致空格/换行无法被识别!!
# $不考虑OCR置信度过滤，因为无法准确过滤的同时会误杀
# $加入了print(result)调试语句

# 解决了最小化和关闭按钮难以点击的问题

# 解决了主界面及字幕悬浮窗会影响截图的问题
# 在前缀匹配中移除了t3项，因其会造成短文本的误匹配(通过修改小于等于为小于仅改变了相似度并没有根本解决问题)

# 更改了前缀匹配的小于等于为小于来限制相似度及比例
# 重构了class TextMatcher中有关文本匹配的逻辑
# $文本匹配现在允许返回多个匹配相似度值

# 新增了的update_textmap的计时显示
# 更改了加载及下载的UI，现在切换游戏/方向不会自动加载



import re
import sys
import os
import time
import ctypes  # <--- [新增]
from ctypes import wintypes  # <--- [新增]
import orjson  # 用于快速读取 JSON 文件，性能优于标准库 json
import mss  # 跨平台屏幕截图库，速度快
import mss.tools
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QRect
from rapidocr_onnxruntime import RapidOCR  # <-- 新增：极速OCR引擎，基于ONNX Runtime
import cv2  # OpenCV，用于图像处理
import numpy as np
from rapidfuzz import process, fuzz  # 快速模糊匹配库，用于修正OCR结果


# <--- [新增] Windows API 常量定义
# 0x00000011 = WDA_EXCLUDEFROMCAPTURE (Windows 10 2004+ 必须)
WDA_EXCLUDEFROMCAPTURE = 0x00000011

# ====== 配置与样式封装 ======

# 路径计算：获取当前脚本所在目录及项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR  # 仓库根目录（脚本当前所在目录）


class Config:
    """
    全局配置管理类
    存储文件路径、默认参数以及游戏特定的数据源URL
    """
    PATHS = {
        "TEXTMAP_ROOT": os.path.join(PROJECT_ROOT, "TextMap"),  # 原始字典存放路径
        "TEXTMAP_MERGED_ROOT": os.path.join(PROJECT_ROOT, "TextMap_KeyLan"),  # 合并后字典存放路径
        "OUTPUT_FILE": os.path.join(PROJECT_ROOT, "OCR_Results.txt")  # 自动保存结果的文件路径
    }

    OCR = {
        "DEFAULT_REGION": (100, 810, 1720, 240),  # 默认截图区域 (x, y, w, h)
        "DEFAULT_INTERVAL": 2.0,  # 自动OCR的默认间隔时间（秒）
    }

    # 游戏配置：定义了不同游戏的文件夹名称和字典下载地址
    GAMES = {
        "Honkai：Star Rail": {
            "folder": "Honkai：Star-Rail",
            "urls": {
                "TextMapEN.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapEN.json",
                "TextMapCHS.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapCHS.json"
            }
        },
        "Genshin Impact": {
            "folder": "Genshin-Impact",
            "urls": {
                "TextMapEN.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapEN.json",
                "TextMapCHS.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapCHS.json"
            }
        }
    }


class UIStyles:
    """
    UI样式统一管理类
    使用 QSS (类似于 CSS) 定义界面的外观
    """
    MAIN_WINDOW = """
        QWidget {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #2c3e50, stop:1 #34495e);
            border-radius: 12px;
        }
    """
    # ... (省略具体的样式定义注释，主要涉及按钮、下拉框、滑动条等控件的美化)
    BUTTON_Themed = """
        QPushButton {
            background-color: #409EFF;
            color: white;
            border-radius: 6px;
            padding: 6px 10px;
            min-width: 60px;
        }
        QPushButton:checked {
            background-color: #67C23A;
        }
        QPushButton:hover {
            background-color: #66b1ff;
        }
    """
    BUTTON_Dark = """
        QPushButton {
            background-color: #34495e; 
            color: #ecf0f1; 
            border: 1px solid #7f8c8d; 
            border-radius: 3px; 
            padding: 4px; 
            font-size: 10px;
        }
        QPushButton:hover {
            background-color: #409EFF;
        }
        QPushButton:pressed {
            background-color: #2c3e50;
        }
    """
    # 在 UIStyles 类中，替换原有的 WINDOW_OP_BUTTON
    # 或者直接添加这两个新的样式属性

    # 最小化按钮：背景设为极低透明度(1)，使其可点击但不可见
    WINDOW_BTN_MIN = """
            QPushButton {
                background-color: rgba(255, 255, 255, 2);  /* 核心修复：2/255的不透明度(1会非常白可能是bug) */
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 40); /* 悬停时显示明显的灰色 */
            }
        """

    # 关闭按钮：背景设为极低透明度(1)
    WINDOW_BTN_CLOSE = """
            QPushButton {
                background-color: rgba(255, 255, 255, 2); /* 核心修复：2/255的不透明度(1会非常白可能是bug) */
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(232, 11, 23, 160); /* 悬停变红 */
            }
        """

    COMBO_BOX = """
        QComboBox {
            background-color: #34495e;
            color: white;
            border: 1px solid #7f8c8d;
            border-radius: 3px; 
            padding: 2px;
        }
        QComboBox:disabled {
            background-color: #2c3e50;
            color: #7f8c8d;
        }
    """
    GROUP_BOX = "QGroupBox{color:white;border:1px solid gray;border-radius:5px;margin-top:6px;} QGroupBox::title{subcontrol-origin:margin;left:10px;}"
    SUBTITLE_WINDOW = """
            #SubtitleFrame {
                background-color: rgba(15, 15, 15, 180);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 15px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: "Microsoft YaHei UI";
                font-size: 22px;
                font-weight: 500;
                background: transparent;
            }
        """
    BUTTON_TOGGLE = """
            QPushButton {
                background-color: #67C23A;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #F56C6C;
            }
        """
    TEXT_EDIT = "QTextEdit { background-color: rgba(255,255,255,0.9); color: black; border-radius: 5px; padding: 8px; font-size: 12px; }"
    SPIN_BOX = "QSpinBox { background: white; border-radius: 4px; padding: 2px; min-width: 60px; }"
    SLIDER = "QSlider::groove:horizontal { height: 8px; background: #7f8c8d; border-radius: 4px; } QSlider::handle:horizontal { width: 16px; height: 16px; background: #409EFF; border-radius: 8px; margin: -4px 0; }"


class DictionaryWorker(QtCore.QThread):
    """
    字典操作后台线程
    用于处理耗时的文件下载和加载操作，避免阻塞主界面 (UI Freeze)
    """
    progress_signal = QtCore.Signal(str)  # 发送文本状态信息
    finished_signal = QtCore.Signal(bool, str)  # 发送完成状态 (成功/失败, 信息)
    map_loaded_signal = QtCore.Signal(dict)  # 发送加载好的字典数据
    percent_signal = QtCore.Signal(int)  # <--- 新增：用于传输下载进度百分比 (0-100)

    def __init__(self, loader, task_type, direction=None):
        super().__init__()
        self.loader = loader  # TextMapLoader 实例
        self.task_type = task_type  # 任务类型: "download" 或 "load"
        self.direction = direction  # 翻译方向 (仅用于 "load" 任务)

    def run(self):
        """线程入口函数"""
        if self.task_type == "download":
            # <--- 修改：将 percent_signal.emit 作为回调函数传入 loader
            success, msg = self.loader.download_files(
                progress_callback=self.progress_signal.emit,
                percent_callback=self.percent_signal.emit
            )
            self.finished_signal.emit(success, msg)
        elif self.task_type == "load":
            try:
                self.progress_signal.emit(f"正在加载/生成 {self.direction} 字典...")
                # 执行耗时的加载/合并逻辑
                data = self.loader.load_text_map(self.direction)
                self.map_loaded_signal.emit(data)
            except Exception as e:
                self.finished_signal.emit(False, f"加载失败: {str(e)}")


class TextMapLoader:
    """
    文本映射加载器
    负责下载原始 JSON 数据，并将其处理为键值对字典 (Key-Value Map)
    """

    def __init__(self, textmap_dir, textmap_merged_dir, textmap_file):
        self.textmap_dir = textmap_dir
        self.textmap_merged_dir = textmap_merged_dir
        self.default_textmap_file = textmap_file
        self.current_urls = {}

    def update_paths(self, game_key):
        """切换游戏时更新相关路径和下载URL"""
        config = Config.GAMES[game_key]
        base_dir = os.path.join(PROJECT_ROOT, config["folder"])
        self.textmap_dir = os.path.join(base_dir, "TextMap")
        self.textmap_merged_dir = os.path.join(base_dir, "TextMap_KeyLan")
        self.default_textmap_file = os.path.join(self.textmap_merged_dir, "TextMapEN_CHS.json")
        self.current_urls = config["urls"]

    def download_files(self, progress_callback=None, percent_callback=None):
        """下载游戏数据文件"""
        import urllib.request
        os.makedirs(self.textmap_dir, exist_ok=True)

        # <--- 新增：定义 urllib 的进度回调函数
        def _reporthook(block_num, block_size, total_size):
            """
            block_num: 已下载的数据块数量
            block_size: 数据块大小
            total_size: 文件总大小
            """
            if percent_callback and total_size > 0:
                # 计算下载百分比
                percent = int((block_num * block_size) / total_size * 100)
                # 限制在 0-100 之间，防止数值溢出
                percent = max(0, min(100, percent))
                percent_callback(percent)

        try:
            for file_name, url in self.current_urls.items():
                target_path = os.path.join(self.textmap_dir, file_name)
                if progress_callback:
                    progress_callback(f"正在下载 {file_name}...")

                # <--- 修改：传入 reporthook 参数以实现进度条更新
                urllib.request.urlretrieve(url, target_path, reporthook=_reporthook)

            return True, "下载完成"
        except Exception as e:
            return False, f"下载失败: {str(e)}"

    def load_text_map(self, direction="en_to_chs"):
        """加载或生成文本映射字典（方案一：保留所有翻译，值存储为列表）"""
        os.makedirs(self.textmap_merged_dir, exist_ok=True)
        # 根据方向决定文件名
        file_name = "TextMapEN_CHS.json" if direction == "en_to_chs" else "TextMapCHS_EN.json"
        target_file = os.path.join(self.textmap_merged_dir, file_name)

        # 1. 如果合并后的缓存文件存在，直接读取
        if os.path.exists(target_file):
            try:
                with open(target_file, 'rb') as f:
                    text_map = orjson.loads(f.read())
                    print(f"[{direction}] 已加载映射文件，包含 {len(text_map)} 条记录")
                    return text_map
            except Exception as e:
                print(f"加载映射文件失败: {e}")

        # 2. 如果缓存不存在，读取原始的 EN 和 CHS 文件进行合并
        en_file = os.path.join(self.textmap_dir, "TextMapEN.json")
        chs_file = os.path.join(self.textmap_dir, "TextMapCHS.json")

        if not os.path.exists(en_file) or not os.path.exists(chs_file):
            print("原始文本映射文件不存在，跳过文本匹配功能")
            return {}

        print(f"正在生成 {direction} 映射文件 (保留所有多义词翻译)，请稍候...")
        try:
            with open(en_file, 'rb') as f:
                en_data = orjson.loads(f.read())
            with open(chs_file, 'rb') as f:
                chs_data = orjson.loads(f.read())

            merged_data = {}
            # 遍历英文数据，寻找对应的中文数据
            for key in en_data.keys():
                if key in chs_data:
                    # 清理换行符，防止匹配干扰
                    en_text = en_data[key].replace('\\n', ' ').strip()
                    chs_text = chs_data[key].replace('\\n', ' ').strip()
                    if not en_text or not chs_text:
                        continue

                    # 根据方向确定源和目标
                    source, target = (en_text, chs_text) if direction == "en_to_chs" else (chs_text, en_text)

                    # --- 修改点：使用 set 存储多义词，防止覆盖 ---
                    if source not in merged_data:
                        merged_data[source] = set()
                    merged_data[source].add(target)

            # --- 修改点：将 set 转换为 list 以便 JSON 序列化 ---
            # 最终结构: {"Open": ["打开", "开启"], ...}
            final_data = {k: list(v) for k, v in merged_data.items()}

            # 3. 将合并后的数据保存为缓存文件
            with open(target_file, 'wb') as f:
                f.write(orjson.dumps(final_data, option=orjson.OPT_INDENT_2))

            print(f"[{direction}] 映射文件已生成: {target_file}")
            return final_data

        except Exception as e:
            print(f"生成文本映射文件失败: {e}")
            return {}


class SelectionOverlay(QtWidgets.QWidget):
    """
    屏幕区域选择遮罩层
    全屏透明窗口，允许用户通过鼠标拖拽框选 OCR 区域
    """
    selection_completed = QtCore.Signal(QRect)  # 选区完成信号

    def __init__(self):
        super().__init__()
        # 设置窗口属性：置顶、无边框、工具窗口
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 背景透明
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(screen)  # 覆盖全屏
        self.start_point = None
        self.end_point = None
        self.selecting = False
        self.setCursor(Qt.CursorShape.CrossCursor)  # 鼠标变为十字线

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()  # 激活窗口以捕获按键
        self.setFocus()
        self.raise_()

    def paintEvent(self, event):
        """绘制半透明背景和蓝色选框"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        # 绘制全屏半透明灰色遮罩
        painter.fillRect(self.rect(), QtGui.QColor(100, 100, 100, 150))

        # 绘制过程保持使用逻辑坐标（跟随鼠标视觉位置）
        if self.selecting and self.start_point and self.end_point:
            selection_rect = QtCore.QRect(self.start_point, self.end_point).normalized()
            # "挖空"选区部分（完全透明）
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection_rect, QtGui.QColor(0, 0, 0, 0))
            # 绘制蓝色边框
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QtGui.QPen(QtGui.QColor(0, 120, 255), 2)
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.selecting = True
            self.update()  # 触发重绘

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.end_point = event.position().toPoint()
            self.update()  # 拖动时持续重绘

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.end_point = event.position().toPoint()
            self.selecting = False

            # --- 修改：将逻辑坐标转换为物理坐标 ---
            # 关键逻辑：解决高分屏(DPI缩放)下的坐标偏差问题
            ratio = self.devicePixelRatio()

            # 必须分别计算点的物理坐标，以确保截图时的像素位置准确
            phys_start_x = int(self.start_point.x() * ratio)
            phys_start_y = int(self.start_point.y() * ratio)
            phys_end_x = int(self.end_point.x() * ratio)
            phys_end_y = int(self.end_point.y() * ratio)

            p1 = QtCore.QPoint(phys_start_x, phys_start_y)
            p2 = QtCore.QPoint(phys_end_x, phys_end_y)

            # 生成物理坐标矩形
            selected_rect = QtCore.QRect(p1, p2).normalized()
            # ------------------------------------

            self.selection_completed.emit(selected_rect)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()  # 按ESC取消
        super().keyPressEvent(event)


class RegionOverlay(QtWidgets.QWidget):
    """
    区域预览层
    当用户调整坐标时，短暂显示当前的截图区域
    """

    def __init__(self, region):
        super().__init__()
        self.region = region  # 这里的 region 已经是物理坐标
        self.setup_ui()

    def setup_ui(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowType.Tool)
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        # 500毫秒后自动关闭
        QtCore.QTimer.singleShot(500, self.close)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 100))  # 灰色背景

        # --- 修改：将物理坐标转换回逻辑坐标进行绘制 ---
        # 屏幕显示需要逻辑坐标，截图需要物理坐标
        ratio = self.devicePixelRatio()
        phys_x, phys_y, phys_w, phys_h = self.region

        # 计算逻辑坐标用于屏幕显示
        log_x = int(phys_x / ratio)
        log_y = int(phys_y / ratio)
        log_w = int(phys_w / ratio)
        log_h = int(phys_h / ratio)
        # ----------------------------------------

        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(log_x, log_y, log_w, log_h, QtGui.QColor(0, 0, 0, 0))
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
        pen = QtGui.QPen(QtGui.QColor(0, 180, 255), 3)
        painter.setPen(pen)
        painter.drawRect(log_x, log_y, log_w, log_h)


class OCRWorker(QtCore.QRunnable):
    """
    OCR 工作单元
    在线程池中运行，执行 "截图数据 -> OCR -> 模糊匹配" 的流程
    """

    class Signals(QtCore.QObject):
        finished = QtCore.Signal(str, str)  # 信号：(处理后的文本, 原始文本)

    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data
        self.signals = self.Signals()

    def run(self):
        try:
            # --- 计时开始 ---
            t_start = time.perf_counter()

            # 提取常规参数
            ocr_engine = self.task_data.get('ocr_engine')
            text_matcher = self.task_data.get('text_matcher')
            match_mode = self.task_data.get('match_mode', 0)
            similarity_threshold = self.task_data.get('similarity_threshold', 60)
            img_cv = self.task_data.get('img_cv')
            monitor = self.task_data.get('monitor')

            # 支持在子线程中截图
            if img_cv is None and monitor is not None:
                with mss.mss() as sct:
                    sct_img = sct.grab(monitor)
                    img_np = np.array(sct_img)
                    img_cv = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

            if img_cv is None:
                raise ValueError("Image data is missing")
            if ocr_engine is None:
                raise ValueError("OCR Engine not initialized")

                # Params: 图像预处理 (提速优化)
                # 1. 灰度化：将 BGR 三通道转为单通道，数据量减少 2/3，显著提升推理速度
                # 注意：RapidOCR (ONNX) 内部虽有处理，但显式转换通常更快且兼容性更好
            # if len(img_cv.shape) == 3:
            #    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                # 2. 二值化 (可选)：将图像变为纯黑白
                # 说明：这能进一步提速，但游戏字体通常带有抗锯齿、阴影或半透明背景。
                # 暴力二值化(OTSU)可能会导致文字边缘锯齿化，反而降低识别率。
                # 建议：先仅使用灰度化。如果速度仍不满足，再尝试取消下面这行的注释。
            #    _, img_cv = cv2.threshold(img_cv, 200, 255, cv2.THRESH_BINARY)
            #    _, img_cv = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # cv2.imwrite(r'D:\IA\OCR\FaintOCR.bak\Image_Output\processed_image.jpg', img_cv)

            # --- 计时：截图完成---
            t_process1 = time.perf_counter()
            capture_cost = t_process1 - t_start

            # 执行 OCR
            raw_text = self.run_rapidocr(ocr_engine, img_cv)

            # --- 计时：OCR完成 ---
            t_process2 = time.perf_counter()
            ocr_cost = t_process2 - t_process1

            if not raw_text or raw_text.strip() == "":
                self.signals.finished.emit("[未识别到文本]", "")
                return

            # 获取分离的匹配结果
            text_original, text_translated, similarity = self.process_text_with_matching(
                raw_text, text_matcher, match_mode, similarity_threshold
            )

            # --- 计时结束：文本匹配 ---
            t_end = time.perf_counter()
            match_cost = t_end - t_process2

            # 3. 构造界面所需的数据
            # 格式化耗时信息，保留3位小数
            perf_info = f"截图: {capture_cost:.3f}s | OCR: {ocr_cost:.3f}s | 匹配: {match_cost:.3f}s"

            if text_translated:
                # 匹配成功
                subtitle_text = f"{text_original}\n{text_translated}"
                # 将耗时信息与相似度拼接
                status_info = f"{perf_info} | 相似度: {similarity}%"
            else:
                # 未匹配
                subtitle_text = text_original
                status_info = perf_info

            # 发送信号
            self.signals.finished.emit(subtitle_text, status_info)

        except Exception as e:
            self.signals.finished.emit(f"[OCR错误] {str(e)}", "")

    def run_rapidocr(self, engine, img):
        """
        调用 RapidOCR 引擎进行推理
        并根据文本框的垂直位置关系决定是否换行
        """
        # result 格式: [[box, text, score], [box, text, score], ...]
        # box 格式: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] (左上, 右上, 右下, 左下)
        result, _ = engine(img)
        print(result)

        if not result:
            return ""

        # 初始化：取出第一个文本块
        full_text = result[0][1]
        prev_box = result[0][0]

        # 从第二个文本块开始遍历
        for i in range(1, len(result)):
            curr_text = result[i][1]
            curr_box = result[i][0]

            # 1. 计算上一个文本框的【最底部】Y坐标
            # 取左下(index 3)和右下(index 2)的 Y 坐标平均值
            prev_bottom_y = (prev_box[2][1] + prev_box[3][1]) / 2

            # 2. 计算当前文本框的【最上部】Y坐标
            # 取左上(index 0)和右上(index 1)的 Y 坐标平均值
            curr_top_y = (curr_box[0][1] + curr_box[1][1]) / 2

            # 3. 核心判断逻辑
            # 如果 上一个框底 < 下一个框顶，说明在视觉上是上下两行 -> 换行
            if prev_bottom_y < curr_top_y:
                full_text += "\n" + curr_text
            else:
                # 否则认为在同一行 -> 加空格拼接
                full_text += " " + curr_text

            # 更新 prev_box 为当前框，用于下一次比较
            prev_box = curr_box

        return full_text.strip()

    def process_text_with_matching(self, ocr_text, text_matcher, match_mode, similarity_threshold):
        """
        尝试在字典中查找 OCR 识别到的文本
        返回: (原词, 翻译文本, 相似度数值)
        """
        # 参数校验：如果模式为0、OCR文本为空、或字典未加载，直接返回原文本
        if (match_mode == 0 or not ocr_text or
                ocr_text.startswith("[") or not text_matcher or
                not text_matcher.text_map):
            return ocr_text, None, 0

        # 执行匹配
        matched_key, matched_translation, similarity = text_matcher.match_text(
            ocr_text, match_mode, similarity_threshold
        )

        # 匹配成功
        if matched_key and matched_translation:
            # 返回结构化数据：(匹配到的原词, 翻译, 相似度)
            return matched_key, matched_translation, similarity

        # 匹配失败，仅返回 OCR 原始文本
        return ocr_text, None, 0


class TextMatcher:
    """
    文本匹配器
    使用 RapidFuzz 库在已加载的字典中进行模糊查找
    [修改版]：使用正则分词（组合文字/象形文字/符号）逻辑代替纯字符长度逻辑
    """

    def __init__(self, text_map, cache_size=3):
        self.text_map = text_map
        self.cache = {}  # 简单的 LRU 缓存
        self.cache_size = cache_size

        # --- 1. 正则表达式预编译 (核心修改) ---
        # 组合文字: 英文、数字、德法西欧重音字符、阿拉伯文、下划线
        combo_chars = r'a-zA-Z0-9\u00C0-\u024F\u0600-\u06FF_'
        # 象形文字: 中文、日文、韩文
        ideograph_chars = r'\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af'

        # 组装正则:
        # 1. 组合文字 (匹配一次或多次 +)
        # 2. 象形文字 (匹配一次)
        # 3. 符号 (既不是组合也不是象形，包含空格，匹配一次或多次 +)
        # 注意：这里去掉了 \s 的排除，意味着空格会被视为符号的一部分被捕获
        self.tokenizer_pattern = re.compile(
            f'[{combo_chars}]+|[{ideograph_chars}]|[^{combo_chars}{ideograph_chars}]+'
        )

        # --- 初始化分级列表 (按 Token 数量分级) ---
        self.keys_list = []  # 原始 Key 列表
        self.candidates_t5 = []  # 前 5 个 Token 的前缀
        self.candidates_t8 = []  # 前 8 个 Token 的前缀
        self.candidates_t13 = []  # 前 13 个 Token 的前缀
        self.candidates_t21 = []  # 前 21 个 Token 的前缀
        self.candidates_full = []  # 完整列表 (用于 >3 Token 的情况)

        # 初始化数据
        self.update_map(text_map)

        self.hits = 0
        self.misses = 0

    def _tokenize(self, text):
        """[新增] 使用正则将文本拆分为 Token 列表"""
        if not text:
            return []
        return self.tokenizer_pattern.findall(text)

    def update_map(self, new_map):
        """
        更新字典时，基于 Token 数量生成前缀列表
        """
        t_start = time.perf_counter()
        self.text_map = new_map
        self.clear_cache()

        if new_map:
            self.keys_list = list(new_map.keys())
            self.candidates_full = self.keys_list

            # 预初始化列表
            c5, c8, c13, c21 = [], [], [], []

            # 遍历所有 Key 进行分词预处理
            # 注意：如果字典非常大，这步可能会比简单的字符串切片稍慢，但在接受范围内
            for k in self.keys_list:
                tokens = self._tokenize(k)
                # 生成不同长度的前缀字符串用于模糊匹配
                # 如果 key 本身很短（例如只有一个 token），tokens[:2] 会自动处理为完整 key
                c5.append("".join(tokens[:5]))
                c8.append("".join(tokens[:8]))
                c13.append("".join(tokens[:13]))
                c21.append("".join(tokens[:21]))

            self.candidates_t5 = c5
            self.candidates_t8 = c8
            self.candidates_t13 = c13
            self.candidates_t21 = c21
            # --- 计时结束 ---
            t_end = time.perf_counter()
            t_cost = t_end - t_start
            print(f"update_map: {t_cost:.7f}s")
        else:
            self.keys_list = []
            self.candidates_full = []
            self.candidates_t5 = []
            self.candidates_t8 = []
            self.candidates_t13 = []
            self.candidates_t21 = []

    def match_text(self, ocr_text, mode, threshold):
        """对外暴露的匹配接口，带缓存"""
        if mode == 0 or not ocr_text or not self.text_map:
            return None, None, 0

        # 生成缓存键
        cache_key = f"{ocr_text}_{mode}_{threshold}"
        if cache_key in self.cache:
            self.hits += 1
            val = self.cache.pop(cache_key)
            self.cache[cache_key] = val
            return val

        self.misses += 1

        if mode == 1:
            result = self._match_full_text(ocr_text, threshold)
        elif mode == 2:
            result = self._match_prefix_text(ocr_text, threshold)
        else:
            result = (None, None, 0)

        if len(self.cache) >= self.cache_size:
            self.cache.pop(next(iter(self.cache)))

        self.cache[cache_key] = result
        return result

    def _get_formatted_value(self, key):
        """[提取] 统一获取格式化后的字典值"""
        val = self.text_map.get(key)
        if isinstance(val, list):
            return " / ".join(val)
        return str(val)

    def _process_fuzzy_results(self, ocr_text, candidates, similarity_threshold):
        """[提取] 统一的模糊匹配与结果处理逻辑(支持返回多重相似度)"""
        # 执行匹配，统一返回 (match_str, score, index)
        results = process.extract(
            ocr_text,
            candidates,
            scorer=fuzz.QRatio,
            limit=3
        )

        if not results:
            return None, None, 0

        # 1. 高置信度处理 (>90) - 统一了原代码中 >=90 和 >90 的细微差异，建议统一用 90
        high_confidence_results = [r for r in results if r[1] >= 90]

        if high_confidence_results:
            # 统一使用索引 (r[2]) 回溯原始 Key
            # 这样无论是截断的前缀列表还是完整的全词列表，都能找到对应的原始 Key
            matched_indices = [r[2] for r in high_confidence_results]
            original_keys = [self.keys_list[i] for i in matched_indices]

            matched_keys_str = " | ".join(original_keys)
            matched_values_str = " | ".join([self._get_formatted_value(k) for k in original_keys])

            # --- 修改点：提取所有高分匹配的相似度并拼接 ---
            # 格式化为字符串: "99.12 | 98.50"
            scores_list = [f"{r[1]:.2f}" for r in high_confidence_results]
            scores_str = " | ".join(scores_list)

            # 注意：这里返回的是字符串，UI层会自动在末尾加上一个 '%'
            # 最终界面显示效果如: "相似度: 99.12 | 98.50%"
            return matched_keys_str, matched_values_str, scores_str

        # 2. 最佳匹配处理 (<90 但 >阈值)
        best_match_str, score, idx = results[0]
        if score >= similarity_threshold:
            best_key = self.keys_list[idx]
            # 单个结果也保留2位小数，保持一致性
            return best_key, self._get_formatted_value(best_key), f"{score:.2f}"

        return None, None, 0

    def _match_full_text(self, ocr_text, similarity_threshold=60):
        """完全匹配模式 (重构后)"""
        if not self.text_map or not ocr_text.strip():
            return None, None, 0

        # 1. 精确匹配优化 (保留原逻辑中的快速查找)
        if ocr_text in self.text_map:
            return ocr_text, self._get_formatted_value(ocr_text), 100

        # 2. 调用通用模糊匹配逻辑
        # 传入完整候选列表
        return self._process_fuzzy_results(ocr_text, self.candidates_full, similarity_threshold)

    def _match_prefix_text(self, ocr_text, similarity_threshold=60):
        """前缀匹配模式 (重构后)"""
        if not self.text_map or not ocr_text.strip():
            return None, None, 0

        # 1. 动态选择候选列表 (这是模式2独有的逻辑)
        ocr_tokens = self._tokenize(ocr_text)
        token_count = len(ocr_tokens)

        if token_count < 5:
            target_candidates = self.candidates_t5
        elif token_count < 8:
            target_candidates = self.candidates_t8
        elif token_count < 13:
            target_candidates = self.candidates_t13
        elif token_count < 21:
            target_candidates = self.candidates_t21
        else:
            target_candidates = self.candidates_full

        # 2. 调用通用模糊匹配逻辑
        return self._process_fuzzy_results(ocr_text, target_candidates, similarity_threshold)

    def clear_cache(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class OCRTaskManager(QtCore.QObject):
    """
    任务管理器
    使用生产者-消费者模式管理 OCR 请求，防止短时间内大量任务卡死程序
    """
    task_completed = QtCore.Signal(str, str)  # 任务完成信号

    def __init__(self, max_threads=1, max_queue_size=1):
        super().__init__()
        self.thread_pool = QtCore.QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(max_threads)  # 限制最大并发线程数
        self.task_queue = []
        self.max_queue_size = max_queue_size
        self.active_tasks = 0
        self.total_submitted = 0
        self.total_completed = 0

    def submit_task(self, task_data):
        """提交新任务，如果队列满则丢弃最旧的任务"""
        if len(self.task_queue) >= self.max_queue_size:
            removed_task = self.task_queue.pop(0)
            print(f"队列已满，移除旧任务 (队列大小: {len(self.task_queue)})")
        self.task_queue.append(task_data)
        self.total_submitted += 1
        print(f"任务已提交 (队列大小: {len(self.task_queue)}, 活跃任务: {self.active_tasks})")
        self._process_queue()

    def _process_queue(self):
        """检查是否有空闲线程和待处理任务"""
        idle_threads = self.thread_pool.maxThreadCount() - self.active_tasks
        while idle_threads > 0 and self.task_queue:
            task_data = self.task_queue.pop(0)
            worker = OCRWorker(task_data)
            worker.signals.finished.connect(self._on_task_completed)
            self.thread_pool.start(worker)  # 放入线程池执行
            self.active_tasks += 1
            idle_threads -= 1
            print(f"启动新任务 (活跃任务: {self.active_tasks}, 队列剩余: {len(self.task_queue)})")

    def _on_task_completed(self, processed_text, raw_text):
        """任务完成后的回调"""
        self.active_tasks -= 1
        self.total_completed += 1
        print(f"任务完成 (活跃任务: {self.active_tasks}, 完成数: {self.total_completed})")
        self.task_completed.emit(processed_text, raw_text)  # 转发结果给主窗口
        self._process_queue()  # 尝试处理下一个任务

    def get_stats(self):
        return {
            'active_tasks': self.active_tasks,
            'queue_size': len(self.task_queue),
            'total_submitted': self.total_submitted,
            'total_completed': self.total_completed,
            'max_threads': self.thread_pool.maxThreadCount(),
            'max_queue_size': self.max_queue_size
        }

    def clear_queue(self):
        self.task_queue.clear()

    def wait_for_completion(self, timeout=5000):
        return self.thread_pool.waitForDone(timeout)


class FloatingOCR(QtWidgets.QWidget):
    """
    主OCR应用程序窗口
    整合了 UI、配置、截图、OCR管理和字典管理
    """

    def __init__(self):
        super().__init__()
        self.sct = mss.mss()  # 初始化屏幕截图对象
        self.ocr_region = Config.OCR["DEFAULT_REGION"]
        self.auto_ocr_enabled = False
        self.auto_ocr_interval = Config.OCR["DEFAULT_INTERVAL"]
        self.auto_copy = False
        self.auto_save = False
        self.match_mode = 0
        self.similarity_threshold = 60
        self.translation_direction = "en_to_chs"  # 默认 英->中

        # === 核心修改：初始化 RapidOCR 引擎 ===
        # 只初始化一次，避免每次OCR都重新加载模型带来的巨大延迟
        try:
            print("正在初始化 RapidOCR 引擎...")
            # 优化参数说明：
            # 1. det_limit_side_len=960: 强制将 1720px 的宽度缩放至 960px 处理。
            #    对于游戏字幕，960px 宽度足够看清文字，且速度提升显著。
            # 2. intra_op_num_threads=4: 限制 ONNX Runtime 的并发线程数。
            #    如果不设置，它可能会占满 CPU 导致线程切换开销，反而变慢。建议设为 2 到 4。
            self.ocr_engine = RapidOCR(
                det_limit_side_len=960,
                det_limit_type='max',
                intra_op_num_threads=4
            )
            print("RapidOCR 引擎初始化完成")
        except Exception as e:
            print(f"RapidOCR 初始化失败: {e}")
            self.ocr_engine = None
        # ====================================

        self.sub_window = SubtitleWindow()  # 创建字幕悬浮窗
        self.current_game = list(Config.GAMES.keys())[0]
        self.text_map_loader = TextMapLoader(None, None, None)
        self.text_map_loader.update_paths(self.current_game)

        # 初始加载仍保持同步，确保启动后状态正确
        self.text_map = self.text_map_loader.load_text_map(self.translation_direction)
        self.text_matcher = TextMatcher(self.text_map, cache_size=3)

        self.task_manager = OCRTaskManager(max_threads=1, max_queue_size=1)
        self.task_manager.task_completed.connect(self.handle_ocr_result)
        self._drag_pos = None  # 用于窗口拖拽
        self.dict_worker = None  # 后台字典工作线程

        self.setup_ui()
        self.setup_timers_and_threads()

        # <--- [新增] 应用截图隐身模式
        # self.apply_stealth_mode()
        # ---------------------------

        # 绑定退出信号，确保资源释放
        QtWidgets.QApplication.instance().aboutToQuit.connect(self.cleanup)

    # <--- [新增] 隐身模式实现方法
    def apply_stealth_mode(self):
        """
        调用 Windows API 将此窗口从截图捕获中排除
        效果：肉眼可见，但截图/录屏时完全透明（穿透到背景）
        """
        if sys.platform != "win32":
            return

        try:
            # 获取 PySide6 窗口句柄并转为 int
            hwnd = int(self.winId())

            # 调用 user32.SetWindowDisplayAffinity
            result = ctypes.windll.user32.SetWindowDisplayAffinity(
                wintypes.HWND(hwnd),
                wintypes.DWORD(WDA_EXCLUDEFROMCAPTURE)
            )

            if result:
                print(f"[Main] 主窗口已设置为截图隐身 (HWND: {hwnd})")
            else:
                print("[Main] 主窗口隐身设置失败，可能是系统版本过低")

        except Exception as e:
            print(f"[Main] API 调用出错: {e}")
    # ---------------------------

    def setup_ui(self):
        """构建主窗口界面"""
        font = QtGui.QFont("Microsoft YaHei UI", 9)
        QtWidgets.QApplication.setFont(font)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # --- 标题栏 (保持不变) ---
        title_bar = QtWidgets.QHBoxLayout()
        title_lbl = QtWidgets.QLabel("OCR 工具 (1.6.5 Mod)")  # 稍微改个名区分一下
        title_lbl.setStyleSheet("font-weight:600; color: white; font-size:14px;")
        title_bar.addWidget(title_lbl)
        title_bar.addStretch()

        # === 最小化按钮 ===
        btn_minimize = QtWidgets.QPushButton("─")
        btn_minimize.setFixedSize(40, 30)
        btn_minimize.setStyleSheet(UIStyles.WINDOW_BTN_MIN)
        btn_minimize.clicked.connect(self.showMinimized)
        title_bar.addWidget(btn_minimize)

        # === 关闭按钮 ===
        btn_close = QtWidgets.QPushButton("✕")
        btn_close.setFixedSize(40, 30)
        btn_close.setStyleSheet(UIStyles.WINDOW_BTN_CLOSE)
        btn_close.clicked.connect(self.close)
        title_bar.addWidget(btn_close)

        main_layout.addLayout(title_bar)

        self.btn_toggle_sub = QtWidgets.QPushButton("开启字幕窗口")
        self.btn_toggle_sub.setCheckable(True)
        self.btn_toggle_sub.setStyleSheet(UIStyles.BUTTON_TOGGLE)
        self.btn_toggle_sub.clicked.connect(self.toggle_subtitle_window)
        main_layout.addWidget(self.btn_toggle_sub)

        # ==========================================================
        # === [修改] 字典配置区域 (合并了游戏选择、方向、加载和下载) ===
        # ==========================================================
        dict_group = QtWidgets.QGroupBox("字典配置")
        dict_group.setStyleSheet(UIStyles.GROUP_BOX)
        dict_layout = QtWidgets.QVBoxLayout()
        dict_layout.setSpacing(6)

        # 1. 游戏选择行
        row_game = QtWidgets.QHBoxLayout()
        row_game.addWidget(QtWidgets.QLabel("游戏:"))
        self.game_selector = QtWidgets.QComboBox()
        self.game_selector.addItems(Config.GAMES.keys())
        self.game_selector.setCurrentText(self.current_game)
        self.game_selector.currentIndexChanged.connect(self.on_game_changed)  # 仅更新变量
        self.game_selector.setStyleSheet(UIStyles.COMBO_BOX)
        self.game_selector.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        row_game.addWidget(self.game_selector)
        dict_layout.addLayout(row_game)

        # 2. 翻译方向行
        row_dir = QtWidgets.QHBoxLayout()
        row_dir.addWidget(QtWidgets.QLabel("方向:"))
        self.direction_combo = QtWidgets.QComboBox()
        self.direction_combo.addItems(["英 -> 中 (English to Chinese)", "中 -> 英 (Chinese to English)"])
        # 恢复上次记住的方向索引（如果有的话），这里默认逻辑不变
        if self.translation_direction == "chs_to_en":
            self.direction_combo.setCurrentIndex(1)
        else:
            self.direction_combo.setCurrentIndex(0)

        self.direction_combo.setStyleSheet(UIStyles.COMBO_BOX)
        self.direction_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.direction_combo.currentIndexChanged.connect(self.on_direction_changed)  # 仅更新变量
        row_dir.addWidget(self.direction_combo)
        dict_layout.addLayout(row_dir)

        # 3. 状态标签
        map_status_text = f"已加载 {len(self.text_map)} 条文本映射" if self.text_map else "文本映射未加载"
        self.map_status_label = QtWidgets.QLabel(map_status_text)
        self.map_status_label.setStyleSheet("color: lightgreen; font-size:10px;")
        self.map_status_label.setWordWrap(True)
        dict_layout.addWidget(self.map_status_label)

        # 4. 按钮行 (加载 & 下载)
        row_btns = QtWidgets.QHBoxLayout()

        # [新增] 加载字典按钮
        self.btn_load_map = QtWidgets.QPushButton("加载/重载字典")
        self.btn_load_map.setStyleSheet(UIStyles.BUTTON_Themed)  # 使用高亮样式
        self.btn_load_map.clicked.connect(self.reload_text_map)  # 绑定加载函数
        row_btns.addWidget(self.btn_load_map)

        # 下载按钮
        self.btn_download_map = QtWidgets.QPushButton("下载最新字典")
        self.btn_download_map.setStyleSheet(UIStyles.BUTTON_Dark)
        self.btn_download_map.clicked.connect(self.handle_download_map)
        row_btns.addWidget(self.btn_download_map)

        dict_layout.addLayout(row_btns)

        # 5. 进度条
        self.download_progress = QtWidgets.QProgressBar()
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(0)
        self.download_progress.setTextVisible(True)
        self.download_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid grey;
                border-radius: 3px;
                text-align: center;
                background-color: #2c3e50;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #409EFF;
                width: 10px;
            }
        """)
        self.download_progress.hide()
        dict_layout.addWidget(self.download_progress)

        dict_group.setLayout(dict_layout)
        main_layout.addWidget(dict_group)
        # ==========================================================

        # 匹配模式滑动条 (保持不变)
        match_group = QtWidgets.QGroupBox("文本匹配模式")
        match_group.setStyleSheet(UIStyles.GROUP_BOX)
        match_layout = QtWidgets.QHBoxLayout()
        self.match_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.match_slider.setRange(0, 2)
        self.match_slider.setValue(0)
        self.match_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.match_slider.setTickInterval(1)
        self.match_slider.valueChanged.connect(self.on_match_mode_changed)
        self.match_label = QtWidgets.QLabel("关闭")
        self.match_label.setFixedWidth(60)
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_label.setStyleSheet("color: white;")
        match_layout.addWidget(QtWidgets.QLabel("模式:"))
        match_layout.addWidget(self.match_slider)
        match_layout.addWidget(self.match_label)
        match_group.setLayout(match_layout)
        main_layout.addWidget(match_group)

        # 相似度阈值设置 (保持不变)
        threshold_group = QtWidgets.QGroupBox("相似度阈值")
        threshold_group.setStyleSheet(UIStyles.GROUP_BOX)
        threshold_layout = QtWidgets.QHBoxLayout()
        self.threshold_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(40, 100)
        self.threshold_slider.setValue(60)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        self.threshold_label = QtWidgets.QLabel("60%")
        self.threshold_label.setFixedWidth(40)
        self.threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.threshold_label.setStyleSheet("color: white;")
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_label)
        threshold_group.setLayout(threshold_layout)
        main_layout.addWidget(threshold_group)

        # 自动 OCR 设置 (保持不变)
        auto_ocr_group = QtWidgets.QGroupBox("自动OCR")
        auto_ocr_group.setStyleSheet(UIStyles.GROUP_BOX)
        auto_layout = QtWidgets.QHBoxLayout()
        self.auto_ocr_btn = QtWidgets.QPushButton("自动OCR: 关")
        self.auto_ocr_btn.setCheckable(True)
        self.auto_ocr_btn.clicked.connect(self.toggle_auto_ocr)
        self.interval_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(200, 5000)
        self.interval_slider.setValue(int(self.auto_ocr_interval * 1000))
        self.interval_slider.valueChanged.connect(self.on_interval_changed)
        self.interval_label = QtWidgets.QLabel(f"{self.auto_ocr_interval}秒")
        self.interval_label.setFixedWidth(40)
        auto_layout.addWidget(self.auto_ocr_btn)
        auto_layout.addWidget(self.interval_slider)
        auto_layout.addWidget(self.interval_label)
        auto_ocr_group.setLayout(auto_layout)
        main_layout.addWidget(auto_ocr_group)

        # 区域坐标设置 (保持不变)
        region_group = QtWidgets.QGroupBox("区域设置")
        region_group.setStyleSheet(UIStyles.GROUP_BOX)
        region_layout = QtWidgets.QGridLayout()
        labels = ["X坐标:", "Y坐标:", "宽度:", "高度:"]
        self.spin_boxes = []
        for i, label in enumerate(labels):
            region_layout.addWidget(QtWidgets.QLabel(label), i, 0)
            spin = QtWidgets.QSpinBox()
            spin.setRange(0, 5000)
            spin.setValue(self.ocr_region[i])
            region_layout.addWidget(spin, i, 1)
            self.spin_boxes.append(spin)
        self.btn_select_region = QtWidgets.QPushButton("框选区域")
        self.btn_select_region.clicked.connect(self.start_region_selection)
        region_layout.addWidget(self.btn_select_region, 4, 0, 1, 2)
        self.btn_set_region = QtWidgets.QPushButton("设置区域")
        self.btn_set_region.clicked.connect(self.update_region)
        region_layout.addWidget(self.btn_set_region, 5, 0, 1, 2)
        region_group.setLayout(region_layout)
        main_layout.addWidget(region_group)

        self.btn_ocr = QtWidgets.QPushButton("执行OCR")
        self.btn_ocr.clicked.connect(self.capture_and_submit_task)
        main_layout.addWidget(self.btn_ocr)

        btn_layout = QtWidgets.QHBoxLayout()
        self.auto_copy_btn = QtWidgets.QPushButton("自动复制: 关")
        self.auto_copy_btn.setCheckable(True)
        self.auto_copy_btn.clicked.connect(self.toggle_auto_copy)
        btn_layout.addWidget(self.auto_copy_btn)
        self.auto_save_btn = QtWidgets.QPushButton("自动保存: 关")
        self.auto_save_btn.setCheckable(True)
        self.auto_save_btn.clicked.connect(self.toggle_auto_save)
        btn_layout.addWidget(self.auto_save_btn)
        main_layout.addLayout(btn_layout)

        self.status_label = QtWidgets.QLabel("就绪")
        self.status_label.setStyleSheet("color: lightgray; font-size:10px;")
        self.status_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        self.setStyleSheet(UIStyles.MAIN_WINDOW + UIStyles.BUTTON_Themed + UIStyles.SPIN_BOX + UIStyles.SLIDER)
        self.resize(350, 700)
        self.move(50, 50)

    def setup_timers_and_threads(self):
        self.ocr_timer = QtCore.QTimer()
        self.ocr_timer.timeout.connect(self.capture_and_submit_task)

    # --- 优化点：使用后台线程处理字典任务 ---

    def set_ui_locked(self, locked):
        """锁定/解锁UI控件，防止任务期间重复操作"""
        self.game_selector.setEnabled(not locked)
        self.direction_combo.setEnabled(not locked)
        self.btn_download_map.setEnabled(not locked)
        self.btn_load_map.setEnabled(not locked)  # [新增] 锁定加载按钮
        self.btn_ocr.setEnabled(not locked)

    def handle_download_map(self):
        """[异步] 处理字典下载逻辑"""
        self.set_ui_locked(True)
        self.status_label.setText(f"正在准备下载 {self.current_game} 字典...")

        # <--- 新增：显示进度条并归零 ---
        self.download_progress.setValue(0)
        self.download_progress.show()
        # -----------------------------

        # 启动后台下载线程
        self.dict_worker = DictionaryWorker(self.text_map_loader, "download")
        self.dict_worker.progress_signal.connect(self.status_label.setText)

        # <--- 新增：连接进度信号到进度条 ---
        self.dict_worker.percent_signal.connect(self.download_progress.setValue)
        # -------------------------------

        self.dict_worker.finished_signal.connect(self.on_download_finished)
        self.dict_worker.start()

    def on_download_finished(self, success, msg):
        """下载完成回调"""
        self.set_ui_locked(False)
        self.status_label.setText(msg)

        # <--- 新增：隐藏进度条 ---
        self.download_progress.hide()
        # -----------------------

        if success:
            QtWidgets.QMessageBox.information(self, "下载完成", "字典下载成功，正在重新加载...")
            self.reload_text_map()  # 下载成功后自动重载
        else:
            QtWidgets.QMessageBox.warning(self, "下载失败", f"{msg}\n\n请检查网络连接。")

    def reload_text_map(self):
        """[异步] 统一的字典重载逻辑"""
        self.set_ui_locked(True)
        self.map_status_label.setText("正在加载/生成...")
        self.map_status_label.setStyleSheet("color: yellow; font-size:10px;")

        # 启动后台加载线程
        self.dict_worker = DictionaryWorker(self.text_map_loader, "load", self.translation_direction)
        self.dict_worker.progress_signal.connect(self.status_label.setText)
        self.dict_worker.map_loaded_signal.connect(self.on_map_loaded)
        self.dict_worker.finished_signal.connect(self.on_map_load_error)
        self.dict_worker.start()

    def on_map_loaded(self, text_map):
        """字典加载完成回调"""
        # 1. 更新主窗口持有的字典引用
        self.text_map = text_map

        # 2. 更新匹配器 (核心修改)
        # 必须调用 update_map 而不是直接赋值，以触发 candidates 列表的预生成
        if hasattr(self, 'text_matcher'):
            self.text_matcher.update_map(self.text_map)
            # 注意：update_map 内部已经包含了 clear_cache()，所以这里不用再手动调用

        # 3. 解锁 UI 并更新状态标签
        self.set_ui_locked(False)

        if self.text_map:
            # 根据当前的翻译方向显示提示
            direction_str = "英->中" if self.translation_direction == "en_to_chs" else "中->英"

            self.map_status_label.setText(f"[{direction_str}] 已加载 {len(self.text_map)} 条")
            self.map_status_label.setStyleSheet("color: lightgreen; font-size:10px;")
            self.status_label.setText("字典加载完成")
        else:
            self.map_status_label.setText("映射未加载，请下载字典")
            self.map_status_label.setStyleSheet("color: #ffb86c; font-size:10px;")
            self.status_label.setText("字典加载失败或为空")

    def on_map_load_error(self, success, msg):
        """字典加载错误回调"""
        self.set_ui_locked(False)
        self.status_label.setText(msg)
        if not success:
            self.map_status_label.setText("加载错误")
            self.map_status_label.setStyleSheet("color: red; font-size:10px;")

    # --------------------------------------

    def start_region_selection(self):
        self.status_label.setText("请框选区域 (ESC取消)")
        self.selection_overlay = SelectionOverlay()
        self.selection_overlay.selection_completed.connect(self.handle_region_selected)
        self.selection_overlay.show()

    def handle_region_selected(self, rect):
        self.spin_boxes[0].setValue(rect.x())
        self.spin_boxes[1].setValue(rect.y())
        self.spin_boxes[2].setValue(rect.width())
        self.spin_boxes[3].setValue(rect.height())
        self.ocr_region = (rect.x(), rect.y(), rect.width(), rect.height())
        self.status_label.setText(f"区域已框选: {rect.x()},{rect.y()} {rect.width()}x{rect.height()}")
        self.show_region_overlay()

    def on_match_mode_changed(self, value):
        modes = ["关闭", "完全匹配", "开头匹配"]
        self.match_mode = value
        self.match_label.setText(modes[value])
        self.status_label.setText(f"匹配模式: {modes[value]}")
        if hasattr(self, 'text_matcher'):
            self.text_matcher.clear_cache()

    def on_threshold_changed(self, value):
        self.similarity_threshold = value
        self.threshold_label.setText(f"{value}%")
        self.status_label.setText(f"相似度阈值: {value}%")
        if hasattr(self, 'text_matcher'):
            self.text_matcher.clear_cache()

    # ==========================================================
    # === [修改] 仅更新变量，移除自动加载逻辑 ===
    # ==========================================================
    def on_direction_changed(self, index):
        new_direction = "en_to_chs" if index == 0 else "chs_to_en"
        if new_direction == self.translation_direction:
            return
        self.translation_direction = new_direction

        # [修改] 仅更新状态提示，不自动加载
        dir_str = '英->中' if index == 0 else '中->英'
        self.status_label.setText(f"方向已变更为: {dir_str} (请点击加载按钮)")
        self.map_status_label.setText(f"待加载: {dir_str} (当前字典不匹配)")
        self.map_status_label.setStyleSheet("color: #ffb86c; font-size:10px;")

    def on_game_changed(self):
        self.current_game = self.game_selector.currentText()
        self.text_map_loader.update_paths(self.current_game)

        # [修改] 仅更新状态提示，不自动加载
        self.status_label.setText(f"游戏已变更为: {self.current_game} (请点击加载按钮)")
        self.map_status_label.setText(f"待加载: {self.current_game} (当前字典不匹配)")
        self.map_status_label.setStyleSheet("color: #ffb86c; font-size:10px;")

    # ==========================================================

    def toggle_auto_ocr(self):
        self.auto_ocr_enabled = not self.auto_ocr_enabled
        self.auto_ocr_btn.setChecked(self.auto_ocr_enabled)
        self.auto_ocr_btn.setText(f"自动OCR: {'开' if self.auto_ocr_enabled else '关'}")
        if self.auto_ocr_enabled:
            self.ocr_timer.start(int(self.auto_ocr_interval * 1000))
            self.status_label.setText(f"自动OCR已开启 ({self.auto_ocr_interval}秒/次)")
        else:
            self.ocr_timer.stop()
            self.status_label.setText("自动OCR已关闭")

    def capture_and_submit_task(self):
        """执行截图并提交 OCR 任务"""
        try:
            x, y, w, h = self.ocr_region

            # 组装截图区域数据（物理坐标）
            # --- 修改：只计算坐标，不进行截图操作 ---
            monitor = {
                "top": int(y),
                "left": int(x),
                "width": int(w),
                "height": int(h)
            }

            # 组装任务数据
            # --- 修改：传递 monitor 而非 img_cv ---
            task_data = {
                'monitor': monitor,  # 传递截图区域信息
                'text_matcher': self.text_matcher,
                'match_mode': self.match_mode,
                'similarity_threshold': self.similarity_threshold,
                'ocr_engine': self.ocr_engine
            }
            self.task_manager.submit_task(task_data)  # 提交到队列
            self.status_label.setText("OCR任务已提交")
        except Exception as e:
            self.status_label.setText(f"任务提交失败: {str(e)}")

    def toggle_subtitle_window(self, checked):
        if checked:
            self.sub_window.show()
            self.btn_toggle_sub.setText("隐藏字幕窗口")
        else:
            self.sub_window.hide()
            self.btn_toggle_sub.setText("开启字幕窗口")

    def handle_ocr_result(self, subtitle_text, status_info):
        """
        OCR完成后的回调函数，更新UI
        :param subtitle_text: 显示在字幕窗口的文本 (原词+翻译)
        :param status_info:   显示在状态栏的信息 (现在包含耗时统计)
        """
        # 1. 更新字幕窗口
        self.sub_window.update_text(subtitle_text)

        # 错误信息处理 (如果 subtitle_text 包含错误信息)
        if subtitle_text.startswith("[") and ("未识别" in subtitle_text or "错误" in subtitle_text):
            self.status_label.setText(subtitle_text.strip("[]"))
            return

        # 2. 更新主界面状态栏
        # --- 修改：不再获取当前系统时间，而是直接显示传入的耗时信息 ---
        if status_info:
            self.status_label.setText(status_info)
        else:
            self.status_label.setText("OCR完成")

        # 3. 自动功能处理
        if self.auto_copy:
            QtWidgets.QApplication.clipboard().setText(subtitle_text)
        if self.auto_save:
            with open(Config.PATHS["OUTPUT_FILE"], "a", encoding="utf-8") as f:
                f.write(f"\n---- {time.ctime()} ----\n{subtitle_text}\n")

    def update_region(self):
        """从输入框更新OCR区域"""
        x = self.spin_boxes[0].value()
        y = self.spin_boxes[1].value()
        w = self.spin_boxes[2].value()
        h = self.spin_boxes[3].value()
        if w < 10 or h < 10:
            self.status_label.setText("区域尺寸不能小于10像素")
            return
        self.ocr_region = (x, y, w, h)
        self.status_label.setText(f"区域已设置: {x},{y} {w}x{h}")
        self.show_region_overlay()

    def show_region_overlay(self):
        self.overlay = RegionOverlay(self.ocr_region)
        self.overlay.show()

    # --- 窗口拖拽逻辑 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def on_interval_changed(self, value):
        self.auto_ocr_interval = value / 1000.0
        self.interval_label.setText(f"{self.auto_ocr_interval:.1f}秒")
        if self.auto_ocr_enabled:
            self.ocr_timer.setInterval(value)
            self.status_label.setText(f"自动OCR间隔已更新: {self.auto_ocr_interval:.1f}秒")

    def toggle_auto_copy(self):
        self.auto_copy = not self.auto_copy
        self.auto_copy_btn.setChecked(self.auto_copy)
        self.auto_copy_btn.setText(f"自动复制: {'开' if self.auto_copy else '关'}")
        self.status_label.setText(f"自动复制: {'开' if self.auto_copy else '关'}")

    def toggle_auto_save(self):
        self.auto_save = not self.auto_save
        self.auto_save_btn.setChecked(self.auto_save)
        self.auto_save_btn.setText(f"自动保存: {'开' if self.auto_save else '关'}")
        self.status_label.setText(f"自动保存: {'开' if self.auto_save else '关'}")

    def cleanup(self):
        """资源清理"""
        self.sub_window.close()
        if hasattr(self, 'ocr_timer'):
            self.ocr_timer.stop()
        if hasattr(self, 'thread_pool'):
            self.thread_pool.waitForDone(2000)
        if hasattr(self, 'text_matcher'):
            self.text_matcher.clear_cache()
        if hasattr(self, 'sct'):
            self.sct.close()
        # 确保后台工作线程也退出
        if self.dict_worker and self.dict_worker.isRunning():
            self.dict_worker.quit()
            self.dict_worker.wait()
        print("资源清理完成，程序安全退出")


class SubtitleWindow(QtWidgets.QWidget):
    """
    独立的字幕显示窗口
    支持：鼠标拖拽移动、毛玻璃效果、无边框、自定义全向拉伸调整大小
    """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMouseTracking(True)  # 开启鼠标追踪以支持边缘检测

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.frame = QtWidgets.QFrame()
        self.frame.setObjectName("SubtitleFrame")
        self.frame.setMouseTracking(True)

        self.scroll_area = QtWidgets.QScrollArea(self.frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.label = QtWidgets.QLabel("等待 OCR 识别...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("background: transparent;")
        self.scroll_area.setWidget(self.label)

        self.frame_layout = QtWidgets.QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(10, 10, 10, 10)
        self.frame_layout.addWidget(self.scroll_area)

        # 右下角调整大小的手柄 (可视提示)
        self.size_grip = QtWidgets.QSizeGrip(self.frame)
        self.size_grip.setStyleSheet("background: transparent; width: 15px; height: 15px;")
        self.size_grip.setFixedSize(15, 15)

        self.layout.addWidget(self.frame)
        self.setStyleSheet(UIStyles.SUBTITLE_WINDOW)

        self.resize(1152, 150)
        self.setMinimumSize(80, 40)

        # 初始居中显示
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move((screen.width() - 1152) // 2, screen.height() - 200)

        self._drag_pos = None
        self._resize_mode = None
        self._resize_margin = 8  # 边缘检测距离

        # <--- [新增] 应用截图隐身模式
        # self.apply_stealth_mode()
        # ---------------------------

    # <--- [新增] 隐身模式实现方法
    def apply_stealth_mode(self):
        """
        调用 Windows API 将此窗口从截图捕获中排除
        """
        if sys.platform != "win32":
            return

        try:
            hwnd = int(self.winId())
            result = ctypes.windll.user32.SetWindowDisplayAffinity(
                wintypes.HWND(hwnd),
                wintypes.DWORD(WDA_EXCLUDEFROMCAPTURE)
            )

            if result:
                print(f"[Subtitle] 字幕窗口已设置为截图隐身 (HWND: {hwnd})")
            else:
                print("[Subtitle] 字幕窗口隐身设置失败")
        except Exception as e:
            print(f"[Subtitle] API 调用出错: {e}")
    # ---------------------------

    def update_text(self, text):
        self.label.setText(text)
        self.scroll_area.verticalScrollBar().setValue(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            # 保持 Grip 在右下角
            rect = self.frame.rect()
            self.size_grip.move(rect.right() - 15, rect.bottom() - 15)

    def _check_resize_area(self, pos):
        """检测鼠标是否位于窗口边缘，返回调整模式 (如 'top-left')"""
        rect = self.rect()
        x, y = pos.x(), pos.y()
        w, h = rect.width(), rect.height()
        m = self._resize_margin

        mode = []
        if y < m:
            mode.append("top")
        elif y > h - m:
            mode.append("bottom")
        if x < m:
            mode.append("left")
        elif x > w - m:
            mode.append("right")

        return "-".join(mode) if mode else None

    def _set_cursor_shape(self, mode):
        """根据鼠标位置改变光标形状"""
        if not mode:
            self.unsetCursor()
            return

        cursors = {
            "top": Qt.SizeVerCursor,
            "bottom": Qt.SizeVerCursor,
            "left": Qt.SizeHorCursor,
            "right": Qt.SizeHorCursor,
            "top-left": Qt.SizeFDiagCursor,
            "bottom-right": Qt.SizeFDiagCursor,
            "top-right": Qt.SizeBDiagCursor,
            "bottom-left": Qt.SizeBDiagCursor
        }
        self.setCursor(cursors.get(mode, Qt.ArrowCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 判断是调整大小还是拖动窗口
            mode = self._check_resize_area(event.position().toPoint())
            if mode:
                self._resize_mode = mode
                self._drag_pos = event.globalPosition().toPoint()
                event.accept()
            else:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        global_pos = event.globalPosition().toPoint()

        # 处理调整大小逻辑
        if self._resize_mode and self._drag_pos:
            rect = self.geometry()
            delta = global_pos - self._drag_pos
            self._drag_pos = global_pos

            new_geo = QRect(rect)
            dx, dy = delta.x(), delta.y()

            if "top" in self._resize_mode:
                new_h = max(self.minimumHeight(), rect.height() - dy)
                new_y = rect.y() + (rect.height() - new_h)
                new_geo.setTop(new_y)

            if "bottom" in self._resize_mode:
                new_geo.setHeight(max(self.minimumHeight(), rect.height() + dy))

            if "left" in self._resize_mode:
                new_w = max(self.minimumWidth(), rect.width() - dx)
                new_x = rect.x() + (rect.width() - new_w)
                new_geo.setLeft(new_x)

            if "right" in self._resize_mode:
                new_geo.setWidth(max(self.minimumWidth(), rect.width() + dx))

            self.setGeometry(new_geo)
            event.accept()
            return

        # 仅移动鼠标：更新光标样式
        if not event.buttons():
            mode = self._check_resize_area(pos)
            self._set_cursor_shape(mode)
            if mode:
                event.accept()
            return

        # 处理拖动窗口逻辑
        if self._drag_pos and not self._resize_mode:
            self.move(global_pos - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._resize_mode = None
        mode = self._check_resize_area(event.position().toPoint())
        self._set_cursor_shape(mode)
        event.accept()


if __name__ == "__main__":
    # --- 优化：开启高分屏支持 ---
    # 这对截图坐标的准确性至关重要
    # --------------------------

    app = QtWidgets.QApplication(sys.argv)
    window = FloatingOCR()
    window.show()
    sys.exit(app.exec())