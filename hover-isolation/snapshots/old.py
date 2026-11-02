# -*- coding: utf-8 -*-
# 累积版本更新记录（按时间顺序）
# Demo 5.0.0 — 原始概念验证
# - 独立 Tkinter 窗口，DeepSeek 后台请求，左侧可编辑提示词。
# - 输入中英文，输出完整词汇/短语/语法解析及 JSON；校验结构与引用。
# - 保留为最初实验基线，不含 OCR 集成或学习反馈。

# Demo 5.0.1 — 第一层候选标注
# - 将生成任务收敛到类别、名称、原文片段，不生成详细解释。
# - 三类颜色标注，分类开关、列表定位、跨片段及重叠显示。
# - 增加离线演示与定位/窗口测试；请求上限 2048 tokens。

# Demo 5.0.2 — 三层独立样式及定位修复（含本版本后续修订）
# - 句法用背景、词块用下划线、单词用粗体；选中时保留三层样式。
# - 点击重叠处选择候选，支持跨片段定位；改用英文提示词。
# - 移除中文参考输入/请求字段，分层筛选，避免常规情态结构挤占重点。
# - occurrence 按完整词边界计数，修复 era 匹配到 venerable 内部的问题。
# - 同一词块的近距离分离引用归并为连续范围，包含中间参数（如 us）。

# Demo 5.0.3 — 提示词重组与浅色下划线
# - 英文提示词分为任务、筛选、类别与输出契约，合并重复约束。
# - 明确词块原句范围与规范标签的区别，保留跨层独立选择和定位边界。
# - 词块下划线独立设为浅蓝灰色 #a6b9cf，不改变文字颜色或其他层样式。
# - 0–3 版文件头累积保留截至各版的更新记录；旧版功能保持原样。
# - 提示词效果仍需真实 API 对照验证，离线测试不证明模型选择质量。
# - 配色后续调整：沿用 5.0.1 的紫色背景、绿色词块下划线与蓝色单词，保留独立样式叠加。
# - 配色再调整：单词粗体恢复正文原色；背景和下划线增加即时选色器（当前会话生效）。

# Demo 5.0.4 — RGB / HSV / HEX 选色
# - 自定义选色窗口：RGB 0–255 整数，HSV 0–360° / 0–100% / 0–100%，HEX #RRGGBB。
# - 三种输入实时同步；校验范围、预览，确认后应用，取消不修改当前颜色。
# - 保留浅紫背景 #f2eafa，下划线默认使用同色系较深紫色 #80659e。
# - 悬停按下划线/字形/背景位置及层级优先级聚焦，点击显示已有条目信息，无候选菜单。

# Demo 5.0.5 — 固定配色与悬停动效
# - 三套浅紫背景配色：紫色 / 浅蓝 / 浅绿下划线，移除自由选色。
# - 悬停绘图层使整项文字平滑上移 3px，并为对应背景、线条或字形绘制同色描边。
# - 保留位置优先级与直接点击；所有标注反馈移除黑色边框。
# - 悬停修订：绘图层与 Text 外边界及基线对齐，按连续文字段绘制；上移减至 1px。
# - 粗体取消彩色描边，以正文同色轻微叠印加重，不改变字号和排版。
# - 再修订：静止/悬停统一 Canvas 绘制，语法填充几何固定，仅文字上移。
# - 参考 4.2.2 深色背景及 alpha 参数合成到面板底色；下划线固定 #7BDCE8。
# - 图片配色修订：整个文字面板改为 #292A39，单词悬停/选中为 #E6DCFF，取消叠印加粗。
# - 保留原有浅紫语法背景、青蓝下划线与静止粗体字重。
# - 反馈修订：下划线加粗到 3px，回退单词变色；各层仅移动自身装饰及文字。
# - 句法移动填充和轮廓；词块移动下划线；单词不牵动背景或下划线。

# Demo 5.0.6 — Qt 半透明字幕悬浮窗
# - 使用 PySide6，与 4.2.2 相同的渐变、背景 alpha、默认不透明度和圆角。
# - 悬浮窗只显示返回文本；主窗口保留输入、提示词、请求、结构数据与条目定位。
# - 原文 #F5F6FA，句法 rgba(154,132,255,0.20) 圆角块，下划线 #7BDCE8 / 3px。
# - 同一 QTextLayout 负责静止、悬停与命中；1px 动画不改变排版，装饰按层独立移动。
# - 修订：背景先画、下划线后画；按 4.2.2 的 14pt Medium 字体及字幕区域水平/垂直居中。
# Demo 5.0.7 — 单词常态配色、稳定窗高与点击解释
# - 单词首次渲染即使用 #E6DCFF 粗体；其他标注颜色保持指定值。
# - 返回文本时只按需增高，不自动缩小当前窗口；解释区位于字幕下方。
# - 同一次 API 请求返回每项简短中文 explanation，点击本地展示，不再次请求。
# - 提示词修订：同层禁止重叠、跨层仅保留独立学习点；引用最小完整范围，标签与解释对应原句。
# - 语境修订：不擅自套用专门义项或缩窄群体范围，优先可复用搭配；下划线悬停保持 3px。
# Demo 5.0.8 — 分类别深度解释
# - 单词采用生成式词典条目：音标、词性、用法、本句义、搭配、例句及分列的其他常见义。
# - 表达解释可复用结构、适用条件与短例；句法区分结构身份、成分关系和语义/话语功能。
# - 保留原句证据约束和同层不重叠；不冒充词典原文，不编造义项编号或不确定的音标/用法。
# - explanation 仍为纯文本，使用分段小标题；每项上限 1000 字符，输出预算 8192 tokens。
# - 解释区增至 220px，超长内容可滚动；重复加载后展开不再累计增高，离线演示同步更新。
# Demo 5.0.9 — 中文双层提示词与按需解释
# - 第一层仅标注，第二层点击后发送原文和选中标注生成简短解释；两层提示词可独立编辑。
# - 标注/解释输出预算分别为 2048/768 tokens；解释建议 80–180 字符，硬上限 320。
# - 同一文本、条目、提示词和模型缓存解释，重复点击合并请求；新文本隔离旧响应。
# - 离线演示使用预置短解释，不联网；保留颜色、圆角、稳定窗高和动画。
# Demo 5.1.0 — 由 5.0.9 重命名，标注契约与显示切换
# - 第一层提示词按用户原文替换；取消条目数、标签长度与句法片段数上限。
# - 单词/词块必须单片段，同类条目不得重叠，保留完整词边界和结构校验。
# - 第一层输出预算调整为 4096 tokens；不完整响应仍拒绝应用。
# - 字幕按钮切换显示/关闭并同步文案；后台解释返回不重新打开已关闭字幕。
# - 提示词再修订：依据用户人工标注，以词汇/表达积累为中心；跨层独立筛选、边界服从学习点、提高句法门槛。
# Demo 5.1.1 — 检索基础、学习单位、显示范围分离
# - 第一层输出 category/base/unit/spans：基础数组用于检索，单位区分词义/结构，引用负责显示。
# - 四维价值筛选，未知掌握状态不推断；使用用户人工标注的少量正例校准，不将留白当负例。
# - 更新解析校验、列表、悬浮窗解释标题及第二层请求，保留两层请求和本地内存缓存。
# - 校验同层不重叠、单词单词形、句法不跨指定标点；离线演示同步迁移。
# - 本版仅实现需求1–4，未加入本地数据库、次数统计或自动掌握判断。
# Demo 5.1.2 — 请求透明展示与双配色预览
# - 界面显示第一/第二层最终 system、user 消息（含人工示例）及完整请求参数。
# - 待发送预览随输入更新；单独保留实际提交请求快照，缓存命中不伪装成发送。
# - 两套精确 RGBA 配色：浅紫或浅金单词，原文/语法背景/下划线相同，选择时实时预览。
# - 配色同步字幕与单词格式；密钥不进入请求体预览，快照仅保存在当前内存。
# Demo 5.1.3 — 系统示例与宽容解析
# - 人工标注正例移入第一层系统提示词，编辑区和完整请求均可查看。
# - 解析器只读取字段和定位原文，不裁决重叠、分类、片段数或句法边界，不拆分或改写。
# - 忽略额外字段；无法定位或缺少必要字段的条目整项跳过，保留原始 JSON 供检查。
# - 第二层允许额外字段与超长解释；完整可解析内容不因 finish_reason 单独被拒绝。
# - 本版后续修订：模型输出精简为 category/form/spans；句法额外返回标准英文 name。
# - 同步解释请求与离线数据；原形和引用按结构范围对应，解析器不二次分割。
# Demo 5.2.0 — 外置提示词与独立版本管理
# - 默认标注（含人工正例）及解释提示词分别存放于 Codeia/Prompts/annotation、explanation。
# - A/E 两条版本序列独立于程序版本；界面可选择、预览编辑、保存当前版本或另存新版本。
# - 切换时保留本次会话草稿；请求使用编辑器当前内容，完整请求与发送快照保持可见。
# - 后续修订：默认标注 An_Demo 5.2.0_02；支持 type/category/canonical/spans，保留 An_Demo 5.2.0_01 旧协议。
# - 子类与标准形式同步到列表、字幕详情及第二层请求；默认解释 Ex_Demo 5.2.0_02。
# - 仍仅按引用和 occurrence 定位，不裁剪、拆分或拒绝重叠标注。
# Demo 5.2.1 — 上下文定位
# - 默认 An_Demo 5.2.1_01 / Ex_Demo 5.2.1_01：text 唯一时直接定位，重复时使用唯一 context。
# - 不再依赖模型的 occurrence；上下文仅定位，不渲染，不裁剪或猜测歧义位置。
# - 无法定位的条目整项跳过，状态栏及提示显示原因；保留原始 JSON。
# - 后续修订：返回 JSON 可编辑，新增本地应用按钮，按当前英文输入重新定位渲染。
# - 应用失败保留原标注；成功清除旧解释缓存，隔离过期解释响应，不调用标注 API。
# Demo 5.2.2 — FAM 内联标注
# - 第一层返回 FAM 文本，按插入标记计算位置；逐字符校验原文保真。
# - W/E 每次独立，S 按 id 关联；支持跨层交叉，检查闭合及同层重叠。
# - 默认 A2.0.0 / Ex_Demo 5.3.0_01；手动编辑 FAM 渲染，解释仍使用结构化 JSON。
# Demo 5.3.0 — 由 5.2.2 重命名
# - 默认标注 An_Demo 5.3.0_01；移除配色选择与预览，单词固定浅金 RGBA(245,216,166,255)。
# - 表达结束标记恢复为 </@E>，严格拒绝 </@E1> 至 </@E6> 等带编号形式。
# - W 仅使用 </@W>，S 使用 </@S#id>，不提供结束标记的兼容分支。
# - 只兼容标记语法，不自动修改模型的类别、标准形式或引用范围。
# - 报错显示行列和附近片段；编辑区自动选中出错标记，未闭合时定位开始标记。
# - 第一层用户消息直接发送原文，移除 english JSON 包装；默认精简提示词 An_Demo 5.3.0_02。
# - 第二层仍发送结构化原文和选中标注，并启用 JSON 解释输出。
# Demo 5.3.1 — 所有层级统一实例 ID
# - 默认 An_Demo 5.3.1_01，起始声明 type/cat/canon，结束统一 </@id>；仅 syntax 可复用 ID。
# - 全局首次声明编号连续递增；跨层独立闭合，支持多片段及交叉。
# - 按标记计算原文范围；解释请求为所有层级携带实例 ID，保留手动渲染和错误定位。
# - 提示词统一命名为 An/Ex_Demo 适用版本_编号，更新默认引用与保存校验。
# Demo 5.4.0 — JSON 标注，复用 5.2.1 提示词与 text/context 定位
# - 保留 5.3.1 配色、交互、请求快照、解释缓存及失败保留旧标注。
# - 本地 JSON 重渲染；无法定位的条目整项跳过，显示诊断。
# Demo 5.4.1 — 按句分组，句内定位并映射回全文坐标
# Demo 5.4.2 — 句内范围标签与 JSON 属性记录
# - 默认 An_Demo 5.4.2_01，完整保存用户提供的提示词及分类快照。
# - sentences 使用 source/annotated/annotations；W/E/S 按句、按层独立编号。
# - 支持跨层交叉及 syntax 多片段；校验原文、闭合、ID、属性、边界与同层重叠。
# - 结构错误整次拒绝并保留旧标注；不根据模型语义自动修补范围或重新分类。
# - 第二层使用 Ex_Demo 5.4.2_01，接收句子、原始属性与程序解析的片段坐标。
# - 保留 JSON 编辑重渲染、请求快照、配色、解释缓存和过期响应隔离。
# - 离线演示采用用户提供的三句示范；不代表模型质量或词频判定已核验。
# - 后续修订：错误列表显示句序号、ID 与属性条目，点击精确定位 JSON 转义后的字符位置。
# - 每句收集首个结构错误；编辑返回文本后清除过期错误列表，重新应用重新校验。
# Demo 5.4.3 — 尽力解析、局部保留与可点击提醒
# - An_Demo 5.4.3_01 原样复制 5.4.2 当前默认文件，解释提示词继续使用 5.4.2。
# - 句子/条目独立解析；未知子类、编号顺序、同层重叠等可渲染问题仅提醒。
# - 无法可靠定位的句子或 ID 跳过，不猜测范围；JSON 语法损坏时保留旧标注。
# - 提醒保留句序号、ID、属性路径及标签字符位置，点击定位原始返回内容。
# - 离线演示更新：S1 连续覆盖 Only by ... can we，包含 E1 与 W1/W2；canonical 同步用户示例。
# - 兼容 Subjunctive 与旧名称；支持围栏/前后文字中的 JSON、损坏响应中的完整句对象。
# - 解析结果始终显示本次原文；没有可用标注时清空旧标注并仅提醒，不显示旧文本。
# - 元素表点击只高亮原始 JSON 的属性和所有对应片段，不触发字幕选中或解释。
# - 高亮按字段路径与转义位置映射；编辑返回文本后须重新应用，避免跳到过期位置。
"""FaintOCR Demo 5.4.3. Run with the project .venv Python (PySide6)."""
from pathlib import Path
import json
import os
import queue
import re
import threading
import time
import urllib.error
import urllib.request

API_URL = "https://api.deepseek.com/chat/completions"
CATEGORIES = {
    "grammar": ("句法结构 · 背景", "#7941b1", "#f2eafa"),
    "phrase": ("表达与词块 · 下划线", "#80659e", ""),
    "word": ("单词 · 粗体", "#30343b", ""),
}
MAX_EXPLANATION_CHARS = 320
PHRASE_UNDERLINE_COLOR = "#7BDCE8"
PROMPT_ROOT = Path(__file__).resolve().parents[1] / 'Prompts'

# 自动默认：启动时扫描兼容提示词，按文件名数字版本/编号取最新；手动选择和草稿不变。
from runpy import run_path as _load_prompt_selection
_latest_prompt = _load_prompt_selection(str(Path(__file__).with_name('prompt_selection.py')))['latest_compatible']
PROMPT_PROFILE = '5.4.3'

# User-supplied annotation fixture; explanatory text is local demo data only.
SAMPLE = 'Only by calling our cherished assumptions into question can we approach the truth with intellectual humility.'
DEMO = {'sentences': [{'source': 'Only by calling our cherished assumptions into question can we approach the truth '
                          'with intellectual humility.',
                'annotated': '<#S1>Only by <#E1>calling our <#W1>cherished</#W1> <#W2>assumptions</#W2> into '
                             'question</#E1> can we</#S1> approach the truth with <#W3>intellectual</#W3> '
                             '<#W4>humility</#W4>.',
                'annotations': [{'id': 'S1',
                                 'category': 'Inversion',
                                 'canonical': 'Only <Adverbial> <Auxiliary> <Subject>'},
                                {'id': 'E1',
                                 'category': 'Idioms & Conventional Expressions',
                                 'canonical': 'call <Object> into question'},
                                {'id': 'W1', 'category': 'Beyond Top 2000', 'canonical': 'cherish'},
                                {'id': 'W2', 'category': 'Beyond Top 2000', 'canonical': 'assumption'},
                                {'id': 'W3', 'category': 'Beyond Top 2000', 'canonical': 'intellectual'},
                                {'id': 'W4', 'category': 'Beyond Top 2000', 'canonical': 'humility'}]}]}
DEMO_EXPLANATIONS = ('Only by 引导的状语置于句首，主句使用 can we approach 部分倒装，强调“只有通过……才能……”。',
 'call <Object> into question 表示“质疑……”。这里的 calling 是动名词形式，中间槽位 our cherished assumptions 指我们珍视的假设。',
 'cherished 源自 cherish，在此作定语，表示“珍视的、深信不疑的”，修饰 assumptions。',
 'assumptions 是 assumption 的复数，意为“假设、未经证实而接受的看法”。这里指我们习以为常的前提。',
 'intellectual 在此作形容词，与 humility 搭配，指对知识、推理和自身认识局限的态度。',
 'humility 意为“谦逊”。intellectual humility 指承认自身认识可能有局限、愿意修正观点的态度。')


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
        "response_format": {"type": "json_object"}, "max_tokens": 8192}


TAG_CATEGORIES = {
    'W': {'Less Common Senses', 'Beyond Top 2000'},
    'E': {'Idioms & Conventional Expressions', 'Formulaic Expressions', 'Lexical Frames',
          'Multiword Verbs', 'Fixed Phrases', 'Collocations'},
    'S': {'Subjunctive', 'Subjunctive / Irrealis', 'Emphatic Constructions', 'Inversion', 'Ellipsis', 'Fronting', 'Parentheticals'},
}
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


def resolve_items(value, text, issues=None):
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
            resolved.append({'category':{'W':'word','E':'phrase','S':'grammar'}[layer],
                             'base':[category],'unit':canonical,'ranges':ranges,'subtype':category,'annotation':annotation,'json_path':rp})
    if text[cursor:].strip(): warn('返回句子未覆盖原文末尾，可用标注已保留。',('sentences',))
    return resolved


def response_json(body):
    """Decode actual JSON; no reconstruction of truncated or malformed content."""
    try:
        content = json.loads(body)["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("模型返回空内容。")
        return json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("API 返回内容无法读取为 JSON。") from exc


def annotation_content(body):
    try:
        choice = json.loads(body)['choices'][0]
        content = choice['message']['content']
        if not isinstance(content, str):
            raise ValueError('模型没有返回 JSON 文本。')
        if choice.get('finish_reason') not in (None, 'stop'):
            raise ValueError('标注输出未完整结束，请缩短原文重试。')
        return content
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('API 返回格式无效。') from exc


def parse_response(body, english):
    content = annotation_content(body)
    value = json.loads(content)
    return value, resolve_items(value, english)


def build_explanation_payload(source, item, prompt, model):
    payload = build_payload(source, prompt, model)
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
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        hints = {400: "参数错误", 401: "密钥无效", 402: "余额不足", 429: "请求过于频繁", 503: "服务繁忙"}
        raise ValueError(f"HTTP {exc.code}：{hints.get(exc.code, '请求失败')}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ValueError("网络连接失败或超时，请重试。") from exc


import sys
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, Signal
from PySide6.QtGui import (QColor, QFont, QPainter, QPen, QLinearGradient,
                          QTextLayout, QTextOption, QTextCharFormat, QPainterPath, QTextCursor)
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QLineEdit, QPushButton, QLabel, QSplitter, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QTabWidget, QCheckBox, QComboBox, QTextBrowser, QMessageBox)

TEXT_COLOR = '#F5F6FA'
WORD_COLOR = '#F5D8A6'
GRAMMAR_RGBA = (154, 132, 255, 51)
BACKGROUND_OPACITY = .8
PALETTE = {'original':(245,246,250,255), 'syntax':(154,132,255,51), 'expression':(123,220,232,255), 'word':(245,216,166,255)}


def rgba(value, alpha=255):
    result = QColor(value)
    result.setAlpha(alpha)
    return result


class SubtitleWindow(QWidget):
    selected = Signal(int)
    visibility_changed = Signal(bool)

    def __init__(self):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setWindowTitle('FaintOCR Demo 5.4.3 · 字幕')
        self.resize(980, 180)
        self.source, self.items = '', []
        self.enabled = set(CATEGORIES)
        self.hovered = None
        self.scroll = 0
        self.lift = 0.
        self.drag_origin = None
        self.layout = None
        self.rects = []
        self.content_height = 0
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.animate)
        self.font = QFont('Microsoft YaHei UI', 14, QFont.Medium)
        self.info_height = 220
        self.info_visible = False
        self.info = QTextBrowser(self)
        self.info.setOpenLinks(False)
        self.info.setFont(QFont('Microsoft YaHei UI', 11))
        self.info.setStyleSheet('QTextBrowser { background: transparent; color: #F5F6FA; border: 0; border-top: 1px solid rgba(230,220,255,60); padding-top: 10px; }')
        self.info.hide()

    def showEvent(self, event):
        super().showEvent(event)
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def set_content(self, source, items, enabled=None):
        self.source, self.items = source, items
        self.info_visible = False
        self.info.clear()
        self.info.hide()
        self.enabled = set(CATEGORIES) if enabled is None else set(enabled)
        self.hovered = None
        self.timer.stop()
        self.lift = self.scroll = 0
        self.relayout()
        screen = self.screen().availableGeometry()
        self.resize(self.width(), max(self.height(), min(max(180, int(self.content_height + 66)), int(screen.height() * .6))))
        self.relayout()
        self.update()

    def relayout(self):
        # Qt offsets use UTF-16; source ranges use Python Unicode code points.
        offsets = [0]
        for char in self.source:
            offsets.append(offsets[-1] + (2 if ord(char) > 0xffff else 1))
        self.layout = QTextLayout(self.source.replace('\n', '\u2028'), self.font)
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        option.setAlignment(Qt.AlignHCenter)
        self.layout.setTextOption(option)
        formats = []
        for item in self.items:
            if item['category'] == 'word' and 'word' in self.enabled:
                for start, end in item['ranges']:
                    part = QTextLayout.FormatRange()
                    part.start, part.length = offsets[start], offsets[end]-offsets[start]
                    part.format = QTextCharFormat()
                    part.format.setFontWeight(QFont.Bold)
                    part.format.setForeground(QColor(*PALETTE["word"]))
                    formats.append(part)
        self.layout.setFormats(formats)
        self.layout.beginLayout()
        y = 0
        while True:
            line = self.layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(max(50, self.width()-62))
            line.setPosition(QPointF(0, y))
            y += line.height()
        self.layout.endLayout()
        self.content_height = y
        self.scroll = min(self.scroll, max(0, y-self.text_area().height()))
        self.rects = [[] for _ in self.items]
        for number, item in enumerate(self.items):
            if item['category'] not in self.enabled:
                continue
            for start, end in item['ranges']:
                for n in range(self.layout.lineCount()):
                    line = self.layout.lineAt(n)
                    a, b = max(offsets[start], line.textStart()), min(offsets[end], line.textStart()+line.textLength())
                    if a < b:
                        x1, x2 = line.cursorToX(a)[0], line.cursorToX(b)[0]
                        self.rects[number].append(QRectF(31+x1, line.y(), max(1,x2-x1), line.height()))

    def resizeEvent(self, event):
        self.hovered = None
        self.lift = 0
        self.timer.stop()
        self.relayout()
        if hasattr(self, 'info'):
            self.position_info()
        super().resizeEvent(event)

    def text_area(self):
        # 4.2.2 draws subtitles with AlignCenter | TextWordWrap in this rectangle.
        return QRectF(31, 24, self.width()-62, max(50, self.height()-66-(self.info_height if self.info_visible else 0)))

    def position_info(self):
        self.info.setGeometry(31, self.height()-self.info_height-28, self.width()-62, self.info_height)

    def show_explanation(self, number, text):
        item = self.items[number]
        if not self.info_visible:
            self.info_visible = True
            cap = self.screen().availableGeometry().height()-40
            self.resize(self.width(), max(self.height(), min(max(180, int(self.content_height+66))+self.info_height, cap)))
        self.position_info()
        self.info.setPlainText(f"{CATEGORIES[item['category']][0]} · {item['subtype'] + ' · ' if item['subtype'] else ''}{item['unit']}\n{text}")
        self.info.verticalScrollBar().setValue(0)
        self.info.show()
        self.relayout()
        self.update()

    def text_top(self):
        return self.text_area().top() + max(0, (self.text_area().height()-self.content_height)/2)

    def displayed_rect(self, rect):
        return rect.translated(0, self.text_top()-self.scroll)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        body = QRectF(12, 10, self.width()-24, self.height()-24)
        # Exact background parameters from 4.2.2 SubtitleWindow.paintEvent.
        p.save()
        p.setOpacity(BACKGROUND_OPACITY)
        p.setPen(Qt.NoPen)
        p.setBrush(rgba('#060815', 28))
        p.drawRoundedRect(body.adjusted(-1, 2, 1, 4), 23, 23)
        gradient = QLinearGradient(body.topLeft(), body.bottomRight())
        gradient.setColorAt(0, rgba('#20222d', 248))
        gradient.setColorAt(1, rgba('#141621', 248))
        p.setBrush(gradient)
        p.setPen(QPen(rgba('#ffffff', 28), 1))
        p.drawRoundedRect(body, 22, 22)
        p.restore()
        viewport = self.text_area().adjusted(-6, -4, 6, 6)
        p.setClipRect(viewport)
        # Backgrounds always precede underlines, regardless of API item order.
        for number, item in sorted(enumerate(self.items), key=lambda pair: {"grammar":0,"phrase":1,"word":2}[pair[1]["category"]]):
            category = item['category']
            for original in self.rects[number]:
                rect = self.displayed_rect(original)
                shift = -self.lift if self.hovered == number else 0
                if category == 'grammar':
                    block = rect.adjusted(-3, -2, 3, 2).translated(0, shift)
                    p.setBrush(QColor(*PALETTE["syntax"]))
                    p.setPen(QPen(rgba('#9A84FF', 150), 1) if self.hovered == number else QPen(Qt.NoPen))
                    p.drawRoundedRect(block, 7, 7)
                elif category == 'phrase':
                    a = QPointF(rect.left(), rect.bottom()-1+shift)
                    b = QPointF(rect.right(), rect.bottom()-1+shift)
                    p.setPen(QPen(QColor(*PALETTE["expression"]), 3, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(a,b)
        if self.layout:
            # Same shaped text/layout in both states; only the target clip translates.
            target = QPainterPath()
            if self.hovered is not None:
                for rect in self.rects[self.hovered]:
                    target.addRect(self.displayed_rect(rect))
            all_text = QPainterPath()
            all_text.addRect(viewport)
            p.setPen(QColor(*PALETTE["original"]))
            p.save()
            p.setClipPath(all_text.subtracted(target), Qt.IntersectClip)
            self.layout.draw(p, QPointF(31, self.text_top()-self.scroll))
            p.restore()
            if not target.isEmpty():
                p.save()
                p.translate(0, -self.lift)
                p.setClipPath(target, Qt.IntersectClip)
                self.layout.draw(p, QPointF(31, self.text_top()-self.scroll))
                p.restore()
        p.end()

    def target_at(self, point):
        if not self.text_area().adjusted(-6, -4, 6, 6).contains(point):
            return None
        hits = []
        for number, rects in enumerate(self.rects):
            for raw in rects:
                rect = self.displayed_rect(raw)
                if rect.contains(point):
                    y = point.y()-rect.top()
                    order = ('phrase','word','grammar') if y >= rect.height()-6 else (('grammar','word','phrase') if y < 4 else ('word','phrase','grammar'))
                    hits.append((order.index(self.items[number]['category']), sum(b-a for a,b in self.items[number]['ranges']), number))
        return min(hits)[2] if hits else None

    def focus(self, number):
        if number != self.hovered:
            self.hovered, self.lift = number, 0
            self.started = time.monotonic()
            self.timer.start() if number is not None else self.timer.stop()
            self.update()
        self.setCursor(Qt.PointingHandCursor if number is not None else Qt.ArrowCursor)

    def animate(self):
        progress = min(1, (time.monotonic()-self.started)/.14)
        self.lift = 1-(1-progress)**3
        if progress >= 1:
            self.timer.stop()
        self.update()

    def mouseMoveEvent(self, event):
        if self.drag_origin is not None:
            self.move((event.globalPosition()-self.drag_origin).toPoint())
        else:
            self.focus(self.target_at(event.position()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            target = self.target_at(event.position())
            if target is None:
                self.drag_origin = event.globalPosition()-QPointF(self.pos())
            else:
                self.selected.emit(target)

    def mouseReleaseEvent(self, event):
        self.drag_origin = None

    def leaveEvent(self, event):
        self.focus(None)

    def wheelEvent(self, event):
        self.focus(None)
        self.scroll = min(max(0, self.content_height-self.text_area().height()), max(0, self.scroll-event.angleDelta().y()/3))
        self.update()


class PromptLibrary(QWidget):
    """Independent file library; switching versions never discards a draft."""
    def __init__(self, folder, prefix, parent=None, default=None):
        super().__init__(parent)
        self.folder, self.prefix = Path(folder), prefix
        self.default = default
        self.drafts, self.disk = {}, {}
        self.current = None
        box = QVBoxLayout(self)
        row = QHBoxLayout()
        self.selector = QComboBox()
        self.refresh_button = QPushButton('刷新版本')
        row.addWidget(self.selector, 1)
        row.addWidget(self.refresh_button)
        box.addLayout(row)
        self.path_label = QLabel(str(self.folder))
        self.path_label.setWordWrap(True)
        box.addWidget(self.path_label)
        self.editor = QPlainTextEdit()
        box.addWidget(self.editor)
        row = QHBoxLayout()
        self.save_button = QPushButton('保存当前版本')
        self.version = QLineEdit()
        self.version.setPlaceholderText(f'新名称，如 {prefix}_Demo 5.4.3_02')
        self.new_button = QPushButton('另存新版本')
        row.addWidget(self.save_button)
        row.addWidget(self.version, 1)
        row.addWidget(self.new_button)
        box.addLayout(row)
        self.note = QLabel('编辑区即预览；请求使用当前内容。切换保留草稿，关闭前请保存。')
        self.note.setWordWrap(True)
        box.addWidget(self.note)
        self.selector.currentTextChanged.connect(self.select_version)
        self.editor.textChanged.connect(self.mark_dirty)
        self.refresh_button.clicked.connect(self.refresh_versions)
        self.save_button.clicked.connect(lambda: self.save_version(False))
        self.new_button.clicked.connect(lambda: self.save_version(True))
        self.refresh_versions()

    def refresh_versions(self):
        names = set(self.drafts)
        if self.folder.exists():
            names.update(p.stem for p in self.folder.glob(self.prefix+'_Demo *.txt') if p.is_file())
        names = sorted(names, key=lambda x: tuple(int(n) for n in re.findall(r'\d+', x)), reverse=True)
        self.selector.blockSignals(True)
        self.selector.clear()
        self.selector.addItems(names)
        if self.current in names:
            self.selector.setCurrentText(self.current)
        self.selector.blockSignals(False)
        if self.current is None and names:
            categories = None
            if PROMPT_PROFILE in ('5.3.1', '5.4.2'):
                table = globals().get('TAG_CATEGORIES', globals().get('FAM_CATEGORIES', {}))
                categories = {name for values in table.values() for name in values}
            chosen = _latest_prompt(self.folder, self.prefix, PROMPT_PROFILE, categories)
            if chosen:
                self.selector.setCurrentText(chosen)
                self.select_version(chosen)
            else:
                self.selector.setCurrentIndex(-1)
                self.note.setText('未找到兼容当前解析器的提示词；可手动选择并检查协议，或另存兼容版本。')
        elif not names:
            self.note.setText('未找到提示词文件；可输入内容并另存新版本。')

    def select_version(self, name):
        if not name or name == self.current:
            return
        if self.current:
            self.drafts[self.current] = self.editor.toPlainText()
        try:
            if name not in self.drafts:
                self.disk[name] = (self.folder/(name+'.txt')).read_text(encoding='utf-8-sig')
                self.drafts[name] = self.disk[name]
            self.current = name
            self.editor.setPlainText(self.drafts[name])
            self.path_label.setText(str(self.folder/(name+'.txt')))
            self.mark_dirty()
        except (OSError, UnicodeError) as exc:
            self.note.setText(f'读取失败：{exc}')
            self.selector.blockSignals(True)
            self.selector.setCurrentText(self.current or '')
            self.selector.blockSignals(False)

    def mark_dirty(self):
        dirty = self.editor.toPlainText() != self.disk.get(self.current, '')
        self.note.setText(('未保存修改 · ' if dirty else '已加载 · ') + '请求使用当前编辑内容；切换保留草稿，关闭前请保存。')

    def save_version(self, new):
        name = self.version.text().strip() if new else self.current
        if not name or not re.fullmatch(re.escape(self.prefix)+r'_Demo \d+\.\d+\.\d+_[0-9]{2,}', name):
            self.note.setText(f'名称须为 {self.prefix}_Demo 版本号_数字编号，例如 {self.prefix}_Demo 5.4.3_02。')
            return
        content = self.editor.toPlainText()
        if not content.strip():
            self.note.setText('不能保存空提示词。')
            return
        target = self.folder/(name+'.txt')
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            if new:
                with target.open('x', encoding='utf-8') as stream:
                    stream.write(content)
            else:
                # Do not silently overwrite changes made in an external editor.
                if target.read_text(encoding='utf-8-sig') != self.disk.get(name):
                    self.note.setText('文件已被外部修改；请另存新版本，避免覆盖。')
                    return
                temporary = target.with_suffix('.txt.tmp')
                temporary.write_text(content, encoding='utf-8')
                temporary.replace(target)
            if self.current:
                self.drafts[self.current] = content
            self.current = name
            self.drafts[name] = self.disk[name] = content
            self.refresh_versions()
            self.path_label.setText(str(target))
            self.note.setText('已保存：'+str(target))
        except FileExistsError:
            self.note.setText('该版本已存在，请使用新的版本号。')
        except (OSError, UnicodeError) as exc:
            self.note.setText(f'保存失败：{exc}')

    def has_unsaved(self):
        if self.current:
            self.drafts[self.current] = self.editor.toPlainText()
        return any(value != self.disk.get(name, '') for name, value in self.drafts.items()) or (not self.current and bool(self.editor.toPlainText().strip()))


class AnnotationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FaintOCR Demo 5.4.3 · 学习元素标注')
        self.resize(1120, 760)
        self.source, self.items = '', []
        self.events = queue.Queue()
        self.explanation_events = queue.Queue()
        self.revision = 0
        self.explanation_cache = {}
        self.explanation_pending = set()
        self.selected_explanation = None
        self.offline = False
        self.busy = False
        self.request_history = []
        self.subtitle = SubtitleWindow()
        self.subtitle.selected.connect(self.select_item)
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.key = QLineEdit(os.environ.get('DEEPSEEK_API_KEY',''))
        self.key.setEchoMode(QLineEdit.Password)
        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.addItems(['deepseek-flash', 'deepseek-v4-pro'])
        self.submit_button = QPushButton('标注学习元素')
        self.demo_button = QPushButton('离线演示')
        self.subtitle_button = QPushButton('显示字幕悬浮窗')
        self.subtitle.visibility_changed.connect(lambda visible: self.subtitle_button.setText('关闭字幕悬浮窗' if visible else '显示字幕悬浮窗'))
        for widget in (QLabel('DeepSeek API Key'), self.key, self.model, self.submit_button, self.demo_button, self.subtitle_button):
            top.addWidget(widget)
        root.addLayout(top)
        splitter = QSplitter()
        self.annotation_library = PromptLibrary(PROMPT_ROOT/'annotation', 'An', default='An_Demo 5.4.3_01')
        self.prompt = self.annotation_library.editor
        self.prompt.setPlaceholderText('第一层：中文标注提示词')
        self.explanation_library = PromptLibrary(PROMPT_ROOT/'explanation', 'Ex', default='Ex_Demo 5.4.2_01')
        self.explanation_prompt = self.explanation_library.editor
        prompt_tabs = QTabWidget()
        prompt_tabs.addTab(self.annotation_library, '第一层 · 仅标注')
        prompt_tabs.addTab(self.explanation_library, '第二层 · 按需解释')
        requests = QTabWidget()
        self.annotation_preview = QPlainTextEdit()
        self.annotation_preview.setReadOnly(True)
        requests.addTab(self.annotation_preview, '第一层待发')
        explanation_page = QWidget()
        explanation_box = QVBoxLayout(explanation_page)
        explanation_box.addWidget(QLabel('选择条目仅预览；点击字幕或列表才请求解释。'))
        self.preview_item = QComboBox()
        self.preview_item.addItem('未选择标注', None)
        explanation_box.addWidget(self.preview_item)
        self.explanation_preview = QPlainTextEdit()
        self.explanation_preview.setReadOnly(True)
        explanation_box.addWidget(self.explanation_preview)
        requests.addTab(explanation_page, '第二层待发')
        history_page = QWidget()
        history_box = QVBoxLayout(history_page)
        history_box.addWidget(QLabel('实际提交给请求线程的快照，不代表请求成功；缓存/离线演示不会新增。'))
        self.history_selector = QComboBox()
        history_box.addWidget(self.history_selector)
        self.history_view = QPlainTextEdit('尚未发送请求。')
        self.history_view.setReadOnly(True)
        history_box.addWidget(self.history_view)
        requests.addTab(history_page, '发送快照')
        prompt_tabs.addTab(requests, '完整 AI 请求')
        splitter.addWidget(prompt_tabs)
        panel = QWidget()
        side = QVBoxLayout(panel)
        side.addWidget(QLabel('英文原文'))
        self.english = QPlainTextEdit()
        self.english.setMaximumHeight(160)
        side.addWidget(self.english)
        filters = QHBoxLayout()
        self.filters = {}
        for category, (label, _, _) in CATEGORIES.items():
            check = QCheckBox(label)
            check.setChecked(True)
            check.toggled.connect(self.render)
            self.filters[category] = check
            filters.addWidget(check)
        side.addLayout(filters)
        side.addWidget(QLabel('返回文本显示于独立半透明字幕窗。拖动空白处移动；滚轮浏览长文本。'))
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['层级', '子类', '标准形式'])
        self.tree.setColumnWidth(0, 140)
        self.tree.setColumnWidth(1, 180)
        self.tree.itemClicked.connect(lambda entry, _: self.highlight_item_json(entry.data(0, Qt.UserRole)))
        side.addWidget(self.tree)
        self.details = QLabel('点击字幕标注查看解释；点击列表条目定位返回 JSON。')
        self.details.setWordWrap(True)
        self.details.setTextFormat(Qt.PlainText)
        side.addWidget(self.details)
        self.raw = QPlainTextEdit()
        self.raw.setPlaceholderText('粘贴或修改返回的 JSON，然后点击“应用 JSON / 重新渲染”。')
        side.addWidget(QLabel('返回 JSON（可编辑，按句分组、范围标签定位）'))
        self.apply_json_button = QPushButton('应用 JSON / 重新渲染')
        self.apply_json_button.clicked.connect(self.apply_json)
        side.addWidget(self.apply_json_button)
        side.addWidget(self.raw)
        self.error_tree = QTreeWidget()
        self.error_tree.setHeaderLabels(['提醒条目（点击定位）', '细节'])
        self.error_tree.setColumnWidth(0, 180)
        self.error_tree.setMaximumHeight(150)
        self.error_tree.hide()
        self.error_tree.itemClicked.connect(self.navigate_error)
        self.raw.textChanged.connect(self.clear_errors)
        side.addWidget(self.error_tree)
        splitter.addWidget(panel)
        splitter.setSizes([420,700])
        root.addWidget(splitter)
        self.status = QLabel('先标注，点击后按需解释；同一文本内缓存解释。密钥不落盘。')
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.PlainText)
        root.addWidget(self.status)
        self.submit_button.clicked.connect(self.submit)
        self.demo_button.clicked.connect(self.demo)
        self.subtitle_button.clicked.connect(self.toggle_subtitle)
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll)
        self.poll_timer.start(80)
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(80)
        self.preview_timer.timeout.connect(self.refresh_request_previews)
        for editor in (self.prompt, self.explanation_prompt, self.english):
            editor.textChanged.connect(lambda: self.preview_timer.start())
        self.model.currentTextChanged.connect(lambda *_: self.preview_timer.start())
        self.preview_item.currentIndexChanged.connect(lambda *_: self.refresh_request_previews())
        self.history_selector.currentIndexChanged.connect(self.show_history)
        self.refresh_request_previews()

    def refresh_request_previews(self):
        first = compose_annotation_payload(self.english.toPlainText(), self.prompt.toPlainText(), self.model.currentText())
        self.annotation_preview.setPlainText('待发送预览（未通过输入校验时不会发送）。\n\n'+format_request(first))
        number = self.preview_item.currentData()
        item = self.items[number] if number is not None and number < len(self.items) else None
        second = compose_explanation_payload(self.source, item, self.explanation_prompt.toPlainText(), self.model.currentText())
        note = '仅预览；命中缓存或离线演示时不会发送。' if item else '未选标注，annotation 为占位 null；此状态不会发送。'
        self.explanation_preview.setPlainText(note+'\n\n'+format_request(second))

    def record_request(self, layer, payload):
        snapshot = json.loads(json.dumps(payload, ensure_ascii=False))
        self.request_history.append({'layer':layer, 'payload':snapshot})
        self.history_selector.addItem(f"{len(self.request_history)} · {layer} · {time.strftime('%H:%M:%S')}")
        self.history_selector.setCurrentIndex(len(self.request_history)-1)
        self.show_history(len(self.request_history)-1)

    def show_history(self, index):
        if 0 <= index < len(self.request_history):
            record = self.request_history[index]
            self.history_view.setPlainText(record['layer']+' · 发送快照\n\n'+format_request(record['payload']))

    def toggle_subtitle(self):
        if self.subtitle.isVisible():
            self.subtitle.close()
        else:
            self.show_subtitle()

    def show_subtitle(self):
        self.subtitle.show()
        self.subtitle.raise_()

    def render(self, *_):
        self.selected_explanation = None
        enabled = {key for key, check in self.filters.items() if check.isChecked()}
        self.subtitle.set_content(self.source, self.items, enabled)
        self.tree.clear()
        for number, item in enumerate(self.items):
            if item['category'] in enabled:
                entry = QTreeWidgetItem([CATEGORIES[item['category']][0], item['subtype'], item['unit']])
                entry.setData(0, Qt.UserRole, number)
                self.tree.addTopLevelItem(entry)
        self.details.setText('点击字幕标注查看解释；点击列表条目定位返回 JSON。')
        self.preview_item.blockSignals(True)
        self.preview_item.clear()
        self.preview_item.addItem('未选择标注', None)
        for number, item in enumerate(self.items):
            self.preview_item.addItem((item['subtype']+' · ' if item['subtype'] else '')+item['unit'], number)
        self.preview_item.blockSignals(False)
        self.refresh_request_previews()

    def reset_explanations(self, offline=False):
        self.revision += 1
        self.explanation_cache.clear()
        self.explanation_pending.clear()
        self.selected_explanation = None
        self.offline = offline

    def display_explanation(self, number, text, reveal=True):
        self.subtitle.show_explanation(number, text)
        if reveal:
            self.show_subtitle()
        item = self.items[number]
        quotes = ' / '.join(self.source[a:b] for a,b in item['ranges'])
        self.details.setText(f"{item['subtype'] + ' · ' if item['subtype'] else ''}{item['unit']}\n原文：{quotes}\n{text}")

    def select_item(self, number):
        self.preview_item.setCurrentIndex(self.preview_item.findData(number))
        self.refresh_request_previews()
        prompt, model = self.explanation_prompt.toPlainText(), self.model.currentText()
        token = (self.revision, number, prompt, model)
        self.selected_explanation = token
        for i in range(self.tree.topLevelItemCount()):
            entry = self.tree.topLevelItem(i)
            if entry.data(0, Qt.UserRole) == number:
                self.tree.setCurrentItem(entry)
        if self.offline:
            self.display_explanation(number, DEMO_EXPLANATIONS[number])
            return
        if token in self.explanation_cache:
            self.display_explanation(number, self.explanation_cache[token])
            return
        if token in self.explanation_pending:
            self.display_explanation(number, '正在解释…')
            return
        key = self.key.text().strip()
        try:
            if not key:
                raise ValueError('请填写 API Key 后再次点击此标注。')
            payload = build_explanation_payload(self.source, self.items[number], prompt, model)
        except ValueError as exc:
            self.display_explanation(number, str(exc))
            return
        self.explanation_pending.add(token)
        self.display_explanation(number, '正在解释…')
        self.record_request("第二层 · 解释", payload)
        threading.Thread(target=self.explanation_worker, args=(token,key,payload), daemon=True).start()

    def explanation_worker(self, token, key, payload):
        try:
            result = parse_explanation(request_annotations(key,payload))
            self.explanation_events.put((token, True, result))
        except Exception as exc:
            message = str(exc).replace(key,'[API Key]') if isinstance(exc,ValueError) else '解释请求失败，请点击重试。'
            self.explanation_events.put((token, False, message))

    def poll_explanations(self):
        while True:
            try:
                token, success, result = self.explanation_events.get_nowait()
            except queue.Empty:
                return
            self.explanation_pending.discard(token)
            if token[0] != self.revision:
                continue
            if success:
                self.explanation_cache[token] = result
            if token == self.selected_explanation:
                self.display_explanation(token[1], result, reveal=False)

    def demo(self):
        if self.busy:
            return
        self.reset_explanations(offline=True)
        self.source = SAMPLE
        self.english.setPlainText(SAMPLE)
        self.items = resolve_items(DEMO, SAMPLE)
        self.raw.setPlainText(json.dumps(DEMO, ensure_ascii=False, indent=2))
        self.rendered_raw = self.raw.toPlainText()
        _, self.rendered_locations, _ = decode_best_effort(self.rendered_raw)
        self.render()
        self.show_subtitle()
        self.status.setText('离线演示 · 无 API 请求')

    def clear_errors(self):
        self.error_tree.clear()
        self.error_tree.hide()
        self.raw.setExtraSelections([])

    def navigate_error(self, entry, column=0):
        start, end = entry.data(0, Qt.UserRole)
        content = self.raw.toPlainText()
        cursor = self.raw.textCursor()
        cursor.setPosition(len(content[:start].encode('utf-16-le')) // 2)
        cursor.setPosition(len(content[:end].encode('utf-16-le')) // 2, QTextCursor.KeepAnchor)
        self.raw.setTextCursor(cursor)
        self.raw.setFocus()
        self.raw.ensureCursorVisible()

    def show_json_error(self, error):
        self.clear_errors()
        content = self.raw.toPlainText()
        if isinstance(error, json.JSONDecodeError):
            entries = [(f'JSON 第 {error.lineno} 行第 {error.colno} 列', str(error), error.pos, min(error.pos+1,len(content)))]
        else:
            if content == getattr(self,'rendered_raw',None):
                locations = self.rendered_locations
            else:
                _, locations, _ = decode_best_effort(content)
            entries = []
            for issue in getattr(error, 'errors', [error]):
                if hasattr(issue,'raw_range'):
                    start,end=issue.raw_range
                    line=content.count('\n',0,start)+1
                    entries.append((f'返回 JSON · 第 {line} 行',str(issue),start,end))
                    continue
                path = getattr(issue,'path',())
                if not path:
                    sentence = re.search(r'第 (\d+) 句',str(issue))
                    if sentence: path = ('sentences',int(sentence[1])-1)
                while path not in locations and path: path = path[:-1]
                start, end = locations.get(path,(0,len(content)))
                position = getattr(issue,'position',None)
                if position is not None and content[start:start+1] == '"':
                    boundaries = decoded_boundaries(content,start,end)
                    decoded = json.loads(content[start:end])
                    position = min(position,len(boundaries)-1)
                    token = TAG_RE.match(decoded,position)
                    stop = min(position+(len(token.group()) if token else 1),len(boundaries)-1)
                    start, end = boundaries[position], boundaries[stop]
                label = ('第 '+str(path[1]+1)+' 句') if len(path)>1 and path[0]=='sentences' else '返回 JSON'
                identity = getattr(issue,'identity','')
                if identity: label += ' · '+identity
                if len(path)>3 and path[2]=='annotations': label += f' · 第 {path[3]+1} 条属性'
                entries.append((label,str(issue),start,end))
        for label, message, start, end in entries:
            entry = QTreeWidgetItem([label,message])
            entry.setToolTip(1,message)
            entry.setData(0,Qt.UserRole,(start,end))
            self.error_tree.addTopLevelItem(entry)
        self.error_tree.setVisible(bool(entries))
        if entries:
            self.error_tree.setCurrentItem(self.error_tree.topLevelItem(0))
            self.navigate_error(self.error_tree.topLevelItem(0))

    def apply_json(self):
        if self.busy: return
        self.apply_result(self.raw.toPlainText(),self.english.toPlainText(),'本地重新渲染 · 无 API 请求')

    def apply_result(self, raw, source, label):
        value, locations, issues = decode_best_effort(raw)
        items = resolve_items(value,source,issues) if value is not None else []
        self.reset_explanations()
        self.source,self.items=source,items
        self.rendered_raw,self.rendered_locations=raw,locations
        self.render();self.show_subtitle()
        self.clear_errors()
        if issues:
            notice=AnnotationError('解析提醒');notice.errors=issues
            self.show_json_error(notice)
        self.status.setToolTip('\n'.join(str(i) for i in issues))
        self.status.setText(f'{label} · {len(items)} 个可用标注 · {len(issues)} 条提醒'
                            + ('；已显示本次原文。' if not items else ''))

    def highlight_item_json(self, number):
        if not isinstance(number,int) or not 0 <= number < len(self.items): return
        raw=self.raw.toPlainText()
        if raw != getattr(self,'rendered_raw',None):
            self.status.setText('提醒：返回 JSON 已编辑，请先应用后再定位元素。')
            return
        item=self.items[number]; path=item['json_path']; annotation=item['annotation']
        locations=self.rendered_locations
        ranges=[]
        if path in locations: ranges.append(locations[path])
        markup_path=path[:2]+('annotated',)
        if markup_path in locations:
            start,end=locations[markup_path]
            markup=json.loads(raw[start:end]); boundaries=decoded_boundaries(raw,start,end)
            opening=None
            for match in TAG_RE.finditer(markup):
                if match[2] != annotation['id']: continue
                if not match[1]: opening=match.start()
                elif opening is not None:
                    ranges.append((boundaries[opening],boundaries[match.end()]))
                    opening=None
        selections=[]
        for start,end in ranges:
            selection=QTextEdit.ExtraSelection()
            cursor=self.raw.textCursor()
            cursor.setPosition(len(raw[:start].encode('utf-16-le'))//2)
            cursor.setPosition(len(raw[:end].encode('utf-16-le'))//2,QTextCursor.KeepAnchor)
            selection.cursor=cursor
            selection.format.setBackground(QColor('#665128'))
            selection.format.setForeground(QColor('#fff1bc'))
            selections.append(selection)
        self.raw.setExtraSelections(selections)
        if selections:
            self.raw.setTextCursor(selections[0].cursor)
            self.raw.setFocus();self.raw.ensureCursorVisible()
        self.details.setText(f"JSON 定位 · 第 {annotation['sentence_index']} 句 · {annotation['id']} · {item['unit']}\n已标出属性记录与 {len(ranges)-1} 个范围片段；点击字幕标注可查看解释。")

    def set_busy(self, busy):
        self.busy = busy
        for widget in (self.submit_button, self.demo_button, self.prompt, self.english, self.raw, self.apply_json_button):
            widget.setEnabled(not busy)

    def submit(self):
        if self.busy:
            return
        key = self.key.text().strip()
        source = self.english.toPlainText()
        try:
            if not key:
                raise ValueError('请填写 API Key，或使用离线演示。')
            payload = build_payload(source, self.prompt.toPlainText(), self.model.currentText())
        except ValueError as exc:
            self.status.setText(str(exc))
            return
        self.reset_explanations()
        self.source,self.items=source,[]
        self.render();self.show_subtitle()
        self.set_busy(True)
        self.raw.clear()
        self.status.setText('正在标注…')
        self.record_request("第一层 · 标注", payload)
        threading.Thread(target=self.worker, args=(key,payload,source), daemon=True).start()

    def worker(self, key, payload, source):
        started=time.monotonic()
        try:
            body=json.loads(request_annotations(key,payload))
            choice=body['choices'][0]
            raw=choice['message']['content']
            if not isinstance(raw,str): raise ValueError('响应没有可读取的文本内容。')
            self.events.put((True,(raw,source,choice.get('finish_reason')),time.monotonic()-started))
        except Exception as exc:
            message=str(exc).replace(key,'[API Key]') if isinstance(exc,ValueError) else '请求或响应读取失败，请重试。'
            self.events.put((False,message,time.monotonic()-started))

    def poll(self):
        self.poll_explanations()
        try: success,result,elapsed=self.events.get_nowait()
        except queue.Empty: return
        self.set_busy(False)
        if success:
            raw,source,reason=result
            self.raw.setPlainText(raw)
            self.apply_result(self.raw.toPlainText(),source,f'返回解析 · {elapsed:.1f} 秒')
            if reason not in (None,'stop'):
                self.status.setText(self.status.text()+f' · 提醒：响应未正常结束（{reason}），请检查完整性。')
        else:
            self.status.setText('请求提醒：'+str(result)+'；已显示本次原文。')

    def closeEvent(self, event):
        if self.annotation_library.has_unsaved() or self.explanation_library.has_unsaved():
            answer = QMessageBox.question(self, '未保存提示词', '有未保存的提示词草稿。是否放弃草稿并关闭？', QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Cancel)
            if answer != QMessageBox.Discard:
                event.ignore()
                return
        self.preview_timer.stop()
        self.poll_timer.stop()
        self.subtitle.close()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnnotationWindow()
    window.show()
    sys.exit(app.exec())
