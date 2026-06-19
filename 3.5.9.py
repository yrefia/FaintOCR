# coding=utf-8
# FaintOCR 3.5.9
# Single-file integration of Codeia 2.2.3 business logic and floating-ui-v16.
# Generated as a new file; source files remain unchanged.
### 解析代码的两个方法：从UI(用户点击)入手；从功能(哪里用到)入手
## 注意：该版本需要在python3.12下运行

# 3.0.0
# 重构了整个UI！

# 3.0.1
# 控制栏新增当前匹配模式，位于游戏名和语言左侧。
# 字幕窗口最小宽度由 760 调整为 980。
# “OCR 状态”现在显示手动待命/识别中、自动开关、检测开关状态。
# 波形仅在 OCR 开启或手动识别过程中动态播放，关闭时保持静止灰色。
# 悬浮球改为 Windows 任务栏主窗口，并设置任务栏图标。
# 从任务栏关闭悬浮球会执行正常退出及资源清理。

# 3.0.2 Pass

# 3.0.3
# 将"MENU_REQUIRED_SPACE"作为了类常量。
# 调整了"DETECT": "debounce_delay"的值为0.4。
# 调整了"PRE_OCR_CROP_RULES": "padding_top"的值为0。
# 调整了"TEXT_HEIGHT_FILTER_RULES": "Genshin Impact": "height_max"的值为42

# 3.0.4
# 新增统一的 Config.DEFAULTS 和 Config.UI_RANGES。
# 控制器、协调层、设置 UI 均从统一配置读取默认值。
# 检测灵敏度现在正确初始化并显示为 50%。
# 自动 OCR 频率改为 次/4秒：范围：1~20；默认：8 次/4秒，对应原来的 0.5 秒/次；1 次/4秒 对应 4 秒/次；20 次/4秒 对应 0.2 秒/次
# 检测 OCR 频率范围调整为 2~20 次/秒。
# 状态提示同步改用 次/4秒。

# 3.0.5
# 设置面板顶部新增 A. 基础设置，包含字幕字号调整。
# 原设置编号顺延为 B~E。
# 字号只影响字幕正文，不影响 UI、状态文字及 Debug 字体。
# 默认字幕字号从 12pt 增大至 14pt。
# 默认字幕窗口不透明度调整为 80%，透明度滑条位置同步。
# 字号、透明度默认值及透明度范围均使用统一配置来源。
# 在滑块或下拉框上滚动鼠标滚轮时，只滚动设置页面，不再误改参数。
# 右侧滚动条改为主题亮紫色，增加亮色轨道和悬停效果。

# 3.0.6
# 设置面板滚动条改为更低饱和度的暗紫灰色，悬停时适度提亮。
# 自动复制与自动保存改为整块可点击的切换按钮：明确显示“已开启/已关闭”；开启后使用克制的主题色突出；点击区域更大、更醒目
# 状态显示已移出滚动区域，固定在设置面板底部。
# 无论设置页面滚动至何处，状态栏始终可见。
# 控制器锁定设置时，新的输出切换按钮也会同步禁用。

# 3.0.7
# 回滚输出按钮禁用逻辑：控制器锁定其他设置时，自动复制和自动保存仍可操作。
# 滚动条适度提升饱和度和亮度：比 3.0.6 更接近主题紫色。仍保持低调，不抢夺设置内容焦点。
# 优化底部状态显示：删除重复的状态指示点。移除类似设置卡片的背景和边框。使用轻量顶部分隔线区分滚动区。状态文本居中显示。状态栏仍固定在设置面板底部。

# 3.0.8
# 基础设置新增“界面语言”选项：简体中文，English
# 切换语言后即时刷新：设置面板全部文本，游戏与语言名称，输出开关，状态栏，悬浮字幕控制栏，后续日志与运行状态
# 所有日志调用均已接入 I18n。
# 中英文词典各有 140 个键，键集合完全一致。
# 调整了"DEFAULTS": "detect_frequency"的值为10

# 3.1.0
# 检测模式新增“检测到变化 -> 正式提交 OCR”耗时。
# 所有 OCR 耗时统一由控制器格式化，并显示本次总用时与近 10 次平均用时。

# 3.1.1
# 修复多行 OCR 耗时统计在调试输出中按单行高度绘制，导致文字重叠的问题。

# 3.1.2
# 悬浮窗实时状态只显示本次耗时，完整耗时与近 10 次平均继续保留在调试输出中。

# 3.1.3
# 为悬浮球新增符合现有 UI 风格的右键菜单，当前提供退出程序功能。

# 3.1.4
# 设置面板打开时，可拖动面板的非交互区域来移动悬浮球与设置面板组合体。
# 调整了"TEXT_HEIGHT_FILTER_RULES": "Genshin Impact": "height_max"的值为45

# 3.1.5
# OCR 完成日志统一由控制器在生成最终耗时信息后输出，并在每次流程结束后留出空行。
# "setup_logging"删除了"compression="zip"# 压缩旧日志"

# 3.1.6i
# 略微优化了悬浮窗图钉图标的形状

# 3.2.0
# 移除了文本匹配拼接多个高相似度文本的逻辑

# 3.2.1
# 原神原始文本文件支持合并下载主 TextMap 与 TextMap_Medium。

# 3.2.2 (+Gemini)
# 原始文本下载改用内存缓冲，合并成功后再原子写入最终文件。

# 3.2.3
# 原始文本下载状态新增已下载大小、总大小与实时下载速率。

# 3.2.4
# 下载进度新增游戏与文件名，并仅显示在设置面板状态栏。

# 3.2.5
# 重构设置面板、悬浮窗状态栏和悬浮窗 Debug 框的信息路由。
# 悬浮窗单行状态新增优先级保护，避免关键消息被高频状态覆盖。

# 3.2.6
# 悬浮状态栏实时显示下载详情，完善字典 Ready 覆盖与 OCR 完成摘要。
# 悬浮 Debug 框新增检测差异、黄线裁剪和文本高度过滤实时信息。

# 3.2.7
# 检测差异仅在触发与复核时输出，OCR 总耗时排除检测耗时并在悬浮状态栏显示模块明细。
# 匹配模式关闭：不显示黄线裁剪及高度过滤信息。
# 匹配模式开启、黄线裁剪关闭：显示黄线裁剪已关闭。
# 匹配模式开启、高度过滤关闭：每次 OCR 仅显示一次“高度过滤：已关闭”，不会逐条刷屏。
# 检测差异仅在触发及复核时输出。
# OCR 单次及近十次平均总耗时不包含检测耗时。
# 悬浮状态栏显示截图、OCR、匹配及总耗时。

# 3.3.0
# 字典任务期间仅禁用“游戏、语言与匹配”区域。
# 其他设置、悬浮球及悬浮窗保持可操作。
# 被禁用区域会整体变暗，并显示“字典任务处理中，此区域暂不可修改”提示。

# 3.3.1
# 字典阶段信息、处理百分比、下载详情及 LOADING/READY/MISSING/ERROR 等状态，均同步显示于设置界面和悬浮窗状态栏。
# 字典就绪后，“一键生成匹配数据”按钮会禁用，并显示绿色“匹配数据已就绪，无需重复生成”状态。
# 控制器增加兜底：已就绪时意外触发不会锁定或启动空任务；任务运行中重复触发也不会终止并重启任务。

# 3.3.2
# 根因：检测模式中，状态栏把“检测→触发OCR”的时间误识别为 OCR 分计时间。
# 修复：仅解析“本次”行，并按 | 拆分后严格匹配完整字段名。
# 保持原有计时、调试框与信号结构不变。
# 调整了"TEXT_HEIGHT_FILTER_RULES": "Genshin Impact"/"Star Rail": "height_max"的值为60

# 3.3.3
# 匹配、黄线裁剪或高度过滤关闭时跳过对应处理及其 Debug 明细。
# 注释掉了"class TextMapLoader": "def clean_unity_rich_text"中的“# text = text.replace(r'\n', ' ').replace(r'\u00A0', ' ')”

# 3.3.4
# 已完全删除：
# UI 中的“前缀匹配（正则）”选项及中英文文案。
# 模式 3 及其数据需求配置。
# _match_prefix_text 匹配方法、分词器及 TkN 候选数据。
# Prefix 数据层、prefix_dict、掩码 4。
# TextMap-CHS_TkN.json 类文件的检查、加载与生成逻辑。
# TkN 生成进度及日志文案。

# 3.4.0
# 文本处理拆分为基础清洗、匹配清洗和按需显示清洗三层。
# 基础映射与静态匹配候选写入硬盘；昵称、主角性别等动态候选仅在内存中生成。
# OCR 文本与候选文本统一执行匹配清洗，匹配成功后再动态渲染原文与译文。

# 3.4.1
# 主角性别选择框移动至玩家昵称输入框左侧。
# 主角性别或玩家昵称修改后，在设置面板状态栏显示更新通知。
# 删除所有 UI Tooltip 设置逻辑。
# 将“cls._save_file_atomic(static_path, static_candidates, indent=True)”中的"indent"改为"True"

# 3.4.2
# 主角性别与玩家昵称按“游戏 + 源语言”分别维护本地化默认值。
# 切换游戏或源语言时自动恢复对应值；用户修改后更新当前组合的内存默认值。
# 个性化配置表保留清晰的数据边界，为后续本地持久化配置作准备。

# 3.4.3
# 悬浮窗主显示框与调试框改用透明只读文本控件，支持鼠标框选复制。
# 调试框文字之外的空白区域仍可拖动整个悬浮窗。
# 控制栏复制按钮点击后短暂显示完成标记并禁用，随后自动恢复。

# 3.4.4
# 悬浮窗主显示框恢复为不可框选文本，仅调试框保留鼠标框选复制能力。
# 复制按钮完成态改为浅灰圆形徽标与细线对勾，若干秒后恢复复制图标。

# 3.4.5
# 优化悬浮窗控制栏复制反馈：使用符合暗色紫色主题的徽标、光晕与亮紫对勾。
# 复制完成态快速淡入、短暂停留后淡出，反馈期间继续禁用重复点击。

# 3.4.6
# 简化悬浮窗复制成功反馈：保留原有悬停圆形点击区域，不改变其表现。
# 点击后仅将复制图标替换为成功对勾，不创建徽标、光晕或额外动画。

# 3.4.7
# 悬浮窗状态栏中间的匹配模式控件显示字典内存满足状态。
# 生成匹配数据按钮按匹配关闭、加载中、文件缺失与内存满足状态切换颜色；仅文件缺失时可点击。

# 3.4.8
# Unified BASE_DIR as the single application path root for both script and packaged exe runs.
# Runtime icon now loads Icons/logo_2b.png via a BASE_DIR-relative path.

# 3.5.0
# 统一“生成匹配数据”按钮边框为标准按钮边框色；仅可点击时悬停显示主题色边框。
# 按钮文字改为当前字典状态文案：待机、已就绪、即将加载、处理中、缺失或错误。

# 3.5.1
# 将“text = text.replace('…', '··')”替换为了“text = text.replace('…', '·')”
# 将“text = text.replace('…', '..')”替换为了“text = text.replace('…', '.')”

# 3.5.2
# 界面语言下拉框始终显示“简体中文”和“English”，不随当前界面语言翻译。
# 源语言与目标语言任一方被改成相同语言时，另一方自动恢复为本次修改前的语言。

# 3.5.3
# 前缀截取匹配时使用“文本长度 + 2”的候选前缀文本进行相似度匹配。

# 3.5.4
# 检测模式停止时仅断开当前 worker 的已连接槽函数，避免快速开关产生 disconnect 警告。
# 快车道 debounce 阶段不再重新计算检测评分，仅捕获并更新 baseline。
# 调整了"TEXT_HEIGHT_FILTER_RULES": "Star Rail": "height_min"的值为24

# 3.5.5
# OCR 任务提交写入悬浮调试框；轻量模型未检出触发兜底时同步通知调试框与悬浮状态栏。

# 3.5.6
# 调试框时间戳精确到毫秒；手动 OCR 以 pending 任务数驱动显示状态，连点每次触发提交。

# 3.5.7
# 设置面板下拉展开列表使用更高不透明度背景；检测旧 session 结果继续展示，只跳过检测完成回调。

# 3.5.8 (+Deepseek)
# 设置面板下拉框恢复 3.5.6 样式。
# 在“combo = QtWidgets.QComboBox()”后新增了“combo.view().setStyleSheet("background: #252936;")”，成功解决了下拉框背景透明的问题。
# 在“logger.add”中删除了“rotation="00:00",# 每天午夜轮转”，成功解决了过期日志未能在预期内被删除的问题。

# 3.5.9
# 移除了OCR标准模型兜底识别



import math
import re
import sys
import os
import time
import ctypes
from collections import deque
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from ctypes import wintypes
import orjson
import mss
import mss.tools
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    Qt,
    QTimer,
    Signal,
    QPropertyAnimation,
    QParallelAnimationGroup,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QCursor,
)
from PySide6.QtWidgets import QApplication, QWidget
from rapidocr_onnxruntime import RapidOCR
import cv2
import numpy as np
from rapidfuzz import process, fuzz
import requests
from loguru import logger  # <--- [新增]

# import onnxruntime as ort
# print("当前可用的加速提供者:", ort.get_available_providers())

# ====== 路径获取逻辑修正 ======
if getattr(sys, "frozen", False):
    # 如果是打包后的 exe 运行，使用 exe 所在的实际目录
    # sys.executable 指向 D:\xxx\xxx.exe
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # 如果是普通脚本运行，使用当前文件所在目录
    BASE_DIR = Path(__file__).resolve().parent

RUNTIME_ICON_FILE = BASE_DIR / "Icons" / "logo_2b.ico"
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
    # 4. 文件输出 (详细记录 DEBUG，按天切割，保留3天，异步写入)
    logger.add(
        os.path.join(log_dir, "runtime_{time:YYYY-MM-DD}.log"),
        retention="3 days",   # 只保留3天
        level="TRACE",
        encoding="utf-8",
        enqueue=True,          # [关键] 异步写入，防止阻塞 UI/OCR 线程
        backtrace=True,
        diagnose=True
    )
    logger.info(I18n.get("log_initialized"))


class I18n:
    """UI 多语言本地化词典 (全量支持)"""
    current_lang = "zh_CN"

    TEXT = {
        "zh_CN": {
            # --- 1. 后台进度文本 ---
            "prog_downloading_raw": "🟡 正在下载缺失源文件 ({0}个)...",
            "prog_downloading_file": "🟡 正在下载: {0}{1}...",
            "prog_generating_map": "🟡 正在生成合并字典...",

            # --- 2. 状态机 (DictState) 文本 ---
            "state_standby": "⚪ 待机 (匹配模式已关闭)",
            "state_ready": "🟢 字典已就绪 (Level {0})",
            "state_pending": "⏳ 即将加载... ({0} ➔ {1})",
            "state_loading": "🟡 正在处理中... ({0} ➔ {1})",
            "state_missing": "🔴 缺失: {0}",
            "state_error": "⚠️ 错误: {0}",
            "state_error_unknown": "未知错误",

            # --- 3. 交互反馈与字幕窗口 ---
            "sub_waiting": "等待 OCR 识别...",
            "status_ocr_submit": "OCR任务已提交",
            "status_sel_region": "请框选区域 (ESC取消)",
            "status_region_ok": "区域已框选: {0},{1} {2}x{3}",
            "status_auto_ocr_on": "自动OCR已开启 ({0}次/4秒)",
            "status_auto_ocr_off": "自动OCR已关闭",
            "status_interval": "自动OCR频率已更新: {0}次/4秒",
            "status_detect_ocr_on": "检测OCR已开启",
            "status_detect_ocr_off": "检测OCR已关闭",
            "status_game_changed": "游戏已切换：{0}",
            "status_languages_changed": "语言已切换：{0} → {1}",
            "status_match_mode_changed": "匹配模式已切换：{0}",
            "status_threshold_changed": "相似度阈值已更新：{0}%",
            "status_detect_frequency_changed": "检测频率已更新：{0} 次/秒",
            "status_detect_sensitivity_changed": "检测灵敏度已更新：{0}%",
            "status_subtitle_size_changed": "字幕字号已更新：{0} pt",
            "status_nickname_changed": "玩家昵称已更新：{0}",
            "status_gender_changed": "主角性别已更新：{0}",

            # --- 5. [新增] OCR 动态状态与后端报错 ---
            "status_perf": "本次 | 截图: {0:.3f}s | OCR: {1:.3f}s | 匹配: {2:.3f}s | 总计: {3:.3f}s\n近{4}次平均 | 截图: {5:.3f}s | OCR: {6:.3f}s | 匹配: {7:.3f}s | 总计: {8:.3f}s",
            "status_perf_detect": "本次 | 检测→触发OCR: {0:.3f}s | 截图: {1:.3f}s | OCR: {2:.3f}s | 匹配: {3:.3f}s | 总计: {4:.3f}s\n近{5}次平均 | 检测→触发OCR: {6:.3f}s | 截图: {7:.3f}s | OCR: {8:.3f}s | 匹配: {9:.3f}s | 总计: {10:.3f}s",
            "status_perf_sim": "{0} | 相似度: {1}%",
            "status_no_text": "未识别到文本",
            "status_ocr_error": "OCR执行出错: {0}",
            "err_cancelled": "操作已取消",
            "ui_settings_title": "FaintOCR 设置",
            "ui_settings_hint": "识别流程、匹配与输出参数",
            "ui_status_connected": "FaintOCR 3.5.9 已连接 OCR 控制器",
            "ui_section_basic": "基础设置",
            "ui_section_ocr": "OCR 运行",
            "ui_section_region": "识别区域",
            "ui_section_match": "游戏、语言与匹配",
            "ui_section_output": "输出设置",
            "ui_interface_language": "界面语言",
            "ui_subtitle_font_size": "字幕字号",
            "ui_manual": "手动",
            "ui_auto": "自动",
            "ui_detect": "检测",
            "ui_manual_no_params": "手动模式无额外参数",
            "ui_auto_frequency": "自动 OCR 频率",
            "ui_detect_frequency": "检测频率",
            "ui_detect_sensitivity": "检测灵敏度",
            "ui_region_hint": "查看或重新确认当前 OCR 捕获范围",
            "ui_show_region": "显示当前区域",
            "ui_game": "游戏",
            "ui_source_language": "源语言",
            "ui_target_language": "目标语言",
            "ui_player_nickname": "玩家昵称",
            "ui_protagonist_gender": "主角性别",
            "ui_gender_female": "女主",
            "ui_gender_male": "男主",
            "ui_match_off": "关闭",
            "ui_match_exact": "完全匹配",
            "ui_match_prefix": "前缀截取",
            "ui_similarity_threshold": "相似度阈值",
            "ui_generate_match_data": "一键生成匹配数据",
            "ui_match_data_ready": "匹配数据已就绪，无需重复生成",
            "ui_match_data_loading": "匹配数据加载中",
            "ui_match_data_missing": "匹配数据缺失，点击生成",
            "ui_dict_memory_ready": "内存就绪",
            "ui_dict_memory_missing": "内存未满足",
            "ui_dict_memory_loading": "加载中",
            "ui_match_locked": "字典任务处理中，此区域暂不可修改",
            "ui_output_hint": "识别完成后自动处理文本结果；启用的操作会以主题色突出显示。",
            "ui_auto_copy": "自动复制",
            "ui_auto_save": "自动保存",
            "ui_enabled": "已开启",
            "ui_disabled": "已关闭",
            "ui_debug_output": "调试输出",
            "ui_exit_program": "退出程序",
            "ui_mode_status": "{0}模式",
            "ui_save_failed": "保存失败: {0}",
            "ui_match_progress": "匹配数据处理进度: {0}%",
            "unit_pt": "{0} pt",
            "unit_per_4s": "{0} 次/4秒",
            "unit_per_s": "{0} 次/秒",
            "unit_percent": "{0}%",
            "log_initialized": "日志系统初始化完成",
            "log_dict_cancel_requested": "字典任务收到取消指令: {0}",
            "log_dict_start": "开始字典任务: {0} Type={1} Mask={2}",
            "log_dict_cancelled": "字典任务在中途已取消",
            "log_dict_worker_error": "字典加载线程发生异常",
            "log_dict_merge_ok": "字典合并成功: {0} 条目",
            "log_dict_merge_failed": "字典合并失败: {0}",
            "log_detect_start_failed": "检测 OCR 启动失败",
            "log_detect_poll": "检测轮询: pixel={0:.3f}x, count={1:.3f}x",
            "log_detect_poll_error": "检测 OCR 轮询异常",
            "log_detect_review_error": "检测 OCR 复核异常",
            "log_ocr_worker_start": "OCRWorker 开始处理图片",
            "log_ocr_fallback": "轻量级检测未发现文本，触发标准模型兜底识别",
            "log_ocr_complete": "OCR完成: {0}\n{1}",
            "log_ocr_fatal": "OCR流程发生严重错误",
            "log_rapidocr_empty": "RapidOCR 未识别到任何内容",
            "log_rapidocr_raw": "RapidOCR 原始数据: {0}",
            "log_filtered_empty": "过滤后未发现符合特征的文本",
            "log_queue_drop": "队列已满，丢弃旧任务 (Size: {0})",
            "log_task_submit": "任务已提交 (队列: {0}, 活跃: {1})",
            "log_worker_start": "启动OCR线程 (剩余队列: {0})",
            "log_task_failed": "OCR任务失败: {0}",
            "log_tasks_reset": "任务管理器已重置，取消了 {0} 个等待任务",
            "log_rapidocr_init_failed": "RapidOCR 初始化失败: {0}",
            "log_capture_failed": "截图失败: {0}",
            "log_detect_trigger": "检测 OCR 触发，变化倍率: {0:.2f}x",
            "log_old_detect_task": "忽略旧检测会话任务: session={0}, reason={1}",
            "log_detect_task_done": "检测任务结束: {0}, 待完成={1}",
            "log_old_detect_result": "忽略旧检测会话 OCR 结果: session={0}",
            "log_stale_worker": "丢弃过期 Worker 数据",
            "log_capture_exclusion_failed": "[{0}] 截图排除设置失败",
            "log_capture_exclusion_error": "[{0}] 截图排除设置异常: {1}",
            "log_cleanup": "FaintOCR 3.5.9 资源清理完成",
            "log_language_changed": "界面语言已切换: {0}",
            "ui_ocr_manual_idle": "手动 OCR：待命",
            "ui_ocr_manual_active": "手动 OCR：识别中",
            "ui_ocr_auto_off": "自动 OCR：已关闭",
            "ui_ocr_auto_on": "自动 OCR：已开启",
            "ui_ocr_detect_off": "检测 OCR：已关闭",
            "ui_ocr_detect_on": "检测 OCR：已开启",
            "app_title": "FaintOCR 3.5.9",
            "ui_download_progress": "正在下载：{0} · {1} · {2}% · {3} · {4}",
            "status_ocr_done": "OCR 完成",
            "status_match_done": "匹配成功 · {0}%",
            "debug_ocr_result": "[{0}] OCR结果: {1}",
            "debug_ocr_detail": "[{0}] {1}",
            "debug_detect": "[检测] {0}",
            "debug_dict": "[字典] {0}",
            "debug_error": "[错误] {0}",
            "status_ocr_summary": "{0} · 截图 {1:.3f}s · OCR {2:.3f}s · 匹配 {3:.3f}s · 总计 {4:.3f}s · {5}",
            "status_match_triggered": "匹配 {0}%",
            "status_match_not_triggered": "未触发匹配",
            "debug_crop_applied": "黄线截取：已截取 {0}/{1}，保留 {2}",
            "debug_crop_skipped": "黄线截取：未截取（{0}）",
            "debug_height_filter_disabled": "高度过滤：已关闭",
            "debug_crop_reason_match_off": "匹配关闭",
            "debug_crop_reason_disabled": "功能关闭",
            "debug_crop_reason_no_rule": "无当前游戏规则",
            "debug_crop_reason_not_found": "未检测到黄线",
            "debug_crop_reason_invalid": "截取高度无效",
            "debug_detect_poll": "检测差异：总值 {0:.3f}x，像素 {1:.3f}x，数量 {2:.3f}x",
            "interface_zh_CN": "简体中文",
            "interface_en_US": "English",
            "detect_mode_fast": "剧烈变化快速通道",
            "detect_mode_normal": "普通变化防抖复核",
            "detect_reason_submit_failed": "提交失败",
            "detect_reason_queue_dropped": "队列丢弃",
            "detect_reason_ocr_complete": "OCR 完成",
            "game_genshin": "原神",
            "game_star_rail": "崩坏：星穹铁道",
            "lang_CHS": "简体中文",
            "lang_EN": "英语",
            "lang_JP": "日语",
            "status_detect_started": "检测 OCR 已启动，正在执行首次 OCR",
            "status_detect_start_error": "检测 OCR 启动失败: {0}",
            "status_detect_stopped": "检测 OCR 已停止",
            "status_detect_updated": "检测区域或游戏已更新，正在执行首次 OCR",
            "status_detect_change": "检测到变化 {0:.2f}x，进入{1}",
            "status_detect_poll_error": "检测 OCR 轮询异常: {0}",
            "status_detect_stable": "剧烈变化已稳定，提交检测 OCR",
            "status_detect_submit": "画面稳定，提交检测 OCR ({0:.2f}x; 像素 {1:.2f}x; 数量 {2:.2f}x)",
            "status_detect_review_failed": "变化复核未通过，恢复检测",
            "status_detect_review_error": "检测 OCR 复核异常: {0}",
            "status_detect_resumed": "检测 OCR 已恢复监视",
            "log_crop_none": "OCR 前裁剪：未检测到参考色块/横线 ({0})",
            "log_crop_invalid": "OCR 前裁剪：候选框裁剪高度无效，跳过。box={0}, img_h={1}",
            "log_crop_use": "OCR 前裁剪：使用候选框 {0}，从 y={1} 开始保留图像",
            "log_crop_candidate": "OCR 前裁剪候选框: x={0}, y={1}, w={2}, h={3}, center_offset={4:.1f}",
            "log_text_include": "并入中心文本: [{0}] -> 中心偏离:{1:.1f}, 高度:{2:.1f}, 高度过滤:{3}",
            "log_text_exclude": "剔除边缘文本: [{0}] -> 中心偏离:{1:.1f}, 高度:{2:.1f}, 高度范围:{3}-{4}, 高度过滤:{5}",
            "log_filter_on": "开",
            "log_filter_off": "关",
        },
        "en_US": {
            # --- 1. Background Progress ---
            "prog_downloading_raw": "🟡 Downloading raw files ({0})...",
            "prog_downloading_file": "🟡 Downloading: {0}{1}...",
            "prog_generating_map": "🟡 Generating merged dictionary...",

            # --- 2. State Machine ---
            "state_standby": "⚪ Standby (Match mode off)",
            "state_ready": "🟢 Dictionary Ready (Level {0})",
            "state_pending": "⏳ Loading soon... ({0} ➔ {1})",
            "state_loading": "🟡 Processing... ({0} ➔ {1})",
            "state_missing": "🔴 Missing: {0}",
            "state_error": "⚠️ Error: {0}",
            "state_error_unknown": "Unknown error",

            # --- 3. Interactive & Subtitles ---
            "sub_waiting": "Waiting for OCR...",
            "status_ocr_submit": "OCR task submitted",
            "status_sel_region": "Please select region (ESC to cancel)",
            "status_region_ok": "Region selected: {0},{1} {2}x{3}",
            "status_auto_ocr_on": "Auto OCR ON ({0}/4s)",
            "status_auto_ocr_off": "Auto OCR OFF",
            "status_interval": "Auto OCR frequency updated: {0}/4s",
            "status_detect_ocr_on": "Detect OCR ON",
            "status_detect_ocr_off": "Detect OCR OFF",
            "status_game_changed": "Game changed: {0}",
            "status_languages_changed": "Languages changed: {0} → {1}",
            "status_match_mode_changed": "Match mode changed: {0}",
            "status_threshold_changed": "Similarity threshold updated: {0}%",
            "status_detect_frequency_changed": "Detection frequency updated: {0}/s",
            "status_detect_sensitivity_changed": "Detection sensitivity updated: {0}%",
            "status_subtitle_size_changed": "Subtitle font size updated: {0} pt",
            "status_nickname_changed": "Player nickname updated: {0}",
            "status_gender_changed": "Protagonist gender updated: {0}",

            # --- 5. [新增] Dynamic Status & Backend Errors ---
            "status_perf": "Current | Capture: {0:.3f}s | OCR: {1:.3f}s | Match: {2:.3f}s | Total: {3:.3f}s\nLast {4} avg | Capture: {5:.3f}s | OCR: {6:.3f}s | Match: {7:.3f}s | Total: {8:.3f}s",
            "status_perf_detect": "Current | Detect→OCR trigger: {0:.3f}s | Capture: {1:.3f}s | OCR: {2:.3f}s | Match: {3:.3f}s | Total: {4:.3f}s\nLast {5} avg | Detect→OCR trigger: {6:.3f}s | Capture: {7:.3f}s | OCR: {8:.3f}s | Match: {9:.3f}s | Total: {10:.3f}s",
            "status_perf_sim": "{0} | Similarity: {1}%",
            "status_no_text": "No text detected",
            "status_ocr_error": "OCR execution error: {0}",
            "err_cancelled": "Operation cancelled",
            "ui_settings_title": "FaintOCR Settings",
            "ui_settings_hint": "Recognition, matching, and output options",
            "ui_status_connected": "FaintOCR 3.5.9 connected to OCR controller",
            "ui_section_basic": "Basic Settings",
            "ui_section_ocr": "OCR Operation",
            "ui_section_region": "Recognition Region",
            "ui_section_match": "Game, Language, and Matching",
            "ui_section_output": "Output Settings",
            "ui_interface_language": "Interface Language",
            "ui_subtitle_font_size": "Subtitle Font Size",
            "ui_manual": "Manual",
            "ui_auto": "Auto",
            "ui_detect": "Detect",
            "ui_manual_no_params": "Manual mode has no additional parameters",
            "ui_auto_frequency": "Auto OCR Frequency",
            "ui_detect_frequency": "Detection Frequency",
            "ui_detect_sensitivity": "Detection Sensitivity",
            "ui_region_hint": "Review or confirm the current OCR capture region",
            "ui_show_region": "Show Current Region",
            "ui_game": "Game",
            "ui_source_language": "Source Language",
            "ui_target_language": "Target Language",
            "ui_player_nickname": "Player Nickname",
            "ui_protagonist_gender": "Protagonist Gender",
            "ui_gender_female": "Female",
            "ui_gender_male": "Male",
            "ui_match_off": "Off",
            "ui_match_exact": "Exact Match",
            "ui_match_prefix": "Prefix Extraction",
            "ui_similarity_threshold": "Similarity Threshold",
            "ui_generate_match_data": "Generate Matching Data",
            "ui_match_data_ready": "Matching data is ready; no regeneration needed",
            "ui_match_data_loading": "Matching data is loading",
            "ui_match_data_missing": "Matching data is missing; click to generate",
            "ui_dict_memory_ready": "Memory Ready",
            "ui_dict_memory_missing": "Memory Missing",
            "ui_dict_memory_loading": "Loading",
            "ui_match_locked": "Dictionary task running; this section is temporarily locked",
            "ui_output_hint": "Automatically process recognized text; enabled actions use the theme color.",
            "ui_auto_copy": "Auto Copy",
            "ui_auto_save": "Auto Save",
            "ui_enabled": "Enabled",
            "ui_disabled": "Disabled",
            "ui_debug_output": "DEBUG OUTPUT",
            "ui_exit_program": "Exit FaintOCR",
            "ui_mode_status": "{0} mode",
            "ui_save_failed": "Save failed: {0}",
            "ui_match_progress": "Matching data progress: {0}%",
            "unit_pt": "{0} pt",
            "unit_per_4s": "{0}/4s",
            "unit_per_s": "{0}/s",
            "unit_percent": "{0}%",
            "log_initialized": "Logging initialized",
            "log_dict_cancel_requested": "Dictionary task cancellation requested: {0}",
            "log_dict_start": "Starting dictionary task: {0} Type={1} Mask={2}",
            "log_dict_cancelled": "Dictionary task cancelled during execution",
            "log_dict_worker_error": "Dictionary worker failed",
            "log_dict_merge_ok": "Dictionary merge completed: {0} entries",
            "log_dict_merge_failed": "Dictionary merge failed: {0}",
            "log_detect_start_failed": "Detect OCR failed to start",
            "log_detect_poll": "Detection poll: pixel={0:.3f}x, count={1:.3f}x",
            "log_detect_poll_error": "Detect OCR polling failed",
            "log_detect_review_error": "Detect OCR review failed",
            "log_ocr_worker_start": "OCRWorker started processing image",
            "log_ocr_fallback": "Lightweight detection found no text; falling back to standard model",
            "log_ocr_complete": "OCR completed: {0}\n{1}",
            "log_ocr_fatal": "OCR pipeline encountered a fatal error",
            "log_rapidocr_empty": "RapidOCR detected no content",
            "log_rapidocr_raw": "RapidOCR raw result: {0}",
            "log_filtered_empty": "No text remained after filtering",
            "log_queue_drop": "Queue full; dropped oldest task (Size: {0})",
            "log_task_submit": "Task submitted (queue: {0}, active: {1})",
            "log_worker_start": "Started OCR worker (remaining queue: {0})",
            "log_task_failed": "OCR task failed: {0}",
            "log_tasks_reset": "Task manager reset; cancelled {0} queued tasks",
            "log_rapidocr_init_failed": "RapidOCR initialization failed: {0}",
            "log_capture_failed": "Screen capture failed: {0}",
            "log_detect_trigger": "Detect OCR triggered; change ratio: {0:.2f}x",
            "log_old_detect_task": "Ignored old detection task: session={0}, reason={1}",
            "log_detect_task_done": "Detection task finished: {0}, pending={1}",
            "log_old_detect_result": "Ignored old detection OCR result: session={0}",
            "log_stale_worker": "Discarded stale worker data",
            "log_capture_exclusion_failed": "[{0}] Capture exclusion failed",
            "log_capture_exclusion_error": "[{0}] Capture exclusion error: {1}",
            "log_cleanup": "FaintOCR 3.5.9 resources cleaned up",
            "log_language_changed": "Interface language changed: {0}",
            "ui_ocr_manual_idle": "Manual OCR: Idle",
            "ui_ocr_manual_active": "Manual OCR: Running",
            "ui_ocr_auto_off": "Auto OCR: Off",
            "ui_ocr_auto_on": "Auto OCR: On",
            "ui_ocr_detect_off": "Detect OCR: Off",
            "ui_ocr_detect_on": "Detect OCR: On",
            "app_title": "FaintOCR 3.5.9",
            "ui_download_progress": "Downloading: {0} · {1} · {2}% · {3} · {4}",
            "status_ocr_done": "OCR completed",
            "status_match_done": "Matched · {0}%",
            "debug_ocr_result": "[{0}] OCR result: {1}",
            "debug_ocr_detail": "[{0}] {1}",
            "debug_detect": "[Detect] {0}",
            "debug_dict": "[Dictionary] {0}",
            "debug_error": "[Error] {0}",
            "status_ocr_summary": "{0} · Capture {1:.3f}s · OCR {2:.3f}s · Match {3:.3f}s · Total {4:.3f}s · {5}",
            "status_match_triggered": "Matched {0}%",
            "status_match_not_triggered": "No match",
            "debug_crop_applied": "Yellow-line crop: cropped {0}/{1}, retained {2}",
            "debug_crop_skipped": "Yellow-line crop: skipped ({0})",
            "debug_height_filter_disabled": "Height filter: disabled",
            "debug_crop_reason_match_off": "matching disabled",
            "debug_crop_reason_disabled": "feature disabled",
            "debug_crop_reason_no_rule": "no rule for current game",
            "debug_crop_reason_not_found": "yellow line not detected",
            "debug_crop_reason_invalid": "invalid crop height",
            "debug_detect_poll": "Detection difference: total {0:.3f}x, pixel {1:.3f}x, count {2:.3f}x",
            "interface_zh_CN": "简体中文",
            "interface_en_US": "English",
            "detect_mode_fast": "large-change fast path",
            "detect_mode_normal": "normal-change debounce review",
            "detect_reason_submit_failed": "submission failed",
            "detect_reason_queue_dropped": "queue dropped",
            "detect_reason_ocr_complete": "OCR completed",
            "game_genshin": "Genshin Impact",
            "game_star_rail": "Honkai: Star Rail",
            "lang_CHS": "Simplified Chinese",
            "lang_EN": "English",
            "lang_JP": "Japanese",
            "status_detect_started": "Detect OCR started; running initial OCR",
            "status_detect_start_error": "Detect OCR failed to start: {0}",
            "status_detect_stopped": "Detect OCR stopped",
            "status_detect_updated": "Detection region or game updated; running initial OCR",
            "status_detect_change": "Change detected {0:.2f}x; entering {1}",
            "status_detect_poll_error": "Detect OCR polling error: {0}",
            "status_detect_stable": "Large change stabilized; submitting detect OCR",
            "status_detect_submit": "Image stable; submitting detect OCR ({0:.2f}x; pixel {1:.2f}x; count {2:.2f}x)",
            "status_detect_review_failed": "Change review failed; resuming detection",
            "status_detect_review_error": "Detect OCR review error: {0}",
            "status_detect_resumed": "Detect OCR monitoring resumed",
            "log_crop_none": "Pre-OCR crop: no reference block/line detected ({0})",
            "log_crop_invalid": "Pre-OCR crop: invalid candidate crop height; skipped. box={0}, img_h={1}",
            "log_crop_use": "Pre-OCR crop: using candidate {0}; retaining image from y={1}",
            "log_crop_candidate": "Pre-OCR crop candidate: x={0}, y={1}, w={2}, h={3}, center_offset={4:.1f}",
            "log_text_include": "Included centered text: [{0}] -> center offset:{1:.1f}, height:{2:.1f}, height filter:{3}",
            "log_text_exclude": "Excluded edge text: [{0}] -> center offset:{1:.1f}, height:{2:.1f}, height range:{3}-{4}, height filter:{5}",
            "log_filter_on": "on",
            "log_filter_off": "off",
        }
    }

    @classmethod
    def get(cls, key, *args):
        template = cls.TEXT.get(cls.current_lang, {}).get(key, key)
        return template.format(*args) if args else template

    @classmethod
    def game_name(cls, game_key):
        return cls.get({"Genshin Impact": "game_genshin", "Star Rail": "game_star_rail"}.get(game_key, game_key))

    @classmethod
    def language_name(cls, language_code):
        return cls.get(f"lang_{language_code}")


class Config:
    # 直接基于 BASE_DIR 创建路径，不再用 dirname(dirname) 这种容易产生偏移的逻辑
    TEXTMAP_ROOT = os.path.join(BASE_DIR, "TextMap")
    OUTPUT_FILE = os.path.join(BASE_DIR, "OCR_Results.txt")
    PRE_OCR_CROP_DEBUG_DIR = os.path.join(BASE_DIR, "Test")
    OCR = {
        "DEFAULT_REGION": (120, 800, 1680, 240),
        "DEFAULT_INTERVAL": 0.5,
        "DETECT": {
            "pixel_threshold": 0.01171,
            "count_threshold": 0.250,
            "debounce_delay": 0.4,
            "debug": False,
            "debug_dir": os.path.join(BASE_DIR, "detect_debug"),
            "rules": {
                "Genshin Impact": (
                    {"color": "FFFFFF", "space": "RGB", "tolerance": 16},
                    {"color": "FFCC33", "space": "HSV", "tolerance": (1, 48, 48)},
                ),
                "Star Rail": (
                    {"color": "FFFFFF", "space": "RGB", "tolerance": 16},
                    {"color": "DBC291", "space": "HSV", "tolerance": (1, 48, 48)},
                ),
            },
        },

        # OCR 前裁剪：先用颜色提取逻辑寻找字幕上方/分隔用横线，
        # 找到后只把横线底边以下的整段图像送入 OCR。
        "PRE_OCR_CROP_RULES": {
            # 全局开关：False 时所有游戏都跳过 OCR 前裁剪
            "enabled": True,

            # 全局调试开关：True 时保存 OCR 前裁剪过程图片
            "debug": False,

            "Genshin Impact": {
                "enabled": True,
                "hex_color": "FFCC33FF",
                "tolerances": (1, 48, 48),
                "close_kernel_size": (128, 48),
                "open_kernel_size": (32, 12),
                "padding_top": 0,
                "min_remaining_height": 24,
            },
            "Star Rail": {
                "enabled": True,
                "hex_color": "dbc291ff",
                "tolerances": (1, 48, 48),
                "close_kernel_size": (128, 48),
                "open_kernel_size": (32, 12),
                "padding_top": 0,
                "min_remaining_height": 24,
            },
        },

        # OCR 文本特征过滤：字体高度规则。
        # 仅在 match_mode != 0 时由 run_rapidocr 使用；
        # enabled=False 时跳过字体高度判断，但仍保留中心偏移判断。
        "TEXT_HEIGHT_FILTER_RULES": {
            # 全局开关：False 时所有游戏都跳过字体高度判断。
            "enabled": True,
            "DEFAULT": {
                # 单游戏/默认规则开关：False 时该规则跳过字体高度判断。
                "enabled": True,
                "height_min": 15,
                "height_max": 60,
            },
            "Genshin Impact": {
                "enabled": True,
                "height_min": 28,
                "height_max": 60,
            },
            "Star Rail": {
                "enabled": True,
                "height_min": 24,
                "height_max": 60,
            },
        },
    }
    DEFAULTS = {
        "interface_language": "zh_CN",
        "game": "Genshin Impact",
        "ocr_mode": 0,
        "auto_ocr_enabled": False,
        "detect_ocr_enabled": False,
        "detect_frequency": 10,
        "detect_sensitivity": 50,
        "match_mode": 0,
        "similarity_threshold": 75,
        "auto_copy": False,
        "auto_save": False,
        "source_lang": "CHS",
        "target_lang": "EN",
        "player_nickname": "旅行者",
        "protagonist_gender": "female",
        "subtitle_font_size": 14,
        "subtitle_opacity": 0.8,
    }
    PERSONALIZATION_DEFAULTS = {
        "Genshin Impact": {
            "CHS": {"player_nickname": "旅行者", "protagonist_gender": "female"},
            "EN": {"player_nickname": "Traveler", "protagonist_gender": "female"},
            "JP": {"player_nickname": "旅人", "protagonist_gender": "female"},
        },
        "Star Rail": {
            "CHS": {"player_nickname": "开拓者", "protagonist_gender": "female"},
            "EN": {"player_nickname": "Trailblazer", "protagonist_gender": "female"},
            "JP": {"player_nickname": "開拓者", "protagonist_gender": "female"},
        },
    }

    @classmethod
    def personalization_default(cls, game_key, source_lang):
        default = cls.PERSONALIZATION_DEFAULTS.get(game_key, {}).get(source_lang, {})
        return {
            "player_nickname": default.get("player_nickname", cls.DEFAULTS["player_nickname"]),
            "protagonist_gender": default.get("protagonist_gender", cls.DEFAULTS["protagonist_gender"]),
        }

    UI_RANGES = {
        "auto_frequency_per_4s": (1, 20),
        "detect_frequency": (1, 20),
        "detect_sensitivity": (1, 100),
        "similarity_threshold": (0, 100),
        "subtitle_font_size": (10, 24),
        "subtitle_opacity": (0.2, 1.0),
    }
    AUTO_FREQUENCY_WINDOW_SECONDS = 4.0

    @classmethod
    def auto_frequency_to_interval(cls, frequency):
        return cls.AUTO_FREQUENCY_WINDOW_SECONDS / max(frequency, 1)

    @classmethod
    def interval_to_auto_frequency(cls, interval):
        return round(cls.AUTO_FREQUENCY_WINDOW_SECONDS / max(interval, 0.001))

    LANG_MAP = {
        "CHS": "简体中文",
        "EN": "English",
        "JP": "日本語"
    }
    GAMES = {
        "Genshin Impact": {
            "folder": "Genshin Impact",
            "urls": {
                "TextMapCHS.json": [
                    "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapCHS.json?inline=false",
                    "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMap_MediumCHS.json?inline=false"
                ],
                "TextMapEN.json": [
                    "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapEN.json?inline=false",
                    "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMap_MediumEN.json?inline=false"
                ],
                "TextMapJP.json": [
                    "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapJP.json?inline=false",
                    "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMap_MediumJP.json?inline=false"
                ]
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
    download_detail_signal = QtCore.Signal(str, str, int, str, str)
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
        logger.info(I18n.get("log_dict_cancel_requested", self.game_key))

    def _report_percent(self, percent, size_text=None, speed_text=None, game_key=None, file_name=None):
        self.percent_signal.emit(percent)
        if all(value is not None for value in (size_text, speed_text, game_key, file_name)):
            self.download_detail_signal.emit(game_key, file_name, percent, size_text, speed_text)

    @logger.catch(exclude=Exception)  # 防止未捕获的崩溃，exclude用于手动处理逻辑异常
    def run(self):
        if self._is_cancelled: return

        callbacks = {
            # [修改] 默认空列表防止无参数时报错
            'progress': lambda key, args=[]: self.progress_signal.emit(key, args),
            'percent': self._report_percent,
            'check_cancel': lambda: self._is_cancelled
        }

        try:
            logger.info(I18n.get("log_dict_start", self.game_key, self.process_type, self.target_mask))
            self.result = TextMapLoader.handle_task(
                self.game_key,
                self.source_lang,
                self.target_lang,
                self.process_type,
                self.target_mask,
                callbacks
            )

            if self._is_cancelled:
                logger.warning(I18n.get("log_dict_cancelled"))
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
                logger.exception(I18n.get("log_dict_worker_error"))
                self.error_signal.emit(False, str(e))


class TextMapLoader:
    """
    文本映射加载器 (静态工具类 - 流水线版)
    逻辑重构：检查 -> (修复) -> 加载，三步合一
    """

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
    def handle_task(cls, game_key, source_lang, target_lang, process_type, target_mask, callbacks=None):
        # 1. 搭建极其纯净的临时沙箱工作内存 (不再依赖任何类属性)
        working_cache = {
            1: {},
            2: {"text_map": {}, "static_candidates": []}
        }

        # 2. 调用真正的核心处理逻辑
        result_mask = cls._execute_task(
            game_key, source_lang, target_lang, process_type, target_mask, working_cache, callbacks
        )

        # 3. 提取有价值的产物 (若沙箱中为空，则转换为 None，方便后续 set_data 识别)
        text_map = working_cache[2].get("text_map") or None
        static_candidates = working_cache[2].get("static_candidates")
        # 4. 返回 质检报告(掩码) + 生产成果(数据)
        return result_mask, text_map, static_candidates

    @classmethod
    def _execute_task(cls, game_key, source_lang, target_lang, process_type, target_mask, working_cache, callbacks):
        if callbacks is None: callbacks = {}
        # [修改] 默认的匿名函数也要适配两个参数
        report_progress = callbacks.get('progress', lambda key, args=[]: None)
        report_percent = callbacks.get(
            'percent',
            lambda percent, size_text=None, speed_text=None, game_key=None, file_name=None: None
        )
        check_cancel = callbacks.get('check_cancel', lambda: False)

        # === 1. 模式解析 ===
        # process_type: 0(检查), 1(加载), 2(修复/生成)
        # target_mask: 目标层级掩码 (1=Raw, 2=Map)

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
            map_file = f"CanonicalMap-{source_lang}to{target_lang}.json"
            static_file = f"MatchStatic-{source_lang}to{target_lang}.json"
            map_path = cls.get_file_path(game_key, map_file)
            static_path = cls.get_file_path(game_key, static_file)
            missing_map = []

            is_m_exist = os.path.exists(map_path) and os.path.exists(static_path)

            # B. 尝试加载 (仅当: 存在 + 目标包含Map + 非纯检查模式)
            if process_type >= 1 and is_m_exist:
                try:
                    with open(map_path, 'rb') as f:
                        data = orjson.loads(f.read())
                    with open(static_path, 'rb') as f:
                        static_candidates = orjson.loads(f.read())
                    expected_static_count = sum(
                        not cls.has_dynamic_tags(key) for key in data
                    )
                    if not isinstance(static_candidates, list) or len(static_candidates) != expected_static_count:
                        raise ValueError("静态匹配候选与基础映射不一致")
                    working_cache[2]["text_map"] = data
                    working_cache[2]["static_candidates"] = static_candidates
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
                    generated_data, static_candidates = cls._merge_and_save_map(
                        game_key, source_lang, target_lang,
                        working_cache[1].get("src"), working_cache[1].get("tgt"),  # <--- 优雅！
                        report_progress, report_percent, check_cancel
                    )
                    if generated_data is not None:
                        working_cache[2]["text_map"] = generated_data
                        working_cache[2]["static_candidates"] = static_candidates
                        missing_map = []
           # C. 判定缺失
            if missing_map:
                result_mask |= 2

        # 3. 结束
        # =========================================================
        return result_mask

    @staticmethod
    def format_bytes(size_in_bytes):
        """将字节数转换为带有合适单位的字符串。"""
        size = max(float(size_in_bytes), 0.0)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @classmethod
    def download_files(cls, game_key, target_files=None, progress_cb=None, percent_cb=None, cancel_cb=None):
        urls = Config.GAMES.get(game_key, {}).get("urls", {})
        if target_files:
            urls = {k: v for k, v in urls.items() if k in target_files}

        result_data = {}

        for name, configured_urls in urls.items():
            path = cls.get_file_path(game_key, name)
            source_urls = configured_urls if isinstance(configured_urls, (list, tuple)) else [configured_urls]
            merged_data = None

            for source_index, url in enumerate(source_urls, start=1):
                display_name = name
                if len(source_urls) > 1:
                    display_name = f"{name} [{source_index}/{len(source_urls)}]"

                last_err = None
                for attempt in range(1, 4):
                    try:
                        if cancel_cb and cancel_cb(): return False, "已取消"

                        if progress_cb:
                            retry_txt = f" ({attempt})" if attempt > 1 else ""
                            progress_cb("prog_downloading_file", [display_name, retry_txt])

                        with requests.get(url, stream=True, timeout=15, verify=False) as r:
                            r.raise_for_status()
                            total_size = int(r.headers.get('content-length', 0))
                            downloaded = 0
                            buffer = bytearray()
                            last_update_time = time.monotonic()
                            last_update_bytes = 0
                            last_speed_bps = 0

                            for chunk in r.iter_content(8192):
                                if cancel_cb and cancel_cb():
                                    raise InterruptedError("已取消")

                                buffer.extend(chunk)
                                downloaded += len(chunk)

                                current_time = time.monotonic()
                                is_complete = total_size > 0 and downloaded >= total_size
                                if percent_cb and (current_time - last_update_time >= 0.2 or is_complete):
                                    interval = current_time - last_update_time
                                    speed_bps = (
                                        (downloaded - last_update_bytes) / interval
                                        if interval > 0 else 0
                                    )
                                    last_speed_bps = speed_bps
                                    percent = min(int((downloaded / total_size) * 100), 100) if total_size > 0 else 0
                                    total_text = cls.format_bytes(total_size) if total_size > 0 else "?"
                                    size_text = f"{cls.format_bytes(downloaded)} / {total_text}"
                                    percent_cb(
                                        percent, size_text, f"{cls.format_bytes(speed_bps)}/s",
                                        game_key, display_name
                                    )
                                    last_update_time = current_time
                                    last_update_bytes = downloaded

                            if percent_cb and downloaded != last_update_bytes:
                                current_time = time.monotonic()
                                interval = current_time - last_update_time
                                speed_bps = (
                                    (downloaded - last_update_bytes) / interval
                                    if interval >= 0.05 else last_speed_bps
                                )
                                percent = min(int((downloaded / total_size) * 100), 100) if total_size > 0 else 0
                                total_text = cls.format_bytes(total_size) if total_size > 0 else "?"
                                size_text = f"{cls.format_bytes(downloaded)} / {total_text}"
                                percent_cb(
                                    percent, size_text, f"{cls.format_bytes(speed_bps)}/s",
                                    game_key, display_name
                                )

                        source_data = orjson.loads(buffer)
                        del buffer
                        if not isinstance(source_data, dict):
                            raise ValueError(f"{display_name} 内容不是 JSON 对象")

                        # 🌟 保留你优秀的零拷贝优化
                        if merged_data is None:
                            merged_data = source_data
                        else:
                            merged_data.update(source_data)
                            del source_data
                        break

                    except InterruptedError:
                        return False, "已取消"
                    except Exception as err:
                        last_err = err
                else:
                    return False, f"下载 {display_name} 失败: {last_err}"

            if cancel_cb and cancel_cb(): return False, "已取消"
            if merged_data is None: return False, f"没有可保存的数据: {name}"

            # ⚠️ 注意这里：如果你为了压榨内存，indent=True 会显著增加生成 JSON 字符串时的内存和磁盘体积
            if not cls._save_file_atomic(path, merged_data, indent=True):
                return False, f"保存合并文件 {name} 失败"

            result_data[name] = merged_data

        return True, result_data

    @classmethod
    def _merge_and_save_map(cls, game_key, source_lang, target_lang, src_d, tgt_d, progress_cb, percent_cb, cancel_cb):
        map_path = cls.get_file_path(game_key, f"CanonicalMap-{source_lang}to{target_lang}.json")
        static_path = cls.get_file_path(game_key, f"MatchStatic-{source_lang}to{target_lang}.json")

        try:
            if not src_d or not tgt_d:
                return None, None

            merged = {}
            total = len(src_d)

            # 加入进度和取消回调检测
            for i, (k, s) in enumerate(src_d.items()):
                if i % 10000 == 0:
                    if cancel_cb(): return None, None
                    percent_cb(int((i / total) * 100))

                if k in tgt_d:
                    s_tx = cls.clean_canonical_text(s, game_key)
                    t_tx = cls.clean_canonical_text(tgt_d[k], game_key)

                    if s_tx and t_tx:
                        if s_tx not in merged:  merged[s_tx] = set()
                        merged[s_tx].add(t_tx)

            if cancel_cb(): return None, None
            percent_cb(100)

            final = {k: list(v) for k, v in merged.items()}
            static_candidates = [
                cls.clean_match_text(key, game_key, source_lang, "", "female")
                for key in final
                if not cls.has_dynamic_tags(key)
            ]

            if (
                    cls._save_file_atomic(map_path, final, indent=True) and
                    cls._save_file_atomic(static_path, static_candidates, indent=True)
            ):
                logger.info(I18n.get("log_dict_merge_ok", len(final)))
                return final, static_candidates
            else:
                return None, None

        except Exception as e:
            logger.exception(I18n.get("log_dict_merge_failed", e))
            return None, None

    @classmethod
    def clean_canonical_text(cls, text, game_key):
        """只移除与用户配置无关的富文本外壳，保留所有动态标签。"""
        if not text:
            return ""

        text = re.sub(r'<[^>]*>', '', text)
        if game_key == "Genshin Impact" and text.startswith('#'):
            text = text[1:]
        return text.strip()

    @staticmethod
    def has_dynamic_tags(text):
        return any(tag in text for tag in ("{NICKNAME}", "{F#", "{M#", "{RUBY#", "{RUBY_B#"))

    @classmethod
    def _render_gender(cls, text, gender):
        if gender == "male":
            text = re.sub(r'\{M#([^}]*)}', r'\1', text)
            return re.sub(r'\{F#[^}]*}', '', text)
        text = re.sub(r'\{F#([^}]*)}', r'\1', text)
        return re.sub(r'\{M#[^}]*}', '', text)

    @classmethod
    def clean_match_text(cls, text, game_key, current_lang, nickname, gender):
        """生成只用于 OCR 匹配的文本；OCR 输入也必须调用同一方法。"""
        if not text:
            return ""
        text = (
            text.replace(r'\n', '').replace('\n', '')
            .replace(r'\u00A0', '').replace('\u00A0', '')
        )
        if game_key == "Genshin Impact":
            text = text.replace('…', '·')
            text = re.sub(r'\{RUBY#(?:\[[^]]*])?[^}]*}', '', text)
        elif game_key == "Star Rail":
            text = text.replace('…', '.')
            text = re.sub(r'\{RUBY_B#[^}]*}([^{]*)\{RUBY_E#}', r'\1', text)
        text = text.replace('{NICKNAME}', nickname)
        text = cls._render_gender(text, gender)
        return text.strip()

    @classmethod
    def clean_display_text(cls, text, game_key, current_lang, nickname, gender):
        """匹配成功后按需渲染一条用于显示的规范文本。"""
        if not text:
            return ""
        text = text.replace('{NICKNAME}', nickname)
        text = cls._render_gender(text, gender)
        if game_key == "Genshin Impact":
            text = re.sub(r'\{RUBY#(?:\[[^]]*])?([^}]*)}', r'(\1)', text)
        elif game_key == "Star Rail":
            text = re.sub(r'\{RUBY_B#([^}]*)}([^{]*)\{RUBY_E#}', r'\2(\1)', text)
        return text.strip()

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


@dataclass(frozen=True)
class DetectConfig:
    region: tuple
    rules: tuple
    pixel_threshold: float
    count_threshold: float
    interval_ms: int
    debounce_delay: float
    debug: bool
    debug_dir: str


def compile_detect_rules(raw_rules):
    compiled = []
    for rule in raw_rules:
        hex_str = rule["color"].lstrip("#")
        rgb = np.array([int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)], dtype=np.int16)
        space = rule["space"].upper()
        tolerance = rule["tolerance"]
        if space == "RGB":
            tolerance = np.array([tolerance] * 3 if isinstance(tolerance, int) else tolerance, dtype=np.int16)
            compiled.append({
                "space": "RGB",
                "lower": np.clip(rgb - tolerance, 0, 255).astype(np.uint8),
                "upper": np.clip(rgb + tolerance, 0, 255).astype(np.uint8),
            })
        elif space == "HSV":
            target = cv2.cvtColor(np.array([[rgb]], dtype=np.uint8), cv2.COLOR_RGB2HSV)[0, 0]
            compiled.append({
                "space": "HSV",
                "target": target.astype(np.int16),
                "tolerance": np.array(tolerance, dtype=np.int16),
            })
    return compiled


def fill_detect_mask(rgb_image, compiled_rules, out_buffer):
    out_buffer.fill(0)
    hsv_image = None
    for rule in compiled_rules:
        if rule["space"] == "RGB":
            mask = cv2.inRange(rgb_image, rule["lower"], rule["upper"])
        else:
            if hsv_image is None:
                hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV).astype(np.int16)
            target = rule["target"]
            tolerance = rule["tolerance"]
            raw_h_diff = np.abs(hsv_image[:, :, 0] - target[0])
            h_diff = np.minimum(raw_h_diff, 180 - raw_h_diff)
            mask = (
                (h_diff <= tolerance[0])
                & (np.abs(hsv_image[:, :, 1] - target[1]) <= tolerance[1])
                & (np.abs(hsv_image[:, :, 2] - target[2]) <= tolerance[2])
            ).astype(np.uint8) * 255
        cv2.bitwise_or(out_buffer, mask, dst=out_buffer)
    return out_buffer


class DetectorWorker(QtCore.QObject):
    status_msg = QtCore.Signal(str)
    debug_msg = QtCore.Signal(str)
    triggered = QtCore.Signal(float, np.ndarray, int, object)
    start_failed = QtCore.Signal(str, int)

    def __init__(self, initial_config, session_id):
        super().__init__()
        self.config = initial_config
        self.session_id = session_id
        self.compiled_rules = compile_detect_rules(initial_config.rules)
        self._sct = None
        self._timer = None
        self._debounce_timer = None
        self._baseline_mask = None
        self._baseline_count = 0
        self._total_pixels = 0
        self._is_fast_pass = False
        self._change_detected_at = None
        self._init_region_buffers(initial_config.region)

    def _init_region_buffers(self, region):
        x, y, w, h = region
        self._monitor = {"left": x, "top": y, "width": w, "height": h}
        self._mask_buffer = np.zeros((h, w), dtype=np.uint8)

    def _capture(self, compare_mask=None):
        bgra = np.array(self._sct.grab(self._monitor))
        rgb = cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGB)
        fill_detect_mask(rgb, self.compiled_rules, self._mask_buffer)
        if self.config.debug and compare_mask is not None and self.config.debug_dir:
            removed_mask = cv2.bitwise_and(compare_mask, cv2.bitwise_not(self._mask_buffer))
            added_mask = cv2.bitwise_and(self._mask_buffer, cv2.bitwise_not(compare_mask))
            if cv2.countNonZero(removed_mask) > 0 or cv2.countNonZero(added_mask) > 0:
                os.makedirs(self.config.debug_dir, exist_ok=True)
                debug_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                debug_bgr[removed_mask > 0] = (0, 0, 255)
                debug_bgr[added_mask > 0] = (0, 255, 0)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                cv2.imwrite(os.path.join(self.config.debug_dir, f"diff_{timestamp}.png"), debug_bgr)
        return rgb, self._mask_buffer

    def _set_baseline(self, mask):
        self._baseline_mask = mask.copy()
        self._baseline_count = cv2.countNonZero(self._baseline_mask)
        self._total_pixels = self._baseline_mask.size

    def _score(self, mask):
        current_count = cv2.countNonZero(mask)
        pixel_diff = cv2.countNonZero(cv2.bitwise_xor(self._baseline_mask, mask)) / max(self._total_pixels, 1)
        count_diff = abs(current_count - self._baseline_count) / max(self._baseline_count, current_count, 1)
        pixel_ratio = pixel_diff / max(self.config.pixel_threshold, 1e-9)
        count_ratio = count_diff / max(self.config.count_threshold, 1e-9)
        return max(pixel_ratio, count_ratio), pixel_ratio, count_ratio, current_count

    @QtCore.Slot()
    def start_work(self):
        if self._timer is not None:
            return False
        try:
            self._sct = mss.MSS()
            rgb, mask = self._capture()
            self._set_baseline(mask)
            self._timer = QtCore.QTimer(self)
            self._timer.timeout.connect(self._on_timeout)
            self._debounce_timer = QtCore.QTimer(self)
            self._debounce_timer.setSingleShot(True)
            self._debounce_timer.timeout.connect(self._on_debounce_timeout)
            self.status_msg.emit(I18n.get("status_detect_started"))
            self.triggered.emit(1.0, rgb, self.session_id, time.perf_counter())
        except Exception as e:
            if self._sct:
                self._sct.close()
                self._sct = None
            message = I18n.get("status_detect_start_error", e)
            self.status_msg.emit(message)
            self.start_failed.emit(message, self.session_id)
            logger.exception(I18n.get("log_detect_start_failed"))

    @QtCore.Slot()
    def stop_work(self):
        self._change_detected_at = None
        if self._timer:
            self._timer.stop()
            self._timer.deleteLater()
            self._timer = None
        if self._debounce_timer:
            self._debounce_timer.stop()
            self._debounce_timer.deleteLater()
            self._debounce_timer = None
        if self._sct:
            self._sct.close()
            self._sct = None
        self.status_msg.emit(I18n.get("status_detect_stopped"))

    @QtCore.Slot(object)
    def update_config(self, new_config):
        old_config = self.config
        self.config = new_config
        rules_changed = old_config.rules != new_config.rules
        if rules_changed:
            self.compiled_rules = compile_detect_rules(new_config.rules)
        if self._timer and old_config.interval_ms != new_config.interval_ms:
            self._timer.setInterval(new_config.interval_ms)
        if self._sct and (old_config.region != new_config.region or rules_changed):
            if self._timer:
                self._timer.stop()
            if self._debounce_timer:
                self._debounce_timer.stop()
            self._change_detected_at = None
            self._init_region_buffers(new_config.region)
            rgb, mask = self._capture()
            self._set_baseline(mask)
            self.status_msg.emit(I18n.get("status_detect_updated"))
            self.triggered.emit(1.0, rgb, self.session_id, time.perf_counter())

    def _on_timeout(self):
        try:
            self._is_fast_pass = False
            _, mask = self._capture(self._baseline_mask)
            score, pixel_ratio, count_ratio, _ = self._score(mask)
            poll_message = I18n.get("log_detect_poll", pixel_ratio, count_ratio)
            logger.trace(poll_message)
            if score > 1.0:
                self.debug_msg.emit(I18n.get("debug_detect_poll", score, pixel_ratio, count_ratio))
                self._timer.stop()
                self._change_detected_at = time.perf_counter()
                self._is_fast_pass = score > 2.0
                mode = I18n.get("detect_mode_fast" if self._is_fast_pass else "detect_mode_normal")
                self.status_msg.emit(I18n.get("status_detect_change", score, mode))
                self._debounce_timer.start(int(self.config.debounce_delay * 1000))
        except Exception as e:
            self.status_msg.emit(I18n.get("status_detect_poll_error", e))
            logger.exception(I18n.get("log_detect_poll_error"))
            if self._timer and self._sct:
                self._timer.start(self.config.interval_ms)

    def _on_debounce_timeout(self):
        try:
            if self._is_fast_pass:
                rgb, mask = self._capture()
                self._set_baseline(mask)
                self.status_msg.emit(I18n.get("status_detect_stable"))
                self.triggered.emit(2.0, rgb, self.session_id, self._change_detected_at)
                self._change_detected_at = None
                self._is_fast_pass = False
                return
            rgb, mask = self._capture(self._baseline_mask)
            score, pixel_ratio, count_ratio, current_count = self._score(mask)
            self.debug_msg.emit(I18n.get("debug_detect_poll", score, pixel_ratio, count_ratio))
            if score > 1.0:
                self._baseline_mask = mask.copy()
                self._baseline_count = current_count
                self.status_msg.emit(I18n.get("status_detect_submit", score, pixel_ratio, count_ratio))
                self.triggered.emit(score, rgb, self.session_id, self._change_detected_at)
                self._change_detected_at = None
            else:
                self._change_detected_at = None
                self.status_msg.emit(I18n.get("status_detect_review_failed"))
                self._timer.start(self.config.interval_ms)
            self._is_fast_pass = False
        except Exception as e:
            self._is_fast_pass = False
            self._change_detected_at = None
            self.status_msg.emit(I18n.get("status_detect_review_error", e))
            logger.exception(I18n.get("log_detect_review_error"))
            if self._timer and self._sct:
                self._timer.start(self.config.interval_ms)

    @QtCore.Slot()
    def resume_work(self):
        if self._timer and self._sct:
            self.status_msg.emit(I18n.get("status_detect_resumed"))
            self._timer.start(self.config.interval_ms)


class OCRWorker(QtCore.QRunnable):
    """
    OCR 工作单元
    在线程池中运行，执行 "截图数据 -> OCR -> 模糊匹配" 的流程
    """

    class Signals(QtCore.QObject):
        # 修改前: finished = QtCore.Signal(str, str)

        # 修改后: 增加一个 bool 参数代表 is_success
        # 格式: (是否成功, 主文本/错误信息, 状态栏附加信息, 是否允许自动复制/保存)
        finished = QtCore.Signal(bool, str, str, bool, str, object, object)
        debug = QtCore.Signal(str)
        status = QtCore.Signal(str)

    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data
        self.signals = self.Signals()

    @staticmethod
    def hex_to_hsv(hex_color):
        """将 RRGGBBAA 或 RRGGBB 转换为 OpenCV 的 HSV 格式。"""
        hex_color = hex_color.replace("<color=", "").replace(">", "").replace("#", "")
        if len(hex_color) < 6:
            raise ValueError(f"颜色值长度不足，无法解析: {hex_color}")

        # hex 颜色按 RGB 读取；OpenCV 的 HSV 仍然使用 H:0-179, S/V:0-255。
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        color_rgb = np.uint8([[[r, g, b]]])
        color_hsv = cv2.cvtColor(color_rgb, cv2.COLOR_RGB2HSV)[0][0]
        return int(color_hsv[0]), int(color_hsv[1]), int(color_hsv[2])

    @classmethod
    def extract_shape_by_color(
            cls,
            image_input,
            hex_color,
            tolerances,
            close_kernel_size=None,
            open_kernel_size=None,
            debug=False,
            debug_dir=None
    ):
        """
        从 Image_提取.py 合入的颜色提取逻辑：
        1. 根据目标颜色生成 HSV mask；
        2. 可选闭运算/开运算合并横线并去噪；
        3. 返回位于图像中心容差范围内的轮廓包围框。
        """
        if isinstance(image_input, np.ndarray):
            img = image_input.copy()
        else:
            raise TypeError("image_input 必须是 OpenCV 图像(numpy.ndarray)")

        h, s, v = cls.hex_to_hsv(hex_color)
        h_tol, s_tol, v_tol = tolerances

        lower_bound = np.array([max(0, h - h_tol), max(0, s - s_tol), max(0, v - v_tol)])
        upper_bound = np.array([min(179, h + h_tol), min(255, s + s_tol), min(255, v + v_tol)])

        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)

        if debug:
            debug_dir = debug_dir or Config.PRE_OCR_CROP_DEBUG_DIR
            os.makedirs(debug_dir, exist_ok=True)
            cv2.imwrite(os.path.join(debug_dir, "process_0.png"), mask)

        if close_kernel_size is not None:
            kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, close_kernel_size)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
            if debug:
                cv2.imwrite(os.path.join(debug_dir, "process_1.png"), mask)

        if open_kernel_size is not None:
            kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, open_kernel_size)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
            if debug:
                cv2.imwrite(os.path.join(debug_dir, "process_2.png"), mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        results = []
        image_width = img.shape[1]
        image_center_x = image_width / 2
        max_center_offset = image_center_x * 3 / 4

        for contour in contours:
            x, y, w, h_box = cv2.boundingRect(contour)
            box_center_x = x + w // 2
            box_center_y = y + h_box // 2
            center_offset = abs(box_center_x - image_center_x)

            if debug:
                logger.trace(I18n.get("log_crop_candidate", x, y, w, h_box, center_offset))

            if center_offset <= max_center_offset:
                results.append({
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h_box,
                    "center": (box_center_x, box_center_y)
                })
                if debug:
                    cv2.rectangle(img, (x, y), (x + w, y + h_box), (0, 0, 255), 2)

        if debug:
            cv2.imwrite(os.path.join(debug_dir, "process_4.png"), img)

        return results

    @classmethod
    def crop_image_below_detected_box(cls, img_cv, game_key, debug_cb=None):
        """
        OCR 前预判裁剪：检测目标色横线/框后，将 OCR 图片裁到该框底边以下。
        裁剪方式是保留整张图的横向宽度，只改变上边界。
        返回 (图片, 是否成功裁剪)，供后续高度过滤判断。
        """
        crop_rules = Config.OCR.get("PRE_OCR_CROP_RULES", {})

        # 全局开关：一键关闭所有游戏的 OCR 前裁剪
        if not crop_rules.get("enabled", False):
            if debug_cb:
                debug_cb(I18n.get("debug_crop_skipped", I18n.get("debug_crop_reason_disabled")))
            return img_cv, False

        # 全局 debug 开关：一键开启/关闭所有 OCR 前裁剪调试图保存
        debug_enabled = crop_rules.get("debug", False)

        rule = crop_rules.get(game_key)
        if not rule or not rule.get("enabled", False):
            if debug_cb:
                debug_cb(I18n.get("debug_crop_skipped", I18n.get("debug_crop_reason_no_rule")))
            return img_cv, False

        if debug_enabled:
            os.makedirs(Config.PRE_OCR_CROP_DEBUG_DIR, exist_ok=True)
            cv2.imwrite(os.path.join(Config.PRE_OCR_CROP_DEBUG_DIR, "process_input.png"), img_cv)

        boxes = cls.extract_shape_by_color(
            img_cv,
            rule["hex_color"],
            rule["tolerances"],
            rule.get("close_kernel_size"),
            rule.get("open_kernel_size"),
            debug=debug_enabled,
            debug_dir=Config.PRE_OCR_CROP_DEBUG_DIR
        )

        if not boxes:
            logger.trace(I18n.get("log_crop_none", game_key))
            if debug_cb:
                debug_cb(I18n.get("debug_crop_skipped", I18n.get("debug_crop_reason_not_found")))
            return img_cv, False

        image_h, image_w = img_cv.shape[:2]
        image_center_x = image_w / 2

        def box_score(box):
            box_center_x = box["x"] + box["w"] / 2

            center_offset = abs(box_center_x - image_center_x)
            top_offset = box["y"]

            center_score = center_offset / max(image_w / 2, 1)
            top_score = top_offset / max(image_h, 1)

            return center_score * 8 + top_score

        target_box = min(boxes, key=box_score)

        crop_y = int(target_box["y"] + target_box["h"] + rule.get("padding_top", 0))
        min_remaining_height = int(rule.get("min_remaining_height", 20))

        if crop_y <= 0 or crop_y >= img_cv.shape[0] - min_remaining_height:
            logger.trace(I18n.get("log_crop_invalid", target_box, img_cv.shape[0]))
            if debug_cb:
                debug_cb(I18n.get("debug_crop_skipped", I18n.get("debug_crop_reason_invalid")))
            return img_cv, False

        logger.trace(I18n.get("log_crop_use", target_box, crop_y))
        cropped_img = img_cv[crop_y:, :].copy()
        if debug_cb:
            debug_cb(I18n.get("debug_crop_applied", crop_y, image_h, image_h - crop_y))
        if debug_enabled:
            cv2.imwrite(os.path.join(Config.PRE_OCR_CROP_DEBUG_DIR, "process_cropped.png"), cropped_img)
        return cropped_img, True

    def run(self):
        try:
            # --- 计时开始 ---
            t_start = time.perf_counter()

            # 提取常规参数
            ocr_engine_std = self.task_data.get('ocr_engine_std')
            ocr_engine_light = self.task_data.get('ocr_engine_light')
            text_matcher = self.task_data.get('text_matcher')
            match_mode = self.task_data.get('match_mode', 0)
            similarity_threshold = self.task_data.get('similarity_threshold')
            img_cv = self.task_data.get('img_cv')  # <--- [核心修改] 直接获取已截好的图像
            game_key = self.task_data.get('game_key', 'Unknown')
            source_lang = self.task_data.get('source_lang', 'Unknown')

            # [Log] 记录开始 (Debug级别)
            logger.debug(I18n.get("log_ocr_worker_start"))
            # 支持在子线程中截图

            if img_cv is None:
                raise ValueError("Image data is missing")

            # ========================================================
            # OCR 前预判裁剪：先用 Image_提取.py 的颜色识别逻辑找参考横线/框，
            # 再把送入 OCR 的图片裁到该框底边以下，避免上方 UI 文本干扰识别。
            crop_succeeded = False
            if match_mode != 0:
                img_cv, crop_succeeded = self.crop_image_below_detected_box(
                    img_cv, game_key, self.signals.debug.emit
                )
            # ========================================================

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
            raw_text = self.run_rapidocr(
                ocr_engine_light, img_cv, game_key, source_lang, match_mode, crop_succeeded,
                self.signals.debug.emit
            )

            # 2. === [核心修改] ===
            # 只有当返回值为 None (轻量级引擎真的什么瞎了什么都没看到) 时，才去触发标准模型兜底
            # 如果返回的是 ""，说明看到了无关的字并被成功剔除，不用再费劲去重试了
            #if raw_text is None:
            #    fallback_message = I18n.get("log_ocr_fallback")
            #    logger.trace(fallback_message)
            #    self.signals.debug.emit(fallback_message)
            #    self.signals.status.emit(fallback_message)
            #    # 扔给标准引擎 (如 1280 边长限制) 再仔细看一遍
            #    raw_text = self.run_rapidocr(
            #        ocr_engine_std, img_cv, game_key, source_lang, match_mode, crop_succeeded,
            #        self.signals.debug.emit
            #    )

            # --- 计时：OCR完成 ---
            t_process2 = time.perf_counter()
            ocr_cost = t_process2 - t_process1
            perf_metrics = {
                "capture": capture_cost,
                "ocr": ocr_cost,
                "match": 0.0,
                "detect_to_trigger": self.task_data.get("detect_to_trigger"),
            }

            # --- 修改点 A: OCR 识别为空的处理 ---
            # 无论是 None (彻底没字) 还是 "" (被过滤空了)，对于 UI 来说都是“没识别到有效文本”
            if not raw_text or raw_text.strip() == "":
                self.signals.finished.emit(
                    True, "", I18n.get("status_no_text"), False, self.task_data.get("task_source", "manual"),
                    self.task_data.get("detect_session_id"), perf_metrics
                )
                return

            # 获取分离的匹配结果
            text_original, text_translated, similarity = self.process_text_with_matching(
                raw_text, text_matcher, match_mode, similarity_threshold
            )

            # --- 计时结束：文本匹配 ---
            t_end = time.perf_counter()
            match_cost = t_end - t_process2
            perf_metrics["match"] = match_cost

            if text_translated:
                # 匹配成功：允许自动复制/保存
                subtitle_text = f"{text_original}\n{text_translated}"
                status_info = ""
                perf_metrics["similarity"] = similarity
                allow_auto_output = True
            else:
                # 未匹配：匹配模式关闭时保留原行为；匹配模式开启时不复制/保存未匹配原文
                subtitle_text = text_original
                status_info = ""
                allow_auto_output = (match_mode == 0)

            self.signals.finished.emit(
                True, subtitle_text, status_info, allow_auto_output, self.task_data.get("task_source", "manual"),
                self.task_data.get("detect_session_id"), perf_metrics
            )

        except Exception as e:
            # [关键修改] 自动记录报错堆栈，但仍发射信号通知UI
            logger.exception(I18n.get("log_ocr_fatal"))
            # [修复] 接入 I18n 处理异常信息
            self.signals.finished.emit(
                False, I18n.get("status_ocr_error", str(e)), "", False, self.task_data.get("task_source", "manual"),
                self.task_data.get("detect_session_id"), None
            )

    def run_rapidocr(
            self, engine, img, game_key, source_lang, match_mode, crop_succeeded=False, debug_cb=None):
        """
        调用 RapidOCR 引擎进行推理
        根据匹配模式、游戏和语言，动态进行特征过滤
        """
        result, _ = engine(img)

        if not result:
            logger.trace(I18n.get("log_rapidocr_empty"))
            return None

        logger.trace(I18n.get("log_rapidocr_raw", result))

        # ========================================================
        # === 特征过滤逻辑 (由 match_mode 决定) ===
        # ========================================================

        # 匹配关闭或黄线未成功裁剪时，完整保留 OCR 结果，不执行中心/高度过滤。
        if match_mode == 0 or not crop_succeeded:
            filtered_result = result
        else:
            # 只有黄线成功裁剪后才允许进入中心区域与高度过滤。
            height_rules_map = Config.OCR.get("TEXT_HEIGHT_FILTER_RULES", {})
            default_height_rules = height_rules_map.get("DEFAULT", {})
            game_height_rules = height_rules_map.get(game_key, {})
            height_rules = {**default_height_rules, **game_height_rules}
            height_filter_enabled = (
                height_rules_map.get("enabled", False)
                and height_rules.get("enabled", False)
            )
            height_min = height_rules.get("height_min", 15)
            height_max = height_rules.get("height_max", 60)

            image_width = img.shape[1]
            screen_center_x = image_width / 2
            max_center_offset = screen_center_x * 3 / 4
            filtered_result = []

            if not height_filter_enabled and debug_cb:
                debug_cb(I18n.get("debug_height_filter_disabled"))

            for item in result:
                box = item[0]
                text = item[1]
                pt_tl, pt_tr, pt_br, pt_bl = box[0], box[1], box[2], box[3]

                box_center_x = (pt_tl[0] + pt_tr[0] + pt_br[0] + pt_bl[0]) / 4
                center_offset = abs(box_center_x - screen_center_x)
                is_centered = center_offset <= max_center_offset

                if not height_filter_enabled:
                    if is_centered:
                        filtered_result.append(item)
                    continue

                mid_top_x = (pt_tl[0] + pt_tr[0]) / 2
                mid_top_y = (pt_tl[1] + pt_tr[1]) / 2
                mid_bot_x = (pt_bl[0] + pt_br[0]) / 2
                mid_bot_y = (pt_bl[1] + pt_br[1]) / 2
                text_height = ((mid_bot_x - mid_top_x) ** 2 + (mid_bot_y - mid_top_y) ** 2) ** 0.5
                is_valid_height = height_min <= text_height <= height_max
                should_include = is_centered and is_valid_height
                filter_state = I18n.get("log_filter_on")

                if should_include:
                    filtered_result.append(item)
                    message = I18n.get("log_text_include", text, center_offset, text_height, filter_state)
                else:
                    message = I18n.get(
                        "log_text_exclude", text, center_offset, text_height, height_min, height_max, filter_state
                    )

                logger.trace(message)
                if debug_cb:
                    debug_cb(message)

        if not filtered_result:
            logger.trace(I18n.get("log_filtered_empty"))
            return ""

        # ========================================================
        # === 文本智能拼接逻辑 ===
        # ========================================================
        full_text = filtered_result[0][1]
        prev_box = filtered_result[0][0]

        for i in range(1, len(filtered_result)):
            curr_text = filtered_result[i][1]
            curr_box = filtered_result[i][0]

            prev_bottom_y = (prev_box[2][1] + prev_box[3][1]) / 2
            curr_top_y = (curr_box[0][1] + curr_box[1][1]) / 2

            if prev_bottom_y < curr_top_y:
                full_text += "\n" + curr_text
            else:
                full_text += " " + curr_text

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
    基于基础映射、静态候选和用户配置构造运行时匹配数据。
    """

    def __init__(self, cache_size=3, len_cache_size=10):
        self.text_map = {}
        self.static_candidates = []
        self.cache = {}
        self.cache_size = cache_size
        self.len_cache_size = len_cache_size
        self.len_cache = {}
        self.global_step = 0
        self.decay_factor = 0.9
        self.log_decay = math.log(self.decay_factor)
        self.game_key = Config.DEFAULTS["game"]
        self.source_lang = Config.DEFAULTS["source_lang"]
        self.target_lang = Config.DEFAULTS["target_lang"]
        self.nickname = Config.DEFAULTS["player_nickname"]
        self.gender = Config.DEFAULTS["protagonist_gender"]
        self.keys_list = []
        self.candidates_full = []
        self.exact_index = {}
        self.hits = 0
        self.misses = 0

    def set_data(self, text_map=None, static_candidates=None, game_key=None, source_lang=None, target_lang=None):
        data_changed = False
        if text_map is not None:
            self.text_map = text_map
            data_changed = True
        if static_candidates is not None:
            self.static_candidates = static_candidates
            data_changed = True
        for name, value in (
                ("game_key", game_key),
                ("source_lang", source_lang),
                ("target_lang", target_lang),
        ):
            if value is not None and value != getattr(self, name):
                setattr(self, name, value)
                data_changed = True
        if data_changed:
            self._rebuild_candidates()

    def set_profile(self, nickname, gender):
        nickname = str(nickname or "").strip()
        gender = "male" if gender == "male" else "female"
        if nickname == self.nickname and gender == self.gender:
            return False
        self.nickname = nickname
        self.gender = gender
        self._rebuild_candidates()

    def _rebuild_candidates(self):
        static_keys = []
        dynamic_keys = []
        for key in self.text_map:
            (dynamic_keys if TextMapLoader.has_dynamic_tags(key) else static_keys).append(key)

        if len(static_keys) != len(self.static_candidates):
            self.keys_list = []
            self.candidates_full = []
            self.exact_index = {}
            self.clear_cache()
            return

        dynamic_candidates = [
            TextMapLoader.clean_match_text(
                key, self.game_key, self.source_lang, self.nickname, self.gender
            )
            for key in dynamic_keys
        ]
        self.keys_list = static_keys + dynamic_keys
        self.candidates_full = list(self.static_candidates) + dynamic_candidates
        self.exact_index = {}
        for index, candidate in enumerate(self.candidates_full):
            self.exact_index.setdefault(candidate, index)
        self.clear_cache()

    def _normalize_ocr(self, text):
        return TextMapLoader.clean_match_text(
            text, self.game_key, self.source_lang, self.nickname, self.gender
        )

    def match_text(self, ocr_text, mode, threshold):
        """对外暴露的匹配接口，带缓存"""
        if mode == 0 or not ocr_text or not self.candidates_full:
            return None, None, 0

        normalized_ocr = self._normalize_ocr(ocr_text)
        cache_key = f"{normalized_ocr}_{mode}_{threshold}"
        if cache_key in self.cache:
            self.hits += 1
            val = self.cache.pop(cache_key)
            self.cache[cache_key] = val
            return val

        self.misses += 1

        if mode == 1:
            result = self._match_full_text(normalized_ocr, threshold)
        elif mode == 2:
            result = self._match_prefix_by_length(normalized_ocr, threshold)
        else:
            result = (None, None, 0)

        if len(self.cache) >= self.cache_size:
            self.cache.pop(next(iter(self.cache)))

        self.cache[cache_key] = result
        return result

    def _get_formatted_value(self, key):
        """匹配成功后才按用户配置渲染译文。"""
        val = self.text_map.get(key)
        if isinstance(val, list):
            rendered = [
                TextMapLoader.clean_display_text(
                    item, self.game_key, self.target_lang, self.nickname, self.gender
                )
                for item in val
            ]
            return " / ".join(item for item in rendered if item)
        return TextMapLoader.clean_display_text(
            str(val), self.game_key, self.target_lang, self.nickname, self.gender
        )

    def _get_display_key(self, key):
        return TextMapLoader.clean_display_text(
            key, self.game_key, self.source_lang, self.nickname, self.gender
        )

    def _process_fuzzy_results(self, ocr_text, candidates, similarity_threshold):
        result = process.extractOne(
            ocr_text,
            candidates,
            scorer=fuzz.QRatio
        )

        if not result:
            return None, None, 0

        # 最高置信度结果处理
        best_match_str, score, idx = result
        if score >= similarity_threshold:
            best_key = self.keys_list[idx]
            return self._get_display_key(best_key), self._get_formatted_value(best_key), f"{score:.2f}"

        return None, None, 0

    def _match_full_text(self, ocr_text, similarity_threshold):
        if not self.candidates_full or not ocr_text.strip():
            return None, None, 0

        exact_index = self.exact_index.get(ocr_text)
        if exact_index is not None:
            key = self.keys_list[exact_index]
            return self._get_display_key(key), self._get_formatted_value(key), 100

        return self._process_fuzzy_results(ocr_text, self.candidates_full, similarity_threshold)

    def _evict_len_cache(self):
        """最优算法：基于静态对数代理分的极简淘汰 (O(N) 且零数学计算)"""
        if not self.len_cache: return
        # 直接利用 Python 内置的 min 函数配合 lambda 提取最小的 proxy_score 对应的 key
        lowest_key = min(self.len_cache, key=lambda k: self.len_cache[k]['proxy_score'])
        del self.len_cache[lowest_key]

    def _match_prefix_by_length(self, ocr_text, similarity_threshold):
        if not self.text_map or not ocr_text.strip():
            return None, None, 0

        target_len = len(ocr_text)
        # 每次调用，全局逻辑时钟推进一步
        self.global_step += 1

        # 1. 缓存查漏：不存在时才进行高开销的截取初始化
        if target_len not in self.len_cache:
            if len(self.len_cache) >= self.len_cache_size:
                self._evict_len_cache()

            self.len_cache[target_len] = {
                'data': [candidate[:target_len + 2] for candidate in self.candidates_full],
                'score': 0.0,
                'last_step': self.global_step
            }

        # ✅ 修复缩进：将状态更新移出 if 块，保证每次命中缓存时，时钟和权重都能正确刷新
        cache_item = self.len_cache[target_len]

        # 计算距离该元素上一次被命中过去了多少步
        distance = self.global_step - cache_item['last_step']
        # 衰减历史权重，并为本次命中贡献 1.0 的热度
        cache_item['score'] = cache_item['score'] * (self.decay_factor ** distance) + 1.0
        # 更新最后一次访问的时间戳为当前最新时钟
        cache_item['last_step'] = self.global_step
        # 重新静态计算并存储供淘汰器比对的静态代理分(基于 ln(S) - Ti * ln(a))
        cache_item['proxy_score'] = math.log(cache_item['score']) - self.global_step * self.log_decay

        # 2. 执行模糊匹配
        return self._process_fuzzy_results(ocr_text, cache_item['data'], similarity_threshold)

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
    task_completed = QtCore.Signal(bool, str, str, bool, str, object, object)
    task_dropped = QtCore.Signal(str, object)
    task_debug = QtCore.Signal(str)
    task_status = QtCore.Signal(str)

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
            logger.debug(I18n.get("log_queue_drop", len(self.task_queue)))
            self.task_dropped.emit(
                removed_task.get("task_source", "manual"),
                removed_task.get("detect_session_id"),
            )
        self.task_queue.append(task_data)
        self.total_submitted += 1
        # logger.trace 用于极高频信息
        submit_message = I18n.get("log_task_submit", len(self.task_queue), self.active_tasks)
        logger.trace(submit_message)
        self.task_debug.emit(submit_message)
        self._process_queue()

    def _process_queue(self):
        """检查是否有空闲线程和待处理任务"""
        idle_threads = self.thread_pool.maxThreadCount() - self.active_tasks
        while idle_threads > 0 and self.task_queue:
            task_data = self.task_queue.pop(0)
            worker = OCRWorker(task_data)
            worker.signals.finished.connect(self._on_task_completed)
            worker.signals.debug.connect(self.task_debug)
            worker.signals.status.connect(self.task_status)
            self.thread_pool.start(worker)  # 放入线程池执行
            self.active_tasks += 1
            idle_threads -= 1
            logger.debug(I18n.get("log_worker_start", len(self.task_queue)))

    def _on_task_completed(self, is_success, main_text, status_info, allow_auto_output, task_source,
                           detect_session_id, perf_metrics):
        """任务完成后的回调"""
        self.active_tasks -= 1
        self.total_completed += 1
        # 转发 4 个参数给主窗口
        self.task_completed.emit(
            is_success, main_text, status_info, allow_auto_output, task_source, detect_session_id, perf_metrics
        )
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
        logger.info(I18n.get("log_tasks_reset", queue_len))


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
    }

    # 定义向 UI 通信的信号
    dict_progress_signal = QtCore.Signal(str, list)  # 字典下载/合并进度文本
    dict_percent_signal = QtCore.Signal(int)  # 字典进度条百分比
    dict_download_detail_signal = QtCore.Signal(str, str, int, str, str)  # 游戏、文件、百分比、大小、速率

    # 统一下发 UI 状态：(业务状态枚举, 缺失文件列表, 当前层级, 目标层级)
    ui_state_signal = QtCore.Signal(str, list, int, int)
    ui_lock_signal = QtCore.Signal(bool)  # 锁定/解锁界面操作

    ocr_result_signal = QtCore.Signal(bool, str, str, bool, str)  # OCR完成信号，含任务来源
    ocr_status_signal = QtCore.Signal(str)
    manual_ocr_dropped_signal = QtCore.Signal()
    detect_status_signal = QtCore.Signal(str)
    detect_failed_signal = QtCore.Signal(str)
    debug_event_signal = QtCore.Signal(str)
    detect_start_signal = QtCore.Signal()
    detect_resume_signal = QtCore.Signal()
    detect_update_signal = QtCore.Signal(object)

    def __init__(self):
        super().__init__()
        # --- 业务状态 ---
        self.current_game = Config.DEFAULTS["game"]
        self.source_lang = Config.DEFAULTS["source_lang"]
        self.target_lang = Config.DEFAULTS["target_lang"]
        self.match_mode = Config.DEFAULTS["match_mode"]
        self.similarity_threshold = Config.DEFAULTS["similarity_threshold"]
        self.personalization_profiles = {
            (game_key, source_lang): dict(profile)
            for game_key, languages in Config.PERSONALIZATION_DEFAULTS.items()
            for source_lang, profile in languages.items()
        }
        self.player_nickname = ""
        self.protagonist_gender = "female"
        self._apply_personalization_profile()

        self.text_matcher = TextMatcher(cache_size=3, len_cache_size=10) # <--- 显式标注我们给它预留了 10 条缓存
        self.text_matcher.set_profile(self.player_nickname, self.protagonist_gender)

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
            logger.error(I18n.get("log_rapidocr_init_failed", e))
            self.ocr_engine_std = None
            self.ocr_engine_light = None

        self.task_manager = OCRTaskManager()
        self.task_manager.task_completed.connect(self._on_ocr_task_completed)
        self.task_manager.task_dropped.connect(self._on_ocr_task_dropped)
        self.task_manager.task_debug.connect(self.debug_event_signal)
        self.task_manager.task_status.connect(self.ocr_status_signal)
        self.dict_worker = None
        self.detect_thread = None
        self.detect_worker = None
        self._detect_signals_connected = False
        self.detect_enabled = False
        self.detect_pending_tasks = 0
        self.detect_session_id = 0
        self.performance_history = {
            "manual": deque(maxlen=10),
            "auto": deque(maxlen=10),
            "detect": deque(maxlen=10),
        }

        # 自动加载的防抖定时器 (属于业务逻辑层)
        self.auto_load_timer = QtCore.QTimer()
        self.auto_load_timer.setSingleShot(True)
        self.auto_load_timer.timeout.connect(self._run_check_and_load)

    # ================= 供 UI 调用的接口 =================

    def set_game(self, game_name):
        self.current_game = game_name
        self._apply_personalization_profile()
        self._reset_dict_state()

    def set_languages(self, source_lang, target_lang):
        source_changed = source_lang != self.source_lang
        self.source_lang = source_lang
        self.target_lang = target_lang
        if source_changed:
            self._apply_personalization_profile()
        self._reset_dict_state()

    def set_match_mode(self, mode):
        self.match_mode = mode
        self.text_matcher.clear_cache()
        self.auto_load_timer.stop()
        self._refresh_ui_state()

    def set_threshold(self, threshold):
        self.similarity_threshold = threshold
        self.text_matcher.clear_cache()

    def set_personalization(self, nickname, gender):
        self.player_nickname = str(nickname or "").strip()
        self.protagonist_gender = "male" if gender == "male" else "female"
        self.personalization_profiles[(self.current_game, self.source_lang)] = {
            "player_nickname": self.player_nickname,
            "protagonist_gender": self.protagonist_gender,
        }
        self.text_matcher.set_profile(self.player_nickname, self.protagonist_gender)

    def _apply_personalization_profile(self):
        key = (self.current_game, self.source_lang)
        profile = self.personalization_profiles.get(key)
        if profile is None:
            profile = Config.personalization_default(*key)
            self.personalization_profiles[key] = dict(profile)
        self.player_nickname = profile["player_nickname"]
        self.protagonist_gender = profile["protagonist_gender"]
        if hasattr(self, "text_matcher"):
            self.text_matcher.set_profile(self.player_nickname, self.protagonist_gender)

    def request_ocr(self, region, task_source="manual"):
        """接收 UI 传来的区域，立即截图后打包提交给任务管理器"""
        if self.ocr_engine_std is None or self.ocr_engine_light is None:
            self.ocr_result_signal.emit(False, "OCR 引擎未初始化", "", False, task_source)
            return False

        x, y, w, h = region
        monitor = {"top": y, "left": x, "width": w, "height": h}

        # === [核心修改] 立即在主线程完成截图，锁死当前画面 ===
        try:
            with mss.MSS() as sct:
                sct_img = sct.grab(monitor)
                img_np = np.array(sct_img)
                img_cv = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            logger.error(I18n.get("log_capture_failed", e))
            self.ocr_result_signal.emit(False, f"截图异常: {e}", "", False, task_source)
            return False
        # ===================================================

        task_data = {
            'img_cv': img_cv,  # <--- [修改] 传递真正的图像矩阵，而非坐标
            'text_matcher': self.text_matcher,
            'match_mode': self.match_mode,
            'similarity_threshold': self.similarity_threshold,
            'ocr_engine_std': self.ocr_engine_std,
            'ocr_engine_light': self.ocr_engine_light,
            'game_key': self.current_game,
            'source_lang': self.source_lang,
            'task_source': task_source,
        }
        self.task_manager.submit_task(task_data)
        return True

    def request_ocr_image(self, img_cv, task_source="manual", detect_session_id=None, change_detected_at=None):
        if self.ocr_engine_std is None or self.ocr_engine_light is None:
            self.ocr_result_signal.emit(False, "OCR 引擎未初始化", "", False, task_source)
            return False
        task_data = {
            "img_cv": img_cv,
            "text_matcher": self.text_matcher,
            "match_mode": self.match_mode,
            "similarity_threshold": self.similarity_threshold,
            "ocr_engine_std": self.ocr_engine_std,
            "ocr_engine_light": self.ocr_engine_light,
            "game_key": self.current_game,
            "source_lang": self.source_lang,
            "task_source": task_source,
            "detect_session_id": detect_session_id,
            "detect_to_trigger": (
                time.perf_counter() - change_detected_at if change_detected_at is not None else None
            ),
        }
        self.task_manager.submit_task(task_data)
        return True

    def _build_detect_config(self, region, frequency, sensitivity):
        detect = Config.OCR["DETECT"]
        sensitivity_scale = 2 ** ((50 - sensitivity) / 50.0)
        return DetectConfig(
            region=region,
            rules=detect["rules"][self.current_game],
            pixel_threshold=detect["pixel_threshold"] * sensitivity_scale,
            count_threshold=detect["count_threshold"] * sensitivity_scale,
            interval_ms=max(1, round(1000 / max(frequency, 1))),
            debounce_delay=detect["debounce_delay"],
            debug=detect["debug"],
            debug_dir=detect["debug_dir"],
        )

    def start_detection(self, region, frequency, sensitivity):
        if self.detect_thread is not None:
            self.update_detection(region, frequency, sensitivity)
            return
        self.detect_session_id += 1
        self.detect_enabled = True
        self.detect_pending_tasks = 0
        self.detect_thread = QtCore.QThread()
        self.detect_worker = DetectorWorker(
            self._build_detect_config(region, frequency, sensitivity), self.detect_session_id
        )
        self.detect_worker.moveToThread(self.detect_thread)
        self.detect_start_signal.connect(self.detect_worker.start_work)
        self.detect_resume_signal.connect(self.detect_worker.resume_work)
        self.detect_update_signal.connect(self.detect_worker.update_config)
        self._detect_signals_connected = True
        self.detect_worker.status_msg.connect(self._on_detect_status)
        self.detect_worker.debug_msg.connect(self.debug_event_signal)
        self.detect_worker.triggered.connect(self._on_detection_triggered)
        self.detect_worker.start_failed.connect(self._on_detection_start_failed)
        self.detect_thread.finished.connect(self.detect_worker.deleteLater)
        self.detect_thread.start()
        self.detect_start_signal.emit()

    def stop_detection(self):
        self.detect_enabled = False
        self.detect_session_id += 1
        self.detect_pending_tasks = 0
        had_worker = self.detect_worker is not None
        if self.detect_worker is not None and self.detect_thread is not None and self.detect_thread.isRunning():
            QtCore.QMetaObject.invokeMethod(
                self.detect_worker, "stop_work", QtCore.Qt.BlockingQueuedConnection
            )
        if had_worker and self._detect_signals_connected:
            self._detect_signals_connected = False
            for signal, slot in (
                (self.detect_start_signal, self.detect_worker.start_work),
                (self.detect_resume_signal, self.detect_worker.resume_work),
                (self.detect_update_signal, self.detect_worker.update_config),
            ):
                try:
                    signal.disconnect(slot)
                except (RuntimeError, TypeError):
                    pass
        if self.detect_thread is not None:
            self.detect_thread.quit()
            self.detect_thread.wait()
        self.detect_worker = None
        self.detect_thread = None

    def update_detection(self, region, frequency, sensitivity):
        if self.detect_enabled and self.detect_worker is not None:
            self.detect_update_signal.emit(self._build_detect_config(region, frequency, sensitivity))

    def _on_detect_status(self, message):
        logger.debug(message)
        self.detect_status_signal.emit(message)

    def _on_detection_start_failed(self, message, session_id):
        if session_id != self.detect_session_id:
            return
        self.stop_detection()
        self.detect_failed_signal.emit(message)

    def _on_detection_triggered(self, score, rgb_image, session_id, change_detected_at):
        if not self.detect_enabled or session_id != self.detect_session_id:
            return
        self.detect_pending_tasks += 1
        logger.debug(I18n.get("log_detect_trigger", score))
        self.debug_event_signal.emit(I18n.get("log_detect_trigger", score))
        img_cv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        if not self.request_ocr_image(
                img_cv, task_source="detect", detect_session_id=session_id,
                change_detected_at=change_detected_at):
            self._finish_detect_task(session_id, I18n.get("detect_reason_submit_failed"))

    def _finish_detect_task(self, session_id, reason):
        if session_id != self.detect_session_id:
            logger.debug(I18n.get("log_old_detect_task", session_id, reason))
            self.debug_event_signal.emit(I18n.get("log_old_detect_task", session_id, reason))
            return
        self.detect_pending_tasks = max(0, self.detect_pending_tasks - 1)
        logger.debug(I18n.get("log_detect_task_done", reason, self.detect_pending_tasks))
        self.debug_event_signal.emit(I18n.get("log_detect_task_done", reason, self.detect_pending_tasks))
        if self.detect_enabled and self.detect_pending_tasks == 0:
            self.detect_resume_signal.emit()

    def _on_ocr_task_dropped(self, task_source, detect_session_id):
        self.debug_event_signal.emit(I18n.get("log_queue_drop", len(self.task_manager.task_queue)))
        if task_source == "manual":
            self.manual_ocr_dropped_signal.emit()
        elif task_source == "detect":
            self._finish_detect_task(detect_session_id, I18n.get("detect_reason_queue_dropped"))

    def _on_ocr_task_completed(self, is_success, main_text, status_info, allow_auto_output, task_source,
                               detect_session_id, perf_metrics):
        stale_detect_session = task_source == "detect" and detect_session_id != self.detect_session_id
        if stale_detect_session:
            logger.debug(I18n.get("log_old_detect_result", detect_session_id))
            self.debug_event_signal.emit(I18n.get("log_old_detect_result", detect_session_id))
        if perf_metrics:
            perf_info = self._format_performance_stats(task_source, perf_metrics)
            similarity = perf_metrics.get("similarity")
            if similarity is not None:
                perf_info = I18n.get("status_perf_sim", perf_info, similarity)
            status_info = f"{status_info} | {perf_info}" if status_info else perf_info
        if is_success:
            log_text = main_text or I18n.get("status_no_text")
            logger.debug(I18n.get("log_ocr_complete", log_text, status_info) + "\n")
        else:
            logger.warning(I18n.get("log_task_failed", main_text) + "\n")
        self.ocr_result_signal.emit(is_success, main_text, status_info, allow_auto_output, task_source)
        if task_source == "detect" and not stale_detect_session:
            self._finish_detect_task(detect_session_id, I18n.get("detect_reason_ocr_complete"))

    def _format_performance_stats(self, task_source, metrics):
        """Use one output path for current, total, and rolling-average timing statistics."""
        sample = {
            "capture": float(metrics.get("capture", 0.0)),
            "ocr": float(metrics.get("ocr", 0.0)),
            "match": float(metrics.get("match", 0.0)),
            "detect_to_trigger": metrics.get("detect_to_trigger"),
        }
        detect_cost = sample["detect_to_trigger"]
        sample["total"] = sample["capture"] + sample["ocr"] + sample["match"]
        if detect_cost is not None:
            detect_cost = float(detect_cost)
            sample["detect_to_trigger"] = detect_cost

        history = self.performance_history.setdefault(task_source, deque(maxlen=10))
        history.append(sample)
        count = len(history)

        def average(key):
            values = [item[key] for item in history if item.get(key) is not None]
            return sum(values) / len(values) if values else 0.0

        if detect_cost is not None:
            return I18n.get(
                "status_perf_detect",
                detect_cost, sample["capture"], sample["ocr"], sample["match"], sample["total"], count,
                average("detect_to_trigger"), average("capture"), average("ocr"), average("match"),
                average("total"),
            )
        return I18n.get(
            "status_perf",
            sample["capture"], sample["ocr"], sample["match"], sample["total"], count,
            average("capture"), average("ocr"), average("match"), average("total"),
        )

    def _dispatch_worker(self, process_type):
        """
        [新增] 统一调度 DictionaryWorker 的核心方法
        :param process_type: 0(检查), 1(加载), 2(修复)
        """
        # 1. 统一计算目标掩码和缺失掩码
        required_mask = self.MODE_REQUIREMENTS.get(self.match_mode, 0)
        mem_missing = required_mask & ~self.current_data_mask

        # 已满足目标时不应进入没有 Worker 回调的 LOADING 状态。
        if mem_missing == 0:
            if process_type > 0:
                self.ui_lock_signal.emit(False)
                self._refresh_ui_state()
            return False

        # 2. 统一停止旧任务
        self._stop_previous_worker()

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
                self.dict_worker.download_detail_signal.connect(self.dict_download_detail_signal)

            self.dict_worker.start()
            return True
        return False

    def run_check(self):
        """后台静默查漏"""
        self._dispatch_worker(process_type=0)

    def run_smart_fix(self):
        """一键修复：需要阻塞定时器并锁住 UI 交互"""
        required_mask = self.MODE_REQUIREMENTS.get(self.match_mode, 0)
        mem_missing = required_mask & ~self.current_data_mask
        if mem_missing == 0:
            self.auto_load_timer.stop()
            self.ui_lock_signal.emit(False)
            self._refresh_ui_state()
            return
        if self.dict_worker and self.dict_worker.isRunning():
            self.ui_lock_signal.emit(True)
            self.ui_state_signal.emit("LOADING", [], self.current_data_mask, required_mask)
            return
        self.auto_load_timer.stop()
        self.ui_lock_signal.emit(True)
        self._dispatch_worker(process_type=2)

    def cleanup(self):
        """清理资源"""
        self.stop_detection()
        self.task_manager.cancel_all()
        self.auto_load_timer.stop()
        self.text_matcher.clear_cache()
        self._stop_previous_worker()

    # ================= 内部业务逻辑 =================

    def _reset_dict_state(self):
        self.current_data_mask = 0
        self.text_matcher.set_data(
            {}, [], self.current_game, self.source_lang, self.target_lang
        )
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
            logger.warning(I18n.get("log_stale_worker"))
            self.debug_event_signal.emit(I18n.get("log_stale_worker"))
            return

        result_mask, text_map, static_candidates = self.dict_worker.result

        # 1. 严格的内存状态管理
        if process_type != 0:
            self.text_matcher.set_data(
                text_map, static_candidates, self.current_game, self.source_lang, self.target_lang
            )
            success_mask = target_mask & ~result_mask
            self.current_data_mask |= success_mask

        # 2. 将 Worker 的质检结果抛给 UI 刷新器进行最终裁定
        self._refresh_ui_state(worker_check_result=result_mask)

    def _on_worker_error(self, success, msg):
        self.ui_lock_signal.emit(False)
        if not success:
            # ✅ 修改：直接把错误信息放进列表里，投递给主状态机！
            self.debug_event_signal.emit(I18n.get("debug_error", msg))
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
            self.auto_load_timer.start(500)

# ===== Floating UI =====
OUTPUT_DIR = BASE_DIR / "outputs"
FONT_FILES = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
]


def apply_capture_exclusion(widget, label):
    """Keep floating UI out of Windows screen captures used by OCR."""
    if sys.platform != "win32":
        return None
    try:
        hwnd = int(widget.winId())
        user32 = ctypes.windll.user32
        display_affinity_exclude = 0x00000011
        get_window_exstyle = -20
        layered_style = 0x00080000
        current_style = user32.GetWindowLongW(hwnd, get_window_exstyle)
        has_layered_style = bool(current_style & layered_style)
        if has_layered_style:
            user32.SetWindowLongW(hwnd, get_window_exstyle, current_style & ~layered_style)
        result = user32.SetWindowDisplayAffinity(
            wintypes.HWND(hwnd), wintypes.DWORD(display_affinity_exclude)
        )
        if has_layered_style:
            user32.SetWindowLongW(hwnd, get_window_exstyle, current_style)
        if not result:
            message = I18n.get("log_capture_exclusion_failed", label)
            logger.warning(message)
            return message
    except Exception as exc:
        message = I18n.get("log_capture_exclusion_error", label, exc)
        logger.warning(message)
        return message
    return None


def color(value: str, alpha: int | None = None) -> QColor:
    result = QColor(value)
    if alpha is not None:
        result.setAlpha(alpha)
    return result


def rounded_path(rect: QRectF, radius: float) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    return path


def draw_icon(painter: QPainter, name: str, center: QPointF, size: float, tint: QColor):
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing)
    painter.translate(center)
    painter.setPen(QPen(tint, max(1.6, size * 0.085), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)
    s = size / 2

    if name == "mic":
        painter.drawRoundedRect(QRectF(-s * 0.34, -s * 0.8, s * 0.68, s * 1.15), s * 0.34, s * 0.34)
        painter.drawArc(QRectF(-s * 0.62, -s * 0.15, s * 1.24, s * 1.05), 180 * 16, 180 * 16)
        painter.drawLine(QPointF(0, s * 0.9), QPointF(0, s * 1.22))
        painter.drawLine(QPointF(-s * 0.38, s * 1.22), QPointF(s * 0.38, s * 1.22))
    elif name == "subtitle":
        painter.drawRoundedRect(QRectF(-s * 0.95, -s * 0.7, s * 1.9, s * 1.4), s * 0.26, s * 0.26)
        painter.drawLine(QPointF(-s * 0.62, -s * 0.18), QPointF(s * 0.62, -s * 0.18))
        painter.drawLine(QPointF(-s * 0.62, s * 0.25), QPointF(s * 0.2, s * 0.25))
    elif name == "settings":
        for y, knob_x in [(-s * 0.62, -s * 0.3), (0, s * 0.38), (s * 0.62, -s * 0.05)]:
            painter.drawLine(QPointF(-s * 0.88, y), QPointF(s * 0.88, y))
            painter.setBrush(tint)
            painter.drawEllipse(QPointF(knob_x, y), s * 0.18, s * 0.18)
            painter.setBrush(Qt.NoBrush)
    elif name == "copy":
        painter.drawRoundedRect(QRectF(-s * 0.72, -s * 0.48, s * 1.15, s * 1.18), s * 0.12, s * 0.12)
        painter.drawRoundedRect(QRectF(-s * 0.35, -s * 0.78, s * 1.08, s * 1.12), s * 0.12, s * 0.12)
    elif name in ("pin", "pin_off"):
        painter.rotate(45)
        head = QRectF(-s * 0.54, -s * 0.82, s * 1.08, s * 0.52)
        if name == "pin_off":
            painter.setBrush(tint)
        painter.drawRoundedRect(head, s * 0.12, s * 0.12)
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(0, -s * 0.30), QPointF(0, -s * 0.02))
        painter.drawLine(QPointF(-s * 0.62, -s * 0.02), QPointF(s * 0.62, -s * 0.02))
        painter.drawLine(QPointF(0, -s * 0.02), QPointF(0, s * 0.84))
    elif name == "chevron_up":
        painter.drawLine(QPointF(-s * 0.65, s * 0.28), QPointF(0, -s * 0.35))
        painter.drawLine(QPointF(0, -s * 0.35), QPointF(s * 0.65, s * 0.28))
    elif name == "chevron_down":
        painter.drawLine(QPointF(-s * 0.65, -s * 0.28), QPointF(0, s * 0.35))
        painter.drawLine(QPointF(0, s * 0.35), QPointF(s * 0.65, -s * 0.28))
    elif name == "spark":
        painter.setBrush(tint)
        painter.setPen(Qt.NoPen)
        star = QPainterPath()
        star.moveTo(0, -s)
        star.cubicTo(s * 0.12, -s * 0.25, s * 0.25, -s * 0.12, s, 0)
        star.cubicTo(s * 0.25, s * 0.12, s * 0.12, s * 0.25, 0, s)
        star.cubicTo(-s * 0.12, s * 0.25, -s * 0.25, s * 0.12, -s, 0)
        star.cubicTo(-s * 0.25, -s * 0.12, -s * 0.12, -s * 0.25, 0, -s)
        painter.drawPath(star)
    elif name == "region":
        for x, y, dx, dy in [
            (-s * 0.9, -s * 0.9, s * 0.55, 0), (-s * 0.9, -s * 0.9, 0, s * 0.55),
            (s * 0.9, -s * 0.9, -s * 0.55, 0), (s * 0.9, -s * 0.9, 0, s * 0.55),
            (-s * 0.9, s * 0.9, s * 0.55, 0), (-s * 0.9, s * 0.9, 0, -s * 0.55),
            (s * 0.9, s * 0.9, -s * 0.55, 0), (s * 0.9, s * 0.9, 0, -s * 0.55),
        ]:
            painter.drawLine(QPointF(x, y), QPointF(x + dx, y + dy))
    elif name == "power":
        painter.drawArc(QRectF(-s * 0.78, -s * 0.68, s * 1.56, s * 1.56), -45 * 16, 270 * 16)
        painter.drawLine(QPointF(0, -s), QPointF(0, -s * 0.1))
    painter.restore()


class SoftWidget(QWidget):
    def __init__(self, parent=None, floating=False):
        super().__init__(parent)
        self._drag_offset = None
        self._drag_origin = None
        self._dragging = False
        self.floating = floating
        self.setAttribute(Qt.WA_TranslucentBackground)
        if floating:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

    def start_drag(self, event):
        self._drag_offset = event.globalPosition().toPoint() - self.mapToGlobal(QPoint(0, 0))
        self._drag_origin = event.globalPosition().toPoint()
        self._dragging = False

    def drag_to(self, event):
        if self._drag_offset is None or not event.buttons() & Qt.LeftButton:
            return False
        if not self._dragging:
            distance = (event.globalPosition().toPoint() - self._drag_origin).manhattanLength()
            self._dragging = distance >= QApplication.startDragDistance()
        if self._dragging:
            target = event.globalPosition().toPoint() - self._drag_offset
            if self.parentWidget():
                target = self.parentWidget().mapFromGlobal(target)
                bounds = self.parentWidget().rect()
            else:
                bounds = self.screen().availableGeometry()
            target.setX(max(bounds.left(), min(target.x(), bounds.right() - self.width() + 1)))
            target.setY(max(bounds.top(), min(target.y(), bounds.bottom() - self.height() + 1)))
            self.move(target)
        return self._dragging

    def finish_drag(self):
        was_dragging = self._dragging
        self._drag_offset = None
        self._drag_origin = None
        self._dragging = False
        return was_dragging

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_drag(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.drag_to(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.finish_drag()
        super().mouseReleaseEvent(event)


class FloatingBall(SoftWidget):
    MENU_REQUIRED_SPACE = 246

    ocrChanged = Signal(bool)
    regionRequested = Signal()
    settingsRequested = Signal()
    subtitleRequested = Signal()
    ballMoved = Signal(QPoint)
    userDragged = Signal()

    def __init__(self, parent=None, floating=False):
        super().__init__(parent, floating)
        if floating:
            # The ball is the application's primary window, so Windows gives
            # it a taskbar entry. Subtitle and settings remain tool windows.
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
            self.setWindowTitle(I18n.get("app_title"))
        self.expanded = False
        self.ocr_enabled = False
        self.ocr_momentary = False
        self.hovered = ""
        self.phase = 0.0
        self._menu_progress = 0.0
        self.menu_direction = "right"
        self._ball_drag_delta = None
        self.settings_window = None
        self.setFixedSize(350, 100)
        self.setMouseTracking(True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(32)

        self.animation = QPropertyAnimation(self, b"menuProgress", self)
        self.animation.setDuration(260)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.collapse_timer = QTimer(self)
        self.collapse_timer.setSingleShot(True)
        self.collapse_timer.setInterval(180)
        self.collapse_timer.timeout.connect(self.collapse)

    def get_menu_progress(self):
        return self._menu_progress

    def set_menu_progress(self, value):
        self._menu_progress = value
        self.update()

    menuProgress = Property(float, get_menu_progress, set_menu_progress)

    def get_ball_anchor(self):
        return self.ball_anchor_global()

    def set_ball_anchor(self, anchor):
        self.set_ball_anchor_global(anchor)

    ballAnchor = Property(QPoint, get_ball_anchor, set_ball_anchor)

    def tick(self):
        self.phase += 0.12
        self.update()

    def ball_rect(self):
        if self.menu_direction == "right":
            return QRectF(10, 12, 76, 76)
        return QRectF(self.width() - 86, 12, 76, 76)

    def menu_rect(self):
        width = 236 * self._menu_progress
        if self.menu_direction == "right":
            return QRectF(self.ball_rect().right() + 10, 21, width, 58)
        return QRectF(self.ball_rect().left() - width - 10, 21, width, 58)

    def ball_anchor_global(self):
        return self.mapToGlobal(self.ball_rect().topLeft().toPoint())

    def set_menu_direction(self, direction):
        if direction == self.menu_direction:
            return
        anchor = self.ball_anchor_global()
        self.menu_direction = direction
        target_global = anchor - self.ball_rect().topLeft().toPoint()
        if self.parentWidget():
            target_global = self.parentWidget().mapFromGlobal(target_global)
        self.move(target_global)

    def choose_menu_direction(self):
        anchor = self.ball_anchor_global()
        ball = self.ball_rect()
        ball_global = QRectF(anchor.x(), anchor.y(), ball.width(), ball.height())
        area = self.screen().availableGeometry()
        right_space = area.right() - ball_global.right()
        left_space = ball_global.left() - area.left()
        self.set_menu_direction("right" if right_space >= self.MENU_REQUIRED_SPACE or right_space >= left_space else "left")

    def button_centers(self):
        rect = self.menu_rect()
        if rect.width() < 180:
            return []
        return [
            ("subtitle", QPointF(rect.left() + 32, rect.center().y())),
            ("power", QPointF(rect.left() + 90, rect.center().y())),
            ("region", QPointF(rect.left() + 148, rect.center().y())),
            ("settings", QPointF(rect.left() + 206, rect.center().y())),
        ]

    def drag_bounds_global(self):
        if self.parentWidget():
            top_left = self.parentWidget().mapToGlobal(QPoint(0, 0))
            return QRect(top_left, self.parentWidget().size())
        area = self.screen().availableGeometry()
        if self.settings_window and self.settings_window.isVisible():
            offset = self.settings_window.panel_offset
            area = QRect(
                area.left(),
                area.top(),
                area.width() - offset.x() - self.settings_window.width() + int(self.ball_rect().width()),
                area.height() - offset.y() - self.settings_window.height() + int(self.ball_rect().height()),
            )
        return area

    def set_ball_anchor_global(self, anchor):
        target_global = anchor - self.ball_rect().topLeft().toPoint()
        self.move(self.parentWidget().mapFromGlobal(target_global) if self.parentWidget() else target_global)
        self.ballMoved.emit(anchor)

    def start_drag(self, event):
        self._drag_origin = event.globalPosition().toPoint()
        self._ball_drag_delta = self._drag_origin - self.ball_anchor_global()
        self._dragging = False

    def drag_to(self, event):
        if self._ball_drag_delta is None or not event.buttons() & Qt.LeftButton:
            return False
        cursor = event.globalPosition().toPoint()
        if not self._dragging:
            self._dragging = (cursor - self._drag_origin).manhattanLength() >= QApplication.startDragDistance()
        if self._dragging:
            area = self.drag_bounds_global()
            anchor = cursor - self._ball_drag_delta
            anchor.setX(max(area.left(), min(anchor.x(), area.right() - int(self.ball_rect().width()) + 1)))
            anchor.setY(max(area.top(), min(anchor.y(), area.bottom() - int(self.ball_rect().height()) + 1)))
            self.set_ball_anchor_global(anchor)
        return self._dragging

    def finish_drag(self):
        was_dragging = self._dragging
        self._ball_drag_delta = None
        self._drag_origin = None
        self._dragging = False
        return was_dragging

    def toggle(self):
        self.set_expanded(not self.expanded)

    def set_expanded(self, expanded):
        if self.expanded == expanded:
            return
        self.expanded = expanded
        self.animation.stop()
        self.animation.setStartValue(self._menu_progress)
        self.animation.setEndValue(1.0 if expanded else 0.0)
        self.animation.start()

    def expand(self):
        self.collapse_timer.stop()
        self.choose_menu_direction()
        self.set_expanded(True)

    def collapse(self):
        if not self._dragging:
            self.set_expanded(False)

    def interactive_region_contains(self, position):
        return self.ball_rect().adjusted(-8, -8, 8, 8).contains(position) or (
            self._menu_progress > 0.05 and self.menu_rect().adjusted(-6, -8, 6, 8).contains(position)
        )

    def global_ball_contains(self, global_position):
        anchor = self.ball_anchor_global()
        return QRectF(anchor.x(), anchor.y(), self.ball_rect().width(), self.ball_rect().height()).contains(global_position)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        menu = self.menu_rect()
        if menu.width() > 5:
            p.setPen(Qt.NoPen)
            p.fillPath(
                rounded_path(menu.translated(0, 5).adjusted(-4, -1, 4, 5), 32),
                color("#090b18", int(15 * self._menu_progress)),
            )
            p.fillPath(
                rounded_path(menu.translated(0, 2).adjusted(-2, -1, 2, 3), 30),
                color("#090b18", int(26 * self._menu_progress)),
            )
            p.fillPath(rounded_path(menu, 29), color("#171925", int(246 * self._menu_progress)))
            p.setPen(QPen(color("#ffffff", int(24 * self._menu_progress)), 1))
            p.drawPath(rounded_path(menu.adjusted(0.5, 0.5, -0.5, -0.5), 28))

            for name, center in self.button_centers():
                if self.hovered == name:
                    p.setPen(Qt.NoPen)
                    p.setBrush(color("#ffffff", 18))
                    p.drawEllipse(center, 22, 22)
                tint = color("#72e6aa") if name == "power" and self.ocr_enabled else color("#f5f6ff")
                draw_icon(p, name, center, 21, tint)

        ball = self.ball_rect()
        for offset, alpha in [(10, 26), (5, 55)]:
            p.setPen(Qt.NoPen)
            p.setBrush(color("#5f6fff", alpha))
            p.drawEllipse(ball.adjusted(-offset, -offset, offset, offset))

        gradient = QLinearGradient(ball.topLeft(), ball.bottomRight())
        gradient.setColorAt(0.0, color("#9b8cff"))
        gradient.setColorAt(0.48, color("#7069f7"))
        gradient.setColorAt(1.0, color("#4b8ff8"))
        p.setBrush(gradient)
        p.setPen(QPen(color("#ffffff", 72), 1.2))
        p.drawEllipse(ball)

        if self.ocr_enabled:
            pulse = 2.0 + (math.sin(self.phase) + 1) * 2.2
            p.setPen(QPen(color("#ffffff", 92), 1.4))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(ball.adjusted(pulse, pulse, -pulse, -pulse))

        center = ball.center()
        for i, height in enumerate([10, 18, 27, 18, 10]):
            animated = height * (0.72 + 0.28 * math.sin(self.phase + i * 0.75)) if self.ocr_enabled else height * 0.45
            x = center.x() + (i - 2) * 8
            p.setPen(QPen(color("#ffffff"), 4, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(x, center.y() - animated / 2), QPointF(x, center.y() + animated / 2))

        if self.expanded:
            p.setPen(QPen(color("#ffffff", 175), 1.6, Qt.SolidLine, Qt.RoundCap))
            start_angle = 132 if self.menu_direction == "right" else -48
            p.drawArc(ball.adjusted(13, 13, -13, -13), start_angle * 16, 96 * 16)

    def mouseMoveEvent(self, event):
        if self.drag_to(event):
            self.collapse_timer.stop()
            self.set_expanded(False)
            self.hovered = ""
            event.accept()
            return

        if self.interactive_region_contains(event.position()):
            self.expand()
        else:
            self.collapse_timer.start()

        self.hovered = ""
        for name, center in self.button_centers():
            if (event.position() - center).manhattanLength() < 30:
                self.hovered = name
                break
        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.ball_rect().contains(event.position()):
                self.start_drag(event)
                event.accept()
                return
            for name, center in self.button_centers():
                if (event.position() - center).manhattanLength() < 30:
                    if name == "subtitle":
                        self.subtitleRequested.emit()
                    elif name == "region":
                        self.regionRequested.emit()
                    elif name == "power":
                        self.ocr_enabled = True if self.ocr_momentary else not self.ocr_enabled
                        self.ocrChanged.emit(self.ocr_enabled)
                    elif name == "settings":
                        self.settingsRequested.emit()
                    self.update()
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        was_dragging = self.finish_drag()
        if event.button() != Qt.LeftButton:
            super().mouseReleaseEvent(event)
            return
        if was_dragging:
            self.userDragged.emit()
            QTimer.singleShot(30, self.expand)
        elif self.ball_rect().contains(event.position()):
            self.ocr_enabled = True if self.ocr_momentary else not self.ocr_enabled
            self.ocrChanged.emit(self.ocr_enabled)
            self.update()
        event.accept()

    def contextMenuEvent(self, event):
        if not self.ball_rect().contains(event.pos()):
            event.ignore()
            return

        self.collapse_timer.stop()
        self.set_expanded(False)
        menu = QtWidgets.QMenu(self)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(23, 25, 37, 246);
                border: 1px solid rgba(145, 136, 255, 120);
                border-radius: 11px;
                padding: 6px;
                color: #f5f6ff;
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
            }
            QMenu::item {
                background: transparent;
                border-radius: 7px;
                padding: 8px 30px 8px 12px;
                margin: 1px;
            }
            QMenu::item:selected {
                background-color: rgba(118, 108, 245, 82);
                color: #ffffff;
            }
        """)
        exit_action = menu.addAction(I18n.get("ui_exit_program"))
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.exec(event.globalPos())
        event.accept()

    def leaveEvent(self, event):
        self.hovered = ""
        self.collapse_timer.start()
        self.update()
        super().leaveEvent(event)

    def closeEvent(self, event):
        event.accept()
        app = QApplication.instance()
        if app is not None:
            app.quit()


class SelectableOverlayText(QtWidgets.QTextEdit):
    """Transparent selectable text that lets blank-area drags move its window."""

    def __init__(self, owner, allow_blank_drag=False):
        super().__init__(owner)
        self.owner = owner
        self.allow_blank_drag = allow_blank_drag
        self._forwarding_drag = False
        self.setReadOnly(True)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.viewport().setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: 0;
                padding: 0;
                color: #f2f3fa;
                selection-background-color: #7168c9;
                selection-color: #ffffff;
            }
        """)

    def mousePressEvent(self, event):
        layout = self.document().documentLayout()
        hit = layout.hitTest(event.position(), Qt.ExactHit)
        if (
                self.allow_blank_drag
                and event.button() == Qt.LeftButton
                and hit < 0
                and not self.owner.pinned
        ):
            self._forwarding_drag = True
            self.owner.start_drag(event)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._forwarding_drag:
            self.owner.drag_to(event)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._forwarding_drag:
            self._forwarding_drag = False
            self.owner.finish_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self is self.owner.debug_text_view:
            self.owner.scroll_debug(event.angleDelta().y())
            event.accept()
            return
        super().wheelEvent(event)


class SubtitleWindow(SoftWidget):
    def __init__(self, parent=None, floating=False):
        super().__init__(parent, floating)
        self.pinned = False
        self.subtitle_text = I18n.get("sub_waiting")
        self.status_text = I18n.get("ui_status_connected")
        self.ocr_active = False
        self.ocr_status_text = I18n.get("ui_ocr_manual_idle")
        self.match_text = I18n.get(
            ("ui_match_off", "ui_match_exact", "ui_match_prefix")[
                Config.DEFAULTS["match_mode"]
            ]
        )
        self.match_mode = Config.DEFAULTS["match_mode"]
        self.match_data_state = "off"
        self.game_text = I18n.game_name(Config.DEFAULTS["game"])
        self.language_text = (
            f"{I18n.language_name(Config.DEFAULTS['source_lang'])}  →  "
            f"{I18n.language_name(Config.DEFAULTS['target_lang'])}"
        )
        self.controls_visible = True
        self._controls_progress = 1.0
        self.subtitle_font_size = Config.DEFAULTS["subtitle_font_size"]
        self._background_opacity = Config.DEFAULTS["subtitle_opacity"]
        self._opacity_dragging = False
        self._resize_edge = ""
        self._resize_origin = None
        self._resize_start_geometry = None
        self._resize_anchor_bottom = None
        self._polling_resize = False
        self.resize_margin = 18
        self.corner_resize_margin = 36
        self.debug_scroll = 0
        self.debug_lines = []
        self.copy_feedback_active = False
        self.hovered = ""
        self.phase = 0.0
        screen = QApplication.primaryScreen().availableGeometry()
        self.minimum_window_width = 980
        self.maximum_window_width = screen.width() * 2
        self.minimum_subtitle_height = 120
        self.controls_section_height = 176
        self.debug_box_height = 108
        self.minimum_window_height = self.minimum_subtitle_height
        self.maximum_window_height = screen.height() * 2
        initial_width = round(screen.width() * 63 / 64) if floating else self.minimum_window_width
        self._subtitle_height = 166
        self.setMinimumWidth(self.minimum_window_width)
        self.setMaximumWidth(self.maximum_window_width)
        self.setMaximumHeight(self.maximum_window_height)
        self.resize(
            max(self.minimum_window_width, min(initial_width, self.maximum_window_width)),
            self._subtitle_height + self.controls_section_height,
        )
        self.debug_text_view = SelectableOverlayText(self, allow_blank_drag=True)
        self.debug_text_view.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.debug_text_view.setFont(QFont("Consolas", 8))
        self.copy_feedback_timer = QTimer(self)
        self.copy_feedback_timer.setSingleShot(True)
        self.copy_feedback_timer.setInterval(1400)
        self.copy_feedback_timer.timeout.connect(self.reset_copy_feedback)
        self.refresh_text_views()
        self.setMouseTracking(True)
        self.controls_animation = QPropertyAnimation(self, b"controlsProgress", self)
        self.controls_animation.setDuration(260)
        self.controls_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.resize_poll_timer = QTimer(self)
        self.resize_poll_timer.setInterval(8)
        self.resize_poll_timer.timeout.connect(self.poll_global_resize)
        timer = QTimer(self)
        timer.timeout.connect(self.tick)
        timer.start(38)
        self.timer = timer

    def tick(self):
        if self.ocr_active:
            self.phase += 0.11
            self.update()

    def control_centers(self):
        controls = [("controls", QPointF(self.width() - 40, self._subtitle_height - 34))]
        if self._controls_progress > 0.15:
            controls.extend([
                ("copy", QPointF(self.width() - 100, self._subtitle_height + 14)),
                ("pin", QPointF(self.width() - 50, self._subtitle_height + 14)),
            ])
        return controls

    def update_text(self, text):
        self.subtitle_text = text or "..."
        self.update()

    def set_subtitle_font_size(self, size):
        self.subtitle_font_size = size
        self.update()

    def update_status(self, text):
        full_text = str(text) if text else ""
        self.status_text = full_text.splitlines()[0] if full_text else ""
        self.update()

    def update_context(self, game, source_language, target_language):
        self.game_text = game
        self.language_text = f"{source_language}  →  {target_language}"
        self.update()

    def update_match_mode(self, mode):
        self.match_mode = mode
        self.match_text = I18n.get(("ui_match_off", "ui_match_exact", "ui_match_prefix")[mode])
        self.update()

    def update_match_data_state(self, state):
        self.match_data_state = state
        self.update()

    def match_status_text(self):
        if self.match_mode == 0 or self.match_data_state == "off":
            return self.match_text
        state_key = {
            "ready": "ui_dict_memory_ready",
            "missing": "ui_dict_memory_missing",
            "loading": "ui_dict_memory_loading",
        }.get(self.match_data_state, "ui_dict_memory_loading")
        return f"{self.match_text} · {I18n.get(state_key)}"

    def update_ocr_state(self, active, mode):
        self.ocr_active = bool(active)
        keys = (
            ("ui_ocr_manual_idle", "ui_ocr_manual_active"),
            ("ui_ocr_auto_off", "ui_ocr_auto_on"),
            ("ui_ocr_detect_off", "ui_ocr_detect_on"),
        )
        self.ocr_status_text = I18n.get(keys[mode][1 if active else 0])
        self.update()

    def retranslate_ui(self, ocr_mode, match_mode):
        self.update_match_mode(match_mode)
        self.update_ocr_state(self.ocr_active, ocr_mode)

    def get_controls_progress(self):
        return self._controls_progress

    def set_controls_progress(self, progress):
        self._controls_progress = progress
        self.setMinimumHeight(round(self.minimum_subtitle_height + self.controls_section_height * progress))
        self.resize(self.width(), round(self._subtitle_height + self.controls_section_height * progress))
        self.refresh_text_views()
        self.update()

    controlsProgress = Property(float, get_controls_progress, set_controls_progress)

    def toggle_controls(self):
        self.controls_animation.stop()
        self.controls_visible = not self.controls_visible
        self.controls_animation.setStartValue(self._controls_progress)
        self.controls_animation.setEndValue(1.0 if self.controls_visible else 0.0)
        self.controls_animation.start()

    def toggle_pinned(self):
        self.pinned = not self.pinned
        self.update()

    def opacity_track(self):
        return QRectF(self.width() - 220, self._subtitle_height + 10, 82, 8)

    def debug_rect(self):
        return QRectF(30, self._subtitle_height + 42, self.width() - 60, self.debug_box_height)

    def refresh_text_views(self):
        debug = self.debug_rect()
        self.debug_text_view.setGeometry(
            QRect(round(debug.left() + 9), round(debug.top() + 22), round(debug.width() - 22), round(debug.height() - 28))
        )
        self.debug_text_view.setVisible(self._controls_progress > 0.15)
        self.refresh_debug_text()

    def refresh_debug_text(self):
        visible_count = 5
        maximum = max(0, len(self.debug_lines) - visible_count)
        self.debug_scroll = max(0, min(self.debug_scroll, maximum))
        visible = self.debug_lines[self.debug_scroll:self.debug_scroll + visible_count]
        self.debug_text_view.setPlainText("\n".join(visible))

    def scroll_debug(self, angle_delta):
        maximum = max(0, len(self.debug_lines) - 5)
        direction = -1 if angle_delta > 0 else 1
        self.debug_scroll = max(0, min(maximum, self.debug_scroll + direction))
        self.refresh_debug_text()
        self.update()

    def copy_subtitle(self):
        if self.copy_feedback_active:
            return
        QApplication.clipboard().setText(self.subtitle_text)
        self.copy_feedback_active = True
        self.copy_feedback_timer.start()
        self.update()

    def reset_copy_feedback(self):
        self.copy_feedback_active = False
        self.update()

    def resize_edge_at(self, position):
        x, y = position.x(), position.y()
        corner = self.corner_resize_margin
        if x <= corner and y <= corner:
            return "topleft"
        if x >= self.width() - corner and y <= corner:
            return "topright"
        if x <= corner and y >= self.height() - corner:
            return "bottomleft"
        if x >= self.width() - corner and y >= self.height() - corner:
            return "bottomright"
        left = x <= self.resize_margin
        right = x >= self.width() - self.resize_margin
        top = y <= self.resize_margin
        bottom = y >= self.height() - self.resize_margin
        return ("top" if top else "bottom" if bottom else "") + ("left" if left else "right" if right else "")

    def qt_edges(self, edge):
        result = Qt.Edges()
        if "left" in edge:
            result |= Qt.LeftEdge
        if "right" in edge:
            result |= Qt.RightEdge
        if "top" in edge:
            result |= Qt.TopEdge
        if "bottom" in edge:
            result |= Qt.BottomEdge
        return result

    def start_native_resize(self, edge):
        handle = self.windowHandle()
        self.setMinimumHeight(round(self.minimum_subtitle_height + self.controls_section_height * self._controls_progress))
        return bool(handle and self.isWindow() and handle.startSystemResize(self.qt_edges(edge)))

    def start_global_resize(self, edge, global_position):
        self._resize_edge = edge
        self._resize_origin = QPoint(global_position)
        self._resize_start_geometry = QRect(self.geometry())
        self._resize_anchor_bottom = self.geometry().bottom()
        self._polling_resize = True
        self.resize_poll_timer.start()

    def finish_resize(self):
        self.resize_poll_timer.stop()
        self._polling_resize = False
        self._resize_edge = ""
        self._resize_origin = None
        self._resize_start_geometry = None
        self._resize_anchor_bottom = None

    def poll_global_resize(self):
        if not QApplication.mouseButtons() & Qt.LeftButton:
            self.finish_resize()
            return
        self.resize_to(QCursor.pos())

    def resizeEvent(self, event):
        if hasattr(self, "_subtitle_height"):
            self._subtitle_height = max(
                self.minimum_subtitle_height,
                round(self.height() - self.controls_section_height * self._controls_progress),
            )
            if hasattr(self, "debug_text_view"):
                self.refresh_text_views()
        super().resizeEvent(event)

    def update_resize_cursor(self, edge):
        cursors = {
            "left": Qt.SizeHorCursor, "right": Qt.SizeHorCursor,
            "top": Qt.SizeVerCursor, "bottom": Qt.SizeVerCursor,
            "topleft": Qt.SizeFDiagCursor, "bottomright": Qt.SizeFDiagCursor,
            "topright": Qt.SizeBDiagCursor, "bottomleft": Qt.SizeBDiagCursor,
        }
        self.setCursor(cursors.get(edge, Qt.ArrowCursor))

    def resize_to(self, global_position):
        if not self._resize_edge or self._resize_start_geometry is None:
            return False
        delta = global_position - self._resize_origin
        start = self._resize_start_geometry
        left, top, right, bottom = start.left(), start.top(), start.right(), start.bottom()
        if "left" in self._resize_edge:
            left += delta.x()
        if "right" in self._resize_edge:
            right += delta.x()
        if "top" in self._resize_edge:
            top += delta.y()
        if "bottom" in self._resize_edge:
            bottom += delta.y()
        width = right - left + 1
        height = bottom - top + 1
        bounded_width = max(self.minimum_window_width, min(width, self.maximum_window_width))
        minimum_height = self.minimum_subtitle_height + self.controls_section_height * self._controls_progress
        bounded_height = max(minimum_height, min(height, self.maximum_window_height))
        if "left" in self._resize_edge:
            left = right - bounded_width + 1
        else:
            right = left + bounded_width - 1
        if "top" in self._resize_edge:
            top = bottom - bounded_height + 1
        else:
            bottom = top + bounded_height - 1
        if "top" in self._resize_edge and self._resize_anchor_bottom is not None:
            bottom = self._resize_anchor_bottom
            top = bottom - bounded_height + 1
        target = QRect(QPoint(left, top), QPoint(right, bottom))
        if target != self.geometry():
            self.setGeometry(target)
        self._subtitle_height = max(
            self.minimum_subtitle_height,
            round(self.height() - self.controls_section_height * self._controls_progress),
        )
        self.update()
        return True

    def drag_to(self, event):
        if self._drag_offset is None or not event.buttons() & Qt.LeftButton:
            return False
        if not self._dragging:
            self._dragging = (event.globalPosition().toPoint() - self._drag_origin).manhattanLength() >= QApplication.startDragDistance()
        if self._dragging:
            target = event.globalPosition().toPoint() - self._drag_offset
            self.move(self.parentWidget().mapFromGlobal(target) if self.parentWidget() else target)
        return self._dragging

    def append_debug(self, message):
        # The debug painter allocates one fixed-height row per list item.
        # Store multiline status messages as physical rows to prevent overlap.
        lines = str(message).splitlines() or [""]
        self.debug_lines.extend(lines)
        if len(self.debug_lines) > 100:
            del self.debug_lines[:-100]
        self.debug_scroll = max(0, len(self.debug_lines) - 5)
        self.refresh_debug_text()
        self.update()

    def set_opacity_from_position(self, x):
        track = self.opacity_track()
        ratio = max(0.0, min(1.0, (x - track.left()) / track.width()))
        opacity_min, opacity_max = Config.UI_RANGES["subtitle_opacity"]
        self._background_opacity = opacity_min + ratio * (opacity_max - opacity_min)
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        body = QRectF(12, 10, self.width() - 24, self.height() - 24)
        p.save()
        p.setOpacity(self._background_opacity)
        p.setPen(Qt.NoPen)
        p.setBrush(color("#060815", 28))
        p.drawRoundedRect(body.adjusted(-1, 2, 1, 4), 23, 23)

        bg = QLinearGradient(body.topLeft(), body.bottomRight())
        bg.setColorAt(0, color("#20222d", 248))
        bg.setColorAt(1, color("#141621", 248))
        p.setBrush(bg)
        p.setPen(QPen(color("#ffffff", 28), 1))
        p.drawRoundedRect(body, 22, 22)
        p.restore()

        p.setFont(QFont("Microsoft YaHei UI", self.subtitle_font_size, QFont.Medium))
        p.setPen(color("#f2f3fa"))
        p.drawText(
            QRectF(31, 24, self.width() - 62, max(50, self._subtitle_height - 66)),
            Qt.AlignCenter | Qt.TextWordWrap,
            self.subtitle_text,
        )
        p.setFont(QFont("Microsoft YaHei UI", 8))
        p.setPen(color("#a7abba"))
        p.drawText(
            QRectF(31, self._subtitle_height - 47, self.width() - 62, 22),
            Qt.AlignCenter,
            self.status_text,
        )

        toggle_center = QPointF(self.width() - 40, self._subtitle_height - 34)
        if self.hovered == "controls":
            p.setBrush(color("#ffffff", 18))
            p.setPen(Qt.NoPen)
            p.drawEllipse(toggle_center, 16, 16)
        draw_icon(
            p,
            "chevron_down" if self.controls_visible else "chevron_up",
            toggle_center,
            15,
            color("#aeb2c7"),
        )

        if self._controls_progress > 0.01:
            p.save()
            p.setOpacity(self._controls_progress)
            p.setPen(QPen(color("#ffffff", 18), 1))
            divider_y = self._subtitle_height - 16
            controls_y = self._subtitle_height + 14
            p.drawLine(QPointF(30, divider_y), QPointF(self.width() - 30, divider_y))

            p.setPen(Qt.NoPen)
            p.setBrush(color("#9b8cff") if self.ocr_active else color("#686d80"))
            p.drawEllipse(QPointF(38, controls_y), 4, 4)
            p.setFont(QFont("Microsoft YaHei UI", 8))
            p.setPen(color("#aeb2c7"))
            p.drawText(QRectF(49, controls_y - 14, 100, 28), Qt.AlignVCenter, self.ocr_status_text)

            for i in range(16):
                x = 150 + i * 8
                h = 4 + (math.sin(self.phase * 1.4 + i * 0.8) + 1) * 4 if self.ocr_active else 4
                waveform_color = color("#8179ee", 150) if self.ocr_active else color("#686d80", 125)
                p.setPen(QPen(waveform_color, 2, Qt.SolidLine, Qt.RoundCap))
                p.drawLine(QPointF(x, controls_y - h / 2), QPointF(x, controls_y + h / 2))

            center_controls_x = max(280, self.width() / 2 - 247)
            for rect, text in [
                (QRectF(center_controls_x, controls_y - 13, 170, 26), self.match_status_text()),
                (QRectF(center_controls_x + 182, controls_y - 13, 110, 26), self.game_text),
                (QRectF(center_controls_x + 304, controls_y - 13, 190, 26), self.language_text),
            ]:
                p.setBrush(color("#ffffff", 12))
                p.setPen(QPen(color("#ffffff", 22), 1))
                p.drawRoundedRect(rect, 13, 13)
                p.setFont(QFont("Microsoft YaHei UI", 8))
                p.setPen(color("#aeb2c7"))
                p.drawText(rect, Qt.AlignCenter, text)

            track = self.opacity_track()
            opacity_min, opacity_max = Config.UI_RANGES["subtitle_opacity"]
            ratio = (self._background_opacity - opacity_min) / (opacity_max - opacity_min)
            handle_x = track.left() + track.width() * ratio
            p.setPen(QPen(color("#ffffff", 25), 3, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(track.left(), track.center().y()), QPointF(track.right(), track.center().y()))
            p.setPen(QPen(color("#9188ff"), 3, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(track.left(), track.center().y()), QPointF(handle_x, track.center().y()))
            p.setPen(Qt.NoPen)
            p.setBrush(color("#d8d4ff"))
            p.drawEllipse(QPointF(handle_x, track.center().y()), 4.5, 4.5)

            for name, center in self.control_centers()[1:]:
                disabled_copy = name == "copy" and self.copy_feedback_active
                if self.hovered == name:
                    p.setBrush(color("#ffffff", 16))
                    p.setPen(Qt.NoPen)
                    p.drawEllipse(center, 17, 17)
                if disabled_copy:
                    p.setBrush(Qt.NoBrush)
                    p.setPen(QPen(color("#d8d4ff"), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.drawLine(
                        QPointF(center.x() - 5.5, center.y()),
                        QPointF(center.x() - 1.5, center.y() + 4),
                    )
                    p.drawLine(
                        QPointF(center.x() - 1.5, center.y() + 4),
                        QPointF(center.x() + 6.5, center.y() - 5),
                    )
                    continue
                icon_name = ("pin_off" if self.pinned else "pin") if name == "pin" else name
                tint = color("#a69cff") if name == "pin" and self.pinned else color("#c7cad8")
                draw_icon(p, icon_name, center, 16, tint)

            debug = self.debug_rect()
            p.setPen(QPen(color("#ffffff", 18), 1))
            p.setBrush(color("#090b13", 145))
            p.drawRoundedRect(debug, 11, 11)
            p.setFont(QFont("Segoe UI", 7, QFont.DemiBold))
            p.setPen(color("#797f94"))
            p.drawText(QRectF(debug.left() + 12, debug.top() + 7, 140, 16), Qt.AlignVCenter, I18n.get("ui_debug_output"))

            visible_count = 5
            max_scroll = max(0, len(self.debug_lines) - visible_count)
            self.debug_scroll = min(self.debug_scroll, max_scroll)
            p.setClipPath(rounded_path(debug.adjusted(1, 1, -1, -1), 10))
            if max_scroll:
                track = QRectF(debug.right() - 7, debug.top() + 9, 2, debug.height() - 18)
                handle_height = max(18, track.height() * visible_count / len(self.debug_lines))
                handle_y = track.top() + (track.height() - handle_height) * self.debug_scroll / max_scroll
                p.setPen(Qt.NoPen)
                p.setBrush(color("#77708f", 120))
                p.drawRoundedRect(QRectF(track.left(), handle_y, track.width(), handle_height), 1, 1)
            p.restore()

    def mouseMoveEvent(self, event):
        if self._resize_edge and not self._polling_resize:
            self.resize_to(event.globalPosition().toPoint())
            event.accept()
            return
        if self._polling_resize:
            event.accept()
            return
        if self._opacity_dragging:
            self.set_opacity_from_position(event.position().x())
            event.accept()
            return
        if self.drag_to(event):
            self.hovered = ""
            event.accept()
            return
        self.hovered = ""
        for name, center in self.control_centers():
            if (event.position() - center).manhattanLength() < 25:
                self.hovered = name
                break
        self.update_resize_cursor("" if self.pinned else self.resize_edge_at(event.position()))
        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edge = "" if self.pinned else self.resize_edge_at(event.position())
            if edge:
                self.controls_animation.stop()
                # Moving top/left edges changes the window origin. Sample the
                # global cursor independently so that movement cannot feed
                # back into widget-local mouse events.
                if "top" in edge or "left" in edge:
                    self.start_global_resize(edge, event.globalPosition().toPoint())
                elif not self.start_native_resize(edge):
                    self.start_global_resize(edge, event.globalPosition().toPoint())
                event.accept()
                return
            if self._controls_progress > 0.8 and self.opacity_track().adjusted(-7, -10, 7, 10).contains(event.position()):
                self._opacity_dragging = True
                self.set_opacity_from_position(event.position().x())
                event.accept()
                return
            if self._controls_progress > 0.8 and self.debug_rect().contains(event.position()):
                if not self.pinned:
                    self.start_drag(event)
                event.accept()
                return
            for name, center in self.control_centers():
                if (event.position() - center).manhattanLength() < 26:
                    if name == "pin":
                        self.toggle_pinned()
                    elif name == "copy":
                        self.copy_subtitle()
                    elif name == "controls":
                        self.toggle_controls()
                    self.update()
                    event.accept()
                    return
            if not self.pinned:
                self.start_drag(event)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._opacity_dragging = False
        self.finish_resize()
        self.update_resize_cursor("" if self.pinned else self.resize_edge_at(event.position()))
        self.finish_drag()
        event.accept()

    def leaveEvent(self, event):
        if not self._resize_edge:
            self.unsetCursor()
        super().leaveEvent(event)

    def wheelEvent(self, event):
        if self._controls_progress > 0.8 and self.debug_rect().contains(event.position()):
            self.scroll_debug(event.angleDelta().y())
            event.accept()
            return
        super().wheelEvent(event)


class SettingsWindow(SoftWidget):
    showRegionRequested = Signal()
    smartFixRequested = Signal()
    runModeChanged = Signal(int)
    autoIntervalChanged = Signal(float)
    detectFrequencyChanged = Signal(int)
    detectSensitivityChanged = Signal(int)
    gameChanged = Signal(str)
    languagesChanged = Signal(str, str)
    matchModeChanged = Signal(int)
    thresholdChanged = Signal(int)
    personalizationChanged = Signal(str, str)
    autoCopyChanged = Signal(bool)
    autoSaveChanged = Signal(bool)
    subtitleFontSizeChanged = Signal(int)
    interfaceLanguageChanged = Signal(str)

    def __init__(self):
        super().__init__(floating=True)
        self.follow_ball_ref = None
        self.panel_offset = QPoint(46, 46)
        self.original_ball_anchor = None
        self.user_moved_ball = False
        self.opening = False
        self._group_drag_origin = None
        self._group_drag_ball_anchor = None
        self._group_dragging = False
        self._dict_locked = False
        self._match_ready = False
        self._generate_state = "off"
        self._generate_text = ""
        self.setFixedSize(500, 690)
        self.setWindowOpacity(0.0)
        self.setStyleSheet("""
            QWidget { color: #e9eaf3; font-family: "Microsoft YaHei UI"; font-size: 9pt; }
            QFrame#panel { background: #13151f; border: 1px solid rgba(255,255,255,28);
                           border-radius: 24px; }
            QFrame#section { background: #1b1e2a; border: 1px solid #2a2e3d; border-radius: 15px; }
            QFrame#section[dictLocked="true"] { background: #151721; border: 1px solid #56506f; }
            QFrame#section[dictLocked="true"] QLabel { color: #676b7b; }
            QFrame#section[dictLocked="true"] QLabel#lockHint { color: #c8c2e8; }
            QFrame#section[dictLocked="true"] QComboBox,
            QFrame#section[dictLocked="true"] QPushButton { background: #171923; border-color: #292c38; color: #666b7b; }
            QFrame#section[dictLocked="true"] QSlider::groove:horizontal { background: #252833; }
            QFrame#section[dictLocked="true"] QSlider::sub-page:horizontal { background: #454158; }
            QFrame#section[dictLocked="true"] QSlider::handle:horizontal {
                background: #555263; border-color: #777386;
            }
            QLabel#title { font-size: 15pt; font-weight: 600; color: #f7f7fc; }
            QLabel#sectionTitle { font-size: 10pt; font-weight: 600; color: #e7e8f1; }
            QLabel#sectionIndex { color: #9188ff; font-size: 8pt; font-weight: 600; }
            QLabel#fieldLabel { color: #8f94a7; font-size: 8pt; }
            QLabel#hint { color: #858a9d; font-size: 8pt; }
            QLabel#lockHint { color: #c8c2e8; background: #29263a; border: 1px solid #57506f;
                              border-radius: 7px; padding: 6px 9px; font-size: 8pt; }
            QComboBox, QSlider, QLineEdit { color: #d2d4df; }
            QComboBox, QLineEdit { background: #252936; border: 1px solid #363b4c; border-radius: 8px;
                        padding: 5px 9px; min-height: 22px; }
            QComboBox:hover { border-color: #615bd1; background: #292d3b; }
            QComboBox::drop-down { border: 0; width: 22px; }
            QComboBox QAbstractItemView { background: #252936; color: #e8e9f1;
                                         border: 1px solid #3b4051; border-radius: 8px;
                                         padding: 4px; outline: 0; font-size: 9pt;
                                         selection-background-color: #7069f7; }
            QSlider::groove:horizontal { height: 5px; background: #303443; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #766cf5; border-radius: 2px; }
            QSlider::handle:horizontal { width: 16px; margin: -6px 0; background: #a198ff;
                                        border: 2px solid #d7d3ff; border-radius: 8px; }
            QPushButton { background: #252936; border: 1px solid #363b4c; color: #d5d7e2;
                          border-radius: 9px; padding: 7px 11px; }
            QPushButton:hover { background: #2c3040; border-color: #615bd1; color: white; }
            QPushButton#generateButton {
                background: #252936; border-color: #363b4c; color: #d5d7e2;
                font-weight: 600;
            }
            QPushButton#generateButton[generateState="off"]:disabled,
            QPushButton#generateButton[generateState="pending"]:disabled,
            QPushButton#generateButton[generateState="loading"]:disabled,
            QPushButton#generateButton[generateState="ready"]:disabled,
            QPushButton#generateButton[generateState="error"]:disabled {
                background: #252936; border-color: #363b4c; color: #858a9d;
                font-weight: 600;
            }
            QPushButton#generateButton[generateState="missing"] {
                background: #252936; border-color: #363b4c; color: #e9eaf3;
                font-weight: 600;
            }
            QPushButton#generateButton[generateState="missing"]:hover {
                background: #2c3040; border-color: #615bd1; color: white;
                font-weight: 600;
            }
            QPushButton#outputToggle { background: #202431; border: 1px solid #393e50; color: #9ca1b4;
                                       border-radius: 11px; padding: 9px 12px; text-align: left;
                                       font-weight: 600; }
            QPushButton#outputToggle:hover { background: #282c3a; border-color: #5c587a; color: #d9dbea; }
            QPushButton#outputToggle:checked { background: #343250; border-color: #7770b8; color: #e7e4ff; }
            QFrame#statusBar { background: transparent; border: 0; border-top: 1px solid #292d3b; }
            QLabel#statusText { color: #9da1b3; font-size: 8pt; padding: 2px 5px; }
            QStackedWidget { background: transparent; }
            QScrollArea { background: transparent; border: 0; }
            QScrollBar:vertical { background: rgba(112,105,166,24); width: 8px; margin: 3px 0;
                                  border-radius: 4px; }
            QScrollBar::handle:vertical { background: #746f9f; border-radius: 4px; min-height: 42px; }
            QScrollBar::handle:vertical:hover { background: #8983b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        panel = QtWidgets.QFrame()
        panel.setObjectName("panel")
        outer.addWidget(panel)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(20, 17, 16, 16)
        layout.setSpacing(10)

        header = QtWidgets.QHBoxLayout()
        self.title_label = QtWidgets.QLabel(I18n.get("ui_settings_title"))
        self.title_label.setObjectName("title")
        header.addWidget(self.title_label)
        header.addStretch()
        close = QtWidgets.QPushButton("×")
        close.setFixedSize(30, 30)
        close.clicked.connect(self.hide_animated)
        header.addWidget(close)
        layout.addLayout(header)

        self.header_hint = QtWidgets.QLabel(I18n.get("ui_settings_hint"))
        self.header_hint.setObjectName("hint")
        layout.addWidget(self.header_hint)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QtWidgets.QWidget()
        content.setStyleSheet("background: transparent;")
        sections = QtWidgets.QVBoxLayout(content)
        sections.setContentsMargins(0, 3, 4, 2)
        sections.setSpacing(10)
        sections.addWidget(self.build_basic_section())
        sections.addWidget(self.build_ocr_section())
        sections.addWidget(self.build_region_section())
        sections.addWidget(self.build_match_section())
        sections.addWidget(self.build_output_section())
        self.scroll_area.setWidget(content)
        layout.addWidget(self.scroll_area, 1)
        status_bar = QtWidgets.QFrame()
        status_bar.setObjectName("statusBar")
        status_layout = QtWidgets.QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 8, 8, 1)
        status_layout.setSpacing(0)
        self.status_label = QtWidgets.QLabel(I18n.get("ui_status_connected"))
        self.status_label.setObjectName("statusText")
        self.status_label.setWordWrap(False)
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label, 1)
        layout.addWidget(status_bar)
        self.animations = QParallelAnimationGroup(self)
        self.connect_controls()
        self.install_group_drag_filters()

    def section(self, index, title_key):
        frame = QtWidgets.QFrame()
        frame.setObjectName("section")
        section_layout = QtWidgets.QVBoxLayout(frame)
        section_layout.setContentsMargins(15, 12, 15, 13)
        section_layout.setSpacing(9)
        heading = QtWidgets.QHBoxLayout()
        heading.setSpacing(8)
        index_label = QtWidgets.QLabel(index)
        index_label.setObjectName("sectionIndex")
        index_label.setFixedWidth(14)
        label = QtWidgets.QLabel(I18n.get(title_key))
        label.setProperty("i18nKey", title_key)
        label.setObjectName("sectionTitle")
        heading.addWidget(index_label)
        heading.addWidget(label)
        heading.addStretch()
        section_layout.addLayout(heading)
        return frame, section_layout

    def combo_box(self, items):
        combo = QtWidgets.QComboBox()
        combo.view().setStyleSheet("background: #252936;")
        combo.addItems(items)
        font = QFont("Microsoft YaHei UI", 9)
        combo.setFont(font)
        combo.view().setFont(font)
        return combo

    def field(self, title_key, control):
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        label = QtWidgets.QLabel(I18n.get(title_key))
        label.setProperty("i18nKey", title_key)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(control)
        return wrapper

    def choice_slider(self, choice_keys, value=0):
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        labels = QtWidgets.QHBoxLayout()
        labels.setSpacing(0)
        for key in choice_keys:
            label = QtWidgets.QLabel(I18n.get(key))
            label.setProperty("i18nKey", key)
            label.setObjectName("hint")
            label.setAlignment(Qt.AlignCenter)
            labels.addWidget(label, 1)
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setRange(0, len(choice_keys) - 1)
        slider.setValue(value)
        slider.setTickInterval(1)
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        layout.addLayout(labels)
        layout.addWidget(slider)
        return wrapper, slider

    def labeled_slider(self, title_key, minimum, maximum, value, formatter):
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        row = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(I18n.get(title_key))
        title_label.setProperty("i18nKey", title_key)
        row.addWidget(title_label)
        row.addStretch()
        value_label = QtWidgets.QLabel()
        value_label.setObjectName("hint")
        row.addWidget(value_label)
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        slider.valueChanged.connect(lambda v: value_label.setText(formatter(v)))
        slider._value_label = value_label
        slider._value_formatter = formatter
        value_label.setText(formatter(value))
        layout.addLayout(row)
        layout.addWidget(slider)
        return wrapper, slider

    def build_basic_section(self):
        frame, layout = self.section("A", "ui_section_basic")
        language_row = QtWidgets.QHBoxLayout()
        language_label = QtWidgets.QLabel(I18n.get("ui_interface_language"))
        language_label.setProperty("i18nKey", "ui_interface_language")
        self.interface_language = self.combo_box([])
        self.interface_language.addItem("简体中文", "zh_CN")
        self.interface_language.addItem("English", "en_US")
        self.interface_language.setCurrentIndex(
            self.interface_language.findData(Config.DEFAULTS["interface_language"])
        )
        language_row.addWidget(language_label)
        language_row.addStretch()
        language_row.addWidget(self.interface_language)
        layout.addLayout(language_row)
        font_min, font_max = Config.UI_RANGES["subtitle_font_size"]
        font_size, self.subtitle_font_size = self.labeled_slider(
            "ui_subtitle_font_size",
            font_min,
            font_max,
            Config.DEFAULTS["subtitle_font_size"],
            lambda value: I18n.get("unit_pt", value),
        )
        layout.addWidget(font_size)
        return frame

    def build_ocr_section(self):
        frame, layout = self.section("B", "ui_section_ocr")
        run_mode_widget, self.run_mode = self.choice_slider(
            ("ui_manual", "ui_auto", "ui_detect"), Config.DEFAULTS["ocr_mode"]
        )
        layout.addWidget(run_mode_widget)
        self.run_params = QtWidgets.QStackedWidget()
        manual = QtWidgets.QLabel(I18n.get("ui_manual_no_params"))
        manual.setProperty("i18nKey", "ui_manual_no_params")
        manual.setObjectName("hint")
        manual.setAlignment(Qt.AlignCenter)
        auto_min, auto_max = Config.UI_RANGES["auto_frequency_per_4s"]
        auto_page, self.auto_frequency = self.labeled_slider(
            "ui_auto_frequency",
            auto_min,
            auto_max,
            Config.interval_to_auto_frequency(Config.OCR["DEFAULT_INTERVAL"]),
            lambda value: I18n.get("unit_per_4s", value),
        )
        detect_page = QtWidgets.QWidget()
        detect_layout = QtWidgets.QVBoxLayout(detect_page)
        detect_layout.setContentsMargins(0, 0, 0, 0)
        detect_min, detect_max = Config.UI_RANGES["detect_frequency"]
        sensitivity_min, sensitivity_max = Config.UI_RANGES["detect_sensitivity"]
        frequency, self.detect_frequency = self.labeled_slider(
            "ui_detect_frequency",
            detect_min,
            detect_max,
            Config.DEFAULTS["detect_frequency"],
            lambda value: I18n.get("unit_per_s", value),
        )
        sensitivity, self.detect_sensitivity = self.labeled_slider(
            "ui_detect_sensitivity",
            sensitivity_min,
            sensitivity_max,
            Config.DEFAULTS["detect_sensitivity"],
            lambda value: I18n.get("unit_percent", value),
        )
        detect_layout.addWidget(frequency)
        detect_layout.addWidget(sensitivity)
        self.run_params.addWidget(manual)
        self.run_params.addWidget(auto_page)
        self.run_params.addWidget(detect_page)
        self.run_params.setCurrentIndex(Config.DEFAULTS["ocr_mode"])
        self.run_mode.valueChanged.connect(self.run_params.setCurrentIndex)
        layout.addWidget(self.run_params)
        return frame

    def build_region_section(self):
        frame, layout = self.section("C", "ui_section_region")
        hint = QtWidgets.QLabel(I18n.get("ui_region_hint"))
        hint.setProperty("i18nKey", "ui_region_hint")
        hint.setObjectName("hint")
        layout.addWidget(hint)
        self.region_button = QtWidgets.QPushButton(I18n.get("ui_show_region"))
        self.region_button.setProperty("i18nKey", "ui_show_region")
        layout.addWidget(self.region_button)
        return frame

    def build_game_language_row(self):
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        self.game_combo = self.combo_box([])
        for game_key in Config.GAMES:
            self.game_combo.addItem(I18n.game_name(game_key), game_key)
        self.game_combo.setCurrentIndex(self.game_combo.findData(Config.DEFAULTS["game"]))
        self.source_lang = self.combo_box([])
        self.target_lang = self.combo_box([])
        for code in Config.LANG_MAP:
            self.source_lang.addItem(I18n.language_name(code), code)
            self.target_lang.addItem(I18n.language_name(code), code)
        self.source_lang.setCurrentIndex(self.source_lang.findData(Config.DEFAULTS["source_lang"]))
        self.target_lang.setCurrentIndex(self.target_lang.findData(Config.DEFAULTS["target_lang"]))
        self._source_lang_code = self.source_lang.currentData()
        self._target_lang_code = self.target_lang.currentData()
        row.addWidget(self.field("ui_game", self.game_combo), 9)
        row.addWidget(self.field("ui_source_language", self.source_lang), 10)
        arrow = QtWidgets.QLabel("→")
        arrow.setObjectName("hint")
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setFixedWidth(14)
        row.addWidget(arrow, 0, Qt.AlignBottom)
        row.addWidget(self.field("ui_target_language", self.target_lang), 10)
        return row

    def build_match_section(self):
        frame, layout = self.section("D", "ui_section_match")
        self.match_section = frame
        self.match_lock_hint = QtWidgets.QLabel(I18n.get("ui_match_locked"))
        self.match_lock_hint.setProperty("i18nKey", "ui_match_locked")
        self.match_lock_hint.setObjectName("lockHint")
        self.match_lock_hint.setAlignment(Qt.AlignCenter)
        self.match_lock_hint.setVisible(False)
        layout.addWidget(self.match_lock_hint)
        mode_widget, self.match_mode = self.choice_slider(
            ("ui_match_off", "ui_match_exact", "ui_match_prefix"),
            Config.DEFAULTS["match_mode"],
        )
        layout.addWidget(mode_widget)
        threshold_min, threshold_max = Config.UI_RANGES["similarity_threshold"]
        threshold, self.threshold = self.labeled_slider(
            "ui_similarity_threshold",
            threshold_min,
            threshold_max,
            Config.DEFAULTS["similarity_threshold"],
            lambda value: I18n.get("unit_percent", value),
        )
        layout.addWidget(threshold)
        layout.addLayout(self.build_game_language_row())
        profile_row = QtWidgets.QHBoxLayout()
        profile_row.setSpacing(8)
        self.player_nickname = QtWidgets.QLineEdit(Config.DEFAULTS["player_nickname"])
        self.player_nickname.setMaxLength(64)
        self.protagonist_gender = self.combo_box([])
        self.protagonist_gender.addItem(I18n.get("ui_gender_female"), "female")
        self.protagonist_gender.addItem(I18n.get("ui_gender_male"), "male")
        self.protagonist_gender.setCurrentIndex(
            self.protagonist_gender.findData(Config.DEFAULTS["protagonist_gender"])
        )
        profile_row.addWidget(self.field("ui_protagonist_gender", self.protagonist_gender), 1)
        profile_row.addWidget(self.field("ui_player_nickname", self.player_nickname), 2)
        layout.addLayout(profile_row)
        self.generate_button = QtWidgets.QPushButton(I18n.get("ui_generate_match_data"))
        self.generate_button.setProperty("i18nKey", "ui_generate_match_data")
        self.generate_button.setObjectName("generateButton")
        layout.addWidget(self.generate_button)
        return frame

    def build_output_section(self):
        frame, layout = self.section("E", "ui_section_output")
        hint = QtWidgets.QLabel(I18n.get("ui_output_hint"))
        hint.setProperty("i18nKey", "ui_output_hint")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(10)
        self.auto_copy = self.output_toggle("ui_auto_copy", Config.DEFAULTS["auto_copy"])
        self.auto_save = self.output_toggle("ui_auto_save", Config.DEFAULTS["auto_save"])
        row.addWidget(self.auto_copy, 1)
        row.addWidget(self.auto_save, 1)
        layout.addLayout(row)
        return frame

    def output_toggle(self, title_key, checked):
        button = QtWidgets.QPushButton()
        button.setObjectName("outputToggle")
        button.setCheckable(True)
        button.setChecked(checked)
        button.setMinimumHeight(48)
        button.setProperty("titleKey", title_key)
        button.toggled.connect(lambda enabled, target=button: self.update_output_toggle(target, enabled))
        self.update_output_toggle(button, checked)
        return button

    def update_output_toggle(self, button, enabled):
        state = I18n.get("ui_enabled" if enabled else "ui_disabled")
        marker = "●" if enabled else "○"
        title = I18n.get(button.property("titleKey"))
        button.setText(f"{marker}  {title}\n     {state}")

    def connect_controls(self):
        self.run_mode.valueChanged.connect(self.runModeChanged)
        self.auto_frequency.valueChanged.connect(
            lambda value: self.autoIntervalChanged.emit(Config.auto_frequency_to_interval(value))
        )
        self.detect_frequency.valueChanged.connect(self.detectFrequencyChanged)
        self.detect_sensitivity.valueChanged.connect(self.detectSensitivityChanged)
        self.game_combo.currentIndexChanged.connect(
            lambda: self.gameChanged.emit(self.game_combo.currentData())
        )
        self.source_lang.currentIndexChanged.connect(self.emit_languages)
        self.target_lang.currentIndexChanged.connect(self.emit_languages)
        self.match_mode.valueChanged.connect(self.matchModeChanged)
        self.threshold.valueChanged.connect(self.thresholdChanged)
        self.player_nickname.editingFinished.connect(self.emit_personalization)
        self.protagonist_gender.currentIndexChanged.connect(self.emit_personalization)
        self.auto_copy.toggled.connect(self.autoCopyChanged)
        self.auto_save.toggled.connect(self.autoSaveChanged)
        self.subtitle_font_size.valueChanged.connect(self.subtitleFontSizeChanged)
        self.interface_language.currentIndexChanged.connect(
            lambda: self.interfaceLanguageChanged.emit(self.interface_language.currentData())
        )
        self.region_button.clicked.connect(self.showRegionRequested)
        self.generate_button.clicked.connect(self.smartFixRequested)
        self.install_wheel_redirects()

    def emit_personalization(self):
        self.personalizationChanged.emit(
            self.player_nickname.text().strip(),
            self.protagonist_gender.currentData() or "female",
        )

    def install_wheel_redirects(self):
        controls = self.findChildren(QtWidgets.QSlider) + self.findChildren(QtWidgets.QComboBox)
        for control in controls:
            control.installEventFilter(self)

    def install_group_drag_filters(self):
        self.installEventFilter(self)
        for widget in self.findChildren(QtWidgets.QWidget):
            widget.installEventFilter(self)

    def is_group_drag_surface(self, widget):
        blocked_types = (
            QtWidgets.QAbstractButton,
            QtWidgets.QAbstractSlider,
            QtWidgets.QComboBox,
            QtWidgets.QLineEdit,
            QtWidgets.QScrollBar,
            QtWidgets.QAbstractItemView,
        )
        current = widget
        while current is not None and current is not self:
            if isinstance(current, blocked_types):
                return False
            current = current.parentWidget()
        return True

    def start_group_drag(self, global_position):
        if self.follow_ball_ref is None or not self.isVisible():
            return
        self.animations.stop()
        self._group_drag_origin = global_position.toPoint()
        self._group_drag_ball_anchor = self.follow_ball_ref.ball_anchor_global()
        self._group_dragging = False

    def move_group_drag(self, global_position):
        if self._group_drag_origin is None or self.follow_ball_ref is None:
            return False
        cursor = global_position.toPoint()
        if not self._group_dragging:
            self._group_dragging = (
                cursor - self._group_drag_origin
            ).manhattanLength() >= QApplication.startDragDistance()
        if self._group_dragging:
            target = self.fit_anchor(self._group_drag_ball_anchor + cursor - self._group_drag_origin)
            self.follow_ball_ref.set_ball_anchor_global(target)
            self.user_moved_ball = True
        return self._group_dragging

    def finish_group_drag(self):
        was_dragging = self._group_dragging
        self._group_drag_origin = None
        self._group_drag_ball_anchor = None
        self._group_dragging = False
        return was_dragging

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Wheel and isinstance(
            watched, (QtWidgets.QSlider, QtWidgets.QComboBox)
        ):
            scrollbar = self.scroll_area.verticalScrollBar()
            delta = event.angleDelta().y()
            step = max(scrollbar.singleStep() * 3, 36)
            scrollbar.setValue(scrollbar.value() - (step if delta > 0 else -step))
            event.accept()
            return True
        if self.is_group_drag_surface(watched):
            if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.start_group_drag(event.globalPosition())
            elif event.type() == QtCore.QEvent.MouseMove and event.buttons() & Qt.LeftButton:
                if self.move_group_drag(event.globalPosition()):
                    event.accept()
                    return True
            elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                if self.finish_group_drag():
                    event.accept()
                    return True
        return super().eventFilter(watched, event)

    def emit_languages(self):
        source = self.source_lang.currentData() or self.source_lang.currentText()
        target = self.target_lang.currentData() or self.target_lang.currentText()
        if source == target:
            source_blocker = QtCore.QSignalBlocker(self.source_lang)
            target_blocker = QtCore.QSignalBlocker(self.target_lang)
            sender = self.sender()
            if sender == self.source_lang:
                fallback_target = self._source_lang_code
                target_index = self.target_lang.findData(fallback_target)
                if target_index >= 0:
                    self.target_lang.setCurrentIndex(target_index)
                    target = fallback_target
            elif sender == self.target_lang:
                fallback_source = self._target_lang_code
                source_index = self.source_lang.findData(fallback_source)
                if source_index >= 0:
                    self.source_lang.setCurrentIndex(source_index)
                    source = fallback_source
            del source_blocker, target_blocker
        self._source_lang_code = source
        self._target_lang_code = target
        self.languagesChanged.emit(
            source,
            target,
        )

    def set_status(self, text):
        self.status_label.setText(text)

    def retranslate_ui(self):
        self.title_label.setText(I18n.get("ui_settings_title"))
        self.header_hint.setText(I18n.get("ui_settings_hint"))
        self.status_label.setText(I18n.get("ui_status_connected"))
        for label in self.findChildren(QtWidgets.QLabel):
            key = label.property("i18nKey")
            if key:
                label.setText(I18n.get(key))
        for button in self.findChildren(QtWidgets.QPushButton):
            key = button.property("i18nKey")
            if key:
                button.setText(I18n.get(key))
        for slider in self.findChildren(QtWidgets.QSlider):
            if hasattr(slider, "_value_formatter"):
                slider._value_label.setText(slider._value_formatter(slider.value()))
        for index in range(self.game_combo.count()):
            game_key = self.game_combo.itemData(index)
            self.game_combo.setItemText(index, I18n.game_name(game_key))
        for combo in (self.source_lang, self.target_lang):
            for index in range(combo.count()):
                combo.setItemText(index, I18n.language_name(combo.itemData(index)))
        for index in range(self.protagonist_gender.count()):
            gender = self.protagonist_gender.itemData(index)
            self.protagonist_gender.setItemText(index, I18n.get(f"ui_gender_{gender}"))
        for index in range(self.interface_language.count()):
            language = self.interface_language.itemData(index)
            self.interface_language.setItemText(
                index,
                "简体中文" if language == "zh_CN" else "English",
            )
        self.update_output_toggle(self.auto_copy, self.auto_copy.isChecked())
        self.update_output_toggle(self.auto_save, self.auto_save.isChecked())
        self._refresh_match_interaction()

    def set_locked(self, locked):
        # Dictionary work only depends on matching configuration. Keep every
        # other settings section, the floating ball, and subtitle UI usable.
        self._dict_locked = locked
        self._refresh_match_interaction()

    def set_match_ready(self, ready):
        self.set_generate_state("ready" if ready else "off")

    def set_generate_state(self, state, text=""):
        if state not in {"off", "pending", "loading", "missing", "ready", "error"}:
            state = "loading"
        self._generate_state = state
        self._match_ready = state == "ready"
        self._generate_text = text or ""
        self._refresh_match_interaction()

    def _refresh_match_interaction(self):
        self.match_lock_hint.setVisible(self._dict_locked)
        self.match_section.setProperty("dictLocked", self._dict_locked)
        self.match_section.setEnabled(not self._dict_locked)
        state = "loading" if self._dict_locked else self._generate_state
        self.generate_button.setProperty("dictReady", state == "ready")
        self.generate_button.setProperty("generateState", state)
        self.generate_button.setEnabled(state == "missing" and not self._dict_locked)
        fallback_text = {
            "off": I18n.get("state_standby"),
            "pending": I18n.get("state_pending", 0, 0),
            "loading": I18n.get("state_loading", 0, 0),
            "missing": I18n.get("ui_match_data_missing"),
            "ready": I18n.get("state_ready", 0),
            "error": I18n.get("state_error", I18n.get("state_error_unknown")),
        }.get(state, I18n.get("ui_generate_match_data"))
        button_text = self._generate_text or fallback_text
        self.generate_button.setText(button_text)
        for widget in (self.match_section, self.generate_button):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    def show_near(self, ball):
        if self.opening:
            return
        if self.isVisible():
            self.hide_animated()
            return
        anchor = ball.ball_anchor_global()
        self.follow_ball_ref = ball
        self.original_ball_anchor = QPoint(anchor)
        self.user_moved_ball = False
        target_anchor = self.fit_anchor(anchor)
        if target_anchor != anchor:
            self.opening = True
            self.animate_ball_to(ball, anchor, target_anchor, lambda: self.open_panel(target_anchor))
        else:
            self.open_panel(target_anchor)

    def open_panel(self, anchor):
        self.opening = False
        x, y = (anchor + self.panel_offset).x(), (anchor + self.panel_offset).y()
        end = QRect(x, y, self.width(), self.height())
        start = QRect(x + 14, y + 10, self.width(), self.height())
        self.setGeometry(start)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.animate_window(start, end, 0.0, 1.0, None)

    def follow_ball(self, anchor):
        if self.isVisible() and self.follow_ball_ref is not None and not self.opening:
            self.animations.stop()
            self.move(anchor + self.panel_offset)

    def mark_user_moved(self):
        if self.isVisible():
            self.user_moved_ball = True

    def fit_anchor(self, anchor):
        area = self.follow_ball_ref.screen().availableGeometry()
        max_x = area.right() - self.panel_offset.x() - self.width() + 1
        max_y = area.bottom() - self.panel_offset.y() - self.height() + 1
        return QPoint(max(area.left(), min(anchor.x(), max_x)), max(area.top(), min(anchor.y(), max_y)))

    def animate_ball_to(self, ball, start, end, finished=None):
        ball.anchor_animation = QPropertyAnimation(ball, b"ballAnchor")
        ball.anchor_animation.setDuration(320)
        ball.anchor_animation.setStartValue(start)
        ball.anchor_animation.setEndValue(end)
        ball.anchor_animation.setEasingCurve(QEasingCurve.OutCubic)
        if finished:
            ball.anchor_animation.finished.connect(finished)
        ball.anchor_animation.start()

    def hide_animated(self):
        if not self.isVisible():
            return
        start = self.geometry()
        end = start.translated(0, 12)
        self.animate_window(start, end, self.windowOpacity(), 0.0, self.finish_hide)

    def finish_hide(self):
        self.hide()
        if (
            not self.user_moved_ball
            and self.original_ball_anchor is not None
            and self.follow_ball_ref is not None
        ):
            current = self.follow_ball_ref.ball_anchor_global()
            target = QPoint(self.original_ball_anchor)
            if current != target:
                self.animate_ball_to(self.follow_ball_ref, current, target)
        self.original_ball_anchor = None
        self.user_moved_ball = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_group_drag(event.globalPosition())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.move_group_drag(event.globalPosition()):
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.finish_group_drag():
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def animate_window(self, start, end, opacity_start, opacity_end, finished):
        self.animations.stop()
        self.animations = QParallelAnimationGroup(self)
        geometry = QPropertyAnimation(self, b"geometry")
        geometry.setDuration(240)
        geometry.setStartValue(start)
        geometry.setEndValue(end)
        geometry.setEasingCurve(QEasingCurve.OutCubic)
        opacity = QPropertyAnimation(self, b"windowOpacity")
        opacity.setDuration(200)
        opacity.setStartValue(opacity_start)
        opacity.setEndValue(opacity_end)
        self.animations.addAnimation(geometry)
        self.animations.addAnimation(opacity)
        if opacity_end == 0.0 and finished:
            self.animations.finished.connect(finished)
        self.animations.start()


class FaintOCRApplication(QtCore.QObject):
    """Coordinates the floating UI and the OCR business layer."""

    FLOATING_PRIORITY_INFO = 10
    FLOATING_PRIORITY_DETECT = 30
    FLOATING_PRIORITY_ACTION = 70
    FLOATING_PRIORITY_DOWNLOAD = 75
    FLOATING_PRIORITY_RESULT = 80
    FLOATING_PRIORITY_USER_ACTION = 90
    FLOATING_PRIORITY_ERROR = 100

    def __init__(self):
        super().__init__()
        I18n.current_lang = Config.DEFAULTS["interface_language"]
        self.controller = OCRController()
        self.ball = FloatingBall(floating=True)
        self.subtitle = SubtitleWindow(floating=True)
        self.settings = SettingsWindow()
        self.ball.settings_window = self.settings

        self.ocr_region = Config.OCR["DEFAULT_REGION"]
        self.ocr_mode = Config.DEFAULTS["ocr_mode"]
        self.auto_ocr_enabled = Config.DEFAULTS["auto_ocr_enabled"]
        self.detect_ocr_enabled = Config.DEFAULTS["detect_ocr_enabled"]
        self.auto_ocr_interval = Config.OCR["DEFAULT_INTERVAL"]
        self.detect_frequency = Config.DEFAULTS["detect_frequency"]
        self.detect_sensitivity = Config.DEFAULTS["detect_sensitivity"]
        self.auto_copy = Config.DEFAULTS["auto_copy"]
        self.auto_save = Config.DEFAULTS["auto_save"]
        self._last_matched_output_text = None
        self._manual_ocr_pending = 0
        self._cleaned_up = False
        self._floating_status_priority = 0
        self._floating_status_protected_until = 0.0
        self.selection_overlay = None
        self.region_overlay = None

        self.ocr_timer = QTimer(self)
        self.ocr_timer.timeout.connect(self.run_auto_ocr)

        self.initialize_ui_state()
        self.connect_signals()
        self.initialize_positions()
        self.controller._refresh_ui_state()

    def initialize_ui_state(self):
        settings = self.settings
        controls = (
            settings.run_mode,
            settings.auto_frequency,
            settings.detect_frequency,
            settings.detect_sensitivity,
            settings.game_combo,
            settings.source_lang,
            settings.target_lang,
            settings.match_mode,
            settings.threshold,
            settings.player_nickname,
            settings.protagonist_gender,
            settings.auto_copy,
            settings.auto_save,
            settings.subtitle_font_size,
            settings.interface_language,
        )
        blockers = [QtCore.QSignalBlocker(control) for control in controls]
        settings.run_mode.setValue(self.ocr_mode)
        settings.run_params.setCurrentIndex(self.ocr_mode)
        settings.auto_frequency.setValue(Config.interval_to_auto_frequency(self.auto_ocr_interval))
        settings.detect_frequency.setValue(self.detect_frequency)
        settings.detect_sensitivity.setValue(self.detect_sensitivity)
        settings.game_combo.setCurrentIndex(settings.game_combo.findData(self.controller.current_game))
        settings.source_lang.setCurrentIndex(settings.source_lang.findData(self.controller.source_lang))
        settings.target_lang.setCurrentIndex(settings.target_lang.findData(self.controller.target_lang))
        settings._source_lang_code = settings.source_lang.currentData()
        settings._target_lang_code = settings.target_lang.currentData()
        settings.match_mode.setValue(self.controller.match_mode)
        settings.threshold.setValue(self.controller.similarity_threshold)
        settings.player_nickname.setText(self.controller.player_nickname)
        settings.protagonist_gender.setCurrentIndex(
            settings.protagonist_gender.findData(self.controller.protagonist_gender)
        )
        settings.subtitle_font_size.setValue(Config.DEFAULTS["subtitle_font_size"])
        settings.interface_language.setCurrentIndex(
            settings.interface_language.findData(I18n.current_lang)
        )
        del blockers
        self.update_subtitle_context()
        self.subtitle.update_match_mode(self.controller.match_mode)
        self.ball.ocr_momentary = self.ocr_mode == 0
        self.sync_ball_state()

    def connect_signals(self):
        self.ball.ocrChanged.connect(self.set_ocr_enabled)
        self.ball.regionRequested.connect(self.start_region_selection)
        self.ball.settingsRequested.connect(lambda: self.settings.show_near(self.ball))
        self.ball.subtitleRequested.connect(self.toggle_subtitle)
        self.ball.ballMoved.connect(self.settings.follow_ball)
        self.ball.userDragged.connect(self.settings.mark_user_moved)

        self.settings.showRegionRequested.connect(self.show_region_overlay)
        self.settings.smartFixRequested.connect(self.controller.run_smart_fix)
        self.settings.runModeChanged.connect(self.set_ocr_mode)
        self.settings.autoIntervalChanged.connect(self.set_auto_interval)
        self.settings.detectFrequencyChanged.connect(self.set_detect_frequency)
        self.settings.detectSensitivityChanged.connect(self.set_detect_sensitivity)
        self.settings.gameChanged.connect(self.set_game)
        self.settings.languagesChanged.connect(self.set_languages)
        self.settings.matchModeChanged.connect(self.set_match_mode)
        self.settings.thresholdChanged.connect(self.set_threshold)
        self.settings.personalizationChanged.connect(self.set_personalization)
        self.settings.autoCopyChanged.connect(self.set_auto_copy)
        self.settings.autoSaveChanged.connect(self.set_auto_save)
        self.settings.subtitleFontSizeChanged.connect(self.set_subtitle_font_size)
        self.settings.interfaceLanguageChanged.connect(self.set_interface_language)

        self.controller.ocr_result_signal.connect(self.handle_ocr_result)
        self.controller.ocr_status_signal.connect(self.handle_ocr_status)
        self.controller.manual_ocr_dropped_signal.connect(self.finish_manual_ocr_request)
        self.controller.detect_status_signal.connect(self.handle_detect_status)
        self.controller.detect_failed_signal.connect(self.handle_detect_failed)
        self.controller.debug_event_signal.connect(self.append_debug)
        self.controller.dict_progress_signal.connect(self.handle_dict_progress)
        self.controller.dict_percent_signal.connect(self.handle_dict_percent)
        self.controller.dict_download_detail_signal.connect(self.handle_dict_download_detail)
        self.controller.ui_state_signal.connect(self.handle_dict_state)
        self.controller.ui_lock_signal.connect(self.settings.set_locked)

        QApplication.instance().aboutToQuit.connect(self.cleanup)

    def initialize_positions(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.ball.menu_direction = "left"
        self.ball.set_ball_anchor_global(QPoint(screen.right() - 75, screen.center().y() - 170))
        self.subtitle.move(
            screen.center().x() - self.subtitle.width() // 2,
            screen.bottom() - self.subtitle.height() - 70,
        )

    def show(self):
        self.ball.show()
        self.subtitle.show()
        for widget, label in (
                (self.ball, "FloatingBall"),
                (self.subtitle, "Subtitle"),
                (self.settings, "Settings"),
        ):
            message = apply_capture_exclusion(widget, label)
            if message:
                self.append_debug(I18n.get("debug_error", message))

    def toggle_subtitle(self):
        self.subtitle.setVisible(not self.subtitle.isVisible())

    def set_ocr_enabled(self, enabled):
        if self.ocr_mode == 0:
            if self.controller.request_ocr(self.ocr_region, task_source="manual"):
                self._manual_ocr_pending += 1
                self.sync_ball_state(True)
                self.show_floating_status(
                    I18n.get("status_ocr_submit"),
                    self.FLOATING_PRIORITY_ACTION,
                    1200,
                )
            else:
                self.sync_ball_state(self._manual_ocr_pending > 0)
        elif self.ocr_mode == 1:
            self.set_auto_ocr_enabled(enabled)
        else:
            self.set_detect_ocr_enabled(enabled)

    def set_ocr_mode(self, mode):
        if mode == self.ocr_mode:
            return
        self.stop_active_mode()
        self.ocr_mode = mode
        self.ball.ocr_momentary = mode == 0
        self.settings.run_params.setCurrentIndex(mode)
        mode_name = I18n.get(("ui_manual", "ui_auto", "ui_detect")[mode])
        self.show_settings_status(I18n.get("ui_mode_status", mode_name))
        self.sync_ball_state(False)

    def stop_active_mode(self):
        self.ocr_timer.stop()
        self._manual_ocr_pending = 0
        if self.detect_ocr_enabled or self.controller.detect_enabled:
            self.controller.stop_detection()
        self.auto_ocr_enabled = False
        self.detect_ocr_enabled = False

    def set_auto_ocr_enabled(self, enabled):
        self.auto_ocr_enabled = enabled
        if enabled:
            self.run_auto_ocr()
            self.ocr_timer.start(max(1, round(self.auto_ocr_interval * 1000)))
            self.route_message(
                I18n.get("status_auto_ocr_on", Config.interval_to_auto_frequency(self.auto_ocr_interval)),
                settings=True,
                floating=True,
                floating_priority=self.FLOATING_PRIORITY_ACTION,
                floating_hold_ms=1800,
            )
        else:
            self.ocr_timer.stop()
            self.route_message(
                I18n.get("status_auto_ocr_off"),
                settings=True,
                floating=True,
                floating_priority=self.FLOATING_PRIORITY_ACTION,
                floating_hold_ms=1800,
            )
        self.sync_ball_state(enabled)

    def run_auto_ocr(self):
        self.controller.request_ocr(self.ocr_region, task_source="auto")

    def set_detect_ocr_enabled(self, enabled):
        self.detect_ocr_enabled = enabled
        if enabled:
            self.controller.start_detection(
                self.ocr_region, self.detect_frequency, self.detect_sensitivity
            )
        else:
            self.controller.stop_detection()
        self.route_message(
            I18n.get("status_detect_ocr_on" if enabled else "status_detect_ocr_off"),
            settings=True,
            floating=True,
            floating_priority=self.FLOATING_PRIORITY_ACTION,
            floating_hold_ms=1800,
        )
        self.sync_ball_state(enabled)

    def sync_ball_state(self, active=None):
        if active is None:
            if self.ocr_mode == 1:
                active = self.auto_ocr_enabled
            elif self.ocr_mode == 2:
                active = self.detect_ocr_enabled
            else:
                active = self.ball.ocr_enabled
        self.ball.ocr_enabled = bool(active)
        self.ball.update()
        self.subtitle.update_ocr_state(active, self.ocr_mode)

    def set_auto_interval(self, seconds):
        self.auto_ocr_interval = seconds
        if self.auto_ocr_enabled:
            self.ocr_timer.setInterval(max(1, round(seconds * 1000)))
        self.show_settings_status(I18n.get("status_interval", Config.interval_to_auto_frequency(seconds)))

    def set_detect_frequency(self, frequency):
        self.detect_frequency = frequency
        self.update_detection()
        self.show_settings_status(I18n.get("status_detect_frequency_changed", frequency))

    def set_detect_sensitivity(self, sensitivity):
        self.detect_sensitivity = sensitivity
        self.update_detection()
        self.show_settings_status(I18n.get("status_detect_sensitivity_changed", sensitivity))

    def update_detection(self):
        self.controller.update_detection(
            self.ocr_region, self.detect_frequency, self.detect_sensitivity
        )

    def set_game(self, game):
        self.controller.set_game(game)
        self.sync_personalization_controls()
        self.update_detection()
        self.update_subtitle_context()
        self.show_settings_status(I18n.get("status_game_changed", I18n.game_name(game)))

    def set_languages(self, source, target):
        self._last_matched_output_text = None
        self.controller.set_languages(source, target)
        self.sync_personalization_controls()
        self.update_subtitle_context()
        self.show_settings_status(
            I18n.get("status_languages_changed", I18n.language_name(source), I18n.language_name(target))
        )

    def set_match_mode(self, mode):
        self._last_matched_output_text = None
        self.controller.set_match_mode(mode)
        self.subtitle.update_match_mode(mode)
        match_name = I18n.get(("ui_match_off", "ui_match_exact", "ui_match_prefix")[mode])
        self.show_settings_status(I18n.get("status_match_mode_changed", match_name))

    def set_threshold(self, threshold):
        self.controller.set_threshold(threshold)
        self.show_settings_status(I18n.get("status_threshold_changed", threshold))

    def set_personalization(self, nickname, gender):
        nickname = str(nickname or "").strip()
        gender = "male" if gender == "male" else "female"
        nickname_changed = nickname != self.controller.player_nickname
        gender_changed = gender != self.controller.protagonist_gender
        self._last_matched_output_text = None
        self.controller.set_personalization(nickname, gender)
        messages = []
        if nickname_changed:
            messages.append(I18n.get("status_nickname_changed", nickname))
        if gender_changed:
            gender_name = I18n.get(f"ui_gender_{self.controller.protagonist_gender}")
            messages.append(I18n.get("status_gender_changed", gender_name))
        if messages:
            self.show_settings_status(" | ".join(messages))

    def sync_personalization_controls(self):
        nickname_blocker = QtCore.QSignalBlocker(self.settings.player_nickname)
        gender_blocker = QtCore.QSignalBlocker(self.settings.protagonist_gender)
        self.settings.player_nickname.setText(self.controller.player_nickname)
        self.settings.protagonist_gender.setCurrentIndex(
            self.settings.protagonist_gender.findData(self.controller.protagonist_gender)
        )
        del nickname_blocker, gender_blocker

    def set_subtitle_font_size(self, size):
        self.subtitle.set_subtitle_font_size(size)
        self.show_settings_status(I18n.get("status_subtitle_size_changed", size))

    def set_auto_copy(self, enabled):
        self.auto_copy = enabled
        self.show_settings_status(I18n.get("ui_auto_copy") + ": " + I18n.get("ui_enabled" if enabled else "ui_disabled"))

    def set_auto_save(self, enabled):
        self.auto_save = enabled
        self.show_settings_status(I18n.get("ui_auto_save") + ": " + I18n.get("ui_enabled" if enabled else "ui_disabled"))

    def set_interface_language(self, language):
        if language not in I18n.TEXT or language == I18n.current_lang:
            return
        I18n.current_lang = language
        QApplication.instance().setApplicationName(I18n.get("app_title"))
        self.ball.setWindowTitle(I18n.get("app_title"))
        self.settings.retranslate_ui()
        self.subtitle.retranslate_ui(self.ocr_mode, self.controller.match_mode)
        self.update_subtitle_context()
        self.show_settings_status(I18n.get("ui_status_connected"))
        logger.info(I18n.get("log_language_changed", language))

    def update_subtitle_context(self):
        source = I18n.language_name(self.controller.source_lang)
        target = I18n.language_name(self.controller.target_lang)
        self.subtitle.update_context(I18n.game_name(self.controller.current_game), source, target)

    def start_region_selection(self):
        self.show_floating_status(
            I18n.get("status_sel_region"),
            self.FLOATING_PRIORITY_USER_ACTION,
            5000,
            force=True,
        )
        self.selection_overlay = SelectionOverlay()
        self.selection_overlay.selection_completed.connect(self.handle_region_selected)
        self.selection_overlay.show()

    def handle_region_selected(self, rect):
        self.ocr_region = (rect.x(), rect.y(), rect.width(), rect.height())
        self.update_detection()
        message = I18n.get("status_region_ok", rect.x(), rect.y(), rect.width(), rect.height())
        self.show_settings_status(message)
        self.show_floating_status(message, self.FLOATING_PRIORITY_USER_ACTION, 2200, force=True)
        self.show_region_overlay()

    def show_region_overlay(self):
        self.region_overlay = RegionOverlay(self.ocr_region)
        self.region_overlay.show()

    def _task_source_name(self, task_source):
        return I18n.get({
            "manual": "ui_manual",
            "auto": "ui_auto",
            "detect": "ui_detect",
        }.get(task_source, task_source))

    def _build_ocr_summary(self, task_source, status_info):
        # Only parse the current-run line and require a real field boundary.
        # Otherwise "OCR:" also matches the tail of "检测→触发OCR:".
        current_line = (status_info or "").splitlines()[0]
        fields = [field.strip() for field in current_line.split("|")]

        def field_seconds(*labels):
            for field in fields:
                field_name, separator, value = field.partition(":")
                if separator and field_name.strip() in labels:
                    try:
                        return float(value.strip().removesuffix("s"))
                    except ValueError:
                        return 0.0
            return 0.0

        similarity_match = re.search(r"(?:相似度|Similarity):\s*([^|%\n]+)%", status_info or "")
        capture_seconds = field_seconds("截图", "Capture")
        ocr_seconds = field_seconds("OCR")
        match_seconds = field_seconds("匹配", "Match")
        total_seconds = field_seconds("总计", "Total")
        match_text = (
            I18n.get("status_match_triggered", similarity_match.group(1).strip())
            if similarity_match else I18n.get("status_match_not_triggered")
        )
        return I18n.get(
            "status_ocr_summary",
            self._task_source_name(task_source),
            capture_seconds,
            ocr_seconds,
            match_seconds,
            total_seconds,
            match_text,
        )

    def finish_manual_ocr_request(self):
        self._manual_ocr_pending = max(0, self._manual_ocr_pending - 1)
        if self.ocr_mode == 0:
            self.sync_ball_state(self._manual_ocr_pending > 0)

    def handle_ocr_result(self, is_success, main_text, status_info, allow_auto_output, task_source):
        source_name = self._task_source_name(task_source)
        if not is_success:
            self.route_message(
                main_text,
                settings=True,
                floating=True,
                debug=True,
                floating_priority=self.FLOATING_PRIORITY_ERROR,
                floating_hold_ms=5000,
                debug_prefix=I18n.get("debug_error", ""),
            )
        elif not main_text:
            self.subtitle.update_text("...")
            if status_info:
                self.append_debug(I18n.get("debug_ocr_detail", source_name, status_info))
            self.show_floating_status(
                self._build_ocr_summary(task_source, status_info),
                self.FLOATING_PRIORITY_RESULT,
                1800 if task_source == "manual" else 1000,
            )
        else:
            self.subtitle.update_text(main_text)
            debug_text = " / ".join(str(main_text).splitlines())
            self.append_debug(I18n.get("debug_ocr_result", source_name, debug_text))
            if status_info:
                self.append_debug(I18n.get("debug_ocr_detail", source_name, status_info))

            self.show_floating_status(
                self._build_ocr_summary(task_source, status_info),
                self.FLOATING_PRIORITY_RESULT,
                1800 if task_source == "manual" else 1000,
            )
            self.process_output(main_text, allow_auto_output)
        if task_source == "manual":
            self.finish_manual_ocr_request()

    def process_output(self, text, allow_auto_output):
        is_matched = allow_auto_output and self.controller.match_mode != 0
        is_duplicate = is_matched and text == self._last_matched_output_text
        if not allow_auto_output or is_duplicate:
            return
        if self.auto_copy:
            QApplication.clipboard().setText(text)
        if self.auto_save:
            try:
                with open(Config.OUTPUT_FILE, "a", encoding="utf-8") as output:
                    output.write(f"\n---- {time.ctime()} ----\n{text}\n")
            except Exception as exc:
                self.route_message(
                    I18n.get("ui_save_failed", exc),
                    settings=True,
                    floating=True,
                    debug=True,
                    floating_priority=self.FLOATING_PRIORITY_ERROR,
                    floating_hold_ms=5000,
                )
        if is_matched:
            self._last_matched_output_text = text

    def show_settings_status(self, message):
        if message:
            self.settings.set_status(" ".join(str(message).split()))

    def show_floating_status(self, message, priority=FLOATING_PRIORITY_INFO, hold_ms=0, force=False):
        if not message:
            return False
        now = time.monotonic()
        if (
                not force
                and now < self._floating_status_protected_until
                and priority < self._floating_status_priority
        ):
            return False
        single_line = " ".join(str(message).split())
        if len(single_line) > 160:
            single_line = single_line[:157] + "..."
        self.subtitle.update_status(single_line)
        self._floating_status_priority = priority
        self._floating_status_protected_until = now + max(hold_ms, 0) / 1000.0
        return True

    def append_debug(self, message):
        if message:
            lines = str(message).splitlines() or [""]
            now = datetime.now()
            timestamp = now.strftime("%H:%M:%S.") + f"{now.microsecond // 1000:03d}"
            formatted = [f"{timestamp} {lines[0]}"]
            formatted.extend(f"         {line}" for line in lines[1:])
            self.subtitle.append_debug("\n".join(formatted))

    def route_message(
            self,
            message,
            *,
            settings=False,
            floating=False,
            debug=False,
            floating_priority=FLOATING_PRIORITY_INFO,
            floating_hold_ms=0,
            debug_prefix=None
    ):
        if not message:
            return
        if settings:
            self.show_settings_status(message)
        if floating:
            self.show_floating_status(message, floating_priority, floating_hold_ms)
        if debug:
            debug_message = f"{debug_prefix} {message}".strip() if debug_prefix else message
            self.append_debug(debug_message)

    def handle_ocr_status(self, message):
        self.show_floating_status(
            message,
            self.FLOATING_PRIORITY_ACTION,
            1600,
        )

    def handle_detect_status(self, message):
        self.append_debug(I18n.get("debug_detect", message))

        error_prefixes = (
            I18n.get("status_detect_start_error", "").split(":")[0],
            I18n.get("status_detect_poll_error", "").split(":")[0],
            I18n.get("status_detect_review_error", "").split(":")[0],
        )
        if any(message.startswith(prefix) for prefix in error_prefixes):
            self.route_message(
                message,
                settings=True,
                floating=True,
                floating_priority=self.FLOATING_PRIORITY_ERROR,
                floating_hold_ms=5000,
            )
            return

        if message in {
            I18n.get("status_detect_started"),
            I18n.get("status_detect_stopped"),
            I18n.get("status_detect_updated"),
        }:
            self.show_floating_status(message, self.FLOATING_PRIORITY_ACTION, 1800)
            return

        if (
                message == I18n.get("status_detect_stable")
                or message.startswith(I18n.get("status_detect_change", 0, "").split("0.00")[0])
                or message.startswith(I18n.get("status_detect_submit", 0, 0, 0).split("0.00")[0])
        ):
            self.show_floating_status(message, self.FLOATING_PRIORITY_DETECT, 800)

    def handle_detect_failed(self, message):
        self.detect_ocr_enabled = False
        self.sync_ball_state(False)
        self.route_message(
            message,
            settings=True,
            floating=True,
            floating_priority=self.FLOATING_PRIORITY_ERROR,
            floating_hold_ms=5000,
        )

    def handle_dict_progress(self, message_key, args):
        message = I18n.get(message_key, *args)
        self.show_settings_status(message)
        self.show_floating_status(message, self.FLOATING_PRIORITY_DOWNLOAD, 500)
        self.append_debug(I18n.get("debug_dict", message))

    def handle_dict_percent(self, percent):
        message = I18n.get("ui_match_progress", percent)
        self.show_settings_status(message)
        self.show_floating_status(message, self.FLOATING_PRIORITY_DOWNLOAD, 300)

    def handle_dict_download_detail(self, game_key, file_name, percent, size_text, speed_text):
        message = I18n.get(
            "ui_download_progress",
            I18n.game_name(game_key),
            file_name,
            percent,
            size_text,
            speed_text
        )
        self.show_settings_status(message)
        self.show_floating_status(message, self.FLOATING_PRIORITY_DOWNLOAD, 300)

    def handle_dict_state(self, state, data_list, current_level, target_level):
        error_detail = data_list[0] if data_list else I18n.get("state_error_unknown")
        messages = {
            "STANDBY": I18n.get("state_standby"),
            "READY": I18n.get("state_ready", current_level),
            "PENDING": I18n.get("state_pending", current_level, target_level),
            "LOADING": I18n.get("state_loading", current_level, target_level),
            "MISSING": I18n.get("state_missing", data_list[0] if data_list else ""),
            "ERROR": I18n.get("state_error", error_detail),
        }
        message = messages.get(state, state)
        generate_state = {
            "STANDBY": "off",
            "READY": "ready",
            "PENDING": "pending",
            "LOADING": "loading",
            "MISSING": "missing",
            "ERROR": "error",
        }.get(state, "loading")
        self.settings.set_generate_state(generate_state, message)
        self.subtitle.update_match_data_state(generate_state)
        self.show_settings_status(message)
        priority = self.FLOATING_PRIORITY_DOWNLOAD
        hold_ms = 2200 if state == "READY" else 800
        if state == "MISSING":
            priority = self.FLOATING_PRIORITY_ACTION
            hold_ms = 2500
        elif state == "ERROR":
            priority = self.FLOATING_PRIORITY_ERROR
            hold_ms = 5000
        self.show_floating_status(message, priority, hold_ms)
        if state in {"READY", "MISSING", "ERROR"}:
            self.append_debug(I18n.get("debug_dict", message))

    def cleanup(self):
        if self._cleaned_up:
            return
        self._cleaned_up = True
        self.ocr_timer.stop()
        self.controller.cleanup()
        self.ball.timer.stop()
        self.ball.collapse_timer.stop()
        self.subtitle.timer.stop()
        self.subtitle.resize_poll_timer.stop()
        logger.info(I18n.get("log_cleanup"))


def load_system_fonts():
    for font_file in FONT_FILES:
        if Path(font_file).exists():
            QFontDatabase.addApplicationFont(font_file)


def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(I18n.get("app_title"))
    app.setWindowIcon(QtGui.QIcon(str(RUNTIME_ICON_FILE)))
    app.setQuitOnLastWindowClosed(True)
    app.setFont(QFont("Microsoft YaHei UI", 9))
    load_system_fonts()
    faintocr = FaintOCRApplication()
    faintocr.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
