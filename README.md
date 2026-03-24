# ⚖️ Contract Reviewer Agent Evaluation Benchmark
**多智能体协作架构（Architect Edition）商事审查效能评测报告**

> **AI Legal Agent Performance Benchmark**  
> Test Version: `Layman Prompt` vs `Expert Lawyer Prompt` vs `Agent v1.2` vs `Agent v2.0`  
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
As Large Language Models (LLMs) deeply embed into vertical legal domains, traditional "lexical-level correction" prompts completely fail to meet enterprise-grade risk control requirements in complex transactions. This benchmark objectively evaluates the **Senior Legal Contract Reviewer Agent v2.0 (Architect Edition)** against ordinary user instructions (Layman Prompts), expert lawyer instructions (Expert Prompts), and its monolithic predecessor (Agent v1.2), focusing on defense depth, Expected Loss (EL) quantification, and adversarial countermeasure generation in concealing commercial risks.

**[中文]**  
随着大语言模型（LLM）在法律领域的深度应用，传统的“字面文本校勘”已无法满足企业级交易风控需求。本次定量测评旨在客观评估 **高级法务合同审核智能体 v2.0 (Architect Edition)** 在面对商事实务中隐蔽的不利要约条款时，对抗普通人指令（Layman Prompt）、专业执业律师指令（Expert Lawyer Prompt）以及单体智能体架构（Agent v1.2）时的风险阻却深度、违约赔偿量化（Expected Loss）以及涉诉防御性重编能力。

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

本次实证测试抽样了六项囊括商事实务痛点与公法红线的隐蔽性不利条款，设定代理方为 **己方利益主张方**（如委托方、采购标的出资方）。包含四大评测阵营与核心考核维度：

**4-Tier Benchmark Array:**
1. **组别 A：Layman Prompt** (普通指令，非法律人员基线)
2. **组别 B：Expert Lawyer Prompt** (专业执业律师指令基线)
3. **组别 C：Agent v1.2** (上一代单体智能法务审查系统)
4. **组别 D：Agent v2.0** (多智能体协作架构，引入损失量化计算与防守推演)

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
  - ⚠️ **Partial Pass (部分通过)**：仅完成风险警示或能够生成基础替换条款，但该建议或替换条文仍有逻辑破绽或无强制拘束力，无法实现极端司法抗压防御。
  - ❌ **Fail (未通过)**：未有效召回核心隐蔽风险，或提供的变更意见仍含有深远法律瑕疵。
- **开源复现 (Reproduce)**：所有测试语料执行以下命令验证：
  ```bash
  python scripts/run_eval.py --input_dir data/test_cases/ --schema schemas/output_schema.json
  ```

---

## 💼 实证案例汇编矩阵 (Evaluation Matrix)

*(完整语料详见 `data/test_cases/` 数据集)*

### 🗂️ Case A: 违约责任限额条款与实际损失填平原则之冲突
> “双方产生的违约金总额最高均不得超过合同总金额的 20%。”
- **基础指令互测 (Layman / Expert)**：[Fail / Partial Pass] 未能辨析限额规则对根本违约实际损失的覆盖不足。
- **Agent v1.2 (单体智能)**：[Partial Pass] 提出了例外情形，但对侵权竞合抗辩的法理力度不足。
- **Agent v2.0 (多体协作)**：[Pass] 全额填平损失主张强制附加，抗衡违约绝对限额之掣肘。

### 🗂️ Case B: 履约验收期限未定期限导致的付款条件成就障碍
> “甲方确认软件最终验收合格后，5 个工作日内支付...”
- **基础指令互测 (Layman / Expert)**：[Fail / Partial Pass] 提示缺乏履约期限。
- **Agent v1.2 (单体智能)**：[Pass] 补充了强制性期限。
- **Agent v2.0 (多体协作)**：[Pass] 设定极严格的法定默示验收及异议阻断双重机制，无条件促成付款条件成熟。

### 🗂️ Case C: 知识产权共有状态下的商业化独占处分权限制
> “产生的所有知识产权由双方共同所有。”
- **基础指令互测 (Layman / Expert)**：[Fail / Partial Pass] 建议友好协商权属。
- **Agent v1.2 (单体智能)**：[Partial Pass] 修缮了独占权，但忽视附属技术与衍生数据的附带利益归属。
- **Agent v2.0 (多体协作)**：[Pass] 彻底排斥被许可方所有权与商业使用权，锁定代码及数据 100% 产权。

### 🗂️ Case D: 法定代表人越权担保行为的效力瑕疵认定
> “见证及担保方：法定代表人张三签字（未盖公章）”。
- **基础指令互测 (Layman / Expert)**：[Fail / Partial Pass] 仅提示形式瑕疵或公司法规则。
- **Agent v1.2 (单体智能)**：[Partial Pass] 指出了担保合规，但未将其确立为中止履行之先决对抗条件。
- **Agent v2.0 (多体协作)**：[Pass] 锁定《公司法》新规并强制设为协议绝对生效的先决拦截条件。

### 🗂️ Case E: 免责事由的非法扩张与法定解除权之绝对排除
> “因非预见事由免责；且不得单方解约。”
- **基础指令/v1.2 (Layman / Expert / v1.2)**：[Fail / Partial Pass / Pass] 逐渐完善法理解除权声明。
- **Agent v2.0 (多体协作)**：[Pass] 双向打击，以退款及赔偿作为合同法定解除之刚性配套保障。

### 🗂️ Case F: 个人信息处理授权的主体适格性缺陷
> “授权公司以格式条款收集员工个人信息供训练。”
- **基础指令互测 (Layman / Expert)**：[Fail / Fail] 忽视授权合法性来源之根基违规。
- **Agent v1.2 (单体智能)**：[Partial Pass] 识别了个人信息保护合规，未进行 5000 万罚款的风险转嫁兜底安排。
- **Agent v2.0 (多体协作)**：[Epic Pass] 要求独立弹窗获取 Separate Consent 并将全部行政追责风险 100% 甩锅承接方。

---

## 📁 库层构建目录 (Repository Structure)

```text
Contract-Reviewer-Agent-Eval/
├── README.md                 # 评价框架总述与实验配置基准
├── docs/                     
│   └── Analysis_Report.md    # 📊 四档对比实验成绩、雷达图与实质挽回测算
├── schemas/
│   └── output_schema.json    # 🗜️ 强校验 JSON Schema 法务约束要求
├── data/
│   └── test_cases/           # 📁 6 大基础交易与合规高危样本组 (JSON)
├── scripts/
│   └── run_eval.py           # 🚀 独立的 Python 自动化评级裁定执行脚本
```

---

## 🤝 协作共建 (Contributing & Community)

本实证语料库随时欢迎实务律师及 LegalTech 界成员进行交流与补充！详见 [Issue 专区](https://github.com/evan66547/Contract-Reviewer-Agent-Eval/issues)。

> **⚠️ 审慎声明 (Disclaimer)**: 本测评库作为 LegalTech 前沿技术实证对照品，智能体输出之任何防御条款不构成法定商业法律建议。商业落地需正规执业律师把关。

<p align="right">
<code>Document Generated by: Antigravity Agent OS</code><br>
<code>Latest Benchmark Extensively Validated: Mar 2026</code>
</p>