"""Check the application's retained I/O behavior without importing legacy OCR."""
import ast
from datetime import datetime
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/faintocr'


def load_io(source_file, *, frozen=False, executable=None, bundle=None):
    tree = ast.parse((PROJECT / 'main.py').read_text(encoding='utf-8'))
    names = {'RUNTIME_DIR', 'RUNTIME_ICON_FILE', '_debug_lock'}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.If) and 'frozen' in ast.unparse(node.test):
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in ('atomic_write_bytes', 'prune_debug_images', 'write_debug_image'):
            nodes.append(node)
        elif isinstance(node, ast.ClassDef) and node.name in ('I18n', 'Config', 'TextMapLoader', 'UserConfigManager'):
            nodes.append(node)
    system = types.SimpleNamespace(frozen=frozen, executable=str(executable or source_file))
    if bundle is not None:
        system._MEIPASS = str(bundle)
    namespace = {'__file__': str(source_file), 'sys': system, 'os': os, 'Path': Path,
                 'datetime': datetime, 'tempfile': tempfile, 'threading': threading,
                 'time': time, 're': re,
                 'orjson': types.SimpleNamespace(loads=json.loads, OPT_INDENT_2=2,
                     dumps=lambda value, **_: json.dumps(value).encode()),
                 'logger': types.SimpleNamespace(error=lambda *_: None, warning=lambda *_: None)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<main I/O>', 'exec'), namespace)
    return namespace


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name).resolve()
        self.io = load_io(self.root / 'project/main.py')
        self.runtime = self.io['RUNTIME_DIR']

    def test_source_and_frozen_paths(self):
        self.assertEqual(self.runtime, self.root / 'project/runtime')
        self.assertEqual(self.io['RUNTIME_ICON_FILE'], self.root / 'project/assets/logo.ico')
        for bundle in (self.root / '_MEI123', self.root / 'install/_internal', None):
            with patch.dict(os.environ, {'LOCALAPPDATA': str(self.root / 'user')}):
                io = load_io(self.root / 'main.py', frozen=True,
                             executable=self.root / 'install/faintocr.exe', bundle=bundle)
            self.assertEqual(io['RUNTIME_DIR'], self.root / 'user/IA/FaintOCR/runtime')
            self.assertEqual(io['RUNTIME_ICON_FILE'], (bundle or self.root / 'install') / 'assets/logo.ico')

    def test_config_and_dictionary_wiring(self):
        config = self.io['Config']
        self.assertEqual(Path(config.USER_CONFIG_FILE), self.runtime / 'config/settings.json')
        self.assertEqual(Path(config.output_file_path()).parent, self.runtime / 'exports/subtitles')
        self.assertFalse(config.OCR['DETECT']['debug'])
        self.assertFalse(config.OCR['PRE_OCR_CROP_RULES']['debug'])
        loader = self.io['TextMapLoader']
        raw = Path(loader.get_file_path('Genshin Impact', 'TextMapCHS.json'))
        derived = Path(loader.get_file_path('Genshin Impact', 'MatchStatic-CHStoEN.json'))
        self.assertEqual(raw, self.runtime / 'data/dictionaries/genshin-impact/raw/TextMapCHS.json')
        self.assertEqual(derived.parent.name, 'derived')
        with self.assertRaises(ValueError):
            loader.get_file_path('Genshin Impact', '../escape.json')
        self.assertTrue(loader._save_file_atomic(str(derived), {'test': 'value'}))
        manager = self.io['UserConfigManager']
        manager.save(manager.default_config())
        self.assertTrue(Path(config.USER_CONFIG_FILE).is_file())
        self.assertIsInstance(manager.load(), dict)

    def test_atomic_write_preserves_previous_file_on_failure(self):
        target = self.runtime / 'config/settings.json'
        write = self.io['atomic_write_bytes']
        write(target, b'original')
        with patch.object(os, 'replace', side_effect=OSError('replace failed')):
            with self.assertRaises(OSError):
                write(target, b'new')
        self.assertEqual(target.read_bytes(), b'original')
        self.assertEqual(list(target.parent.glob('*.tmp')), [])

    def test_debug_cleanup_preserves_other_data(self):
        directory = self.runtime / 'debug/detection'
        directory.mkdir(parents=True)
        for index in range(5):
            path = directory / f'diff_{index}.png'
            path.write_bytes(b'image')
            os.utime(path, (1000 + index, 1000 + index))
        exported = self.runtime / 'exports/subtitles/2026-10-29.txt'
        self.io['atomic_write_bytes'](exported, b'keep')
        unrelated = directory / 'personal.png'
        unrelated.write_bytes(b'keep')
        prune = self.io['prune_debug_images']
        prune(directory, max_files=2, now=1005)
        self.assertEqual({p.name for p in directory.glob('diff_*.png')}, {'diff_3.png', 'diff_4.png'})
        prune(directory, now=1005 + 4 * 86400)
        self.assertEqual(list(directory.glob('diff_*.png')), [])
        self.assertTrue(unrelated.exists())
        self.assertEqual(exported.read_bytes(), b'keep')
        with self.assertRaises(ValueError):
            prune(exported.parent)

    def test_image_write_failure_is_reported(self):
        target = self.runtime / 'debug/preprocessing/process_input.png'
        with self.assertRaises(OSError):
            self.io['write_debug_image'](target, object(), lambda *_: (False, None))

    def test_real_png_write_in_unicode_path(self):
        import cv2
        import numpy as np
        io = load_io(self.root / '中文目录/main.py')
        target = io['RUNTIME_DIR'] / 'debug/preprocessing/process_input.png'
        io['write_debug_image'](target, np.zeros((8, 8, 3), dtype=np.uint8), cv2.imencode)
        self.assertTrue(target.read_bytes().startswith(b'\x89PNG'))

    def test_original_ocr_construction_restored(self):
        self.assertFalse((PROJECT / 'runtime_paths.py').exists())
        tree = ast.parse((PROJECT / 'main.py').read_text(encoding='utf-8'))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'RapidOCR']
        self.assertEqual(len(calls), 2)
        self.assertEqual([{k.arg for k in call.keywords} for call in calls],
                         [{'intra_op_num_threads'}, {'det_limit_side_len', 'det_limit_type', 'intra_op_num_threads'}])
        self.assertFalse(any(isinstance(n, ast.FunctionDef) and n.name == 'prepare_ocr_config' for n in tree.body))


if __name__ == '__main__':
    unittest.main()
