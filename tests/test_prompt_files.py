"""Regression checks for explicit prompt loading and safe saves."""
import ast
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages'))
from ia_learning_core import PROMPT_ROOT
from ia_learning_core.core import PromptFile


class PromptFileTests(unittest.TestCase):
    def test_given_files_load_without_scanning(self):
        with patch.object(Path, 'glob', side_effect=AssertionError('Unexpected scan')), patch.object(
            Path, 'iterdir', side_effect=AssertionError('Unexpected scan')
        ):
            for name in ('annotation.txt', 'explanation.txt'):
                self.assertTrue(PromptFile(PROMPT_ROOT / name).read().strip())

    def test_missing_file_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / 'alternative.txt').write_text('alternative', encoding='utf-8')
            with self.assertRaises(FileNotFoundError):
                PromptFile(path / 'annotation.txt').read()

    def test_save_and_conflict_protection(self):
        with tempfile.TemporaryDirectory() as folder:
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
        paths = [eval(compile(ast.Expression(call.args[0]), str(entry), 'eval'),
                      {'PROMPT_ROOT': PROMPT_ROOT}) for call in calls]
        self.assertEqual(set(paths), {PROMPT_ROOT / 'annotation.txt', PROMPT_ROOT / 'explanation.txt'})
        for path in paths:
            self.assertTrue(PromptFile(path).read().strip())

if __name__ == '__main__':
    unittest.main()
