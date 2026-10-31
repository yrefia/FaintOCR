"""Streaming protocol and incremental session regression tests, without network."""
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'packages'))
from ia_learning_core import core


def chunk(text=None, reason=None):
    return ('data: ' + json.dumps({'choices': [{'index': 0, 'delta': {'content': text},
                                               'finish_reason': reason}]}, ensure_ascii=False) + '\r\n\r\n').encode()


class StreamingTests(unittest.TestCase):
    def test_protocol_and_each_delta(self):
        response = io.BytesIO(b': keep-alive\r\n\r\n' + chunk() + chunk('中😀') + chunk('文')
                              + chunk(reason='length') + b'data: {"choices": [], "usage": {}}\n\n'
                              + b'data: [DONE]\n\n')
        updates = []
        body = core.read_annotation_stream(response, updates.append)
        self.assertEqual(updates, ['中😀', '中😀文'])
        self.assertEqual(core.extract_choice(body), ('中😀文', 'length'))

    def test_incomplete_and_error_streams(self):
        for body in (chunk('partial'), chunk(reason='stop'), b'data: [DONE]\n\n',
                     b'data: {bad}\n\n', b'data: {"error":{"message":"busy"}}\n\n'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                core.read_annotation_stream(io.BytesIO(body))

    def test_progress_parses_complete_sentence_before_completion(self):
        sentence = {'source': 'Hello.', 'annotated': '<#W1>Hello</#W1>.',
                    'annotations': [{'id': 'W1', 'category': 'Beyond Top 2000', 'canonical': 'hello'}]}
        raw = '{"sentences":[' + json.dumps(sentence)
        session = core.LearningCore()
        session.set_text('Hello.')
        session.annotation_pending = True
        token = (session.revision,)
        for text in ('{', raw):
            session._events.put({'kind': 'annotation', 'token': token, 'success': True,
                                 'partial': True, 'data': (text, None)})
            [event] = session.poll()
            self.assertEqual(event['document']['raw'], text)
            self.assertTrue(session.annotation_pending)
        self.assertEqual(len(session.document['items']), 1)
        session._events.put({'kind': 'annotation', 'token': token, 'success': True,
                             'data': (raw + ']}', 'stop')})
        session.poll()
        self.assertFalse(session.annotation_pending)
        session.set_text('New text.')
        session._events.put({'kind': 'annotation', 'token': token, 'success': True,
                             'partial': True, 'data': (raw, None)})
        self.assertEqual(session.poll(), [])
        self.assertEqual(session.document['source'], 'New text.')

    def test_default_transport_emits_progress_and_terminal(self):
        session = core.LearningCore()
        response = io.BytesIO(chunk('{') + chunk('}') + chunk(reason='stop') + b'data: [DONE]\n\n')
        with patch.object(core.urllib.request, 'urlopen', return_value=response):
            session.annotate('Hello.', 'JSON', 'test', key='key')
            events = []
            deadline = time.monotonic() + 2
            while session.annotation_pending and time.monotonic() < deadline:
                events.extend(session.poll())
                time.sleep(.01)
        self.assertEqual([e.get('partial', False) for e in events], [True, True, False])
        self.assertTrue(events[-1]['success'])
        self.assertTrue(response.closed)
        self.assertFalse(core.compose_explanation_payload('Hello.', None, 'JSON', 'test')['stream'])
