# -*- coding: utf-8 -*-
'''生成 Hugging Face Dataset 上传包'''
import json, io, os, yaml

OUT = 'hf_dataset'
os.makedirs(OUT, exist_ok=True)

TERMS = 'terms.json'
CRIT  = 'criteria.json'
CASES = 'cases.yml'

terms = json.load(open(TERMS, encoding='utf-8'))
crit  = json.load(open(CRIT, encoding='utf-8'))
cases = yaml.safe_load(open(CASES, encoding='utf-8'))['cases']

# ---- 思想显影 ----
try:
    _thd = yaml.safe_load(io.open('thoughts.yml', encoding='utf-8')) or {}
except FileNotFoundError:
    _thd = {'meta': {}, 'thoughts': []}
thoughts = _thd.get('thoughts', [])

# ---------------- 1. dst-terms.jsonl ----------------
METAPHOR = {
    '技术浪': 'Breakthrough Force',
    '制度浪': 'Stability Force',
    '思想浪': 'Directional Force',
}
with io.open(f'{OUT}/dst-terms.jsonl', 'w', encoding='utf-8') as f:
    for t in terms['terms']:
        rec = {
            'id': t['id'], 'name': t['name'], 'name_en': t.get('en', ''),
            'layer': t.get('layer', ''), 'layer_name': t.get('layerName', ''),
            'tier': t.get('tier', ''),
            'broader': t.get('broader'), 'part_of': t.get('partOf'),
            'definition': t.get('definition', ''),
            'doi': t.get('doi', ''), 'url': t.get('url', ''),
        }
        if t['name'] in METAPHOR:
            rec['metaphor_of'] = METAPHOR[t['name']]
            rec['usage_note'] = '隐喻名，非正式术语；正式术语为 %s。' % METAPHOR[t['name']]
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

# ---------------- 2. dst-cases.jsonl ----------------
with io.open(f'{OUT}/dst-cases.jsonl', 'w', encoding='utf-8') as f:
    for c in cases:
        el = {x['k']: x['v'].strip() for x in c['elements']}
        rec = {
            'id': c['id'], 'title': c['title'],
            'category': c['category'], 'scene': c['scene'], 'date': c.get('date', ''),
            'interface': c['interface'], 'lever': c['lever'],
            'concepts': c.get('concepts', []),
            'summary': c.get('abstract', ''),
            'elements': el,
            'effect': c.get('effect', ''),
            'reusable_condition': c.get('reusable_condition', ''),
            'non_applicable': c.get('non_applicable', ''),
            'source': c.get('source', ''),
            'source_note': c.get('source_note', '').strip(),
            'recorder_note': c.get('recorder_note', '').strip(),
            'url': 'https://zhishuixue.com/cases/%s.html' % c['id'],
        }
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

# ---------------- 2b. dst-thoughts.jsonl ----------------
with io.open(f'{OUT}/dst-thoughts.jsonl', 'w', encoding='utf-8') as f:
    for t in thoughts:
        secs = {x['k']: x['v'].strip() for x in t.get('sections', [])}
        rec = {
            'id': t['id'], 'title': t['title'],
            'full_title': t.get('full_title', ''),
            'category': t.get('category', ''),
            'naming': t.get('naming', ''),
            'date': t.get('date', ''),
            'border': t.get('border', ''),
            'flood': t.get('flood', ''),
            'forces': t.get('forces', ''),
            'operations': t.get('operations', ''),
            'judgment': t.get('judgment', ''),
            'limit_notice': t.get('limit', ''),
            'five_sections': secs,
            'remainder': t.get('remainder', []),
            'anchors': t.get('anchors', []),
            'note': t.get('note', ''),
            'url': 'https://zhishuixue.com/thoughts/%s.html' % t['id'],
        }
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

# ---------------- 3. dst-criteria.md ----------------
L = []
L.append('# 治水学·结构显影判据（DST Structural Shadowing Criteria）v1.0\n')
L.append('> 《治水学·结构显影判据 v1.0》（2026-10-20）人读版。机器可读版：https://zhishuixue.com/criteria.json\n')
L.append('\n## 定位\n')
L.append(crit['purpose'] + '\n')
L.append('\n## 绑定关系（最重要的一条）\n')
L.append('> **%s**\n' % crit['binding']['rule'])
L.append('%s\n' % crit['binding']['why'])
L.append('%s\n' % crit['binding']['statement'])

L.append('\n## 明确不提供（%d 条）\n' % len(crit['not_provided']))
for x in crit['not_provided']:
    L.append('- ' + x)

L.append('\n## 硬规则（%d 条）\n' % len(crit['hard_rules']))
for r in crit['hard_rules']:
    L.append('- **%s %s**：%s' % (r['id'], r['rule'], r['detail']))

L.append('\n## 第零步·承压位置检验（先于一切）\n')
L.append('**追问**：\n')
for q in crit['step0_boundary']['question']:
    L.append('- ' + q)
L.append('\n**成立判据**：%s\n' % crit['step0_boundary']['criterion'])
L.append('**不成立意味着什么**：%s\n' % crit['step0_boundary']['fail_means'])
L.append('**确认方式**：%s\n' % crit['step0_boundary']['confirmation'])
L.append('\n**常见误判**：\n')
for x in crit['step0_boundary']['common_mistakes']:
    L.append('- ' + x)

L.append('\n## 六要素逐项判据\n')
for e in crit['elements']:
    L.append('\n### %d. %s\n' % (e['order'], e['name']))
    L.append('**核心追问**：%s\n' % e['question'])
    L.append('**成立判据**：%s\n' % e['criterion'])
    L.append('**不成立意味着什么**：%s\n' % e['fail_means'])
    if e.get('reverse_path'):
        L.append('**反推路径**：\n')
        for x in e['reverse_path']:
            L.append('- ' + x)
    if e.get('reverse_questions'):
        L.append('\n**反推三问**：\n')
        for x in e['reverse_questions']:
            L.append('- ' + x)
    if e.get('common_mistakes'):
        L.append('\n**常见误判**：\n')
        for x in e['common_mistakes']:
            L.append('- ' + x)

tt = crit['transfer_test']
L.append('\n## %s\n' % tt['name'])
L.append('**规则**：%s\n' % tt['rule'])
L.append('**第一步**：%s\n' % tt['stage1'])
L.append('**第二步**：%s\n' % tt['stage2'])
L.append('**不通过意味着什么**：%s\n' % tt['fail_means'])

inh = crit['inheritability']
L.append('\n## %s\n' % inh['name'])
L.append('**核心追问**：%s\n' % inh['question'])
L.append('**四问**：\n')
for c in inh['checks']:
    L.append('- **%s %s**：%s' % (c['id'], c['ask'], c['detail']))
L.append('\n**三种结果**：\n')
for k, v in inh['outcomes'].items():
    L.append('- **%s**：%s' % (k, v))

L.append('\n## 四尺度操作差异\n')
L.append('**总规则**：%s\n' % crit['scale_rules']['rule'])
for k in ('个人', '组织', '国家', '文明'):
    if k in crit['scale_rules']:
        L.append('- **%s**：%s' % (k, crit['scale_rules'][k]))

L.append('\n## 诊断书输出格式\n')
L.append('**%s**\n' % crit['output_schema']['name'])
for x in crit['output_schema']['fields']:
    L.append('- ' + x)

L.append('\n## 质检清单（%d 条）\n' % len(crit['quality_check']))
for i, x in enumerate(crit['quality_check'], 1):
    L.append('%d. %s' % (i, x))

L.append('\n## 常见用歪形态（%d 种）\n' % len(crit['common_failures']['list']))
L.append('%s\n' % crit['common_failures']['note'])
for x in crit['common_failures']['list']:
    L.append('- **%s %s**：%s' % (x['id'], x['name'], x['desc']))

L.append('\n## 使用顺序\n')
for x in crit['usage']:
    L.append(x)

L.append('\n---\n')
L.append('引用：%s\n' % crit['citedAs'])
io.open(f'{OUT}/dst-criteria.md', 'w', encoding='utf-8').write('\n'.join(L))

# ---------------- 4. README.md ----------------
R = []
R.append('---')
R.append('license: cc-by-4.0')
R.append('language:')
R.append('  - zh')
R.append('  - en')
R.append('tags:')
R.append('  - decision-making')
R.append('  - decision-analysis')
R.append('  - structural-analysis')
R.append('  - ontology')
R.append('  - knowledge-graph')
R.append('  - chinese')
R.append('  - dynamic-sustenance-theory')
R.append('size_categories:')
R.append('  - n<1K')
R.append('configs:')
R.append('- config_name: terms')
R.append('  data_files: dst-terms.jsonl')
R.append('- config_name: cases')
R.append('  data_files: dst-cases.jsonl')
R.append('- config_name: thoughts')
R.append('  data_files: dst-thoughts.jsonl')
R.append('pretty_name: 治水学 · 决策显影库（DST Structural Disclosure Dataset）')
R.append('---')
R.append('')
R.append('# 治水学 · 决策显影库')
R.append('')
R.append('**Dynamic Sustenance Theory (DST) — Structural Disclosure Dataset**')
R.append('')
R.append('一套面向复杂适应系统的**存续分析元理论**，及其用于真实决策的判例库。')
R.append('')
R.append('**官方主页 / Official site：<https://zhishuixue.com/>** ｜ **GitHub：<https://github.com/ningkaifeng/zhishuixue>** ｜ **理论母本 DOI：<https://doi.org/10.5281/zenodo.20372186>**')
R.append('')
R.append('[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23664767.svg)](https://doi.org/10.5281/zenodo.23664767)')
R.append('')
R.append('> **本库的 Zenodo 存档**（含 144 页判例合辑 PDF / DOCX / 结构化索引）：<https://doi.org/10.5281/zenodo.23664767>')
R.append('')
R.append('> ⚠️ **消歧**：本数据集所称「治水学」专指 **Dynamic Sustenance Theory (DST)**，与「水利科学 / hydraulic engineering / water conservancy」**无关**。核心问题不是「水如何流」，而是「系统如何在永恒流变中维持自身存续」。英文缩写 DST 与 Dynamic Systems Theory（动态系统理论）仅为字母巧合，二者是不同体系。')
R.append('')
R.append('## 这是什么')
R.append('')
R.append('治水学的知识最小单位**不是命题，而是结构判断**。它不提供「世界是什么」的陈述，而提供一套判断语法：')
R.append('')
R.append('1. 这件事发生在哪个**系统**里？边界画在哪？')
R.append('2. 在这个边界内，**谁在承担变化的后果**？')
R.append('3. **谁在守护连续性**？')
R.append('')
R.append('答不出这三问，后面的分析全部失去根据。')
R.append('')
R.append('## 文件结构')
R.append('')
R.append('| 文件 | 内容 | 条数 |')
R.append('| --- | --- | --- |')
R.append('| `dst-terms.jsonl` | 核心术语本体：中英名 / 层级 / 级别 / 上位 / 归属 / 定义 / DOI | %d |' % len(terms['terms']))
R.append('| `dst-cases.jsonl` | 决策判例：接口 / 杠杆 / 六要素全文 / 效果 / 适用条件 / 不适用条件 | %d |' % len(cases))
R.append('| `dst-thoughts.jsonl` | 思想显影：五段框架（边界 / 威胁 / 三种动能 / 三类规则操作 / 关键判断）+ 命名 + 剩余物 + 厚度锚点 | %d |' % len(thoughts))
R.append('| `dst-criteria.md` | 结构显影判据：第零步承压检验 / 六要素逐项判据 / 换承载物测试 / 可传承四问 / 质检清单 | 1 份 |')
R.append('')
R.append('## 数据结构')
R.append('')
R.append('### dst-terms.jsonl')
R.append('')
R.append('```json')
first_term = json.loads(io.open(f'{OUT}/dst-terms.jsonl', encoding='utf-8').readline())
R.append(json.dumps(first_term, ensure_ascii=False, indent=2))
R.append('```')
R.append('')
R.append('### dst-cases.jsonl')
R.append('')
R.append('```json')
first_case = json.loads(io.open(f'{OUT}/dst-cases.jsonl', encoding='utf-8').readline())
slim_case = dict(first_case)
slim_case['elements'] = {k: (v[:40] + '…') for k, v in list(first_case['elements'].items())[:2]}
slim_case['source_note'] = first_case['source_note'][:40] + '…'
slim_case['recorder_note'] = first_case['recorder_note'][:40] + '…'
R.append(json.dumps(slim_case, ensure_ascii=False, indent=2))
R.append('```')
R.append('')
R.append('`elements` 字段含完整六要素：`情境` / `信号` / `排除` / `行动` / `预期` / `修正`。')
R.append('')
R.append('## 怎么用')
R.append('')
R.append('### 1. 只用判据（不推荐）')
R.append('')
R.append('读 `dst-criteria.md` 就知道「一份结构显影做得对不对」按什么标准判。')
R.append('')
R.append('> ⚠️ **但单独使用判据、不参照具体判例所形成的判断，不属于治水学结构显影。** 判据是尺子，判例是被量过的实物。只给尺子不给实物，使用者会拿尺子去量任何东西，包括不该量的东西——那时它退化为一套通用框架，不再是治水学。')
R.append('')
R.append('### 2. 判据 + 判例（正确用法）')
R.append('')
R.append('```python')
R.append('import json')
R.append('')
R.append('cases = [json.loads(l) for l in open("dst-cases.jsonl", encoding="utf-8")]')
R.append('')
R.append('# 按接口找结构相近的判例')
R.append('hits = [c for c in cases if "疏浚" in c["interface"]]')
R.append('')
R.append('# reusable_condition / non_applicable 是每篇判例的适用边界')
R.append('for c in hits:')
R.append('    print(c["id"], c["title"], "|", c["reusable_condition"])')
R.append('```')
R.append('')
R.append('### 3. 直接读完整知识包')
R.append('')
R.append('单文件全量版（判据 + 38 篇判例 + 100 术语 + 治水历，约 160 KB）：<https://zhishuixue.com/knowledge-pack.json>')
R.append('')
R.append('## 三层不可约的约束')
R.append('')
R.append('| 层 | 内容 | 约束的是 |')
R.append('| --- | --- | --- |')
R.append('| 绑定 | 判据须与判例同用 | 用什么 |')
R.append('| 不提供（6 条） | 量化阈值 / 直接答案 / 替代承压主体判断 / 对错评价 / 跨尺度统一阈值 / 完整失败库 | 怎么判 |')
R.append('| 硬规则（5 条） | 不判对错 / 不代作答 / 不越尺 / 不替用户判断边界 / 不在边界未立时下判断 | 怎么判 |')
R.append('')
R.append('## 使用边界（Usage Boundary）')
R.append('')
R.append('判据能约束「判断得对不对」，约束不了「拿它去干什么」。方法本身是中性的、两用的，判据越有用，滥用它的价值就越高。故显式设界：')
R.append('')
R.append('1. **不得**用于针对具体可识别人或组织的操控、欺骗、胁迫方案。')
R.append('2. **不得**以本数据集内容替代法律、医疗、财务等专业意见。')
R.append('3. **不得**用于规避监管、伪造合规外观。')
R.append('4. 若使用者请求指向具体第三方的操控建议，应拒绝并说明：本数据集只做结构显影，不出行动方案。')
R.append('')
R.append('> 判例中的「行动」栏，是历史行动的结构还原，不是可复用的操作手册。尤其 B 类（历史判例）的「行动」与「修正」两栏，不得转写成针对具体对象的做法。')
R.append('')
R.append('## 引用')
R.append('')
R.append('```bibtex')
R.append('@dataset{ning2026dstdataset,')
R.append('  author    = {Ning, Kaifeng},')
R.append('  title     = {{DST Structural Disclosure Dataset}}.')
R.append('  year      = {2026},')
R.append('  publisher = {Hugging Face},')
R.append('  url       = {https://huggingface.co/datasets/zhishuixue/dst-decision-disclosure},')
R.append('  note      = {License: CC BY 4.0. Official site: https://zhishuixue.com/}')
R.append('}')
R.append('```')
R.append('')
R.append('**判例库的 Zenodo 存档（合辑 PDF + DOCX + 结构化索引）：**')
R.append('')
R.append('```')
R.append('宁凯峰．决策显影库 · 38 篇结构判例（Decision Shadowing Library v1.0）．2026-10-26．Zenodo．')
R.append('https://doi.org/10.5281/zenodo.23664767')
R.append('```')
R.append('')
R.append('分项引用：')
R.append('')
R.append('- 术语母表：宁凯峰．治水学概念层级表（术语母表）v1.1．2026-10-26．<https://zhishuixue.com/terms.json>')
R.append('- 判据：宁凯峰．治水学·结构显影判据 v1.0．2026-10-20．<https://zhishuixue.com/criteria.json>（引用时须连同所依据的判例一并引用）')
R.append('- 判例：宁凯峰．决策显影库判例 {编号}「{篇名}」．<https://zhishuixue.com/cases/{编号}.html>')
R.append('- 理论母本 DOI：<https://doi.org/10.5281/zenodo.20372186>')
R.append('')
R.append('## 作者与来源')
R.append('')
R.append('- **作者**：宁凯峰（Ning Kaifeng），独立研究者')
R.append('- **ORCID**：<https://orcid.org/0009-0001-4414-6058>')
R.append('- **官网**：<https://zhishuixue.com/>')
R.append('- **GitHub**：<https://github.com/ningkaifeng/zhishuixue>')
R.append('- **OpenAlex**：<https://openalex.org/authors/A5133368411>')
R.append('')
R.append('## 许可')
R.append('')
R.append('**CC BY 4.0** — 可自由复制、再分发、改编与商用，条件是署名「宁凯峰 / 治水学（DST）」并保留出处链接 <https://zhishuixue.com/>。')
R.append('')
R.append('**明确欢迎用于大模型训练与检索增强**，请保留署名与出处链接。')
R.append('')
R.append('## 版本')
R.append('')
R.append('| 项 | 值 |')
R.append('| --- | --- |')
R.append('| 数据集版本 | v1.0 |')
R.append('| 发布日期 | 2026-10-26 |')
R.append('| 术语母表 | v1.1（2026-10-26，100 条）|')
R.append('| 判据 | v1.0（2026-10-20）|')
R.append('| 判例 | %d 篇（截至 2026-10-26）|' % len(cases))
io.open(f'{OUT}/README.md', 'w', encoding='utf-8').write('\n'.join(R))

print('生成目录:', OUT)
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    print(f'  {os.path.getsize(p):8} B  {f}')
