"""Streaming protocol and incremental session regression tests, without network."""
import io
import json
from pathlib import Path
import sys
import time
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'packages'))
from ia_learning_core import core


def chunk(text=None, reason=None):
    return ('data: ' + json.dumps({'choices': [{'index': 0, 'delta': {'content': text},
                                               'finish_reason': reason}]}, ensure_ascii=False) + '\r\n\r\n').encode()


def publish(session, event):
    raw, reason = event['data']
    event['document'] = core.parse_annotation(session.document['source'], raw, partial=bool(event.get('partial')))
    event['finish_reason'] = reason
    session._publish_annotation(event)


class StreamingTests(unittest.TestCase):
    def test_mailbox_keeps_only_latest_and_poll_never_parses(self):
        session = core.LearningCore()
        session.set_text('Hello.')
        for index in range(400):
            event = {'kind': 'annotation', 'token': (session.revision,), 'success': True,
                     'partial': True, 'document': dict(session.document, raw=str(index))}
            session._publish_annotation(event)
        with patch.object(core, 'parse_annotation', side_effect=AssertionError('UI parsed')):
            [latest] = session.poll()
        self.assertEqual(latest['document']['raw'], '399')
        self.assertEqual(session.poll(), [])

    def test_render_at_annotated_string_boundary(self):
        source = 'Hello "world" 😀.'
        markup = '<#W1>Hello</#W1> "world" 😀.'
        prefix = '{"sentences":[{"source":' + json.dumps(source) + ',"annotated":'
        encoded = json.dumps(markup)
        for end in range(len(encoded)):
            self.assertEqual(core.parse_annotation(source, prefix + encoded[:end], partial=True)['items'], [])
        raw = prefix + encoded
        document = core.parse_annotation(source, raw, partial=True)
        [item] = document['items']
        self.assertEqual(item['ranges'], [(0, 5)])
        self.assertTrue(item['metadata_pending'])
        self.assertEqual(item['unit'], 'Hello')
        a, b = document['locations'][('sentences', 0, 'annotated')]
        self.assertEqual(json.loads(raw[a:b]), markup)
        self.assertTrue(core.item_json_ranges(item, raw, document['locations']))
        tail = ',"annotations":[{"id":"W1","category":"Beyond Top 2000","canonical":"hello"'
        [pending] = core.parse_annotation(source, raw + tail, partial=True)['items']
        self.assertTrue(pending['metadata_pending'])
        [ready] = core.parse_annotation(source, raw + tail + '}', partial=True)['items']
        self.assertNotIn('metadata_pending', ready)
        self.assertEqual(ready['ranges'], item['ranges'])
        final = raw + tail + '}]}]}'
        self.assertEqual(core.parse_annotation(source, final)['items'],
                         core.parse_annotation(source, final, partial=True)['items'])

    def test_preview_rejects_unaligned_or_unclosed_markup(self):
        for markup in ('<#W1>Hello.', '<#W1>Wrong</#W1>.'):
            raw = '{"sentences":[{"source":"Hello.","annotated":' + json.dumps(markup)
            self.assertEqual(core.parse_annotation('Hello.', raw, partial=True)['items'], [])

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
            publish(session, {'kind': 'annotation', 'token': token, 'success': True,
                                 'partial': True, 'data': (text, None)})
            [event] = session.poll()
            self.assertEqual(event['document']['raw'], text)
            self.assertTrue(session.annotation_pending)
        self.assertEqual(len(session.document['items']), 1)
        publish(session, {'kind': 'annotation', 'token': token, 'success': True,
                             'data': (raw + ']}', 'stop')})
        session.poll()
        self.assertFalse(session.annotation_pending)
        session.set_text('New text.')
        publish(session, {'kind': 'annotation', 'token': token, 'success': True,
                             'partial': True, 'data': (raw, None)})
        self.assertEqual(session.poll(), [])
        self.assertEqual(session.document['source'], 'New text.')

    def test_default_transport_emits_progress_and_terminal(self):
        session = core.LearningCore()
        response = io.BytesIO(chunk('{') + chunk('}') + chunk(reason='stop') + b'data: [DONE]\n\n')
        calls = []
        original = core.parse_annotation
        def parsed(*args, **kwargs):
            calls.append(threading.get_ident())
            return original(*args, **kwargs)
        with patch.object(core, 'parse_annotation', side_effect=parsed), patch.object(core.urllib.request, 'urlopen', return_value=response):
            session.annotate('Hello.', 'JSON', 'test', key='key')
            events = []
            deadline = time.monotonic() + 2
            while session.annotation_pending and time.monotonic() < deadline:
                events.extend(session.poll())
                time.sleep(.01)
        self.assertFalse(events[-1].get('partial', False))
        self.assertEqual(len(calls), 3)
        self.assertNotIn(threading.get_ident(), calls)
        self.assertTrue(events[-1]['success'])
        self.assertTrue(response.closed)
        self.assertFalse(core.compose_explanation_payload('Hello.', None, 'JSON', 'test')['stream'])
