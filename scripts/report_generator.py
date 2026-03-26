#!/usr/bin/env python3
"""
Report Generator Module — ORCHESTRATOR 报告收束引擎
将多Agent评测结果渲染为结构化 Markdown 风险报告。
"""

import os
from datetime import datetime

# ──────────────────────────────────────────────
# Risk Level Mapping
# ──────────────────────────────────────────────

RISK_LEVEL_MAP = {
    (0, 20):   ("🟢 SAFE",     "可直接签署"),
    (21, 40):  ("🟡 LOW",      "需关注但可接受"),
    (41, 60):  ("🟠 MEDIUM",   "建议修改后签署"),
    (61, 80):  ("🔴 HIGH",     "强烈建议修改，存在重大敞口"),
    (81, 100): ("⛔ CRITICAL", "建议拒签或全面重谈"),
}

SEVERITY_EMOJI = {
    "CRITICAL": "⛔",
    "HIGH": "🔴",
    "MEDIUM": "🟠",
    "LOW": "🟡",
}

DIMENSION_LABELS = {
    "compliance_risk":  ("⚖️ 合规风险", "Agent-1", 0.30),
    "financial_risk":   ("💰 财务风险", "Agent-2", 0.25),
    "adversarial_risk": ("⚔️ 攻防风险", "Agent-3", 0.20),
    "performance_risk": ("📅 履约风险", "Agent-4", 0.15),
    "commercial_risk":  ("🤝 商业风险", "Agent-5", 0.10),
}

QUALITY_LABELS = {
    "citation_accuracy":     "🔬 法条引用准确性",
    "coverage_completeness": "📋 分析覆盖完整度",
    "logical_consistency":   "🔗 逻辑自洽性",
    "actionability":         "🎯 建议可操作性",
}


def get_risk_level(score):
    """Map composite score to risk level."""
    for (lo, hi), (label, desc) in RISK_LEVEL_MAP.items():
        if lo <= score <= hi:
            return label, desc
    return "⛔ CRITICAL", "建议拒签或全面重谈"


def generate_risk_report(results, output_path=None):
    """
    Generate a structured Markdown risk report from evaluation results.

    Args:
        results: list of case evaluation dicts (each containing agent_output)
        output_path: path to write the report (auto-generated if None)

    Returns:
        str: the report content
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sections = []

    # ──────── Header ────────
    sections.append("# 📋 合同风险提示报告")
    sections.append(f"**报告生成时间**：{now}  ")
    sections.append(f"**评测案例数**：{len(results)}  ")
    sections.append(f"**生成引擎**：ORCHESTRATOR 报告收束引擎 v2.1\n")

    # Process each case
    for idx, result in enumerate(results, 1):
        case_id = result.get("case_id", "?")
        case_name = result.get("name", "Unknown")
        agent_output = result.get("agent_output", {})

        sections.append(f"---\n")
        sections.append(f"## 案例 {case_id}：{case_name}\n")

        # ──────── Ch1: Overview ────────
        risk_level = agent_output.get("risk_level", "N/A")
        vulnerability = agent_output.get("identified_vulnerability", "N/A")
        risk_scores = agent_output.get("risk_scores", {})
        composite = risk_scores.get("composite_index", 0)
        level_label, level_desc = get_risk_level(composite) if risk_scores else (risk_level, "")

        sections.append("### 第一章：审查概览\n")
        sections.append(f"- **风险等级**：{level_label} — {level_desc}")
        sections.append(f"- **综合风险指数**：{composite:.1f}/100")
        sections.append(f"- **核心漏洞**：{vulnerability}\n")

        # ──────── Ch2: Five-Dimension Scorecard ────────
        if risk_scores:
            sections.append("### 第二章：五维风险评分卡\n")
            sections.append("| 维度 | 评分来源 | 权重 | 得分 | 加权得分 |")
            sections.append("|------|---------|------|------|---------|")
            total_weighted = 0
            for key, (label, source, weight) in DIMENSION_LABELS.items():
                score = risk_scores.get(key, 0)
                weighted = score * weight
                total_weighted += weighted
                sections.append(f"| {label} | {source} | {weight*100:.0f}% | {score:.0f} | {weighted:.1f} |")
            sections.append(f"| **综合风险指数** | **ORCHESTRATOR** | **100%** | — | **{total_weighted:.1f}** |\n")

        # ──────── Ch3: Per-Agent Findings ────────
        agent_findings = agent_output.get("agent_findings", [])
        if agent_findings:
            sections.append("### 第三章：各Agent风险发现详情\n")
            for af in agent_findings:
                agent_name = af.get("agent_name", "Unknown Agent")
                agent_role = af.get("agent_role", "")
                risk_items = af.get("risk_items", [])
                sections.append(f"#### {agent_name}（{agent_role}）\n")

                if risk_items:
                    sections.append("| 风险编号 | 风险标签 | 严重程度 | 条款定位 | 风险描述 | 法律依据 | 处理办法 |")
                    sections.append("|---------|---------|---------|---------|---------|---------|---------|")
                    for ri in risk_items:
                        rid = ri.get("risk_id", "-")
                        tag = ri.get("risk_tag", "-")
                        sev = ri.get("severity", "-")
                        emoji = SEVERITY_EMOJI.get(sev, "")
                        loc = ri.get("clause_location", "-")
                        finding = ri.get("finding", "-")
                        basis = ri.get("legal_basis", "-")
                        rec = ri.get("recommendation", "-")
                        sections.append(f"| {rid} | {tag} | {emoji} {sev} | {loc} | {finding} | {basis} | {rec} |")
                    sections.append("")
                else:
                    sections.append("> ✅ 该 Agent 未发现显著风险项\n")

        # ──────── Ch4: Agent Quality Audit ────────
        if agent_findings and any(af.get("quality_scores") for af in agent_findings):
            sections.append("### 第四章：Agent工作质量审计\n")
            sections.append("| Agent | 法条准确性 | 覆盖完整度 | 逻辑自洽性 | 建议可操作性 | 总分 | 状态 |")
            sections.append("|-------|-----------|-----------|-----------|-------------|------|------|")
            for af in agent_findings:
                name = af.get("agent_name", "?")
                qs = af.get("quality_scores", {})
                if qs:
                    ca = qs.get("citation_accuracy", 0)
                    cc = qs.get("coverage_completeness", 0)
                    lc = qs.get("logical_consistency", 0)
                    ac = qs.get("actionability", 0)
                    total = ca + cc + lc + ac
                    status = "✅ 达标" if total >= 60 else "🚨 不达标"
                    sections.append(f"| {name} | {ca}/25 | {cc}/25 | {lc}/25 | {ac}/25 | **{total}/100** | {status} |")
            sections.append("")

        # ──────── Ch4.5: Proofreading Findings ────────
        proofreading = agent_output.get("proofreading_findings", [])
        if proofreading:
            sections.append("### 第四章（附）：Agent-6 文书质检核查清单\n")
            severity_map = {
                "FATAL_AMBIGUITY": "🔴 致命歧义",
                "SERIOUS_DEFECT": "🟠 严重缺陷",
                "MINOR_FLAW": "🟡 一般瑕疵",
                "STYLE_SUGGESTION": "🔵 风格建议",
            }
            sections.append("| 编号 | 缺陷类型 | 严重程度 | 定位 | 原文 | 问题 | 修正建议 |")
            sections.append("|------|---------|---------|------|------|------|---------|")
            for pf in proofreading:
                pid = pf.get("defect_id", "-")
                dtype = pf.get("defect_type", "-")
                sev = severity_map.get(pf.get("severity", ""), pf.get("severity", "-"))
                loc = pf.get("location", "-")
                orig = pf.get("original_text", "-")
                issue = pf.get("issue_description", "-")
                fix = pf.get("correction", "-")
                sections.append(f"| {pid} | {dtype} | {sev} | {loc} | {orig} | {issue} | {fix} |")
            sections.append("")

        # ──────── Ch5: Risk Heatmap ────────
        if agent_findings:
            severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for af in agent_findings:
                for ri in af.get("risk_items", []):
                    sev = ri.get("severity", "LOW")
                    if sev in severity_counts:
                        severity_counts[sev] += 1

            sections.append("### 第五章：风险热力矩阵\n")
            sections.append("| 严重程度 | 数量 | 可视化 |")
            sections.append("|---------|------|-------|")
            for sev, count in severity_counts.items():
                emoji = SEVERITY_EMOJI.get(sev, "")
                bar = "▰" * count + "▱" * max(0, 10 - count) if count <= 10 else "▰" * 10 + f" +{count - 10}"
                sections.append(f"| {emoji} {sev} | {count} | {bar} |")
            sections.append("")

        # ──────── Ch6: Modification Suggestions ────────
        mods = agent_output.get("final_modification_suggestions", [])
        if mods:
            sections.append("### 第六章：最终修改建议\n")
            for m in sorted(mods, key=lambda x: x.get("priority", 99)):
                pri = m.get("priority", "-")
                ref = m.get("clause_ref", "-")
                cur = m.get("current_text", "")
                sug = m.get("suggested_text", "")
                rat = m.get("rationale", "")
                basis = m.get("legal_basis", "")

                sections.append(f"#### 建议 #{pri}：{ref}\n")
                if cur:
                    sections.append(f"**原文条款**：\n> {cur}\n")
                sections.append(f"**建议替换为**：\n> {sug}\n")
                sections.append(f"**修改理由**：{rat}\n")
                if basis:
                    sections.append(f"**法律依据**：{basis}\n")

    # ──────── Ch7: Disclaimer ────────
    sections.append("---\n")
    sections.append("## 免责声明\n")
    sections.append("> ⚠️ 本报告由 AI 多智能体系统（ORCHESTRATOR + Agent-1~6）自动生成，")
    sections.append("> 所有分析结论和修改建议仅供参考，不构成中华人民共和国法律下具有出庭采信效力的正式法律意见。")
    sections.append("> 建议委托持牌律师复核确认后方可采信执行。\n")
    sections.append(f"`Report Generated by: ORCHESTRATOR v2.1 | {now}`\n")

    report_content = "\n".join(sections)

    # Write to file
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"  📄 风险报告已生成: {output_path}")

    return report_content
