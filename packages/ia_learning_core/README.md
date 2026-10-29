# IA Learning Core

- `core.py`：标准库实现的请求、解析、后台任务及固定提示词文件读写。
- `view.py`：依赖 PySide6 的标注视图。
- `prompts/annotation.txt`：标注提示词。
- `prompts/explanation.txt`：解释提示词。
- `__init__.py`：导出 `PROMPT_ROOT`，不自动导入 Qt。

应用通过 `PROMPT_ROOT / 'annotation.txt'` 和 `PROMPT_ROOT / 'explanation.txt'` 指定文件，不扫描目录或选择版本。`PromptFile.save()` 检查空内容和外部修改后保存；历史由 Git 记录。

入口将工作区 `packages/` 加入模块搜索路径。目前使用源码导入，尚未配置安装或 wheel 构建；未来构建时需将提示词包含为包数据。文件来源集中见根目录 README.md。

提示词编辑界面属于 Demo 5.5.0，内联于其入口中；5.4.3 仅为对照基线，不依赖本包。

DeepSeek 密钥由核心在发送请求前读取仓库根目录 `deepseek_api_key.json` 的 `api_key`。`LearningCore.annotate(source, prompt, model)` 和 `explain(number, prompt, model)` 支持可选关键字参数 `key`，优先使用非空传入值，否则读取本地配置。资源和配置定位不依赖工作目录。
