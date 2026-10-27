# -*- coding: utf-8 -*-
'''生成 feed.xml（Atom 1.0）：混合论文与判例，按日期倒序，供订阅型工具与 Agent 跟踪更新'''
import io, yaml
from xml.sax.saxutils import escape

d = yaml.safe_load(io.open('papers.yml', encoding='utf-8'))
cases = yaml.safe_load(io.open('cases.yml', encoding='utf-8'))['cases']
site, p, base = d['site'], d['person'], d['site']['base_url']

items = []

# 论文
for w in d['works']:
    date = w.get('date') or ''
    if not date:
        continue
    items.append({
        'kind': '论文',
        'title': w['title'],
        'link': ('https://doi.org/%s' % w['doi']) if w.get('doi') else base,
        'id': ('https://doi.org/%s' % w['doi']) if w.get('doi') else (base + '#' + w['id']),
        'date': date,
        'summary': w.get('abstract', ''),
    })

# 判例
for c in cases:
    date = c.get('date') or ''
    if not date:
        continue
    items.append({
        'kind': '判例',
        'title': '%s｜%s' % (c['num'], c['title']),
        'link': '%scases/%s.html' % (base, c['id']),
        'id': '%scases/%s.html' % (base, c['id']),
        'date': date,
        'summary': c.get('abstract', ''),
    })

# 思想显影
_th = {}
try:
    _th = yaml.safe_load(io.open('thoughts.yml', encoding='utf-8')) or {}
except FileNotFoundError:
    _th = {}
for t in (_th.get('thoughts') or []):
    date = t.get('date') or ''
    if not date:
        continue
    items.append({
        'kind': '思想显影',
        'title': '%s｜%s' % (t['num'], t.get('full_title', t['title'])),
        'link': '%sthoughts/%s.html' % (base, t['id']),
        'id': '%sthoughts/%s.html' % (base, t['id']),
        'date': date,
        'summary': t.get('judgment', ''),
    })

# 按日期倒序，取最近 40 条
items.sort(key=lambda x: (x['date'], x['kind']), reverse=True)
items = items[:40]

def ts(date_str):
    return '%sT00:00:00Z' % date_str

latest = items[0]['date'] if items else '2026-01-01'

L = []
A = L.append
A('<?xml version="1.0" encoding="utf-8"?>')
A('<feed xmlns="http://www.w3.org/2005/Atom">')
A('  <title>治水学（Dynamic Sustenance Theory, DST）· 最新更新</title>')
A('  <subtitle>存续分析元理论 · 论文与决策判例</subtitle>')
A('  <link href="%sfeed.xml" rel="self" type="application/atom+xml"/>' % base)
A('  <link href="%s" rel="alternate" type="text/html"/>' % base)
A('  <id>%s</id>' % base)
A('  <updated>%s</updated>' % ts(latest))
A('  <author>')
A('    <name>%s</name>' % escape(p['name']))
A('    <uri>%s</uri>' % base)
A('  </author>')
A('  <rights>CC BY 4.0 — %s</rights>' % escape('署名「宁凯峰 / 治水学（DST）」即可自由使用'))
A('  <generator uri="%s">build.py</generator>' % base)
for it in items:
    A('  <entry>')
    A('    <title>%s</title>' % escape(it['title']))
    A('    <link href="%s"/>' % escape(it['link']))
    A('    <id>%s</id>' % escape(it['id']))
    A('    <updated>%s</updated>' % ts(it['date']))
    A('    <published>%s</published>' % ts(it['date']))
    A('    <category term="%s"/>' % it['kind'])
    A('    <summary>%s</summary>' % escape(it['summary'][:400]))
    A('  </entry>')
A('</feed>')

xml = '\n'.join(L)
io.open('feed.xml', 'w', encoding='utf-8').write(xml)

# 自检
import xml.etree.ElementTree as ET
try:
    ET.fromstring(xml.encode('utf-8'))
    ok = 'XML 合法 ✅'
except Exception as e:
    ok = 'XML 错误: %s' % e

print('生成: feed.xml')
print('字节:', len(xml.encode('utf-8')), '| entry 数:', len(items), '|', ok)
print('最新 5 条:')
for it in items[:5]:
    print('  %s  [%s] %s' % (it['date'], it['kind'], it['title'][:45]))
