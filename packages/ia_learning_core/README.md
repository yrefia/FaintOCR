# IA Learning Core

- `core.py`：标准库实现的请求、解析、后台任务及固定提示词文件读写；不依赖第三方包。
- `view.py`：依赖 PySide6 的标注视图，只用 QtCore / QtGui / QtWidgets。
- `prompts/annotation.txt`：标注提示词。
- `prompts/explanation.txt`：解释提示词。
- `__init__.py`：导出 `PROMPT_ROOT`、`prompt_dir()`、`prompt_path()`，不自动导入 Qt。

## 安装

标注请求默认使用 SSE 流式传输；每个非空内容增量在后台线程解析，
从累计 JSON 中读取已闭合字段。解析快照存入单槽邮箱，`poll()` 每轮只取最新
快照（生成中为 `partial=True`），不会重放历史增量。完成与失败携带最后文档，
主线程仅应用快照；标注未变化时不重建视图，只有范围、层级或原文变化才重新排版。`source` 与 `annotated` 字符串完整后立即渲染
可验证的标签范围；不等待句子对象或 `annotations` 数组闭合。属性未到达时显示
“属性接收中”，暂不请求解释，完整属性记录到达后补齐；最终结果仍按原规则校验。
不补猜未完成的 JSON 字段。宿主必须保持生成状态，直到收到最终成功或失败事件；
断流时保留预览，但提示结果不完整。解释请求仍使用非流式 JSON。
默认传输支持 `request_annotations(key, payload, on_delta=callback)`，回调接收累计文本；
原有注入的双参数 transport 仍返回完整响应体。旧 revision 的增量和终态均被丢弃。

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

`core.config_candidates()` 给出密钥文件优先级：`IA_LEARNING_CONFIG_PATH` → 用户配置目录 `%APPDATA%\IA\ia-learning-core\` → 仓库根目录；设置了 `IA_LEARNING_CONFIG_PATH` 时只使用该文件，文件不存在直接报错，不回退到后面的位置。`DEEPSEEK_API_KEY` 环境变量优先于这些文件；`LearningCore.annotate(...)` 与 `explain(...)` 的关键字参数 `key` 优先级最高。资源和配置定位不依赖工作目录。

Demo 5.5.0 的提示词编辑器属于其入口，5.4.3 仅为对照基线，都不依赖本包的界面代码。
