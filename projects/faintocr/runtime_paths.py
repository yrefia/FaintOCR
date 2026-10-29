"""FaintOCR resource locations and bounded runtime file operations."""
from dataclasses import dataclass
import copy
from datetime import datetime
import hashlib
import os
from pathlib import Path
import re
import sys
import tempfile
import threading
import time


@dataclass(frozen=True)
class AppPaths:
    assets: Path
    runtime: Path

    @classmethod
    def resolve(cls, source_file, *, frozen=None, executable=None, bundle_dir=None, environ=None):
        env = os.environ if environ is None else environ
        frozen = getattr(sys, 'frozen', False) if frozen is None else frozen
        source = Path(source_file).resolve().parent
        if frozen:
            bundle = bundle_dir if bundle_dir is not None else getattr(sys, '_MEIPASS', None)
            assets = (Path(bundle).resolve() if bundle else Path(executable or sys.executable).resolve().parent) / 'assets'
            local = Path(env.get('LOCALAPPDATA') or Path.home() / 'AppData' / 'Local')
            runtime = local / 'IA' / 'FaintOCR' / 'runtime'
        else:
            assets, runtime = source / 'assets', source / 'runtime'
        override = env.get('FAINTOCR_RUNTIME_DIR')
        if override:
            runtime = Path(override).expanduser()
            if not runtime.is_absolute():
                raise ValueError('FAINTOCR_RUNTIME_DIR 必须是绝对路径。')
        return cls(assets.resolve(), runtime.resolve())

    @property
    def settings(self): return self.runtime / 'config' / 'settings.json'

    @property
    def dictionaries(self): return self.runtime / 'data' / 'dictionaries'

    @property
    def subtitles(self): return self.runtime / 'exports' / 'subtitles'

    @property
    def logs(self): return self.runtime / 'logs'

    @property
    def debug(self): return self.runtime / 'debug'

    @property
    def models(self): return self.runtime / 'cache' / 'models' / 'rapidocr_onnxruntime'

    def subtitle_file(self, date=None):
        return self.subtitles / f'{date or datetime.now():%Y-%m-%d}.txt'

    def dictionary_file(self, game, filename):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', game):
            raise ValueError('Invalid dictionary game directory')
        if re.fullmatch(r'TextMap[A-Z]+\.json', filename):
            category = 'raw'
        elif re.fullmatch(r'(?:CanonicalMap|MatchStatic)-[A-Z]+to[A-Z]+\.json', filename):
            category = 'derived'
        else:
            raise ValueError('Invalid dictionary filename')
        return self.dictionaries / game / category / filename


def atomic_write_bytes(path, content):
    """Write beside the destination and replace only after a successful flush."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', prefix=target.name + '.', suffix='.tmp',
                                         dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def cache_model(source, cache_dir):
    """Copy a bundled model into a content-addressed writable cache."""
    source = Path(source)
    content = source.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    target = Path(cache_dir) / digest / source.name
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        atomic_write_bytes(target, content)
    return target


def prepare_model_config(config, package_dir, paths):
    """Preserve the legacy engine config while moving model reads to runtime."""
    result = copy.deepcopy(config)
    for section in ('Det', 'Cls', 'Rec'):
        model = Path(result[section]['model_path'])
        if not model.is_absolute():
            model = Path(package_dir) / model
        result[section]['model_path'] = str(cache_model(model, paths.models))
    keys = result['Rec'].get('rec_keys_path')
    if keys:
        source = Path(keys)
        if not source.is_absolute():
            source = Path(package_dir) / source
        result['Rec']['rec_keys_path'] = str(cache_model(source, paths.models))
    return result


_debug_lock = threading.Lock()


def prune_debug_images(paths, directory, *, max_files=200, max_age_days=3, now=None):
    """Only remove generated PNGs in one of the two designated debug folders."""
    directory = Path(directory).resolve()
    allowed = [paths.debug / 'detection', paths.debug / 'preprocessing']
    if directory not in allowed or not directory.is_relative_to(paths.runtime):
        raise ValueError('Refusing to clean outside designated debug folders')
    if max_files < 0 or max_age_days < 0:
        raise ValueError('Debug retention limits must be nonnegative')
    if not directory.exists():
        return
    now = time.time() if now is None else now
    files = []
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file():
            continue
        if re.fullmatch(r'(?:diff_[0-9_]+|process_(?:input|cropped|[0-9]+))\.png', path.name):
            files.append((path.stat().st_mtime, path))
    for index, (modified, path) in enumerate(sorted(files, key=lambda item: item[0], reverse=True)):
        if index >= max_files or modified < now - max_age_days * 86400:
            path.unlink(missing_ok=True)


def write_debug_image(paths, path, image, encoder):
    target = Path(path).resolve()
    allowed = [paths.debug / 'detection', paths.debug / 'preprocessing']
    if target.parent not in allowed:
        raise ValueError('Debug image must be in a designated debug folder')
    with _debug_lock:
        target.parent.mkdir(parents=True, exist_ok=True)
        success, encoded = encoder('.png', image)
        if not success:
            raise OSError(f'无法写入调试图片：{target}')
        atomic_write_bytes(target, encoded.tobytes())
        prune_debug_images(paths, target.parent)
