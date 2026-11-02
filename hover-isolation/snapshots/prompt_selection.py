"""Content-based prompt compatibility and numeric newest-version selection.
No prompt names are pinned: newly saved files participate on the next startup.
"""
import json
import re
from pathlib import Path

PROFILES = {
    '5.2.0': ('occurrence', 'occurrence'),
    '5.2.1': ('context', 'context'),
    '5.3.0': ('fam_layers', 'fam_layers'),
    '5.3.1': ('fam_ids', 'fam_ids'),
    '5.4.0': ('context', 'context'),
    '5.4.1': ('sentences', 'sentences'),
    '5.4.2': ('tags', 'tags'),
    '5.4.3': ('tags', 'tags'),
}

def version_key(name):
    match = re.fullmatch(r'(?:An|Ex)_Demo (\d+)\.(\d+)\.(\d+)_(\d+)', name)
    return tuple(map(int,match.groups())) if match else ()

def examples(content):
    decoder=json.JSONDecoder()
    for match in re.finditer(r'\{',content):
        try: value,_=decoder.raw_decode(content,match.start())
        except ValueError: continue
        if isinstance(value,dict): yield value

def annotation_protocol(content):
    found=set()
    for value in examples(content):
        if isinstance(value.get('sentences'),list):
            for group in value['sentences']:
                if not isinstance(group,dict): continue
                if {'source','annotated','annotations'} <= group.keys(): found.add('tags')
                elif {'text','items'} <= group.keys(): found.add('sentences')
        elif isinstance(value.get('items'),list):
            for item in value['items']:
                if not isinstance(item,dict): continue
                spans=item.get('spans',[])
                if isinstance(spans,list) and spans:
                    found.add('occurrence' if any(isinstance(s,dict) and 'occurrence' in s for s in spans) else 'context')
    # Nested items examples in a sentence-based schema do not define a second protocol.
    if found & {'tags','sentences'}: found -= {'context','occurrence'}
    if not found:
        if re.search(r'<@(?:id|[1-9]\d*)\s+type=',content): found.add('fam_ids')
        elif '<@W' in content and '<@E' in content and '<@S' in content: found.add('fam_layers')
    return next(iter(found)) if len(found)==1 else None

def explanation_protocol(content):
    if not any(isinstance(v.get('explanation'),str) for v in examples(content)): return None
    if 'annotation.source' in content and 'sentence_index' in content: return 'tags'
    if 'annotation.sentence' in content: return 'sentences'
    if 'start/end' in content:
        return 'fam_ids' if '所有层级共享' in content else 'fam_layers'
    if 'context' in content: return 'context'
    if 'occurrence' in content: return 'occurrence'
    if 'form' in content and 'spans' in content: return 'occurrence'
    return None

def declared_categories(content):
    """Read category names from JSON examples and conventional classification tables."""
    names=set()
    for value in examples(content):
        name=value.get('category')
        if isinstance(name,str) and name not in ('word','phrase','grammar'): names.add(name)
    for line in content.splitlines():
        if not re.match(r'\s*\|\s*\d+\s*\|',line): continue
        cells=[c.strip() for c in line.strip().strip('|').split('|')]
        # Tables have either priority/name/definition or priority/group/name/definition.
        cell=cells[1] if len(cells)==4 else cells[2] if len(cells)>=5 else ''
        matches=re.findall(r'[（(]([A-Za-z][A-Za-z /&-]+)[）)]',cell)
        if matches: names.add(matches[-1])
        elif re.fullmatch(r'[A-Za-z][A-Za-z /&-]+',cell): names.add(cell)
    return names

def compatible(content, prefix, profile, allowed_categories=None):
    protocol=annotation_protocol(content) if prefix=='An' else explanation_protocol(content)
    expected=PROFILES[profile][0 if prefix=='An' else 1]
    if protocol != expected: return False
    if prefix=='An' and allowed_categories is not None:
        if declared_categories(content)-set(allowed_categories): return False
    return True

def latest_compatible(folder, prefix, profile, allowed_categories=None):
    candidates=[]
    for path in Path(folder).glob(prefix+'_Demo *.txt'):
        if not path.is_file() or not version_key(path.stem): continue
        try: content=path.read_text(encoding='utf-8-sig')
        except (OSError,UnicodeError): continue
        if compatible(content,prefix,profile,allowed_categories): candidates.append(path.stem)
    return max(candidates,key=version_key) if candidates else None
