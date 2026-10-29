"""Local credential loading without real API calls or personal credentials."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages'))
from ia_learning_core import core


class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'deepseek_api_key.json'

    def write(self, value):
        self.path.write_text(json.dumps(value), encoding='utf-8-sig')

    def test_default_path_is_repository_root(self):
        self.assertEqual(core.DEEPSEEK_CONFIG_PATH, ROOT / 'deepseek_api_key.json')
        self.write({'api_key': '  test-only-key  '})
        with patch.object(core, 'DEEPSEEK_CONFIG_PATH', self.path):
            self.assertEqual(core.load_deepseek_api_key(), 'test-only-key')

    def test_missing_empty_or_wrong_type_is_actionable(self):
        with self.assertRaisesRegex(ValueError, '缺少'):
            core.load_deepseek_api_key(self.path)
        for value in ({}, [], None, {'api_key': 123}, {'api_key': ''}, {'api_key': '  '}):
            self.write(value)
            with self.assertRaisesRegex(ValueError, 'api_key'):
                core.load_deepseek_api_key(self.path)

    def test_invalid_config_does_not_echo_secret(self):
        secret = 'private-test-value'
        self.path.write_text('{"api_key": "' + secret, encoding='utf-8')
        with self.assertRaises(ValueError) as caught:
            core.load_deepseek_api_key(self.path)
        self.assertNotIn(secret, str(caught.exception))
        for key in ('test\nHeader: value', 'test key', '密钥'):
            self.write({'api_key': key})
            with self.assertRaisesRegex(ValueError, '无效字符'):
                core.load_deepseek_api_key(self.path)

    def test_core_reads_updated_key_before_each_request(self):
        received = []
        ready = threading.Event()
        def transport(key, payload):
            received.append(key)
            ready.set()
            return json.dumps({'choices': [{'message': {'content': '{"sentences": []}'}, 'finish_reason': 'stop'}]})
        session = core.LearningCore(transport, config_path=self.path)
        self.addCleanup(session.close)
        for index, key in enumerate(('test-first', 'test-second')):
            self.write({'api_key': key})
            ready.clear()
            session.annotate('English text ' + str(index), 'Return JSON.', 'test-model')
            self.assertTrue(ready.wait(2))
        self.assertEqual(received, ['test-first', 'test-second'])

    def test_missing_key_does_not_start_transport(self):
        with patch.object(core, 'request_annotations') as transport:
            session = core.LearningCore(config_path=self.path)
            self.addCleanup(session.close)
            with self.assertRaises(ValueError):
                session.annotate('English text', 'Return JSON.', 'test-model')
            transport.assert_not_called()
            self.assertFalse(session.annotation_pending)


if __name__ == '__main__':
    unittest.main()
