# OCR引擎已替换为 RapidOCR (极速版)

import sys
import os
import time
import orjson  # 用于快速读取
import mss
import mss.tools
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QRect
from rapidocr_onnxruntime import RapidOCR  # <-- 新增：极速OCR引擎
import cv2
import numpy as np
from rapidfuzz import process, fuzz

# ====== 配置与样式封装 ======

# 路径计算
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # 上一级目录


class Config:
    """全局配置管理"""
    PATHS = {
        # "TESSERACT": ... <-- 已移除，不再需要外部依赖路径
        "TEXTMAP_ROOT": os.path.join(PROJECT_ROOT, "TextMap"),
        "TEXTMAP_MERGED_ROOT": os.path.join(PROJECT_ROOT, "TextMap_KeyLan"),
        "OUTPUT_FILE": os.path.join(PROJECT_ROOT, "OCR_Results.txt")
    }

    OCR = {
        "DEFAULT_REGION": (100, 810, 1720, 240),
        "DEFAULT_INTERVAL": 2.0,
    }

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
    """UI样式统一管理"""
    MAIN_WINDOW = """
        QWidget {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #2c3e50, stop:1 #34495e);
            border-radius: 12px;
        }
    """
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
    WINDOW_OP_BUTTON = "QPushButton{background:transparent;color:white;border:none;} QPushButton:hover{color:#ff8080}"
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


# =====================
# 初始化Tesseract (已删除)
# pytesseract.pytesseract.tesseract_cmd = Config.PATHS["TESSERACT"]


class SubtitleWindow(QtWidgets.QWidget):
    """独立的字幕显示窗口，支持拖动、毛玻璃、滚动条及【全向边缘调整大小】"""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMouseTracking(True)

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

        self.size_grip = QtWidgets.QSizeGrip(self.frame)
        self.size_grip.setStyleSheet("background: transparent; width: 15px; height: 15px;")
        self.size_grip.setFixedSize(15, 15)

        self.layout.addWidget(self.frame)
        self.setStyleSheet(UIStyles.SUBTITLE_WINDOW)

        self.resize(1152, 150)
        self.setMinimumSize(300, 100)

        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move((screen.width() - 1152) // 2, screen.height() - 200)

        self._drag_pos = None
        self._resize_mode = None
        self._resize_margin = 8

    def update_text(self, text):
        self.label.setText(text)
        self.scroll_area.verticalScrollBar().setValue(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            rect = self.frame.rect()
            self.size_grip.move(rect.right() - 15, rect.bottom() - 15)

    def _check_resize_area(self, pos):
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

        if not event.buttons():
            mode = self._check_resize_area(pos)
            self._set_cursor_shape(mode)
            if mode:
                event.accept()
            return

        if self._drag_pos and not self._resize_mode:
            self.move(global_pos - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._resize_mode = None
        mode = self._check_resize_area(event.position().toPoint())
        self._set_cursor_shape(mode)
        event.accept()


class DictionaryWorker(QtCore.QThread):
    progress_signal = QtCore.Signal(str)
    finished_signal = QtCore.Signal(bool, str)
    map_loaded_signal = QtCore.Signal(dict)

    def __init__(self, loader, task_type, direction=None):
        super().__init__()
        self.loader = loader
        self.task_type = task_type
        self.direction = direction

    def run(self):
        if self.task_type == "download":
            success, msg = self.loader.download_files(self.progress_signal.emit)
            self.finished_signal.emit(success, msg)
        elif self.task_type == "load":
            try:
                self.progress_signal.emit(f"正在加载/生成 {self.direction} 字典...")
                data = self.loader.load_text_map(self.direction)
                self.map_loaded_signal.emit(data)
            except Exception as e:
                self.finished_signal.emit(False, f"加载失败: {str(e)}")


class TextMapLoader:
    def __init__(self, textmap_dir, textmap_merged_dir, textmap_file):
        self.textmap_dir = textmap_dir
        self.textmap_merged_dir = textmap_merged_dir
        self.default_textmap_file = textmap_file
        self.current_urls = {}

    def update_paths(self, game_key):
        config = Config.GAMES[game_key]
        base_dir = os.path.join(PROJECT_ROOT, config["folder"])
        self.textmap_dir = os.path.join(base_dir, "TextMap")
        self.textmap_merged_dir = os.path.join(base_dir, "TextMap_KeyLan")
        self.default_textmap_file = os.path.join(self.textmap_merged_dir, "TextMapEN_CHS.json")
        self.current_urls = config["urls"]

    def download_files(self, progress_callback=None):
        import urllib.request
        os.makedirs(self.textmap_dir, exist_ok=True)
        try:
            for file_name, url in self.current_urls.items():
                target_path = os.path.join(self.textmap_dir, file_name)
                if progress_callback:
                    progress_callback(f"正在下载 {file_name}...")
                urllib.request.urlretrieve(url, target_path)
            return True, "下载完成"
        except Exception as e:
            return False, f"下载失败: {str(e)}"

    def load_text_map(self, direction="en_to_chs"):
        os.makedirs(self.textmap_merged_dir, exist_ok=True)
        file_name = "TextMapEN_CHS.json" if direction == "en_to_chs" else "TextMapCHS_EN.json"
        target_file = os.path.join(self.textmap_merged_dir, file_name)

        if os.path.exists(target_file):
            try:
                with open(target_file, 'rb') as f:
                    text_map = orjson.loads(f.read())
                    print(f"[{direction}] 已加载映射文件，包含 {len(text_map)} 条记录")
                    return text_map
            except Exception as e:
                print(f"加载映射文件失败: {e}")

        en_file = os.path.join(self.textmap_dir, "TextMapEN.json")
        chs_file = os.path.join(self.textmap_dir, "TextMapCHS.json")

        if not os.path.exists(en_file) or not os.path.exists(chs_file):
            print("原始文本映射文件不存在，跳过文本匹配功能")
            return {}

        print(f"正在生成 {direction} 映射文件，请稍候...")
        try:
            with open(en_file, 'rb') as f:
                en_data = orjson.loads(f.read())
            with open(chs_file, 'rb') as f:
                chs_data = orjson.loads(f.read())

            merged_data = {}
            for key in en_data.keys():
                if key in chs_data:
                    en_text = en_data[key].replace('\\n', ' ').strip()
                    chs_text = chs_data[key].replace('\\n', ' ').strip()
                    if not en_text or not chs_text:
                        continue
                    if direction == "en_to_chs":
                        merged_data[en_text] = chs_text
                    else:
                        merged_data[chs_text] = en_text

            with open(target_file, 'wb') as f:
                f.write(orjson.dumps(merged_data, option=orjson.OPT_INDENT_2))

            print(f"[{direction}] 映射文件已生成: {target_file}")
            return merged_data

        except Exception as e:
            print(f"生成文本映射文件失败: {e}")
            return {}


class SelectionOverlay(QtWidgets.QWidget):
    selection_completed = QtCore.Signal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.start_point = None
        self.end_point = None
        self.selecting = False
        self.setCursor(Qt.CursorShape.CrossCursor)

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.setFocus()
        self.raise_()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(100, 100, 100, 150))
        if self.selecting and self.start_point and self.end_point:
            selection_rect = QtCore.QRect(self.start_point, self.end_point).normalized()
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection_rect, QtGui.QColor(0, 0, 0, 0))
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QtGui.QPen(QtGui.QColor(0, 120, 255), 2)
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.end_point = event.position().toPoint()
            self.selecting = False
            selected_rect = QtCore.QRect(self.start_point, self.end_point).normalized()
            self.selection_completed.emit(selected_rect)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)


class RegionOverlay(QtWidgets.QWidget):
    def __init__(self, region):
        super().__init__()
        self.region = region
        self.setup_ui()

    def setup_ui(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowType.Tool)
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        QtCore.QTimer.singleShot(500, self.close)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 100))
        x, y, w, h = self.region
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(x, y, w, h, QtGui.QColor(0, 0, 0, 0))
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
        pen = QtGui.QPen(QtGui.QColor(0, 180, 255), 3)
        painter.setPen(pen)
        painter.drawRect(x, y, w, h)


class OCRWorker(QtCore.QRunnable):
    class Signals(QtCore.QObject):
        finished = QtCore.Signal(str, str)

    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data
        self.signals = self.Signals()

    def run(self):
        try:
            img_cv = self.task_data.get('img_cv')
            # language = self.task_data.get('language', Config.OCR["LANGUAGE"]) # RapidOCR 自动识别中英文，无需手动指定
            text_matcher = self.task_data.get('text_matcher')
            match_mode = self.task_data.get('match_mode', 0)
            similarity_threshold = self.task_data.get('similarity_threshold', 85)
            ocr_engine = self.task_data.get('ocr_engine')  # 获取引擎实例

            if img_cv is None:
                raise ValueError("Image data is missing")

            if ocr_engine is None:
                raise ValueError("OCR Engine not initialized")

            # RapidOCR 对原图支持很好，通常不需要 Tesseract 那种强力的 Thresholding
            # 直接使用 OpenCV 格式的图片即可
            raw_text = self.run_rapidocr(ocr_engine, img_cv)

            if not raw_text or raw_text.strip() == "":
                self.signals.finished.emit("[未识别到文本]", "")
                return

            processed_text = self.process_text_with_matching(
                raw_text, text_matcher, match_mode, similarity_threshold
            )
            self.signals.finished.emit(processed_text, raw_text)

        except Exception as e:
            self.signals.finished.emit(f"[OCR错误] {str(e)}", "")

    def run_rapidocr(self, engine, img):
        # rapidocr_onnxruntime 调用方式: result, elapse = engine(img)
        # result 格式: [[box, text, score], [box, text, score], ...]
        result, _ = engine(img)

        if result:
            # 将所有识别到的文本行拼接起来，用换行符分隔
            text_list = [line[1] for line in result]
            return "\n".join(text_list).strip()
        return ""

    def process_text_with_matching(self, ocr_text, text_matcher, match_mode, similarity_threshold):
        if (match_mode == 0 or not ocr_text or
                ocr_text.startswith("[") or not text_matcher or
                not text_matcher.text_map):
            return ocr_text

        matched_key, matched_chinese, similarity = text_matcher.match_text(
            ocr_text, match_mode, similarity_threshold
        )

        if matched_key and matched_chinese:
            output = f"{matched_key}\n{matched_chinese}\n[匹配成功 - 相似度: {similarity}%]"
            return output

        return ocr_text


class TextMatcher:
    def __init__(self, text_map, cache_size=100):
        self.text_map = text_map
        self.cache = {}
        self.cache_size = cache_size
        self.hits = 0
        self.misses = 0

    def match_text(self, ocr_text, mode, threshold):
        if mode == 0 or not ocr_text or not self.text_map:
            return None, None, 0

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

    def _match_full_text(self, ocr_text, similarity_threshold=85):
        if not self.text_map or not ocr_text.strip():
            return None, None, 0
        if ocr_text in self.text_map:
            return ocr_text, self.text_map[ocr_text], 100
        candidates = list(self.text_map.keys())
        result = process.extractOne(
            ocr_text, candidates, scorer=fuzz.QRatio, score_cutoff=similarity_threshold
        )
        if result:
            best_match, score, _ = result
            return best_match, self.text_map[best_match], score
        return None, None, 0

    def _match_prefix_text(self, ocr_prefix, similarity_threshold=90):
        if not self.text_map or len(ocr_prefix.strip()) < 3:
            return None, None, 0
        prefix_length = len(ocr_prefix)
        prefix_candidates = {}
        for key in self.text_map.keys():
            if len(key) >= prefix_length:
                truncated_key = key[:prefix_length]
                prefix_candidates[truncated_key] = key
        if not prefix_candidates:
            return None, None, 0
        result = process.extractOne(
            ocr_prefix, list(prefix_candidates.keys()), scorer=fuzz.QRatio, score_cutoff=similarity_threshold
        )
        if result:
            best_truncated, score, _ = result
            best_match = prefix_candidates[best_truncated]
            return best_match, self.text_map[best_match], score
        return None, None, 0

    def clear_cache(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_cache_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache)
        }


class OCRTaskManager(QtCore.QObject):
    task_completed = QtCore.Signal(str, str)

    def __init__(self, max_threads=1, max_queue_size=1):
        super().__init__()
        self.thread_pool = QtCore.QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(max_threads)
        self.task_queue = []
        self.max_queue_size = max_queue_size
        self.active_tasks = 0
        self.total_submitted = 0
        self.total_completed = 0

    def submit_task(self, task_data):
        if len(self.task_queue) >= self.max_queue_size:
            removed_task = self.task_queue.pop(0)
            print(f"队列已满，移除旧任务 (队列大小: {len(self.task_queue)})")
        self.task_queue.append(task_data)
        self.total_submitted += 1
        print(f"任务已提交 (队列大小: {len(self.task_queue)}, 活跃任务: {self.active_tasks})")
        self._process_queue()

    def _process_queue(self):
        idle_threads = self.thread_pool.maxThreadCount() - self.active_tasks
        while idle_threads > 0 and self.task_queue:
            task_data = self.task_queue.pop(0)
            worker = OCRWorker(task_data)
            worker.signals.finished.connect(self._on_task_completed)
            self.thread_pool.start(worker)
            self.active_tasks += 1
            idle_threads -= 1
            print(f"启动新任务 (活跃任务: {self.active_tasks}, 队列剩余: {len(self.task_queue)})")

    def _on_task_completed(self, processed_text, raw_text):
        self.active_tasks -= 1
        self.total_completed += 1
        print(f"任务完成 (活跃任务: {self.active_tasks}, 完成数: {self.total_completed})")
        self.task_completed.emit(processed_text, raw_text)
        self._process_queue()

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
    """主OCR应用程序窗口"""

    def __init__(self):
        super().__init__()
        self.sct = mss.mss()
        self.ocr_region = Config.OCR["DEFAULT_REGION"]
        self.auto_ocr_enabled = False
        self.auto_ocr_interval = Config.OCR["DEFAULT_INTERVAL"]
        self.auto_copy = False
        self.auto_save = False
        self.match_mode = 0
        self.similarity_threshold = 85
        self.translation_direction = "en_to_chs"  # 默认 英->中

        # === 核心修改：初始化 RapidOCR 引擎 ===
        # 只初始化一次，避免重复加载模型带来的延迟
        try:
            print("正在初始化 RapidOCR 引擎...")
            self.ocr_engine = RapidOCR()
            print("RapidOCR 引擎初始化完成")
        except Exception as e:
            print(f"RapidOCR 初始化失败: {e}")
            self.ocr_engine = None
        # ====================================

        self.sub_window = SubtitleWindow()
        self.current_game = list(Config.GAMES.keys())[0]
        self.text_map_loader = TextMapLoader(None, None, None)
        self.text_map_loader.update_paths(self.current_game)

        # 初始加载仍保持同步，确保启动后状态正确
        self.text_map = self.text_map_loader.load_text_map(self.translation_direction)
        self.text_matcher = TextMatcher(self.text_map, cache_size=100)

        self.task_manager = OCRTaskManager(max_threads=1, max_queue_size=1)
        self.task_manager.task_completed.connect(self.handle_ocr_result)
        self._drag_pos = None
        self.dict_worker = None  # 后台字典工作线程

        self.setup_ui()
        self.setup_timers_and_threads()
        QtWidgets.QApplication.instance().aboutToQuit.connect(self.cleanup)

    def setup_ui(self):
        font = QtGui.QFont("Microsoft YaHei UI", 9)
        QtWidgets.QApplication.setFont(font)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        title_bar = QtWidgets.QHBoxLayout()
        title_lbl = QtWidgets.QLabel("OCR 工具 (RapidOCR)")
        title_lbl.setStyleSheet("font-weight:600; color: white; font-size:14px;")
        title_bar.addWidget(title_lbl)
        title_bar.addStretch()
        btn_minimize = QtWidgets.QPushButton("─")
        btn_minimize.setFixedSize(24, 24)
        btn_minimize.setStyleSheet(UIStyles.WINDOW_OP_BUTTON)
        btn_minimize.clicked.connect(self.showMinimized)
        title_bar.addWidget(btn_minimize)
        btn_close = QtWidgets.QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet(UIStyles.WINDOW_OP_BUTTON)
        btn_close.clicked.connect(self.close)
        title_bar.addWidget(btn_close)
        main_layout.addLayout(title_bar)

        self.btn_toggle_sub = QtWidgets.QPushButton("开启字幕窗口")
        self.btn_toggle_sub.setCheckable(True)
        self.btn_toggle_sub.setStyleSheet(UIStyles.BUTTON_TOGGLE)
        self.btn_toggle_sub.clicked.connect(self.toggle_subtitle_window)
        main_layout.addWidget(self.btn_toggle_sub)

        match_status_group = QtWidgets.QGroupBox("文本匹配状态")
        match_status_group.setStyleSheet(UIStyles.GROUP_BOX)
        status_layout = QtWidgets.QVBoxLayout()
        map_status_text = f"已加载 {len(self.text_map)} 条文本映射" if self.text_map else "文本映射未加载"
        self.map_status_label = QtWidgets.QLabel(map_status_text)
        self.map_status_label.setStyleSheet("color: lightgreen; font-size:10px;")

        self.game_selector = QtWidgets.QComboBox()
        self.game_selector.addItems(Config.GAMES.keys())
        self.game_selector.setCurrentText(self.current_game)
        self.game_selector.currentIndexChanged.connect(self.on_game_changed)
        self.game_selector.setStyleSheet(UIStyles.COMBO_BOX)
        status_layout.addWidget(QtWidgets.QLabel("当前游戏项目:"))
        status_layout.addWidget(self.game_selector)

        direction_group = QtWidgets.QGroupBox("翻译方向")
        direction_group.setStyleSheet(UIStyles.GROUP_BOX)
        dir_layout = QtWidgets.QHBoxLayout()
        self.direction_combo = QtWidgets.QComboBox()
        self.direction_combo.addItems(["英 -> 中 (English to Chinese)", "中 -> 英 (Chinese to English)"])
        self.direction_combo.setStyleSheet(UIStyles.COMBO_BOX)
        self.direction_combo.currentIndexChanged.connect(self.on_direction_changed)
        dir_layout.addWidget(self.direction_combo)
        direction_group.setLayout(dir_layout)
        main_layout.addWidget(direction_group)

        self.btn_download_map = QtWidgets.QPushButton("下载最新字典 (GitLab)")
        self.btn_download_map.setStyleSheet(UIStyles.BUTTON_Dark)
        status_layout.addWidget(self.btn_download_map)
        self.btn_download_map.clicked.connect(self.handle_download_map)
        match_status_group.setLayout(status_layout)
        main_layout.addWidget(match_status_group)

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

        threshold_group = QtWidgets.QGroupBox("相似度阈值")
        threshold_group.setStyleSheet(UIStyles.GROUP_BOX)
        threshold_layout = QtWidgets.QHBoxLayout()
        self.threshold_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(40, 100)
        self.threshold_slider.setValue(85)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        self.threshold_label = QtWidgets.QLabel("85%")
        self.threshold_label.setFixedWidth(40)
        self.threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.threshold_label.setStyleSheet("color: white;")
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_label)
        threshold_group.setLayout(threshold_layout)
        main_layout.addWidget(threshold_group)

        auto_ocr_group = QtWidgets.QGroupBox("自动OCR")
        auto_ocr_group.setStyleSheet(UIStyles.GROUP_BOX)
        auto_layout = QtWidgets.QHBoxLayout()
        self.auto_ocr_btn = QtWidgets.QPushButton("自动OCR: 关")
        self.auto_ocr_btn.setCheckable(True)
        self.auto_ocr_btn.clicked.connect(self.toggle_auto_ocr)
        self.interval_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(500, 5000)
        self.interval_slider.setValue(int(self.auto_ocr_interval * 1000))
        self.interval_slider.valueChanged.connect(self.on_interval_changed)
        self.interval_label = QtWidgets.QLabel(f"{self.auto_ocr_interval}秒")
        self.interval_label.setFixedWidth(40)
        auto_layout.addWidget(self.auto_ocr_btn)
        auto_layout.addWidget(self.interval_slider)
        auto_layout.addWidget(self.interval_label)
        auto_ocr_group.setLayout(auto_layout)
        main_layout.addWidget(auto_ocr_group)

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
        self.btn_ocr.setEnabled(not locked)

    def handle_download_map(self):
        """[异步] 处理字典下载逻辑"""
        self.set_ui_locked(True)
        self.status_label.setText(f"正在准备下载 {self.current_game} 字典...")

        # 启动后台下载线程
        self.dict_worker = DictionaryWorker(self.text_map_loader, "download")
        self.dict_worker.progress_signal.connect(self.status_label.setText)
        self.dict_worker.finished_signal.connect(self.on_download_finished)
        self.dict_worker.start()

    def on_download_finished(self, success, msg):
        """下载完成回调"""
        self.set_ui_locked(False)
        self.status_label.setText(msg)
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
        self.text_map = text_map
        # 更新匹配器
        if hasattr(self, 'text_matcher'):
            self.text_matcher.text_map = self.text_map
            self.text_matcher.clear_cache()

        # 更新UI状态
        self.set_ui_locked(False)
        if self.text_map:
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

    def on_direction_changed(self, index):
        new_direction = "en_to_chs" if index == 0 else "chs_to_en"
        if new_direction == self.translation_direction:
            return
        self.translation_direction = new_direction
        self.status_label.setText(f"正在切换方向至: {'英->中' if index == 0 else '中->英'}...")
        # 调用异步加载
        self.reload_text_map()

    def on_game_changed(self):
        self.current_game = self.game_selector.currentText()
        self.status_label.setText(f"切换至: {self.current_game}")
        self.text_map_loader.update_paths(self.current_game)
        # 调用异步加载
        self.reload_text_map()

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
        try:
            x, y, w, h = self.ocr_region
            monitor = {"top": y, "left": x, "width": w, "height": h}
            sct_img = self.sct.grab(monitor)
            img_np = np.array(sct_img)
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            task_data = {
                'img_cv': img_cv,
                # 'language': Config.OCR["LANGUAGE"], # RapidOCR 自动处理
                'text_matcher': self.text_matcher,
                'match_mode': self.match_mode,
                'similarity_threshold': self.similarity_threshold,
                'ocr_engine': self.ocr_engine  # 传递引擎实例
            }
            self.task_manager.submit_task(task_data)
            self.status_label.setText("OCR任务已提交")
        except Exception as e:
            self.status_label.setText(f"截图失败: {str(e)}")

    def toggle_subtitle_window(self, checked):
        if checked:
            self.sub_window.show()
            self.btn_toggle_sub.setText("隐藏字幕窗口")
        else:
            self.sub_window.hide()
            self.btn_toggle_sub.setText("开启字幕窗口")

    def handle_ocr_result(self, processed_text, raw_text):
        self.sub_window.update_text(processed_text)
        if processed_text.startswith("[") and ("未识别" in processed_text or "错误" in processed_text):
            self.status_label.setText(processed_text.strip("[]"))
            return
        self.status_label.setText(f"OCR完成 ({time.strftime('%H:%M:%S')})")
        if self.auto_copy:
            QtWidgets.QApplication.clipboard().setText(processed_text)
        if self.auto_save:
            with open(Config.PATHS["OUTPUT_FILE"], "a", encoding="utf-8") as f:
                f.write(f"\n---- {time.ctime()} ----\n{processed_text}\n")

    def update_region(self):
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


if __name__ == "__main__":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    window = FloatingOCR()
    window.show()
    sys.exit(app.exec())