# IA Python Workspace

IA 的 Python 项目与公共代码仓库，统一使用 Git 管理。

## 目录结构

```text
projects/
├── faintocr/
│   ├── README.md
│   ├── main.py
│   ├── assets/logo.ico
│   └── runtime/                   # 按需生成，Git 忽略
└── faintocr-demo/
    ├── README.md
    └── main.py
packages/
└── ia_learning_core/
    ├── README.md
    ├── __init__.py                # 提示词定位与包入口
    ├── core.py                    # 标准库实现的请求/解析核心
    ├── view.py                    # 依赖 PySide6 的标注视图
    └── prompts/
        ├── annotation.txt
        └── explanation.txt
tests/
├── check_rapidocr.py
├── check_faintocr.py
├── test_credentials.py
├── test_demo.py
├── test_packaging.py
├── test_faintocr_runtime.py
├── test_faintocr_compatibility.py
└── test_prompt_files.py
.github/workflows/ci.yml             # ruff + 单元测试
pyproject.toml                       # 包元数据、可选依赖（extras）、ruff 配置
requirements.txt                     # 完整环境快照（OCR + Demo）
requirements-demo.txt                # Demo 的最小直接依赖
requirements-faintocr.txt            # FaintOCR 的最小直接依赖
requirements-dev.txt                 # 开发工具（ruff）
deepseek_api_key.json                # 本地配置，Git 忽略
```

FaintOCR 与 Demo 是两个独立应用。公共包包含学习核心、标注视图和固定提示词资源；提示词编辑器内联在 Demo 5.5.0 内。5.4.3 仅作为外部原始对照基线，不是公共包调用方，也不保存在当前仓库。`ia_` 是 IA 命名空间前缀，不代表版本。`ia_learning_core` 已是可安装包（`pyproject.toml`，extras：`demo` / `faintocr` / `dev`）；`requirements.txt` 是完整环境快照，`requirements-demo.txt` 与 `requirements-faintocr.txt` 只列各应用的直接依赖。`tests/check_rapidocr.py` 是环境自检入口，`tests/test_prompt_files.py` 与 `tests/test_packaging.py` 是回归单测。

## 运行

在工作区根目录，使用 `.venv` 中的 Python 运行（见下一节）：

```powershell
.venv\Scripts\python.exe projects/faintocr/main.py
.venv\Scripts\python.exe projects/faintocr-demo/main.py
```

入口优先导入已安装的 `ia_learning_core`；未安装时才回退到仓库内 `packages/`。安装为可编辑包（推荐，导入不再依赖终端工作目录或源码位置）：

```powershell
.venv\Scripts\python.exe -m pip install -e .
```

5.4.3 作为外部对照文件，不作为当前环境的运行入口。具体依赖见项目 README.md。导入和资源路径均相对于源码定位，不依赖终端工作目录。

## Python 环境

工作区默认为 **Python 3.14.10**，虚拟环境位于 `.venv/`，已安装 OCR 依赖 `rapidocr==3.10.0` 与 ONNX Runtime 后端 `onnxruntime==1.31.1`，完整版本见 `requirements.txt`。

依赖按用途拆分，任一文件都可单独安装：

| 文件 | 用途 |
| --- | --- |
| `requirements.txt` | 完整环境快照（OCR + Demo），用于复现当前 `.venv` |
| `requirements-demo.txt` | 只装 Demo：`PySide6-Essentials==6.12.0` |
| `requirements-faintocr.txt` | 只装 OCR 应用：Qt Essentials + RapidOCR 等直接依赖 |
| `requirements-dev.txt` | 开发工具 `ruff` |

两个应用只用 QtCore / QtGui / QtWidgets，因此 Qt 依赖只声明 `PySide6-Essentials`；`PySide6` 元包、`PySide6-Addons`、`PySide6-WebEngine`、`PySide6-Pdf` 都不需要，也不再出现在依赖文件中。当前 `.venv` 因此从约 927 MB 降到约 518 MB（WebEngine/Pdf 约 290 MB，Addons 与元包约 105 MB）。

安装示例：

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-demo.txt   # 只跑 Demo
.venv\Scripts\python.exe -m pip install -r requirements.txt         # 完整环境
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt     # 代码检查
```

选择 3.14 的原因：RapidOCR 的默认后端是 onnxruntime，而 onnxruntime 1.31.1 在 Windows 上只发布到 `cp314` 的 wheel，没有 `cp315`，所以 3.14 是当前能跑通 RapidOCR 的最高 Python 版本；3.14.10 是该分支最新补丁。

| 路径 | 用途 |
| --- | --- |
| `.python/` | uv 安装的独立 CPython 3.14.10，不写注册表和用户目录 |
| `.venv/` | 工作区虚拟环境，由上面的解释器创建 |
| `.tooling/uv.exe` | 重建环境用的 uv 0.13.6 |

上述目录都在 `.gitignore` 中忽略，不入库。

激活后即可运行，也可以直接用 `.venv\Scripts\python.exe`，不激活同样有效：

```powershell
.venv\Scripts\Activate.ps1
python tests/check_rapidocr.py
```

从零重建环境（需要联网，当前工作区已有 `.tooling/uv.exe`；新克隆的仓库需先从 PyPI 的 `uv` 包取出 `uv.exe`）：

```powershell
$env:UV_NO_CONFIG = '1'
$env:UV_CACHE_DIR = "$PWD\.tooling\cache"
$env:UV_PYTHON_INSTALL_DIR = "$PWD\.python"
.\.tooling\uv.exe python install 3.14.10
.\.tooling\uv.exe venv --python "$PWD\.python\cpython-3.14.10-windows-x86_64-none\python.exe" --seed .venv
.\.tooling\uv.exe pip install --python .\.venv\Scripts\python.exe -r requirements.txt
```

`tests/check_rapidocr.py` 渲染一张中英文图片并实际调用引擎，用于确认解释器、依赖、模型与推理链路可用；首次运行会把 PP-OCRv6 检测与识别模型下载到 `.venv\Lib\site-packages\rapidocr\models`（约 30 MB），之后可离线运行。它不命名为 `test_*.py`，因此 `unittest discover` 不会自动执行，单测保持快速、无模型依赖。

兼容性说明：`projects/faintocr` 已适配当前 RapidOCR 3.x 的构造参数及输出对象，已补齐运行依赖。FaintOCR 和 Demo 均使用本工作区虚拟环境，原生窗口和生成图片的实际 OCR 流程已验证。`ia_learning_core` 可用 `pip install -e .` 安装（`pyproject.toml` 声明包数据，提示词随 wheel 一起分发），因此入口和测试不再需要 `sys.path` 探测仓库布局。

## DeepSeek API Key

在仓库根目录的 `deepseek_api_key.json` 中填写：

```json
{
  "api_key": ""
}
```

将空字符串替换为自己的密钥。该文件已加入根目录 `.gitignore`，不会随正常 Git 提交入库；新克隆需自行创建。不要强制添加此文件。

`ia_learning_core` 在实际发送标注或解释请求前解析密钥，不依赖当前工作目录。优先级从高到低：

1. `annotate()` / `explain()` 的关键字参数 `key`（Demo 界面输入框，非空时优先）；
2. 环境变量 `DEEPSEEK_API_KEY`；
3. 环境变量 `IA_LEARNING_CONFIG_PATH` 指向的 JSON 文件（设置后文件不存在会直接报错，不回退到 4、5）；
4. 用户配置目录 `%APPDATA%\IA\ia-learning-core\deepseek_api_key.json`；
5. 仓库根目录 `deepseek_api_key.json`（源码检出时的历史位置，保留兼容）。

查找顺序与实现见 `core.config_candidates()`。公共核心保留密钥回退能力；Demo 只在启动时读取本地密钥到输入框，此后请求仅使用输入框当前值，清空后不再回退。输入框只显示前 8 位和后 4 位，中间按实际字符数显示圆点，支持逐位编辑；不超过 12 位时前后范围覆盖整个密钥。修改输入框立即生效，修改本地配置需重启 Demo。离线演示不需要密钥，界面输入不会写入配置文件、请求体或界面历史。

核心调用接口为 `annotate(source, prompt, model, key=None)` 和 `explain(number, prompt, model, key=None)`（`key` 为仅限关键字参数）；测试可通过 `LearningCore(config_path=...)` 指定临时配置，避免接触真实密钥。

无需切换目录即可启动 Demo：

```powershell
& "D:\IA\IA-Python-Workspace\.venv\Scripts\python.exe" "D:\IA\IA-Python-Workspace\projects\faintocr-demo\main.py"
```

## 提示词

Demo 5.5.0 通过 `ia_learning_core.prompt_path()` 取 `annotation.txt` 与 `explanation.txt`，不扫描目录、不解析文件名版本、不自动选择兼容版本。加载失败会在编辑器中显示具体错误，不会回退到其他文件。

提示词位置按运行方式解析（`ia_learning_core.prompt_dir()`）：

- `IA_PROMPT_DIR` 环境变量优先；
- 源码检出（包目录旁有 `.git`）返回包内 `prompts/`，与 Git 版本历史一致；
- 安装后的包（例如 wheel）返回用户配置目录 `%APPDATA%\IA\ia-learning-core\prompts\`，首次使用时从包内默认值复制，之后编辑的是用户副本。

界面保留编辑、保存、重新加载和未保存修改提醒。请求使用当前编辑内容；保存更新当前提示词文件，检测到外部修改时拒绝覆盖。重新加载有未保存修改时需要确认。源码检出时的修改历史由 Git 记录；提示词内容应与解析器协议保持一致。

## 命名与 Git

- Python 文件使用小写下划线命名，入口统一为 `main.py`。
- 文档统一为 `README.md`，提示词按用途命名，不在文件名中编码版本和来源。
- 项目目录使用小写连字符，Python 包使用小写下划线。
- 当前应用入口直接放在项目根目录，5.4.3 使用外部对照文件。后续版本通过 Git 提交与发布标签记录。
- `.gitignore` 排除虚拟环境、缓存、密钥配置和运行数据；不忽略提示词。

Git 分支为 `main`，已建立提交历史；尚未设置远程仓库。公共包已是可安装包：`pyproject.toml` 声明包目录、包数据（两个提示词）与 `demo` / `faintocr` / `dev` 三个 extras，`pip install -e .` 后入口与测试直接 `import ia_learning_core`；构建的 wheel 中包含两个提示词资源。

## 验证

对照检查默认读取本机 `D:\IA\OCR\FaintOCR\Codeia\5.x\Demo 5.4.3.py`；其他机器（如 CI）可用环境变量指定，文件不存在时仅跳过对照检查，其余检查继续：

```powershell
$env:FAINTOCR_REFERENCE_PATH = "D:\IA\OCR\FaintOCR\Codeia\5.x\Demo 5.4.3.py"
```

两条检查，互不干扰：

- 回归单测：`.venv\Scripts\python.exe -B -m unittest discover -s tests -v`，共 51 项检查（含 FaintOCR 路径/文件 I/O 的 7 项、接口兼容性的 6 项、打包约束的 6 项）：密钥解析优先级（界面密钥、环境变量、用户配置、仓库根目录）与无效配置提示，固定提示词加载与保存保护、提示词目录覆盖与用户副本、5.4.3 对照解析及请求协议、真实 Qt 离屏启动与绘制、6 个离线标注的选择、错误恢复，模拟标注/解释请求、缓存和失败处理，以及 extras 与 requirements 文件的一致性、`core.py` 只依赖标准库、入口优先使用已安装包。均已在 Python 3.14.10 + PySide6-Essentials 6.12.0 下通过，不调用真实 API。
- 环境自检：`.venv\Scripts\python.exe tests\check_rapidocr.py`，渲染中英文图片并真实调用 RapidOCR，首次运行需下载约 30 MB 模型。
- 代码检查：`.venv\Scripts\ruff.exe check .`（规则见 `pyproject.toml`），CI 配置见 `.github/workflows/ci.yml`。

在 DSH 沙箱等受限环境中，`tempfile` 以 0o700 创建的临时目录拿不到工作区写权限，涉及临时目录的用例会报 `PermissionError [WinError 5]`；这属于环境限制，请在普通终端或 CI 中运行单测。测试已对临时目录清理使用 `ignore_cleanup_errors=True`，清理阶段不会因此报错；环境自检在本环境通过。

## 文件来源

本节集中记录原文件名及来源；源码文件名只表达用途。

| 当前路径 | 原文件 / 来源 |
| --- | --- |
| `projects/faintocr/main.py` | `4.2.2.py`，FaintOCR 4.2.2 主应用 |
| 外部对照（不入库） | `D:\IA\OCR\FaintOCR\Codeia\5.x\Demo 5.4.3.py` |
| `projects/faintocr-demo/main.py` | `Demo 5.5.0.py`，采用共享 core/view 的独立应用 |
| `packages/ia_learning_core/core.py` | `core.py`，从 Demo 拆分的学习核心 |
| `packages/ia_learning_core/view.py` | `view.py`，从 Demo 拆分的 Qt 标注视图 |
| `packages/ia_learning_core/prompts/annotation.txt` | `An_Demo 5.4.3_03.txt`，标注提示词，正文保持原样 |
| `packages/ia_learning_core/prompts/explanation.txt` | `Ex_Demo 5.4.2_01.txt`，解释提示词，正文保持原样 |
| `tests/test_demo.py` | 5.5.0 真实 Qt 与对照回归检查；提示词编辑器现位于 5.5.0 入口，已移除公共 `prompt_editor.py` |
| `packages/ia_learning_core/__init__.py` | 整理时新增的包入口；本轮加入提示词目录解析（`prompt_dir` / `prompt_path`） |
| `tests/test_credentials.py` | 本地密钥读取及错误处理的回归检查；本轮补充密钥优先级用例 |
| `tests/test_prompt_files.py` | 固定提示词加载与保存逻辑的回归检查；本轮补充提示词目录覆盖用例 |
| `tests/test_packaging.py` | 本轮新增，检查 extras 与 requirements 一致、只依赖标准库、提示词随包分发 |
| `pyproject.toml` | 本轮新增，包元数据、extras、包数据与 ruff 配置 |
| `requirements.txt` | 完整环境快照；本轮改为 PyPI 规范包名并去掉 Qt 元包 / WebEngine / Pdf / Addons |
| `requirements-demo.txt`、`requirements-faintocr.txt`、`requirements-dev.txt` | 本轮新增，按应用与开发用途拆分的最小依赖 |
| `.github/workflows/ci.yml` | 本轮新增，ruff 与单元测试的持续集成 |
| `scripts/check_rapidocr.py` | 本次新增，渲染测试图并调用引擎的环境自检（现位于 `tests/check_rapidocr.py`） |
| `.gitignore`、各级 `README.md` | 整理时新增或更新；根文档原名为 `README.MD` |

5.4.3 使用外部原始对照文件，不跟随公共包改动。5.5.0 是真实调用方，其提示词编辑器属于应用界面，直接加载固定提示词。外部实际文件名为 `Demo 5.4.3.py`，而非 `5.4.3.py`。

## 原源码头部记录

以下为迁入文档的原始头部历史，仅供来源追溯，不代表当前行为。

### FaintOCR Demo 5.4.3

```text
# -*- coding: utf-8 -*-
# 累积版本更新记录（按时间顺序）
# Demo 5.0.0 — 原始概念验证
# - 独立 Tkinter 窗口，DeepSeek 后台请求，左侧可编辑提示词。
# - 输入中英文，输出完整词汇/短语/语法解析及 JSON；校验结构与引用。
# - 保留为最初实验基线，不含 OCR 集成或学习反馈。

# Demo 5.0.1 — 第一层候选标注
# - 将生成任务收敛到类别、名称、原文片段，不生成详细解释。
# - 三类颜色标注，分类开关、列表定位、跨片段及重叠显示。
# - 增加离线演示与定位/窗口测试；请求上限 2048 tokens。

# Demo 5.0.2 — 三层独立样式及定位修复（含本版本后续修订）
# - 句法用背景、词块用下划线、单词用粗体；选中时保留三层样式。
# - 点击重叠处选择候选，支持跨片段定位；改用英文提示词。
# - 移除中文参考输入/请求字段，分层筛选，避免常规情态结构挤占重点。
# - occurrence 按完整词边界计数，修复 era 匹配到 venerable 内部的问题。
# - 同一词块的近距离分离引用归并为连续范围，包含中间参数（如 us）。

# Demo 5.0.3 — 提示词重组与浅色下划线
# - 英文提示词分为任务、筛选、类别与输出契约，合并重复约束。
# - 明确词块原句范围与规范标签的区别，保留跨层独立选择和定位边界。
# - 词块下划线独立设为浅蓝灰色 #a6b9cf，不改变文字颜色或其他层样式。
# - 0–3 版文件头累积保留截至各版的更新记录；旧版功能保持原样。
# - 提示词效果仍需真实 API 对照验证，离线测试不证明模型选择质量。
# - 配色后续调整：沿用 5.0.1 的紫色背景、绿色词块下划线与蓝色单词，保留独立样式叠加。
# - 配色再调整：单词粗体恢复正文原色；背景和下划线增加即时选色器（当前会话生效）。

# Demo 5.0.4 — RGB / HSV / HEX 选色
# - 自定义选色窗口：RGB 0–255 整数，HSV 0–360° / 0–100% / 0–100%，HEX #RRGGBB。
# - 三种输入实时同步；校验范围、预览，确认后应用，取消不修改当前颜色。
# - 保留浅紫背景 #f2eafa，下划线默认使用同色系较深紫色 #80659e。
# - 悬停按下划线/字形/背景位置及层级优先级聚焦，点击显示已有条目信息，无候选菜单。

# Demo 5.0.5 — 固定配色与悬停动效
# - 三套浅紫背景配色：紫色 / 浅蓝 / 浅绿下划线，移除自由选色。
# - 悬停绘图层使整项文字平滑上移 3px，并为对应背景、线条或字形绘制同色描边。
# - 保留位置优先级与直接点击；所有标注反馈移除黑色边框。
# - 悬停修订：绘图层与 Text 外边界及基线对齐，按连续文字段绘制；上移减至 1px。
# - 粗体取消彩色描边，以正文同色轻微叠印加重，不改变字号和排版。
# - 再修订：静止/悬停统一 Canvas 绘制，语法填充几何固定，仅文字上移。
# - 参考 4.2.2 深色背景及 alpha 参数合成到面板底色；下划线固定 #7BDCE8。
# - 图片配色修订：整个文字面板改为 #292A39，单词悬停/选中为 #E6DCFF，取消叠印加粗。
# - 保留原有浅紫语法背景、青蓝下划线与静止粗体字重。
# - 反馈修订：下划线加粗到 3px，回退单词变色；各层仅移动自身装饰及文字。
# - 句法移动填充和轮廓；词块移动下划线；单词不牵动背景或下划线。

# Demo 5.0.6 — Qt 半透明字幕悬浮窗
# - 使用 PySide6，与 4.2.2 相同的渐变、背景 alpha、默认不透明度和圆角。
# - 悬浮窗只显示返回文本；主窗口保留输入、提示词、请求、结构数据与条目定位。
# - 原文 #F5F6FA，句法 rgba(154,132,255,0.20) 圆角块，下划线 #7BDCE8 / 3px。
# - 同一 QTextLayout 负责静止、悬停与命中；1px 动画不改变排版，装饰按层独立移动。
# - 修订：背景先画、下划线后画；按 4.2.2 的 14pt Medium 字体及字幕区域水平/垂直居中。
# Demo 5.0.7 — 单词常态配色、稳定窗高与点击解释
# - 单词首次渲染即使用 #E6DCFF 粗体；其他标注颜色保持指定值。
# - 返回文本时只按需增高，不自动缩小当前窗口；解释区位于字幕下方。
# - 同一次 API 请求返回每项简短中文 explanation，点击本地展示，不再次请求。
# - 提示词修订：同层禁止重叠、跨层仅保留独立学习点；引用最小完整范围，标签与解释对应原句。
# - 语境修订：不擅自套用专门义项或缩窄群体范围，优先可复用搭配；下划线悬停保持 3px。
# Demo 5.0.8 — 分类别深度解释
# - 单词采用生成式词典条目：音标、词性、用法、本句义、搭配、例句及分列的其他常见义。
# - 表达解释可复用结构、适用条件与短例；句法区分结构身份、成分关系和语义/话语功能。
# - 保留原句证据约束和同层不重叠；不冒充词典原文，不编造义项编号或不确定的音标/用法。
# - explanation 仍为纯文本，使用分段小标题；每项上限 1000 字符，输出预算 8192 tokens。
# - 解释区增至 220px，超长内容可滚动；重复加载后展开不再累计增高，离线演示同步更新。
# Demo 5.0.9 — 中文双层提示词与按需解释
# - 第一层仅标注，第二层点击后发送原文和选中标注生成简短解释；两层提示词可独立编辑。
# - 标注/解释输出预算分别为 2048/768 tokens；解释建议 80–180 字符，硬上限 320。
# - 同一文本、条目、提示词和模型缓存解释，重复点击合并请求；新文本隔离旧响应。
# - 离线演示使用预置短解释，不联网；保留颜色、圆角、稳定窗高和动画。
# Demo 5.1.0 — 由 5.0.9 重命名，标注契约与显示切换
# - 第一层提示词按用户原文替换；取消条目数、标签长度与句法片段数上限。
# - 单词/词块必须单片段，同类条目不得重叠，保留完整词边界和结构校验。
# - 第一层输出预算调整为 4096 tokens；不完整响应仍拒绝应用。
# - 字幕按钮切换显示/关闭并同步文案；后台解释返回不重新打开已关闭字幕。
# - 提示词再修订：依据用户人工标注，以词汇/表达积累为中心；跨层独立筛选、边界服从学习点、提高句法门槛。
# Demo 5.1.1 — 检索基础、学习单位、显示范围分离
# - 第一层输出 category/base/unit/spans：基础数组用于检索，单位区分词义/结构，引用负责显示。
# - 四维价值筛选，未知掌握状态不推断；使用用户人工标注的少量正例校准，不将留白当负例。
# - 更新解析校验、列表、悬浮窗解释标题及第二层请求，保留两层请求和本地内存缓存。
# - 校验同层不重叠、单词单词形、句法不跨指定标点；离线演示同步迁移。
# - 本版仅实现需求1–4，未加入本地数据库、次数统计或自动掌握判断。
# Demo 5.1.2 — 请求透明展示与双配色预览
# - 界面显示第一/第二层最终 system、user 消息（含人工示例）及完整请求参数。
# - 待发送预览随输入更新；单独保留实际提交请求快照，缓存命中不伪装成发送。
# - 两套精确 RGBA 配色：浅紫或浅金单词，原文/语法背景/下划线相同，选择时实时预览。
# - 配色同步字幕与单词格式；密钥不进入请求体预览，快照仅保存在当前内存。
# Demo 5.1.3 — 系统示例与宽容解析
# - 人工标注正例移入第一层系统提示词，编辑区和完整请求均可查看。
# - 解析器只读取字段和定位原文，不裁决重叠、分类、片段数或句法边界，不拆分或改写。
# - 忽略额外字段；无法定位或缺少必要字段的条目整项跳过，保留原始 JSON 供检查。
# - 第二层允许额外字段与超长解释；完整可解析内容不因 finish_reason 单独被拒绝。
# - 本版后续修订：模型输出精简为 category/form/spans；句法额外返回标准英文 name。
# - 同步解释请求与离线数据；原形和引用按结构范围对应，解析器不二次分割。
# Demo 5.2.0 — 外置提示词与独立版本管理
# - 默认标注（含人工正例）及解释提示词分别存放于 Codeia/Prompts/annotation、explanation。
# - A/E 两条版本序列独立于程序版本；界面可选择、预览编辑、保存当前版本或另存新版本。
# - 切换时保留本次会话草稿；请求使用编辑器当前内容，完整请求与发送快照保持可见。
# - 后续修订：默认标注 An_Demo 5.2.0_02；支持 type/category/canonical/spans，保留 An_Demo 5.2.0_01 旧协议。
# - 子类与标准形式同步到列表、字幕详情及第二层请求；默认解释 Ex_Demo 5.2.0_02。
# - 仍仅按引用和 occurrence 定位，不裁剪、拆分或拒绝重叠标注。
# Demo 5.2.1 — 上下文定位
# - 默认 An_Demo 5.2.1_01 / Ex_Demo 5.2.1_01：text 唯一时直接定位，重复时使用唯一 context。
# - 不再依赖模型的 occurrence；上下文仅定位，不渲染，不裁剪或猜测歧义位置。
# - 无法定位的条目整项跳过，状态栏及提示显示原因；保留原始 JSON。
# - 后续修订：返回 JSON 可编辑，新增本地应用按钮，按当前英文输入重新定位渲染。
# - 应用失败保留原标注；成功清除旧解释缓存，隔离过期解释响应，不调用标注 API。
# Demo 5.2.2 — FAM 内联标注
# - 第一层返回 FAM 文本，按插入标记计算位置；逐字符校验原文保真。
# - W/E 每次独立，S 按 id 关联；支持跨层交叉，检查闭合及同层重叠。
# - 默认 A2.0.0 / Ex_Demo 5.3.0_01；手动编辑 FAM 渲染，解释仍使用结构化 JSON。
# Demo 5.3.0 — 由 5.2.2 重命名
# - 默认标注 An_Demo 5.3.0_01；移除配色选择与预览，单词固定浅金 RGBA(245,216,166,255)。
# - 表达结束标记恢复为 </@E>，严格拒绝 </@E1> 至 </@E6> 等带编号形式。
# - W 仅使用 </@W>，S 使用 </@S#id>，不提供结束标记的兼容分支。
# - 只兼容标记语法，不自动修改模型的类别、标准形式或引用范围。
# - 报错显示行列和附近片段；编辑区自动选中出错标记，未闭合时定位开始标记。
# - 第一层用户消息直接发送原文，移除 english JSON 包装；默认精简提示词 An_Demo 5.3.0_02。
# - 第二层仍发送结构化原文和选中标注，并启用 JSON 解释输出。
# Demo 5.3.1 — 所有层级统一实例 ID
# - 默认 An_Demo 5.3.1_01，起始声明 type/cat/canon，结束统一 </@id>；仅 syntax 可复用 ID。
# - 全局首次声明编号连续递增；跨层独立闭合，支持多片段及交叉。
# - 按标记计算原文范围；解释请求为所有层级携带实例 ID，保留手动渲染和错误定位。
# - 提示词统一命名为 An/Ex_Demo 适用版本_编号，更新默认引用与保存校验。
# Demo 5.4.0 — JSON 标注，复用 5.2.1 提示词与 text/context 定位
# - 保留 5.3.1 配色、交互、请求快照、解释缓存及失败保留旧标注。
# - 本地 JSON 重渲染；无法定位的条目整项跳过，显示诊断。
# Demo 5.4.1 — 按句分组，句内定位并映射回全文坐标
# Demo 5.4.2 — 句内范围标签与 JSON 属性记录
# - 默认 An_Demo 5.4.2_01，完整保存用户提供的提示词及分类快照。
# - sentences 使用 source/annotated/annotations；W/E/S 按句、按层独立编号。
# - 支持跨层交叉及 syntax 多片段；校验原文、闭合、ID、属性、边界与同层重叠。
# - 结构错误整次拒绝并保留旧标注；不根据模型语义自动修补范围或重新分类。
# - 第二层使用 Ex_Demo 5.4.2_01，接收句子、原始属性与程序解析的片段坐标。
# - 保留 JSON 编辑重渲染、请求快照、配色、解释缓存和过期响应隔离。
# - 离线演示采用用户提供的三句示范；不代表模型质量或词频判定已核验。
# - 后续修订：错误列表显示句序号、ID 与属性条目，点击精确定位 JSON 转义后的字符位置。
# - 每句收集首个结构错误；编辑返回文本后清除过期错误列表，重新应用重新校验。
# Demo 5.4.3 — 尽力解析、局部保留与可点击提醒
# - An_Demo 5.4.3_01 原样复制 5.4.2 当前默认文件，解释提示词继续使用 5.4.2。
# - 句子/条目独立解析；未知子类、编号顺序、同层重叠等可渲染问题仅提醒。
# - 无法可靠定位的句子或 ID 跳过，不猜测范围；JSON 语法损坏时保留旧标注。
# - 提醒保留句序号、ID、属性路径及标签字符位置，点击定位原始返回内容。
# - 离线演示更新：S1 连续覆盖 Only by ... can we，包含 E1 与 W1/W2；canonical 同步用户示例。
# - 兼容 Subjunctive 与旧名称；支持围栏/前后文字中的 JSON、损坏响应中的完整句对象。
# - 解析结果始终显示本次原文；没有可用标注时清空旧标注并仅提醒，不显示旧文本。
# - 元素表点击只高亮原始 JSON 的属性和所有对应片段，不触发字幕选中或解释。
# - 高亮按字段路径与转义位置映射；编辑返回文本后须重新应用，避免跳到过期位置。
"""FaintOCR Demo 5.4.3. Run with the project .venv Python (PySide6)."""
```

### FaintOCR Demo 5.5.0

```text
# -*- coding: utf-8 -*-
# Demo 5.5.0 — 5.4.3 的模块化等价入口（不集成 OCR）
# - 请求、提示词发现、宽容解析、JSON 位置、缓存及过期响应归 ia_learning_core/core.py。
# - QTextLayout 排版、标注绘制、悬停、命中检测归 ia_learning_core/view.py。
# - 本文件只保留调试 UI、提示词编辑、窗口容器、拖动与解释面板。
# - 原 5.4.3、4.2.2 与所有提示词正文保留，示例、协议、配色不变。
# - UI 通过 core.poll() 接收后台结果；共享核心不依赖 PySide6。
# - 有意偏离 5.4.3：标注输出预算 8192 → 16384 tokens、请求超时 60 → 180 秒。6000 字符原文实测输出
#   约 5.6k–8.2k tokens，8192 时会被截断（finish_reason=length）；截断时状态栏提示缩短原文。
```

### FaintOCR 4.2.2

```text
# coding=utf-8
# FaintOCR 4.2.2
### 解析代码的两个方法：从UI(用户点击)入手；从功能(哪里用到)入手
## 注意：该版本需要在python3.12下运行


# 4.0.0
# 新增首次欢迎页、聚焦式新手教程遮罩、悬浮球菜单引导与任务清单进度。
# 4.0.0b
# 修复新手教程语言同步、遮罩点击阻塞、引导卡片按钮位置、菜单控件合并介绍与拖动跟随。
# 4.0.0c
# 从欢迎页开始显示遮罩，遮罩拦截背景点击，进度面板显示动画状态并承载跳过按钮。
# 4.0.0d
# 恢复菜单控件逐个介绍，修正遮罩点击后的层级，并优化进度完成动画。
# 4.0.1
# 新手教程继续扩展至设置、依赖文件、OCR 模式与首次识别结果。
# 遮罩行为回滚到 4.0.0b：透明输入，不拦截点击，也不主动抬高前景窗口。
# 4.0.1c
# 基于 4.0.1 遮罩实现修正欢迎页下拉框、菜单悬停引导、设置面板聚焦与教程误点击锁定。
# 4.0.1d
# 修复设置面板教程阶段的层级闪动，并在高亮设置项前自动滚动到目标控件。
# 4.0.1e
# 改进教程动作提示、上一步状态回退、匹配数据生成流程，并避免 OCR 模式切换自动推进。
# 4.0.1f
# 设置面板教程改为仅由引导卡片推进，修正最终 OCR 聚焦、操作提示布局与设置面板误关闭。
# 4.0.1g
# 重写教程进度映射，优化任务完成勾选视觉，并让一键生成介绍直接由下一步推进。
# 4.0.2
# 合并教程准备数据任务，点击执行 OCR 即完成教程，并收紧教程期间的悬浮球与设置面板交互锁。
# 4.0.2b
# 修复教程点击设置按钮阶段的悬浮球菜单悬停光效。
# 4.1.0
# 为 Windows 任务栏图标设置进程 AppUserModelID。
# 4.1.0b (+Deepseek)(+Gemini)
# "class FaintOCRApplication": "def show": self.ball.show()
# 后添加了```
#         icon = QtGui.QIcon(str(RUNTIME_ICON_FILE))
#         if not icon.isNull():
#             self.ball.setWindowIcon(icon)
#             # 通过微调标志强制 Windows 刷新任务栏缓存（无副作用）
#             flags = self.ball.windowFlags()
#             self.ball.setWindowFlags(flags)
# ```解决了未正确在任务栏显示自定义图标的问题。
# 4.1.0c
# 添加了两处图标设置错误的I18n文本
# 调整了读取图标的位置和图标名称
# 4.1.1
# 更改了原神远程仓库的路径至2，并对应地更改了主分支名称由master改为main
# 现在检查本地文件过期时不再检查创建时间，避免了更新文件时可能发生的文件创建时间不更新导致重复判断过期；并调整了I18n文本以适配修改
# 4.2.0
# 将复制按钮移至字幕悬浮窗内部，在展开/收起按钮左侧依次排列复制、写入文件按钮。
# 新增手动追加当前字幕（含译文）到配置输出文件的功能，支持成功反馈及失败提示。
# 收起下拉区域后仍可复制或写入；状态文字为操作按钮预留空间。
# 源码模式的数据根目录固定到 Codeia，exe 模式仍使用 exe 所在目录。
# 透明度滑块右移至固定按钮左侧，移除原复制按钮留下的空位。
# 手动和自动保存统一写入数据根目录的 OCR_Results 文件夹，按本地日期分文件，跨午夜自动切换。
# 保存内容移除时间戳及分隔线；将完整 text 原样写入，再追加两个换行。
# 4.2.1
# 去重仅控制自动保存；自动复制对每次符合输出条件的结果执行，不受重复文本限制。
# 关闭自动保存时不更新去重记录；仅在匹配结果自动保存成功后更新，失败可重试。
# 恢复状态文字原始绘制区域（左右各留 31 像素），使其相对整个悬浮窗居中。
# 4.2.2
# 移除复制、保存按钮的鼠标悬停文字提示，保留按钮操作、悬停高亮和成功反馈。
```

## FaintOCR 兼容性审计

当前主程序的完整 I/O 清单、环境缺项及目录迁移影响见 [FaintOCR README](projects/faintocr/README.md)。FaintOCR 已通过当前虚拟环境中的实际窗口与 OCR 工作流检查，详情及验证边界见项目 README。

FaintOCR 源码运行数据位于项目 `runtime/`；打包运行数据默认位于 `%LOCALAPPDATA%/IA/FaintOCR/runtime/`，图标等只读资源从 `assets/` 加载。路径直接定义在 `main.py` 中，不提供环境变量覆盖。旧数据未迁移或删除；模型由当前 RapidOCR 引擎自行管理。图标来源及打包资源要求见项目 README。

FaintOCR 集成检查：`.venv\Scripts\python.exe -B tests/check_faintocr.py --native --capture`，使用临时配置和生成图像，测试原生 Qt、双引擎推理、后台 OCR 到字幕导出和 MSS 小区域抓取，不保存屏幕内容。首次缺少 OCR 模型时由 RapidOCR 自行下载。
