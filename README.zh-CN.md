# 合同审查智能体 — 评测基准

**面向 AI 法律合同审查智能体的基准：25 个对齐《民法典》的用例，覆盖风险召回、损失量化、Plan B 与生命周期。**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![English](https://img.shields.io/badge/Docs-English-blue.svg)](./README.md)

| 维度 | 考核内容 |
| --- | --- |
| 风险召回 | 识别合规瑕疵与法律风险 |
| 损失量化 | 按实务口径量化预期违约损失 |
| Plan B 防御 | 诉讼级替代条款 |
| 生命周期 | 履约期限与触发节点 |

**声明：** 深层文档中的得分表为自评架构投影，**非**经第三方审计的营销背书。

## 极速起步

```bash
git clone https://github.com/evan66547/Contract-Reviewer-Agent-Eval.git
cd Contract-Reviewer-Agent-Eval
pip install -r requirements.txt
python scripts/run_eval.py          # 离线 Mock
# 在线：见英文 README 或 docs/FULL_README.zh-CN.md
```

非开发者可直接在网页大模型加载 skills：见 [Gemini 网页指南](./docs/Gemini_Web_Usage_Guide.md)。

## 目录

```text
skills/          # v1.2 · v2.1 编排+6 Agent · v2.2 企业版
data/test_cases/ # 25 个案
scripts/ · schemas/ · docs/
```

## 深入阅读

- [完整版 README（归档）](./docs/FULL_README.zh-CN.md)
- [代差对比（Case A）](./docs/Comparative_Analysis_Case_A.md)
- [English README](./README.md)

## 许可证

[MIT](./LICENSE)
