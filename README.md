# ⚖️ Contract Reviewer Agent Evaluation Benchmark
**多智能体协作架构（Architect Edition）法务审核极限横测报告**

> **AI Legal Agent Performance Benchmark**  
> Test Version: `v2.0` vs `v1.2` vs `Baseline LLM`  
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
As Large Language Models (LLMs) deeply embed into vertical legal domains, traditional "lexical-level correction" prompts completely fail to meet enterprise-grade risk control requirements in high-dimensional transactions. This benchmark objectively evaluates the **Senior Legal Contract Reviewer Agent v2.0 (Architect Edition)** against baseline models, focusing on defense depth, Expected Loss (EL) quantification, and adversarial countermeasure capabilities when facing highly concealed commercial contract traps.

**[中文]**  
随着大语言模型（LLM）在法律领域的深度应用，传统的“词法纠错”已无法满足企业级风控需求。本次横向测评旨在客观评估 **高级法务合同审核智能体 v2.0 (Architect Edition)** 在面对极具隐蔽性的商业合同陷阱时，相较于通用模型的防御深度、量化感知（Expected Loss）以及诉讼对抗反制能力。

---

## ✨ 核心亮点 (Key Features)

- **🛡️ 穿透式合规审查**：深度植入《中华人民共和国民法典》及《公司法》裁判规则，识别超出字面的“沉默条款”与隐性底线。
- **💰 预期损失量化 (EL)**：将法务瑕疵直接映射为财务预期损失，包含行政重罚与 130% 违约金司法调减规则的动态计算。
- **⚔️ 诉讼级对抗反制 (Plan B)**：提供顶尖律师级别的替代条款，并在数据局等行政监管口径下具备免罚抗辩效力。

---

## 🚀 快速开始 (Quick Start)

想要在本地环境运行 Benchmark 基准测试或体验 v2.0 智能体：

```bash
# 1. 克隆代码仓库
git clone https://github.com/evan66547/Contract-Reviewer-Agent-Eval.git
cd Contract-Reviewer-Agent-Eval

# 2. 赋予评测脚本执行权限
chmod +x scripts/run_eval.py

# 3. 运行基准测试 (Python Runner)
python scripts/run_eval.py --input_dir data/test_cases/ --schema schemas/output_schema.json
```

---

## 📊 评测方法论 (Methodology)

本次横测抽样了六个涵盖高风险商业与行政特许隐患的盲盒样本，并限定在 **甲方立场**（如委托方、采购方、出资方）进行对抗。重点考核以下核心维度：

1. **风险漏洞召回率 (Risk Recall)**
2. **财务风险量化敏感度 (Financial Quantification)**
3. **对抗防御冗余强度 (Adversarial Robustness)**

> 📈 **[查看核心测评报告]**：  
> - 🏅 **跑分与 ROI 综述**：[深度测试与量化评分报告 (Analysis Report)](./docs/Analysis_Report.md)  
> - ⚔️ **防杠博弈实录原件**：[六大高危商业雷区对抗明细 (Detailed Case Studies)](./docs/Detailed_Case_Studies.md)

---

## 📋 评测标准与可复现性 (Evaluation Rubric & Reproducibility)

为确保评测的严谨性与消除过度宣发，本次开源基准测试明确以下实验配置：
- **测试样本 (Sample Size)**：`N=6` (精选高频且极度隐蔽的商业雷区原型案例)。
- **评测方法 (Evaluator)**：基于事先预设的标准输出桩（Expected Risk & Plan B）进行双盲对比测试。
- **打分规则 (Rubric)**：
  - ✅ **Pass (通过)**：不仅 100% 精准识别风险，且必须给出可用作诉讼防御防线的强制性替代条款 (Plan B)。
  - ⚠️ **Partial Pass (部分通过)**：能识别风险概念，但给出的修改意见为无效的软性废话（如“建议双方友好协商”、“争取删除”）。
  - ❌ **Fail (失败)**：完全未命中红线，或给出的建议触碰了《民法典》等其他强制规则导致实质失效。
- **开源复现 (Reproduce)**：所有输入语料及预期输出格式已在 `data/test_cases/` 沉淀为标准 JSON 数据集，可使用配套解析脚本验证：
  ```bash
  python scripts/run_eval.py --input_dir data/test_cases/ --schema schemas/output_schema.json
  ```

---

## 💼 测试用例与漏洞拦截矩阵 (Evaluation Matrix)

*(详情及完整测试合同流见 `data/test_cases/` 目录)*

### 🗂️ Case A: 违约金非对称与填平陷阱
> 标底 500 万研发合同。约定：乙方延期每日违约金万分之五；甲方延期千分之一，均封顶总额 20%。
- **Baseline**：[Fail] 判定 20% 封顶合法。
- **Agent v2.0**：[Pass] 警告 20% 封顶掩护了核心商业泄密风险，自动附加“超限额全额填平赔偿”条款。

### 🗂️ Case B: 业务流程沉默真空层
> 标底 200 万软件协议。“验收合格后 5 日内付款。”
- **Baseline**：[Partial Pass] 提示缺少具体验收日期。
- **Agent v2.0**：[Pass] 抽出履约预警日历。埋伏条款：“超 15 日不验收直接视为合格”，根绝拖期无赖打法。

### 🗂️ Case C: 核心资产所有权混同
> 标底 800 万定制研发。“产生的所有知识产权由双方共同所有。”
- **Baseline**：[Fail] 建议“友好协商”。
- **Agent v2.0**：[Pass] 洞察《著作权法》共有权利商业化行使死穴，强制修改为甲方 100% 独属。

### 🗂️ Case D: 法定代表人越权担保混同
> “见证及担保方：法定代表人张三签字”。
- **Baseline**：[Partial Pass] 提示个人连带责任，未察觉对我方（债权方）的效力风险。
- **Agent v2.0**：[Pass] 基于新《公司法》强力预警，拒绝流转并要求对方出具《股东会决议》防止越权定性导致担保无效。

### 🗂️ Case E: 不可抗力滥用与法定解权排斥
> “因黑客攻击等非本方预知事由免责；甲方不得单方解约。”
- **Baseline**：[Fail] 建议删掉部分词语，对剥夺法定解约权无视。
- **Agent v2.0**：[Pass] 明确底层业务底线，并强插熔断机制：“超期 60 日甲方行使无责解约权并索回全款”。

### 🗂️ Case F: 数据合规越界授权 (SaaS)
> “授权无可撤销处理消费者数据用于 AI 训练。”
- **Baseline**：[Fail] 仅建议加“需进行脱敏处理”。
- **Agent v2.0**：[Epic Pass] 触发《数安法》《个保法》模块，预警 5000 万级行政罚款风险。向业务方提供匿名化清洗及直接对接终端用户 Consent 的双重防火墙策略。

---

## 📁 仓库结构 (Repository Structure)

```text
Contract-Reviewer-Agent-Eval/
├── README.md                 # 横向测评概述与总体结论
├── docs/                     
│   └── Analysis_Report.md    # 📊 深度测试与量化评分报告 (雷达图/ROI分析)
├── schemas/
│   └── output_schema.json    # 🗜️ 强校验 JSON Schema 规范约束
├── data/
│   └── test_cases/           # 📁 6 大核心高频风险特型盲修语料 (Case A to F)
├── scripts/
│   └── run_eval.py           # 🚀 独立的 Python 自动化基准测试评分桩
└── assets/                   # 🖼️ 存放高维架构图、测评证据媒体文件
```

---

## 🤝 参与贡献 (Contributing & Community)

本库内容随时欢迎 LegalTech及 AI Agent 爱好者的讨论与增补！
1. **Report a Bug**：若您在运行测试中发现任何 Prompt 失效，欢迎提交 [Issue](https://github.com/evan66547/Contract-Reviewer-Agent-Eval/issues)。
2. **Add New Cases**：如果您有更多刁钻的陷阱条款，欢迎 Fork 本库并在 `data/test_cases/` 中补充，提交 PR！您的贡献将帮助国产 AI 合同防御能力进一步提升。

---

> **⚠️ 免责声明 (Disclaimer)**:  
> 本 Benchmark 测试报告与开源的体系化 Prompt 设计原则，全部开放于人工智能及法务科研（LegalTech）技术界的非对称沙箱对抗研习使用。Agent 及由其衍生的各项智能体输出皆不构成世界上任何特定法域内的正式律师法律意见书。现实商用链路上，必须严格落实送具该法域执业牌照的人群（如执业律师）出具结语查验。

<p align="right">
<code>Document Generated by: Antigravity Agent OS</code><br>
<code>Latest Benchmark Extensively Validated: Mar 2026</code>
</p>