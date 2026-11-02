"""IA 共享学习逻辑、固定提示词与可选 Qt 标注视图。

导入本包不会加载 Qt；只有 ``ia_learning_core.view`` 依赖 PySide6。
"""
from pathlib import Path
import os

PACKAGE_ROOT = Path(__file__).resolve().parent
# 包内提示词是默认值：源码检出时它本身就是可编辑、可提交的工作副本。
PROMPT_ROOT = PACKAGE_ROOT / 'prompts'
USER_PROMPT_ROOT = Path(os.environ.get('APPDATA') or Path.home() / '.config') / 'IA' / 'ia-learning-core' / 'prompts'
PROMPT_DIR_ENV = 'IA_PROMPT_DIR'
PROMPT_NAMES = ('annotation.txt', 'explanation.txt')


def is_source_checkout():
    """True when the package sits inside a Git work tree, so prompt edits stay versioned."""
    return (PACKAGE_ROOT.parents[1] / '.git').exists()


def prompt_dir():
    """Directory holding the editable prompt files.

    ``IA_PROMPT_DIR`` wins; a source checkout keeps editing the versioned copies;
    an installed package uses a per-user directory seeded from the packaged defaults.
    """
    override = os.environ.get(PROMPT_DIR_ENV, '').strip()
    if override:
        return Path(override)
    return PROMPT_ROOT if is_source_checkout() else USER_PROMPT_ROOT


def prompt_path(name):
    """Absolute path of one editable prompt file, copying the default on first use."""
    if Path(name).name != name:
        raise ValueError('提示词名称不能包含路径分隔符。')
    directory = prompt_dir()
    path = directory / name
    if directory == PROMPT_ROOT:
        return path
    if not path.is_file():
        if name not in PROMPT_NAMES:
            raise ValueError(f'未知提示词：{name}')
        directory.mkdir(parents=True, exist_ok=True)
        path.write_text((PROMPT_ROOT / name).read_text(encoding='utf-8-sig'), encoding='utf-8')
    return path
