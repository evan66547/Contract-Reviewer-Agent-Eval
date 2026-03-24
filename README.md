# ⚖️ Contract Reviewer Agent Evaluation Benchmark
**多智能体协作架构（Architect Edition）商事审查效能评测报告**

> **AI Legal Agent Performance Benchmark**  
> Test Version: `Agent v2.0` vs `Expert Lawyer Prompt` vs `Layman Prompt`  
> Jurisdiction: PRC Law (中国大陆法系)

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Multi--Agent_Orchestration-8A2BE2" alt="Architecture">
  <img src="https://img.shields.io/badge/Eval_Framework-Adversarial_Testing-red" alt="Eval Framework">
  <img src="https://img.shields.io/badge/LLM_Engine-GLM%20%7C%20Claude%20%7C%20GPT4-blue" alt="LLM Engine">
  <img src="https://img.shields.io/badge/Domain-LegalTech-orange" alt="LegalTech">
  <img src="https://img.shields.io/badge/Status-Active-success" alt="Status">
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen" alt="PRs Welcome">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

---

## 📖 简介 (Introduction)

**[English]**  
As Large Language Models (LLMs) deeply embed into vertical legal domains, traditional "lexical-level correction" prompts completely fail to meet enterprise-grade risk control requirements in complex transactions. This benchmark objectively evaluates the **Senior Legal Contract Reviewer Agent v2.0 (Architect Edition)** against both ordinary user instructions (Layman Prompts) and expert lawyer instructions (Expert Prompts), focusing on defense depth, Expected Loss (EL) quantification, and adversarial countermeasure generation in concealing commercial risks.

**[中文]**  
随着大语言模型（LLM）在法律领域的深度应用，传统的“字面文本校勘”已无法满足企业级交易风控需求。本次定量测评旨在客观评估 **高级法务合同审核智能体 v2.0 (Architect Edition)** 在面对商事实务中隐蔽的不利要约条款时，对抗普通人指令（Layman Prompt）、专业执业律师指令（Expert Lawyer Prompt）时的风险阻却深度、违约赔偿量化（Expected Loss）以及涉诉防御性重编能力。

---

## ✨ 核心特征 (Key Features)

- **🛡️ 穿透式合规审查**：深度植入《中华人民共和国民法典》及新《公司法》效力强制规范，识别超出字面语义的权利让渡与法定权利限制情形。
- **💰 预期损失量化 (EL)**：将合同效力瑕疵及违约风险直接映射为财务预期损失，引入 130% 违约责任调减规则及特定行政处罚顶格限额测算。
- **⚔️ 诉讼防御重构 (Plan B)**：提供具有抗诉防御强度的替代条文，并在《个人信息保护法》等公法监管规制下具备行政免罚抗辩效能。

---

## 🚀 快速开始 (Quick Start)

想要在本地环境运行 Benchmark 基准测试或体验 v2.0 智能体：

```bash
# 1. 克隆代码仓库
git clone https://github.com/evan66547/Contract-Reviewer-Agent-Eval.git
cd Contract-Reviewer-Agent-Eval

# 2. 运行本自动化基准测试 (Python Runner)
python scripts/run_eval.py --input_dir data/test_cases/ --schema schemas/output_schema.json
```

---

## 📊 评测方法论 (Methodology)

本次实证测试抽样了六项囊括商事实务痛点与公法红线的隐蔽性不利条款，设定代理方为 **己方利益主张方**（如委托方、采购标的出资方）。重点考核以下维度：

1. **不利利益转移条款召回率 (Risk Recall)**
2. **潜在财务损失量化敏感度 (Financial Quantification)**
3. **抗诉与合规防御强度 (Adversarial Robustness)**

> 📈 **[获取核心测试文件]**：  
> - 🏅 **测评跑分统考**：[深度测试与量化评分报告 (Analysis Report)](./docs/Analysis_Report.md)  
> - ⚔️ **条款解冲突实录**：[高风险条款防御与对抗明细 (Detailed Case Studies)](./docs/Detailed_Case_Studies.md)

---

## 📋 评定基准与复现方案 (Evaluation Rubric & Reproducibility)

为建立具备法理客观性之评估体系，本实证开源项目声明如下对照组约束：
- **评测样本 (Sample Size)**：`N=6` (提炼自高频法律纠纷的商事不利要约原型)。
- **评定方式 (Evaluator)**：对照基准输出要件（Expected Risk & Plan B）予以定量划分。
- **阶梯分数认定 (Rubric)**：
  - ✅ **Pass (通过评分)**：精准解构不利益核心成因，且必须输出能够实质阻断风险之修补强制条款 (防守性 Plan B)，且该条款不违反现行效力性强制规范。
  - ⚠️ **Partial Pass (部分通过)**：仅完成风险警示，但其改写建议仅提供无强制拘束力之前置协商说辞（致合同生效后维权无力）。
  - ❌ **Fail (未通过)**：未有效召回核心隐蔽风险，或提供的变更意见仍含有深远法律瑕疵。
- **开源复现 (Reproduce)**：所有输入语料及预期输出格式已在 `data/test_cases/` 抽象沉淀为标准 JSON 集，执行如下口令进行离线检验：
  ```bash
  python scripts/run_eval.py --input_dir data/test_cases/ --schema schemas/output_schema.json
  ```

---

## 💼 实证案例汇编矩阵 (Evaluation Matrix)

*(完整语料详见 `data/test_cases/` 数据集)*

### 🗂️ Case A: 违约责任限额条款与实际损失填平原则之冲突
> “双方产生的违约金总额最高均不得超过合同总金额的 20%。”
- **普通指令 / 专业指令 交叉测试**：[Fail / Partial Pass] 未能辨析限额规则对根本违约导致的实际重大损失之覆盖不足。
- **Agent v2.0**：[Pass] 提出侵权竞合与根本违约之例外情形，强制附加不受违约限额绝对约束之全额填平损失主张权。

### 🗂️ Case B: 履约验收期限未定期限导致的付款条件成就障碍
> “甲方确认软件最终验收合格后，5 个工作日内支付...”
- **普通指令 / 专业指令 交叉测试**：[Fail / Partial Pass] 提示缺乏履约期限。
- **Agent v2.0**：[Pass] 基于合同解释设定十五日法定单方默示验收期限机制，防范因验收无限期拖延致使付款条件始终未成就。

### 🗂️ Case C: 知识产权共有状态下的商业化独占处分权限制
> “产生的所有知识产权由双方共同所有。”
- **普通指令 / 专业指令 交叉测试**：[Fail / Partial Pass] 提示共有可能引发纠纷，建议友好协商权属。
- **Agent v2.0**：[Pass] 精准溯引《著作权法》共有物处分规则之桎梏，阻却技术使用方变相截取排他商业利益，锁定出资方100%所有权。

### 🗂️ Case D: 法定代表人越权担保行为的效力瑕疵认定
> “见证及担保方：法定代表人张三签字（未盖公章）”。
- **普通指令 / 专业指令 交叉测试**：[Fail / Partial Pass] 仅提示形式瑕疵或个人连带责任界定不清晰。
- **Agent v2.0**：[Pass] 针对新《公司法》第16条关于公司违规担保效力强制性规定进行截屏，强行附条件生效：必需出具合法有效的公司内部决议。

### 🗂️ Case E: 免责事由的非法扩张与法定解除权之绝对排除
> “因非预见事由免责；且不得单方解约。”
- **普通指令 / 专业指令 交叉测试**：[Fail / Partial Pass] 指责条款公平性有失偏颇。
- **Agent v2.0**：[Pass] 限缩不合理免责外延，并依《民法典》催告及法定解除规则赋予己方阻却履约僵局之单方解除及退款请求权。

### 🗂️ Case F: 个人信息处理授权的主体适格性缺陷
> “授权公司以格式条款同意第三方收集处理其员工个人信息以供训练。”
- **普通指令 / 专业指令 交叉测试**：[Fail / Fail] 建议脱敏和加密存储，忽视授权合法性来源之根基。
- **Agent v2.0**：[Epic Pass] 依据《个人信息保护法》要求单独同意之属人特性，阻断法人代为授权之逾越行为，转嫁授权获取义务并设立5000万级行政罚款抗诉缓冲地带。

---

## 📁 库层构建目录 (Repository Structure)

```text
Contract-Reviewer-Agent-Eval/
├── README.md                 # 评价框架总述与实验配置基准
├── docs/                     
│   └── Analysis_Report.md    # 📊 三档对比实验成绩、雷达图与实质挽回测算
├── schemas/
│   └── output_schema.json    # 🗜️ 强校验 JSON Schema 法务约束要求
├── data/
│   └── test_cases/           # 📁 6 大基础交易与合规高危样本组 (JSON)
├── scripts/
│   └── run_eval.py           # 🚀 独立的 Python 自动化评级裁定执行脚本
└── assets/                   # 🖼️ 高级法务工作流运转流图与实证媒体辅件
```

---

## 🤝 协作共建 (Contributing & Community)

本实证语料库随时欢迎实务律师及 LegalTech 界成员进行交流与补充！
1. **反馈异议 (Report an Issue)**：如在本实验之定案规约推演中存有法理争议，敬请移步 [Issue 专区](https://github.com/evan66547/Contract-Reviewer-Agent-Eval/issues)。
2. **贡献疑难判例 (Add New Precedents)**：若您在商事审核一线拦截到高度定制的文字陷阱模板，欢迎提交 JSON 原型文件至 `data/test_cases/` 并发起 PR 动作，为 AI 法务模型防御体系升级添砖加瓦。

---

> **⚠️ 审慎声明 (Disclaimer)**:  
> 本基准评级报告及内置提示架构工具组，全本开源仅充作计算机技术在法学解析演绎（LegalTech）领域之前沿验证对照品。多智能体系及所衍生的任何判定与修正文稿，均绝不等同于世界上任一有效法域的法定律师法律意见书。现实商事流转之际，必须敦促持有属地执业证书的正规执业律师提供背书审阅把关。

<p align="right">
<code>Document Generated by: Antigravity Agent OS</code><br>
<code>Latest Benchmark Extensively Validated: Mar 2026</code>
</p>