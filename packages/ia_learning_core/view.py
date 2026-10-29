"""Embeddable Qt annotation view. No API calls, prompts or application window policy."""
from PySide6.QtCore import Qt, QRectF, QPointF, QEasingCurve, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTextLayout, QTextOption, QTextCharFormat, QPainterPath
from PySide6.QtWidgets import QWidget

from .core import LAYER_KEYS, utf16_offsets

PALETTE = {'original':(245,246,250,255), 'grammar':(154,132,255,51), 'phrase':(123,220,232,255), 'word':(245,216,166,255)}
LAYERS = set(LAYER_KEYS.values())
# 背景先画、下划线后画，与 API 返回的条目顺序无关。
PAINT_ORDER = {'grammar': 0, 'phrase': 1, 'word': 2}

def rgba(value, alpha=255):
    result = QColor(value)
    result.setAlpha(alpha)
    return result

class AnnotatedTextView(QWidget):
    annotation_clicked = Signal(int)
    # 文字区内边距；外壳通过 preferred_height() 取高度，不必知道这些数字。
    MARGIN_X, MARGIN_TOP, MARGIN_BOTTOM = 31, 24, 42

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.source, self.items = '', []
        self.enabled = set(LAYERS)
        self.hovered = None
        self.scroll = self.lift = 0
        self.text_layout = None
        self.rects = []
        self.content_height = 0
        # 悬停条目在 140ms 内上浮 1px（OutCubic）。
        self.lift_animation = QVariantAnimation(self)
        self.lift_animation.setStartValue(0.0)
        self.lift_animation.setEndValue(1.0)
        self.lift_animation.setDuration(140)
        self.lift_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.lift_animation.valueChanged.connect(self._set_lift)
        self.text_font = QFont('Microsoft YaHei UI', 14, QFont.Medium)
        self.relayout()

    def set_content(self, source, items, enabled=None):
        self.source, self.items = source, items
        self.enabled = set(LAYERS) if enabled is None else set(enabled)
        self.hovered = None
        self.lift_animation.stop()
        self.lift = self.scroll = 0
        self.relayout()
        self.update()

    def set_font_size(self, size):
        self.text_font.setPointSizeF(float(size))
        self.relayout()
        self.update()

    def set_enabled_layers(self, layers):
        self.set_content(self.source, self.items, layers)

    def text_area(self):
        return QRectF(self.MARGIN_X, self.MARGIN_TOP, self.width()-2*self.MARGIN_X,
                      max(50, self.height()-self.MARGIN_TOP-self.MARGIN_BOTTOM))

    def preferred_height(self):
        """Widget height that shows the laid-out text without scrolling."""
        return int(self.content_height + self.MARGIN_TOP + self.MARGIN_BOTTOM)

    def resizeEvent(self, event):
        self.hovered = None
        self.lift = 0
        self.lift_animation.stop()
        self.relayout()
        super().resizeEvent(event)

    def relayout(self):
        # Qt offsets use UTF-16; source ranges use Python Unicode code points.
        offsets = utf16_offsets(self.source)
        self.text_layout = QTextLayout(self.source.replace('\n', '\u2028'), self.text_font)
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        option.setAlignment(Qt.AlignHCenter)
        self.text_layout.setTextOption(option)
        formats = []
        for item in self.items:
            if item['category'] == 'word' and 'word' in self.enabled:
                for start, end in item['ranges']:
                    part = QTextLayout.FormatRange()
                    part.start, part.length = offsets[start], offsets[end]-offsets[start]
                    part.format = QTextCharFormat()
                    part.format.setFontWeight(QFont.Bold)
                    part.format.setForeground(QColor(*PALETTE['word']))
                    formats.append(part)
        self.text_layout.setFormats(formats)
        self.text_layout.beginLayout()
        y = 0
        while True:
            line = self.text_layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(max(50, self.width()-2*self.MARGIN_X))
            line.setPosition(QPointF(0, y))
            y += line.height()
        self.text_layout.endLayout()
        self.content_height = y
        self.scroll = min(self.scroll, max(0, y-self.text_area().height()))
        self.rects = [[] for _ in self.items]
        for number, item in enumerate(self.items):
            if item['category'] not in self.enabled:
                continue
            for start, end in item['ranges']:
                for n in range(self.text_layout.lineCount()):
                    line = self.text_layout.lineAt(n)
                    a, b = max(offsets[start], line.textStart()), min(offsets[end], line.textStart()+line.textLength())
                    if a < b:
                        x1, x2 = line.cursorToX(a)[0], line.cursorToX(b)[0]
                        self.rects[number].append(QRectF(self.MARGIN_X+x1, line.y(), max(1,x2-x1), line.height()))


    def text_top(self):
        return self.text_area().top() + max(0, (self.text_area().height()-self.content_height)/2)


    def displayed_rect(self, rect):
        return rect.translated(0, self.text_top()-self.scroll)


    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        viewport = self.text_area().adjusted(-6, -4, 6, 6)
        p.setClipRect(viewport)
        # Backgrounds always precede underlines, regardless of API item order.
        for number, item in sorted(enumerate(self.items), key=lambda pair: PAINT_ORDER[pair[1]['category']]):
            category = item['category']
            for original in self.rects[number]:
                rect = self.displayed_rect(original)
                shift = -self.lift if self.hovered == number else 0
                if category == 'grammar':
                    block = rect.adjusted(-3, -2, 3, 2).translated(0, shift)
                    p.setBrush(QColor(*PALETTE['grammar']))
                    p.setPen(QPen(rgba('#9A84FF', 150), 1) if self.hovered == number else QPen(Qt.NoPen))
                    p.drawRoundedRect(block, 7, 7)
                elif category == 'phrase':
                    a = QPointF(rect.left(), rect.bottom()-1+shift)
                    b = QPointF(rect.right(), rect.bottom()-1+shift)
                    p.setPen(QPen(QColor(*PALETTE['phrase']), 3, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(a,b)
        if self.text_layout:
            # Same shaped text/layout in both states; only the target clip translates.
            target = QPainterPath()
            if self.hovered is not None:
                for rect in self.rects[self.hovered]:
                    target.addRect(self.displayed_rect(rect))
            all_text = QPainterPath()
            all_text.addRect(viewport)
            p.setPen(QColor(*PALETTE['original']))
            p.save()
            p.setClipPath(all_text.subtracted(target), Qt.IntersectClip)
            self.text_layout.draw(p, QPointF(self.MARGIN_X, self.text_top()-self.scroll))
            p.restore()
            if not target.isEmpty():
                p.save()
                p.translate(0, -self.lift)
                p.setClipPath(target, Qt.IntersectClip)
                self.text_layout.draw(p, QPointF(self.MARGIN_X, self.text_top()-self.scroll))
                p.restore()
        p.end()


    def target_at(self, point):
        if not self.text_area().adjusted(-6, -4, 6, 6).contains(point):
            return None
        hits = []
        for number, rects in enumerate(self.rects):
            for raw in rects:
                rect = self.displayed_rect(raw)
                if rect.contains(point):
                    y = point.y()-rect.top()
                    order = ('phrase','word','grammar') if y >= rect.height()-6 else (('grammar','word','phrase') if y < 4 else ('word','phrase','grammar'))
                    hits.append((order.index(self.items[number]['category']), sum(b-a for a,b in self.items[number]['ranges']), number))
        return min(hits)[2] if hits else None


    def focus(self, number):
        if number != self.hovered:
            self.hovered, self.lift = number, 0
            self.lift_animation.stop()
            if number is not None:
                self.lift_animation.start()
            self.update()
        self.setCursor(Qt.PointingHandCursor if number is not None else Qt.ArrowCursor)


    def _set_lift(self, value):
        self.lift = value
        self.update()


    def leaveEvent(self, event):
        self.focus(None)
        super().leaveEvent(event)


    def wheelEvent(self, event):
        self.focus(None)
        self.scroll = min(max(0, self.content_height-self.text_area().height()), max(0, self.scroll-event.angleDelta().y()/3))
        self.update()


    def mouseMoveEvent(self, event):
        self.focus(self.target_at(event.position()))

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        target = self.target_at(event.position())
        if target is not None:
            self.annotation_clicked.emit(target)
        elif (handle := self.window().windowHandle()) is not None:
            # 按住空白处拖动所在窗口，交给系统完成移动。
            handle.startSystemMove()
