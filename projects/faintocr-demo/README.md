# FaintOCR Demo

`main.py` 是当前运行入口，使用公共 `ia_learning_core.core` 和 `ia_learning_core.view`。提示词编辑器 `PromptEditor` 定义在本入口内，属于 Demo 界面，不属于公共包。

5.4.3 是外部历史对照文件，不保存在本项目中，也不是公共包调用方。对照测试通过 `FAINTOCR_REFERENCE_PATH` 指定其路径，见根目录 README.md。

5.5.0 直接读取公共包的 `prompts/annotation.txt` 和 `prompts/explanation.txt`，支持编辑、保存和重新加载，不扫描版本。

从工作区根目录运行：

```powershell
.venv\Scripts\python.exe projects/faintocr-demo/main.py
```

已在 Python 3.14.10 和项目 requirements.txt 中锁定的 PySide6 下通过 Qt 离屏启动、窗口绘制、离线标注、提示词编辑及模拟网络流程测试。真实 API 调用及实际鼠标拖动未验证。

密钥由公共核心直接读取根目录 `deepseek_api_key.json` 中的 `api_key`，界面可输入临时密钥，留空时读取配置文件。该文件被 Git 忽略，填写后即可发起请求。
