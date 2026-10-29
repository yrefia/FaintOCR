"""Offline demo sample, its annotation fixture and local explanations."""

# User-supplied annotation fixture; explanatory text is local demo data only.
SAMPLE = 'Only by calling our cherished assumptions into question can we approach the truth with intellectual humility.'
DEMO = {
    'sentences': [
        {
            'source': 'Only by calling our cherished assumptions into question can we approach the truth '
            'with intellectual humility.',
            'annotated': '<#S1>Only by <#E1>calling our <#W1>cherished</#W1> <#W2>assumptions</#W2> into '
            'question</#E1> can we</#S1> approach the truth with <#W3>intellectual</#W3> '
            '<#W4>humility</#W4>.',
            'annotations': [
                {'id': 'S1', 'category': 'Inversion', 'canonical': 'Only <Adverbial> <Auxiliary> <Subject>'},
                {
                    'id': 'E1',
                    'category': 'Idioms & Conventional Expressions',
                    'canonical': 'call <Object> into question',
                },
                {'id': 'W1', 'category': 'Beyond Top 2000', 'canonical': 'cherish'},
                {'id': 'W2', 'category': 'Beyond Top 2000', 'canonical': 'assumption'},
                {'id': 'W3', 'category': 'Beyond Top 2000', 'canonical': 'intellectual'},
                {'id': 'W4', 'category': 'Beyond Top 2000', 'canonical': 'humility'},
            ],
        }
    ]
}
DEMO_EXPLANATIONS = (
    'Only by 引导的状语置于句首，主句使用 can we approach 部分倒装，强调“只有通过……才能……”。',
    'call <Object> into question 表示“质疑……”。这里的 calling 是动名词形式，中间槽位 our cherished assumptions 指我们珍视的假设。',
    'cherished 源自 cherish，在此作定语，表示“珍视的、深信不疑的”，修饰 assumptions。',
    'assumptions 是 assumption 的复数，意为“假设、未经证实而接受的看法”。这里指我们习以为常的前提。',
    'intellectual 在此作形容词，与 humility 搭配，指对知识、推理和自身认识局限的态度。',
    'humility 意为“谦逊”。intellectual humility 指承认自身认识可能有局限、愿意修正观点的态度。',
)
