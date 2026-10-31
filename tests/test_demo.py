"""Baseline comparison and real Qt checks for the active Demo application."""
import ast
import json
import os
from pathlib import Path
import re
import runpy
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QMessageBox, QLineEdit
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages'))
from ia_learning_core import core, PROMPT_ROOT

# 本机对照文件的固定位置；其他机器（如 CI）用 FAINTOCR_REFERENCE_PATH 指定，缺失时才跳过。
DEFAULT_REFERENCE_PATH = Path(r'D:\IA\OCR\FaintOCR\Codeia\5.x\Demo 5.4.3.py')


def baseline_logic():
    path = Path(os.environ.get('FAINTOCR_REFERENCE_PATH') or DEFAULT_REFERENCE_PATH)
    if not path.is_file():
        raise unittest.SkipTest(f'5.4.3 对照文件不存在：{path}；请设置 FAINTOCR_REFERENCE_PATH')
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    nodes = []
    constants = {'API_URL', 'CATEGORIES', 'MAX_EXPLANATION_CHARS',
                 'PHRASE_UNDERLINE_COLOR', 'TAG_CATEGORIES', 'TAG_RE',
                 'SAMPLE', 'DEMO', 'DEMO_EXPLANATIONS'}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name != 'rgba':
            nodes.append(node)
        elif isinstance(node, ast.ClassDef) and node.name == 'AnnotationError':
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in node.targets):
            nodes.append(node)
    namespace = {'json': json, 're': re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


class DemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.module = runpy.run_path(str(ROOT / 'projects/faintocr-demo/main.py'))

    def setUp(self):
        self.errors = []
        self.hook = patch.object(sys, 'excepthook', lambda *args: self.errors.append(args))
        self.hook.start()
        with patch.object(core, 'load_deepseek_api_key', return_value='startup-test-key-1234'):
            self.window = self.module['AnnotationWindow']()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.Discard):
            self.window.close()
        self.app.processEvents()
        self.hook.stop()
        self.assertFalse(self.errors, self.errors)

    def wait_until(self, predicate):
        deadline = time.monotonic() + 5
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents()
            self.window.poll()
            time.sleep(.01)
        self.assertTrue(predicate(), 'Timed out waiting for background response')

    def test_baseline_parser_and_payload_equivalence(self):
        ref = baseline_logic()
        source = ref['SAMPLE']
        raw = json.dumps(ref['DEMO'], ensure_ascii=False)
        self.assertEqual(self.module['SAMPLE'], source)
        self.assertEqual(self.module['DEMO'], ref['DEMO'])
        expected = ref['resolve_items'](ref['DEMO'], source)
        self.assertEqual(core.parse_annotation(source, raw)['items'], expected)
        annotation = (PROMPT_ROOT / 'annotation.txt').read_text(encoding='utf-8-sig')
        explanation = (PROMPT_ROOT / 'explanation.txt').read_text(encoding='utf-8-sig')
        # 唯一有意的差异：标注输出预算从 5.4.3 的 8192 放宽，避免长文被截断。
        payload = core.build_payload(source, annotation, 'deepseek-chat')
        self.assertTrue(payload.pop('stream'))
        self.assertEqual(payload.pop('max_tokens'), core.ANNOTATION_MAX_TOKENS)
        reference = ref['build_payload'](source, annotation, 'deepseek-chat')
        self.assertFalse(reference.pop('stream'))
        self.assertEqual(reference.pop('max_tokens'), 8192)
        self.assertEqual(payload, reference)
        for item in expected:
            self.assertEqual(core.build_explanation_payload(source, item, explanation, 'deepseek-chat'),
                             ref['build_explanation_payload'](source, item, explanation, 'deepseek-chat'))
        for text in (raw, '```json\n' + raw + '\n```', raw[:-2], '{"sentences": [}'): 
            actual, locations, warnings = core.decode_best_effort(text)
            value, positions, issues = ref['decode_best_effort'](text)
            self.assertEqual(actual, value)
            self.assertEqual(locations, positions)
            self.assertEqual([str(x) for x in warnings], [str(x) for x in issues])

    def test_offline_render_and_selection(self):
        w = self.window
        self.assertEqual(w.key.echoMode(), w.key.EchoMode.Password)
        self.assertTrue(w.prompt.toPlainText().strip())
        self.assertTrue(w.explanation_prompt.toPlainText().strip())
        w.demo()
        self.assertEqual(len(w.items), 6)
        self.assertEqual(w.tree.topLevelItemCount(), 6)
        for number in range(6):
            w.select_item(number)
            w.highlight_item_json(number)
            self.app.processEvents()
        w.show_subtitle()
        self.app.processEvents()
        self.assertFalse(w.grab().isNull())
        self.assertFalse(w.subtitle.grab().isNull())
        w.apply_result('{"sentences": [}', w.source, 'invalid JSON')
        self.app.processEvents()
        self.assertGreater(w.error_tree.topLevelItemCount(), 0)
        w.demo()
        self.assertEqual(len(w.items), 6)
        # The text layout must not shadow QWidget.layout().
        self.assertIsNone(w.subtitle.view.layout())

    def test_hover_lift_animation_completes_and_resets(self):
        w = self.window
        w.demo()
        view = w.subtitle.view
        view.focus(0)
        deadline = time.monotonic() + 1
        while view.lift < 1 and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(.01)
        self.assertEqual(view.lift, 1.0)
        view.focus(None)
        self.assertEqual(view.lift, 0)
        self.assertIsNone(view.hovered)

    def test_subtitle_layout_and_utf16_selection(self):
        w, subtitle = self.window, self.window.subtitle
        w.demo()
        self.app.processEvents()
        self.assertTrue(subtitle.info_panel.isHidden())
        self.assertEqual(subtitle.view.height(), subtitle.height())
        self.assertGreaterEqual(subtitle.height(), subtitle.view.preferred_height())
        w.select_item(0)
        self.app.processEvents()
        self.assertFalse(subtitle.info_panel.isHidden())
        self.assertEqual(subtitle.view.height() + subtitle.info_height, subtitle.height())
        self.assertTrue(subtitle.info.toPlainText().strip())
        # Characters outside the BMP take two UTF-16 units in Qt; selections must still match Python indices.
        text = '前😀后 {"a": "😀x"}'
        w.raw.setPlainText(text)
        start = text.index('x')
        self.module['select_range'](w.raw, start, start + 1)
        self.assertEqual(w.raw.textCursor().selectedText(), 'x')

    def test_streaming_preview_stays_busy_until_terminal_event(self):
        w = self.window
        w.core.set_text(self.module['SAMPLE'])
        w.core.annotation_pending = True
        w.set_busy(True)
        token = (w.core.revision,)
        raw = json.dumps(self.module['DEMO'])
        w.core._events.put({'kind': 'annotation', 'token': token, 'success': True,
                            'partial': True, 'data': (raw[:-2], None), 'elapsed': .1})
        w.poll()
        self.assertTrue(w.busy)
        self.assertTrue(w.core.annotation_pending)
        self.assertEqual(len(w.items), 6)
        self.assertIn('流式标注中', w.status.text())
        w.core._events.put({'kind': 'annotation', 'token': token, 'success': True,
                            'data': (raw, 'stop'), 'elapsed': .2})
        w.poll()
        self.assertFalse(w.busy)
        self.assertFalse(w.core.annotation_pending)
        self.assertEqual(len(w.items), 6)

    def test_mock_annotation_explanation_cache_and_failure(self):
        w = self.window
        calls = []
        def transport(key, payload):
            calls.append(payload)
            user = json.loads(payload['messages'][1]['content'])
            content = {'explanation': 'Mock explanation'} if 'annotation' in user else self.module['DEMO']
            return json.dumps({'choices': [{'message': {'content': json.dumps(content)}, 'finish_reason': 'stop'}]})
        w.core.transport = transport
        self.config_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.config_dir.cleanup)
        config = Path(self.config_dir.name) / 'deepseek_api_key.json'
        config.write_text(json.dumps({'api_key': 'test-key'}), encoding='utf-8')
        w.core.config_path = config
        w.key.setText('test-key')
        w.english.setPlainText(self.module['SAMPLE'])
        w.submit()
        self.wait_until(lambda: not w.busy)
        self.assertEqual(len(w.items), 6)
        w.select_item(0)
        self.wait_until(lambda: 'Mock explanation' in w.details.text())
        count = len(calls)
        w.select_item(0)
        self.app.processEvents()
        self.assertEqual(len(calls), count)
        def failure(key, payload):
            raise ValueError('failure test-key')
        w.core.transport = failure
        w.submit()
        self.wait_until(lambda: not w.busy)
        self.assertNotIn('test-key', w.status.text())
        self.assertIn('failure', w.status.text())

    def test_truncated_annotation_asks_for_shorter_text(self):
        w = self.window
        body = {'choices': [{'message': {'content': json.dumps(self.module['DEMO'])}, 'finish_reason': 'length'}]}
        w.core.transport = lambda key, payload: json.dumps(body)
        w.key.setText('test-key')
        w.english.setPlainText(self.module['SAMPLE'])
        w.submit()
        self.wait_until(lambda: not w.busy)
        self.assertIn('token 上限', w.status.text())

    def test_ui_key_overrides_config_for_both_requests(self):
        w = self.window
        keys = []
        def transport(key, payload):
            keys.append(key)
            user = json.loads(payload['messages'][1]['content'])
            content = {'explanation': 'Override explanation'} if 'annotation' in user else self.module['DEMO']
            return json.dumps({'choices': [{'message': {'content': json.dumps(content)}, 'finish_reason': 'stop'}]})
        w.core.transport = transport
        w.key.setText(' ui-test-key ')
        w.english.setPlainText(self.module['SAMPLE'])
        with patch.object(core, 'load_deepseek_api_key', side_effect=AssertionError('Override must not read config')):
            w.submit()
            self.wait_until(lambda: not w.busy)
            w.select_item(0)
            self.wait_until(lambda: 'Override explanation' in w.details.text())
        self.assertEqual(keys, ['ui-test-key', 'ui-test-key'])

    def test_key_startup_mask_and_no_fallback(self):
        w = self.window
        self.assertEqual(w.key.text(), 'startup-test-key-1234')
        self.assertEqual(w.key.echoMode(), QLineEdit.Password)
        w.key.setText('short')
        self.assertNotEqual(w.key.displayText(), 'short')
        w.key.clear()
        w.english.setPlainText(self.module['SAMPLE'])
        with patch.object(core, 'load_deepseek_api_key', side_effect=AssertionError('No reload')):
            with patch.object(w.core, 'transport') as transport:
                w.submit()
                self.assertFalse(w.busy)
                self.assertIn('请输入 API Key', w.status.text())
                w.apply_result(json.dumps(self.module['DEMO']), self.module['SAMPLE'], 'test')
                w.select_item(0)
                self.assertIn('请输入 API Key', w.details.text())
                transport.assert_not_called()

    def test_key_native_editing(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        edit = self.window.key
        edit.setText('abcdefgh1234567890wxyz')
        edit.setFocus()
        edit.setCursorPosition(10)
        QTest.keyClicks(edit, 'AB')
        self.assertEqual(edit.text(), 'abcdefgh12AB34567890wxyz')
        self.assertEqual(len(edit.displayText()), len(edit.text()))
        edit.setSelection(8, 4)
        QTest.keyClicks(edit, 'Z')
        self.assertEqual(edit.text(), 'abcdefghZ34567890wxyz')
        QTest.keyClick(edit, Qt.Key_Backspace)
        self.assertEqual(edit.text(), 'abcdefgh34567890wxyz')
        edit.selectAll()
        QTest.keyClick(edit, Qt.Key_Delete)
        self.assertEqual(edit.text(), '')

    def test_key_visibility_toggle_preserves_editing(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        edit = self.window.key
        secret = 'abcdefgh1234567890wxyz'
        edit.setText(secret)
        edit.setSelection(8, 4)
        self.assertEqual(edit.echoMode(), QLineEdit.Password)
        QTest.mouseClick(edit.visibility_button, Qt.LeftButton)
        self.assertEqual(edit.echoMode(), QLineEdit.Normal)
        self.assertEqual(edit.displayText(), secret)
        self.assertEqual(edit.selectedText(), '1234')
        self.assertEqual(edit.visibility_button.text(), '隐藏')
        QTest.mouseClick(edit.visibility_button, Qt.LeftButton)
        self.assertEqual(edit.echoMode(), QLineEdit.Password)
        self.assertEqual(edit.selectedText(), '1234')
        self.assertEqual(edit.text(), secret)
        self.assertNotEqual(edit.displayText(), secret)
        self.assertEqual(edit.visibility_button.text(), '显示')
        edit.setText('x' * 120)
        edit.setCursorPosition(60)
        QTest.mouseClick(edit.visibility_button, Qt.LeftButton)
        self.assertEqual(edit.cursorPosition(), 60)
        self.assertEqual(edit.text(), 'x' * 120)
        self.assertFalse(edit.grab().isNull())

    def test_editor_save_reload_conflict_and_cancel(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            path = Path(folder) / 'annotation.txt'
            path.write_text('original', encoding='utf-8')
            editor = self.module['PromptEditor'](path)
            editor.editor.setPlainText('edited')
            self.assertTrue(editor.has_unsaved())
            editor.save_prompt()
            self.assertEqual(path.read_text(encoding='utf-8'), 'edited')
            path.write_text('external', encoding='utf-8')
            editor.editor.setPlainText('draft')
            editor.save_prompt()
            self.assertIn('外部修改', editor.note.text())
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.Cancel):
                editor.reload_prompt()
            self.assertEqual(editor.editor.toPlainText(), 'draft')
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.Discard):
                editor.reload_prompt()
            self.assertEqual(editor.editor.toPlainText(), 'external')
            self.assertFalse(editor.has_unsaved())
            editor.close()


if __name__ == '__main__':
    unittest.main()
