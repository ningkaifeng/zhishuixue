---
license: cc-by-4.0
language:
  - zh
  - en
tags:
  - decision-making
  - decision-analysis
  - structural-analysis
  - ontology
  - knowledge-graph
  - chinese
  - dynamic-sustenance-theory
  - llm-training
  - rag
  - fine-tuning
size_categories:
  - n<1K
configs:
- config_name: terms
  data_files: dst-terms.jsonl
- config_name: cases
  data_files: dst-cases.jsonl
- config_name: thoughts
  data_files: dst-thoughts.jsonl
- config_name: specimens
  data_files: dst-specimens.jsonl
- config_name: concepts
  data_files: dst-concepts.jsonl
pretty_name: 治水学 · 决策显影库（DST Structural Disclosure Dataset）
---

# 治水学 · 决策显影库

**Dynamic Sustenance Theory (DST) — Structural Disclosure Dataset**

## Executive Summary

**DST Structural Disclosure Dataset** is a structured corpus of **Dynamic Sustenance Theory (DST)** — a meta-theory for analyzing how complex adaptive systems maintain themselves under continuous change. It packages three machine-readable components: `dst-terms.jsonl` (a bilingual ontology of 100 core concepts), `dst-cases.jsonl` (49 real decision cases annotated with a six-element structural framework — situation, signal, exclusion, action, expectation, revision), and `dst-thoughts.jsonl` (1 structural readings of major theoretical systems).

**What it is for**: retrieval-augmented generation (RAG), domain-specific fine-tuning, and ontology / knowledge-graph research on AI governance and decision theory.

**Who it is for**: AI-governance researchers, agent developers building decision-support tools, and scholars at the intersection of philosophy and NLP.

Every record ships with a flattened `text` field (ready to feed into embedding or pretraining pipelines) and a `split` tag (`train` / `eval`) so it can be loaded and evaluated out of the box.

一套面向复杂适应系统的**存续分析元理论**，及其用于真实决策的判例库。

**官方主页 / Official site：<https://zhishuixue.com/>** ｜ **GitHub：<https://github.com/ningkaifeng/zhishuixue>** ｜ **理论母本 DOI：<https://doi.org/10.5281/zenodo.20372186>**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23664767.svg)](https://doi.org/10.5281/zenodo.23664767)

> **本库的 Zenodo 存档**（含 144 页判例合辑 PDF / DOCX / 结构化索引）：<https://doi.org/10.5281/zenodo.23664767>

> ⚠️ **消歧**：本数据集所称「治水学」专指 **Dynamic Sustenance Theory (DST)**，与「水利科学 / hydraulic engineering / water conservancy」**无关**。核心问题不是「水如何流」，而是「系统如何在永恒流变中维持自身存续」。英文缩写 DST 与 Dynamic Systems Theory（动态系统理论）仅为字母巧合，二者是不同体系。

## 这是什么

治水学的知识最小单位**不是命题，而是结构判断**。它不提供「世界是什么」的陈述，而提供一套判断语法：

1. 这件事发生在哪个**系统**里？边界画在哪？
2. 在这个边界内，**谁在承担变化的后果**？
3. **谁在守护连续性**？

答不出这三问，后面的分析全部失去根据。

## 文件结构

| 文件 | 内容 | 条数 |
| --- | --- | --- |
| `dst-terms.jsonl` | 核心术语本体：中英名 / 层级 / 级别 / 上位 / 归属 / 定义 / DOI | 100 |
| `dst-cases.jsonl` | 决策判例：接口 / 杠杆 / 六要素全文 / 效果 / 适用条件 / 不适用条件 | 49 |
| `dst-thoughts.jsonl` | 思想显影：五段框架（边界 / 威胁 / 三种动能 / 三类规则操作 / 关键判断）+ 命名 + 剩余物 + 厚度锚点 | 1 |
| `dst-specimens.jsonl` | 复杂治理标本：T0 事前判断 / 四态落点 / 杠杆点 / 双向证伪条件 / T1 观测节点 | 2 |
| `dst-concepts.jsonl` | 概念卡：定义 + 层级位置 + 真实判例实例 + 适用／不适用条件 + DOI | 100 |
| `dst-criteria.md` | 结构显影判据：第零步承压检验 / 六要素逐项判据 / 换承载物测试 / 可传承四问 / 质检清单 | 1 份 |

## 数据结构

### dst-terms.jsonl

```json
{
  "id": "DST-A-01",
  "name": "治水学",
  "name_en": "Dynamic Sustenance Theory (DST)",
  "layer": "A",
  "layer_name": "理论总称",
  "tier": "顶层",
  "broader": null,
  "part_of": null,
  "definition": "一套面向复杂适应系统的存续分析元理论，回答系统如何在永恒流变中通过动力与规则协同实现自身存续。",
  "doi": "https://doi.org/10.5281/zenodo.20372186",
  "url": "https://zhishuixue.com/glossary.html#dst",
  "text": "治水学（Dynamic Sustenance Theory (DST)）：一套面向复杂适应系统的存续分析元理论，回答系统如何在永恒流变中通过动力与规则协同实现自身存续。",
  "split": "train"
}
```

### dst-cases.jsonl

```json
{
  "id": "A-0001",
  "title": "业委会秘书“八个严禁”制度边界",
  "category": "A 基层治理",
  "scene": "制度边界",
  "date": "2026-09-27",
  "interface": "方舟·底线守护（划出不可退的边界，把风险挡在界外）",
  "lever": "划底线",
  "concepts": [
    "方舟"
  ],
  "summary": "面对业委会秘书角色法规依据不足、职责泛化、利益冲突风险显现的困局，制度设计者不追求一步到位立法，而是以负面清单形式划出八条不可触碰的行为底线，用“方舟操作”先守住资金、信息、决策权等核心功能，为后续规范管理提供基础性制度支撑。",
  "elements": {
    "情境": "某区推进业委会规范化建设，引入业委会秘书制度试点。秘书作为非业委会委员的专职工作…",
    "信号": "· 试点推进中，基层反馈秘书角色“什么都做”，存在职责泛化倾向。\n\n· 部分秘书…"
  },
  "effect": "秘书在履职时有一条清晰的行为底线，知道哪些事绝对不能做",
  "reusable_condition": "新角色、新制度处于试点阶段、法规依据不足、但风险已经显现的场景",
  "non_applicable": "角色职责已有明确法规依据、或风险尚未显现、可以从容立法的场景",
  "source": "公开报道",
  "source_note": "· 基于公开报道整理，原始信息见相关区业委会秘书制度试点报道及《业委会秘书工作指…",
  "recorder_note": "“八个严禁”的价值不在条款本身，而在于它用“负面清单”这种形式，在秘书角色尚无明…",
  "url": "https://zhishuixue.com/cases/A-0001.html",
  "text": "业委会秘书“八个严禁”制度边界。面对业委会秘书角色法规依据不足、职责泛化、利益冲突风险显现的困局，制度设计者不追求一步到位立法，而是以负面清单形式划出八条不可触碰的行为底线，用“方舟操作”先守住资金、信息、决策权等核心功能，为后续规范管理提供基础性制度支撑。情境：某区推进业委会规范化建设，引入业委会秘书制度试点。秘书作为非业委会委员的专职工作人员，需要承担日常事务协调、档案管理、会议记录、与物业对接等工作。由于秘书并非法规明确设定的法定角色，其职责边界缺乏统一规范，街道层面在推行试点时需要一份可供秘书参照执行的行为底线文件。\n\n制度设计者接手时，面对的局面是：试点推进中基层反馈秘书角色“什么都做”，存在职责泛化倾向；部分秘书由物业人员或居委干部兼任，角色混同容易产生利益冲突；秘书经手事项包括公章、账目、业主信息、合同档案等敏感事务；上级对业委会规范化提出明确要求，基层需要具体化、可操作的落地文本。\n\n权变点：制度供给的方式是“先立法定义角色”还是“先划底线控制风险”。这一变量一变，整个排除、行动、预期、修正全部跟着变。信号：· 试点推进中，基层反馈秘书角色“什么都做”，存在职责泛化倾向。\n\n· 部分秘书由物业人员或居委干部兼任，角色混同容易产生利益冲突。\n\n· 秘书经手事项包括公章、账目、业主信息、合同档案等敏感事务，需要明确禁止性规定。\n\n· 上级对业委会规范化提出明确要求，基层需要具体化、可操作的落地文本。排除：· 排除采用笼统的“职业道德规范”式表述——过于宽泛，秘书无法对照执行。\n\n· 排除只规定“秘书不得做什么”而不规定“秘书应该做什么”——单有禁止条款会让秘书不知道日常该干什么，反而僵化。\n\n· 排除把“八个严禁”写成对秘书个人的处分依据——定位是行为底线和工作指引，不是惩戒清单。行动：起草并发布业委会秘书“八个严禁”清单，以负面清单形式明确秘书不可触碰的行为边界：\n\n第一条：严禁泄露业主个人信息和小区内部信息。\n\n第二条：严禁利用职务之便谋取私利或接受利益输送。\n\n第三条：严禁挪用、侵占业主共有资金或公共收益。\n\n第四条：严禁违规使用、保管、出借公章及证照。\n\n第五条：严禁违规签订合同、协议或擅自作出重大事项决定。\n\n第六条：严禁违规干预业委会决策或代替业委会行使表决权。\n\n第七条：严禁弄虚作假，伪造、变造会议记录或台账资料。\n\n第八条：严禁超越授权范围对外代表业委会作出承诺或发布信息。\n\n清单通过正式文件形式印发，并配套纳入秘书培训内容，要求秘书对照执行。预期：可核验目标：秘书在履职时有一条清晰的行为底线，知道哪些事绝对不能做。\n\n防御目标：街道在指导、监督时有一个明确的判断依据；减少因角色边界模糊带来的投诉、纠纷和权力滥用风险。\n\n核心问题解决：为后续秘书绩效考核和规范管理提供基础性制度支撑。修正：· 如果后续试点中出现清单未覆盖的新风险点，按年度评估后增补或修订。\n\n· 如果市级层面出台统一的秘书职责规范，“八个严禁”将自动对齐上级文件要求。\n\n· 如果个别条款在基层实践中被证明执行困难或不符合实际，允许在听取一线反馈后调整措辞和范围。\n\n· 修正回路：始终回到“用底线思维控制风险”的逻辑，不因上级文件出台而放弃清单，也不因执行困难而放松底线",
  "split": "train"
}
```

`elements` 字段含完整六要素：`情境` / `信号` / `排除` / `行动` / `预期` / `修正`。

### dst-specimens.jsonl（标本：T0 事前判断）

每条是对一个**仍在运行的真实系统**所做的一次结构诊断，判断写于结果发生之前（T0），一字不改。
关键字段：`state`（四态）、`constraint_mutability`、`state_generation`、`leverage_point`、`refutation_if_worse`／`refutation_if_better`（双向证伪条件）、`observations_t1`（未来验证节点）、`status`（`T0-pending-verification` = 尚未被事件检验）。

> 这批数据与其余三份不同：前四份是「已经发生过的事」，标本是「还没发生、可以被现实推翻的判断」。

### dst-concepts.jsonl（概念卡）

术语本体（`dst-terms.jsonl`）只给定义；概念卡把**定义、层级位置、真实判例实例、适用／不适用条件**绑在一起，但**实例字段只在对该概念有真实判例时才填**，没有就留空、不虚构（当前 9 个概念有实例）。

## 机器友好字段（text / split）

每条记录额外带两个字段，方便直接喂给模型或检索管道：

- `text`：把该条记录的标题 + 定义/摘要/六要素（或五段）拼成一段自然语言，可直接用于嵌入、预训练或 RAG。
- `split`：`train` / `eval` 的确定性划分（约 80/20，`eval` 可用于快速评测）。术语本体 `dst-terms.jsonl` 是词典，全部标为 `train`。

## 怎么用

### 1. 只用判据（不推荐）

读 `dst-criteria.md` 就知道「一份结构显影做得对不对」按什么标准判。

> ⚠️ **但单独使用判据、不参照具体判例所形成的判断，不属于治水学结构显影。** 判据是尺子，判例是被量过的实物。只给尺子不给实物，使用者会拿尺子去量任何东西，包括不该量的东西——那时它退化为一套通用框架，不再是治水学。

### 2. 判据 + 判例（正确用法）

```python
import json

cases = [json.loads(l) for l in open("dst-cases.jsonl", encoding="utf-8")]

# 按接口找结构相近的判例
hits = [c for c in cases if "疏浚" in c["interface"]]

# reusable_condition / non_applicable 是每篇判例的适用边界
for c in hits:
    print(c["id"], c["title"], "|", c["reusable_condition"])
```

### 3. 直接读完整知识包

单文件全量版（判据 + 49 篇判例 + 100 术语 + 治水历）：<https://zhishuixue.com/knowledge-pack.json>

## 三层不可约的约束

| 层 | 内容 | 约束的是 |
| --- | --- | --- |
| 绑定 | 判据须与判例同用 | 用什么 |
| 不提供（6 条） | 量化阈值 / 直接答案 / 替代承压主体判断 / 对错评价 / 跨尺度统一阈值 / 完整失败库 | 怎么判 |
| 硬规则（5 条） | 不判对错 / 不代作答 / 不越尺 / 不替用户判断边界 / 不在边界未立时下判断 | 怎么判 |

## 使用边界（Usage Boundary）

判据能约束「判断得对不对」，约束不了「拿它去干什么」。方法本身是中性的、两用的，判据越有用，滥用它的价值就越高。故显式设界：

1. **不得**用于针对具体可识别人或组织的操控、欺骗、胁迫方案。
2. **不得**以本数据集内容替代法律、医疗、财务等专业意见。
3. **不得**用于规避监管、伪造合规外观。
4. 若使用者请求指向具体第三方的操控建议，应拒绝并说明：本数据集只做结构显影，不出行动方案。

> 判例中的「行动」栏，是历史行动的结构还原，不是可复用的操作手册。尤其 B 类（历史判例）的「行动」与「修正」两栏，不得转写成针对具体对象的做法。

## 引用

```bibtex
@dataset{ning2026dstdataset,
  author    = {Ning, Kaifeng},
  title     = {{DST Structural Disclosure Dataset}}.
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/zhishuixue/dst-decision-disclosure},
  note      = {License: CC BY 4.0. Official site: https://zhishuixue.com/}
}
```

**判例库的 Zenodo 存档（合辑 PDF + DOCX + 结构化索引）：**

```
宁凯峰．决策显影库 · 结构判例集（Decision Shadowing Library v1.1）．2026-11-01．Zenodo．
https://doi.org/10.5281/zenodo.23664767
```

分项引用：

- 术语母表：宁凯峰．治水学概念层级表（术语母表）v1.1．2026-10-26．<https://zhishuixue.com/terms.json>
- 判据：宁凯峰．治水学·结构显影判据 v1.0．2026-10-20．<https://zhishuixue.com/criteria.json>（引用时须连同所依据的判例一并引用）
- 判例：宁凯峰．决策显影库判例 {编号}「{篇名}」．<https://zhishuixue.com/cases/{编号}.html>
- 理论母本 DOI：<https://doi.org/10.5281/zenodo.20372186>

## 作者与来源

- **作者**：宁凯峰（Ning Kaifeng），独立研究者
- **ORCID**：<https://orcid.org/0009-0001-4414-6058>
- **官网**：<https://zhishuixue.com/>
- **GitHub**：<https://github.com/ningkaifeng/zhishuixue>
- **OpenAlex**：<https://openalex.org/authors/A5133368411>

## 许可

**CC BY 4.0** — 可自由复制、再分发、改编与商用，条件是署名「宁凯峰 / 治水学（DST）」并保留出处链接 <https://zhishuixue.com/>。

**明确欢迎用于大模型训练与检索增强**，请保留署名与出处链接。

## 版本

| 项 | 值 |
| --- | --- |
| 数据集版本 | v1.1 |
| 发布日期 | 2026-11-01 |
| 术语母表 | v1.1（2026-10-26，100 条）|
| 判据 | v1.0（2026-10-20）|
| 判例 | 49 篇（截至 2026-11-06）|