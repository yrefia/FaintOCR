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
    def test_source_response_preserves_recovery_and_streaming(self):
        fixture = json.loads((Path(__file__).parent / 'fixtures/missing_hash_annotation.json').read_text(encoding='utf-8'))
        for sentence in fixture['response']['sentences']:
            sentence['source'] = core.RANGE_TAG_RE.sub('', sentence['annotated'])
        raw = json.dumps(fixture['response'], ensure_ascii=False)
        for partial in (False, True):
            doc = core.parse_annotation(fixture['input'], raw, partial=partial)
            self.assertEqual(len(doc['items']), 30)
            self.assertTrue(any('标签格式不规范' in str(w) for w in doc['warnings']))
        prefix = '{"sentences":[{"source":"Hello.","annotated":'
        waiting = core.parse_annotation('Hello.', prefix, partial=True)
        self.assertEqual(waiting['items'], [])
        self.assertEqual(waiting['warnings'], [])
        ready = core.parse_annotation('Hello.', prefix + '"<#W1>Hello</W1>."', partial=True)
        self.assertEqual(ready['items'][0]['ranges'], [(0, 5)])
        mismatched = core.parse_annotation('Hello.', prefix + '"<#W1>World</W1>."', partial=True)
        self.assertEqual(mismatched['items'], [])

    def test_real_missing_hash_response_preserves_all_six_sentences(self):
        fixture = json.loads((Path(__file__).parent / 'fixtures/missing_hash_annotation.json').read_text(encoding='utf-8'))
        raw = json.dumps(fixture['response'], ensure_ascii=False)
        document = core.parse_annotation(fixture['input'], raw)
        self.assertEqual(len(document['items']), 30)
        self.assertEqual({i['annotation']['sentence_index'] for i in document['items']}, set(range(1, 7)))
        expression = next(i for i in document['items'] if i['annotation']['sentence_index'] == 5
                          and i['annotation']['id'] == 'E1')
        a, b = expression['ranges'][0]
        self.assertEqual(fixture['input'][a:b], 'come to terms with')
        self.assertTrue(any('标签格式不规范' in str(w) for w in document['warnings']))
        self.assertFalse(any('未覆盖原文末尾' in str(w) for w in document['warnings']))

    def test_typo_in_tag_keeps_ranges_and_original_json_locations(self):
        for markup in ('<#W1>Hello</W1>.', '<W1>Hello</#W1>.', '< #W1 >Hello< / W1 >.'):
            raw = json.dumps({'sentences': [{'annotated': markup, 'annotations': [
                {'id': 'W1', 'category': 'Beyond Top 2000', 'canonical': 'hello'}]}]})
            for partial in (False, True):
                doc = core.parse_annotation('Hello.', raw, partial=partial)
                [item] = doc['items']
                self.assertEqual(item['ranges'], [(0, 5)])
                self.assertEqual(doc['raw'], raw)
                self.assertTrue(any('标签格式不规范' in str(w) for w in doc['warnings']))
                self.assertTrue(core.item_json_ranges(item, raw, doc['locations']))

    def test_broken_range_does_not_hide_other_ranges_or_later_sentence(self):
        value = {'sentences': [
            {'annotated': '<#W1>Hello <#W2>world</#W2>.', 'annotations': []},
            {'annotated': '<#W1>Goodbye</#W1>.', 'annotations': []}]}
        doc = core.parse_annotation('Hello world. Goodbye.', json.dumps(value))
        self.assertEqual([i['ranges'] for i in doc['items']], [[(6, 11)], [(13, 20)]])
        value['sentences'][0]['annotated'] = 'Changed text.'
        doc = core.parse_annotation('Hello world. Goodbye.', json.dumps(value))
        self.assertEqual([i['ranges'] for i in doc['items']], [[(13, 20)]])
        self.assertTrue(any('恢复定位' in str(w) for w in doc['warnings']))

    def test_missing_metadata_keeps_verified_visual_range(self):
        for records in (None, [], [{'id': 'W1'}]):
            raw = json.dumps({'sentences': [{'annotated': '<#W1>Hello</#W1>.', 'annotations': records}]})
            [item] = core.parse_annotation('Hello.', raw)['items']
            self.assertEqual(item['ranges'], [(0, 5)])
            self.assertEqual(item['category'], 'word')
            self.assertTrue(item['metadata_pending'])

    def test_sourceless_stream_and_repeated_sentences(self):
        sentence = {'annotated': '<#W1>Hello</#W1>.',
                    'annotations': [{'id': 'W1', 'category': 'Beyond Top 2000', 'canonical': 'hello'}]}
        source = 'Hello. Hello.'
        raw = json.dumps({'sentences': [sentence, sentence]})
        items = core.parse_annotation(source, raw)['items']
        self.assertEqual([item['ranges'] for item in items], [[(0, 5)], [(7, 12)]])
        self.assertEqual([item['annotation']['source'] for item in items], ['Hello.', 'Hello.'])
        partial = '{"sentences":[{"annotated":"<#W1>Hello</#W1>."'
        [item] = core.parse_annotation(source, partial, partial=True)['items']
        self.assertTrue(item['metadata_pending'])
        self.assertEqual(item['ranges'], [(0, 5)])
        # Complete sentences are recoverable even if the enclosing array is truncated.
        self.assertEqual(core.parse_annotation(source, raw[:-2])['items'], items)

    def test_sourceless_does_not_guess_original_text(self):
        sentence = {'annotated': '<#W1>Hello</#W1>.',
                    'annotations': [{'id': 'W1', 'category': 'Beyond Top 2000', 'canonical': 'hello'}]}
        raw = json.dumps({'sentences': [sentence]})
        for source in ('Hallo.', 'Missing. Hello. Hello.', '<#W1>Hello</#W1>.'):
            result = core.parse_annotation(source, raw)
            self.assertEqual(result['items'], [])
            self.assertTrue(result['warnings'])

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
