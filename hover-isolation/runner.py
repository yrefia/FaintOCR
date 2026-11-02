"""Offline 2x2 comparison; snapshots are never edited in place."""
from pathlib import Path
import json
import sys
import time
import inspect
import textwrap

ROOT = Path(__file__).resolve().parent
SNAP = ROOT / 'snapshots'
sys.path.insert(0, str(SNAP))

from PySide6.QtCore import QTimer, QVariantAnimation, QEasingCurve, Qt, QPointF
from PySide6.QtGui import QPainter, QTextLayout, QPainterPath, QColor
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


def create_test(version, timing, height, curve, frames, duration, rendering="native", exit_curve=None, exit_duration=140):
    started = time.perf_counter()

    def probe(base):
        # Adapt the snapshot's decoration/shell painter without editing the snapshot.
        source = textwrap.dedent(inspect.getsource(base.paintEvent))
        source = source.replace('shift = -self.lift if self.hovered == number else 0',
                                'shift = -self.lifts.get(number, 0)')
        begin = source.index('    if self.' + ('layout' if version == '5.4.3' else 'text_layout') + ':')
        end = source.index('    p.end()', begin)
        source = source[:begin] + '    self._draw_moving_text(p, viewport)\n' + source[end:]
        scope = dict(base.paintEvent.__globals__)
        exec(compile(source, '<isolation-multiple-target-painter>', 'exec'), scope)
        paint_snapshot = scope['paintEvent']

        class Probe(base):
            def __init__(self, *args, **kwargs):
                self.lifts = {}
                self.motions = {}
                super().__init__(*args, **kwargs)

            def relayout(self):
                self.reset_hover()
                super().relayout()
                if rendering == 'outline':
                    attr = 'layout' if version == '5.4.3' else 'text_layout'
                    current = getattr(self, attr)
                    if current is not None:
                        setattr(self, attr, OutlineLayout(current))

            def _stop_motion(self, number):
                motion = self.motions.pop(number, None)
                if motion:
                    motion['driver'].stop()
                    motion['driver'].deleteLater()

            def reset_hover(self):
                for number in list(self.motions):
                    self._stop_motion(number)
                self.lifts.clear()
                self.hovered = None
                self.lift = 0
                self.update()

            def _move_to(self, number, goal, milliseconds, easing):
                initial = self.lifts.get(number, 0.0)
                self._stop_motion(number)
                if milliseconds == 0 or easing is None or initial == goal:
                    self._finish(number, goal)
                    return
                self.lifts[number] = initial
                start = time.monotonic()
                def value(progress):
                    self.lifts[number] = initial + (goal - initial) * progress
                    self.lift = self.lifts.get(self.hovered, 0.0)
                    self.update()
                if timing == 'QTimer':
                    driver = QTimer(self)
                    driver.setInterval(16)
                    def tick():
                        progress = min(1, (time.monotonic() - start) * 1000 / milliseconds)
                        value(easing.valueForProgress(progress))
                        if progress >= 1:
                            self._finish(number, goal)
                    driver.timeout.connect(tick)
                else:
                    driver = QVariantAnimation(self)
                    driver.setStartValue(0.0)
                    driver.setEndValue(1.0)
                    driver.setDuration(milliseconds)
                    driver.setEasingCurve(easing)
                    driver.valueChanged.connect(value)
                    driver.finished.connect(lambda: self._finish(number, goal))
                self.motions[number] = {'driver': driver, 'goal': goal}
                driver.start()

            def _finish(self, number, goal):
                self._stop_motion(number)
                if goal == 0 and number != self.hovered:
                    self.lifts.pop(number, None)
                else:
                    self.lifts[number] = goal
                self.lift = self.lifts.get(self.hovered, 0.0)
                self.update()

            def focus(self, number):
                if number == self.hovered:
                    return
                previous = self.hovered
                self.hovered = number
                if previous is not None:
                    self._move_to(previous, 0.0, exit_duration, exit_curve)
                if number is not None:
                    self._move_to(number, float(height), duration, curve)
                self.lift = self.lifts.get(number, 0.0)
                self.setCursor(Qt.PointingHandCursor if number is not None else Qt.ArrowCursor)
                self.update()

            def _draw_moving_text(self, painter, viewport):
                text_layout = self.layout if version == '5.4.3' else self.text_layout
                if not text_layout:
                    return
                origin = QPointF(31 if version == '5.4.3' else self.MARGIN_X, self.text_top()-self.scroll)
                # Shared glyphs must not be duplicated by overlapping annotations.
                # The actual hovered target wins, then the newest active target.
                order = list(reversed(self.lifts))
                if self.hovered in order:
                    order.remove(self.hovered)
                    order.insert(0, self.hovered)
                claimed = QPainterPath()
                targets = []
                for number in order:
                    target = QPainterPath()
                    for rect in self.rects[number]:
                        part = QPainterPath()
                        part.addRect(self.displayed_rect(rect))
                        target = target.united(part)
                    targets.append((number, target.subtracted(claimed)))
                    claimed = claimed.united(target)
                all_text = QPainterPath()
                all_text.addRect(viewport)
                painter.setPen(QColor(245, 246, 250, 255))
                painter.save()
                painter.setClipPath(all_text.subtracted(claimed), Qt.IntersectClip)
                text_layout.draw(painter, origin)
                painter.restore()
                for number, target in targets:
                    painter.save()
                    painter.translate(0, -self.lifts[number])
                    painter.setClipPath(target, Qt.IntersectClip)
                    text_layout.draw(painter, origin)
                    painter.restore()

            def paintEvent(self, event):
                frames.append({'ms': (time.perf_counter() - started) * 1000,
                               'lift': float(self.lift), 'hovered': self.hovered,
                               'lifts': dict(self.lifts),
                               'goals': {n: m['goal'] for n, m in self.motions.items()},
                               'size': [self.width(), self.height()]})
                paint_snapshot(self, event)
        return Probe

    if version == '5.4.3':
        ns = load(SNAP / 'old.py')
        base = ns['SubtitleWindow']
        window = probe(base)()
        view = window
    else:
        ns = load(SNAP / 'new.py')
        base = ns['AnnotatedTextView']
        ns['AnnotatedTextView'] = probe(base)
        window = ns['SubtitleWindow']()
        view = window.view

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
    duration = slider_row('进入时长', 6000, 140, ' ms')
    exit_time = slider_row('退出时长', 6000, 140, ' ms')
    curves = QComboBox()
    names = ['OutCubic', 'Linear', 'InCubic', 'InOutCubic', 'OutQuad', 'OutSine', 'OutExpo', 'OutBack', 'OutBounce', 'OutElastic']
    curves.addItems(names)
    form.addRow('进入缓动', curves)
    exit_curves = QComboBox()
    exit_curves.addItem('无（立即复位）', None)
    for name in names:
        exit_curves.addItem(name, name)
    form.addRow('退出缓动', exit_curves)
    exit_note = QLabel('退出默认立即复位。进入和退出各有独立时长，均从当前位移接续。\n每个标注独立运行；方向改变时位置连续，但速度可能变化。')
    exit_note.setWordWrap(True)
    animation.addWidget(exit_note)
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
    leave = QPushButton('退出悬停')
    save = QPushButton('保存帧记录')
    toggle_window = QPushButton('关闭悬浮窗')
    status = QLabel()
    actions = QHBoxLayout()
    for widget in (replay, leave, save, toggle_window):
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
        payload = {key: state[key] for key in ('version', 'timing', 'height', 'curve', 'rendering', 'exit_curve', 'exit_duration_ms', 'frames')}
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
        window, view = create_test(v, t, height.value(), QEasingCurve(getattr(QEasingCurve, curves.currentText())), frames, duration.value(), rendering.currentData(),
                                   QEasingCurve(getattr(QEasingCurve, exit_curves.currentData())) if exit_curves.currentData() else None, exit_time.value())
        if position is not None:
            window.move(position)
        state.update(window=window, view=view, frames=frames, version=v, timing=t,
                     height=height.value(), curve=curves.currentText(), duration=duration.value(), rendering=rendering.currentData(), exit_curve=exit_curves.currentData(), exit_duration_ms=exit_time.value())
        shell = ('5.4.3：顶层 SubtitleWindow 直接绘制文字与标注。' if v == '5.4.3'
                 else '5.5.0：SubtitleWindow 外壳 + AnnotatedTextView 子视图绘制。')
        clock = ('每个标注独立运行。QTimer：16ms timeout，time.monotonic 测量经过时间，QEasingCurve 求位移。' if t == 'QTimer'
                 else '每个标注独立运行。QVariantAnimation：Qt 动画时钟推进，QEasingCurve 插值，valueChanged 更新位移。')
        paint = ('原始：QTextLayout 完成排版并直接绘制字形；背景为抗锯齿几何图形。纵向小数位移可能阶梯化。'
                 if rendering.currentData() == 'native' else
                 '轮廓：QTextLayout 排版 → glyphRuns 保留字形与位置 → QRawFont.pathForGlyph 缓存轮廓 → QPainter.fillPath 抗锯齿绘制。静止与动画文字统一使用轮廓，保留加粗和颜色；锐利度可能不同，首次布局成本更高。背景和裁剪仍使用原实现。')
        technology.setText('<b>窗口结构</b><br>' + shell + '<br><br><b>动画计时</b><br>' + clock + '<br><br><b>文字渲染</b><br>' + paint)
        formula.setText('t∈[0,1]；进入位移 = 起始位移 + (高度 − 起始位移) × f(t)\n' + FORMULAS[curves.currentText()])
        formula.setText(formula.text() + ('\n\n退出：立即复位' if exit_curves.currentData() is None else '\n\n退出位移 = 离开时高度 × [1 − f(t)]\n' + FORMULAS[exit_curves.currentData()]))
        status.setText('当前：' + v + '+' + t)
        toggle_window.setText('关闭悬浮窗')
        replay.setEnabled(True)
        leave.setEnabled(True)

    def replay_animation():
        state['view'].reset_hover()
        state['view'].focus(state['view'].replay_target)

    def toggle_floating_window():
        if state['window'].isVisible():
            state['view'].reset_hover()
            save_frames()
            state['window'].close()
            toggle_window.setText('打开悬浮窗')
            replay.setEnabled(False)
            leave.setEnabled(False)
        else:
            state['window'].show()
            toggle_window.setText('关闭悬浮窗')
            replay.setEnabled(True)
            leave.setEnabled(True)

    toggle_window.clicked.connect(toggle_floating_window)
    versions.currentIndexChanged.connect(rebuild)
    height.valueChanged.connect(rebuild)
    duration.valueChanged.connect(rebuild)
    exit_time.valueChanged.connect(rebuild)
    curves.currentIndexChanged.connect(rebuild)
    rendering.currentIndexChanged.connect(rebuild)
    exit_curves.currentIndexChanged.connect(rebuild)
    leave.clicked.connect(lambda: state['view'].focus(None))
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
        duration.setValue(140)
        for index in range(4):
            versions.setCurrentIndex(index)
            for curve_index in range(1, exit_curves.count()):
                exit_curves.setCurrentIndex(curve_index)
                app.processEvents()
                QTest.qWait(60)
                replay_animation()
                QTest.qWait(220)
                view = state['view']
                view.focus(None)
                assert view.hovered is None and view.lifts[view.replay_target] == 5
                QTest.qWait(50)
                assert view.replay_target in view.motions
                QTest.qWait(180)
                assert view.hovered is None and view.lift == 0
                replay_animation()
                QTest.qWait(50)
                view.focus(None)
                view.focus(view.replay_target)
                assert view.motions[view.replay_target]['goal'] == 5
                view.reset_hover()
        duration.setValue(200)
        exit_time.setValue(400)
        exit_curves.setCurrentText('Linear')
        curves.setCurrentText('Linear')
        for index in range(4):
            versions.setCurrentIndex(index)
            app.processEvents()
            QTest.qWait(60)
            view = state['view']
            first = view.replay_target
            second = next(n for n in range(len(view.items)) if n != first)
            view.focus(first)
            QTest.qWait(80)
            before_exit = view.lifts[first]
            view.focus(second)
            assert view.lifts[first] == before_exit
            assert first in view.motions and second in view.motions
            QTest.qWait(60)
            before_enter = view.lifts[first]
            assert 0 < before_enter < before_exit
            view.focus(first)
            assert view.lifts[first] == before_enter
            assert first in view.motions and second in view.motions
            QTest.qWait(240)
            assert view.lifts[first] == 5
            assert second in view.motions  # exit uses 400ms, not the 200ms entry duration
            QTest.qWait(220)
            assert second not in view.lifts and first not in view.motions
            view.reset_hover()
        exit_curves.setCurrentIndex(0)
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
        print('PASS: four variants, entry/exit curves, re-entry, endpoints and reset')
        panel.close()
        return
    sys.exit(app.exec())


if __name__ == '__main__':
    run()
