#!/usr/bin/env python3
"""生成 dst-ontology.json —— 治水学诊断本体（v0.1）

铁律：每一条概念/关系/取值/判据都来自知识库已有文档，逐条标注 source，
不虚拟创造。三条权威源：
  S1 = terms.json（术语母表 100 条，官网已发布）
  S2 = 《复杂系统诊断的判据 v1.1》（AI治理库·标本库）
  S3 = 《标本库·领域对接口径 v1.2》（AI治理库·标本库）
"""
import json, datetime

NOW = datetime.datetime.now().strftime("%Y-%m-%d")
BASE = "https://zhishuixue.com"

S1 = "terms.json（术语母表，100 条）"
S2 = "《复杂系统诊断的判据 v1.1》"
S3 = "《标本库·领域对接口径 v1.2》"

sources = [
    {"id": "terms", "name": "terms.json", "full": S1,
     "url": BASE + "/terms.json", "role": "概念定义（术语层权威）"},
    {"id": "criteria", "name": "复杂系统诊断的判据 v1.1", "full": S2,
     "url": BASE + "/specimens.html", "role": "判定规则（五步判据与取值）"},
    {"id": "interface", "name": "标本库·领域对接口径 v1.2", "full": S3,
     "url": BASE + "/specimens.html", "role": "逻辑位置与承载物的分野、防降格铁律"},
]

# ---------------- entities（概念） ----------------
entities = [
    {"id": "boundary", "name": "边界", "en": "Boundary",
     "definition": "先划边界。边界决定一切——边界画在哪，决定什么是系统内／系统外／压力源，也决定三种动能、三种操作的具体承载物。换一个边界，整套显影全变。",
     "note": "结构层（语法层）只有一个「边界」问题，没有「存续单位」——存续单位是实体概念、属于存在域，只出现在承载物层或工具层。",
     "source": S3 + " §〇"},
    {"id": "sustenance", "name": "存续", "en": "Sustenance",
     "definition": "存在在可观测层面的唯一形式：系统通过持续对抗失序压力以维持自身运作完整性。",
     "termId": "DST-B-01", "termUrl": "https://zhishuixue.com/glossary.html#sustenance", "source": S1},
    {"id": "ti", "name": "体（动力-规则协同结构）", "en": "Ti",
     "definition": "动力-规则协同的内在结构（不是动力层）；由动力层（三浪）与规则层（三元）协同构成。",
     "termId": "DST-B-07", "termUrl": "https://zhishuixue.com/glossary.html#ti", "source": S1},
    {"id": "force-generation", "name": "生成动能（突破性动能）", "en": "Breakthrough Force",
     "definition": "能改变——系统产生改变的能力来源。",
     "note": "三动能之一，不可与他者互替。「技术」只是它在文明尺度最常见的经验承载物（隐喻名，非定义）。",
     "source": S3 + " §一"},
    {"id": "force-maintenance", "name": "维持动能（稳定性动能）", "en": "Stability Force",
     "definition": "能持续——系统维持持续输出的能力来源。",
     "note": "三动能之一，不可与他者互替。「制度」只是隐喻名，非定义。",
     "source": S3 + " §一"},
    {"id": "force-direction", "name": "导向动能（方向性动能）", "en": "Directional Force",
     "definition": "能定向——系统定向的能力来源。",
     "note": "三动能之一，不可与他者互替。「思想」只是隐喻名，非定义。",
     "source": S3 + " §一"},
    {"id": "op-source", "name": "源头改造（疏浚）", "en": "Source Transformation (Dredging)",
     "definition": "规则引导动力去改造、转化、消除压力源；作用对象是压力的生成源。",
     "termId": "DST-D-02", "termUrl": "https://zhishuixue.com/glossary.html#dredging", "source": S1},
    {"id": "op-boundary", "name": "底线守护（方舟）", "en": "Boundary Safeguarding (Arking)",
     "definition": "规则引导动力去守护底线、建立防御、维持核心结构稳定；作用对象是系统边界。",
     "termId": "DST-D-03", "termUrl": "https://zhishuixue.com/glossary.html#arking", "source": S1},
    {"id": "op-consensus", "name": "共识凝聚（祭祀）", "en": "Consensus Cohesion (Sacrificing)",
     "definition": "规则引导动力去凝聚共识、校准方向、协调集体行动；作用对象是主体间关系。",
     "termId": "DST-D-04", "termUrl": "https://zhishuixue.com/glossary.html#sacrificing", "source": S1},
    {"id": "state", "name": "状态（四态）", "en": "State",
     "definition": "系统能否维持自身。由「约束可调性 × 状态生成能力」两维度组合出四个互斥且穷尽态。落点是动态张力曲线在当下的位置标注，不是封死的静态标签。",
     "source": S2 + " §4.1"},
    {"id": "constraint-mutability", "name": "约束可调性", "en": "Constraint Mutability",
     "definition": "约束本身是否还可调（可调／固化），是状态诊断的第一维度。",
     "source": S2 + " §4.1"},
    {"id": "state-generation", "name": "状态生成能力", "en": "State Generation",
     "definition": "系统能否正常生成核心状态，以「产出能不能成活」为准（不是「有没有在动」）。",
     "note": "「强／弱」是状态生成能力（系统能否维持自身核心状态）的强弱，不是三动能「生成（突破性动能）」的强弱——两者不可混。",
     "source": S2 + " §4.1"},
    {"id": "tempo-mismatch", "name": "节奏失配", "en": "Tempo-Mismatch",
     "definition": "维持能力与干预节奏是否匹配。三个前置预警准则任一触发即报警、不加权。",
     "source": S2 + " §4.2"},
    {"id": "stress-gap", "name": "失序压力差（适应能力-压力差）", "en": "Adaptive Capacity–Stress Gap",
     "definition": "维持能力与压力的差距是否在扩大。判「差距趋势」而非「压力绝对值」。",
     "source": S2 + " §4.3"},
    {"id": "leverage-point", "name": "杠杆点", "en": "Leverage Point",
     "definition": "哪里调整最能恢复维持能力。给定位原则而非具体位置：优先高流量且少数行动者单边可变的约束；次寻环间接口；避免针对状态本身（状态是果、约束是因）。",
     "source": S2 + " §4.4"},
    {"id": "intervention-channel", "name": "干预通道", "en": "Intervention Channel",
     "definition": "由约束可变性三分类决定的干预通道：Adjustable→repair；Solidified→external intervention／reconfiguration；Broken→aftermath management。",
     "source": S2 + " §4.5"},
    {"id": "layered-asynchrony", "name": "分层异步", "en": "Layered Asynchrony",
     "definition": "动力层与规则层之间结构性的非同步耦合：传导时间差恒大于零且不可消除，使动态适配无法完全闭合。",
     "termId": "DST-E-01", "termUrl": "https://zhishuixue.com/glossary.html#layered-asynchrony", "source": S1},
    {"id": "response-gap", "name": "响应缺口", "en": "Response Gap",
     "definition": "规则层完成有效响应所需周期，超过系统承受而不发生核心功能损害的时间窗口的部分。响应缺口天然非负——超过窗口才有缺口。",
     "termId": "DST-E-02", "termUrl": "https://zhishuixue.com/glossary.html#response-gap", "source": S1},
]

# ---------------- relations（关系） ----------------
relations = [
    {"id": "r-state", "subject": "state", "predicate": "determinedBy",
     "object": ["constraint-mutability", "state-generation"],
     "description": "状态由「约束可调性 × 状态生成能力」两维度组合推出，缺一不可。",
     "source": S2 + " §4.1"},
    {"id": "r-stage", "subject": "locked-in-stage", "predicate": "determinedBy",
     "object": "constraint-mutability",
     "description": "锁定态分期（早期／中后期）由「约束可调性」的深浅划：早期＝约束尚可调（对应修复通道）；中后期＝约束已固化（对应外部介入通道）。状态生成能力的强弱作辅助标定。",
     "source": S2 + " §4.1"},
    {"id": "r-tempo", "subject": "tempo-mismatch", "predicate": "hasCriterion",
     "object": ["transmission-delay", "feedback-time-constant", "response-attenuation"],
     "description": "节奏失配的三个前置预警准则，任一触发即报警、不加权，不作加权评分。",
     "source": S2 + " §4.2"},
    {"id": "r-leverage", "subject": "leverage-point", "predicate": "locatedBy",
     "object": "location-principle",
     "description": "杠杆点按定位原则找，不按显眼程度找；显眼 ≠ 杠杆。",
     "source": S2 + " §4.4"},
    {"id": "r-channel", "subject": "constraint-mutability", "predicate": "mapsTo",
     "object": "intervention-channel",
     "description": "约束可变性三分类决定干预通道：Adjustable→repair；Solidified→external intervention；Broken→aftermath management。",
     "source": S2 + " §4.5"},
    {"id": "r-op-source", "subject": "op-source", "predicate": "actsOn",
     "object": "pressure-source",
     "description": "源头改造的作用对象是压力的生成源。",
     "source": S1},
    {"id": "r-op-boundary", "subject": "op-boundary", "predicate": "actsOn",
     "object": "system-boundary",
     "description": "底线守护的作用对象是系统边界。",
     "source": S1},
    {"id": "r-op-consensus", "subject": "op-consensus", "predicate": "actsOn",
     "object": "intersubjective-relation",
     "description": "共识凝聚的作用对象是主体间关系。",
     "source": S1},
    {"id": "r-response-gap", "subject": "response-gap", "predicate": "isA",
     "object": "layered-asynchrony",
     "description": "响应缺口是分层异步的表现（术语母表中其上位即分层异步）。",
     "source": S1},
    {"id": "r-op-form", "subject": ["op-source", "op-boundary", "op-consensus"],
     "predicate": "definedAs",
     "object": "rule-guides-force",
     "description": "三种操作统一定义为「规则引导动力去作用于对象」——操作是规则层对动力层的引导动作，不是动力或承载物本身。",
     "source": S3 + " §二"},
]

# ---------------- valueDomains（取值范围） ----------------
value_domains = [
    {"id": "state", "name": "状态", "source": S2 + " §4.1", "values": [
        {"value": "adaptive", "label": "适应态", "en": "Adaptive",
         "condition": "约束可调 + 可生成"},
        {"value": "crisis-restructuring", "label": "危机重构窗口", "en": "Crisis-restructuring window",
         "condition": "约束可调 + 断裂"},
        {"value": "locked-in", "label": "锁定态", "en": "Locked-in",
         "condition": "固化 + 可生成"},
        {"value": "collapse", "label": "崩溃态", "en": "Collapse",
         "condition": "固化 + 断裂"},
    ]},
    {"id": "state-generation", "name": "状态生成能力（三档）", "source": S2 + " §4.1", "values": [
        {"value": "generating-strong", "label": "可生成（强）", "condition": "正常生成核心状态，产出能成活（规则真的生效、真的运转）"},
        {"value": "generating-weak", "label": "可生成（弱）", "condition": "还在生成，但产出落不了地、活不了（还在动、但产出不成活）"},
        {"value": "broken", "label": "断裂", "condition": "不能再生成核心状态（动作停止）→ collapse"},
    ]},
    {"id": "constraint-mutability", "name": "约束可变性（三分类）", "source": S2 + " §4.5", "values": [
        {"value": "adjustable", "label": "可调", "en": "Adjustable", "condition": "有弹性可调整 → repair"},
        {"value": "solidified", "label": "固化", "en": "Solidified", "condition": "制度化锁入、单点无效 → external intervention / reconfiguration"},
        {"value": "broken", "label": "失效", "en": "Broken", "condition": "约束失效、系统崩 → aftermath management"},
    ]},
    {"id": "tempo-criterion", "name": "节奏失配三准则", "source": S2 + " §4.2", "values": [
        {"value": "transmission-delay", "label": "传输延迟单调增长", "condition": "干预发出到系统响应延迟随次数递增"},
        {"value": "feedback-time-constant", "label": "反馈环时间常数比跨数量级", "condition": "状态生成环与治理干预环时间常数差一个数量级"},
        {"value": "response-attenuation", "label": "响应衰减", "condition": "同干预边际效应递减"},
    ]},
]

# ---------------- constraints（判据与约束） ----------------
constraints = [
    {"id": "c-anti-degradation", "name": "防降格铁律",
     "rule": "填出「技术、制度、文化」三个并列板块即为误翻译，因缺动力与规则相互拉扯，推倒重填。三种动能与三种操作是「逻辑位置」，不是「技术／制度／思想」这些承载物。",
     "source": S3 + " §三（引《结构显影的判据》5.3）"},
    {"id": "c-logical-position", "name": "逻辑位置 vs 承载物",
     "rule": "承载物和落点都由「分析边界」决定——特定边界决定特定承载物、特定落点；边界一移，承载物与落点全量重排。对外对接必须对接「逻辑位置」（能力），不能对接「承载物」（技术／制度／思想）。",
     "source": S3 + " §〇"},
    {"id": "c-no-fake", "name": "五项不提供",
     "rule": "不提供量化阈值／不提供直接答案／不替代承压主体判断／不提供对错评价／不提供跨尺度统一阈值。",
     "source": S2 + " §八"},
    {"id": "c-validity", "name": "可检验性四问",
     "rule": "判定链可追溯（落点由两维度组合推出）；T0 可证伪（留修正条件）；信息可得性诚实（不可得的明确标注）；干预四问可回滚（调哪条／方向幅度／如何验证／如何回滚齐全）。",
     "source": S2 + " §六"},
    {"id": "c-boundary-vs-unit", "name": "结构层只有边界，没有存续单位",
     "rule": "结构层（语法层）只有一个「边界」问题，没有「存续单位」——「存续单位」是实体概念、属于存在域，只出现在承载物层或工具层。标本结构层只写边界，不写存续单位。",
     "source": S3 + " §〇"},
]

ontology = {
    "schema": "dst-ontology/1.0",
    "title": "治水学诊断本体",
    "titleEn": "DST Diagnosis Ontology",
    "version": "v0.1",
    "generatedAt": NOW,
    "license": "CC BY 4.0",
    "maintainer": "宁凯峰（独立研究者）· ORCID 0009-0001-4414-6058",
    "source": BASE + "/ontology.json",
    "note": ("本本体把治水学诊断语法的核心概念、概念间关系、取值范围与判定约束显式化，"
             "供大模型与 Agent 理解「治水学的概念地图」。每一条都标注出处（terms.json／判据 v1.1／对接口径 v1.2），"
             "不虚构、不越界。本体只管结构，不替代判断——判断权始终在使用者。"),
    "sources": sources,
    "entities": entities,
    "relations": relations,
    "valueDomains": value_domains,
    "constraints": constraints,
}

OUT = "/sandbox/workspace/repo/dst-ontology.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(ontology, f, ensure_ascii=False, indent=2)
print("已写出", OUT, "(%d B)" % __import__("os").path.getsize(OUT))
print("entities:", len(entities), "| relations:", len(relations),
      "| valueDomains:", len(value_domains), "| constraints:", len(constraints))
