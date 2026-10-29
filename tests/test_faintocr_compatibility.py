"""RapidOCR 3.x adaptation checks using the real FaintOCR module."""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import numpy as np

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('faintocr_compat_tests', ROOT / 'projects/faintocr/main.py')
faintocr = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = faintocr
SPEC.loader.exec_module(faintocr)


class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = faintocr.QApplication.instance() or faintocr.QApplication([])

    def setUp(self):
        self.worker = faintocr.OCRWorker({})
        self.image = np.zeros((200, 400, 3), dtype=np.uint8)

    def result(self, boxes, texts, scores=None):
        return types.SimpleNamespace(boxes=np.array(boxes), txts=tuple(texts),
                                     scores=tuple(scores or [.99] * len(texts)))

    def test_empty_output_is_normal(self):
        for result in (types.SimpleNamespace(boxes=None, txts=None, scores=None),
                       self.result([], [])):
            self.assertIsNone(self.worker.run_rapidocr(lambda _: result, self.image, 'Genshin Impact', 'CHS', 0))

    def test_new_output_keeps_line_joining(self):
        result = self.result([
            [[20, 10], [100, 10], [100, 40], [20, 40]],
            [[120, 10], [200, 10], [200, 40], [120, 40]],
            [[20, 60], [100, 60], [100, 90], [20, 90]],
        ], ['Hello', 'world', 'next line'])
        text = self.worker.run_rapidocr(lambda _: result, self.image, 'Genshin Impact', 'EN', 0)
        self.assertEqual(text, 'Hello world\nnext line')

    def test_height_filter_still_requires_crop(self):
        result = self.result([
            [[120, 10], [220, 10], [220, 40], [120, 40]],
            [[120, 60], [220, 60], [220, 70], [120, 70]],
        ], ['valid', 'too short'])
        engine = lambda _: result
        self.assertEqual(self.worker.run_rapidocr(engine, self.image, 'Genshin Impact', 'EN', 1, True), 'valid')
        self.assertEqual(self.worker.run_rapidocr(engine, self.image, 'Genshin Impact', 'EN', 1, False), 'valid\ntoo short')

    def test_misaligned_output_is_not_silently_truncated(self):
        result = self.result([[[0, 0], [10, 0], [10, 30], [0, 30]]], ['one', 'two'])
        with self.assertRaises(ValueError):
            self.worker.run_rapidocr(lambda _: result, self.image, 'Genshin Impact', 'EN', 0)

    def test_controller_passes_new_parameter_names(self):
        with patch.object(faintocr, 'RapidOCR') as factory:
            controller = faintocr.OCRController()
            self.addCleanup(controller.cleanup)
            params = [call.kwargs['params'] for call in factory.call_args_list]
        self.assertEqual(params, [
            {'EngineConfig.onnxruntime.intra_op_num_threads': 4},
            {'Det.limit_side_len': 1280, 'Det.limit_type': 'max',
             'EngineConfig.onnxruntime.intra_op_num_threads': 4},
        ])

    def test_rapidfuzz_matching_with_current_version(self):
        matcher = faintocr.TextMatcher()
        matcher.set_data({'Hello world': ['你好世界']}, ['Hello world'], 'Genshin Impact', 'EN', 'CHS')
        key, translation, score = matcher.match_text('Hello world', 1, 75)
        self.assertEqual(key, 'Hello world')
        self.assertIn('你好世界', translation)


if __name__ == '__main__':
    unittest.main()
