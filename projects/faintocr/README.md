# FaintOCR

FaintOCR 主应用，入口为 `main.py`，源码来源为原 `4.2.2.py`。网络、屏幕、剪贴板和 OCR 协议保持原逻辑，本次仅重构资源与运行数据的 I/O 布局。

## 目录结构

```text
faintocr/
├── main.py
├── README.md
├── assets/
│   └── logo.ico                  # 只读、随 Git 和应用一起分发
└── runtime/                      # 源码运行默认位置，全部 Git 忽略
    ├── config/settings.json
    ├── data/dictionaries/
    │   ├── genshin-impact/
    │   │   ├── raw/              # TextMapCHS/EN/JP.json
    │   │   └── derived/          # CanonicalMap、MatchStatic
    │   └── star-rail/
    │       ├── raw/
    │       └── derived/
    ├── exports/subtitles/YYYY-MM-DD.txt
    ├── logs/runtime_YYYY-MM-DD.log
    └── debug/
        ├── detection/
        └── preprocessing/
```

运行目录按需建立，不提交空目录。当前仓库没有旧运行数据，因此没有执行数据迁移或旧数据删除。`assets/logo.ico` 复制自 `D:\IA\OCR\FaintOCR\Codeia\logo.ico`；原文件未修改。

## 源码与打包后的路径

| 运行方式 | 只读资源 | 默认可写运行数据 |
| --- | --- | --- |
| Python 直接运行 | `main.py` 同级 `assets/` | `main.py` 同级 `runtime/` |
| PyInstaller 单目录包 | `sys._MEIPASS/assets/`，通常在包的 `_internal/` 中 | `%LOCALAPPDATA%/IA/FaintOCR/runtime/` |
| PyInstaller 单文件包 | 临时解包目录 `sys._MEIPASS/assets/` | `%LOCALAPPDATA%/IA/FaintOCR/runtime/` |
| 其他设置了 `sys.frozen` 的打包方式 | exe 同级 `assets/` | `%LOCALAPPDATA%/IA/FaintOCR/runtime/` |

路径不依赖当前终端工作目录。打包运行不会把用户数据写入安装目录或临时解包目录；`LOCALAPPDATA` 缺失时回退到用户主目录的 `AppData/Local`。

路径定义直接保留在 `main.py` 中，不再使用独立路径管理模块或 `AppPaths`。不提供 `FAINTOCR_RUNTIME_DIR` 环境变量覆盖。

## 打包资源约定

打包时需要：

- 将本项目 `assets/` 收集到包内的 `assets/`，不能只设置 exe 图标而漏掉运行时 `logo.ico`。
- 收集 `rapidocr_onnxruntime` 的 `config.yaml`、默认模型以及配置引用的字符表等数据，保留包内相对布局。使用 PyInstaller 时可在 spec 的 `datas` 中加入 `collect_data_files("rapidocr_onnxruntime")`，并加入 `(项目 assets 目录, "assets")`。
- 不打包 `runtime/`、本机配置、日志、导出文件或根目录 `deepseek_api_key.json`。
- 在与旧 OCR 接口兼容、依赖齐全的环境构建。本次未生成或实测 exe；测试模拟了单文件、单目录及普通 frozen 路径分支。

路径依据参见 [PyInstaller 运行时文档](https://pyinstaller.org/en/stable/runtime-information.html)。

## OCR 模型

已恢复原始 `RapidOCR(...)` 初始化：标准引擎和轻量引擎自行使用其默认配置与模型。应用不再复制模型、创建哈希目录、验证修复模型缓存或重写模型配置；原有双引擎参数保持不变。

撤回独立路径模块时，原子写入和调试图片处理函数放回 `main.py`，保留这些已经确认的行为。没有删除任何运行数据或模型文件。

## 写入与清理边界

- 配置、词库和调试图统一采用同目录临时文件 → flush/fsync → 原子替换；失败时保留已有目标文件并清理本次临时文件。
- 字幕是追加保存的用户输出，按当天日期分文件，跨午夜自动换文件；不参与缓存或日志清理。
- 日志仍保留三天。
- 调试图默认关闭。开启后每次保存只在对应 `detection/` 或 `preprocessing/` 文件夹内清理本程序命名的 PNG：保留最近三天、最多 200 张；不会递归清理，不跟随符号链接。
- 调试图采用 OpenCV PNG 编码后由 Python 写文件，支持中文目录；编码或写入失败会记录警告。
- 配置、原始词库、派生词库、字幕和模型不参与调试图清理。词库原有的显式刷新/删除失效文件逻辑保留，仅作用于当前游戏和指定文件。
- 未使用的 `OUTPUT_DIR` 常量已移除；保留旧路径的 Git 忽略项只为防止旧程序误生成的数据入库。

## 当前 I/O 清单

| 接口 | 输入/输出位置或系统 | 本次变化 |
| --- | --- | --- |
| 配置 | `runtime/config/settings.json` | 从根目录 UserConfig.json 移入，统一原子写入 |
| 原始词库 | `runtime/data/dictionaries/<game>/raw/` | 与派生文件分层，游戏目录名统一小写连字符 |
| 派生映射与匹配缓存 | 同游戏的 `derived/` | 生成、mtime 检查和失效删除均经过统一路径函数 |
| 字幕导出 | `runtime/exports/subtitles/` | 新目录，文件名使用日期，保持追加行为 |
| 日志 | stderr、`runtime/logs/`、调试浮窗 | 文件位置改变，轮转规则不变 |
| 检测/预处理图片 | `runtime/debug/detection/`、`preprocessing/` | 检查编码写入结果，增加保留边界 |
| 应用图标 | `assets/logo.ico` | 已从原目录复制为版本化资源 |
| 系统字体 | Windows Fonts 的 segoeui、segoeuib、msyh、msyhbd | 未改 |
| 屏幕像素 | MSS 截图 → NumPy/OpenCV | 未改 |
| OCR 模型 | 由原 rapidocr_onnxruntime 引擎管理 | 已撤回应用侧模型缓存和配置重写 |
| GitLab 仓库元数据 | HTTPS 请求仓库更新时间 | 未改 |
| GitLab 原始词库下载 | HTTPS 流式下载到 raw 词库 | 网络协议不变，保存路径改变 |
| 剪贴板 | Qt 手动/自动写入字幕 | 未改 |
| GUI | 鼠标、控件、区域选择输入和浮窗输出 | 未改 |
| Windows 窗口接口 | AppUserModelID、窗口样式、截图排除 | 未改 |
| 启动上下文 | argv、frozen、_MEIPASS、LOCALAPPDATA | 分离资源与可写数据，不依赖 CWD |

主程序没有 DeepSeek/API Key I/O，也没有调用 `ia_learning_core`。没有数据库、监听端口、子进程或文件选择对话框接口。

## 环境兼容性与验证

工作区环境为 Python 3.14.10 + rapidocr 3.10.0，尚不具备完整运行此主程序的条件：缺少 orjson、mss、rapidfuzz、loguru 和 rapidocr_onnxruntime。原主程序仍依赖旧构造参数及 `result, _ = engine(img)` 返回协议，不能仅换 import 使用 RapidOCR 3.x。已移除为模型配置重写新增的 PyYAML 导入。

本次未安装或替换 OCR 引擎，也未声称 FaintOCR 整体能运行。撤回后 21 项回归检查通过，包含：源码/模拟打包目录、raw/derived 分层、原子替换失败保护、调试清理边界、真实中文路径 PNG 写入、原始 OCR 构造参数检查，以及原有 Demo/密钥测试。主程序中的配置与词库 I/O 类使用 AST 提取执行，避开未安装的 OCR 依赖；这不等同于完整主程序启动测试。

运行全部检查（对照源码路径可选）：

```powershell
$env:FAINTOCR_REFERENCE_PATH = 'D:\IA\OCR\FaintOCR\Codeia\5.x\Demo 5.4.3.py'
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```
