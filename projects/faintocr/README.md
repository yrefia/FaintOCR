# FaintOCR

独立 OCR 应用，当前保留版本 `4.2.2`，入口为 `main.py`。

从工作区根目录运行：

```powershell
python projects/faintocr/main.py
```

源码中的第三方依赖包括 PySide6、orjson、mss、rapidocr_onnxruntime、opencv-python（cv2）、numpy、rapidfuzz、requests 和 loguru。当前未提供经过验证的依赖版本锁定文件。

工作区默认环境是 Python 3.14.10 + rapidocr 3.x（见根目录 README 的 Python 环境一节），与本应用不兼容：这里依赖已停更的 `rapidocr_onnxruntime`，并调用旧接口 `result, _ = engine(img)`。运行本应用需要单独的 Python 3.12 环境并安装上述依赖，或先改写 OCR 调用代码。

源码模式的数据根目录为本项目目录：配置 `UserConfig.json`、`TextMap/`、`OCR_Results/`、`logs/`、`Test/`、`detect_debug/` 和 `outputs/` 均位于项目根目录，已加入 Git 忽略规则。打包模式仍使用可执行文件所在目录。

代码还引用 `logo.ico` 等外部资源；本次提供的文件中未包含这些资源，未进行完整 GUI 运行验证。

## I/O 接口与重构影响审计（2026-10-29）

审计对象为当前 `main.py`。下表按进程对外边界完整归类；线程队列、Qt signals/slots 和内存中的 NumPy 数组是进程内传递，不另计为外部 I/O。代码行号对应此次审计版本。

### I/O 清单

| 接口 | 方向 / 实际行为 | 代码位置 | 环境与目录影响 |
| --- | --- | --- | --- |
| 用户配置 | 读取 `UserConfig.json`；以 `.tmp` 写入并 `os.replace` 原子替换；启动读，设置变更/退出时保存 | `UserConfigManager.load/save`，931–955；配置路径 703 | 数据根目录变了；新位置无配置，将回到默认设置。读写依赖缺失的 orjson |
| 原始游戏词库 | 读写 `TextMap/<游戏目录>/TextMapCHS.json`、`TextMapEN.json`、`TextMapJP.json`；检查 mtime，清理失效文件 | `get_file_path` 1365；加载 1493；原子保存 1829 | 新位置无旧词库；需迁移或重新获取。JSON 解析依赖 orjson |
| 派生映射与匹配缓存 | 读写 `CanonicalMap-<源语言>to<目标语言>.json`、`MatchStatic-<源语言>to<目标语言>.json`；生成、删除失效缓存、临时文件替换 | 1390–1425、1530–1575、1720–1775、1829 | 同属 TextMap，新位置无缓存；可重新生成。匹配链路还缺 rapidfuzz |
| 字幕文本输出 | 手动/自动追加 UTF-8 文本到 `OCR_Results/OCR_Results_YYYY-MM-DD.txt`，每条后追加两个换行 | `Config.output_file_path` 699；`write_subtitle_to_file` 7656 | 新路径；父目录按需建立，旧记录不会自动搬迁 |
| 日志 | 写 stderr、`logs/runtime_YYYY-MM-DD.log`，保留三天；日志同时桥接到浮窗 | `setup_logging` 77；`FloatingDebugLogBridge` 105 | 新路径，目录自动建立；当前缺 loguru，日志链路不可用 |
| 检测调试图片 | 开启调试时写 `detect_debug/diff_<时间>.png` | 2081–2086 | 新路径，目录按需建立；截图输入仍受 mss 缺失影响 |
| 图像处理调试图片 | 写 `Test/process_input.png`、`process_cropped.png`、`process_0/1/2/4.png` | 2291–2404 | 新路径，目录按需建立；cv2 图像写入接口可用，但完整链路未运行 |
| 应用图标 | 从 `BASE_DIR/logo.ico` 创建 Qt 图标 | 62、7259–7268 | 新位置缺文件；原目录存在。功能可降级，但任务栏/窗口自定义图标缺失 |
| 系统字体 | 读取 Windows Fonts 中 segoeui、segoeuib、msyh、msyhbd，交给 Qt 注册 | 3593–3598、7878 | 四个字体文件均存在；不受项目层级变化影响 |
| 屏幕像素输入 | 手动截图：`mss.MSS().grab(monitor)`；检测循环：长期截图对象抓取区域，转换 NumPy/OpenCV 图像 | `_capture` 2073；`start_work` 2102；手动截图 3154–3163 | 当前缺 mss，无法截图；无项目路径依赖。多屏、DPI、区域坐标仍需实际桌面验证 |
| OCR 引擎/模型 | 截图数组进入两个 RapidOCR 实例；引擎读取模型，返回框、文本和置信度 | 初始化 3036/3041；`run_rapidocr` 2555 | 旧模块缺失；新版构造参数和返回结构不兼容。模型位置由引擎包配置控制，不由项目 BASE_DIR 控制 |
| GitLab 仓库元数据 | HTTPS GET `gitlab.com/api/v4/projects/<编码项目名>`，读取 `last_activity_at`，与本地 mtime 比较 | `GitLabRepositoryChecker` 1241 | URL/协议不受目录变化影响；requests 可导入，未实测远端连通性 |
| GitLab 词库下载 | HTTPS 流式 GET `Dimbreath/AnimeGameData2`、`Dimbreath/turnbasedgamedata` 的 main 分支 TextMap 文件；重试、进度和取消 | 配置 849–874；下载 1625–1680 | 网络目标未变，落盘位置变为新 TextMap。原代码使用 `verify=False`，这是已有行为，不是本次重构引入 |
| 系统剪贴板 | 手动复制字幕或识别后自动 `QApplication.clipboard().setText` | 5646、7679 | 仅写剪贴板，没有读取；无项目路径依赖。Qt 已可导入，未改动用户剪贴板验证 |
| GUI 输入与显示输出 | 鼠标按钮、拖动、滚轮、区域选择、设置控件输入；显示悬浮球、字幕、区域覆盖层、欢迎/教程与设置窗口；读取屏幕尺寸和鼠标位置 | 各 QWidget 事件；应用连接 7167–7205 | PySide6 可导入且 Demo 已通过离屏运行；不能据此认定 FaintOCR 所有 GUI/原生窗口功能正常，程序仍被导入依赖阻断 |
| Windows 窗口系统 | 设置 AppUserModelID；读取/切换窗口扩展样式；`SetWindowDisplayAffinity` 将浮窗排除出截图 | 67–74、3601–3633 | 依赖 Windows 原生窗口与桌面会话，不依赖项目目录；实际截图排除未验证 |
| 启动上下文 | 读取 `sys.argv` 交给 QApplication；读取 `sys.frozen` / `sys.executable` 定位打包目录；默认设置 `QT_ENABLE_HIGHDPI_SCALING` | 53–60、7884–7897 | 源码模式基于 `__file__`，可从任意工作目录启动；打包模式仍使用 exe 目录。未定义独立 CLI 文件输入/输出参数 |

补充：`OUTPUT_DIR = BASE_DIR / "outputs"`（3592）目前仅声明，没有实际读写调用；不是正在使用的输出接口。主程序没有 DeepSeek/API Key I/O，也没有调用 `ia_learning_core`；这些属于 Demo，不能与 FaintOCR OCR 主程序混为一谈。未发现数据库、监听端口、子进程或用户文件选择对话框接口。

### 已确认的影响

1. **环境阻断启动。** 当前 `.venv` 是 Python 3.14.10。直接导入主程序首先抛出 `ModuleNotFoundError: No module named 'orjson'`。同时缺少 mss、rapidfuzz、loguru、rapidocr_onnxruntime；这些是当前环境实际缺项，不只是 requirements 文件声明问题。
2. **RapidOCR 不是改一行 import 就能兼容。** 已安装 rapidocr 3.10.0 / onnxruntime 1.31.1。安装包的构造签名为 `(config_path=None, params=None)`，主代码的 `intra_op_num_threads=4`、`det_limit_side_len=1280` 等旧关键字会报 TypeError。新版返回 `RapidOCROutput`（boxes/txts/scores），旧代码 `result, _ = engine(img)` 也会报不能解包。若迁移到新版，需显式映射配置与结果结构，并重新验证双引擎、过滤、坐标、识别精度和速度。
3. **资源根目录已正确调整，但旧数据未迁移。** 当前为 `D:\IA\IA-Python-Workspace\projects\faintocr`；原目录 `D:\IA\OCR\FaintOCR\Codeia` 存在 UserConfig.json、TextMap、logo.ico、OCR_Results、logs 和 Test。新位置均不存在。仅移动 Python 文件不会迁移这些资料。
4. **新目录中的缺项需区别处理。** UserConfig.json 不存在会恢复默认设置，TextMap 缺失需迁移或重新生成，logo.ico 缺失影响图标；logs、OCR_Results、Test、detect_debug 是按需建立的输出目录，缺失本身不是异常。旧运行记录仍留在原位置。
5. **未发现这次层级迁移留下的路径计算错误。** 源码 BASE_DIR 已是 `Path(__file__).resolve().parent`，已验证指向项目根目录。去掉版本目录之后，数据仍留在项目级。Git 忽略规则与这些目录一致。
6. **未受路径变化直接影响的接口不能视为已完成端到端验证。** 字体位置存在；PySide6、cv2、numpy、requests 可实际导入。GitLab 在线访问、真实屏幕捕获、剪贴板、Windows 截图排除和 FaintOCR 完整 UI 尚未实测。

### 验证边界与下一步

此次只审计 FaintOCR，未安装其缺失依赖、迁移旧数据、下载词库或模型，也未改变主程序业务代码。未对当前不兼容的 RapidOCR 接口做静默替换。

如继续适配当前环境，应依次补齐依赖，适配 RapidOCR 3.x 的构造参数和输出结构，迁移需要保留的配置/词库/图标，再验证真实截图 → OCR → 匹配 → 显示 → 剪贴板/文件输出链路。
