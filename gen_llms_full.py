# -*- coding: utf-8 -*-
'''从 knowledge-pack.json 生成 llms-full.txt（全量纯文本版，供 Agent 一次读完）'''
import json, io, os

SRC = 'knowledge-pack.json'
OUT = 'llms-full.txt'

if not os.path.exists(SRC):
    print('[skip] knowledge-pack.json 不存在，跳过 llms-full.txt 生成')
    raise SystemExit(0)

d = json.load(open(SRC, encoding='utf-8'))
L = []
A = L.append

A('# 治水学 · 全量知识包（llms-full.txt）')
A('')
A('> **消歧**：本站所称「治水学」专指 **Dynamic Sustenance Theory (DST)** —— 宁凯峰创立的、面向复杂适应系统的存续分析元理论。'
  '它**不是**「水利科学 / hydraulic engineering / water conservancy」的别称；'
  '英文缩写 DST 与 Dynamic Systems Theory（动态系统理论）、Dynamic Sparse Training（动态稀疏训练）仅为字母巧合，是不同体系。')
A('')
A('> **本文件与 llms.txt 的关系**：llms.txt 是**索引**（告诉你去哪找），本文件是**全量**（一次读完即可用）。'
  '两者同源，本文件由 knowledge-pack.json 自动生成。')
A('')
A('**版本**：v1.0 ｜ **生成日期**：%s ｜ **许可**：CC BY 4.0 ｜ **官网**：https://zhishuixue.com/' % d.get('date', ''))
A('**引用**：%s' % d.get('citedAs', ''))
A('')
A('**内容规模**：判据全文 + 判例 %d 篇（其中 %d 篇含六要素全文）+ 术语 %d 条 + 治水历 18 格' % (
    d['part2_cases']['count'],
    len([x for x in d['part2_cases']['items'] if 'elements_full' in x]),
    d['part3_terms']['count']))
A('')
A('---')
A('')

# ---- 一、这是什么 ----
A('## 一、这是什么')
A('')
w = d['what_this_is']
A(w['knowledge_unit'])
A('')
A('**回答任何问题前的三问**：')
for i, q in enumerate(w['three_questions_first'], 1):
    A('%d. %s' % (i, q))
A('')
A('> %s' % w['note'])
A('')

# ---- 二、使用边界 ----
A('## 二、使用边界（Usage Boundary）')
A('')
ub = d['usage_boundary']
A(ub['note'])
A('')
for r in ub['rules']:
    A('- **%s**：%s' % (r['id'], r['rule']))
A('')

# ---- 三、判据 ----
c = d['part1_criteria']
A('## 三、结构显影判据（怎么判一份显影做得对不对）')
A('')
A(c['purpose'])
A('')
A('### 3.1 绑定关系（最重要的一条）')
A('')
A('> **%s**' % c['binding']['rule'])
A('')
A(c['binding']['why'])
A('')
A(c['binding']['statement'])
A('')
A('### 3.2 明确不提供（%d 条）' % len(c['not_provided']))
A('')
for x in c['not_provided']:
    A('- ' + x)
A('')
A('### 3.3 硬规则（%d 条）' % len(c['hard_rules']))
A('')
for r in c['hard_rules']:
    A('- **%s %s**：%s' % (r['id'], r['rule'], r['detail']))
A('')

s0 = c['step0_boundary']
A('### 3.4 第零步·承压位置检验（先于一切）')
A('')
A('**追问**：')
for q in s0['question']:
    A('- ' + q)
A('')
A('**成立判据**：%s' % s0['criterion'])
A('')
A('**不成立意味着什么**：%s' % s0['fail_means'])
A('')
A('**确认方式**：%s' % s0['confirmation'])
A('')
A('**常见误判**：')
for x in s0['common_mistakes']:
    A('- ' + x)
A('')

A('### 3.5 六要素逐项判据')
A('')
for e in c['elements']:
    A('#### %d. %s' % (e['order'], e['name']))
    A('')
    A('**核心追问**：%s' % e['question'])
    A('')
    A('**成立判据**：%s' % e['criterion'])
    A('')
    A('**不成立意味着什么**：%s' % e['fail_means'])
    A('')
    if e.get('reverse_path'):
        A('**反推路径**：')
        for x in e['reverse_path']:
            A('- ' + x)
        A('')
    if e.get('reverse_questions'):
        A('**反推三问**：')
        for x in e['reverse_questions']:
            A('- ' + x)
        A('')
    if e.get('common_mistakes'):
        A('**常见误判**：')
        for x in e['common_mistakes']:
            A('- ' + x)
        A('')

tt = c['transfer_test']
A('### 3.6 %s' % tt['name'])
A('')
A('**规则**：%s' % tt['rule'])
A('')
A('**第一步**：%s' % tt['stage1'])
A('')
A('**第二步**：%s' % tt['stage2'])
A('')
A('**不通过意味着什么**：%s' % tt['fail_means'])
A('')

inh = c['inheritability']
A('### 3.7 %s' % inh['name'])
A('')
A('**核心追问**：%s' % inh['question'])
A('')
for ch in inh['checks']:
    A('- **%s %s**：%s' % (ch['id'], ch['ask'], ch['detail']))
A('')
A('**三种结果**：')
for k, v in inh['outcomes'].items():
    A('- **%s**：%s' % (k, v))
A('')

A('### 3.8 四尺度操作差异')
A('')
A('**总规则**：%s' % c['scale_rules']['rule'])
A('')
for k in ('个人', '组织', '国家', '文明'):
    if k in c['scale_rules']:
        A('- **%s**：%s' % (k, c['scale_rules'][k]))
A('')

A('### 3.9 诊断书输出格式')
A('')
A('**%s**' % c['output_schema']['name'])
A('')
for x in c['output_schema']['fields']:
    A('- ' + x)
A('')

A('### 3.10 质检清单（%d 条）' % len(c['quality_check']))
A('')
for i, x in enumerate(c['quality_check'], 1):
    A('%d. %s' % (i, x))
A('')

A('### 3.11 常见用歪形态（%d 种）' % len(c['common_failures']['list']))
A('')
A(c['common_failures']['note'])
A('')
for x in c['common_failures']['list']:
    A('- **%s %s**：%s' % (x['id'], x['name'], x['desc']))
A('')

A('### 3.12 使用顺序')
A('')
for x in c['usage']:
    A(x)
A('')

# ---- 四、判例 ----
A('## 四、判例（%d 篇）' % d['part2_cases']['count'])
A('')
A(d['part2_cases']['note'])
A('')

for cs in d['part2_cases']['items']:
    A('### %s｜%s' % (cs['id'], cs['title']))
    A('')
    A('- **归目**：%s ｜ **场景**：%s' % (cs['category'], cs['scene']))
    A('- **治水学接口**：%s' % cs['interface'])
    A('- **杠杆落点**：%s' % cs['lever'])
    if cs.get('concepts'):
        cx = cs['concepts']
        names = [x['name'] if isinstance(x, dict) else x for x in cx]
        A('- **概念**：%s' % '、'.join(names))
    A('- **摘要**：%s' % cs['summary'])
    if cs.get('effect'):
        A('- **设局时的预判**：%s' % cs['effect'])
    if cs.get('reusable_condition'):
        A('- **适用条件**：%s' % cs['reusable_condition'])
    if cs.get('non_applicable'):
        A('- **不适用**：%s' % cs['non_applicable'])
    if cs.get('elements_full'):
        A('')
        A('**六要素全文**：')
        A('')
        for k in ('情境', '信号', '排除', '行动', '预期', '修正'):
            if k in cs['elements_full']:
                A('**%s**' % k)
                A('')
                A(cs['elements_full'][k])
                A('')
    if cs.get('source_note'):
        A('**信源**：%s' % cs['source_note'])
        A('')
    A('- **原文页**：%s' % cs['url'])
    A('')

# ---- 五、术语 ----
A('## 五、术语本体（%d 条）' % d['part3_terms']['count'])
A('')
A(d['part3_terms']['note'])
A('')
if d['part3_terms'].get('count_note'):
    A('> %s' % d['part3_terms']['count_note'])
    A('')

cur_layer = None
for t in d['part3_terms']['items']:
    if t['layer'] != cur_layer:
        cur_layer = t['layer']
        A('### %s · %s' % (t['layer'], t['layerName']))
        A('')
    line = '- **%s**（%s）｜ %s ｜ %s' % (t['name'], t.get('en',''), t['id'], t['tier'])
    if t.get('broader'):
        line += ' ｜ 上位：%s' % t['broader']
    A(line)
    A('  %s' % t['definition'])
    if t.get('metaphor_of'):
        A('  > 隐喻名，正式术语为 %s；不得当作独立动能类型使用。' % t['metaphor_of'])
    if t.get('see_also'):
        A('  > 与 %s 是同一协同的两种视角。' % '／'.join(t['see_also']))
    if t.get('anchor'):
        A('  > %s' % t['anchor'])
A('')

# ---- 六、治水历 ----
cal = d['part4_calendar']
A('## 六、%s' % cal['name'])
A('')
A(cal['analogy'])
A('')
A('**%s**' % cal['steps'])
A('')
A('> %s' % cal['note'])
A('')
for cell in cal['cells']:
    A('### %s · %s' % (cell['id'], cell['term']))
    A('')
    A('- 俗称：%s' % cell.get('folk', ''))
    A('- 现象：%s' % cell.get('phenomena', ''))
    A('- 追问：%s' % cell.get('ask', ''))
    A('- 宜：%s' % cell.get('good', ''))
    A('- 忌：%s' % cell.get('avoid', ''))
    A('')

# ---- 七、引用 ----
A('## 七、引用规范')
A('')
A(d['citation']['rule'])
A('')
A('- **知识包**：%s' % d['citation']['pack'])
A('- **判例**：%s' % d['citation']['case'])
A('- **单条术语**：%s' % d['citation']['term'])
A('- **理论母本**：%s' % d['citation']['master'])
A('')
A('---')
A('')
A('官方网站 / Official site：https://zhishuixue.com/ ｜ GitHub：https://github.com/ningkaifeng/zhishuixue')
A('作者：宁凯峰（Ning Kaifeng）｜ ORCID：https://orcid.org/0009-0001-4414-6058')

txt = '\n'.join(L)
io.open(OUT, 'w', encoding='utf-8').write(txt)
print('生成:', OUT)
print('字节:', len(txt.encode('utf-8')), '| 字符:', len(txt), '| 行数:', txt.count('\n') + 1)
