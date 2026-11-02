# 上浮动画交叉隔离测试

在仓库根目录运行 PowerShell：

```powershell
$env:QT_QPA_PLATFORM = 'windows'
& '.\.venv\Scripts\python.exe' '.\hover-isolation\runner.py'
```

统一控制窗提供 5.4.3 / 5.5.0 绘制结构与 QTimer / QVariantAnimation 的四种组合。
上浮高度为 0–400 逻辑像素，时长为 0–10000ms，0ms 立即到达终点。
默认 1px、140ms、OutCubic；QTimer 间隔 16ms。曲线选择下方显示公式。
滑块释放后应用参数，也可直接输入数值。切换参数会重建测试窗口并重置记录。
演示窗为 1500×850，使用 demo-annotations.json 中用户提供的完整文本和标注。
鼠标移入标注观察，或将鼠标留在控制窗并点击“重播 be 上浮”。

## 保存帧记录

保存当前版本从创建以来的 paintEvent 入口记录到 `<版本>+<计时方式>-frames.json`。
JSON 包含版本、高度、曲线、时长，以及每次绘制的相对时间 ms、上浮量 lift、
悬停目标 hovered、视图尺寸 size。切换设置和关闭控制窗也会自动保存；同名文件覆盖。
如需比较不同参数，请先另存生成的 JSON。生成记录不纳入 Git。

记录可用于比较绘制间隔是否有明显空档、上浮量是否跳变、目标或视图尺寸是否改变。
记录包含静止期和重播，不只有动画帧；分析时应截取同一次动画的时间段。
它记录应用绘制事件，不是显示器实际呈现时间，也没有分别记录文字和标注的像素位置，
因此不能独自证明画面流畅或两者同步，需要结合实际观察或录屏。

## 文件与隔离边界

- runner.py：统一入口、参数控件、计时替换和帧记录。
- demo-annotations.json：演示文本与标注数据。
- snapshots/：创建隔离实验时保存的旧版和新版源码及加载依赖。

快照不跟随主程序更新，5.5.0 快照也不等于现在已经回退动画的主程序。
没有 API 请求；未复现完整 Demo 的网络与后台工作负载。
QTimer 测试包装通过 QEasingCurve.valueForProgress 求值；默认 OutCubic 与旧公式
数学等价，但包装代码并非逐字相同。OutBack / OutElastic 可能超调，OutBounce 会回弹。
上浮距离很大时可能越过视图边界而被裁剪，这是保留原绘制结构时的行为。

离屏检查（验证逻辑，不验证屏幕流畅度）：

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
& '.\.venv\Scripts\python.exe' '-B' '.\hover-isolation\runner.py' '--smoke'
```
