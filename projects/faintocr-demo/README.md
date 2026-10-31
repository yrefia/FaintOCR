# FaintOCR Demo

`main.py` 是当前运行入口，使用公共 `ia_learning_core.core` 和 `ia_learning_core.view`。提示词编辑器 `PromptEditor` 定义在本入口内，属于 Demo 界面，不属于公共包。

## 依赖

Demo 只需要 Qt 界面，见 `requirements-demo.txt`（`PySide6-Essentials==6.12.0`）。核心与视图只用 QtCore / QtGui / QtWidgets，不需要 PySide6 元包、WebEngine、Pdf 或 Addons；OCR 相关依赖属于 `projects/faintocr`（`requirements-faintocr.txt`）。

公共包已可通过 `pyproject.toml` 安装，入口会优先使用已安装的包，未安装时才回退到仓库内 `packages/`：

```powershell
.venv\Scripts\python.exe -m pip install -e .
```

5.4.3 是外部历史对照文件，不保存在本项目中，也不是公共包调用方。对照测试默认读取本机固定路径，也可通过 `FAINTOCR_REFERENCE_PATH` 指定，见根目录 README.md。

5.5.0 读取公共包的 `annotation.txt` 和 `explanation.txt`，支持编辑、保存和重新加载，不扫描版本。

从工作区根目录运行：

```powershell
.venv\Scripts\python.exe projects/faintocr-demo/main.py
```

已在 Python 3.14.10 和 `requirements-demo.txt` 锁定的 PySide6-Essentials 6.12.0 下通过 Qt 离屏启动、窗口绘制、离线标注、提示词编辑及模拟网络流程测试。真实 API 调用及实际鼠标拖动未验证。

## 提示词与密钥

提示词位置按 `ia_learning_core.prompt_dir()` 解析：`IA_PROMPT_DIR` 环境变量 → 源码检出时的包内 `prompts/`（改动随 Git 记录）→ 安装后的用户目录 `%APPDATA%\IA\ia-learning-core\prompts\`（首次从包内默认值复制）。界面只修改当前提示词文件，不覆盖其他副本。

程序仅在启动时读取本地密钥并填入输入框，顺序为 `DEEPSEEK_API_KEY` → `IA_LEARNING_CONFIG_PATH` → 用户配置目录 → 仓库根目录。显式配置路径无效时不会回退。此后标注与解释请求只使用输入框当前的完整密钥；清空后提示输入，不再读取本地配置。界面仅显示前 8 位和后 4 位，中间按实际字符数显示圆点，支持逐位编辑；不超过 12 位时前后范围覆盖整个密钥。可用 Ctrl+A 后粘贴替换完整密钥。密钥不会写入配置文件、请求体或界面历史。
