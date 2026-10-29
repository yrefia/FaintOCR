"""Packaging guarantees: one dependency source, installable core, prompt resources."""
import ast
from pathlib import Path
import re
import sys
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / 'packages'
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))
from ia_learning_core import PROMPT_DIR_ENV, PROMPT_ROOT, USER_PROMPT_ROOT, prompt_path

DIRECT_REQUIREMENTS = {
    'demo': ROOT / 'requirements-demo.txt',
    'faintocr': ROOT / 'requirements-faintocr.txt',
}
UNUSED_QT_MODULES = {'pyside6', 'pyside6-addons', 'pyside6-webengine', 'pyside6-pdf'}


def normalize(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def parse_requirements(path):
    pins = {}
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or line.startswith('-'):
            continue
        name, _, version = line.partition('==')
        pins[normalize(name)] = version
    return pins


def project_metadata():
    return tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = project_metadata()
        cls.declared = {
            extra: {normalize(spec.partition('==')[0]): spec.partition('==')[2]
                    for spec in cls.metadata['project']['optional-dependencies'][extra]}
            for extra in DIRECT_REQUIREMENTS
        }
        cls.pins = {extra: parse_requirements(path) for extra, path in DIRECT_REQUIREMENTS.items()}
        cls.snapshot = parse_requirements(ROOT / 'requirements.txt')
        cls.files = {'requirements.txt': cls.snapshot}
        cls.files.update({path.name: cls.pins[extra] for extra, path in DIRECT_REQUIREMENTS.items()})

    def test_optional_dependencies_match_requirements_files(self):
        for extra in DIRECT_REQUIREMENTS:
            self.assertEqual(self.declared[extra], self.pins[extra], extra)

    def test_snapshot_covers_every_direct_dependency(self):
        for extra, pins in self.pins.items():
            for name, version in pins.items():
                self.assertEqual(self.snapshot.get(name), version, f'{name}（{extra}）与 requirements.txt 不一致')

    def test_unused_qt_modules_are_not_declared(self):
        for name, pins in self.files.items():
            self.assertFalse(set(pins) & UNUSED_QT_MODULES, name)

    def test_prompts_are_packaged_and_reachable(self):
        tool = self.metadata['tool']['setuptools']
        self.assertEqual(tool['package-dir'][''], 'packages')
        self.assertEqual(tool['packages'], ['ia_learning_core'])
        self.assertIn('prompts/*.txt', tool['package-data']['ia_learning_core'])
        for name in ('annotation.txt', 'explanation.txt'):
            self.assertTrue((PROMPT_ROOT / name).is_file())
            self.assertTrue(prompt_path(name).is_file())
        self.assertNotEqual(USER_PROMPT_ROOT, PROMPT_ROOT)
        self.assertEqual(PROMPT_DIR_ENV, 'IA_PROMPT_DIR')

    def test_core_imports_standard_library_only(self):
        tree = ast.parse((PACKAGES / 'ia_learning_core/core.py').read_text(encoding='utf-8'))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split('.')[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported.add(node.module.split('.')[0])
        third_party = {name for name in imported if name not in sys.stdlib_module_names}
        self.assertEqual(third_party, set())

    def test_entry_point_prefers_installed_package(self):
        entry = (ROOT / 'projects/faintocr-demo/main.py').read_text(encoding='utf-8')
        guard = "if importlib.util.find_spec('ia_learning_core') is None:\n    sys.path.insert("
        self.assertIn(guard, entry, '入口应先查找已安装的包，只在找不到时回退到源码路径')
        self.assertEqual(entry.count("/ 'packages'"), 1)


if __name__ == '__main__':
    unittest.main()
