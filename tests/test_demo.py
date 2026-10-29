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
from PySide6.QtWidgets import QApplication, QMessageBox
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages'))
from ia_learning_core import core, PROMPT_ROOT


def baseline_logic():
    configured = os.environ.get('FAINTOCR_REFERENCE_PATH')
    if not configured or not Path(configured).is_file():
        raise unittest.SkipTest('Set FAINTOCR_REFERENCE_PATH to the external comparison source')
    path = Path(configured)
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
        self.assertEqual(payload.pop('max_tokens'), core.ANNOTATION_MAX_TOKENS)
        reference = ref['build_payload'](source, annotation, 'deepseek-chat')
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
