# IA Learning Core

- `core.py`：标准库实现的请求、解析、后台任务及固定提示词文件读写；不依赖第三方包。
- `view.py`：依赖 PySide6 的标注视图，只用 QtCore / QtGui / QtWidgets。
- `prompts/annotation.txt`：标注提示词。
- `prompts/explanation.txt`：解释提示词。
- `__init__.py`：导出 `PROMPT_ROOT`、`prompt_dir()`、`prompt_path()`，不自动导入 Qt。

## 安装

工作区提供 `pyproject.toml`（setuptools 后端），包目录为 `packages/`，提示词通过 `package-data` 随包分发：

```powershell
.venv\Scripts\python.exe -m pip install -e .
```

可选依赖：`demo`、`faintocr`、`dev`（`pip install -e ".[demo]"`）。构建出的 wheel 包含 `prompts/annotation.txt` 与 `prompts/explanation.txt`。

## 提示词

`prompt_path('annotation.txt')` / `prompt_path('explanation.txt')` 返回当前可编辑文件：

1. `IA_PROMPT_DIR` 环境变量；
2. 源码检出（包目录旁有 `.git`）时是包内 `prompts/`；
3. 安装后的包使用 `%APPDATA%\IA\ia-learning-core\prompts\`，首次使用时从包内默认值复制。

`PromptFile.save()` 检查空内容和外部修改后保存；源码检出时的历史由 Git 记录。应用通过 `prompt_path()` 指定文件，不扫描目录或选择版本。

## 密钥

`core.config_candidates()` 给出密钥文件优先级：`IA_LEARNING_CONFIG_PATH` → 用户配置目录 `%APPDATA%\IA\ia-learning-core\` → 仓库根目录。`DEEPSEEK_API_KEY` 环境变量优先于这些文件；`LearningCore.annotate(...)` 与 `explain(...)` 的关键字参数 `key` 优先级最高。资源和配置定位不依赖工作目录。

Demo 5.5.0 的提示词编辑器属于其入口，5.4.3 仅为对照基线，都不依赖本包的界面代码。
