"""Regression checks for explicit prompt loading and safe saves."""
import ast
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages'))
from ia_learning_core import PROMPT_DIR_ENV, PROMPT_ROOT, prompt_path
from ia_learning_core.core import PromptFile


class PromptFileTests(unittest.TestCase):
    def test_given_files_load_without_scanning(self):
        with patch.object(Path, 'glob', side_effect=AssertionError('Unexpected scan')), patch.object(
            Path, 'iterdir', side_effect=AssertionError('Unexpected scan')
        ):
            for name in ('annotation.txt', 'explanation.txt'):
                self.assertTrue(PromptFile(PROMPT_ROOT / name).read().strip())

    def test_missing_file_does_not_fall_back(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            path = Path(folder)
            (path / 'alternative.txt').write_text('alternative', encoding='utf-8')
            with self.assertRaises(FileNotFoundError):
                PromptFile(path / 'annotation.txt').read()

    def test_save_and_conflict_protection(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            path = Path(folder) / 'annotation.txt'
            path.write_text('original', encoding='utf-8-sig')
            prompt = PromptFile(path)
            self.assertEqual(prompt.read(), 'original')
            prompt.save('edited', previous='original')
            self.assertEqual(prompt.read(), 'edited')
            self.assertFalse(path.with_suffix('.txt.tmp').exists())
            path.write_text('external edit', encoding='utf-8')
            with self.assertRaises(ValueError):
                prompt.save('stale edit', previous='edited')
            self.assertEqual(prompt.read(), 'external edit')
            with self.assertRaises(ValueError):
                prompt.save('   ', previous='external edit')
            self.assertEqual(prompt.read(), 'external edit')

    def test_active_entry_point_uses_explicit_files(self):
        entry = ROOT / 'projects/faintocr-demo/main.py'
        tree = ast.parse(entry.read_text(encoding='utf-8'))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == 'PromptEditor']
        self.assertEqual(len(calls), 2)
        names = []
        for call in calls:
            argument = call.args[0]
            self.assertIsInstance(argument, ast.Call)
            self.assertEqual(ast.unparse(argument.func), 'prompt_path')
            names.append(ast.literal_eval(argument.args[0]))
        self.assertEqual(names, ['annotation.txt', 'explanation.txt'])
        with patch.object(Path, 'glob', side_effect=AssertionError('Unexpected scan')), patch.object(
            Path, 'iterdir', side_effect=AssertionError('Unexpected scan')
        ):
            for name in names:
                self.assertTrue(PromptFile(prompt_path(name)).read().strip())

    def test_override_directory_is_seeded_from_packaged_defaults(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder, patch.dict(os.environ, {PROMPT_DIR_ENV: folder}):
            target = prompt_path('explanation.txt')
            self.assertEqual(target, Path(folder) / 'explanation.txt')
            self.assertTrue(target.is_file())
            self.assertIn('JSON', target.read_text(encoding='utf-8'))
            target.write_text('local edit', encoding='utf-8')
            self.assertEqual(prompt_path('explanation.txt').read_text(encoding='utf-8'), 'local edit')
            with self.assertRaises(ValueError):
                prompt_path('missing.txt')
            with self.assertRaises(ValueError):
                prompt_path('../annotation.txt')

    def test_source_checkout_keeps_versioned_prompt_files(self):
        with patch.dict(os.environ, {PROMPT_DIR_ENV: ''}):
            self.assertEqual(prompt_path('annotation.txt'), PROMPT_ROOT / 'annotation.txt')
            self.assertEqual(prompt_path('explanation.txt'), PROMPT_ROOT / 'explanation.txt')

if __name__ == '__main__':
    unittest.main()
