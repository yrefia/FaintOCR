### 解析代码的两个方法：从UI(用户点击)入手；从功能(哪里用到)入手
## 注意：该版本需要在python3.12下运行

# 更改了默认ocr间隔
# 修复了bug：在内存状态为2的情况下，删除内存文件并由更高级加载触发检查，并让当前模式降低至2，会导致不可修复问题
# - 修复思路1：检查时即加载，即可放弃二次检查，保证内存硬盘状态一致
# - 修复思路2：先内存后硬盘
# - 何时可以if反向？没有任性条件时 a=1 b=2 == b=2 a=1 除非 a=1会令b不重要

# 仅添加了静态依赖图
# 加入了Loader的set_data,删除了Controller初始化时对Matcher的set_data的初始化
# handle_task现在接受任务类型和任务掩码两个参数，在判断时更加智能了（更改了Loader的判断，DictWorker的签名和Controller的调用）
# A4:
# 修改了TextMapLoader 内存缓存结构及配套的 set_data 方法；
# 优化了handle_task的代码表达，使用了类属性而非局部变量储存数据
# 嵌套了原handle_task方法进新handle_task方法内部，优化掉了类属性为大局部变量
# handle_task现在会有条件地检查，且返回值是统一的；
# 更改了handle_task和_generate_prefix_file/_merge_and_save_map/download_files方法的联动，这些方法不再在内部读取文件，且返回生成的值
# 优化了handle_task的代码表达
# 删除了I18n字典中的有关缺失和悬停的文本并删除了FloatingOCR中有关设置悬停的代码，删除了Loader的set_data方法
# 现在OCRController在每次内存不满足时都检查，且也会按需检查了，优化了worker_finished和_refresh_ui_state的代码表达
# A5:
# 精简了check/load/fix三个方法中的共同代码为_dispatch_worker
# 删除了_refresh_ui_state中多余的loading信号
# 修改了加载间隔
# A6:
# 重构了download_files方法
# 移除了全局枚举类转而直接发送信号



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

# import onnxruntime as ort
# print("当前可用的加速提供者:", ort.get_available_providers())

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
            "state_error": "⚠️ 操作失败",

            "btn_generate": "一键生成",
            "btn_ready": "已就绪",
            "btn_load_now": "立即加载",
            "btn_processing": "处理中...",
            "btn_retry": "重试",

            # --- 3. UI 界面固定文本 (setup_ui) ---
            "ui_title": "FaintOCR(2.0.2A6)",
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
            "ui_mode_2": "前缀匹配(截取)",
            "ui_mode_3": "前缀匹配(正则)",
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
            "state_error": "⚠️ Operation failed",

            "btn_generate": "Generate",
            "btn_ready": "Ready",
            "btn_load_now": "Load Now",
            "btn_processing": "Processing...",
            "btn_retry": "Retry",

            # --- 3. UI Static Text ---
            "ui_title": "FaintOCR(2.0.2A6)",
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
            "ui_mode_2": "Prefix(Len)",
            "ui_mode_3": "Prefix(Regex)",
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
        "DEFAULT_INTERVAL": 0.5,
    }
    LANG_MAP = {
        "CHS": "简体中文",
        "EN": "English",
        "JP": "日本語"
    }
    GAMES = {
        "Genshin Impact": {
            "folder": "Genshin Impact",
            "urls": {
                "TextMapCHS.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapCHS.json?inline=false",
                "TextMapEN.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapEN.json?inline=false",
                "TextMapJP.json": "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapJP.json?inline=false"
            }
        },
        "Star Rail": {
            "folder": "Star Rail",
            "urls": {
                "TextMapCHS.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapCHS.json?inline=false",
                "TextMapEN.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapEN.json?inline=false",
                "TextMapJP.json": "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/TextMap/TextMapJP.json?inline=false"
            }
        }
    }


class UIStyles:
    MAIN_WINDOW = """
        QWidget {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #2c3e50, stop:1 #34495e);
            border-radius: 12px;
            color: white; /* 让所有继承自 QWidget 的子控件默认使用白色字体 */
        }
        QLabel {
            color: white; /* 显式指定 QLabel 为白色，防止被系统默认主题覆盖 */
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
    # [修改] 增加了一个 int 参数以支持同时返回 process_type 和 target_mask
    work_finished_signal = QtCore.Signal(str, str, str, int, int)
    error_signal = QtCore.Signal(bool, str)

    def __init__(self, game_key, source_lang, target_lang, process_type, target_mask):
        super().__init__()
        self.game_key = game_key
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.process_type = process_type
        self.target_mask = target_mask
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
            logger.info(f"开始字典任务: {self.game_key} Type={self.process_type} Mask={self.target_mask}")
            self.result = TextMapLoader.handle_task(
                self.game_key,
                self.source_lang,
                self.target_lang,
                self.process_type,
                self.target_mask,
                callbacks
            )

            if self._is_cancelled:
                logger.warning("字典任务在中途已取消")
                return

            self.work_finished_signal.emit(
                self.game_key,
                self.source_lang,
                self.target_lang,
                self.process_type,
                self.target_mask
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

    # ==========================================
    # [新增] 静态数据结构：定义节点及其直接母依赖
    # 掩码规则: 1=Raw, 2=Map, 4=Prefix
    # ==========================================
    DEP_GRAPH = {
        4: 2,  # Prefix(4) 依赖 Map(2)
        2: 1,  # Map(2) 依赖 Raw(1)
        1: 0  # Raw(1) 无依赖
    }

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
    def handle_task(cls, game_key, source_lang, target_lang, process_type, target_mask, callbacks=None):
        # 1. 搭建极其纯净的临时沙箱工作内存 (不再依赖任何类属性)
        working_cache = {
            1: {},
            2: {"text_map": {}, "keys_list": []},
            4: {"prefix_dict": {}}
        }

        # 2. 调用真正的核心处理逻辑
        result_mask = cls._execute_task(
            game_key, source_lang, target_lang, process_type, target_mask, working_cache, callbacks
        )

        # 3. 提取有价值的产物 (若沙箱中为空，则转换为 None，方便后续 set_data 识别)
        text_map = working_cache[2].get("text_map") or None
        keys_list = working_cache[2].get("keys_list") or None
        prefix_dict = working_cache[4].get("prefix_dict") or None

        # 4. 返回 质检报告(掩码) + 生产成果(数据)
        return result_mask, text_map, keys_list, prefix_dict

    @classmethod
    def _execute_task(cls, game_key, source_lang, target_lang, process_type, target_mask, working_cache, callbacks):
        if callbacks is None: callbacks = {}
        # [修改] 默认的匿名函数也要适配两个参数
        report_progress = callbacks.get('progress', lambda key, args=[]: None)
        report_percent = callbacks.get('percent', lambda x: None)
        check_cancel = callbacks.get('check_cancel', lambda: False)

        # === 1. 模式解析 ===
        # process_type: 0(检查), 1(加载), 2(修复/生成)
        # target_mask: 目标层级掩码 (1=Raw, 2=Map, 4=Prefix)

        # [修改] 仅对生成/修复任务强制进行下位包含，防止依赖断裂
        if process_type >= 2 and target_mask > 0:
            target_mask = (1 << target_mask.bit_length()) - 1

        # [修改 2] 统一使用 result_mask 记录状态，彻底移除 missing_raw 等列表
        result_mask = 0

        # =========================================================
        # 阶段 1: RAW 文件 (统一探测与修复)
        # =========================================================
        if target_mask & 1:
            src_raw_file = f"TextMap{source_lang}.json"
            tgt_raw_file = f"TextMap{target_lang}.json"
            missing_raw = []

            # A. 集中探测与尝试加载 (利用遍历统一逻辑)
            for cache_key, file_name in [("src", src_raw_file), ("tgt", tgt_raw_file)]:
                file_path = cls.get_file_path(game_key, file_name)
                is_r_exist = os.path.exists(file_path)

                if process_type >= 1 and is_r_exist:
                    try:
                        with open(file_path, 'rb') as f:
                            # ✅ 直接读入沙箱
                            working_cache[1][cache_key] = orjson.loads(f.read())
                    except:
                        is_r_exist = False

                # 如果依然不存在 (没文件或加载失败)，装入待办列表
                if not is_r_exist:
                    missing_raw.append(file_name)

            # B. 集中修复与状态判定
            if process_type >= 2 and missing_raw:
                if check_cancel(): raise Exception(I18n.get("err_cancelled"))
                report_progress("prog_downloading_raw", [len(missing_raw)])

                # ✅ 完美联动：接收下载器直接返回的内存字典
                success, downloaded_data = cls.download_files(
                    game_key, missing_raw, report_progress, report_percent, check_cancel
                )
                if success and isinstance(downloaded_data, dict):
                    # 安全地将下载回来的数据补充进沙箱（有什么填什么）
                    if src_raw_file in downloaded_data:
                        working_cache[1]["src"] = downloaded_data[src_raw_file]
                    if tgt_raw_file in downloaded_data:
                        working_cache[1]["tgt"] = downloaded_data[tgt_raw_file]
                    # 最终查验：需要的 src 和 tgt 是否都在沙箱里齐备了
                    if "src" in working_cache[1] and "tgt" in working_cache[1]:
                        missing_raw = []  # 确认无误，擦除缺失标记

            if missing_raw:
                result_mask |= 1

        # =========================================================
        # 阶段 2: MAP 字典 (检查 -> 修复 -> 加载)
        # =========================================================
        if target_mask & 2:
            map_file = f"TextMap-{source_lang}to{target_lang}.json"
            map_path = cls.get_file_path(game_key, map_file)
            missing_map = []

            is_m_exist = os.path.exists(map_path)

            # B. 尝试加载 (仅当: 存在 + 目标包含Map + 非纯检查模式)
            if process_type >= 1 and is_m_exist:
                try:
                    with open(map_path, 'rb') as f:
                        data = orjson.loads(f.read())
                        # ✅ 直接读写沙箱
                        working_cache[2]["text_map"] = data
                        working_cache[2]["keys_list"] = list(data.keys())
                except:
                    is_m_exist = False  # 加载失败视为文件损坏/不存在
            if not is_m_exist:
                missing_map.append(map_file)

            # B. 尝试修复 (仅当: 不存在 + 修复模式 + 目标包含Map + Raw文件齐全)
            if process_type >= 2 and missing_map:
                src_data = working_cache[1].get("src")
                tgt_data = working_cache[1].get("tgt")
                if src_data and tgt_data:
                    if check_cancel(): raise Exception(I18n.get("err_cancelled"))
                    # ✅ 抛出 Key，没有参数就传空列表
                    report_progress("prog_generating_map", [])
                    # [关键优化] 接收返回的数据对象，而不是 boolean
                    # ✅ 完美联动：直接从沙箱中取出刚刚加载的 1 级数据传给生成器！
                    generated_data = cls._merge_and_save_map(
                        game_key, source_lang, target_lang,
                        working_cache[1].get("src"), working_cache[1].get("tgt"),  # <--- 优雅！
                        report_progress, report_percent, check_cancel
                    )
                    if generated_data is not None:
                        working_cache[2]["text_map"] = generated_data
                        working_cache[2]["keys_list"] = list(generated_data.keys())
                        missing_map = []
           # C. 判定缺失
            if missing_map:
                result_mask |= 2

        # =========================================================
        # 阶段 3: PREFIX 前缀索引 (检查 -> 修复 -> 加载)
        # =========================================================
        if target_mask & 4:
            pfx_file_tokens = [5, 8, 13, 21]
            missing_pfx_tokens = []  # 统一收集缺失的 N 和路径

            for N in pfx_file_tokens:
                p_file = f"TextMap-{source_lang}_Tk{N}.json"
                p_path = cls.get_file_path(game_key, p_file)
                is_p_exist = os.path.exists(p_path)

                # A. 尝试加载
                if process_type >= 1 and is_p_exist:
                    try:
                        with open(p_path, 'rb') as f:
                            # ✅ 直接读写沙箱
                            working_cache[4]["prefix_dict"][N] = orjson.loads(f.read())
                    except:
                        is_p_exist = False
                if not is_p_exist:
                    missing_pfx_tokens.append((N, p_path))

            if process_type >= 2 and missing_pfx_tokens:
                # ✅ 从沙箱中获取 keys_list
                keys_list = working_cache[2].get("keys_list")
                if keys_list:
                    if check_cancel(): raise Exception(I18n.get("err_cancelled"))

                    # 核心修改：一键移交所有任务给生成器
                    generated_results = cls._generate_prefix_files(
                        missing_pfx_tokens, keys_list, report_progress, report_percent, check_cancel
                    )

                    # 判定结果并擦除标记
                    if generated_results:
                        for N, prefixes in generated_results.items():
                            working_cache[4]["prefix_dict"][N] = prefixes
                        missing_pfx_tokens = []
            if missing_pfx_tokens:
                result_mask |= 4
        # =========================================================
        # 4. 结束
        # =========================================================
        return result_mask

    @classmethod
    def download_files(cls, game_key, target_files=None, progress_cb=None, percent_cb=None, cancel_cb=None):
        urls = Config.GAMES.get(game_key, {}).get("urls", {})
        if target_files:
            urls = {k: v for k, v in urls.items() if k in target_files}

        result_data = {}

        for name, url in urls.items():
            path = cls.get_file_path(game_key, name)
            tmp = path + ".tmp"

            for attempt in range(1, 4):  # 允许重试 3 次
                try:
                    if cancel_cb and cancel_cb(): return False, "已取消"

                    # 🌟 恢复：汇报正在下载的文件名和重试次数
                    if progress_cb:
                        retry_txt = f" ({attempt})" if attempt > 1 else ""
                        progress_cb("prog_downloading_file", [name, retry_txt])

                    with requests.get(url, stream=True, timeout=15, verify=False) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get('content-length', 0))
                        downloaded = 0

                        with open(tmp, 'wb') as f:
                            for chunk in r.iter_content(8192):
                                if cancel_cb and cancel_cb(): return False, "已取消"
                                f.write(chunk)
                                downloaded += len(chunk)

                                # 🌟 恢复：计算百分比并疯狂刷新 UI 进度条
                                if percent_cb and total_size > 0:
                                    percent_cb(int((downloaded / total_size) * 100))

                            f.flush()
                            os.fsync(f.fileno())  # 强制刷入磁盘，防断电损坏

                    # 原子落盘与内存加载
                    os.replace(tmp, path)
                    with open(path, 'rb') as f:
                        result_data[name] = orjson.loads(f.read())

                    break  # ✅ 成功！跳出重试循环

                except Exception as err:
                    if os.path.exists(tmp): os.remove(tmp)
                    last_err = err
            else:
                # ❌ for-else 绝招：连败3次才判定失败
                return False, f"下载 {name} 失败: {last_err}"

        return True, result_data

    @classmethod
    def _merge_and_save_map(cls, game_key, source_lang, target_lang, src_d, tgt_d, progress_cb, percent_cb, cancel_cb):
        # [修改] 签名增加了 src_d 和 tgt_d 作为参数，移除了内部的 open() 逻辑
        out_p = cls.get_file_path(game_key, f"TextMap-{source_lang}to{target_lang}.json")

        try:
            # 防御性判断
            if not src_d or not tgt_d:
                return None

            merged = {}
            total = len(src_d)

            # 加入进度和取消回调检测
            for i, (k, s) in enumerate(src_d.items()):
                if i % 10000 == 0:
                    if cancel_cb(): return None
                    percent_cb(int((i / total) * 100))

                if k in tgt_d:
                    s_tx = cls.clean_unity_rich_text(s, game_key, source_lang)
                    t_tx = cls.clean_unity_rich_text(tgt_d[k], game_key, target_lang)

                    if s_tx and t_tx:
                        if s_tx not in merged:  merged[s_tx] = set()
                        merged[s_tx].add(t_tx)

            if cancel_cb(): return None
            percent_cb(100)

            final = {k: list(v) for k, v in merged.items()}

            if cls._save_file_atomic(out_p, final, indent=True):
                logger.info(f"字典合并成功: {len(final)} 条目")
                return final
            else:
                return None

        except Exception as e:
            logger.exception(f"字典合并失败: {e}")
            return None

    @classmethod
    def clean_unity_rich_text(cls, text, game_key, current_lang):
        """
        根据特定规则清洗文本：
        1. 全局应用：标准化空格、去标签、替换省略号
        2. 条件应用（仅当以#开头）：去#、换昵称、处理性别、处理注音
        """
        if not text:
            return ""

        text = text.replace(r'\n', ' ').replace(r'\u00A0', ' ')
        text = re.sub(r'<[^>]*>', '', text)

        if game_key == "Genshin Impact":
            text = text.replace('…', '···')
            if text.startswith('#'):
                text = text[1:]
                nicknames = {"CHS": "旅行者", "EN": "Traveler", "JP": "旅人"}
                nickname = nicknames.get(current_lang, "Traveler")
                text = text.replace('{NICKNAME}', nickname)
                text = re.sub(r'\{F#([^}]*)}', r'\1', text)
                text = re.sub(r'\{M#[^}]*}', '', text)
            text = re.sub(r'\{RUBY#(?:\[[^]]*])?([^}]*)}', r'(\1)', text)

        elif game_key == "Star Rail":
            text = text.replace('…', '...')
            nicknames = {"CHS": "开拓者", "EN": "Trailblazer", "JP": "開拓者"}
            nickname = nicknames.get(current_lang, "Trailblazer")
            text = text.replace('{NICKNAME}', nickname)
            text = re.sub(r'\{F#([^}]*)}', r'\1', text)
            text = re.sub(r'\{M#[^}]*}', '', text)
            text = re.sub(r'\{RUBY_B#([^}]*)}([^{]*)\{RUBY_E#}', r'\2(\1)', text)

        return text.strip()

    @classmethod
    def _generate_prefix_files(cls, missing_tokens, keys_list, progress_cb, percent_cb, cancel_cb):
        """
        批量生成前缀文件
        :param missing_tokens: List[Tuple[int, str]] 包含 (N, file_path) 的列表
        :param keys_list: 原始字典键列表
        :return: Dict[int, List[str]] 成功生成的前缀字典，失败返回 None
        """
        if not missing_tokens or not keys_list:
            return {}

        try:
            # 1. 集中执行全局分词 (耗时操作仅执行一次)
            if cancel_cb(): return None
            progress_cb("prog_preparing_tokens", [])
            tokenized_data = [cls._tokenize(k) for k in keys_list]

            results = {}
            total = len(tokenized_data)

            # 2. 批量生成缺失的前缀文件
            for N, file_path in missing_tokens:
                if cancel_cb(): return None
                progress_cb("prog_generating_prefix", [N])

                prefixes = []
                for i, tokens in enumerate(tokenized_data):
                    if i % 50000 == 0:
                        if cancel_cb(): return None
                        percent_cb(int((i / total) * 100))

                    # 截断并拼接
                    prefixes.append("".join(tokens[:N]))

                if cancel_cb(): return None
                percent_cb(100)

                # 调用原子写入
                if cls._save_file_atomic(file_path, prefixes, indent=False):
                    logger.debug(f"前缀索引生成成功: Tk{N}")
                    results[N] = prefixes
                else:
                    return None  # 如果有任何一个文件写入失败，直接判定整体任务失败

            return results

        except Exception as e:
            logger.error(f"批量前缀生成发生严重失败: {e}")
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
            ocr_engine_std = self.task_data.get('ocr_engine_std')
            ocr_engine_light = self.task_data.get('ocr_engine_light')
            text_matcher = self.task_data.get('text_matcher')
            match_mode = self.task_data.get('match_mode', 0)
            similarity_threshold = self.task_data.get('similarity_threshold', 60)
            monitor = self.task_data.get('monitor')

            # [Log] 记录开始 (Debug级别)
            logger.debug("OCRWorker 开始处理图片")
            # 支持在子线程中截图

            if monitor is not None:
                with mss.mss() as sct:
                    sct_img = sct.grab(monitor)
                    img_np = np.array(sct_img)
                    img_cv = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

            if img_cv is None:
                raise ValueError("Image data is missing")

            # ========================================================
            # Params: 图像预处理 (提速优化)
            # 1. 灰度化：将 BGR 三通道转为单通道，数据量减少 2/3，显著提升推理速度
            # 注意：RapidOCR (ONNX) 内部虽有处理，但显式转换通常更快且兼容性更好
            #if len(img_cv.shape) == 3:
            #    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            # 2. 二值化 (可选)：将图像变为纯黑白
            # 说明：这能进一步提速，但游戏字体通常带有抗锯齿、阴影或半透明背景。
            # 暴力二值化(OTSU)可能会导致文字边缘锯齿化，反而降低识别率。
            # 建议：先仅使用灰度化。如果速度仍不满足，再尝试取消下面这行的注释。
            #    _, img_cv = cv2.threshold(img_cv, 191, 255, cv2.THRESH_BINARY)
            #    _, img_cv = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # ========================================================

            # ========================================================
            # --- 新增：使用 Alpha 混合对图像进行预处理 ---
            # 1. 创建一个与原图尺寸完全相同的纯色遮罩 (这里以中灰色 100, 100, 100 为例)
            overlay = np.full(img_cv.shape, 100, dtype=np.uint8)
            # 2. 设定 Alpha 混合的权重
            # 达到 150/255 的遮罩不透明度
            alpha_mask = 150 / 255.0  # 遮罩占比 (58.8%)
            alpha_img = 1.0 - alpha_mask  # 原图占比 (41.2%)
            # 3. 利用 OpenCV 的 addWeighted 瞬间完成全矩阵的 Alpha 混合计算
            # 底层数学公式依然是: dst = img_cv * alpha_img + overlay * alpha_mask + 0
            img_cv = cv2.addWeighted(img_cv, alpha_img, overlay, alpha_mask, 0)
            # img_cv = cv2.addWeighted(img_cv, alpha_img, overlay, alpha_mask, 0)
            # ========================================================

            # ========================================================
            # 直接将所有像素值乘以 0.5，完美等效于和黑色混合，速度极快
            # img_cv = cv2.convertScaleAbs(img_cv, alpha=0.6)
            # ========================================================

            # ========================================================
            # 3. 【新增核心杀招】：物理缩放
            # 如果游戏的字幕其实很大，完全可以把图片缩小一倍再送给 OCR。像素量变成原来的 1/4，检测(Det)速度会翻倍！
            # 你可以尝试 fx=0.7, fy=0.7 或者 fx=0.5, fy=0.5，寻找速度和识别率的完美平衡点
            # img_cv = cv2.resize(img_cv, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
            # ========================================================

            # cv2.imwrite(r'./processed_image.jpg', img_cv)

            # --- 计时：截图完成---
            t_process1 = time.perf_counter()
            capture_cost = t_process1 - t_start

            # 1. 先让轻量级引擎 (如 640 边长限制) 全速跑一遍
            raw_text = self.run_rapidocr(ocr_engine_light, img_cv)

            # 2. 如果轻量级引擎什么都没看出来 (漏检了，或者确实没字)
            if not raw_text or raw_text.strip() == "":
                logger.trace("轻量级检测未发现文本，触发标准模型兜底识别...")
                # 扔给标准引擎 (如 1280 边长限制) 再仔细看一遍
                raw_text = self.run_rapidocr(ocr_engine_std, img_cv)

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
            logger.debug(f"OCR完成: {subtitle_text}\n{status_info}")
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

    # 修改 __init__ 方法的签名，并增加 len_cache_size 属性
    def __init__(self, cache_size=3, len_cache_size=10):  # <--- [修改] 增加 len_cache_size，默认给10条足够了
        self.text_map = {}
        self.cache = {}
        self.cache_size = cache_size

        self.len_cache_size = len_cache_size  # <--- [新增] 长度截取缓存的最大容量
        self.len_cache = {}  # 现在的结构变为: { target_len: {'data': [...], 'hits': int, 'last_accessed': float} }

        # [新增] 逻辑时钟与衰减因子
        self.global_step = 0
        self.decay_factor = 0.9

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

        # <--- [修改] 增加新模式的分发
        if mode == 1:
            result = self._match_full_text(ocr_text, threshold)
        elif mode == 2:
            result = self._match_prefix_by_length(ocr_text, threshold)
        elif mode == 3:
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

    def _evict_len_cache(self):
        """最优算法：基于逻辑距离的指数衰减淘汰"""
        lowest_key = None
        lowest_score = float('inf')

        for k, v in self.len_cache.items():
            # 计算距离上次被命中的“逻辑距离”
            distance = self.global_step - v['last_step']

            # 计算衰减后的即时权重 (S * a^distance)
            current_weight = v['score'] * (self.decay_factor ** distance)

            if current_weight < lowest_score:
                lowest_score = current_weight
                lowest_key = k

        if lowest_key is not None:
            del self.len_cache[lowest_key]

    def _match_prefix_by_length(self, ocr_text, similarity_threshold=60):
        if not self.text_map or not ocr_text.strip():
            return None, None, 0

        target_len = len(ocr_text)
        # [新增] 每次调用，全局逻辑时钟推进一步
        self.global_step += 1

        if target_len not in self.len_cache:
            if len(self.len_cache) >= self.len_cache_size:
                self._evict_len_cache()

            # 初始化新缓存，初始权重为 0
            self.len_cache[target_len] = {
                'data': [k[:target_len] for k in self.keys_list],
                'score': 0.0,
                'last_step': self.global_step
            }

        # 获取该缓存的引用
        cache_item = self.len_cache[target_len]
        # 1. 计算距离上次命中过去了多少步
        distance = self.global_step - cache_item['last_step']
        # 2. 衰减历史权重，并为本次命中 +1
        cache_item['score'] = cache_item['score'] * (self.decay_factor ** distance) + 1.0
        # 3. 更新最后访问步数
        cache_item['last_step'] = self.global_step

        return self._process_fuzzy_results(ocr_text, cache_item['data'], similarity_threshold)

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
        self.len_cache.clear()  # <--- [新增] 清空缓存
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
    # ==========================================
    # [新增] 静态路由表：UI模式 -> 内存需求掩码
    # ==========================================
    MODE_REQUIREMENTS = {
        0: 0,
        1: 2,  # 模式1: 只需要 Map(2)
        2: 2,  # 模式2: 只需要 Map(2)
        3: 2 | 4  # 模式3: 需要 Map(2) + Prefix(4)
    }

    # 定义向 UI 通信的信号
    dict_progress_signal = QtCore.Signal(str, list)  # 字典下载/合并进度文本
    dict_percent_signal = QtCore.Signal(int)  # 字典进度条百分比

    # 统一下发 UI 状态：(业务状态枚举, 缺失文件列表, 当前层级, 目标层级)
    ui_state_signal = QtCore.Signal(str, list, int, int)
    ui_lock_signal = QtCore.Signal(bool)  # 锁定/解锁界面操作

    ocr_result_signal = QtCore.Signal(bool, str, str)  # OCR完成信号

    def __init__(self):
        super().__init__()
        # --- 业务状态 ---
        self.current_game = list(Config.GAMES.keys())[0]
        lang_codes = list(Config.LANG_MAP.keys())
        self.source_lang = lang_codes[0]  # "CHS"
        self.target_lang = lang_codes[1]  # "EN"
        self.match_mode = 0
        self.similarity_threshold = 60

        self.text_matcher = TextMatcher(cache_size=3, len_cache_size=10) # <--- 显式标注我们给它预留了 10 条缓存

        # [核心修改] 废除所有 missing_xxx 列表，仅用掩码跟踪状态
        self.current_data_mask = 0  # 内存中已加载的数据

        try:
            # 1. 实例化标准引擎 (负责兜底检测 + 最终的高精度识别)
            self.ocr_engine_std = RapidOCR(
                intra_op_num_threads=4
            )
            # 2. 实例化轻量引擎 (专门用于第一波快速筛选)
            # 可以传入一个更轻量的模型路径 det_model_path="..."，或者直接使用更小的边长限制
            self.ocr_engine_light = RapidOCR(
                det_limit_side_len=1280,  # 会导致部分文本不可识别
                det_limit_type='max',  # 和上条联合使用
                intra_op_num_threads=4  # 可以小幅提升速度
            )
        except Exception as e:
            logger.error(f"RapidOCR 初始化失败: {e}")
            self.ocr_engine_std = None
            self.ocr_engine_light = None

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

    def set_languages(self, source_lang, target_lang):
        # 直接赋值，不需要去 Config.LANG_MAP 里查了
        self.source_lang = source_lang
        self.target_lang = target_lang
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
        if self.ocr_engine_std is None or self.ocr_engine_light is None:
            self.ocr_result_signal.emit(False, "OCR 引擎未初始化", "")
            return

        x, y, w, h = region
        monitor = {"top": y, "left": x, "width": w, "height": h}
        task_data = {
            'monitor': monitor,
            'text_matcher': self.text_matcher,
            'match_mode': self.match_mode,
            'similarity_threshold': self.similarity_threshold,
            'ocr_engine_std': self.ocr_engine_std,  # 标准引擎
            'ocr_engine_light': self.ocr_engine_light  # 轻量引擎
        }
        self.task_manager.submit_task(task_data)

    def _dispatch_worker(self, process_type):
        """
        [新增] 统一调度 DictionaryWorker 的核心方法
        :param process_type: 0(检查), 1(加载), 2(修复)
        """
        # 1. 统一停止旧任务
        self._stop_previous_worker()

        # 2. 统一计算目标掩码和缺失掩码
        required_mask = self.MODE_REQUIREMENTS.get(self.match_mode, 0)
        mem_missing = required_mask & ~self.current_data_mask

        # 3. 统一分发 UI Loading 状态
        # (只有 process_type 为 1或2 时才切状态，0是后台静默检查)
        if process_type > 0:
            # 【修改投递】直接发字符串
            self.ui_state_signal.emit("LOADING", [], self.current_data_mask, required_mask)

        # 4. 统一按需实例化并启动 Worker
        if mem_missing > 0:
            self.dict_worker = DictionaryWorker(
                self.current_game, self.source_lang, self.target_lang, process_type, mem_missing
            )

            # 基础信号绑定 (全模式通用)
            self.dict_worker.work_finished_signal.connect(self._on_worker_finished)
            self.dict_worker.error_signal.connect(self._on_worker_error)

            # 差异化信号绑定 (仅修复模式需要进度条)
            if process_type == 2:
                self.dict_worker.progress_signal.connect(self.dict_progress_signal)
                self.dict_worker.percent_signal.connect(self.dict_percent_signal)

            self.dict_worker.start()

    def run_check(self):
        """后台静默查漏"""
        self._dispatch_worker(process_type=0)

    def run_smart_fix(self):
        """一键修复：需要阻塞定时器并锁住 UI 交互"""
        self.auto_load_timer.stop()
        self.ui_lock_signal.emit(True)
        self._dispatch_worker(process_type=2)

    def cleanup(self):
        """清理资源"""
        self.task_manager.cancel_all()
        self.auto_load_timer.stop()
        self.text_matcher.clear_cache()
        self._stop_previous_worker()

    # ================= 内部业务逻辑 =================

    def _reset_dict_state(self):
        self.current_data_mask = 0
        self.text_matcher.set_data({}, [], {})
        self.auto_load_timer.stop()
        self._refresh_ui_state()

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
        """自动触发的内存加载"""
        self._dispatch_worker(process_type=1)

    def _on_worker_finished(self, handle_game, handle_source_lang, handle_target_lang, process_type, target_mask):
        self.ui_lock_signal.emit(False)
        if (
                handle_game != self.current_game or handle_source_lang != self.source_lang or handle_target_lang != self.target_lang):
            logger.warning("丢弃过期 Worker 数据")
            return

        # [修复] 完美适配 Loader 返回的 4 个参数
        result_mask, text_map, keys_list, prefix_dict = self.dict_worker.result

        # 1. 严格的内存状态管理
        if process_type != 0:
            self.text_matcher.set_data(text_map, keys_list, prefix_dict)
            success_mask = target_mask & ~result_mask
            self.current_data_mask |= success_mask

        # 2. 将 Worker 的质检结果抛给 UI 刷新器进行最终裁定
        self._refresh_ui_state(worker_check_result=result_mask)

    def _on_worker_error(self, success, msg):
        self.ui_lock_signal.emit(False)
        if not success:
            # ✅ 修改：直接把错误信息放进列表里，投递给主状态机！
            self.ui_state_signal.emit("ERROR", [msg], 0, 0)

    def _refresh_ui_state(self, worker_check_result=None):
        """
        [重构] 渲染器方法：完全通过当前内存状态和按需传来的校验结果决定 UI
        """
        if self.match_mode == 0:
            self.ui_state_signal.emit("STANDBY", [], 0, 0)
            return

        required_mask = self.MODE_REQUIREMENTS.get(self.match_mode, 0)
        mem_missing = required_mask & ~self.current_data_mask

        # 场景 1: 内存已经满足，万事大吉
        if mem_missing == 0:
            self.ui_state_signal.emit("READY", [], self.current_data_mask, required_mask)
            return

        # 场景 2: 内存不足，且还不知道硬盘情况 (通常是刚切换 UI 模式)
        if worker_check_result is None:
            self.run_check()  # 发起硬盘查漏
            return

        # 场景 3: 内存不足，但 Worker 刚刚汇报了硬盘查勘/加载/修复的结果
        if worker_check_result > 0:
            # 【修改投递】
            self.ui_state_signal.emit("MISSING", [worker_check_result], 0, 0)
        else:
            # 【修改投递】
            self.ui_state_signal.emit("PENDING", [], self.current_data_mask, required_mask)
            self.auto_load_timer.start(1000)


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

        # === [关键修改 1]：先创建大脑(Controller)，再创建脸部(UI) ===
        self.controller = OCRController()
        # UI 初始化现在可以安全地读取 self.controller 里的值了
        self.setup_ui()
        self._connect_controller_signals()

        self.sub_window = SubtitleWindow()

        self.setup_timers()
        self.apply_stealth_mode()

        QtWidgets.QApplication.instance().aboutToQuit.connect(self.cleanup)

        # 启动时执行一次快速检查 (委托给 Controller)
        self.controller._refresh_ui_state()

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
                logger.info(f"[Main] 主窗口已设置为截图隐身 (HWND: {hwnd})")
            else:
                logger.warning("[Main] 主窗口隐身设置失败")

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
        title_lbl.setStyleSheet("font-weight:600; font-size:14px;") # 删除了 color: white;
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
        self.game_selector.setCurrentText(self.controller.current_game)
        self.game_selector.currentIndexChanged.connect(self.on_game_changed)
        self.game_selector.setStyleSheet(UIStyles.COMBO_BOX)
        self.game_selector.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        row_game.addWidget(self.game_selector)
        dict_layout.addLayout(row_game)

        row_lang = QtWidgets.QHBoxLayout()
        row_lang.addWidget(QtWidgets.QLabel(I18n.get("ui_lbl_source")))  # [多语言] 源:
        # 初始化源语言下拉框
        self.combo_source = QtWidgets.QComboBox()
        self.combo_source.setStyleSheet(UIStyles.COMBO_BOX)
        for code, text in Config.LANG_MAP.items():
            self.combo_source.addItem(text, code)  # text是"简体中文", code是"CHS"
        self.combo_source.setCurrentIndex(self.combo_source.findData(self.controller.source_lang))
        self.combo_source.currentIndexChanged.connect(self.on_language_changed)

        row_lang.addWidget(self.combo_source)
        row_lang.addWidget(QtWidgets.QLabel("➜"))  # 符号无需翻译
        row_lang.addWidget(QtWidgets.QLabel(I18n.get("ui_lbl_target")))  # [多语言] 译:
        # 初始化目标语言下拉框
        self.combo_target = QtWidgets.QComboBox()
        self.combo_target.setStyleSheet(UIStyles.COMBO_BOX)
        for code, text in Config.LANG_MAP.items():
            self.combo_target.addItem(text, code)
        self.combo_target.setCurrentIndex(self.combo_target.findData(self.controller.target_lang))
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
        self.match_slider.setRange(0, 3)
        self.match_slider.setValue(self.controller.match_mode)
        self.match_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.match_slider.setTickInterval(1)
        self.match_slider.valueChanged.connect(self.on_match_mode_changed)

        self.match_label = QtWidgets.QLabel(I18n.get(f"ui_mode_{self.controller.match_mode}"))
        self.match_label.setFixedWidth(80)
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.threshold_slider.setValue(self.controller.similarity_threshold)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)

        self.threshold_label = QtWidgets.QLabel(f"{self.controller.similarity_threshold}%")
        self.threshold_label.setFixedWidth(40)
        self.threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.status_label.setWordWrap(True)  # <--- 新增：开启自动换行
        # 修改：将垂直策略从 Fixed 改为 Minimum，允许高度随多行文字自动增长
        self.status_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Minimum)
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
        # 1. 直接获取隐形的内部代码 (如 "CHS", "EN")
        current_source_code = self.combo_source.currentData()
        current_target_code = self.combo_target.currentData()

        # 2. 如果源语言和目标语言相同，执行互换
        if current_source_code == current_target_code:
            self.combo_source.blockSignals(True)
            self.combo_target.blockSignals(True)

            sender = self.sender()
            if sender == self.combo_source:
                prev_source_code = self.controller.source_lang
                # 让 target 下拉框自动选中隐形数据为 prev_source_code 的那项
                self.combo_target.setCurrentIndex(self.combo_target.findData(prev_source_code))
                current_target_code = prev_source_code

            elif sender == self.combo_target:
                prev_target_code = self.controller.target_lang
                # 让 source 下拉框自动选中隐形数据为 prev_target_code 的那项
                self.combo_source.setCurrentIndex(self.combo_source.findData(prev_target_code))
                current_source_code = prev_target_code

            self.combo_source.blockSignals(False)
            self.combo_target.blockSignals(False)

        # 3. 把纯正的内部代码传给 Controller
        self.controller.set_languages(current_source_code, current_target_code)

    # 1. 匹配模式滑动
    def on_match_mode_changed(self, value):
        modes = [I18n.get("ui_mode_0"), I18n.get("ui_mode_1"), I18n.get("ui_mode_2"), I18n.get("ui_mode_3")]
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

        # 【直接比对字符串】
        if state == "STANDBY":
            self.map_status_label.setStyleSheet("color: gray; font-size:11px;")
            self.map_status_label.setText(I18n.get("state_standby"))
            self.btn_smart_fix.setText(I18n.get("btn_generate"))
            self.btn_smart_fix.setEnabled(False)

        elif state == "READY":
            self.map_status_label.setStyleSheet("color: lightgreen; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_ready", current_lvl))
            self.btn_smart_fix.setText(I18n.get("btn_ready"))
            self.btn_smart_fix.setEnabled(False)

        elif state == "PENDING":
            self.map_status_label.setStyleSheet("color: #8be9fd; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_pending", current_lvl, target_lvl))
            self.btn_smart_fix.setText(I18n.get("btn_load_now"))
            self.btn_smart_fix.setEnabled(True)

        elif state == "LOADING":
            self.map_status_label.setStyleSheet("color: #f1c40f; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_loading", current_lvl, target_lvl))
            self.btn_smart_fix.setText(I18n.get("btn_processing"))
            self.btn_smart_fix.setEnabled(False)

        elif state == "MISSING":
            self.map_status_label.setStyleSheet("color: #ff5555; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_missing", data_list[0]))
            self.btn_smart_fix.setText(I18n.get("btn_generate"))
            self.btn_smart_fix.setEnabled(True)

        elif state == "ERROR":
            self.map_status_label.setStyleSheet("color: red; font-size:11px; font-weight:bold;")
            self.map_status_label.setText(I18n.get("state_error"))
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

        self.resize(1500, 150)
        self.setMinimumSize(80, 40)

        # 初始居中显示
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move((screen.width() - 1500) // 2, screen.height() - 160)

        self._drag_pos = None
        self._resize_mode = None
        self._resize_margin = 8  # 边缘检测距离

        self.apply_stealth_mode()

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