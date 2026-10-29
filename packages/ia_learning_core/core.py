"""Shared learning logic, API v1. Pure Python: no Qt or application imports.
"""
from pathlib import Path
import copy
import json
import os
import queue
import re
import threading
import time
from typing import TypedDict
import urllib.error
import urllib.request

# 密钥解析与源码目录布局解耦。优先级：
#   显式参数 > DEEPSEEK_API_KEY > IA_LEARNING_CONFIG_PATH > 用户配置目录 > 仓库根目录旧位置。
API_KEY_ENV = 'DEEPSEEK_API_KEY'
CONFIG_PATH_ENV = 'IA_LEARNING_CONFIG_PATH'
USER_CONFIG_ROOT = Path(os.environ.get('APPDATA') or Path.home() / '.config') / 'IA' / 'ia-learning-core'
USER_CONFIG_PATH = USER_CONFIG_ROOT / 'deepseek_api_key.json'
# 源码检出时的历史位置，仅作为最后一个候选。
DEEPSEEK_CONFIG_PATH = Path(__file__).resolve().parents[2] / 'deepseek_api_key.json'


def config_candidates():
    """Credential files in priority order; the first existing file wins.

    A set ``IA_LEARNING_CONFIG_PATH`` is binding: ``load_deepseek_api_key`` uses only that file.
    """
    configured = os.environ.get(CONFIG_PATH_ENV, '').strip()
    if configured:
        yield Path(configured)
    yield USER_CONFIG_PATH
    yield DEEPSEEK_CONFIG_PATH


def _validated_key(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('请在 deepseek_api_key.json 中填写非空字符串 api_key、设置 DEEPSEEK_API_KEY 环境变量，或使用离线演示。')
    key = value.strip()
    if any(ord(char) < 33 or ord(char) > 126 for char in key):
        raise ValueError('密钥含有无效字符；请检查 deepseek_api_key.json 或 DEEPSEEK_API_KEY。')
    return key


def load_deepseek_api_key(config_path=None):
    """Resolve one credential without exposing file contents in error messages."""
    if config_path is None:
        environment_key = os.environ.get(API_KEY_ENV, '').strip()
        if environment_key:
            return _validated_key(environment_key)
    configured = os.environ.get(CONFIG_PATH_ENV, '').strip()
    if config_path is not None:
        path = Path(config_path)
    elif configured:
        # 显式指定的文件缺失时直接报错，不回退到其他候选，以免悄悄用上另一把密钥。
        path = Path(configured)
        if not path.is_file():
            raise ValueError(f'{CONFIG_PATH_ENV} 指向的 {path} 不存在，请修正该变量或创建文件。')
    else:
        path = next((candidate for candidate in config_candidates() if candidate.is_file()), None)
    if path is None:
        raise ValueError(f'缺少 deepseek_api_key.json：请设置 {API_KEY_ENV}，或在 {USER_CONFIG_PATH} '
                         '或仓库根目录创建该文件并填写 api_key。')
    try:
        content = path.read_text(encoding='utf-8-sig')
    except FileNotFoundError:
        raise ValueError('缺少 deepseek_api_key.json，请创建并填写 api_key。') from None
    except (OSError, UnicodeError):
        raise ValueError('无法读取 deepseek_api_key.json，请检查文件权限和 UTF-8 编码。') from None
    try:
        settings = json.loads(content)
    except ValueError:
        raise ValueError('deepseek_api_key.json 不是有效的 JSON，请检查格式。') from None
    if not isinstance(settings, dict):
        raise ValueError('请在 deepseek_api_key.json 中填写非空字符串 api_key，或使用离线演示。')
    return _validated_key(settings.get('api_key'))


API_VERSION = 1

API_URL = "https://api.deepseek.com/chat/completions"
CATEGORIES = {
    "grammar": ("句法结构 · 背景", "#7941b1", "#f2eafa"),
    "phrase": ("表达与词块 · 下划线", "#80659e", ""),
    "word": ("单词 · 粗体", "#30343b", ""),
}
MAX_EXPLANATION_CHARS = 320
# 5.4.3 用 8192 / 60 秒：6000 字符原文实测输出约 5.6k–8.2k tokens，会被截断（finish_reason=length）；
# deepseek-v4-pro 约 160 tokens/秒，16384 tokens 需约 100 秒，因此一并放宽超时。
ANNOTATION_MAX_TOKENS = 16384
REQUEST_TIMEOUT = 180
PHRASE_UNDERLINE_COLOR = "#7BDCE8"

def build_payload(english, prompt, model):
    if not re.search(r"[A-Za-z]", english):
        raise ValueError("请输入英文原文。")
    if len(english) > 6000:
        raise ValueError("这是短文本标注工具，单个输入框请控制在 6000 字符内。")
    if not prompt.strip() or "json" not in prompt.lower():
        raise ValueError("提示词须包含 JSON 格式约定。")
    if not model.strip():
        raise ValueError("请填写模型名称。")
    return compose_annotation_payload(english, prompt, model)


def compose_annotation_payload(english, prompt, model):
    """Compose without validation so the UI can show incomplete drafts too."""
    return {"model": model.strip(), "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps({"english": english}, ensure_ascii=False)},
    ], "thinking": {"type": "disabled"}, "stream": False,
        "response_format": {"type": "json_object"}, "max_tokens": ANNOTATION_MAX_TOKENS}


TAG_CATEGORIES = {
    'W': {'Less Common Senses', 'Beyond Top 2000'},
    'E': {'Idioms & Conventional Expressions', 'Formulaic Expressions', 'Lexical Frames',
          'Multiword Verbs', 'Fixed Phrases', 'Collocations'},
    'S': {'Subjunctive', 'Subjunctive / Irrealis', 'Emphatic Constructions', 'Inversion', 'Ellipsis', 'Fronting', 'Parentheticals'},
}
# 标签字母到层级键（W 单词、E 表达、S 句法）；CATEGORIES 与 view 都按层级键取用。
LAYER_KEYS = {'W': 'word', 'E': 'phrase', 'S': 'grammar'}
TAG_RE = re.compile(r'<(/?)#([WES][1-9][0-9]*)>')


class AnnotationError(ValueError):
    def __init__(self, message, path=(), position=None, identity=''):
        super().__init__(message)
        self.path, self.position, self.identity = path, position, identity
        self.errors = [self]


def json_locations(raw):
    """Index JSON value paths without searching repeated sentence/ID strings."""
    decoder, locations = json.JSONDecoder(), {}
    def skip(i):
        while i < len(raw) and raw[i].isspace(): i += 1
        return i
    def walk(i, path):
        i = skip(i); start = i
        if raw[i] == '{':
            i = skip(i+1)
            while raw[i] != '}':
                key, i = decoder.raw_decode(raw, i)
                i = walk(skip(i)+1, path+(key,)); i = skip(i)
                if raw[i] != ',': break
                i = skip(i+1)
            i += 1
        elif raw[i] == '[':
            i = skip(i+1); index = 0
            while raw[i] != ']':
                i = walk(i,path+(index,)); index += 1; i = skip(i)
                if raw[i] != ',': break
                i = skip(i+1)
            i += 1
        else:
            _, i = decoder.raw_decode(raw,i)
        locations[path] = (start,i)
        return i
    walk(0,())
    return locations


def utf16_offsets(text):
    """offsets[i] is the UTF-16 index of Python index i in text (Qt positions are UTF-16)."""
    offsets = [0]
    for char in text:
        offsets.append(offsets[-1] + (2 if ord(char) > 0xffff else 1))
    return offsets


def decoded_boundaries(raw, start, end):
    """Map decoded string characters to raw JSON, including escaped surrogate pairs."""
    positions = []; i = start+1
    while i < end-1:
        positions.append(i)
        if raw[i] != chr(92): i += 1; continue
        if raw[i+1] != 'u': i += 2; continue
        code = int(raw[i+2:i+6],16); i += 6
        if 0xD800 <= code <= 0xDBFF and raw[i:i+2] == chr(92)+'u':
            low = int(raw[i+2:i+6],16)
            if 0xDC00 <= low <= 0xDFFF: i += 6
    positions.append(end-1)
    return positions


def decode_best_effort(raw):
    """Read complete JSON values; salvage complete sentences, never invent missing text.

    All locations continue to refer to the unmodified editor text, including fences.
    """
    decoder=json.JSONDecoder()
    def notice(message,start=0,end=None):
        issue=AnnotationError(message)
        issue.raw_range=(start,min(start+1,len(raw)) if end is None else end)
        return issue
    def indexed(value,start,end):
        locations={p:(a+start,b+start) for p,(a,b) in json_locations(raw[start:end]).items()}
        issues=[]
        if isinstance(value,list):
            value={'sentences':value}
            locations={('sentences',)+p:bounds for p,bounds in locations.items()}
            issues.append(notice('顶层为数组，已作为 sentences 读取。',start,end))
        elif isinstance(value,dict) and {'source','annotated','annotations'} <= value.keys():
            value={'sentences':[value]}
            locations={('sentences',0)+p:bounds for p,bounds in locations.items()}
            issues.append(notice('顶层为单句对象，已作为一个句子读取。',start,end))
        return value,locations,issues
    try:
        value=json.loads(raw)
        return indexed(value,0,len(raw))
    except (ValueError,RecursionError) as exc:
        pos=getattr(exc,'pos',0)
        initial=notice('JSON 提醒：'+str(exc)+'；尝试保留完整可读内容。',pos)
    # A single fenced/prose-wrapped document is recoverable without rewriting JSON.
    for match in re.finditer(r'[\[{]',raw):
        try: candidate,end=decoder.raw_decode(raw,match.start())
        except (ValueError,RecursionError): continue
        if isinstance(candidate,dict) and isinstance(candidate.get('sentences'),list):
            value,locations,notes=indexed(candidate,match.start(),end)
            return value,locations,[initial,notice('已提取完整 JSON，忽略前后附加内容。',match.start(),end)]+notes
    # Only recover explicit complete sentence objects, not incomplete properties.
    array=re.search(r'"sentences"\s*:\s*\[',raw)
    groups=[]; locations={}
    if array:
        cursor=array.end()
        while cursor < len(raw):
            char=raw[cursor]
            if char=='"':
                try: _,cursor=decoder.raw_decode(raw,cursor)
                except ValueError: break
                continue
            if char=='{':
                try: candidate,end=decoder.raw_decode(raw,cursor)
                except (ValueError,RecursionError):
                    cursor+=1; continue
                if isinstance(candidate,dict) and {'source','annotated','annotations'} <= candidate.keys():
                    index=len(groups);groups.append(candidate)
                    for path,(a,b) in json_locations(raw[cursor:end]).items():
                        locations[('sentences',index)+path]=(cursor+a,cursor+b)
                cursor=end;continue
            cursor+=1
    if groups:
        return {'sentences':groups},locations,[initial,notice(f'已恢复 {len(groups)} 个完整句子对象；不完整部分未补猜。',array.start(),array.end())]
    return None,{},[initial,notice('没有可恢复的完整 JSON 标注，显示本次原文。',0,len(raw))]


def resolve_items(value, text, issues=None) -> 'list[Item]':
    """Recover independently locatable annotations; never invent missing boundaries."""
    issues = issues if issues is not None else []
    def warn(message, path=(), position=None, identity=''):
        issues.append(AnnotationError(message,path,position,identity))
    if not isinstance(value,dict) or not isinstance(value.get('sentences'),list):
        warn('未找到 sentences 数组，无法读取标注。')
        return []
    resolved, cursor = [], 0
    for index, group in enumerate(value['sentences']):
        path = ('sentences',index)
        def note(message, field='annotated', position=None, identity=''):
            warn(f'第 {index+1} 句：{message}',path+(field,),position,identity)
        if not isinstance(group,dict):
            warn(f'第 {index+1} 句不是对象，已跳过。',path); continue
        source, markup, records = (group.get(k) for k in ('source','annotated','annotations'))
        if not isinstance(source,str) or not source:
            note('缺少有效 source，已跳过。','source'); continue
        # Prefer the next exact source position; fallback only when unambiguous.
        offset = cursor
        if not text.startswith(source,offset):
            while offset < len(text) and text[offset].isspace(): offset += 1
        if not text.startswith(source,offset):
            matches = [m.start() for m in re.finditer('(?='+re.escape(source)+')',text)]
            later = [p for p in matches if p >= cursor]
            candidates = later if later else matches
            if len(candidates) != 1:
                note('source 无法唯一对应原文，已跳过此句。','source'); continue
            offset = candidates[0]
            note('句子遗漏或顺序不一致；已按唯一原文位置定位。','source')
        cursor = max(cursor,offset+len(source))
        if not isinstance(markup,str):
            note('缺少有效 annotated，已跳过此句。'); continue
        if not isinstance(records,list):
            note('annotations 不是数组，已跳过此句。','annotations'); continue
        attrs, duplicate = {}, set()
        for ri, record in enumerate(records):
            rp = path+('annotations',ri)
            if not isinstance(record,dict):
                warn('属性不是对象，已跳过。',rp); continue
            identity = record.get('id')
            if not isinstance(identity,str) or not re.fullmatch(r'[WES][1-9][0-9]*',identity):
                warn('ID 无法推导层级，已跳过。',rp,identity=str(identity)); continue
            if identity in attrs:
                duplicate.add(identity); warn(f'{identity} 属性重复，无法确定采用哪条，已跳过该 ID。',rp,identity=identity)
            attrs[identity] = (record,rp)
        active, spans, invalid, first, starts = {}, {}, set(), [], {}
        pos = offset_local = 0
        aligned = True
        while pos < len(markup):
            literal = TAG_RE.match(source,offset_local)
            if literal and markup.startswith(literal.group(),pos):
                pos += len(literal.group()); offset_local = literal.end(); continue
            token = TAG_RE.match(markup,pos)
            if token:
                closing, identity = token.groups()
                if closing:
                    if identity not in active:
                        note('结束标签没有对应开始标签，该 ID 已跳过。',position=pos,identity=identity); invalid.add(identity)
                    else:
                        begin, opening = active.pop(identity)
                        if begin == offset_local:
                            note('空片段，该 ID 已跳过。',position=opening,identity=identity); invalid.add(identity)
                        spans.setdefault(identity,[]).append((begin,offset_local))
                else:
                    if identity in active:
                        note('同一 ID 嵌套，无法确定范围，已跳过该 ID。',position=pos,identity=identity); invalid.add(identity)
                    if identity not in starts:
                        starts[identity]=pos; first.append(identity)
                    active[identity]=(offset_local,pos)
                pos=token.end()
            else:
                if offset_local >= len(source) or markup[pos] != source[offset_local]:
                    note('annotated 与 source 不一致或标签损坏，无法可靠映射此句，已跳过。',position=pos)
                    aligned=False; break
                pos+=1; offset_local+=1
        if not aligned: continue
        if offset_local != len(source):
            note('annotated 缺少原文末尾，已跳过此句。',position=pos); continue
        for identity,(_,opening) in active.items():
            note('标签未闭合，该 ID 已跳过。',position=opening,identity=identity); invalid.add(identity)
        for identity,(record,rp) in attrs.items():
            if identity not in starts:
                warn('属性没有对应范围标签，已跳过。',rp,identity=identity)
        previous = []; counts = dict(W=0,E=0,S=0)
        for identity in first:
            layer=identity[0]; counts[layer]+=1
            if int(identity[1:]) != counts[layer]:
                note('编号未按层从 1 连续递增，已按实际标签定位。',position=starts[identity],identity=identity)
            if identity not in attrs:
                note('缺少属性记录，已跳过该 ID。',position=starts[identity],identity=identity); continue
            if identity in invalid or identity in duplicate: continue
            record,rp=attrs[identity]; local=spans.get(identity,[])
            if not local: continue
            category,canonical=record.get('category'),record.get('canonical')
            if not isinstance(canonical,str) or not canonical.strip():
                warn('canonical 缺失，已跳过该 ID。',rp,identity=identity); continue
            if not isinstance(category,str) or not category.strip():
                warn('category 缺失，已跳过该 ID。',rp,identity=identity); continue
            if category not in TAG_CATEGORIES[layer]:
                warn(f'未知子类 {category}，保留原值显示，请核对分类依据。',rp,identity=identity)
            if layer != 'S' and len(local)>1:
                note('word/expression 使用了多个片段，已保留实际范围，请核对。',position=starts[identity],identity=identity)
            if any(layer==other_layer and a<d and c<b for other_layer,ranges in previous for a,b in local for c,d in ranges):
                note('与同层条目重叠，已保留范围，请核对。',position=starts[identity],identity=identity)
            previous.append((layer,local))
            for begin,end in local:
                quote=source[begin:end]
                if quote != quote.strip() or any(a<boundary<b for a,b in (m.span() for m in re.finditer(r"[^\W_]+(?:['’‐‑-][^\W_]+)*",source)) for boundary in (begin,end)):
                    note('片段边缘含空白或切开单词，已保留实际范围，请核对。',position=starts[identity],identity=identity)
                words=re.findall(r"[^\W\d_]+(?:['’‐‑-][^\W\d_]+)*",quote)
                if (layer=='W' and len(words)!=1) or (layer=='E' and len(words)<2):
                    note('片段词数不符合该层级约定，已保留实际范围，请核对。',position=starts[identity],identity=identity)
            ranges=[(offset+a,offset+b) for a,b in local]
            annotation=dict(record,sentence_index=index+1,source=source,
                            spans=[{'text':text[a:b],'start':a,'end':b} for a,b in ranges])
            resolved.append({'category':LAYER_KEYS[layer],
                             'base':[category],'unit':canonical,'ranges':ranges,'subtype':category,'annotation':annotation,'json_path':rp})
    if text[cursor:].strip(): warn('返回句子未覆盖原文末尾，可用标注已保留。',('sentences',))
    return resolved


def api_error_message(body):
    """The API's own error text from an error response body, or None."""
    try:
        error = json.loads(body).get('error')
    except (ValueError, TypeError, AttributeError):
        return None
    message = error.get('message') if isinstance(error, dict) else error
    return message.strip()[:200] if isinstance(message, str) and message.strip() else None


def raise_api_error(body):
    detail = api_error_message(body)
    if detail:
        raise ValueError(f'API 错误：{detail}')


def extract_choice(body):
    """(content, finish_reason) of the first choice; error bodies and bad shapes raise ValueError."""
    raise_api_error(body)
    try:
        choice = json.loads(body)['choices'][0]
        content = choice['message']['content']
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ValueError('API 返回格式无效。') from exc
    if not isinstance(content, str):
        raise ValueError('响应没有可读取的文本内容。')
    return content, choice.get('finish_reason')


def response_json(body):
    """Decode actual JSON; no reconstruction of truncated or malformed content."""
    content, _ = extract_choice(body)
    if not content.strip():
        raise ValueError("模型返回空内容。")
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("API 返回内容无法读取为 JSON。") from exc


def build_explanation_payload(source, item, prompt, model):
    build_payload(source, prompt, model)  # 复用第一层的输入校验
    return compose_explanation_payload(source, item, prompt, model)


def compose_explanation_payload(source, item, prompt, model):
    payload = compose_annotation_payload(source, prompt, model)
    annotation = None if item is None else item['annotation']
    payload['messages'][1]['content'] = json.dumps({'english': source, 'annotation': annotation}, ensure_ascii=False)
    payload['response_format'] = {'type':'json_object'}
    payload['max_tokens'] = 768
    return payload


def format_request(payload):
    """Message content is shown verbatim, followed by the exact JSON body."""
    sections = [f"接口：{API_URL}"]
    for message in payload['messages']:
        sections.append(f"===== {message['role']} =====\n{message['content']}")
    sections.append('===== 完整请求体 JSON =====\n'+json.dumps(payload, ensure_ascii=False, indent=2))
    return '\n\n'.join(sections)


def parse_explanation(body):
    value = response_json(body)
    if not isinstance(value, dict) or not isinstance(value.get('explanation'), str) or not value['explanation'].strip():
        raise ValueError('响应缺少可显示的 explanation 文本。')
    return value['explanation']


def request_annotations(key, payload):
    request = urllib.request.Request(API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        hints = {400: "参数错误", 401: "密钥无效", 402: "余额不足", 429: "请求过于频繁", 503: "服务繁忙"}
        try:
            detail = api_error_message(exc.read().decode("utf-8", "replace"))
        except OSError:
            detail = None
        finally:
            exc.close()
        suffix = f"（{detail}）" if detail else ""
        raise ValueError(f"HTTP {exc.code}：{hints.get(exc.code, '请求失败')}{suffix}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ValueError("网络连接失败或超时，请重试。") from exc



# Public API v1: plain Python data, explicit host-provided prompt paths.
class Item(TypedDict):
    """One resolved annotation; ranges are Python indices into the full source text."""
    category: str  # LAYER_KEYS 的值
    base: list[str]
    unit: str  # canonical
    ranges: list[tuple[int, int]]
    subtype: str  # 属性记录里的 category 子类
    annotation: dict  # 原始属性记录，另附 sentence_index / source / spans
    json_path: tuple


class Document(TypedDict):
    source: str
    items: list[Item]
    warnings: list[AnnotationError]
    raw: str
    locations: dict[tuple, tuple[int, int]]  # JSON 值路径 -> 返回文本中的 [start, end)


def parse_annotation(source, raw) -> Document:
    value, locations, warnings = decode_best_effort(raw)
    items = resolve_items(value, source, warnings) if value is not None else []
    return {'source': source, 'items': items, 'warnings': warnings,
            'raw': raw, 'locations': locations}


def item_json_ranges(item, raw, locations):
    path, annotation = item['json_path'], item['annotation']
    ranges = [locations[path]] if path in locations else []
    markup_path = path[:2] + ('annotated',)
    if markup_path in locations:
        start, end = locations[markup_path]
        markup = json.loads(raw[start:end])
        boundaries = decoded_boundaries(raw, start, end)
        opening = None
        for match in TAG_RE.finditer(markup):
            if match[2] != annotation['id']:
                continue
            if not match[1]:
                opening = match.start()
            elif opening is not None:
                ranges.append((boundaries[opening], boundaries[match.end()]))
                opening = None
    return ranges


def warning_locations(raw, locations, warnings):
    """Return (label, details, start, end), all in original raw JSON coordinates."""
    entries = []
    for issue in warnings:
        if hasattr(issue, 'raw_range'):
            start, end = issue.raw_range
            line = raw.count('\n', 0, start) + 1
            entries.append((f'返回 JSON · 第 {line} 行', str(issue), start, end))
            continue
        # resolve_items 给每条句子级提醒都附带了 path，直接按它定位，不从提示文字反解句号。
        path = getattr(issue, 'path', ())
        while path not in locations and path:
            path = path[:-1]
        start, end = locations.get(path, (0, len(raw)))
        position = getattr(issue, 'position', None)
        if position is not None and raw[start:start+1] == '"':
            boundaries = decoded_boundaries(raw, start, end)
            decoded = json.loads(raw[start:end])
            position = min(position, len(boundaries)-1)
            token = TAG_RE.match(decoded, position)
            stop = min(position+(len(token.group()) if token else 1), len(boundaries)-1)
            start, end = boundaries[position], boundaries[stop]
        label = ('第 '+str(path[1]+1)+' 句') if len(path)>1 and path[0]=='sentences' else '返回 JSON'
        identity = getattr(issue, 'identity', '')
        if identity:
            label += ' · '+identity
        if len(path)>3 and path[2]=='annotations':
            label += f' · 第 {path[3]+1} 条属性'
        entries.append((label, str(issue), start, end))
    return entries


class PromptFile:
    """Read and save one explicit prompt path without directory discovery."""
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        return self.path.read_text(encoding='utf-8-sig')

    def save(self, content, *, previous):
        if not content.strip():
            raise ValueError('不能保存空提示词。')
        if self.read() != previous:
            raise ValueError('文件已被外部修改；请先备份编辑内容，再重新加载文件。')
        temporary = self.path.with_suffix(self.path.suffix + '.tmp')
        temporary.write_text(content, encoding='utf-8')
        temporary.replace(self.path)
        return self.path


class LearningCore:
    """One document session. Call public methods and poll() on one owner thread.

    Daemon workers only do transport/decoding and enqueue values. They never touch
    widgets or session state. poll() applies current-revision results and caches.
    Transport is injectable as transport(key, payload) -> response body for tests.
    """
    def __init__(self, transport=None, *, config_path=None):
        self.config_path = config_path
        self.transport = transport or request_annotations
        self.revision = 0
        self.document = {'source':'', 'items':[], 'warnings':[], 'raw':'', 'locations':{}}
        self.explanation_cache = {}
        self.explanation_pending = set()
        self.selected_explanation = None
        self.annotation_pending = False
        self._annotation_signature = None
        self._events = queue.Queue()
        self._closed = False

    def reset(self):
        self.revision += 1
        self.explanation_cache.clear()
        self.explanation_pending.clear()
        self.selected_explanation = None
        self.annotation_pending = False
        self._annotation_signature = None

    def clear_selection(self):
        """Forget which explanation the UI waits for; pending results stay cached."""
        self.selected_explanation = None

    def _ensure_open(self):
        if self._closed:
            raise RuntimeError('会话已关闭。')

    def _resolve_key(self, key):
        """A non-empty key from the caller wins; otherwise read the configured credential."""
        return key.strip() if isinstance(key, str) and key.strip() else load_deepseek_api_key(self.config_path)

    def set_text(self, source):
        self._ensure_open()
        self.reset()
        self.document = {'source':source, 'items':[], 'warnings':[], 'raw':'', 'locations':{}}
        return self.document

    def apply_json(self, source, raw):
        self.set_text(source)
        self.document = parse_annotation(source, raw)
        return self.document

    def _launch(self, kind, token, key, payload):
        snapshot = copy.deepcopy(payload)
        def run():
            started = time.monotonic()
            try:
                body = self.transport(key, snapshot)
                if kind == 'annotation':
                    data = extract_choice(body)
                else:
                    data = parse_explanation(body)
                event = {'kind':kind, 'token':token, 'success':True, 'data':data}
            except Exception as exc:
                message = str(exc) if isinstance(exc,ValueError) else '请求或响应读取失败，请重试。'
                if key:
                    message = message.replace(key, '[API Key]')
                event = {'kind':kind, 'token':token, 'success':False, 'data':message}
            event['elapsed'] = time.monotonic()-started
            self._events.put(event)
        threading.Thread(target=run, daemon=True).start()

    def annotate(self, source, prompt, model, *, key=None):
        self._ensure_open()
        # 先校验输入，避免输入有误时却提示缺少密钥。
        payload = build_payload(source, prompt, model)
        key = self._resolve_key(key)
        signature = (source, prompt, model)
        if self.annotation_pending and signature == self._annotation_signature:
            return {'state':'pending', 'payload':None}
        self.set_text(source)
        self.annotation_pending = True
        self._annotation_signature = signature
        self._launch('annotation', (self.revision,), key, payload)
        return {'state':'started', 'payload':payload}

    def explain(self, number, prompt, model, *, key=None):
        self._ensure_open()
        if not 0 <= number < len(self.document['items']):
            raise ValueError('请选择有效标注。')
        token = (self.revision, number, prompt, model)
        self.selected_explanation = token
        if token in self.explanation_cache:
            return {'state':'cached', 'text':self.explanation_cache[token], 'payload':None}
        if token in self.explanation_pending:
            return {'state':'pending', 'text':'正在解释…', 'payload':None}
        payload = build_explanation_payload(self.document['source'], self.document['items'][number], prompt, model)
        key = self._resolve_key(key)
        self.explanation_pending.add(token)
        self._launch('explanation', token, key, payload)
        return {'state':'started', 'text':'正在解释…', 'payload':payload}

    def poll(self):
        events = []
        while True:
            try:
                event = self._events.get_nowait()
            except queue.Empty:
                break
            token = event['token']
            if self._closed or token[0] != self.revision:
                continue
            if event['kind'] == 'annotation':
                self.annotation_pending = False
                if event['success']:
                    raw, reason = event['data']
                    self.document = parse_annotation(self.document['source'], raw)
                    event['document'] = self.document
                    event['finish_reason'] = reason
            else:
                self.explanation_pending.discard(token)
                if event['success']:
                    self.explanation_cache[token] = event['data']
                event['selected'] = token == self.selected_explanation
            events.append(event)
        return events

    def close(self):
        self.reset()
        self._closed = True
