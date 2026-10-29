"""Explicit FaintOCR integration check; temporary config, generated image, no game data.

Run normally for offscreen Qt checks; --native displays transient native windows.
--capture additionally grabs a 16x16 screen region without saving its contents.
OCR models remain managed by RapidOCR and may download on first use.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--capture', action='store_true')
    args = parser.parse_args()
    os.environ['QT_QPA_PLATFORM'] = 'windows' if args.native else 'offscreen'
    import numpy as np
    from check_rapidocr import _render_target
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('faintocr_integration', root / 'projects/faintocr/main.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    app = module.QApplication([])
    errors = []
    original_hook = sys.excepthook
    sys.excepthook = lambda *event: errors.append(event)
    try:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            module.RUNTIME_DIR = directory / 'runtime'
            module.Config.USER_CONFIG_FILE = str(module.RUNTIME_DIR / 'config/settings.json')
            module.Config.TEXTMAP_ROOT = str(module.RUNTIME_DIR / 'data/dictionaries')
            module.setup_logging()
            module.load_system_fonts()
            module.set_windows_app_user_model_id()
            ui = module.FaintOCRApplication()
            try:
                # Onboarding and GitLab are outside this local compatibility check.
                with patch.object(ui, 'maybe_show_tutorial'), patch.object(
                    module.requests, 'get', side_effect=AssertionError('Unexpected GitLab request')
                ):
                    if args.native:
                        ui.show()
                    else:
                        ui.ball.show()
                        ui.subtitle.show()
                    ui.settings.show()
                    app.processEvents()
                    for name in ('ball', 'subtitle', 'settings'):
                        assert not getattr(ui, name).grab().isNull(), name
                    print('PASS: native Qt rendering' if args.native else 'PASS: offscreen Qt rendering')
                    assert ui.controller.ocr_engine_std is not None
                    assert ui.controller.ocr_engine_light is not None
                    image_path = Path(_render_target(directory / 'target.png'))
                    bgr = module.cv2.imdecode(np.frombuffer(image_path.read_bytes(), dtype=np.uint8), module.cv2.IMREAD_COLOR)
                    worker = module.OCRWorker({})
                    for name in ('std', 'light'):
                        text = worker.run_rapidocr(getattr(ui.controller, 'ocr_engine_' + name), bgr,
                                                  'Genshin Impact', 'CHS', 0)
                        assert 'rapidocr' in text.lower() and '中文' in text, text
                        print('PASS: real bilingual inference,', name)
                    finished = []
                    ui.controller.ocr_result_signal.connect(lambda *event: finished.append(event))
                    assert ui.controller.request_ocr_image(bgr)
                    deadline = time.monotonic() + 30
                    while not finished and time.monotonic() < deadline:
                        app.processEvents()
                        time.sleep(.01)
                    assert finished and finished[0][0], finished
                    text = finished[0][1]
                    assert 'rapidocr' in text.lower(), text
                    assert 'rapidocr' in ui.subtitle.subtitle_text.lower()
                    output = ui.write_subtitle_to_file(text)
                    assert output and 'RapidOCR' in Path(output).read_text(encoding='utf-8')
                    print('PASS: threaded OCR -> subtitle -> UTF-8 export')
                    if args.capture:
                        with module.mss.MSS() as capture:
                            screen = capture.monitors[1]
                            shot = capture.grab({'left': screen['left'], 'top': screen['top'],
                                                 'width': 16, 'height': 16})
                            assert np.asarray(shot).shape == (16, 16, 4)
                        print('PASS: native MSS capture (not saved)')
            finally:
                ui.cleanup()
                for widget in app.topLevelWidgets():
                    widget.close()
                app.processEvents()
                module.logger.complete()
                module.logger.remove()
            assert Path(module.Config.USER_CONFIG_FILE).is_file()
            print('PASS: settings save and shutdown')
    finally:
        sys.excepthook = original_hook
    for error in errors:
        original_hook(*error)
    assert not errors, 'Qt callback errors occurred'
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
