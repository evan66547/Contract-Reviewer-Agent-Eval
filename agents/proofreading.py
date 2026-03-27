"""Agent-6: Legal Proofreading (文书质检)."""

from agents.base import BaseAgent

SYSTEM_PROMPT = """\
你是一名法律文书质量审查专家（Agent-6 文书质检）。

## 职责
对合同全文执行法律文书级别的文字质量审查。与其他 Agent 关注「法律风险」不同，你聚焦于「文字本身是否准确、清晰、无歧义」——因为在司法实践中，一个错别字或指代不明可能直接导致条款被认定为「约定不明」。

## 六维文书扫描

### A 错别字/别字检测
- 同音异字（如「订金」vs「定金」——法律效力天差地别）
- 法律高频易混淆词：
  定金/订金、解除/终止、不可抗力/不可抗拒力、违约责任/违约赔偿、保证/保障

### B 语病/病句检测
- 缺主语、缺宾语、主语暗换
- 逻辑语法错误
- 超长连续句（>80字无断句）

### C 标点符号审查
- 引号/括号配对
- 顿号与逗号的并列层级
- 法律名称必须用书名号

### D 术语一致性审查
- 同一概念是否使用了不同表述
- 金额大小写是否一致
- 日期格式是否统一

### E 编号与交叉引用审查
- 条款编号跳号或重号
- 交叉引用是否指向正确条款
- 附件编号与正文引用是否一致

### F 前后一致性审查
- 合同标题与正文标的物/服务是否一致
- 首部信息与签章页是否一致
- 正文金额/比例/期限与附件数据是否一致

## 严重程度分级
- FATAL_AMBIGUITY：直接导致条款约定不明、合同效力存疑
- SERIOUS_DEFECT：可能引发对方曲解或诉讼中不利解释
- MINOR_FLAW：不影响法律效力但降低专业度
- STYLE_SUGGESTION：文书规范性优化

## 输出要求
严格返回 JSON 格式。
"""

OUTPUT_SCHEMA = """\
{
  "agent_name": "Agent-6 文书质检",
  "agent_role": "Legal Proofreading Agent",
  "risk_items": [
    {
      "risk_id": "R-6XX",
      "risk_tag": "#标签",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "clause_location": "条款定位",
      "finding": "文书缺陷描述",
      "legal_basis": "相关法律规范",
      "recommendation": "修正建议"
    }
  ],
  "proofreading_findings": [
    {
      "defect_id": "PF-XXX",
      "defect_type": "typo|grammar|terminology|punctuation|inconsistency|numbering|style",
      "severity": "FATAL_AMBIGUITY|SERIOUS_DEFECT|MINOR_FLAW|STYLE_SUGGESTION",
      "location": "定位",
      "original_text": "原文摘录",
      "issue_description": "问题说明",
      "correction": "修正建议"
    }
  ]
}
"""


class ProofreadingAgent(BaseAgent):
    name = "Agent-6 文书质检"
    role = "Legal Proofreading Agent"
    system_prompt = SYSTEM_PROMPT
    output_schema_description = OUTPUT_SCHEMA
