# FaintOCR

FaintOCR 主应用，入口为 `main.py`，源码来源为原 `4.2.2.py`。已适配工作区 Python 3.14.10、RapidOCR 3.10.0、PySide6 6.12.0。网络、截图、剪贴板及下游文本过滤逻辑保持原有行为。

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
- 收集 `rapidocr` 的配置、默认模型配置及引擎需要的数据，保留包内相对布局。使用 PyInstaller 时可在 spec 的 `datas` 中加入 `collect_data_files("rapidocr")`，并加入 `(项目 assets 目录, "assets")`。
- 不打包 `runtime/`、本机配置、日志、导出文件或根目录 `deepseek_api_key.json`。
- 在安装根目录 requirements.txt 的当前兼容环境中构建。本次未生成或实测 exe；测试模拟了单文件、单目录及普通 frozen 路径分支。

路径依据参见 [PyInstaller 运行时文档](https://pyinstaller.org/en/stable/runtime-information.html)。

## OCR 模型

使用 `from rapidocr import RapidOCR`。模型仍由引擎自行管理，应用不复制模型、不创建哈希目录、不重写配置文件。两个引擎的线程参数改为 `EngineConfig.onnxruntime.intra_op_num_threads=4`；轻量路径保留 `Det.limit_side_len=1280`、`Det.limit_type=max`，通过新版 `params` 字典传入。

当前引擎默认使用 PP-OCRv6 检测/识别与分类模型。已有模型位于当前引擎的默认目录，首次使用或模型缺失时可能由 RapidOCR 下载。模型版本不同于原旧包的默认值，生成测试图识别通过不代表每个游戏场景的准确率和性能完全相同。

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
| OCR 模型 | 由当前 rapidocr 引擎管理 | 已撤回应用侧模型缓存和配置重写 |
| GitLab 仓库元数据 | HTTPS 请求仓库更新时间 | 未改 |
| GitLab 原始词库下载 | HTTPS 流式下载到 raw 词库 | 网络协议不变，保存路径改变 |
| 剪贴板 | Qt 手动/自动写入字幕 | 未改 |
| GUI | 鼠标、控件、区域选择输入和浮窗输出 | 未改 |
| Windows 窗口接口 | AppUserModelID、窗口样式、截图排除 | 未改 |
| 启动上下文 | argv、frozen、_MEIPASS、LOCALAPPDATA | 分离资源与可写数据，不依赖 CWD |

主程序没有 DeepSeek/API Key I/O，也没有调用 `ia_learning_core`。没有数据库、监听端口、子进程或文件选择对话框接口。

## 本次兼容性核查与修复

| 核查项目 | 原问题 | 当前处理与结果 |
| --- | --- | --- |
| 导入依赖 | 缺少 orjson、mss、rapidfuzz、loguru，主程序首先在 orjson 处失败 | 已在项目 .venv 安装并在根 requirements.txt 锁定，包含 Windows 日志依赖 win32-setctime |
| 引擎导入 | 导入未安装的 rapidocr_onnxruntime | 改为已安装的 rapidocr 3.10.0 |
| 构造参数 | 旧线程和检测尺寸关键字不被新版接受 | 使用 params 中的完整配置键，保留原线程数和轻量检测尺寸 |
| 返回结果 | 旧代码按 result, elapsed 解包 | 从输出对象 boxes/txts/scores 组装原过滤算法所需的框/文本/分数；处理空结果，字段长度不一致时明确报错 |
| 文本过滤 | 需确认适配没有改变原有语义 | 同行空格、跨行换行、裁剪后高度筛选及未裁剪时保留结果均通过回归检查 |
| 模糊匹配 | 缺失 RapidFuzz，无法匹配词库 | 补齐依赖，真实 TextMatcher 匹配检查通过 |
| 屏幕截图 | 需确认 MSS 新版本支持当前调用 | MSS 10.2.0 的 MSS().grab 实测通过；16×16 测试区域未保存 |
| Qt | 需验证当前 PySide6 的真实窗口行为 | 原生 Windows 浮球、字幕和设置窗口绘制、退出清理通过，无 Qt 回调异常 |
| 图像处理 | 当前安装 opencv-python-headless | 本程序 GUI 由 Qt 提供，无需 OpenCV HighGUI；真实 OCRWorker 预处理和推理流程通过 |
| 文件/日志 | 需验证新 Python 下配置、导出与日志写入 | 临时目录中的 orjson 设置保存、UTF-8 字幕导出和 Loguru 初始化/清理均通过 |

补齐版本为 orjson 3.13.0、mss 10.2.0、RapidFuzz 3.14.6、loguru 0.7.3、win32-setctime 1.2.1；pip check 未发现依赖冲突。

## 运行与检查

无需切换目录即可运行：

```powershell
& "D:\IA\IA-Python-Workspace\.venv\Scripts\python.exe" "D:\IA\IA-Python-Workspace\projects\faintocr\main.py"
```

从仓库根目录执行回归测试：

```powershell
$env:FAINTOCR_REFERENCE_PATH = 'D:\IA\OCR\FaintOCR\Codeia\5.x\Demo 5.4.3.py'
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

27 项检查通过。快速测试不执行模型推理；其中保留的 I/O 测试使用 AST 提取，新增兼容性测试直接导入真实 FaintOCR 主模块。

显式运行模型与主程序集成检查：

```powershell
.venv\Scripts\python.exe -B tests/check_faintocr.py
# 显示短暂的原生窗口，并额外测试小区域屏幕抓取：
.venv\Scripts\python.exe -B tests/check_faintocr.py --native --capture
```

集成检查实测通过：两个引擎识别生成的中英文图片；图像经后台线程 OCR → 字幕显示 → UTF-8 导出；原生窗口绘制；配置保存和退出。检查使用临时配置，不覆盖真实用户数据。正常运行会按项目目录约定生成 runtime 文件。

验证边界：未进行真实游戏连续运行、各种 DPI/多显示器组合、GitLab 在线词库下载和打包 exe 的端到端验证；真实 API 密钥及 Demo 不受此次适配影响。原生窗口截图排除设置调用未报错，但未专门验证不同录屏软件中的排除效果。
