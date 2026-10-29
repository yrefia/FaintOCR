"""Runtime I/O checks without importing the unavailable legacy OCR stack."""
import ast
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects' / 'faintocr'
sys.path.insert(0, str(PROJECT))
from runtime_paths import (
    AppPaths, atomic_write_bytes, cache_model, prepare_model_config,
    prune_debug_images, write_debug_image,
)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name).resolve()
        self.paths = AppPaths(self.root / 'assets', self.root / 'runtime')

    def test_source_paths_ignore_current_directory(self):
        source = self.root / 'project' / 'main.py'
        with patch('os.getcwd', return_value=str(self.root / 'elsewhere')):
            paths = AppPaths.resolve(source, frozen=False, environ={})
        self.assertEqual(paths.assets, source.parent / 'assets')
        self.assertEqual(paths.runtime, source.parent / 'runtime')
        self.assertFalse(paths.runtime.exists())

    def test_frozen_resources_and_writable_data_are_separate(self):
        for bundle in (self.root / '_MEI123', self.root / 'install' / '_internal', None):
            paths = AppPaths.resolve(self.root / 'main.py', frozen=True,
                                     executable=self.root / 'install' / 'faintocr.exe',
                                     bundle_dir=bundle, environ={'LOCALAPPDATA': str(self.root / 'user')})
            expected = (bundle or self.root / 'install') / 'assets'
            self.assertEqual(paths.assets, expected)
            self.assertEqual(paths.runtime, self.root / 'user/IA/FaintOCR/runtime')
            self.assertFalse(paths.runtime.is_relative_to(self.root / 'install'))

    def test_absolute_override_and_relative_rejection(self):
        for frozen in (False, True):
            paths = AppPaths.resolve(PROJECT / 'main.py', frozen=frozen,
                                     environ={'FAINTOCR_RUNTIME_DIR': str(self.root / 'portable')})
            self.assertEqual(paths.runtime, self.root / 'portable')
            with self.assertRaisesRegex(ValueError, '绝对路径'):
                AppPaths.resolve(PROJECT / 'main.py', frozen=frozen,
                                 environ={'FAINTOCR_RUNTIME_DIR': 'runtime'})

    def test_dictionary_separation_and_path_validation(self):
        self.assertEqual(self.paths.dictionary_file('genshin-impact', 'TextMapCHS.json'),
                         self.paths.dictionaries / 'genshin-impact/raw/TextMapCHS.json')
        self.assertEqual(self.paths.dictionary_file('star-rail', 'CanonicalMap-CHStoEN.json'),
                         self.paths.dictionaries / 'star-rail/derived/CanonicalMap-CHStoEN.json')
        for game, name in [('../escape', 'TextMapCHS.json'), ('game', '../evil.json'), ('game', 'unknown.json')]:
            with self.assertRaises(ValueError):
                self.paths.dictionary_file(game, name)

    def test_subtitle_date_rollover(self):
        self.assertEqual(self.paths.subtitle_file(datetime(2026, 10, 29)).name, '2026-10-29.txt')
        self.assertEqual(self.paths.subtitle_file(datetime(2026, 10, 30)).name, '2026-10-30.txt')
        self.assertEqual(self.paths.subtitle_file().parent, self.paths.subtitles)

    def test_atomic_write_preserves_previous_file_on_failure(self):
        target = self.paths.settings
        atomic_write_bytes(target, b'original')
        with patch('runtime_paths.os.replace', side_effect=OSError('replace failed')):
            with self.assertRaises(OSError):
                atomic_write_bytes(target, b'new')
        self.assertEqual(target.read_bytes(), b'original')
        self.assertEqual(list(target.parent.glob('*.tmp')), [])
        atomic_write_bytes(target, b'new')
        self.assertEqual(target.read_bytes(), b'new')

    def test_model_cache_preserves_source_and_repairs_corruption(self):
        source = self.root / 'bundled.onnx'
        source.write_bytes(b'model-one')
        cached = cache_model(source, self.paths.models)
        self.assertTrue(cached.is_relative_to(self.paths.models))
        self.assertEqual(cached.read_bytes(), b'model-one')
        cached.write_bytes(b'corrupted')
        self.assertEqual(cache_model(source, self.paths.models).read_bytes(), b'model-one')
        source.write_bytes(b'model-two')
        updated = cache_model(source, self.paths.models)
        self.assertNotEqual(cached, updated)
        self.assertEqual(cached.read_bytes(), b'model-one')

    def test_legacy_config_maps_models_and_keys_to_cache(self):
        package = self.root / 'package'
        package.mkdir()
        config = {'Global': {'text_score': .5}}
        for part in ('Det', 'Cls', 'Rec'):
            (package / (part + '.onnx')).write_bytes(part.encode())
            config[part] = {'model_path': part + '.onnx'}
        (package / 'keys.txt').write_text('characters', encoding='utf-8')
        config['Rec']['rec_keys_path'] = 'keys.txt'
        configured = prepare_model_config(config, package, self.paths)
        for part in ('Det', 'Cls', 'Rec'):
            path = Path(configured[part]['model_path'])
            self.assertTrue(path.is_relative_to(self.paths.models))
            self.assertEqual(path.read_bytes(), part.encode())
        self.assertEqual(Path(configured['Rec']['rec_keys_path']).read_text(), 'characters')
        self.assertEqual(config['Det']['model_path'], 'Det.onnx')
        self.assertEqual(configured['Global'], config['Global'])

    def test_debug_cleanup_preserves_other_data(self):
        directory = self.paths.debug / 'detection'
        directory.mkdir(parents=True)
        for index in range(5):
            path = directory / f'diff_{index}.png'
            path.write_bytes(b'image')
            os.utime(path, (1000 + index, 1000 + index))
        exported = self.paths.subtitle_file(datetime(2026, 10, 29))
        atomic_write_bytes(exported, b'keep subtitle')
        atomic_write_bytes(self.paths.settings, b'keep settings')
        unrelated = directory / 'personal.png'
        unrelated.write_bytes(b'keep')
        prune_debug_images(self.paths, directory, max_files=2, max_age_days=3, now=1005)
        self.assertEqual({p.name for p in directory.glob('diff_*.png')}, {'diff_3.png', 'diff_4.png'})
        prune_debug_images(self.paths, directory, now=1005 + 4 * 86400)
        self.assertEqual(list(directory.glob('diff_*.png')), [])
        self.assertTrue(unrelated.exists())
        self.assertEqual(exported.read_bytes(), b'keep subtitle')
        self.assertEqual(self.paths.settings.read_bytes(), b'keep settings')
        with self.assertRaises(ValueError):
            prune_debug_images(self.paths, self.paths.subtitles)

    def test_image_write_failure_is_not_silent(self):
        target = self.paths.debug / 'preprocessing/process_input.png'
        with self.assertRaisesRegex(OSError, '无法写入'):
            write_debug_image(self.paths, target, object(), lambda *_: (False, None))
        with self.assertRaises(ValueError):
            write_debug_image(self.paths, self.paths.subtitles / 'image.png', object(), lambda *_: (True, None))

    def test_real_png_write_in_unicode_path(self):
        import cv2
        import numpy as np
        paths = AppPaths(self.root / 'assets', self.root / '中文运行目录')
        target = paths.debug / 'preprocessing/process_input.png'
        write_debug_image(paths, target, np.zeros((8, 8, 3), dtype=np.uint8), cv2.imencode)
        self.assertTrue(target.read_bytes().startswith(b'\x89PNG'))

    def test_main_config_and_dictionary_wiring(self):
        tree = ast.parse((PROJECT / 'main.py').read_text(encoding='utf-8'))
        nodes = [node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name in ('I18n', 'Config', 'TextMapLoader', 'UserConfigManager')]
        fake_json = types.SimpleNamespace(loads=json.loads, OPT_INDENT_2=2,
                                         dumps=lambda value, **_: json.dumps(value).encode())
        logger = types.SimpleNamespace(error=lambda *_: None, warning=lambda *_: None)
        namespace = {'PATHS': self.paths, 'os': os, 'Path': Path, 'datetime': datetime,
                     'orjson': fake_json, 'atomic_write_bytes': atomic_write_bytes,
                     'logger': logger, 'I18n': types.SimpleNamespace(get=lambda *args: str(args))}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<main I/O classes>', 'exec'), namespace)
        config = namespace['Config']
        self.assertEqual(Path(config.USER_CONFIG_FILE), self.paths.settings)
        self.assertFalse(config.OCR['DETECT']['debug'])
        self.assertFalse(config.OCR['PRE_OCR_CROP_RULES']['debug'])
        loader = namespace['TextMapLoader']
        raw = Path(loader.get_file_path('Genshin Impact', 'TextMapCHS.json'))
        derived = Path(loader.get_file_path('Genshin Impact', 'MatchStatic-CHStoEN.json'))
        self.assertEqual(raw.parent.name, 'raw')
        self.assertEqual(derived.parent.name, 'derived')
        self.assertTrue(loader._save_file_atomic(str(derived), {'test': 'value'}))
        self.assertEqual(json.loads(derived.read_bytes()), {'test': 'value'})
        manager = namespace['UserConfigManager']
        manager.save(manager.default_config())
        self.assertTrue(self.paths.settings.is_file())
        self.assertIsInstance(manager.load(), dict)


if __name__ == '__main__':
    unittest.main()
