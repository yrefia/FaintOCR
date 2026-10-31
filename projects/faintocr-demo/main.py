"""Learning annotation application entry point."""

from pathlib import Path
import importlib.util
import sys
import json
import time

# 已安装（含 pip install -e .）时直接使用安装的包；未安装时才回退到仓库内 packages/。
if importlib.util.find_spec('ia_learning_core') is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'packages'))
from ia_learning_core import core, prompt_path
from ia_learning_core.view import AnnotatedTextView, rgba
from ia_learning_core.core import (
    CATEGORIES,
    AnnotationError,
    PromptFile,
    compose_annotation_payload,
    compose_explanation_payload,
    format_request,
    utf16_offsets,
)

# runpy 与测试不会把入口所在目录加入 sys.path，示例数据模块需要显式加入。
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from demo_data import SAMPLE, DEMO, DEMO_EXPLANATIONS
from PySide6.QtCore import Qt, QRectF, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QLinearGradient, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QTabWidget,
    QCheckBox,
    QComboBox,
    QTextBrowser,
    QMessageBox,
    QToolButton,
)

DEMO_TITLE = 'FaintOCR Demo 5.5.0'


class ApiKeyEdit(QLineEdit):
    """Native password editing with an explicit reveal toggle."""

    def __init__(self):
        super().__init__()
        self.setEchoMode(QLineEdit.Password)
        self.setPlaceholderText('请输入 API Key')
        self.setAccessibleName('DeepSeek API Key')
        self.setMinimumSize(240, 34)
        self.setTextMargins(8, 0, 54, 0)
        self.visibility_button = QToolButton(self)
        self.visibility_button.setText('显示')
        self.visibility_button.setAccessibleName('显示 API Key')
        self.visibility_button.setToolTip('显示 API Key')
        self.visibility_button.setCheckable(True)
        self.visibility_button.setAutoRaise(True)
        self.visibility_button.setCursor(Qt.PointingHandCursor)
        self.visibility_button.toggled.connect(self.set_key_visible)

    def set_key_visible(self, visible):
        position = self.cursorPosition()
        start = self.selectionStart()
        length = len(self.selectedText())
        self.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
        if start >= 0:
            self.setSelection(start + length, -length) if position == start else self.setSelection(start, length)
        else:
            self.setCursorPosition(position)
        label = '隐藏' if visible else '显示'
        self.visibility_button.setText(label)
        self.visibility_button.setToolTip(label + ' API Key')
        self.visibility_button.setAccessibleName(label + ' API Key')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.visibility_button.setGeometry(self.width() - 50, 3, 46, self.height() - 6)


class SubtitleWindow(QWidget):
    """Demo-owned floating shell. Shared view owns only annotated text rendering."""

    selected = Signal(int)
    visibility_changed = Signal(bool)

    def __init__(self):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(f'{DEMO_TITLE} · 字幕')
        self.resize(980, 180)
        self.info_height = 220
        self.view = AnnotatedTextView(self)
        self.view.annotation_clicked.connect(self.selected.emit)
        self.info = QTextBrowser()
        self.info.setOpenLinks(False)
        self.info.setFont(QFont('Microsoft YaHei UI', 11))
        self.info.setStyleSheet(
            'QTextBrowser { background: transparent; color: #F5F6FA; border: 0; border-top: 1px solid rgba(230,220,255,60); padding-top: 10px; }'
        )
        # 解释区与字幕文字左右对齐，底部给圆角边框留出位置。
        self.info_panel = QWidget()
        panel = QVBoxLayout(self.info_panel)
        panel.setContentsMargins(AnnotatedTextView.MARGIN_X, 0, AnnotatedTextView.MARGIN_X, 28)
        panel.addWidget(self.info)
        self.info_panel.setFixedHeight(self.info_height)
        self.info_panel.hide()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.view, 1)
        layout.addWidget(self.info_panel)

    @property
    def source(self):
        return self.view.source

    @property
    def items(self):
        return self.view.items

    def showEvent(self, event):
        super().showEvent(event)
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def set_content(self, source, items, enabled=None):
        self.info.clear()
        self.info_panel.hide()
        self.view.set_content(source, items, enabled)
        screen = self.screen().availableGeometry()
        self.resize(
            self.width(), max(self.height(), min(max(180, self.view.preferred_height()), int(screen.height() * 0.6)))
        )
        self.update()

    def show_explanation(self, number, text):
        item = self.items[number]
        if self.info_panel.isHidden():
            cap = self.screen().availableGeometry().height() - 40
            self.resize(
                self.width(), max(self.height(), min(max(180, self.view.preferred_height()) + self.info_height, cap))
            )
        self.info.setPlainText(
            f"{CATEGORIES[item['category']][0]} · {item['subtype'] + ' · ' if item['subtype'] else ''}{item['unit']}\n{text}"
        )
        self.info.verticalScrollBar().setValue(0)
        self.info_panel.show()

    def closeEvent(self, event):
        self.view.focus(None)
        super().closeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        body = QRectF(12, 10, self.width() - 24, self.height() - 24)
        p.setOpacity(0.8)
        p.setPen(Qt.NoPen)
        p.setBrush(rgba('#060815', 28))
        p.drawRoundedRect(body.adjusted(-1, 2, 1, 4), 23, 23)
        gradient = QLinearGradient(body.topLeft(), body.bottomRight())
        gradient.setColorAt(0, rgba('#20222d', 248))
        gradient.setColorAt(1, rgba('#141621', 248))
        p.setBrush(gradient)
        p.setPen(QPen(rgba('#ffffff', 28), 1))
        p.drawRoundedRect(body, 22, 22)
        p.end()


def confirm_discard(parent, text):
    """True when the user agrees to drop unsaved prompt edits."""
    answer = QMessageBox.question(
        parent, '未保存提示词', text, QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Cancel
    )
    return answer == QMessageBox.Discard


def range_cursor(editor, offsets, start, end):
    """QTextCursor over Python indices [start, end) of the editor text; offsets come from utf16_offsets."""
    cursor = editor.textCursor()
    cursor.setPosition(offsets[start])
    cursor.setPosition(offsets[end], QTextCursor.KeepAnchor)
    return cursor


def select_range(editor, start, end):
    editor.setTextCursor(range_cursor(editor, utf16_offsets(editor.toPlainText()), start, end))
    editor.setFocus()
    editor.ensureCursorVisible()


class PromptEditor(QWidget):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.file = PromptFile(path)
        self.disk = None
        layout = QVBoxLayout(self)
        self.path_label = QLabel(str(self.file.path))
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)
        self.editor = QPlainTextEdit()
        layout.addWidget(self.editor)
        row = QHBoxLayout()
        self.save_button = QPushButton('保存提示词')
        self.reload_button = QPushButton('重新加载')
        row.addWidget(self.save_button)
        row.addWidget(self.reload_button)
        layout.addLayout(row)
        self.note = QLabel()
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.editor.textChanged.connect(self.mark_dirty)
        self.save_button.clicked.connect(self.save_prompt)
        self.reload_button.clicked.connect(self.reload_prompt)
        self.reload_prompt()

    def has_unsaved(self):
        return self.editor.toPlainText() != (self.disk or '')

    def mark_dirty(self):
        if self.disk is None:
            self.note.setText('提示词文件未加载；请修复文件后重新加载。')
        else:
            status = '未保存修改' if self.has_unsaved() else '已加载'
            self.note.setText(status + ' · 请求使用当前编辑内容。')

    def reload_prompt(self):
        if self.has_unsaved() and not confirm_discard(self, '重新加载会丢弃当前未保存修改，是否继续？'):
            return
        try:
            content = self.file.read()
        except (OSError, UnicodeError) as exc:
            self.note.setText(f'读取失败：{exc}')
            return
        self.disk = content
        self.editor.setPlainText(content)
        self.mark_dirty()

    def save_prompt(self):
        if self.disk is None:
            self.note.setText('请先成功加载提示词文件，再保存修改。')
            return
        content = self.editor.toPlainText()
        try:
            self.file.save(content, previous=self.disk)
        except (OSError, UnicodeError, ValueError) as exc:
            self.note.setText(f'保存失败：{exc}')
            return
        self.disk = content
        self.note.setText('已保存：' + str(self.file.path))


class AnnotationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{DEMO_TITLE} · 学习元素标注')
        self.resize(1120, 760)
        self.source, self.items = '', []
        # 最近一次渲染所用的返回 JSON 及其位置索引，用于判断编辑区是否已改动。
        self.rendered_raw, self.rendered_locations = None, {}
        self.core = core.LearningCore()
        self.offline = False
        self.busy = False
        self.request_history = []
        self.subtitle = SubtitleWindow()
        self.subtitle.selected.connect(self.select_item)
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.key = ApiKeyEdit()
        try:
            self.key.setText(core.load_deepseek_api_key())
        except ValueError as exc:
            self.key.setToolTip(f'启动时读取密钥失败：{exc}\n请输入 API Key；请求不会重新读取本地配置。')
        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.addItems(['deepseek-flash', 'deepseek-v4-pro'])
        self.submit_button = QPushButton('标注学习元素')
        self.demo_button = QPushButton('离线演示')
        self.subtitle_button = QPushButton('显示字幕悬浮窗')
        self.subtitle.visibility_changed.connect(
            lambda visible: self.subtitle_button.setText('关闭字幕悬浮窗' if visible else '显示字幕悬浮窗')
        )
        for widget in (
            QLabel('DeepSeek API Key'),
            self.key,
            QLabel('模型'),
            self.model,
            self.submit_button,
            self.demo_button,
            self.subtitle_button,
        ):
            top.addWidget(widget)
        root.addLayout(top)
        splitter = QSplitter()
        self.annotation_library = PromptEditor(prompt_path('annotation.txt'))
        self.prompt = self.annotation_library.editor
        self.prompt.setPlaceholderText('第一层：中文标注提示词')
        self.explanation_library = PromptEditor(prompt_path('explanation.txt'))
        self.explanation_prompt = self.explanation_library.editor
        prompt_tabs = QTabWidget()
        prompt_tabs.addTab(self.annotation_library, '第一层 · 仅标注')
        prompt_tabs.addTab(self.explanation_library, '第二层 · 按需解释')
        requests = QTabWidget()
        self.annotation_preview = QPlainTextEdit()
        self.annotation_preview.setReadOnly(True)
        requests.addTab(self.annotation_preview, '第一层待发')
        explanation_page = QWidget()
        explanation_box = QVBoxLayout(explanation_page)
        explanation_box.addWidget(QLabel('选择条目仅预览；点击字幕才请求解释，列表点击只定位 JSON。'))
        self.preview_item = QComboBox()
        self.preview_item.addItem('未选择标注', None)
        explanation_box.addWidget(self.preview_item)
        self.explanation_preview = QPlainTextEdit()
        self.explanation_preview.setReadOnly(True)
        explanation_box.addWidget(self.explanation_preview)
        requests.addTab(explanation_page, '第二层待发')
        history_page = QWidget()
        history_box = QVBoxLayout(history_page)
        history_box.addWidget(QLabel('实际提交给请求线程的快照，不代表请求成功；缓存/离线演示不会新增。'))
        self.history_selector = QComboBox()
        history_box.addWidget(self.history_selector)
        self.history_view = QPlainTextEdit('尚未发送请求。')
        self.history_view.setReadOnly(True)
        history_box.addWidget(self.history_view)
        requests.addTab(history_page, '发送快照')
        prompt_tabs.addTab(requests, '完整 AI 请求')
        splitter.addWidget(prompt_tabs)
        panel = QWidget()
        side = QVBoxLayout(panel)
        side.addWidget(QLabel('英文原文'))
        self.english = QPlainTextEdit()
        self.english.setMaximumHeight(160)
        side.addWidget(self.english)
        filters = QHBoxLayout()
        self.filters = {}
        for category, (label, _, _) in CATEGORIES.items():
            check = QCheckBox(label)
            check.setChecked(True)
            check.toggled.connect(self.render)
            self.filters[category] = check
            filters.addWidget(check)
        side.addLayout(filters)
        side.addWidget(QLabel('返回文本显示于独立半透明字幕窗。拖动空白处移动；滚轮浏览长文本。'))
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['层级', '子类', '标准形式'])
        self.tree.setColumnWidth(0, 140)
        self.tree.setColumnWidth(1, 180)
        self.tree.itemClicked.connect(lambda entry, _: self.highlight_item_json(entry.data(0, Qt.UserRole)))
        side.addWidget(self.tree)
        self.details = QLabel('点击字幕标注查看解释；点击列表条目定位返回 JSON。')
        self.details.setWordWrap(True)
        self.details.setTextFormat(Qt.PlainText)
        side.addWidget(self.details)
        self.raw = QPlainTextEdit()
        self.raw.setPlaceholderText('粘贴或修改返回的 JSON，然后点击“应用 JSON / 重新渲染”。')
        side.addWidget(QLabel('返回 JSON（可编辑，按句分组、范围标签定位）'))
        self.apply_json_button = QPushButton('应用 JSON / 重新渲染')
        self.apply_json_button.clicked.connect(self.apply_json)
        side.addWidget(self.apply_json_button)
        side.addWidget(self.raw)
        self.error_tree = QTreeWidget()
        self.error_tree.setHeaderLabels(['提醒条目（点击定位）', '细节'])
        self.error_tree.setColumnWidth(0, 180)
        self.error_tree.setMaximumHeight(150)
        self.error_tree.hide()
        self.error_tree.itemClicked.connect(self.navigate_error)
        self.raw.textChanged.connect(self.clear_errors)
        side.addWidget(self.error_tree)
        splitter.addWidget(panel)
        splitter.setSizes([420, 700])
        root.addWidget(splitter)
        self.status = QLabel('先标注，点击后按需解释；同一文本内缓存解释。密钥不落盘。')
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.PlainText)
        root.addWidget(self.status)
        self.submit_button.clicked.connect(self.submit)
        self.demo_button.clicked.connect(self.demo)
        self.subtitle_button.clicked.connect(self.toggle_subtitle)
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll)
        self.poll_timer.start(80)
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(80)
        self.preview_timer.timeout.connect(self.refresh_request_previews)
        for editor in (self.prompt, self.explanation_prompt, self.english):
            editor.textChanged.connect(lambda: self.preview_timer.start())
        self.model.currentTextChanged.connect(lambda *_: self.preview_timer.start())
        self.preview_item.currentIndexChanged.connect(lambda *_: self.refresh_request_previews())
        self.history_selector.currentIndexChanged.connect(self.show_history)
        self.refresh_request_previews()

    def refresh_request_previews(self):
        first = compose_annotation_payload(
            self.english.toPlainText(), self.prompt.toPlainText(), self.model.currentText()
        )
        self.annotation_preview.setPlainText('待发送预览（未通过输入校验时不会发送）。\n\n' + format_request(first))
        number = self.preview_item.currentData()
        item = self.items[number] if number is not None and number < len(self.items) else None
        second = compose_explanation_payload(
            self.source, item, self.explanation_prompt.toPlainText(), self.model.currentText()
        )
        note = (
            '仅预览；命中缓存或离线演示时不会发送。' if item else '未选标注，annotation 为占位 null；此状态不会发送。'
        )
        self.explanation_preview.setPlainText(note + '\n\n' + format_request(second))

    def record_request(self, layer, payload):
        snapshot = json.loads(json.dumps(payload, ensure_ascii=False))
        self.request_history.append({'layer': layer, 'payload': snapshot})
        self.history_selector.addItem(f"{len(self.request_history)} · {layer} · {time.strftime('%H:%M:%S')}")
        self.history_selector.setCurrentIndex(len(self.request_history) - 1)
        self.show_history(len(self.request_history) - 1)

    def show_history(self, index):
        if 0 <= index < len(self.request_history):
            record = self.request_history[index]
            self.history_view.setPlainText(record['layer'] + ' · 发送快照\n\n' + format_request(record['payload']))

    def toggle_subtitle(self):
        if self.subtitle.isVisible():
            self.subtitle.close()
        else:
            self.show_subtitle()

    def show_subtitle(self):
        self.subtitle.show()
        self.subtitle.raise_()

    def render(self, *_):
        self.core.clear_selection()
        enabled = {key for key, check in self.filters.items() if check.isChecked()}
        self.subtitle.set_content(self.source, self.items, enabled)
        self.tree.clear()
        for number, item in enumerate(self.items):
            if item['category'] in enabled:
                entry = QTreeWidgetItem([CATEGORIES[item['category']][0], item['subtype'], item['unit']])
                entry.setData(0, Qt.UserRole, number)
                self.tree.addTopLevelItem(entry)
        self.details.setText('点击字幕标注查看解释；点击列表条目定位返回 JSON。')
        self.preview_item.blockSignals(True)
        self.preview_item.clear()
        self.preview_item.addItem('未选择标注', None)
        for number, item in enumerate(self.items):
            self.preview_item.addItem((item['subtype'] + ' · ' if item['subtype'] else '') + item['unit'], number)
        self.preview_item.blockSignals(False)
        self.refresh_request_previews()

    def display_explanation(self, number, text, reveal=True):
        self.subtitle.show_explanation(number, text)
        if reveal:
            self.show_subtitle()
        item = self.items[number]
        quotes = ' / '.join(self.source[a:b] for a, b in item['ranges'])
        self.details.setText(
            f"{item['subtype'] + ' · ' if item['subtype'] else ''}{item['unit']}\n原文：{quotes}\n{text}"
        )

    def select_item(self, number):
        self.preview_item.setCurrentIndex(self.preview_item.findData(number))
        self.refresh_request_previews()
        for i in range(self.tree.topLevelItemCount()):
            entry = self.tree.topLevelItem(i)
            if entry.data(0, Qt.UserRole) == number:
                self.tree.setCurrentItem(entry)
        if self.offline:
            self.display_explanation(number, DEMO_EXPLANATIONS[number])
            return
        try:
            result = self.core.explain(
                number, self.explanation_prompt.toPlainText(), self.model.currentText(), key=self.input_api_key()
            )
        except ValueError as exc:
            self.display_explanation(number, str(exc))
            return
        self.display_explanation(number, result['text'])
        if result['payload'] is not None:
            self.record_request('第二层 · 解释', result['payload'])

    def demo(self):
        if self.busy:
            return
        self.english.setPlainText(SAMPLE)
        self.raw.setPlainText(json.dumps(DEMO, ensure_ascii=False, indent=2))
        result = self.core.apply_json(SAMPLE, self.raw.toPlainText())
        self.offline = True
        self.show_document(result)
        self.status.setText('离线演示 · 无 API 请求')

    def clear_errors(self):
        self.error_tree.clear()
        self.error_tree.hide()
        self.raw.setExtraSelections([])

    def navigate_error(self, entry, column=0):
        select_range(self.raw, *entry.data(0, Qt.UserRole))

    def show_json_error(self, error):
        self.clear_errors()
        content = self.raw.toPlainText()
        locations = self.rendered_locations if content == self.rendered_raw else core.decode_best_effort(content)[1]
        entries = core.warning_locations(content, locations, getattr(error, 'errors', [error]))
        for label, message, start, end in entries:
            entry = QTreeWidgetItem([label, message])
            entry.setToolTip(1, message)
            entry.setData(0, Qt.UserRole, (start, end))
            self.error_tree.addTopLevelItem(entry)
        self.error_tree.setVisible(bool(entries))
        if entries:
            self.error_tree.setCurrentItem(self.error_tree.topLevelItem(0))
            self.navigate_error(self.error_tree.topLevelItem(0))

    def apply_json(self):
        if self.busy:
            return
        self.apply_result(self.raw.toPlainText(), self.english.toPlainText(), '本地重新渲染 · 无 API 请求')

    def apply_result(self, raw, source, label):
        result = self.core.apply_json(source, raw)
        self.offline = False
        self.show_document(result, label)

    def show_document(self, result, label='解析完成'):
        self.source, self.items = result['source'], result['items']
        self.rendered_raw, self.rendered_locations = result['raw'], result['locations']
        self.render()
        self.show_subtitle()
        self.clear_errors()
        issues = result['warnings']
        if issues:
            notice = AnnotationError('解析提醒')
            notice.errors = issues
            self.show_json_error(notice)
        self.status.setToolTip('\n'.join(str(i) for i in issues))
        self.status.setText(
            f'{label} · {len(self.items)} 个可用标注 · {len(issues)} 条提醒'
            + ('；已显示本次原文。' if not self.items else '')
        )

    def highlight_item_json(self, number):
        if not isinstance(number, int) or not 0 <= number < len(self.items):
            return
        raw = self.raw.toPlainText()
        if raw != self.rendered_raw:
            self.status.setText('提醒：返回 JSON 已编辑，请先应用后再定位元素。')
            return
        item = self.items[number]
        annotation = item['annotation']
        ranges = core.item_json_ranges(item, raw, self.rendered_locations)
        selections = []
        offsets = utf16_offsets(raw)
        for start, end in ranges:
            selection = QTextEdit.ExtraSelection()
            selection.cursor = range_cursor(self.raw, offsets, start, end)
            selection.format.setBackground(QColor('#665128'))
            selection.format.setForeground(QColor('#fff1bc'))
            selections.append(selection)
        self.raw.setExtraSelections(selections)
        if selections:
            self.raw.setTextCursor(selections[0].cursor)
            self.raw.setFocus()
            self.raw.ensureCursorVisible()
        self.details.setText(
            f"JSON 定位 · 第 {annotation['sentence_index']} 句 · {annotation['id']} · {item['unit']}\n已标出属性记录与 {len(ranges) - 1} 个范围片段；点击字幕标注可查看解释。"
        )

    def set_busy(self, busy):
        self.busy = busy
        for widget in (
            self.submit_button,
            self.demo_button,
            self.prompt,
            self.english,
            self.raw,
            self.apply_json_button,
        ):
            widget.setEnabled(not busy)

    def submit(self):
        if self.busy:
            return
        try:
            result = self.core.annotate(
                self.english.toPlainText(), self.prompt.toPlainText(), self.model.currentText(), key=self.input_api_key()
            )
        except ValueError as exc:
            self.status.setText(str(exc))
            return
        self.offline = False
        self.raw.clear()
        self.show_document(self.core.document)
        self.set_busy(True)
        self.status.setText('正在标注…')
        if result['payload'] is not None:
            self.record_request('第一层 · 标注', result['payload'])

    def input_api_key(self):
        key = self.key.text().strip()
        if not key:
            raise ValueError('请输入 API Key；请求仅使用输入框中的密钥。')
        return key

    def poll(self):
        for event in self.core.poll():
            if event['kind'] == 'explanation':
                if event['selected']:
                    self.display_explanation(event['token'][1], event['data'], reveal=False)
                continue
            self.set_busy(False)
            if event['success']:
                result = event['document']
                self.raw.setPlainText(result['raw'])
                # QTextDocument normalizes line endings; reindex only if that changed raw coordinates.
                if self.raw.toPlainText() != result['raw']:
                    result = self.core.apply_json(result['source'], self.raw.toPlainText())
                self.show_document(result, f"返回解析 · {event['elapsed']:.1f} 秒")
                reason = event['finish_reason']
                if reason == 'length':
                    self.status.setText(
                        self.status.text() + ' · 提醒：输出达到 token 上限，后面的句子可能缺少标注；请缩短原文后重试。'
                    )
                elif reason not in (None, 'stop'):
                    self.status.setText(self.status.text() + f' · 提醒：响应未正常结束（{reason}），请检查完整性。')
            else:
                self.status.setText('请求提醒：' + event['data'] + '；已显示本次原文。')

    def closeEvent(self, event):
        unsaved = self.annotation_library.has_unsaved() or self.explanation_library.has_unsaved()
        if unsaved and not confirm_discard(self, '有未保存的提示词草稿。是否放弃草稿并关闭？'):
            event.ignore()
            return
        self.core.close()
        self.preview_timer.stop()
        self.poll_timer.stop()
        self.subtitle.close()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnnotationWindow()
    window.show()
    sys.exit(app.exec())
