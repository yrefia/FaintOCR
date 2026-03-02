### 解析代码的两个方法：从UI(用户点击)入手；从功能(哪里用到)入手
## 注意：该版本需要在python3.12下运行

# 重构了FloatingOCR类为MVC架构

# 规范了FloatingOCR的setup_ui中对初始游戏和初始语言的定义
# 修复了新版本中点击一键生成后不禁用一键生成按钮的问题,以及防抖加载功能跳跃的问题

# 重构了状态机间通信的信号方式，引入了状态指示灯
# 耦合了ui锁定与进度条生命周期，简化了逻辑
# 解决了在准备加载的2.4秒防抖定时时，界面会一直显示准备加载的问题；将"FloatingOCR"的"on_dict_error"与"update_dict_ui_state"合并；进度条先100再隐藏，更换了图标⚠️
# 重新编排了FloatingOCR中各个方法在代码中的物理位置

# 3.
# 加入了进度文本的I18n国际化支持
# 删除了handle_task末尾的完成进度报告

# 加入了全局I18n国际化语言支持
# 修复了加入loguru后点击关闭程序不会正常退出的问题
# 调整了loguru日志文件等级为TRACE；现在合并文本失败也有报错了
# 修复了打包成exe后loguru找不到控制台输出而报错的问题
# 修复了I18n"missing_more"本地化歧义的问题

# 全面扩充 I18n 字典，现在绝大部分文本都经过I18n

# 6.
# 加入了隐身模式在win10上的兼容:问题由透明背景导致，先设置隐身再设置透明背景会导致透明背景失效，需要先设置透明背景然后设置隐身模式时移除窗口样式再添加回来



import re
import sys
import os
import time
import ctypes
from ctypes import wintypes
import orjson
import mss
import mss.tools
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QRect
from rapidocr_onnxruntime import RapidOCR
import cv2
import numpy as np
from rapidfuzz import process, fuzz
import requests
from loguru import logger  # <--- [新增]
from enum import Enum


# ====== 路径获取逻辑修正 ======
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe 运行，使用 exe 所在的实际目录
    # sys.executable 指向 D:\xxx\xxx.exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是普通脚本运行，使用当前文件所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 现在的 BASE_DIR 就是你希望存放数据的根目录（即 .exe 所在的 D 盘目录）


# ====== [新增] 日志配置函数 ======
def setup_logging():
    # 1. 创建日志目录
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    # 2. 清除默认处理程序
    logger.remove()
    # 3. 控制台输出 (仅在控制台存在时启用，防止打包 -w 参数导致 NoneType 报错)
    if sys.stderr is not None:
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>"
        )
    # 4. 文件输出 (详细记录 DEBUG，按天切割，保留10天，异步写入)
    logger.add(
        os.path.join(log_dir, "runtime_{time:YYYY-MM-DD}.log"),
        rotation="00:00",      # 每天午夜轮转
        retention="3 days",   # 只保留3天
        compression="zip",     # 压缩旧日志
        level="TRACE",
        encoding="utf-8",
        enqueue=True,          # [关键] 异步写入，防止阻塞 UI/OCR 线程
        backtrace=True,
        diagnose=True
    )
    logger.info("日志系统初始化完成")

class DictState(Enum):
    STANDBY = 0  # 待机
    READY = 1    # 就绪
    PENDING = 2  # ⏳ 即将加载 (新增：用于防抖倒计时的 2.4 秒)
    LOADING = 3  # 🟡 加载/生成中
    MISSING = 4  # 🔴 文件缺失
    ERROR = 5    # ⚠️ 严重错误


class I18n:
    """UI 多语言本地化词典 (全量支持)"""
    current_lang = "zh_CN"

    TEXT = {
        "zh_CN": {
            # --- 1. 后台进度文本 ---
            "prog_downloading_raw": "🟡 正在下载缺失源文件 ({0}个)...",
            "prog_downloading_file": "🟡 正在下载: {0}{1}...",
            "prog_generating_map": "🟡 正在生成合并字典...",
            "prog_preparing_tokens": "🟡 正在预处理分词数据...",
            "prog_generating_prefix": "🟡 正在生成索引 (Tk{0})...",

            # --- 2. 状态机 (DictState) 文本 ---
            "state_standby": "⚪ 待机 (匹配模式已关闭)",
            "state_ready": "🟢 字典已就绪 (Level {0})",
            "state_pending": "⏳ 即将加载... ({0} ➔ {1})",
            "state_loading": "🟡 正在处理中... ({0} ➔ {1})",
            "state_missing": "🔴 缺失: {0}",
            "state_error": "⚠️ 操作失败 (请看悬停提示)",

            "missing_more": "{0} 及另外 {1} 个文件",  # [修复] 消除中英文语义歧义
            "tooltip_missing": "缺失文件列表:\n{0}",
            "tooltip_error": "错误详情:\n{0}",

            "btn_generate": "一键生成",
            "btn_ready": "已就绪",
            "btn_load_now": "立即加载",
            "btn_processing": "处理中...",
            "btn_retry": "重试",

            # --- 3. UI 界面固定文本 (setup_ui) ---
            "ui_title": "FaintOCR(1.10.4)",
            "ui_btn_sub_show": "开启字幕窗口",
            "ui_btn_sub_hide": "隐藏字幕窗口",
            "ui_grp_dict": "字典配置",
            "ui_lbl_game": "游戏:",
            "ui_lbl_source": "源:",
            "ui_lbl_target": "译:",
            "ui_map_init": "等待检查...",
            "ui_btn_fix_init": "一键修复/初始化",
            "ui_grp_match": "文本匹配模式",
            "ui_lbl_mode": "模式:",
            "ui_mode_0": "关闭",
            "ui_mode_1": "完全匹配",
            "ui_mode_2": "开头匹配",
            "ui_grp_threshold": "相似度阈值",
            "ui_grp_auto_ocr": "自动OCR",
            "ui_btn_auto_ocr_on": "自动OCR: 开",
            "ui_btn_auto_ocr_off": "自动OCR: 关",
            "ui_grp_region": "区域设置",
            "ui_btn_sel_region": "框选区域",
            "ui_btn_show_region": "显示当前区域",
            "ui_btn_ocr": "执行OCR",
            "ui_btn_auto_copy_on": "自动复制: 开",
            "ui_btn_auto_copy_off": "自动复制: 关",
            "ui_btn_auto_save_on": "自动保存: 开",
            "ui_btn_auto_save_off": "自动保存: 关",
            "ui_status_ready": "就绪",

            # --- 4. 交互反馈与字幕窗口 ---
            "sub_waiting": "等待 OCR 识别...",
            "status_threshold": "相似度阈值: {0}%",
            "status_ocr_submit": "OCR任务已提交",
            "status_sel_region": "请框选区域 (ESC取消)",
            "status_region_ok": "区域已框选: {0},{1} {2}x{3}",
            "status_auto_ocr_on": "自动OCR已开启 ({0:.1f}秒/次)",  # [修复] 统一浮点数格式
            "status_auto_ocr_off": "自动OCR已关闭",
            "status_interval": "自动OCR间隔已更新: {0:.1f}秒",

            # --- 5. [新增] OCR 动态状态与后端报错 ---
            "status_perf": "截图: {0:.3f}s | OCR: {1:.3f}s | 匹配: {2:.3f}s",
            "status_perf_sim": "{0} | 相似度: {1}%",
            "status_no_text": "未识别到文本",
            "status_ocr_error": "OCR执行出错: {0}",
            "err_cancelled": "操作已取消",
            "err_download_fail": "下载失败: {0}",
        },
        "en_US": {
            # --- 1. Background Progress ---
            "prog_downloading_raw": "🟡 Downloading raw files ({0})...",
            "prog_downloading_file": "🟡 Downloading: {0}{1}...",
            "prog_generating_map": "🟡 Generating merged dictionary...",
            "prog_preparing_tokens": "🟡 Preparing tokenizer data...",
            "prog_generating_prefix": "🟡 Generating prefix index (Tk{0})...",

            # --- 2. State Machine ---
            "state_standby": "⚪ Standby (Match mode off)",
            "state_ready": "🟢 Dictionary Ready (Level {0})",
            "state_pending": "⏳ Loading soon... ({0} ➔ {1})",
            "state_loading": "🟡 Processing... ({0} ➔ {1})",
            "state_missing": "🔴 Missing: {0}",
            "state_error": "⚠️ Operation failed (See tooltip)",

            "missing_more": "{0} and {1} more",
            "tooltip_missing": "Missing Files:\n{0}",
            "tooltip_error": "Error Details:\n{0}",

            "btn_generate": "Generate",
            "btn_ready": "Ready",
            "btn_load_now": "Load Now",
            "btn_processing": "Processing...",
            "btn_retry": "Retry",

            # --- 3. UI Static Text ---
            "ui_title": "FaintOCR(1.10.4)",
            "ui_btn_sub_show": "Show Subtitles",
            "ui_btn_sub_hide": "Hide Subtitles",
            "ui_grp_dict": "Dictionary Config",
            "ui_lbl_game": "Game:",
            "ui_lbl_source": "Src:",
            "ui_lbl_target": "Tgt:",
            "ui_map_init": "Waiting for check...",
            "ui_btn_fix_init": "Smart Fix/Init",
            "ui_grp_match": "Match Mode",
            "ui_lbl_mode": "Mode:",
            "ui_mode_0": "Off",
            "ui_mode_1": "Exact Match",
            "ui_mode_2": "Prefix Match",
            "ui_grp_threshold": "Similarity Threshold",
            "ui_grp_auto_ocr": "Auto OCR",
            "ui_btn_auto_ocr_on": "Auto OCR: ON",
            "ui_btn_auto_ocr_off": "Auto OCR: OFF",
            "ui_grp_region": "Region Settings",
            "ui_btn_sel_region": "Select Region",
            "ui_btn_show_region": "Show Region",
            "ui_btn_ocr": "Run OCR",
            "ui_btn_auto_copy_on": "Auto Copy: ON",
            "ui_btn_auto_copy_off": "Auto Copy: OFF",
            "ui_btn_auto_save_on": "Auto Save: ON",
            "ui_btn_auto_save_off": "Auto Save: OFF",
            "ui_status_ready": "Ready",

            # --- 4. Interactive & Subtitles ---
            "sub_waiting": "Waiting for OCR...",
            "status_threshold": "Similarity Threshold: {0}%",
            "status_ocr_submit": "OCR task submitted",
            "status_sel_region": "Please select region (ESC to cancel)",
            "status_region_ok": "Region selected: {0},{1} {2}x{3}",
            "status_auto_ocr_on": "Auto OCR ON ({0:.1f}s/interval)",  # [修复] 统一浮点数格式
            "status_auto_ocr_off": "Auto OCR OFF",
            "status_interval": "Auto OCR interval updated: {0:.1f}s",

            # --- 5. [新增] Dynamic Status & Backend Errors ---
            "status_perf": "Capture: {0:.3f}s | OCR: {1:.3f}s | Match: {2:.3f}s",
            "status_perf_sim": "{0} | Similarity: {1}%",
            "status_no_text": "No text detected",
            "status_ocr_error": "OCR execution error: {0}",
            "err_cancelled": "Operation cancelled",
            "err_download_fail": "Download failed: {0}",
        }
    }

    @classmethod
    def get(cls, key, *args):
        template = cls.TEXT.get(cls.current_lang, {}).get(key, key)
        return template.format(*args) if args else template


class Config:
    # 直接基于 BASE_DIR 创建路径，不再用 dirname(dirname) 这种容易产生偏移的逻辑
    TEXTMAP_ROOT = os.path.join(BASE_DIR, "TextMap")
    OUTPUT_FILE = os.path.join(BASE_DIR, "OCR_Results.txt")
    OCR = {
        "DEFAULT_REGION": (100, 810, 1720, 240),
        "DEFAULT_INTERVAL": 2.0,
    }
    LANG_MAP = {
        "简体中文": "CHS",
        "English": "EN",
        "日本語": "JP"
    }
    GAMES = {
        "Genshin Impact": {
            "folder": "Genshin Impact",
            "urls": {
                "TextMapCHS.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapCHS.json",
                "TextMapEN.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapEN.json",
                "TextMapJP.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapJP.json"
            }
        },
        "Star Rail": {
            "folder": "Star Rail",
            "urls": {
                "TextMapCHS.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapCHS.json",
                "TextMapEN.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapEN.json",
                "TextMapJP.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapJP.json"
            }
        }
    }


class UIStyles:
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
    WINDOW_BTN_MIN = """
            QPushButton {
                background-color: rgba(255, 255, 255, 2);
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 80);
            }
        """
    WINDOW_BTN_CLOSE = """
            QPushButton {
                background-color: rgba(255, 255, 255, 2);
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(232, 11, 23, 160);
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
    progress_signal = QtCore.Signal(str, list)
    percent_signal = QtCore.Signal(int)
    work_finished_signal = QtCore.Signal(str, str, str, int)
    error_signal = QtCore.Signal(bool, str)

    def __init__(self, game_key, source_lang, target_lang, handle_mode):
        super().__init__()
        self.game_key = game_key
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.handle_mode = handle_mode
        self.result = []
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        logger.info(f"字典任务收到取消指令: {self.game_key}")

    @logger.catch(exclude=Exception)  # 防止未捕获的崩溃，exclude用于手动处理逻辑异常
    def run(self):
        if self._is_cancelled: return

        callbacks = {
            # [修改] 默认空列表防止无参数时报错
            'progress': lambda key, args=[]: self.progress_signal.emit(key, args),
            'percent': self.percent_signal.emit,
            'check_cancel': lambda: self._is_cancelled
        }

        try:
            logger.info(f"开始字典任务: {self.game_key} Mode={self.handle_mode}")
            self.result = TextMapLoader.handle_task(
                self.game_key,
                self.source_lang,
                self.target_lang,
                self.handle_mode,
                callbacks
            )

            if self._is_cancelled:
                logger.warning("字典任务在中途已取消")
                return

            self.work_finished_signal.emit(
                self.game_key,
                self.source_lang,
                self.target_lang,
                self.handle_mode
            )
            logger.success("字典任务执行成功")

        except Exception as e:
            if not self._is_cancelled:
                # [关键] 记录完整堆栈，方便排查是网络问题还是解析问题
                logger.exception("字典加载线程发生异常")
                self.error_signal.emit(False, str(e))


class TextMapLoader:
    """
    文本映射加载器 (静态工具类 - 流水线版)
    逻辑重构：检查 -> (修复) -> 加载，三步合一
    """

    # 类属性：预编译正则
    combo_chars = r'a-zA-Z0-9\u00C0-\u024F\u0600-\u06FF_'
    ideograph_chars = r'\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af'
    TOKENIZER_PATTERN = re.compile(
        f'[{combo_chars}]+|[{ideograph_chars}]|[^{combo_chars}{ideograph_chars}]+'
    )

    @classmethod
    def get_file_path(cls, game_key, filename):
        config = Config.GAMES.get(game_key, {})
        folder = config.get("folder", "")
        if not folder:
            work_dir = os.path.join(Config.TEXTMAP_ROOT, "Unknown")
        else:
            work_dir = os.path.join(Config.TEXTMAP_ROOT, folder)
        os.makedirs(work_dir, exist_ok=True)
        return os.path.join(work_dir, filename)

    @classmethod
    def _tokenize(cls, text):
        if not text: return []
        return cls.TOKENIZER_PATTERN.findall(text)

    @classmethod
    def handle_task(cls, game_key, source_lang, target_lang, mode, callbacks=None):
        if callbacks is None: callbacks = {}
        # [修改] 默认的匿名函数也要适配两个参数
        report_progress = callbacks.get('progress', lambda key, args=[]: None)
        report_percent = callbacks.get('percent', lambda x: None)
        check_cancel = callbacks.get('check_cancel', lambda: False)

        # === 1. 模式解析 ===
        # mode=0: 检查模式，target_map/prefix 均为 False
        is_repair = (mode < 0)
        task_mask = abs(mode)
        target_map = bool(task_mask & 1)
        target_prefix = bool(task_mask & 2)

        missing_raw = []
        missing_map = []
        missing_prefix = []

        # 数据容器
        text_map = {}
        keys_list = []
        prefix_dict = {}

        # =========================================================
        # 阶段 1: RAW 文件 (检查 -> 修复)
        # =========================================================
        # [修改] 始终检查 Raw
        src_raw_file = f"TextMap{source_lang}.json"
        tgt_raw_file = f"TextMap{target_lang}.json"
        raw_files = [src_raw_file, tgt_raw_file]
        for f in raw_files:
            if not os.path.exists(cls.get_file_path(game_key, f)):
                missing_raw.append(f)

        # 只有在修复模式且确实缺失时，才执行下载
        if missing_raw and is_repair:
            if check_cancel(): raise Exception(I18n.get("err_cancelled"))
            # ✅ 抛出 Key 和参数：文件数量
            report_progress("prog_downloading_raw", [len(missing_raw)])
            success, msg = cls.download_files(game_key, missing_raw, report_progress, report_percent, check_cancel)
            if success:
                missing_raw = []  # 修复成功

        # =========================================================
        # 阶段 2: MAP 字典 (检查 -> 修复 -> 加载)
        # =========================================================
        map_file = f"TextMap-{source_lang}to{target_lang}.json"
        map_path = cls.get_file_path(game_key, map_file)
        is_map_exist = os.path.exists(map_path)

        # B. 尝试加载 (仅当: 存在 + 目标包含Map)
        # 注意：Mode 0 下 target_map 为 False，这里直接跳过读取
        if is_map_exist and target_map:
            try:
                with open(map_path, 'rb') as f:
                    data = orjson.loads(f.read())
                if data:
                    text_map = data
                    keys_list = list(data.keys())  # 获取 Keys 用于后续 Prefix 生成
            except:
                is_map_exist = False  # 加载失败视为文件损坏/不存在

        # B. 尝试修复 (仅当: 不存在 + 修复模式 + 目标包含Map + Raw文件齐全)
        if not missing_raw:
            if not is_map_exist and is_repair and target_map:
                if check_cancel(): raise Exception(I18n.get("err_cancelled"))
                # ✅ 抛出 Key，没有参数就传空列表
                report_progress("prog_generating_map", [])
                # [关键优化] 接收返回的数据对象，而不是 boolean
                generated_data = cls._merge_and_save_map(game_key, source_lang, target_lang, report_progress, report_percent, check_cancel)
                if generated_data is not None:
                    is_map_exist = True
                    # [关键优化] 直接使用内存数据，避免写后读
                    text_map = generated_data
                    keys_list = list(text_map.keys())

        # C. 判定缺失
        if not is_map_exist:
            missing_map.append(map_file)

        # =========================================================
        # 阶段 3: PREFIX 前缀索引 (检查 -> 修复 -> 加载)
        # =========================================================
        prefix_tokens = [5, 8, 13, 21]
        # [新增] 缓存预分词数据，避免多次循环时重复分词
        cached_tokenized_keys = None
        for N in prefix_tokens:
            p_file = f"TextMap-{source_lang}_Tk{N}.json"
            p_path = cls.get_file_path(game_key, p_file)
            is_p_exist = os.path.exists(p_path)

            # A. 尝试加载
            if is_p_exist and target_prefix:
                try:
                    with open(p_path, 'rb') as f:
                        prefix_dict[N] = orjson.loads(f.read())
                except:
                    is_p_exist = False

            # B. 尝试修复 (仅当: 不存在 + 修复模式 + 目标包含Prefix + 依赖Keys存在)
            if keys_list:
                if not is_p_exist and is_repair and target_prefix:
                    if check_cancel(): raise Exception(I18n.get("err_cancelled"))
                    # [新增] 只有确实需要生成文件时，才执行全量分词 (惰性加载)
                    if cached_tokenized_keys is None:
                        # ✅ 抛出 Key
                        report_progress("prog_preparing_tokens", [])
                        # 一次性对所有 Key 进行分词
                        cached_tokenized_keys = [cls._tokenize(k) for k in keys_list]
                    # ✅ 抛出 Key 和参数：N的值
                    report_progress("prog_generating_prefix", [N])
                    # [修改] 传入预分词后的数据 (cached_tokenized_keys) 而非原始 keys_list
                    generated_prefixes = cls._generate_prefix_file(p_path, cached_tokenized_keys, N, report_progress, report_percent, check_cancel)
                    if generated_prefixes is not None:
                        is_p_exist = True
                        # 直接使用返回的数据
                        prefix_dict[N] = generated_prefixes

            # C. 判定缺失
            if not is_p_exist:
                missing_prefix.append(p_file)

        # =========================================================
        # 4. 结束
        # =========================================================
        # 数据容器
        if text_map == {}:
            text_map = None
        if not keys_list:
            keys_list = None
        if prefix_dict == {}:
            prefix_dict = None

        return missing_raw, missing_map, missing_prefix, text_map, keys_list, prefix_dict

    @classmethod
    def download_files(cls, game_key, target_files=None, progress_callback=None, percent_callback=None,
                       check_cancel_func=None):
        """
        [重构] 使用 requests 实现的工业级流式下载
        1. 保持了原有的原子写入 (Atomic Write) 和强制刷盘 (fsync) 逻辑
        2. 使用 requests.iter_content 简化流式读取
        3. 自动处理 HTTP 错误状态码
        """
        config = Config.GAMES.get(game_key, {})
        current_urls = config.get("urls", {})
        folder = config.get("folder", "")

        work_dir = os.path.join(Config.TEXTMAP_ROOT, folder)
        os.makedirs(work_dir, exist_ok=True)

        # 伪装 Header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 定义取消异常
        class DownloadCancelled(Exception):
            pass

        try:
            # 筛选需要下载的文件
            if target_files:
                files_to_download = {k: v for k, v in current_urls.items() if k in target_files}
            else:
                files_to_download = current_urls

            if not files_to_download:
                return True, "无需下载"

            for file_name, url in files_to_download.items():
                if check_cancel_func and check_cancel_func():
                    return False, I18n.get("err_cancelled")  # [修复]

                final_path = cls.get_file_path(game_key, file_name)
                temp_path = final_path + ".download"

                # 清理旧的临时文件
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass

                max_retries = 3
                success = False
                last_error = None

                for attempt in range(1, max_retries + 1):
                    try:
                        logger.info(f"开始下载 [{attempt}/{max_retries}]: {file_name}")
                        if progress_callback:
                            retry_text = f" ({attempt})" if attempt > 1 else ""
                            # ✅ 抛出 Key 和参数：文件名，重试文本
                            progress_callback("prog_downloading_file", [file_name, retry_text])

                        # --- [核心优化] Requests 流式下载 ---
                        # stream=True 是关键，防止大文件瞬间撑爆内存
                        # verify=False 对应原代码的忽略 SSL 证书
                        with requests.get(url, stream=True, headers=headers, timeout=15, verify=False) as response:
                            # 如果状态码不是 200，直接抛出异常，进入 retry 逻辑
                            response.raise_for_status()

                            total_size = int(response.headers.get('content-length', 0))
                            downloaded_size = 0
                            chunk_size = 8192

                            with open(temp_path, 'wb') as f:
                                # 使用 iter_content 替代手动的 while read
                                for chunk in response.iter_content(chunk_size=chunk_size):
                                    # 1. 极高频取消检测
                                    if check_cancel_func and check_cancel_func():
                                        return False, I18n.get("err_cancelled")  # [修复]

                                    if chunk:  # 过滤掉 keep-alive 的空 chunk
                                        f.write(chunk)
                                        downloaded_size += len(chunk)

                                        # 2. 进度回调 (简单限流)
                                        if percent_callback and total_size > 0:
                                            percent = int(downloaded_size / total_size * 100)
                                            percent_callback(max(0, min(100, percent)))

                                # Loop 结束，文件写完
                                # 3. [保留] 强制刷盘，确保数据物理写入
                                f.flush()
                                os.fsync(f.fileno())

                        # With 结束，文件关闭。

                        # 4. [保留] 原子替换
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        os.replace(temp_path, final_path)

                        success = True
                        logger.success(f"下载完成: {file_name}")
                        break  # 成功退出循环

                    except DownloadCancelled:
                        raise  # 向上抛出
                    except Exception as e:
                        last_error = e
                        logger.warning(f"下载失败重试 {file_name}: {e}")
                        if os.path.exists(temp_path):
                            try:
                                os.remove(temp_path)
                            except:
                                pass
                        time.sleep(1)

                if not success:
                    logger.error(f"文件下载最终失败: {file_name}")
                    raise Exception(f"{file_name} fail: {str(last_error)}")

            return True, "下载完成"

        except DownloadCancelled:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False, I18n.get("err_cancelled")  # [修复]
        except Exception as e:
            logger.error(f"下载流程异常: {e}")
            return False, I18n.get("err_download_fail", str(e))  # [修复]

    @classmethod
    def _merge_and_save_map(cls, game_key, source_lang, target_lang, progress_cb, percent_cb, cancel_cb):
        src_p = cls.get_file_path(game_key, f"TextMap{source_lang}.json")
        tgt_p = cls.get_file_path(game_key, f"TextMap{target_lang}.json")
        out_p = cls.get_file_path(game_key, f"TextMap-{source_lang}to{target_lang}.json")

        try:
            with open(src_p, 'rb') as f:
                src_d = orjson.loads(f.read())
            with open(tgt_p, 'rb') as f:
                tgt_d = orjson.loads(f.read())

            merged = {}
            total = len(src_d)

            # 加入进度和取消回调检测
            for i, (k, s) in enumerate(src_d.items()):
                # 每处理 10000 条汇报一次进度，避免回调开销过大
                if i % 10000 == 0:
                    if cancel_cb(): return None  # [修改] 返回 None
                    percent_cb(int((i / total) * 100))

                if k in tgt_d:
                    # [修改] 调用清洗函数处理 Source (OCR 识别的源语言)
                    s_tx = cls.clean_unity_rich_text(s)
                    # [修改] 调用清洗函数处理 Target (显示的翻译文本)
                    t_tx = cls.clean_unity_rich_text(tgt_d[k])
                    if s_tx and t_tx:
                        if s_tx not in merged:  merged[s_tx] = set()
                        merged[s_tx].add(t_tx)

            # 最终强制满进度
            if cancel_cb(): return None  # [修改] 返回 None
            percent_cb(100)

            final = {k: list(v) for k, v in merged.items()}
            # [修复] 调用原子写入
            if cls._save_file_atomic(out_p, final, indent=True):
                logger.info(f"字典合并成功: {len(final)} 条目")  # [Log]
                return final
            else:
                return None

        except Exception as e:
            logger.exception(f"字典合并失败: {e}") # [Log] 记录堆栈
            return None  # [修改] 失败返回 None

    @classmethod
    def clean_unity_rich_text(cls, text):
        """
        根据特定规则清洗文本：
        1. 全局应用：标准化空格、去标签、替换省略号
        2. 条件应用（仅当以#开头）：去#、换昵称、处理性别、处理注音
        """
        if not text:
            return ""

        # ===============================
        # 第一阶段：全局通用处理 (无条件执行)
        # ===============================

        # 1. 标准化空白字符 (\n -> 空格, \u00A0 -> 空格)
        text = text.replace(r'\n', ' ').replace(r'\u00A0', ' ')

        # 2. 将所有 "…" (中文省略号) 替换为 "···" (三个中点)
        # 说明：OCR 有时会将省略号识别为三个点，统一格式有助于匹配
        text = text.replace('…', '···')

        # 3. 剔除 Unity 富文本标签 (如 <color=...>)
        text = re.sub(r'<[^>]+>', '', text)

        # ===============================
        # 第二阶段：特定逻辑处理 (仅针对以 # 开头的文本)
        # ===============================

        if text.startswith('#'):
            # 0. 剔除开头的 "#"
            text = text[1:]

        # 4. 替换昵称变量
        # 注意：原文本可能是 #{NICKNAME}，但因为上面去掉了首位 #，
        # 或者是中间出现的 {NICKNAME}，这里直接匹配花括号部分即可
        text = text.replace('{NICKNAME}', 'Player')

        # 4. [升级版] 简化性别分歧逻辑 -> 始终保留女主文案
        # 逻辑：同时匹配 "{M..}{F..}" 和 "{F..}{M..}" 两种顺序
        # 这里的 (?:...) 是非捕获组，用于组合逻辑
        # Group 1: 捕获 M在前 F在后时的 F内容
        # Group 2: 捕获 F在前 M在后时的 F内容
        gender_pattern = r'(?:\{M#.*?\}\{F#(.*?)\})|(?:\{F#(.*?)\}\{M#.*?\})'

        # 使用 lambda 函数：如果匹配到了第一种情况(M前F后)，取Group 1；否则取Group 2
        text = re.sub(gender_pattern, lambda m: m.group(1) or m.group(2), text)

        # 6. [升级版] 处理注音（Ruby）文本
        # 目标：统一转为 "正文(注音)" 或 "(注音)正文" 的括号形式

        # 情况 A: 处理 {RUBY_B#注音}正文{RUBY_E#} 格式
        # 例如：{RUBY_B#死亡之泰坦}塞纳托斯{RUBY_E#} -> (死亡之泰坦)塞纳托斯
        text = re.sub(r'\{RUBY_B#(.*?)}', r'(\1)', text)  # 将开始标签改为 (内容)
        text = text.replace('{RUBY_E#}', '')  # 删除结束标签

        # 情况 B: 处理 {RUBY#[S]注音} 格式
        # 例如：河{RUBY#[S]灰河}里 -> 河(灰河)里
        # 逻辑：匹配 {RUBY 开头，兼容 # 或 =，忽略中间可能存在的 [S]/[D] 标记，捕获正文
        text = re.sub(r'\{RUBY#.*?(?:\[.*?])?(.*?)}', r'(\1)', text)

        return text.strip()

    @classmethod
    def _generate_prefix_file(cls, file_path, tokenized_data, token_len, progress_cb, percent_cb, cancel_cb):
        """
        [修改] 生成前缀文件
        :param tokenized_data: 已经分好词的列表 List[List[str]]
        :param token_len: 截取长度
        """
        try:
            prefixes = []
            total = len(tokenized_data)

            # [修改] 直接遍历已经分好词的数据，不再在循环内调用 _tokenize
            for i, tokens in enumerate(tokenized_data):
                if i % 50000 == 0:
                    if cancel_cb(): return None
                    percent_cb(int((i / total) * 100))

                # [修改] 直接截断并拼接，极大提高速度
                prefixes.append("".join(tokens[:token_len]))

            if cancel_cb(): return None
            percent_cb(100)

            # [修复] 调用原子写入
            if cls._save_file_atomic(file_path, prefixes, indent=False):
                logger.debug(f"前缀索引生成成功: Tk{token_len}")  # [Log]
                return prefixes
            else:
                return None

        except Exception as e:
            logger.error(f"前缀生成失败 Tk{token_len}: {e}") # [Log]
            return None

    # [新增] 原子写入方法：先写 tmp，再重命名
    @classmethod
    def _save_file_atomic(cls, final_path, data, indent=False):
        temp_path = final_path + ".tmp"
        try:
            # 序列化参数
            option = orjson.OPT_INDENT_2 if indent else 0

            with open(temp_path, 'wb') as f:
                f.write(orjson.dumps(data, option=option))
                f.flush()
                os.fsync(f.fileno())  # 强制刷入磁盘，防止断电数据丢失

            # 原子操作：如果 final_path 已存在，会无声覆盖
            # 这一步极快，几乎不可能被中断
            os.replace(temp_path, final_path)
            return True
        except Exception as e:
            logger.critical(f"原子写入失败 (磁盘满或权限不足): {final_path} - {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False


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
        # [新增] 关闭时自动销毁对象释放内存
        self.setAttribute(Qt.WA_DeleteOnClose)

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
        # [新增] 关闭时自动销毁对象释放内存
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowType.Tool)
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        # 500毫秒后自动关闭
        QtCore.QTimer.singleShot(250, self.close)

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
        # 修改前: finished = QtCore.Signal(str, str)

        # 修改后: 增加一个 bool 参数代表 is_success
        # 格式: (是否成功, 主文本/错误信息, 状态栏附加信息)
        finished = QtCore.Signal(bool, str, str)

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

            # [Log] 记录开始 (Debug级别)
            logger.debug("OCRWorker 开始处理图片")
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

            # cv2.imwrite(r'/Image_Output/processed_image.jpg', img_cv)

            # --- 计时：截图完成---
            t_process1 = time.perf_counter()
            capture_cost = t_process1 - t_start

            # 执行 OCR
            raw_text = self.run_rapidocr(ocr_engine, img_cv)

            # --- 计时：OCR完成 ---
            t_process2 = time.perf_counter()
            ocr_cost = t_process2 - t_process1

            # --- 修改点 A: OCR 识别为空的处理 ---
            if not raw_text or raw_text.strip() == "":
                # [修复] 接入 I18n
                self.signals.finished.emit(True, "", I18n.get("status_no_text"))
                return

            # 获取分离的匹配结果
            text_original, text_translated, similarity = self.process_text_with_matching(
                raw_text, text_matcher, match_mode, similarity_threshold
            )

            # --- 计时结束：文本匹配 ---
            t_end = time.perf_counter()
            match_cost = t_end - t_process2

            # 3. 构造界面所需的数据 (接入 I18n)
            perf_info = I18n.get("status_perf", capture_cost, ocr_cost, match_cost)

            if text_translated:
                # 匹配成功
                subtitle_text = f"{text_original}\n{text_translated}"
                status_info = I18n.get("status_perf_sim", perf_info, similarity)
            else:
                # 未匹配
                subtitle_text = text_original
                status_info = perf_info

            # [Log] 成功 (Debug级别)
            logger.debug(f"OCR完成: {raw_text[:20]}... 耗时:{match_cost:.3f}s")
            self.signals.finished.emit(True, subtitle_text, status_info)

        except Exception as e:
            # [关键修改] 自动记录报错堆栈，但仍发射信号通知UI
            logger.exception("OCR流程发生严重错误")
            # [修复] 接入 I18n 处理异常信息
            self.signals.finished.emit(False, I18n.get("status_ocr_error", str(e)), "")

    def run_rapidocr(self, engine, img):
        """
        调用 RapidOCR 引擎进行推理
        并根据文本框的垂直位置关系决定是否换行
        """
        # result 格式: [[box, text, score], [box, text, score], ...]
        # box 格式: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] (左上, 右上, 右下, 左下)
        result, _ = engine(img)

        # 如果需要调试OCR坐标，使用 trace 级别 (默认不记录，不卡顿)
        if not result:
            logger.trace("RapidOCR 未识别到任何内容")
            return ""

        logger.trace(f"RapidOCR 原始数据: {result}")

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
    文本匹配器 (纯净版)
    不再负责文件读写，只负责接收数据和计算匹配
    """

    def __init__(self, cache_size=3):
        self.text_map = {}
        self.cache = {}
        self.cache_size = cache_size

        # 内部列表初始化
        self.keys_list = []
        self.candidates_full = []
        self.candidates_t5 = []
        self.candidates_t8 = []
        self.candidates_t13 = []
        self.candidates_t21 = []

        # 只需要简单的 tokenizer 用于处理输入的 OCR 文本
        combo_chars = r'a-zA-Z0-9\u00C0-\u024F\u0600-\u06FF_'
        ideograph_chars = r'\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af'
        self.tokenizer_pattern = re.compile(
            f'[{combo_chars}]+|[{ideograph_chars}]|[^{combo_chars}{ideograph_chars}]+'
        )

        self.hits = 0
        self.misses = 0

    def set_data(self, text_map=None, keys_list=None, prefix_dict=None):
        """
        更新匹配数据 (支持增量/部分更新)
        :param text_map: 主翻译字典 (可选)
        :param keys_list: 原文键列表 (可选)
        :param prefix_dict: 前缀索引字典 (可选)
        """
        data_changed = False

        # 1. 更新主字典
        if text_map is not None:
            self.text_map = text_map
            data_changed = True

        # 2. 更新完整键列表 (用于完全匹配)
        if keys_list is not None:
            self.keys_list = keys_list
            self.candidates_full = self.keys_list
            data_changed = True

        # 3. 更新前缀索引 (用于前缀匹配)
        if prefix_dict is not None:
            # 从传入的字典中提取各级索引
            # 使用 get(N, []) 确保即使 key 不存在也重置为空列表，防止脏数据
            self.candidates_t5 = prefix_dict.get(5, [])
            self.candidates_t8 = prefix_dict.get(8, [])
            self.candidates_t13 = prefix_dict.get(13, [])
            self.candidates_t21 = prefix_dict.get(21, [])
            data_changed = True

        # 只有当任何数据发生变动时，才清理缓存
        if data_changed:
            self.clear_cache()

    def _tokenize(self, text):
        if not text: return []
        return self.tokenizer_pattern.findall(text)

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

        # 1. 高置信度处理 (>=90) - 统一了原代码中 >=90 和 >90 的细微差异，建议统一用 90
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

        # 2. 最佳匹配处理 (<90 但 >=阈值)
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
    task_completed = QtCore.Signal(bool, str, str)

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
            logger.debug(f"队列已满，丢弃旧任务 (Size: {len(self.task_queue)})")
        self.task_queue.append(task_data)
        self.total_submitted += 1
        # logger.trace 用于极高频信息
        logger.trace(f"任务已提交 (队列: {len(self.task_queue)}, 活跃: {self.active_tasks})")
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
            logger.debug(f"启动OCR线程 (剩余队列: {len(self.task_queue)})")

    def _on_task_completed(self, is_success, main_text, status_info):
        """任务完成后的回调"""
        self.active_tasks -= 1
        self.total_completed += 1
        # 仅在失败时记录 Warning，成功时 Debug
        if not is_success:
            logger.warning(f"OCR任务失败: {main_text}")
        # 转发 3 个参数给主窗口
        self.task_completed.emit(is_success, main_text, status_info)
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

    # 在 OCRTaskManager 类中添加
    def cancel_all(self):
        """清空等待队列，并尝试移除线程池中未开始的任务"""
        queue_len = len(self.task_queue)
        self.task_queue.clear()  # 1. 清空 Python 端的缓冲队列
        self.thread_pool.clear()  # 2. (重要) 移除 Qt 线程池中已排队但未启动的线程
        logger.info(f"任务管理器已重置，取消了 {queue_len} 个等待任务")


class OCRController(QtCore.QObject):
    """
    UI 与 业务逻辑解耦：控制器层
    只负责管理状态、调度引擎和多线程，不直接操作任何 UI 控件。
    """
    # 定义向 UI 通信的信号
    dict_progress_signal = QtCore.Signal(str, list)  # 字典下载/合并进度文本
    dict_percent_signal = QtCore.Signal(int)  # 字典进度条百分比

    # 统一下发 UI 状态：(业务状态枚举, 缺失文件列表, 当前层级, 目标层级)
    ui_state_signal = QtCore.Signal(object, list, int, int)
    ui_lock_signal = QtCore.Signal(bool)  # 锁定/解锁界面操作

    ocr_result_signal = QtCore.Signal(bool, str, str)  # OCR完成信号

    def __init__(self):
        super().__init__()
        # --- 业务状态 ---
        self.current_game = list(Config.GAMES.keys())[0]
        self.source_lang = Config.LANG_MAP[list(Config.LANG_MAP.keys())[0]]
        self.target_lang = Config.LANG_MAP[list(Config.LANG_MAP.keys())[1]]
        self.match_mode = 0
        self.similarity_threshold = 60

        self.text_matcher = TextMatcher(cache_size=3)
        self.text_matcher.set_data({}, {}, {})

        self.missing_raw = []
        self.missing_map = []
        self.missing_prefix = []
        self.satisfied_files_level = 0

        # --- 核心组件 ---
        try:
            self.ocr_engine = RapidOCR(det_limit_side_len=960, det_limit_type='max', intra_op_num_threads=4)
        except Exception as e:
            logger.error(f"RapidOCR 初始化失败: {e}")
            self.ocr_engine = None

        self.task_manager = OCRTaskManager()
        self.task_manager.task_completed.connect(self.ocr_result_signal)
        self.dict_worker = None

        # 自动加载的防抖定时器 (属于业务逻辑层)
        self.auto_load_timer = QtCore.QTimer()
        self.auto_load_timer.setSingleShot(True)
        self.auto_load_timer.timeout.connect(self._run_check_and_load)

    # ================= 供 UI 调用的接口 =================

    def set_game(self, game_name):
        self.current_game = game_name
        self._reset_dict_state()

    def set_languages(self, source_name, target_name):
        self.source_lang = Config.LANG_MAP[source_name]
        self.target_lang = Config.LANG_MAP[target_name]
        self._reset_dict_state()

    def set_match_mode(self, mode):
        self.match_mode = mode
        self.text_matcher.clear_cache()
        self.auto_load_timer.stop()
        self._refresh_ui_state()

    def set_threshold(self, threshold):
        self.similarity_threshold = threshold
        self.text_matcher.clear_cache()

    def request_ocr(self, region):
        """接收 UI 传来的区域，打包提交给任务管理器"""
        if self.ocr_engine is None:
            self.ocr_result_signal.emit(False, "OCR 引擎未初始化", "")
            return

        x, y, w, h = region
        monitor = {"top": y, "left": x, "width": w, "height": h}
        task_data = {
            'monitor': monitor,
            'text_matcher': self.text_matcher,
            'match_mode': self.match_mode,
            'similarity_threshold': self.similarity_threshold,
            'ocr_engine': self.ocr_engine
        }
        self.task_manager.submit_task(task_data)

    def run_check(self):
        """执行快速检查"""
        self._stop_previous_worker()
        self.dict_worker = DictionaryWorker(self.current_game, self.source_lang, self.target_lang, handle_mode=0)
        self.dict_worker.work_finished_signal.connect(self._on_worker_finished)
        self.dict_worker.error_signal.connect(self._on_worker_error)
        self.dict_worker.start()

    def run_smart_fix(self):
        """执行智能修复/下载"""
        self.auto_load_timer.stop()
        self._stop_previous_worker()
        self.ui_lock_signal.emit(True)
        # 告诉 UI 准备进入加载/生成状态
        self.ui_state_signal.emit(DictState.LOADING, [], self.satisfied_files_level, self.match_mode)

        target_mode = self.match_mode
        current_level = self.satisfied_files_level
        handle_mode = 0

        if target_mode == 1 and current_level < 1:
            handle_mode = -1
        elif target_mode == 2 and current_level < 2:
            handle_mode = -3

        self.dict_worker = DictionaryWorker(self.current_game, self.source_lang, self.target_lang, handle_mode)
        self.dict_worker.progress_signal.connect(self.dict_progress_signal)
        self.dict_worker.percent_signal.connect(self.dict_percent_signal)
        self.dict_worker.work_finished_signal.connect(self._on_worker_finished)
        self.dict_worker.error_signal.connect(self._on_worker_error)
        self.dict_worker.start()

    def cleanup(self):
        """清理资源"""
        self.task_manager.cancel_all()
        self.auto_load_timer.stop()
        self.text_matcher.clear_cache()
        self._stop_previous_worker()

    # ================= 内部业务逻辑 =================

    def _reset_dict_state(self):
        self.satisfied_files_level = 0
        self.text_matcher.set_data({}, [], {})
        self.auto_load_timer.stop()
        self.run_check()

    def _stop_previous_worker(self):
        if self.dict_worker and self.dict_worker.isRunning():
            try:
                self.dict_worker.work_finished_signal.disconnect()
                self.dict_worker.error_signal.disconnect()
            except:
                pass
            self.dict_worker.cancel()
            self.dict_worker.wait(200)
            if self.dict_worker.isRunning():
                self.dict_worker.terminate()
                self.dict_worker.wait()
            self.dict_worker = None

    def _run_check_and_load(self):
        # 告诉 UI 进入自动加载的黄灯状态
        self.ui_state_signal.emit(DictState.LOADING, [], self.satisfied_files_level, self.match_mode)

        self._stop_previous_worker()
        target_mode = self.match_mode
        current_level = self.satisfied_files_level
        handle_mode = 0

        if target_mode == 1 and current_level < 1:
            handle_mode = 1
        elif target_mode == 2:
            if current_level == 0:
                handle_mode = 3
            elif current_level == 1:
                handle_mode = 2

        if handle_mode == 0: return

        self.dict_worker = DictionaryWorker(self.current_game, self.source_lang, self.target_lang, handle_mode)
        self.dict_worker.work_finished_signal.connect(self._on_worker_finished)
        self.dict_worker.error_signal.connect(self._on_worker_error)
        self.dict_worker.start()

    def _on_worker_finished(self, handle_game, handle_source_lang, handle_target_lang, handle_mode):
        self.ui_lock_signal.emit(False)
        if (
                handle_game != self.current_game or handle_source_lang != self.source_lang or handle_target_lang != self.target_lang):
            logger.warning("丢弃过期 Worker 数据")
            return

        result_data = self.dict_worker.result
        (missing_raw, missing_map, missing_prefix, text_map, keys_list, prefix_dict) = result_data

        self.missing_raw = missing_raw
        self.missing_map = missing_map
        self.missing_prefix = missing_prefix

        if handle_mode != 0:
            self.text_matcher.set_data(text_map, keys_list, prefix_dict)
            task_mask = abs(handle_mode)
            if bool(task_mask & 1) and not self.missing_raw and not self.missing_map:
                self.satisfied_files_level = 1
            if bool(task_mask & 2) and not self.missing_raw and not self.missing_map and not self.missing_prefix:
                self.satisfied_files_level = 2

        self._refresh_ui_state()

    def _on_worker_error(self, success, msg):
        self.ui_lock_signal.emit(False)
        if not success:
            # ✅ 修改：直接把错误信息放进列表里，投递给主状态机！
            self.ui_state_signal.emit(DictState.ERROR, [msg], 0, 0)

    def _refresh_ui_state(self):
        if self.match_mode == 0:
            self.ui_state_signal.emit(DictState.STANDBY, [], 0, 0)
            return

        current_missing = []
        current_missing.extend(self.missing_raw)
        if self.match_mode >= 1: current_missing.extend(self.missing_map)
        if self.match_mode >= 2: current_missing.extend(self.missing_prefix)

        if len(current_missing) > 0:
            self.ui_state_signal.emit(DictState.MISSING, current_missing, 0, 0)
        else:
            if self.satisfied_files_level < self.match_mode:
                self.ui_state_signal.emit(DictState.PENDING, [], self.satisfied_files_level, self.match_mode)
                self.auto_load_timer.start(2400)
            else:
                self.ui_state_signal.emit(DictState.READY, [], self.satisfied_files_level, self.match_mode)


class FloatingOCR(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # --- UI 局部纯视觉与状态变量 ---
        self.ocr_region = Config.OCR["DEFAULT_REGION"]
        self.auto_ocr_enabled = False
        self.auto_ocr_interval = Config.OCR["DEFAULT_INTERVAL"]
        self.auto_copy = False
        self.auto_save = False
        self._drag_pos = None

        self.setup_ui()
        self.sub_window = SubtitleWindow()

        # --- 绑定核心大脑 (Controller) ---
        # 实例化业务逻辑控制器，UI 不再亲自处理复杂的字典与识别逻辑
        self.controller = OCRController()
        self._connect_controller_signals()

        self.setup_timers()
        self.apply_stealth_mode()

        QtWidgets.QApplication.instance().aboutToQuit.connect(self.cleanup)

        # 启动时执行一次快速检查 (委托给 Controller)
        self.controller.run_check()

    def _connect_controller_signals(self):
        """将大脑(Controller)的信号连接到脸部(UI)的肌肉(更新方法)上"""
        self.controller.dict_progress_signal.connect(self.update_progress_ui_state)
        self.controller.dict_percent_signal.connect(self.download_progress.setValue)
        self.controller.ui_state_signal.connect(self.update_dict_ui_state)
        self.controller.ui_lock_signal.connect(self.set_ui_locked)
        self.controller.ocr_result_signal.connect(self.handle_ocr_result)

    def apply_stealth_mode(self):
        if sys.platform != "win32": return
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32

            # Windows 常量
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000

            # 1. 此时获取到的 current_ex_style 一定会包含 0x80000
            current_ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            has_layered = (current_ex_style & WS_EX_LAYERED) != 0

            if has_layered:
                # 瞬间脱下“透明外套”
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_ex_style & ~WS_EX_LAYERED)

            # 2. 施加防截图隐身魔法
            result = user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), wintypes.DWORD(WDA_EXCLUDEFROMCAPTURE))

            if has_layered:
                # 3. 瞬间把“透明外套”穿回来
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_ex_style)

            if result:
                logger.info(f"[Main] 字幕窗口已设置为截图隐身 (HWND: {hwnd})")
            else:
                logger.warning("[Main] 字幕窗口隐身设置失败")

        except Exception as e:
            logger.warning(f"[Main] API 调用出错: {e}")

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
        title_lbl = QtWidgets.QLabel(I18n.get("ui_title"))  # [多语言] 标题
        title_lbl.setStyleSheet("font-weight:600; color: white; font-size:14px;")
        title_bar.addWidget(title_lbl)
        title_bar.addStretch()
        btn_minimize = QtWidgets.QPushButton("─")
        btn_minimize.setFixedSize(40, 30)
        btn_minimize.setStyleSheet(UIStyles.WINDOW_BTN_MIN)
        btn_minimize.clicked.connect(self.showMinimized)
        title_bar.addWidget(btn_minimize)
        btn_close = QtWidgets.QPushButton("✕")
        btn_close.setFixedSize(40, 30)
        btn_close.setStyleSheet(UIStyles.WINDOW_BTN_CLOSE)
        btn_close.clicked.connect(self.close)
        title_bar.addWidget(btn_close)
        main_layout.addLayout(title_bar)

        self.btn_toggle_sub = QtWidgets.QPushButton(I18n.get("ui_btn_sub_show"))  # [多语言] 开启字幕窗口
        self.btn_toggle_sub.setCheckable(True)
        self.btn_toggle_sub.setStyleSheet(UIStyles.BUTTON_TOGGLE)
        self.btn_toggle_sub.clicked.connect(self.toggle_subtitle_window)
        main_layout.addWidget(self.btn_toggle_sub)

        dict_group = QtWidgets.QGroupBox(I18n.get("ui_grp_dict"))  # [多语言] 字典配置
        dict_group.setStyleSheet(UIStyles.GROUP_BOX)
        dict_layout = QtWidgets.QVBoxLayout()
        dict_layout.setSpacing(6)

        row_game = QtWidgets.QHBoxLayout()
        row_game.addWidget(QtWidgets.QLabel(I18n.get("ui_lbl_game")))  # [多语言] 游戏:
        self.game_selector = QtWidgets.QComboBox()
        self.game_selector.addItems(list(Config.GAMES.keys()))
        self.game_selector.setCurrentText(list(Config.GAMES.keys())[0])
        self.game_selector.currentIndexChanged.connect(self.on_game_changed)
        self.game_selector.setStyleSheet(UIStyles.COMBO_BOX)
        self.game_selector.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        row_game.addWidget(self.game_selector)
        dict_layout.addLayout(row_game)

        row_lang = QtWidgets.QHBoxLayout()
        row_lang.addWidget(QtWidgets.QLabel(I18n.get("ui_lbl_source")))  # [多语言] 源:
        self.combo_source = QtWidgets.QComboBox()
        self.combo_source.addItems(list(Config.LANG_MAP.keys()))
        self.combo_source.setCurrentText(list(Config.LANG_MAP.keys())[0])
        self.combo_source.setStyleSheet(UIStyles.COMBO_BOX)
        self.combo_source.currentIndexChanged.connect(self.on_language_changed)
        row_lang.addWidget(self.combo_source)
        row_lang.addWidget(QtWidgets.QLabel("➜"))  # 符号无需翻译
        row_lang.addWidget(QtWidgets.QLabel(I18n.get("ui_lbl_target")))  # [多语言] 译:
        self.combo_target = QtWidgets.QComboBox()
        self.combo_target.addItems(list(Config.LANG_MAP.keys()))
        self.combo_target.setCurrentText(list(Config.LANG_MAP.keys())[1])
        self.combo_target.setStyleSheet(UIStyles.COMBO_BOX)
        self.combo_target.currentIndexChanged.connect(self.on_language_changed)
        row_lang.addWidget(self.combo_target)
        dict_layout.addLayout(row_lang)

        self.map_status_label = QtWidgets.QLabel(I18n.get("ui_map_init"))  # [多语言] 等待检查...
        self.map_status_label.setStyleSheet("color: #ffb86c; font-size:10px;")
        self.map_status_label.setWordWrap(True)
        dict_layout.addWidget(self.map_status_label)

        row_btns = QtWidgets.QHBoxLayout()
        self.btn_smart_fix = QtWidgets.QPushButton(I18n.get("ui_btn_fix_init"))  # [多语言] 一键修复/初始化
        self.btn_smart_fix.setStyleSheet(UIStyles.BUTTON_Dark)
        self.btn_smart_fix.clicked.connect(self.run_smart_fix)
        self.btn_smart_fix.setEnabled(False)
        row_btns.addWidget(self.btn_smart_fix)
        dict_layout.addLayout(row_btns)

        self.download_progress = QtWidgets.QProgressBar()
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(0)
        self.download_progress.setTextVisible(True)
        self.download_progress.setStyleSheet("""
            QProgressBar {border: 1px solid grey; border-radius: 3px; text-align: center; background-color: #2c3e50; color: white;}
            QProgressBar::chunk {background-color: #409EFF; width: 10px;}
        """)
        self.download_progress.hide()
        dict_layout.addWidget(self.download_progress)
        dict_group.setLayout(dict_layout)
        main_layout.addWidget(dict_group)

        match_group = QtWidgets.QGroupBox(I18n.get("ui_grp_match"))  # [多语言] 文本匹配模式
        match_group.setStyleSheet(UIStyles.GROUP_BOX)
        match_layout = QtWidgets.QHBoxLayout()
        self.match_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.match_slider.setRange(0, 2)
        self.match_slider.setValue(0)
        self.match_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.match_slider.setTickInterval(1)
        self.match_slider.valueChanged.connect(self.on_match_mode_changed)
        self.match_label = QtWidgets.QLabel(I18n.get("ui_mode_0"))  # [多语言] 关闭
        self.match_label.setFixedWidth(60)
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_label.setStyleSheet("color: white;")
        match_layout.addWidget(QtWidgets.QLabel(I18n.get("ui_lbl_mode")))  # [多语言] 模式:
        match_layout.addWidget(self.match_slider)
        match_layout.addWidget(self.match_label)
        match_group.setLayout(match_layout)
        main_layout.addWidget(match_group)

        threshold_group = QtWidgets.QGroupBox(I18n.get("ui_grp_threshold"))  # [多语言] 相似度阈值
        threshold_group.setStyleSheet(UIStyles.GROUP_BOX)
        threshold_layout = QtWidgets.QHBoxLayout()
        self.threshold_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(60)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        self.threshold_label = QtWidgets.QLabel("60%")  # 纯数字，无需多语言
        self.threshold_label.setFixedWidth(40)
        self.threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.threshold_label.setStyleSheet("color: white;")
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_label)
        threshold_group.setLayout(threshold_layout)
        main_layout.addWidget(threshold_group)

        auto_ocr_group = QtWidgets.QGroupBox(I18n.get("ui_grp_auto_ocr"))  # [多语言] 自动OCR
        auto_ocr_group.setStyleSheet(UIStyles.GROUP_BOX)
        auto_layout = QtWidgets.QHBoxLayout()
        self.auto_ocr_btn = QtWidgets.QPushButton(I18n.get("ui_btn_auto_ocr_off"))  # [多语言] 自动OCR: 关
        self.auto_ocr_btn.setCheckable(True)
        self.auto_ocr_btn.clicked.connect(self.toggle_auto_ocr)
        self.interval_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(200, 5000)
        self.interval_slider.setValue(int(self.auto_ocr_interval * 1000))
        self.interval_slider.valueChanged.connect(self.on_interval_changed)
        self.interval_label = QtWidgets.QLabel(f"{self.auto_ocr_interval}s")  # 统一用 's' 代表秒
        self.interval_label.setFixedWidth(40)
        auto_layout.addWidget(self.auto_ocr_btn)
        auto_layout.addWidget(self.interval_slider)
        auto_layout.addWidget(self.interval_label)
        auto_ocr_group.setLayout(auto_layout)
        main_layout.addWidget(auto_ocr_group)

        region_group = QtWidgets.QGroupBox(I18n.get("ui_grp_region"))  # [多语言] 区域设置
        region_group.setStyleSheet(UIStyles.GROUP_BOX)
        region_layout = QtWidgets.QVBoxLayout()

        self.btn_select_region = QtWidgets.QPushButton(I18n.get("ui_btn_sel_region"))  # [多语言] 框选区域
        self.btn_select_region.clicked.connect(self.start_region_selection)
        region_layout.addWidget(self.btn_select_region)

        self.btn_show_region = QtWidgets.QPushButton(I18n.get("ui_btn_show_region"))  # [多语言] 显示当前区域
        self.btn_show_region.clicked.connect(self.show_region_overlay)
        region_layout.addWidget(self.btn_show_region)

        region_group.setLayout(region_layout)
        main_layout.addWidget(region_group)

        self.btn_ocr = QtWidgets.QPushButton(I18n.get("ui_btn_ocr"))  # [多语言] 执行OCR
        self.btn_ocr.clicked.connect(self.capture_and_submit_task)
        main_layout.addWidget(self.btn_ocr)

        btn_layout = QtWidgets.QHBoxLayout()
        self.auto_copy_btn = QtWidgets.QPushButton(I18n.get("ui_btn_auto_copy_off"))  # [多语言] 自动复制: 关
        self.auto_copy_btn.setCheckable(True)
        self.auto_copy_btn.clicked.connect(self.toggle_auto_copy)
        btn_layout.addWidget(self.auto_copy_btn)
        self.auto_save_btn = QtWidgets.QPushButton(I18n.get("ui_btn_auto_save_off"))  # [多语言] 自动保存: 关
        self.auto_save_btn.setCheckable(True)
        self.auto_save_btn.clicked.connect(self.toggle_auto_save)
        btn_layout.addWidget(self.auto_save_btn)
        main_layout.addLayout(btn_layout)

        self.status_label = QtWidgets.QLabel(I18n.get("ui_status_ready"))  # [多语言] 就绪
        self.status_label.setStyleSheet("color: lightgray; font-size:10px;")
        self.status_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        self.setStyleSheet(UIStyles.MAIN_WINDOW + UIStyles.BUTTON_Themed + UIStyles.SPIN_BOX + UIStyles.SLIDER)
        self.resize(200, 200)
        self.move(50, 50)

    def setup_timers(self):
        # 移除了负责业务的 auto_load_timer，只保留负责交互的 ocr_timer
        self.ocr_timer = QtCore.QTimer()
        self.ocr_timer.timeout.connect(self.capture_and_submit_task)

    # ================= UI 动作与 Controller 通信 (Delegation) =================

    def on_game_changed(self):
        self.controller.set_game(self.game_selector.currentText())

    def on_language_changed(self):
        self.controller.set_languages(self.combo_source.currentText(), self.combo_target.currentText())

    # 1. 匹配模式滑动
    def on_match_mode_changed(self, value):
        modes = [I18n.get("ui_mode_0"), I18n.get("ui_mode_1"), I18n.get("ui_mode_2")]
        self.match_label.setText(modes[value])
        self.controller.set_match_mode(value)

    # 2. 阈值滑动
    def on_threshold_changed(self, value):
        self.threshold_label.setText(f"{value}%") # 这个纯数字不用翻译
        self.status_label.setText(I18n.get("status_threshold", value))
        self.controller.set_threshold(value)

    def run_smart_fix(self):
        # [修改] 完美解耦：UI 仅仅通知大脑“用户按了按钮”，其他一切交由信号闭环处理
        self.controller.run_smart_fix()

    # 3. 提交OCR按钮
    def capture_and_submit_task(self):
        self.status_label.setText(I18n.get("status_ocr_submit"))
        self.controller.request_ocr(self.ocr_region)

    # ================= 接收 Controller 的状态同步 (Reactive UI) =================

    def set_ui_locked(self, locked):
        self.game_selector.setEnabled(not locked)
        self.combo_source.setEnabled(not locked)
        self.combo_target.setEnabled(not locked)
        self.match_slider.setEnabled(not locked)
        self.btn_ocr.setEnabled(not locked)

        # [修改] 将进度条的生命周期与 UI 锁定状态彻底强绑定
        if locked:
            self.download_progress.setValue(0)
            self.download_progress.show()
        else:
            self.download_progress.setValue(100)
            self.download_progress.hide()

    def update_dict_ui_state(self, state, data_list, current_lvl, target_lvl):
        """视图层自主决定如何展示业务状态 (全面支持国际化)"""
        self.map_status_label.setToolTip("")

        if state == DictState.STANDBY:
            self.map_status_label.setStyleSheet("color: gray; font-size:11px;")
            self.map_status_label.setText(I18n.get("state_standby"))
            self.btn_smart_fix.setText(I18n.get("btn_generate"))
            self.btn_smart_fix.setEnabled(False)

        elif state == DictState.READY:
            self.map_status_label.setStyleSheet("color: lightgreen; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_ready", current_lvl))
            self.btn_smart_fix.setText(I18n.get("btn_ready"))
            self.btn_smart_fix.setEnabled(False)

        elif state == DictState.PENDING:
            self.map_status_label.setStyleSheet("color: #8be9fd; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_pending", current_lvl, target_lvl))
            self.btn_smart_fix.setText(I18n.get("btn_load_now"))
            self.btn_smart_fix.setEnabled(True)

        elif state == DictState.LOADING:
            self.map_status_label.setStyleSheet("color: #f1c40f; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_loading", current_lvl, target_lvl))
            self.btn_smart_fix.setText(I18n.get("btn_processing"))
            self.btn_smart_fix.setEnabled(False)

        elif state == DictState.MISSING:
            self.map_status_label.setStyleSheet("color: #ff5555; font-size:11px; font-weight:bold;")
            # 多语言支持的文件省略语法
            missing_str = data_list[0] if len(data_list) == 1 else I18n.get("missing_more", data_list[0],
                                                                            len(data_list) - 1)
            self.map_status_label.setText(I18n.get("state_missing", missing_str))
            self.map_status_label.setToolTip(I18n.get("tooltip_missing", "\n".join(data_list)))
            self.btn_smart_fix.setText(I18n.get("btn_generate"))
            self.btn_smart_fix.setEnabled(True)

        elif state == DictState.ERROR:
            self.map_status_label.setStyleSheet("color: red; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_error"))
            error_msg = data_list[0] if data_list else "Unknown Error"
            self.map_status_label.setToolTip(I18n.get("tooltip_error", error_msg))
            self.btn_smart_fix.setText(I18n.get("btn_retry"))
            self.btn_smart_fix.setEnabled(True)

    def update_progress_ui_state(self, msg_key, args):
        """UI 层专门负责将 Key 翻译成文本并上色"""
        # 1. 查字典并格式化文本
        formatted_text = I18n.get(msg_key, *args)
        # 2. 凡是进度回调，统统是黄色处理中状态 (纯粹的逻辑！)
        self.map_status_label.setText(formatted_text)

    def handle_ocr_result(self, is_success, main_text, status_info):
        if not is_success:
            self.status_label.setText(f"⚠️ {main_text}")
            self.status_label.setStyleSheet("color: #ff5555; font-weight: bold;")
            return
        if not main_text:
            self.status_label.setText(status_info)
            self.status_label.setStyleSheet("color: yellow;")
            self.sub_window.update_text("...")
            return

        self.sub_window.update_text(main_text)
        self.status_label.setText(status_info)
        self.status_label.setStyleSheet("color: lightgray;")

        if self.auto_copy:
            QtWidgets.QApplication.clipboard().setText(main_text)
        if self.auto_save:
            try:
                with open(Config.OUTPUT_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n---- {time.ctime()} ----\n{main_text}\n")
            except Exception as e:
                logger.error(f"自动保存结果失败: {e}")

    # ================= 纯 UI 视窗/鼠标交互逻辑 =================

    def start_region_selection(self):
        self.status_label.setText(I18n.get("status_sel_region"))
        self.selection_overlay = SelectionOverlay()
        self.selection_overlay.selection_completed.connect(self.handle_region_selected)
        self.selection_overlay.show()

    def handle_region_selected(self, rect):
        self.ocr_region = (rect.x(), rect.y(), rect.width(), rect.height())
        self.status_label.setText(I18n.get("status_region_ok", rect.x(), rect.y(), rect.width(), rect.height()))
        self.show_region_overlay()

    def show_region_overlay(self):
        self.overlay = RegionOverlay(self.ocr_region)
        self.overlay.show()

    def toggle_auto_ocr(self):
        self.auto_ocr_enabled = not self.auto_ocr_enabled
        self.auto_ocr_btn.setChecked(self.auto_ocr_enabled)
        self.auto_ocr_btn.setText(I18n.get("ui_btn_auto_ocr_on" if self.auto_ocr_enabled else "ui_btn_auto_ocr_off"))
        if self.auto_ocr_enabled:
            self.ocr_timer.start(int(self.auto_ocr_interval * 1000))
            self.status_label.setText(I18n.get("status_auto_ocr_on", self.auto_ocr_interval))
        else:
            self.ocr_timer.stop()
            self.status_label.setText(I18n.get("status_auto_ocr_off"))

    def on_interval_changed(self, value):
        self.auto_ocr_interval = value / 1000.0
        self.interval_label.setText(f"{self.auto_ocr_interval:.1f}s") # 数字后缀改个 's' 通用
        if self.auto_ocr_enabled:
            self.ocr_timer.setInterval(value)
            self.status_label.setText(I18n.get("status_interval", self.auto_ocr_interval))

    def toggle_subtitle_window(self, checked):
        if checked:
            self.sub_window.show()
            self.btn_toggle_sub.setText(I18n.get("ui_btn_sub_hide"))
        else:
            self.sub_window.hide()
            self.btn_toggle_sub.setText(I18n.get("ui_btn_sub_show"))

    def toggle_auto_copy(self):
        self.auto_copy = not self.auto_copy
        self.auto_copy_btn.setChecked(self.auto_copy)
        text = I18n.get("ui_btn_auto_copy_on" if self.auto_copy else "ui_btn_auto_copy_off")
        self.auto_copy_btn.setText(text)
        self.status_label.setText(text)

    def toggle_auto_save(self):
        self.auto_save = not self.auto_save
        self.auto_save_btn.setChecked(self.auto_save)
        text = I18n.get("ui_btn_auto_save_on" if self.auto_save else "ui_btn_auto_save_off")
        self.auto_save_btn.setText(text)
        self.status_label.setText(text)

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

    def cleanup(self):
        self.sub_window.close()
        self.ocr_timer.stop()
        self.controller.cleanup()  # 委托给 Controller 清理核心资源
        logger.info("界面退出，资源清理指令已发送")


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

        # [修改] 替换为多语言词典
        self.label = QtWidgets.QLabel(I18n.get("sub_waiting"))
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
        self.apply_stealth_mode()
        # ---------------------------

    def apply_stealth_mode(self):
        if sys.platform != "win32": return
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32

            # Windows 常量
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000

            # 1. 此时获取到的 current_ex_style 一定会包含 0x80000
            current_ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            has_layered = (current_ex_style & WS_EX_LAYERED) != 0

            if has_layered:
                # 瞬间脱下“透明外套”
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_ex_style & ~WS_EX_LAYERED)

            # 2. 施加防截图隐身魔法
            result = user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), wintypes.DWORD(WDA_EXCLUDEFROMCAPTURE))

            if has_layered:
                # 3. 瞬间把“透明外套”穿回来
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_ex_style)

            if result:
                logger.info(f"[Subtitle] 字幕窗口已设置为截图隐身 (HWND: {hwnd})")
            else:
                logger.warning("[Subtitle] 字幕窗口隐身设置失败")

        except Exception as e:
            logger.warning(f"[Subtitle] API 调用出错: {e}")
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
    # [新增] 初始化日志
    setup_logging()

    app = QtWidgets.QApplication(sys.argv)
    window = FloatingOCR()
    window.show()

    # 记录程序退出
    ret_code = app.exec()
    logger.info(f"程序退出，代码: {ret_code}")
    sys.exit(ret_code)