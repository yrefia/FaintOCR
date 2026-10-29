"""API error reporting and input validation order, without real API calls."""
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages'))
from ia_learning_core import core

ERROR_BODY = json.dumps({'error': {'message': 'Model Not Exist', 'type': 'invalid_request_error'}})


class ApiErrorTests(unittest.TestCase):
    def events(self, session):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            events = session.poll()
            if events:
                return events
            time.sleep(.01)
        self.fail('worker produced no event')

    def test_http_error_keeps_api_message(self):
        error = urllib.error.HTTPError(core.API_URL, 400, 'Bad Request', {}, io.BytesIO(ERROR_BODY.encode()))
        self.addCleanup(error.close)
        with patch.object(core.urllib.request, 'urlopen', side_effect=error):
            with self.assertRaisesRegex(ValueError, r'HTTP 400：参数错误（Model Not Exist）'):
                core.request_annotations('test-key', {})

    def test_http_error_without_json_body_keeps_hint(self):
        error = urllib.error.HTTPError(core.API_URL, 503, 'Busy', {}, io.BytesIO(b'<html>busy</html>'))
        self.addCleanup(error.close)
        with patch.object(core.urllib.request, 'urlopen', side_effect=error):
            with self.assertRaisesRegex(ValueError, r'^HTTP 503：服务繁忙$'):
                core.request_annotations('test-key', {})

    def test_error_body_reaches_annotation_and_explanation(self):
        session = core.LearningCore(lambda key, payload: ERROR_BODY)
        self.addCleanup(session.close)
        session.annotate('Hello world.', 'Return JSON.', 'test-model', key='test-key')
        [event] = self.events(session)
        self.assertFalse(event['success'])
        self.assertEqual(event['data'], 'API 错误：Model Not Exist')
        with self.assertRaisesRegex(ValueError, 'Model Not Exist'):
            core.parse_explanation(ERROR_BODY)

    def test_malformed_annotation_body_is_reported_as_format_error(self):
        session = core.LearningCore(lambda key, payload: json.dumps({'unexpected': True}))
        self.addCleanup(session.close)
        session.annotate('Hello world.', 'Return JSON.', 'test-model', key='test-key')
        [event] = self.events(session)
        self.assertEqual(event['data'], 'API 返回格式无效。')

    def test_input_errors_win_over_missing_key(self):
        session = core.LearningCore()
        self.addCleanup(session.close)
        with patch.object(core, 'load_deepseek_api_key', side_effect=ValueError('缺少密钥')):
            with self.assertRaisesRegex(ValueError, '请输入英文原文'):
                session.annotate('', 'Return JSON.', 'test-model')
            with self.assertRaisesRegex(ValueError, '提示词须包含 JSON'):
                session.annotate('Hello world.', 'no format', 'test-model')
            with self.assertRaisesRegex(ValueError, '缺少密钥'):
                session.annotate('Hello world.', 'Return JSON.', 'test-model')


if __name__ == '__main__':
    unittest.main()
