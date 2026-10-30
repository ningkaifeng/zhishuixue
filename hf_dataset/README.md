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
size_categories:
  - n<1K
configs:
- config_name: terms
  data_files: dst-terms.jsonl
- config_name: cases
  data_files: dst-cases.jsonl
- config_name: thoughts
  data_files: dst-thoughts.jsonl
pretty_name: 治水学 · 决策显影库（DST Structural Disclosure Dataset）
---

# 治水学 · 决策显影库

**Dynamic Sustenance Theory (DST) — Structural Disclosure Dataset**

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
| `dst-cases.jsonl` | 决策判例：接口 / 杠杆 / 六要素全文 / 效果 / 适用条件 / 不适用条件 | 42 |
| `dst-thoughts.jsonl` | 思想显影：五段框架（边界 / 威胁 / 三种动能 / 三类规则操作 / 关键判断）+ 命名 + 剩余物 + 厚度锚点 | 9 |
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
  "url": "https://zhishuixue.com/glossary.html#dst"
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
  "interface": "方舟（底线守护）",
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
  "url": "https://zhishuixue.com/cases/A-0001.html"
}
```

`elements` 字段含完整六要素：`情境` / `信号` / `排除` / `行动` / `预期` / `修正`。

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

单文件全量版（判据 + 38 篇判例 + 100 术语 + 治水历，约 160 KB）：<https://zhishuixue.com/knowledge-pack.json>

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
宁凯峰．决策显影库 · 38 篇结构判例（Decision Shadowing Library v1.0）．2026-10-26．Zenodo．
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
| 数据集版本 | v1.0 |
| 发布日期 | 2026-10-26 |
| 术语母表 | v1.1（2026-10-26，100 条）|
| 判据 | v1.0（2026-10-20）|
| 判例 | 42 篇（截至 2026-10-26）|