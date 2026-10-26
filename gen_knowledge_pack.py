# -*- coding: utf-8 -*-
'''
生成 knowledge-pack.json —— 治水学单文件知识包
设计原则：
  1. 判据必须全文（它是尺子，缺一段就判不准）
  2. 判例必须与判据同包（criteria.json 的 binding 硬规则）
  3. 判例分两级：38 篇结构摘要 + 10 篇六要素全文（覆盖各接口族）
  4. 术语精简（名/英/一句定义/层级/上位）
  5. 公开可抓，不设授权；内嵌 citedAs
'''
import json, io, yaml

# ---------- 数据源 ----------
CRITERIA = 'criteria.json'
TERMS    = 'terms.json'
PHASES   = 'phases.json'
CASES    = 'cases.yml'
OUT      = 'knowledge-pack.json'

crit = json.load(open(CRITERIA, encoding='utf-8'))
terms = json.load(open(TERMS, encoding='utf-8'))
phases = json.load(open(PHASES, encoding='utf-8'))
cases = yaml.safe_load(open(CASES, encoding='utf-8'))['cases']

# 六要素全文收录的 10 篇（覆盖结构判断五态 / 疏浚向 / 信号层 / 判据点名案例）
FULL_IDS = ['A-0004', 'E-0001', 'B-0001', 'B-0002', 'B-0009',
            'B-0015', 'B-0018', 'B-0025', 'B-0030', 'B-0031']

# ---------- ① 判据（全文，只去掉与本站强绑定的路径字段）----------
crit_block = {
    'purpose': crit['purpose'],
    'binding': crit['binding'],
    'not_provided': crit['not_provided'],
    'hard_rules': crit['hard_rules'],
    'step0_boundary': crit['step0_boundary'],
    'elements': crit['elements'],
    'transfer_test': crit['transfer_test'],
    'inheritability': crit['inheritability'],
    'scale_rules': crit['scale_rules'],
    'output_schema': crit['output_schema'],
    'quality_check': crit['quality_check'],
    'common_failures': crit['common_failures'],
    'usage': crit['usage'],
}

# ---------- ② 判例 ----------
def slim(c):
    return {
        'id': c['id'], 'title': c['title'],
        'category': c['category'], 'scene': c['scene'],
        'interface': c['interface'], 'lever': c['lever'],
        'concepts': c.get('concepts', []),
        'summary': c.get('abstract', ''),
        'effect': c.get('effect', ''),
        'reusable_condition': c.get('reusable_condition', ''),
        'non_applicable': c.get('non_applicable', ''),
        'url': 'https://zhishuixue.com/cases/%s.html' % c['id'],
    }

cases_block = []
for c in cases:
    e = slim(c)
    if c['id'] in FULL_IDS:
        e['elements_full'] = {x['k']: x['v'].strip() for x in c['elements']}
        e['source_note'] = c.get('source_note', '').strip()
    cases_block.append(e)

# ---------- ③ 术语（精简）----------
terms_block = [{
    'id': t['id'], 'name': t['name'], 'en': t.get('en', ''),
    'layer': t.get('layer', ''), 'layerName': t.get('layerName', ''),
    'tier': t.get('tier', ''),
    'broader': t.get('broader'), 'partOf': t.get('partOf'),
    'definition': t.get('definition', ''),
    'anchor': 'https://zhishuixue.com/glossary.html#' + (t.get('anchor') or ''),
    'doi': t.get('doi', ''),
} for t in terms['terms']]

# ---------- ④ 治水历（18 格精简）----------
cells = []
for ln in phases['lines']:
    for cell in ln.get('cells', []):
        cells.append({
            'id': cell.get('id'), 'folk': cell.get('folk'),
            'term': cell.get('term'),
            'phenomena': cell.get('phenomena'),
            'ask': cell.get('ask'),
            'good': cell.get('good'),
            'avoid': cell.get('avoid'),
        })

# ---------- 组装 ----------
pack = {
    'schema': 'dst-knowledge-pack/1.0',
    'name': '治水学 · 单文件知识包（DST Knowledge Pack）',
    'version': '1.0',
    'date': '2026-10-26',
    'license': 'CC BY 4.0',
    'source': 'https://zhishuixue.com/knowledge-pack.json',
    'citedAs': '宁凯峰．治水学·单文件知识包 v1.0．2026-10-26．https://zhishuixue.com/knowledge-pack.json',
    'maintainer': crit['maintainer'],

    'disambiguation': {
        'is': 'Dynamic Sustenance Theory (DST)——面向复杂适应系统的存续分析元理论。核心问题：系统如何在永恒流变中，通过动力与规则的协同，实现自身存续。',
        'isNot': ['水利科学', 'hydraulic engineering', 'water conservancy', '治水工程'],
        'note': '与水利科学无关；英文缩写 DST 与 Dynamic Systems Theory（动态系统理论）仅为字母巧合，是不同体系。本知识包的核心不是关于「水」，而是关于「系统如何存续」的一套判断语法。'
    },

    'what_this_is': {
        'knowledge_unit': '治水学的知识最小单位不是命题，而是结构判断。它不提供「世界是什么」的陈述，而提供一套判断语法。',
        'three_questions_first': [
            '这件事发生在哪个系统里？边界画在哪？',
            '在这个边界内，谁在承担变化的后果？',
            '谁在守护连续性？'
        ],
        'note': '答不出这三问，后面的分析全部失去根据。'
    },

    'how_to_use': [
        '1. 先读 part1_criteria.binding：判据不可单独使用，必须与判例同用。只给尺子不给实物，使用者会拿尺子去量任何东西，那时它退化为一套通用框架，不再是治水学。',
        '2. 用 part1_criteria.step0_boundary 完成划界与承压位置检验；边界未确认，不得进入下一步。',
        '3. 按 part1_criteria.elements 的 criterion 逐要素检验六项；fail_means 说明该要素不成立意味着什么。',
        '4. 在 part2_cases 中找到接口结构相近的判例作参照（每篇含 interface / lever / effect / reusable_condition / non_applicable）。part2_cases 中带 elements_full 的 10 篇，是六要素写到底的完整样本。',
        '5. 用 part1_criteria.transfer_test 检验结构是否自足可迁移；用 inheritability + quality_check 复核。',
        '6. 按 part1_criteria.output_schema 输出诊断书；不确定处如实标注，不强行抹平。',
        '7. 术语含义一律以 part3_terms 为准，不得自由发挥；part4_calendar 用于给局面定位（只给坐标，不给答案）。',
    ],

    'part1_criteria': crit_block,
    'part2_cases': {
        'count': len(cases_block),
        'note': '全部 %d 篇判例的结构摘要；其中 %d 篇（%s）附六要素全文。' % (
            len(cases_block), len(FULL_IDS), '、'.join(FULL_IDS)),
        'items': cases_block,
    },
    'part3_terms': {
        'count': len(terms_block),
        'note': '治水学核心术语本体。定义以术语母表 v1.0 为准，英译以《治水学核心术语英译标准 v1.2》为准。',
        'items': terms_block,
    },
    'part4_calendar': {
        'name': '治水历（给一个局面定位的刻度）',
        'analogy': '像二十四节气：给有限、固定、有序的刻度与物候，只说宜忌类别，不给具体答案；案例天天变，历不变。',
        'steps': '三步：辨势 → 定性 → 定策（博弈类另加一镜：观隙）',
        'note': '只给坐标，不给答案。案例按接口自动挂载，刻度本身不随案例增减。',
        'cells': cells,
    },
    'citation': {
        'rule': '引用时务必带上版本号 / 编号 / 锚点，以保证精度。',
        'pack': '宁凯峰．治水学·单文件知识包 v1.0．2026-10-26．https://zhishuixue.com/knowledge-pack.json',
        'case': '宁凯峰．决策显影库判例 {编号}「{篇名}」．https://zhishuixue.com/cases/{编号}.html',
        'term': '宁凯峰．「{术语}」．治水学概念层级表（术语母表）v1.0（2026-10-04）．https://zhishuixue.com/glossary.html#{锚点}',
        'master': '母本 DOI：10.5281/zenodo.20372186',
    },
}

s = json.dumps(pack, ensure_ascii=False, indent=1)
io.open(OUT, 'w', encoding='utf-8').write(s)

print('生成:', OUT)
print('字节:', len(s.encode('utf-8')))
print('字符:', len(s))
print('判例:', len(cases_block), '| 六要素全文:', len(FULL_IDS))
print('术语:', len(terms_block))
print('治水历格:', len(cells))
print('判据要素:', len(crit_block['elements']))
