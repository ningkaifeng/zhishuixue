#!/usr/bin/env python3
"""生成 dst-diagnosis.schema.json —— 治水学诊断接口契约（v0.1）

铁律：所有字段与取值都取自知识库库存，逐项标注出处：
  S2 = 《复杂系统诊断的判据 v1.1》（五项判定的取值与判据）
  S3 = 《标本库·领域对接口径 v1.2》（三动能/三操作/逻辑位置）
  S4 = 标本 No.01 / No.02 正文（11 字段与规范层四问）
  S5 = cases.yml 49 篇判例（六要素的实际字段）
关键约束：五项判定（系统诊断）与六要素（事件显影）是两把尺，不可混用
（依据：判据 v1.1 §七「诊断的尺不是判例的尺」）。
"""
import json, datetime, os

NOW = datetime.datetime.now().strftime("%Y-%m-%d")
OUT = "/sandbox/workspace/repo/dst-diagnosis.schema.json"

S2 = "《复杂系统诊断的判据 v1.1》"
S3 = "《标本库·领域对接口径 v1.2》"
S4 = "标本 No.01/No.02 正文"
S5 = "cases.yml（49 篇判例的六要素字段）"
S6 = "《通用结构语法·诊断工作表 v2.0》"

FIVE_STATES = ["adaptive", "crisis-restructuring", "evasive-lock-in", "locked-in", "collapse"]
GEN_LEVELS = ["generating-strong", "generating-weak", "broken"]
MUTABILITY = ["adjustable", "evasive", "solidified", "broken"]

system_input = {
    "type": "object",
    "title": "系统诊断 · 输入",
    "description": ("给一个仍在运行的真实系统：先划边界，再提交可得的公开信息。" + S4),
    "properties": {
        "system": {"type": "string", "description": "系统名称，例如「全球 AI 治理」"},
        "boundary": {"type": "string",
                     "description": ("分析边界，须含时间窗。边界决定什么是系统内/系统外/压力源，也决定三种动能与三种操作的承载物；边界一移，整套显影全变。（" + S3 + " §〇）")},
        "infoAvailable": {"type": "array", "items": {"type": "string"},
                          "description": "事前可得的公开信息（法规文本、发布记录、统计数据等）"},
        "infoUnavailable": {"type": "array", "items": {"type": "string"},
                            "description": "事前不可得的信息（内部决策、真实让步空间等）——必须诚实标注，信息不足属「诊断条件未满足」，不是第五态"},
        "observations": {"type": "array", "items": {"type": "string"},
                         "description": "观察到的现象事实，供诊断使用"},
        "asOf": {"type": "string", "description": "T0 判断时点（ISO 日期），用于事后核验"},
    },
    "required": ["system", "boundary"],
}

system_output = {
    "type": "object",
    "title": "系统诊断 · 输出（五项判定 + 干预四问）",
    "description": ("产出结构，不产出结论：系统处于什么态、该往哪调、怎么验证。（" + S2 + " §一）"),
    "properties": {
        "boundary": {"type": "string", "description": "复述分析边界"},
        "judgment": {"type": "string",
                     "description": "一句话结构判断，须可独立引用、不依赖专名（换掉全部专名后仍成立）。"},
        "stateDiagnosis": {
            "type": "object",
            "description": ("第 2 步 · 状态诊断：约束可调性 × 状态生成能力 → 五态。（" + S2 + " §4.1；" + S6 + " 工作表 v2.0）"),
            "properties": {
                "constraintMutability": {"enum": MUTABILITY,
                                         "description": ("约束可调性四分类：可调 adjustable（能改且改得起）/ 讳锁 evasive（形式可改，一改就把损失摆上台面，于是无人先动）/ 固化 solidified（改不动）/ 破裂 broken（已断）。讳锁 ≠ 固化：两者药方相反，固化的出路是外部介入，讳锁的出路是先把代价摆到桌面（disclosure-first）。（" + S6 + " 工作表 v2.0）")},
                "stateGeneration": {"enum": GEN_LEVELS,
                                    "description": "状态生成能力三档：可生成（强）/ 可生成（弱，产出落不了地）/ 断裂。注意：这是「系统能否生成核心状态」，不是三动能之「生成（突破性动能）」的强弱。（" + S2 + " §4.1）"},
                "state": {"enum": FIVE_STATES,
                          "description": ("五态：adaptive 适应态（可调+可生成）/ crisis-restructuring 危机重构窗口（可调+断裂）/ evasive-lock-in 讳锁态（讳锁+可生成：约束形式可改，动用即暴露损失，于是无人先动）/ locked-in 锁定态（固化+可生成）/ collapse 崩溃态（固化+断裂）。注意：讳锁与断裂不组合——产出一旦断裂，「瞒得住」的前提即不成立。")},
                "stage": {"enum": ["early", "mid-late"],
                          "description": "仅 locked-in 与 evasive-lock-in 时适用：早期＝约束尚可调（修复通道，讳锁态则为 disclosure-first）；中后期＝约束已固化（外部介入通道）。由约束可调性深浅划，生成能力强弱作辅助标定。（" + S2 + " §4.1）"},
            },
            "required": ["constraintMutability", "stateGeneration", "state"],
        },
        "tempoMismatch": {
            "type": "object",
            "description": "第 3 步 · 节奏失配：三准则任一触发即报警，不加权。（" + S2 + " §4.2）",
            "properties": {
                "triggeredCriteria": {
                    "type": "array",
                    "items": {"enum": ["transmission-delay", "feedback-time-constant", "response-attenuation"]},
                    "description": "触发的准则：传输延迟单调增长 / 反馈环时间常数比跨数量级 / 响应衰减（同干预边际效应递减）",
                },
                "note": {"type": "string", "description": "趋势描述（须用变化方向与速率差，不能用静态存量词）"},
            },
        },
        "stressGap": {
            "type": "object",
            "description": "第 4 步 · 适应能力—压力差：判差距趋势而非压力绝对值。（" + S2 + " §4.3）",
            "properties": {
                "widening": {"type": "boolean", "description": "差距是否在扩大（压力接近速度是否快于适应能力增长）"},
                "note": {"type": "string"},
            },
        },
        "operations": {
            "type": "object",
            "description": "三种操作当前状态：三者缺一即说明显影漏了。（" + S3 + " §二 ）",
            "properties": {
                "sourceTransformation": {"type": "string", "description": "源头改造（疏浚）：改造压力源本身——当前状态"},
                "boundarySafeguarding": {"type": "string", "description": "底线守护（方舟）：守住不可接受的边界——当前状态"},
                "consensusCohesion": {"type": "string", "description": "共识凝聚（祭祀）：把各方拉到同一张桌子——当前状态"},
            },
        },
        "leveragePoint": {
            "type": "object",
            "description": "第 5 步 · 杠杆点：给定位原则而非具体位置。（" + S2 + " §4.4）",
            "properties": {
                "location": {"type": "string", "description": "杠杆点位置（须满足：高流量 + 少数行动者单边可变；不是最显眼处）"},
                "rationale": {"type": "string", "description": "为什么是这里（对照定位原则）"},
            },
        },
        "constraintClassification": {"enum": MUTABILITY,
                                     "description": ("约束可变性四分类，决定干预通道：adjustable→repair；evasive→disclosure-first；solidified→external-intervention；broken→aftermath-management。（" + S6 + " 工作表 v2.0；" + S2 + " §4.5）")},
        "interventionChannel": {"enum": ["repair", "disclosure-first", "external-intervention", "aftermath-management"],
                                "description": "干预通道：可调→repair（修复）；讳锁→disclosure-first（先披露代价，后调整）；固化→external-intervention（外部介入/重构）；破裂→aftermath-management（事后管理）"},
        "interventionFourQuestions": {
            "type": "object",
            "description": "干预四问，四问齐全才可回滚。（" + S4 + "；" + S2 + " §六）",
            "properties": {
                "whichConstraint": {"type": "string", "description": "① 调哪条约束"},
                "direction": {"type": "string", "description": "② 方向与幅度"},
                "verification": {"type": "string", "description": "③ 如何验证调对了"},
                "rollback": {"type": "string", "description": "④ 如何回滚（含：设限后撤回受政治刚性约束、往往难退）"},
            },
            "required": ["whichConstraint", "direction", "verification", "rollback"],
        },
        "normativeLayer": {
            "type": "object",
            "description": ("规范层四问：任一约束必须同时回答四问，答不全就只是存在域的标语、不是存续域的约束。（" + S4 + "）"),
            "properties": {
                "authorization": {"type": "string", "description": "① 谁授权（国内法授权 / 国际协调 / 多边共识）"},
                "liability": {"type": "string", "description": "② 谁赔（设条件者是否被问责、评估是否独立）"},
                "exit": {"type": "string", "description": "③ 怎么退（条件错误时有无纠偏与救济通道）"},
                "fallback": {"type": "string", "description": "④ 退不动时系统怎么续命（约束撤不回时靠什么兜底）"},
            },
        },
        "refutation": {
            "type": "object",
            "description": "双向修正条件：什么情况说明这个判断错了。（" + S4 + "；" + S2 + " §六「T0 可证伪」）",
            "properties": {
                "ifWorse": {"type": "string", "description": "恶化方向：落点修正为什么态"},
                "ifBetter": {"type": "string", "description": "好转方向：落点修正为什么态"},
            },
            "required": ["ifWorse", "ifBetter"],
        },
        "infoAvailability": {
            "type": "object",
            "description": "信息可得性诚实标注：不可得的明确标了，没拿事后信息假装事前可得。（" + S2 + " §六）",
            "properties": {
                "available": {"type": "array", "items": {"type": "string"}},
                "unavailable": {"type": "array", "items": {"type": "string"}},
            },
        },
        "validity": {
            "type": "object",
            "description": "可检验性四问，全为 true 才算立住。（" + S2 + " §六）",
            "properties": {
                "chainTraceable": {"type": "boolean", "description": "判定链可追溯（落点由两维度组合推出，不是拍脑袋）"},
                "falsifiable": {"type": "boolean", "description": "T0 可证伪（留了双向修正条件）"},
                "infoHonest": {"type": "boolean", "description": "信息可得性诚实"},
                "fourQuestionsComplete": {"type": "boolean", "description": "干预四问齐全可回滚"},
            },
        },
        "judgeable": {
            "type": "boolean",
            "description": ("本次输入是否足以做出判定。false 时只需填 boundary 与 unjudgeableReason，"
                            "其余判定字段留空——这是给模型的退出通道，防止信息不足时硬编一份看似完整的诊断。"
                            "（依据：《复杂系统诊断的判据 v1.1》 §八「五项不提供」；标本 T0 的「信息可得性诚实标注」）"),
        },
        "unjudgeableReason": {
            "type": "array",
            "items": {"enum": ["boundary-unconfirmed", "bearer-unconfirmed",
                               "info-unavailable", "out-of-scale"]},
            "description": ("判不出的原因（judgeable=false 时必填，可多选）：边界未由承压者确认 / "
                            "承压者未点名 / 关键信息事前不可得 / 超出该尺度的适用范围。"
                            "（依据：《结构显影的判据》 §二 第零步承压位置检验——承压位置不能由观察者单方面锁定）"),
        },
    },
    "required": ["boundary", "judgment", "judgeable"],
    "allOf": [
        {"if": {"properties": {"judgeable": {"const": True}}, "required": ["judgeable"]},
         "then": {"required": ["stateDiagnosis", "leveragePoint", "refutation"]}},
        {"if": {"properties": {"judgeable": {"const": False}}, "required": ["judgeable"]},
         "then": {"required": ["unjudgeableReason"],
                  "not": {"anyOf": [{"required": ["stateDiagnosis"]},
                                    {"required": ["leveragePoint"]},
                                    {"required": ["refutation"]}]}}},
    ],
}

event_input = {
    "type": "object",
    "title": "事件显影 · 输入",
    "description": ("给一个已发生的决策事件：情境、人物、约束、结果。" + S5),
    "properties": {
        "event": {"type": "string", "description": "事件名称"},
        "scene": {"type": "string", "description": "场景归类（如：组织治理、基层治理、企业管理、宏观治理）"},
        "actors": {"type": "array", "items": {"type": "string"}, "description": "承压者/决策者（须点名，并说明其「最怕失去什么」）"},
        "sourceMaterial": {"type": "string", "description": "素材来源（史料/访谈/公开报道），用于核验"},
        "asOf": {"type": "string", "description": "记录日期（ISO）"},
    },
    "required": ["event", "scene"],
}

event_output = {
    "type": "object",
    "title": "事件显影 · 输出（六要素）",
    "description": ("六要素是事件尺的骨架：只显影结构，不评价对错。（" + S5 + "）"),
    "properties": {
        "situation": {"type": "string",
                      "description": "情境：第一层·系统边界（这是哪个系统、边界在哪）/ 第二层·威胁识别（最大威胁是什么）/ 第三层·现状约束（此刻受什么限制）"},
        "signal": {"type": "string",
                   "description": "信号：当事人当时能观察到、且能据此判断的可见信息。须分主判据（裁决）与辅判据（提示），并写清「看到什么算成立」"},
        "exclusion": {"type": "string",
                      "description": "排除：哪些做法被排除、为什么排除（硬字段）。每条须带「何时不成立」，否则排除是假的"},
        "action": {"type": "string",
                   "description": "行动：当事人实际做了什么，须是【结构动作】（可被拍下来的具体动作），不是形容词"},
        "expectation": {"type": "string",
                        "description": "预期：分两层——【当时能判断的】（决定该不该做）与【事后才能验证的】（决定能不能成），防事后归因"},
        "correction": {"type": "string",
                       "description": "修正：硬边界——什么情况说明这个判断要改"},
        "counterExample": {"type": "string",
                           "description": "同结构对照（可选但推荐）：同结构、不同承载、不同结局的反例，防幸存者偏差；无则明写「未检索到，存在幸存者偏差风险」"},
        "interface": {"type": "string",
                      "description": "治水学接口，格式「族·细分（通俗解释）」：族取疏浚/方舟/祭祀/信号层/结构判断/响应失效各态/分层异步/动力调控/对象维"},
        "lever": {"type": "string", "description": "杠杆落点：这个动作真正作用在哪个结构位置"},
        "effect": {"type": "string", "description": "效果：结果如何（历史事件填史实结果）"},
        "reusableCondition": {"type": "string", "description": "可复用条件：什么情况下这套结构可迁移"},
        "nonApplicable": {"type": "string", "description": "不适用条件：什么情况下不成立"},
    },
    "required": ["situation", "signal", "exclusion", "action", "expectation", "correction"],
}

doc = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://zhishuixue.com/dst-diagnosis.schema.json",
    "title": "治水学诊断接口契约",
    "version": "v0.1",
    "generatedAt": NOW,
    "license": "CC BY 4.0",
    "maintainer": "宁凯峰（独立研究者）· ORCID 0009-0001-4414-6058",
    "description": ("把治水学的两把尺定义成可被 Agent 调用的输入/输出契约："
                    "①系统诊断（五项判定，面向「仍在运行的真实系统」）；"
                    "②事件显影（六要素，面向「已发生的决策事件」）。"
                    "每一条字段与取值都取自知识库库存，并标注出处。"),
    "x-separationRule": ("五项判定（系统诊断）与六要素（事件显影）是两把不同的尺，显影对象不同（系统/事件），"
                         "不可互相误评、不可混用同一个输出结构。依据：" + S2 + " §七「诊断的尺不是判例的尺」。"),
    "x-usageRules": [
        "诊断产出结构，不产出结论——判断权在使用者，本契约只保证结构透明、可证伪、可迭代。（" + S2 + " §一）",
        "不提供量化阈值／不提供直接答案／不替代承压主体判断／不提供对错评价／不提供跨尺度统一阈值。（" + S2 + " §八）",
        "三种动能与三种操作是「逻辑位置」，不是技术/制度/思想这些承载物；填出并列板块即为误翻译。（" + S3 + " §三）",
        "落点是动态张力曲线的当前位置标注，不是封死的静态标签。",
    ],
    "x-toolDefinitions": [
        {
            "name": "dst_system_diagnosis",
            "description": ("对仍在运行的真实系统做结构诊断（治水学五项判定）：划边界 → 状态诊断（约束可调性×状态生成能力→五态）"
                            "→ 节奏失配 → 压力差 → 杠杆点与干预四问。产出结构判断与双向证伪条件，不产出结论或建议。"
                            "适用：治理系统、行业格局、组织机制等「结局尚未发生」的系统。"),
            "input": {"$ref": "#/$defs/SystemDiagnosisInput"},
            "output": {"$ref": "#/$defs/SystemDiagnosisOutput"},
            "notes": "适用边界：必须是仍在运行、结局未知的系统；历史事件请用 dst_event_shadowing。",
        },
        {
            "name": "dst_event_shadowing",
            "description": ("对已发生的决策事件做结构显影（治水学六要素）：情境 → 信号 → 排除 → 行动 → 预期 → 修正，"
                            "并标注治水学接口与杠杆落点。只显影结构、不评价对错。"
                            "适用：历史判例、商业决策复盘、治理事件。"),
            "input": {"$ref": "#/$defs/EventShadowingInput"},
            "output": {"$ref": "#/$defs/EventShadowingOutput"},
            "notes": "适用边界：结局已知的事件；仍在运行的系统请用 dst_system_diagnosis。",
        },
    ],
    "$defs": {
        "SystemDiagnosisInput": system_input,
        "SystemDiagnosisOutput": system_output,
        "EventShadowingInput": event_input,
        "EventShadowingOutput": event_output,
    },
}


def _seal(node):
    """所有 object 封死 additionalProperties，防止两把尺的字段混进来"""
    if isinstance(node, dict):
        if node.get("type") == "object" and "additionalProperties" not in node:
            node["additionalProperties"] = False
        for v in node.values():
            _seal(v)
    elif isinstance(node, list):
        for x in node:
            _seal(x)


_seal(doc["$defs"])

doc["x-validationNote"] = ("本文件是「契约清单」，顶层不自带 type，不能直接用顶层校验实例。"
                           "校验时请取 $defs 中的子 schema："
                           '{"$schema": ..., "$ref": "#/$defs/SystemDiagnosisOutput", "$defs": <本文件 $defs>}。'
                           "所有 object 均已封死 additionalProperties，混入另一把尺的字段会被拒绝（依据：判据 v1.1 §七）。")


# ---------------- few-shot 示例（真实数据反推，不是编的） ----------------
EXAMPLES = [
    {
        "name": "example-1-normal-diagnosis",
        "note": ("真实案例：标本 No.01（全球 AI 治理，T0=2026-11-07）。"
                 "输入来自公开信息，输出为 T0 锁定的判断；本示例用于让 Agent 照抄结构，不代表对当下状态的重新判定。"),
        "tool": "dst_system_diagnosis",
        "input": {
            "system": "全球 AI 治理",
            "boundary": "全球 AI 治理（2024–2026）：以主要司法辖区的模型发布监管为系统内，以模型能力跃迁为压力源；不含各国国内产业政策。",
            "infoAvailable": [
                "EU AI Act 文本与实施时间表",
                "美国行政令与后续修订",
                "主要实验室模型发布记录与公开能力评测分数",
                "公开的监管咨询意见"
            ],
            "infoUnavailable": [
                "各国监管机关内部真实让步空间",
                "实验室与监管方的非公开沟通"
            ],
            "observations": [
                "EU AI Act 核心条款落地时间被推迟，未出现实质修订",
                "主要实验室的模型发布间隔缩短，能力评测分数持续抬升",
                "监管规则仍以事后追责为主，部署前条件尚未成文"
            ],
            "asOf": "2026-11-07"
        },
        "output": {
            "judgeable": True,
            "boundary": "全球 AI 治理（2024–2026）；系统内＝主要辖区的模型发布监管，压力源＝模型能力跃迁。",
            "judgment": "全球 AI 治理处于锁定态早期，规则持续追不上模型能力，可干预的杠杆点是模型发布节点——把约束从事后追责移到部署前条件，是目前唯一还能动的入口。",
            "stateDiagnosis": {
                "constraintMutability": "adjustable",
                "stateGeneration": "generating-strong",
                "state": "locked-in"
            },
            "tempoMismatch": {
                "triggeredCriteria": ["transmission-delay", "response-attenuation"],
                "note": "规则产出周期以年计、模型能力迭代以月计，差距在扩大而非收敛；同一类干预（追加披露要求）的边际效应在递减"
            },
            "stressGap": {
                "widening": True,
                "note": "压力（能力跃迁速度）快于适应能力（规则产出速度）"
            },
            "operations": {
                "sourceTransformation": "源头改造（疏浚）：未发生——监管仍作用于部署后的追责，未触及能力跃迁本身",
                "boundarySafeguarding": "底线守护（方舟）：部分存在——不可接受风险清单构成硬边界，但执行滞后",
                "consensusCohesion": "共识凝聚（祭祀）：弱——主要辖区之间无共同评估标准，方向无法收敛"
            },
            "leveragePoint": {
                "location": "模型发布许可（部署前条件）",
                "rationale": "满足高流量（每次发布都是规则与能力的交汇点）与少数行动者单边可变（少数实验室可自行调整发布门槛）；不是最显眼处——最显眼的是立法，但立法周期长"
            },
            "constraintClassification": "adjustable",
            "interventionChannel": "repair",
            "interventionFourQuestions": {
                "whichConstraint": "模型发布的准入条件（从「发布后追责」改为「部署前证明」）",
                "direction": "把条件从结果端移到部署前，幅度限于可验证的能力评测项",
                "verification": "以「部署前条件成文并被至少一个主要辖区采纳」为验证标志",
                "rollback": "条件设限后撤回受政治刚性约束——一旦成为法定要求，取消会被读作放松监管，须预留日落条款"
            },
            "normativeLayer": {
                "authorization": "国内法授权（各辖区立法），国际协调为辅",
                "liability": "设条件者需被问责，评估须独立于被评估方",
                "exit": "条件错误时有纠偏程序（复审与修订窗口）",
                "fallback": "约束撤不回时，以强制披露与事后追责兜底"
            },
            "refutation": {
                "ifWorse": "规则产出全面停止 → collapse（固化+断裂）；若崩溃逼出约束被迫松动 → crisis-restructuring window（可调+断裂）",
                "ifBetter": "核心条款执行顺利、重大事故触发快速立法、约束从固化重新变可调 → adaptive（适应态）"
            },
            "infoAvailability": {
                "available": ["法规文本与时间表", "公开的模型发布记录与评测分数"],
                "unavailable": ["监管机关内部让步空间", "非公开沟通"]
            },
            "validity": {
                "chainTraceable": True,
                "falsifiable": True,
                "infoHonest": True,
                "fourQuestionsComplete": True
            }
        }
    },
    {
        "name": "example-2-unjudgeable",
        "note": ("演示退出通道：边界未经承压者确认、关键信息事前不可得。"
                 "此时正确输出是「判不出」，不是硬填一份看似完整的诊断。"),
        "tool": "dst_system_diagnosis",
        "input": {
            "system": "某制造企业的供应链决策机制",
            "boundary": "该公司供应链决策（2025–2026）——边界尚未与该机制的承压者（采购负责人）确认",
            "infoAvailable": ["公开发布的招投标公告"],
            "infoUnavailable": ["内部审批权限划分", "供应商真实议价空间", "该机制的实际承压者身份"],
            "observations": ["2025 年两次更换主供应商，公告口径均称「综合评估」"],
            "asOf": "2026-11-19"
        },
        "output": {
            "judgeable": False,
            "unjudgeableReason": ["boundary-unconfirmed", "bearer-unconfirmed", "info-unavailable"],
            "boundary": "该公司供应链决策（2025–2026）；边界尚未由承压者确认，暂不作为判定依据。",
            "judgment": "本次不足以做出结构判断：边界未经承压者确认，且审批权限与议价空间事前不可得；强行判定会产出看似完整、实则空转的诊断。"
        }
    },
    {
        "name": "example-3-evasive-lock-in",
        "note": ("真实案例：工具包样例 No.03（AI 基础设施资本开支，2026 Q3 末）——"
                 "「讳锁 evasive-lock-in」就是从这一例跑出来的形态。本示例用于让 Agent 分辨："
                 "「所有人都说该改、但没人先动」不是固化。固化等外部介入，讳锁必须先把代价摆到桌面（disclosure-first）。"),
        "tool": "dst_system_diagnosis",
        "input": {
            "system": "AI 基础设施资本开支",
            "boundary": ("美国五大超大规模厂商 + neocloud 的 AI 资本开支与融资安排（2026 Q3 末）；"
                         "系统内＝资本开支决策与融资结构，压力源＝算力需求增速快于自有现金流（造血）。"),
            "infoAvailable": [
                "财报 capex 指引与季度经营现金流",
                "折旧政策与会计估计披露",
                "评级机构报告与杠杆率口径",
                "公开的债务与 SPV 发行文件"
            ],
            "infoUnavailable": [
                "SPV 真实杠杆（表外，不直接可见）",
                "「GPU 经济寿命约 3 年」并非行业共识，属独立估计",
                "收入／capex 口径存在争议（资本化范围不同）"
            ],
            "observations": [
                "资本开支增速反超经营现金流，缺口转向表外融资",
                "GPU 折旧年限仍按 5–6 年，独立估计的经济寿命约 3 年",
                "杠杆率与评级门槛逼近触发线",
                "公开场合都在说「折旧该改」，但无一家先动"
            ],
            "asOf": "2026-09-30"
        },
        "output": {
            "judgeable": True,
            "boundary": ("美国五大超大规模厂商 + neocloud 的 AI 资本开支与融资安排（2026 Q3 末）；"
                         "系统内＝capex 决策与融资结构，压力源＝算力需求增速快于自有现金流。"),
            "judgment": ("AI 基础设施资本开支处于讳锁态：折旧假设形式上可改（CFO 与审计师即可定），"
                         "但一改立刻在利润表与杠杆率上暴露损失，于是所有人都在说该改、没人先动——"
                         "出路不是直接调，而是先强制披露代价。"),
            "stateDiagnosis": {
                "constraintMutability": "evasive",
                "stateGeneration": "generating-strong",
                "state": "evasive-lock-in"
            },
            "tempoMismatch": {
                "triggeredCriteria": ["feedback-time-constant"],
                "note": ("方向与前两例相反：债务与融资工具期限以年计，GPU 经济寿命约 3 年——"
                         "是资本工具的期限追不上资产贬值速度，而非规则追不上技术。"
                         "同一个「节奏失配」，两例方向互为镜像。")
            },
            "stressGap": {
                "widening": True,
                "note": "压力侧（资本需求增速）斜率高于能力侧（自有现金流），缺口在 Q3 反超并转向表外"
            },
            "operations": {
                "sourceTransformation": "源头改造（疏浚）：未发生——没有任何一方动 capex 节奏本身",
                "boundarySafeguarding": "底线守护（方舟）：名义存在（四条底线：折旧／杠杆率／评级门槛／监管资本），实际全部逼近触发线",
                "consensusCohesion": "共识凝聚（祭祀）：看似强、实则分裂——口头共识是「该改」，行为共识是「谁先改谁先暴露」"
            },
            "leveragePoint": {
                "location": "GPU 折旧年限（5–6 年 vs 独立估计经济寿命约 3 年）",
                "rationale": ("四条底线里唯一三条同时成立的一条：①每季度都要用一次（高频经过）；"
                              "②CFO 与审计师极少数人即可单边决定（不需要多方同意）；"
                              "③是约束不是状态——利润与杠杆率是它的结果。不是最显眼处：最显眼的是算力与模型能力。")
            },
            "constraintClassification": "evasive",
            "interventionChannel": "disclosure-first",
            "interventionFourQuestions": {
                "whichConstraint": "GPU 折旧年限（从 5–6 年向约 3 年靠）",
                "direction": "不一次性改，先强制披露「若按 3 年折旧，利润与杠杆是多少」，调整幅度由披露结果决定",
                "verification": "披露后市场定价是否出现非线性跳变——跳变说明此前定价建立在错误假设上",
                "rollback": "设线性过渡期；若融资成本上升过猛，暂停并补流动性安排"
            },
            "normativeLayer": {
                "authorization": "由会计与披露准则层面授权（CFO 与审计师即可变更会计估计），不需立法",
                "liability": "假设的签署方承担陈述责任；但失真后果主要由承压者承受",
                "exit": "承压者（电费用户、零售信贷、养老金）无退出通道——这是判为讳锁而非可调的关键",
                "fallback": "若披露触发融资成本骤升，以流动性安排与过渡期兜底；最终承担者仍是纳税人"
            },
            "refutation": {
                "ifWorse": "违约／评级下调／赎回受限／SPV 回表 任一生效 → 讳锁出现破口（向 broken 方向恶化）",
                "ifBetter": "强制披露落地且定价出现非线性跳变 → 盖子被掀开，讳锁解除，转入 crisis-restructuring 或 repair"
            },
            "infoAvailability": {
                "available": ["capex 指引与经营现金流", "折旧政策披露", "评级与杠杆率口径"],
                "unavailable": ["SPV 真实杠杆", "「经济寿命 3 年」的行业共识", "口径一致性"]
            },
            "validity": {
                "chainTraceable": True,
                "falsifiable": True,
                "infoHonest": True,
                "fourQuestionsComplete": True
            }
        }
    }
]
doc["version"] = "v1.2"
doc["x-changelog"] = [
    {"version": "v1.2", "date": "2026-11-20",
     "changes": [
         "constraintMutability / constraintClassification 由三分类升为四分类，新增 evasive（讳锁）",
         "stateDiagnosis.state 由四态升为五态，新增 evasive-lock-in（讳锁态）",
         "interventionChannel 新增 disclosure-first（讳锁的出路：先把代价摆到桌面，再调整）",
         "依据：《通用结构语法·诊断工作表 v2.0》与标本 No.03（AI 基础设施资本开支）的实践形态"
     ],
     "note": "讳锁 ≠ 固化。把「所有人都说该改、但没人先动」判成固化，会开错药方：固化等外部介入，讳锁需先披露代价。"}
]
doc["x-examples"] = [{"name": e["name"], "tool": e["tool"], "note": e["note"]} for e in EXAMPLES]
doc["x-exampleFile"] = "https://zhishuixue.com/dst-diagnosis.examples.json"
EX_OUT = OUT.replace(".schema.json", ".examples.json")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
print("已写出", OUT, "(%d B)" % os.path.getsize(OUT))
print("tools:", [t["name"] for t in doc["x-toolDefinitions"]])
print("$defs:", list(doc["$defs"].keys()))
print("SystemDiagnosisOutput 字段:", len(system_output["properties"]))
print("EventShadowingOutput 字段:", len(event_output["properties"]))
print("additionalProperties 封死节点数:", json.dumps(doc["$defs"]).count('"additionalProperties": false'))

with open(EX_OUT, "w", encoding="utf-8") as f:
    json.dump({
        "schema": "https://zhishuixue.com/dst-diagnosis.schema.json",
        "note": ("few-shot 示例集：给 Agent 一对完整的「输入→输出」。"
                 "多数 agent 不会执行 JSON Schema 校验，而是照抄示例；"
                 "因此示例比 schema 本身更决定它能不能被正确调用。"
                 "example-2 专门演示 judgeable=false 的退出通道。"),
        "license": "CC BY 4.0",
        "examples": EXAMPLES,
    }, f, ensure_ascii=False, indent=2)
print("已写出", EX_OUT, "(%d B)" % os.path.getsize(EX_OUT))
