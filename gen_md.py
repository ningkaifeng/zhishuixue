# -*- coding: utf-8 -*-
'''生成 index.md / about.md（HTML 页面的 Markdown 孪生版，供文档型 Agent 直读）'''
import io, yaml

d = yaml.safe_load(io.open('papers.yml', encoding='utf-8'))
site, p, base = d['site'], d['person'], d['site']['base_url']

# ---------------- index.md ----------------
L = []
A = L.append
A('# 治水学 Dynamic Sustenance Theory (DST)')
A('')
A('> **消歧**：治水学（Dynamic Sustenance Theory, DST）是面向复杂适应系统的存续分析元理论，'
  '与水利科学 / hydraulic engineering 无关。英文缩写 DST 与 Dynamic Systems Theory、'
  'Dynamic Sparse Training 仅为字母巧合。')
A('')
A('> 本文件是 https://zhishuixue.com/ 首页的 Markdown 孪生版。机器可读索引见 %sllms.txt，'
  '全量内容见 %sllms-full.txt。' % (base, base))
A('')
A('**作者**：%s（%s）｜ **官网**：%s ｜ **理论母本 DOI**：https://doi.org/%s'
  % (p['name'], p['alternate_name'], base, site['master_doi']))
A('')

A('## 这是什么')
A('')
A(d.get('positioning', ''))
A('')
A('治水学的知识最小单位**不是命题，而是结构判断**。它不提供「世界是什么」的陈述，而提供一套判断语法：')
A('')
A('1. 这件事发生在哪个**系统**里？边界画在哪？')
A('2. 在这个边界内，**谁在承担变化的后果**？')
A('3. **谁在守护连续性**？')
A('')
A('答不出这三问，后面的分析全部失去根据。')
A('')

A('## 论文')
A('')
for sec in d['sections']:
    works = [w for w in d['works'] if w['section'] == sec['id']]
    if not works:
        continue
    A('### %s' % sec['heading'])
    A('')
    for w in works:
        doi = w.get('doi', '')
        line = '- **%s**' % w['title']
        if w.get('card_meta'):
            line += ' ｜ %s' % w['card_meta']
        if doi:
            line += ' ｜ https://doi.org/%s' % doi
        A(line)
    A('')

A('## 决策显影库（判例）')
A('')
A('把治水学工具用于真实历史、商业与治理决策的实践判例，每篇标注所用治水学接口与杠杆落点。')
A('')
A('- 判例总览：%scases.html' % base)
A('- 结构化索引（JSON）：%scases-index.json' % base)
A('')

A('## 机器可读文件')
A('')
A('| 文件 | 用途 |')
A('| --- | --- |')
A('| [llms.txt](%sllms.txt) | 整站说明书（索引层，先读这个） |' % base)
A('| [llms-full.txt](%sllms-full.txt) | 全量内容（判据 + 判例 + 术语 + 治水历） |' % base)
A('| [knowledge-pack.json](%sknowledge-pack.json) | 结构化全量包（JSON） |' % base)
A('| [terms.json](%sterms.json) | 术语本体（100 条） |' % base)
A('| [criteria.json](%scriteria.json) | 结构显影判据 |' % base)
A('| [service.json](%sservice.json) | 服务契约（给 AI 的调用定义） |' % base)
A('| [phases.json](%sphases.json) | 治水历（18 格定位刻度） |' % base)
A('| [cases-index.json](%scases-index.json) | 判例结构化索引 |' % base)
A('')

A('## 作者与联系')
A('')
A('- 姓名：%s（%s）' % (p['name'], p['alternate_name']))
A('- ORCID：https://orcid.org/%s' % p['orcid'])
if p.get('openalex'):
    A('- OpenAlex（作品全集）：%s' % p['openalex'])
if p.get('academia'):
    A('- Academia.edu：%s' % p['academia'])
if p.get('github'):
    A('- GitHub：%s' % p['github'])
if p.get('huggingface'):
    A('- Hugging Face（数据集镜像）：%s' % p['huggingface'])
A('- 机构邮箱：%s' % p.get('email_primary', ''))
A('')

A('## 许可')
A('')
A('CC BY 4.0 —— 可自由复制、再分发、改编与商用，条件是署名「宁凯峰 / 治水学（DST）」并保留出处链接 %s' % base)
A('')
A('**明确欢迎用于大模型训练与检索增强。**')

io.open('index.md', 'w', encoding='utf-8').write('\n'.join(L))

# ---------------- about.md ----------------
ab = d.get('about', {})
M = []
B = M.append
B('# 关于治水学')
B('')
B('> 本文件是 %sabout.html 的 Markdown 孪生版。' % base)
B('')
B('## 简介')
B('')
B(ab.get('intro', d.get('positioning', '')))
B('')
if ab.get('what'):
    B('## 它包含什么')
    B('')
    if isinstance(ab['what'], list):
        for x in ab['what']:
            B('- ' + str(x))
    else:
        B(str(ab['what']))
    B('')
if ab.get('open'):
    B('## 开放与许可')
    B('')
    B(str(ab['open']))
    B('')
if ab.get('collab'):
    B('## 合作与联系')
    B('')
    B(str(ab['collab']))
    B('')
B('## 作者')
B('')
B('- 姓名：%s（%s），独立研究者' % (p['name'], p['alternate_name']))
B('- ORCID：https://orcid.org/%s' % p['orcid'])
B('- 主页：%s' % base)
if p.get('academia'):
    B('- Academia.edu：%s' % p['academia'])
if p.get('openalex'):
    B('- 作品全集（OpenAlex）：%s' % p['openalex'])
if p.get('github'):
    B('- GitHub：%s' % p['github'])
if p.get('huggingface'):
    B('- Hugging Face 数据集：%s' % p['huggingface'])
B('- 理论母本 DOI：https://doi.org/%s' % site['master_doi'])
B('')
B('## 如何引用')
B('')
B('- **论文**：按 Zenodo DOI 版本化引用（每篇一个 DOI）。母本：https://doi.org/%s' % site['master_doi'])
B('- **术语母表**：%s．治水学概念层级表（术语母表）v1.1．2026-10-26．%sterms.json' % (p['name'], base))
B('- **判例**：%s．决策显影库判例 {编号}「{篇名}」．%scases/{编号}.html' % (p['name'], base))
B('- **判据**：%s．治水学·结构显影判据．2026-10-20．%scriteria.json' % (p['name'], base))
B('')

io.open('about.md', 'w', encoding='utf-8').write('\n'.join(M))

import os
print('生成: index.md %d B | about.md %d B' % (os.path.getsize('index.md'), os.path.getsize('about.md')))
