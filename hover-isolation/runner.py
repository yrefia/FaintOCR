"""Offline 2x2 comparison; snapshots are never edited in place."""
from pathlib import Path
import json
import sys
import time

ROOT = Path(__file__).resolve().parent
SNAP = ROOT / 'snapshots'
sys.path.insert(0, str(SNAP))

from PySide6.QtCore import QTimer, QVariantAnimation, QEasingCurve, Qt
from PySide6.QtGui import QPainterPath, QPainter, QTextLayout
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QDoubleSpinBox, QFormLayout, QSlider, QHBoxLayout, QGroupBox, QScrollArea
from ia_learning_core import core

DATA = json.loads((ROOT / 'demo-annotations.json').read_text(encoding='utf-8'))
TEXT = ' '.join(sentence['source'] for sentence in DATA['sentences'])
FORMULAS = {
    'Linear': 'f(t) = t',
    'InCubic': 'f(t) = t³',
    'OutCubic': 'f(t) = 1 − (1 − t)³',
    'InOutCubic': 't < ½: 4t³；否则: 1 − (−2t + 2)³/2',
    'OutQuad': 'f(t) = 1 − (1 − t)²',
    'OutSine': 'f(t) = sin(πt/2)',
    'OutExpo': 't = 1: 1；否则: 1 − 2^(−10t)',
    'OutBack': 'u=t−1，s=1.70158；f(t)=1+(s+1)u³+su²',
    'OutBounce': 'n=7.5625，d=2.75\nt<1/d: nt²\nt<2/d: n(t−1.5/d)²+0.75\nt<2.5/d: n(t−2.25/d)²+0.9375\n否则: n(t−2.625/d)²+0.984375',
    'OutElastic': 't=0: 0；t=1: 1；否则:\nf(t)=2^(−10t) sin((t−0.075)·2π/0.3)+1',
}


def load(path, source=None):
    ns = {'__file__': str(path), '__name__': 'isolation_' + path.stem}
    exec(compile(source or path.read_text(encoding='utf-8-sig'), str(path), 'exec'), ns)
    return ns


class OutlineLayout:
    """Delegate shaping/geometry; cache shaped glyph outlines and format colors."""
    def __init__(self, layout):
        self.layout = layout
        self.paths = []
        formats = layout.formats()
        for run in layout.glyphRuns(0, -1, QTextLayout.GlyphRunRetrievalFlag.RetrieveAll):
            raw = run.rawFont()
            for glyph, position, index in zip(run.glyphIndexes(), run.positions(), run.stringIndexes()):
                brush = None
                for part in formats:
                    if part.start <= index < part.start + part.length:
                        brush = part.format.foreground()
                path = raw.pathForGlyph(glyph).translated(position)
                self.paths.append((path, brush))

    def __getattr__(self, name):
        return getattr(self.layout, name)

    def draw(self, painter, position):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(position)
        for path, brush in self.paths:
            painter.fillPath(path, brush if brush is not None else painter.pen().brush())
        painter.restore()


class WallClockTimer(QTimer):
    """The old 16ms timer and monotonic-clock cubic curve."""
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setInterval(16)
        self.timeout.connect(self.tick)

    def start(self):
        self.started = time.monotonic()
        super().start()

    def tick(self):
        progress = 1 if self.duration == 0 else min(1, (time.monotonic() - self.started) / (self.duration / 1000))
        self.owner._set_lift(self.height * self.curve.valueForProgress(progress))
        if progress >= 1:
            self.stop()


def create_test(version, timing, height, curve, frames, duration, rendering="native"):
    started = time.perf_counter()

    def probe(base):
        class Probe(base):
            def relayout(self):
                super().relayout()
                if rendering == 'outline':
                    attr = 'layout' if version == '5.4.3' else 'text_layout'
                    current = getattr(self, attr)
                    if current is not None:
                        setattr(self, attr, OutlineLayout(current))

            def focus(self, number):
                super().focus(number)
                if duration == 0 and number is not None:
                    driver = self.timer if version == '5.4.3' else self.lift_animation
                    driver.stop()
                    self.lift = height
                    self.update()

            def animate(self):
                progress = 1 if duration == 0 else min(1, (time.monotonic() - self.started) / (duration / 1000))
                self.lift = height * curve.valueForProgress(progress)
                if progress >= 1:
                    self.timer.stop()
                self.update()

            def paintEvent(self, event):
                frames.append({'ms': (time.perf_counter() - started) * 1000,
                               'lift': float(self.lift), 'hovered': self.hovered,
                               'size': [self.width(), self.height()]})
                super().paintEvent(event)
        return Probe

    if version == '5.4.3':
        ns = load(SNAP / 'old.py')
        base = ns['SubtitleWindow']
        if timing == 'QVariantAnimation':
            class Swapped(base):
                def __init__(self):
                    super().__init__()
                    self.timer.stop()
                    self.timer.deleteLater()
                    self.timer = QVariantAnimation(self)
                    self.timer.setStartValue(0.0)
                    self.timer.setEndValue(1.0)
                    self.timer.setDuration(140)
                    self.timer.setEasingCurve(QEasingCurve.OutCubic)
                    self.timer.valueChanged.connect(self.set_lift)

                def set_lift(self, value):
                    self.lift = value
                    self.update()
            base = Swapped
        window = probe(base)()
        view = window
    else:
        ns = load(SNAP / 'new.py')
        base = ns['AnnotatedTextView']
        if timing == 'QTimer':
            class Swapped(base):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.lift_animation.stop()
                    self.lift_animation.deleteLater()
                    self.lift_animation = WallClockTimer(self)
            base = Swapped
        ns['AnnotatedTextView'] = probe(base)
        window = ns['SubtitleWindow']()
        view = window.view

    driver = view.timer if version == '5.4.3' else view.lift_animation
    if isinstance(driver, QVariantAnimation):
        driver.setDuration(duration)
        driver.setEndValue(float(height))
        driver.setEasingCurve(curve)
    elif isinstance(driver, WallClockTimer):
        driver.duration = duration
        driver.height = height
        driver.curve = curve

    items = core.resolve_items(DATA, TEXT)
    view.replay_target = next((i for i, item in enumerate(items) if any(TEXT[a:b] == 'be' for a, b in item['ranges'])), 0)
    window.resize(1500, 850)
    window.set_content(TEXT, items)
    window.resize(1500, 850)
    window.move(100, 180)
    window.setWindowTitle(version + '+' + timing + ' / ' + rendering)
    window.show()

    return window, view


def run(version='5.4.3', timing='QTimer'):
    app = QApplication.instance() or QApplication(sys.argv)
    panel = QWidget()
    panel.setWindowTitle('上浮动画交叉隔离测试')
    outer = QVBoxLayout(panel)
    outer.setContentsMargins(16, 16, 16, 16)
    heading = QLabel('上浮动画 · 对照实验')
    heading.setStyleSheet('font-size: 20px; font-weight: 600;')
    outer.addWidget(heading)
    intro = QLabel('选择版本与绘制方式，再调整动画参数。重播时请将鼠标留在控制窗。')
    intro.setWordWrap(True)
    outer.addWidget(intro)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.NoFrame)
    body = QWidget()
    scroll.setWidget(body)
    outer.addWidget(scroll)
    layout = QVBoxLayout(body)
    layout.setContentsMargins(0, 8, 8, 8)
    layout.setSpacing(14)
    def section(title):
        group = QGroupBox(title)
        group.setStyleSheet('QGroupBox { font-weight: 600; }')
        inner = QVBoxLayout(group)
        inner.setContentsMargins(12, 18, 12, 12)
        inner.setSpacing(10)
        layout.addWidget(group)
        return inner
    selection = section('版本与绘制')
    form = QFormLayout()
    form.setHorizontalSpacing(16)
    form.setVerticalSpacing(10)
    selection.addLayout(form)
    versions = QComboBox()
    variants = [(v, t) for v in ('5.4.3', '5.5.0') for t in ('QTimer', 'QVariantAnimation')]
    versions.addItems([v + '+' + t for v, t in variants])
    versions.setCurrentIndex(variants.index((version, timing)))
    form.addRow('测试版本', versions)
    rendering = QComboBox()
    rendering.addItem('原始文字绘制（QTextLayout.draw）', 'native')
    rendering.addItem('字形轮廓绘制（QRawFont → QPainterPath）', 'outline')
    form.addRow('文字绘制方式', rendering)
    technology = QLabel()
    technology.setWordWrap(True)
    technology.setTextInteractionFlags(Qt.TextSelectableByMouse)
    selection.addWidget(technology)
    animation = section('动画参数')
    form = QFormLayout()
    form.setHorizontalSpacing(16)
    form.setVerticalSpacing(12)
    animation.addLayout(form)

    def slider_row(title, maximum, initial, suffix):
        row = QWidget()
        box = QHBoxLayout(row)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(12)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, maximum)
        slider.setValue(initial)
        slider.setTracking(False)
        value = QDoubleSpinBox()
        value.setMinimumWidth(112)
        value.setDecimals(0)
        value.setRange(0, maximum)
        value.setValue(initial)
        value.setSuffix(suffix)
        slider.valueChanged.connect(value.setValue)
        value.valueChanged.connect(lambda v: slider.setValue(int(v)))
        box.addWidget(slider)
        box.addWidget(value)
        form.addRow(title, row)
        return slider
    height = slider_row('上浮高度', 300, 1, ' px')
    duration = slider_row('上浮总时间', 6000, 140, ' ms')
    curves = QComboBox()
    names = ['OutCubic', 'Linear', 'InCubic', 'InOutCubic', 'OutQuad', 'OutSine', 'OutExpo', 'OutBack', 'OutBounce', 'OutElastic']
    curves.addItems(names)
    form.addRow('缓动曲线', curves)
    limits = QLabel('高度 0–300px · 时长 0–6000ms（0ms 立即到达终点）\n滑块释放后应用；切换参数会保存记录并重建悬浮窗。')
    limits.setWordWrap(True)
    animation.addWidget(limits)
    math_section = section('缓动公式')
    formula = QLabel()
    formula.setWordWrap(True)
    formula.setTextInteractionFlags(Qt.TextSelectableByMouse)
    formula.setStyleSheet('padding: 8px; font-size: 13px;')
    math_section.addWidget(formula)
    note = QLabel('OutBack / OutElastic 可能超出设定高度；OutBounce 会回弹。')
    note.setWordWrap(True)
    math_section.addWidget(note)
    layout.addStretch()
    replay = QPushButton('重播 be 上浮（固定目标）')
    save = QPushButton('保存帧记录')
    toggle_window = QPushButton('关闭悬浮窗')
    status = QLabel()
    actions = QHBoxLayout()
    for widget in (replay, save, toggle_window):
        widget.setMinimumHeight(34)
        actions.addWidget(widget)
    outer.addLayout(actions)
    status.setWordWrap(True)
    outer.addWidget(status)
    state = {}

    def save_frames():
        if not state:
            return
        destination = ROOT / (state['version'] + '+' + state['timing'] + '+' + state['rendering'] + '-frames.json')
        payload = {key: state[key] for key in ('version', 'timing', 'height', 'curve', 'rendering', 'frames')}
        payload['duration_ms'] = state['duration']
        destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        status.setText(f"已保存 {len(state['frames'])} 帧：{destination.name}")

    def rebuild():
        position = None
        if state:
            save_frames()
            position = state['window'].pos()
            state['window'].close()
            state['window'].deleteLater()
        v, t = variants[versions.currentIndex()]
        frames = []
        window, view = create_test(v, t, height.value(), QEasingCurve(getattr(QEasingCurve, curves.currentText())), frames, duration.value(), rendering.currentData())
        if position is not None:
            window.move(position)
        state.update(window=window, view=view, frames=frames, version=v, timing=t,
                     height=height.value(), curve=curves.currentText(), duration=duration.value(), rendering=rendering.currentData())
        shell = ('5.4.3：顶层 SubtitleWindow 直接绘制文字与标注。' if v == '5.4.3'
                 else '5.5.0：SubtitleWindow 外壳 + AnnotatedTextView 子视图绘制。')
        clock = ('QTimer：16ms timeout，time.monotonic 测量经过时间，QEasingCurve 求位移。' if t == 'QTimer'
                 else 'QVariantAnimation：Qt 动画时钟推进，QEasingCurve 插值，valueChanged 更新位移。')
        paint = ('原始：QTextLayout 完成排版并直接绘制字形；背景为抗锯齿几何图形。纵向小数位移可能阶梯化。'
                 if rendering.currentData() == 'native' else
                 '轮廓：QTextLayout 排版 → glyphRuns 保留字形与位置 → QRawFont.pathForGlyph 缓存轮廓 → QPainter.fillPath 抗锯齿绘制。静止与动画文字统一使用轮廓，保留加粗和颜色；锐利度可能不同，首次布局成本更高。背景和裁剪仍使用原实现。')
        technology.setText('<b>窗口结构</b><br>' + shell + '<br><br><b>动画计时</b><br>' + clock + '<br><br><b>文字渲染</b><br>' + paint)
        formula.setText('t∈[0,1]；上浮位移 = 高度 × f(t)\n' + FORMULAS[curves.currentText()])
        status.setText('当前：' + v + '+' + t)
        toggle_window.setText('关闭悬浮窗')
        replay.setEnabled(True)

    def replay_animation():
        state['view'].focus(None)
        state['view'].focus(state['view'].replay_target)

    def toggle_floating_window():
        if state['window'].isVisible():
            state['view'].focus(None)
            save_frames()
            state['window'].close()
            toggle_window.setText('打开悬浮窗')
            replay.setEnabled(False)
        else:
            state['window'].show()
            toggle_window.setText('关闭悬浮窗')
            replay.setEnabled(True)

    toggle_window.clicked.connect(toggle_floating_window)
    versions.currentIndexChanged.connect(rebuild)
    height.valueChanged.connect(rebuild)
    duration.valueChanged.connect(rebuild)
    curves.currentIndexChanged.connect(rebuild)
    rendering.currentIndexChanged.connect(rebuild)
    replay.clicked.connect(replay_animation)
    save.clicked.connect(save_frames)
    rebuild()
    panel.resize(760, 860)
    panel.move(20, 20)
    panel.show()
    def shutdown(event):
        save_frames()
        state['window'].close()
        event.accept()
    panel.closeEvent = shutdown
    if '--smoke' in sys.argv:
        from PySide6.QtTest import QTest
        for index in range(4):
            versions.setCurrentIndex(index)
            for name in ('OutCubic', 'Linear', 'OutBack'):
                curves.setCurrentText(name)
                height.setValue(5)
                app.processEvents()
                QTest.qWait(60)
                replay_animation()
                QTest.qWait(250)
                assert abs(state['view'].lift - 5) < 1e-6, state['view'].lift
                state['view'].focus(None)
                assert state['view'].lift == 0
        for render_index in range(2):
            rendering.setCurrentIndex(render_index)
            for version_index in range(4):
                versions.setCurrentIndex(version_index)
                app.processEvents()
                QTest.qWait(60)
                replay_animation()
                QTest.qWait(250)
                assert abs(state['view'].lift - 5) < 1e-6
                if render_index:
                    target_layout = state['view'].layout if state['version'] == '5.4.3' else state['view'].text_layout
                    assert isinstance(target_layout, OutlineLayout) and target_layout.paths
                    assert any(brush is not None for _, brush in target_layout.paths)
        duration.setValue(0)
        height.setValue(300)
        for index in range(4):
            versions.setCurrentIndex(index)
            replay_animation()
            assert state['view'].lift == 300
        duration.setValue(6000)
        replay_animation()
        QTest.qWait(100)
        assert 0 <= state['view'].lift < 300
        toggle_floating_window()
        assert not state['window'].isVisible() and panel.isVisible()
        toggle_floating_window()
        assert state['window'].isVisible()
        print('PASS: all four variants, three curves, 5px endpoint and reset')
        panel.close()
        return
    sys.exit(app.exec())


if __name__ == '__main__':
    run()
