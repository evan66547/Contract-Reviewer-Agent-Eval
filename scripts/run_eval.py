#!/usr/bin/env python3
"""
Benchmark Evaluation Runner for Contract Reviewer Agent (v2.0)
【LLM-as-a-Judge Enhanced Edition】
Usage:
  Mock mode (Pipeline Check): python scripts/run_eval.py --input_dir data/test_cases/
  Live mode (Real Score):     python scripts/run_eval.py --live --model gpt-4o --output results/report.json
"""

import argparse
import glob
import json
import os
import re
import sys

from jsonschema import ValidationError, validate

# Add project root to path for agents package
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.join(_SCRIPT_DIR, "..")
sys.path.insert(0, _PROJECT_ROOT)
os.chdir(_PROJECT_ROOT)

# ──────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────


def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks and markdown code fences from reasoning-model outputs."""
    text = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()
    # Strip ```json ... ``` code fences
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, flags=re.DOTALL)
    if m:
        text = m.group(1).strip()
    return text


def _robust_json_loads(text: str) -> dict:
    """Parse JSON with fallbacks for common LLM output issues."""
    text = _strip_thinking(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    depth = 0
    start = text.find("{")
    if start >= 0:
        for i, c in enumerate(text[start:], start):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
    return json.loads(text)


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# LLM Calls (Generator & Judge)
# ──────────────────────────────────────────────


def mock_llm_call(prompt, schema):
    """
    Returns a fake schema-compliant response.
    WARNING: This does NOT represent agent performance. Used for CI/CD workflow testing ONLY.
    """
    return {
        "risk_level": "CRITICAL",
        "identified_vulnerability": "Mock Vulnerability... (No real semantic meaning)",
        "clause_location": "N/A",
        "expected_loss_estimation": {
            "amount_range": "Mock Range",
            "calculation_logic": "Mock Logic",
        },
        "legal_citations": [{"law_name": "民法典", "article_number": "未知"}],
        "citation_verified": True,
        "confidence_degrade": "",
        "defense_plan_b": "Mock Plan B",
        # ── ORCHESTRATOR 报告收束 Mock 数据 ──
        "agent_findings": [
            {
                "agent_name": "Agent-1 合规审核",
                "agent_role": "Compliance Agent",
                "quality_scores": {
                    "citation_accuracy": 22,
                    "coverage_completeness": 20,
                    "logical_consistency": 23,
                    "actionability": 21,
                },
                "risk_items": [
                    {
                        "risk_id": "R-001",
                        "risk_tag": "#强制性规范违反",
                        "severity": "CRITICAL",
                        "clause_location": "违约责任条款",
                        "finding": "[Mock] 违约金限额与实际损失填平原则冲突",
                        "legal_basis": "《民法典》第584条",
                        "recommendation": "[Mock] 增加根本违约例外排除条款",
                    }
                ],
            },
            {
                "agent_name": "Agent-2 风险量化",
                "agent_role": "Risk Quant Agent",
                "quality_scores": {
                    "citation_accuracy": 20,
                    "coverage_completeness": 21,
                    "logical_consistency": 22,
                    "actionability": 19,
                },
                "risk_items": [
                    {
                        "risk_id": "R-002",
                        "risk_tag": "#违约金过高",
                        "severity": "HIGH",
                        "clause_location": "第8条违约金",
                        "finding": "[Mock] 账面违约金面临司法调减风险",
                        "legal_basis": "司法解释130%规则",
                        "recommendation": "[Mock] 将EL上限压至实际损失130%",
                    }
                ],
            },
            {
                "agent_name": "Agent-3 谈判策略",
                "agent_role": "Negotiation Agent",
                "quality_scores": {
                    "citation_accuracy": 21,
                    "coverage_completeness": 22,
                    "logical_consistency": 20,
                    "actionability": 23,
                },
                "risk_items": [
                    {
                        "risk_id": "R-003",
                        "risk_tag": "#Plan B防御漏洞",
                        "severity": "MEDIUM",
                        "clause_location": "争议解决条款",
                        "finding": "[Mock] 替代条款存在语义歧义攻击面",
                        "legal_basis": "合同解释原则",
                        "recommendation": "[Mock] 收紧定义条款，消除歧义空间",
                    }
                ],
            },
            {
                "agent_name": "Agent-4 生命周期",
                "agent_role": "Lifecycle Agent",
                "quality_scores": {
                    "citation_accuracy": 18,
                    "coverage_completeness": 19,
                    "logical_consistency": 21,
                    "actionability": 20,
                },
                "risk_items": [
                    {
                        "risk_id": "R-004",
                        "risk_tag": "#期限黑洞",
                        "severity": "HIGH",
                        "clause_location": "验收条款",
                        "finding": "[Mock] 验收期限未设上限，付款条件无法成就",
                        "legal_basis": "《民法典》第159条",
                        "recommendation": "[Mock] 设置15日默示验收期",
                    }
                ],
            },
            {
                "agent_name": "Agent-5 商业撮合",
                "agent_role": "Deal-Maker Agent",
                "quality_scores": {
                    "citation_accuracy": 19,
                    "coverage_completeness": 20,
                    "logical_consistency": 22,
                    "actionability": 22,
                },
                "risk_items": [
                    {
                        "risk_id": "R-005",
                        "risk_tag": "#交易摩擦",
                        "severity": "LOW",
                        "clause_location": "整体条款",
                        "finding": "[Mock] 法务条款过严可能增加谈判摩擦",
                        "legal_basis": "商业惯例",
                        "recommendation": "[Mock] 提供分期对赌折中方案",
                    }
                ],
            },
            {
                "agent_name": "Agent-6 文书质检",
                "agent_role": "Legal Proofreading Agent",
                "quality_scores": {
                    "citation_accuracy": 23,
                    "coverage_completeness": 22,
                    "logical_consistency": 24,
                    "actionability": 21,
                },
                "risk_items": [
                    {
                        "risk_id": "R-006",
                        "risk_tag": "#术语误用",
                        "severity": "HIGH",
                        "clause_location": "第3条 订金条款",
                        "finding": "[Mock] 合同中将『定金』写作『订金』，法律效力截然不同",
                        "legal_basis": "《民法典》第586条 定金罚则",
                        "recommendation": "[Mock] 将所有『订金』替换为『定金』并明确适用定金罚则",
                    }
                ],
            },
        ],
        "risk_scores": {
            "compliance_risk": 75,
            "financial_risk": 60,
            "adversarial_risk": 45,
            "performance_risk": 55,
            "commercial_risk": 30,
            "composite_index": 75 * 0.30
            + 60 * 0.25
            + 45 * 0.20
            + 55 * 0.15
            + 30 * 0.10,
        },
        "proofreading_findings": [
            {
                "defect_id": "PF-001",
                "defect_type": "terminology",
                "severity": "FATAL_AMBIGUITY",
                "location": "第3条",
                "original_text": "[Mock] 乙方应在签约时支付订金人民币伍拾万元整",
                "issue_description": "[Mock] 『订金』与『定金』法律效力不同：定金适用双倍返还罚则，订金仅为预付款可退",
                "correction": "[Mock] 替换为『定金』并添加『适用《民法典》第586条定金罚则』",
            },
            {
                "defect_id": "PF-002",
                "defect_type": "grammar",
                "severity": "SERIOUS_DEFECT",
                "location": "第5条",
                "original_text": "[Mock] 如甲方未能在规定期限内完成验收并且乙方有权解除合同",
                "issue_description": "[Mock] 句子缺少主语转换连词，『并且』前后主语暂换导致逻辑关系不清",
                "correction": "[Mock] 改为『如甲方未能在规定期限内完成验收，则乙方有权解除合同』",
            },
        ],
        "final_modification_suggestions": [
            {
                "priority": 1,
                "clause_ref": "第8条 违约责任",
                "current_text": "[Mock] 违约金总额不超过合同总额20%",
                "suggested_text": "[Mock] 前述违约金限额不适用于根本违约、商业秘密泄露或知识产权侵权造成的实际损失",
                "rationale": "[Mock] 填平原则保护己方实际损失求偿权",
                "legal_basis": "《民法典》第584条",
            },
            {
                "priority": 2,
                "clause_ref": "第5条 验收",
                "current_text": "[Mock] 甲方应及时组织验收",
                "suggested_text": "[Mock] 甲方应在交付后15个工作日内完成验收，逾期未提出异议视为验收合格",
                "rationale": "[Mock] 设置明确期限防止付款条件成就障碍",
                "legal_basis": "《民法典》第159条",
            },
        ],
    }


def live_llm_call(prompt, schema, model="gpt-4o", base_url=None, api_key=None):
    """Call the Generation LLM to review the contract."""
    system_prompt = (
        "你是一名具备15年经验的中国执业资深商业律师。请严格按照JSON Schema审查合同。"
        "必须包含: risk_level, identified_vulnerability, clause_location, expected_loss_estimation, legal_citations, citation_verified, defense_plan_b。"
    )
    user_prompt = f"合同条款：\n{prompt}\n\n要求的输出 Schema：\n{json.dumps(schema, ensure_ascii=False)}"

    if "gemini" in model.lower():
        import google.generativeai as genai

        m = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        response = m.generate_content(user_prompt)
        return json.loads(response.text)
    else:
        from openai import OpenAI

        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        if api_key:
            kwargs["api_key"] = api_key
        client = OpenAI(**kwargs)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return _robust_json_loads(response.choices[0].message.content)


def llm_as_a_judge(
    agent_output, case_data, model="gpt-4o", base_url=None, api_key=None
):
    """
    Use an LLM to blindly judge the semantic quality of the agent's output against the Ground Truth.
    This replaces the flawed difflib string-matching approach and truly evaluates "Plan B" effectiveness.
    """
    judge_prompt = f"""
    你是独立客观的第三方『法律基准测试裁判』。请评估受测 Agent 出具的风控报告是否真正解决了基准库(Ground Truth)中的问题。
    请你从 0 到 100 分独立给出四个维度的打分，并严格返回 JSON 格式：
    {{"recall_score": int, "el_precision_score": int, "adversarial_score": int, "lifecycle_score": int}}

    【基准答案 (Ground Truth)】
    期待发现的漏洞: {case_data.get("expected_vulnerability_recall", [])}
    期待的 Plan B 防御方向: {case_data.get("expected_plan_b", "")}

    【受测 Agent 输出】
    识别到的漏洞: {agent_output.get("identified_vulnerability", "")}
    预期损失估算逻辑: {json.dumps(agent_output.get("expected_loss_estimation", dict()), ensure_ascii=False)}
    给出的 Plan B: {agent_output.get("defense_plan_b", "")}

    【打分规则】
    1. recall_score (漏洞召回): Agent 是否准确识别了基准答案预期的业务/法律致命漏洞？(哪怕表述不同，语义相符即可满分)
    2. el_precision_score (损失估算精度): Agent 的损失估算逻辑是否客观？是否有天价违约金调减意识？
    3. adversarial_score (抗对抗防御/Plan B): Agent 写的条款是否比基准答案规定的方向更强、更滴水不漏？不要受限于文字相似度，写得越狠越完美分数越高。
    4. lifecycle_score (生命周期): 是否指出了隐藏的期限黑洞？如无涉及但总体优秀也可酌情给高分。
    """

    if "gemini" in model.lower():
        import google.generativeai as genai

        m = genai.GenerativeModel(
            model_name=model,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        response = m.generate_content(judge_prompt)
        return json.loads(response.text)
    else:
        from openai import OpenAI

        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        if api_key:
            kwargs["api_key"] = api_key
        client = OpenAI(**kwargs)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return _robust_json_loads(response.choices[0].message.content)


# ──────────────────────────────────────────────
# Case Evaluator
# ──────────────────────────────────────────────


def evaluate_case(
    case_data,
    schema,
    live=False,
    model="gpt-4o",
    orchestrate=False,
    base_url=None,
    api_key=None,
):
    case_id = case_data.get("case_id", "?")
    case_name = case_data.get("name", "Unknown")
    print(f"\n[{case_id}] Evaluating: {case_name}")

    contract_text = case_data.get("contract_snippet", "")

    # 1. Output Generation
    if orchestrate and live:
        # ── TRUE MULTI-AGENT ORCHESTRATION ──
        from agents.base import LLMBackend
        from agents.orchestrator import Orchestrator

        print("  🧠 Running ORCHESTRATOR + 6-Agent parallel pipeline...")
        backend = LLMBackend(
            model=model, temperature=0.1, base_url=base_url, api_key=api_key
        )
        orc = Orchestrator(backend, max_workers=6)
        agent_output = orc.run(contract_text)
    elif live:
        print("  ⏳ Calling Generation LLM (single-call mode)...")
        agent_output = live_llm_call(
            contract_text, schema, model, base_url=base_url, api_key=api_key
        )
    else:
        agent_output = mock_llm_call(contract_text, schema)

    # 2. Schema Validation (Pipeline Integrity)
    try:
        validate(instance=agent_output, schema=schema)
        print("  ✓ Schema Validation: PASSED")
        schema_pass = True
    except ValidationError as e:
        print(f"  ✗ Schema Validation: FAILED ({e.message})")
        schema_pass = False

    # 3. LLM-as-a-Judge Scoring
    if live:
        print("  ⚖️ Calling Judge LLM for Semantic Evaluation...")
        judge_scores = llm_as_a_judge(
            agent_output, case_data, model=model, base_url=base_url, api_key=api_key
        )
        r_score = judge_scores.get("recall_score", 0)
        e_score = judge_scores.get("el_precision_score", 0)
        a_score = judge_scores.get("adversarial_score", 0)
        l_score = judge_scores.get("lifecycle_score", 0)

        # Exact Weighting from the Documentation
        final_score = (
            (r_score * 0.35) + (e_score * 0.25) + (a_score * 0.30) + (l_score * 0.10)
        )

        print(f"  📊 Recall (35%):  {r_score}/100")
        print(f"  📊 EL Prec (25%): {e_score}/100")
        print(f"  📊 Plan B (30%):  {a_score}/100")
        print(f"  📊 Lifecyc (10%): {l_score}/100")
        print(f"  🏆 Weighted Final: {final_score:.1f}/100")
    else:
        print(
            "  ⚠️ MOCK MODE: Bypass semantic scoring. (Requires --live for real benchmarking)"
        )
        r_score, e_score, a_score, l_score, final_score = 0, 0, 0, 0, 0

    return {
        "case_id": case_id,
        "name": case_name,
        "schema_pass": schema_pass,
        "scores": {
            "recall": r_score,
            "el_precision": e_score,
            "adversarial": a_score,
            "lifecycle": l_score,
            "final": final_score,
        },
        "agent_output": agent_output,
    }


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data/test_cases/")
    parser.add_argument("--schema", default="schemas/output_schema.json")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use real API to generate & LLM-as-a-Judge to score",
    )
    parser.add_argument(
        "--orchestrate",
        action="store_true",
        help="Enable true multi-agent orchestration (6 parallel agents)",
    )
    parser.add_argument("--model", default="gpt-4o")
    parser.add_argument(
        "--base-url", default=None, help="Custom OpenAI-compatible API base URL"
    )
    parser.add_argument(
        "--api-key", default=None, help="Custom API key (overrides OPENAI_API_KEY env)"
    )
    parser.add_argument("--output", default=None)
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate Markdown risk report via ORCHESTRATOR",
    )
    parser.add_argument(
        "--report_output", default=None, help="Custom path for the risk report"
    )
    args = parser.parse_args()

    schema = load_json(args.schema)
    test_files = sorted(glob.glob(os.path.join(args.input_dir, "*.json")))
    test_files = [f for f in test_files if not f.endswith("README.md")]

    if args.orchestrate and not args.live:
        print("\n⚠️  --orchestrate requires --live. Falling back to mock mode.\n")

    if not args.live:
        print("\n" + "!" * 60)
        print("🚨 ATTENTION: Running in MOCK Mode 🚨")
        print("Mock mode ONLY validates the execution pipeline and JSON schema.")
        print(
            "SCORES WILL BE 0. To evaluate AI performance, you MUST use the --live flag."
        )
        print("!" * 60 + "\n")
    elif args.orchestrate:
        print("\n" + "=" * 60)
        print("🧠 MULTI-AGENT ORCHESTRATION MODE ENABLED")
        print(f"   Model: {args.model} | Workers: 6 | Pipeline: ORCHESTRATOR + 6-Agent")
        print("=" * 60 + "\n")

    results = []
    for file in test_files:
        case_data = load_json(file)
        result = evaluate_case(
            case_data,
            schema,
            live=args.live,
            model=args.model,
            orchestrate=args.orchestrate,
            base_url=args.base_url,
            api_key=args.api_key,
        )
        results.append(result)

    passed = sum(1 for r in results if r["schema_pass"])
    if args.live:
        avg_r = sum(r["scores"]["recall"] for r in results) / len(results)
        avg_e = sum(r["scores"]["el_precision"] for r in results) / len(results)
        avg_a = sum(r["scores"]["adversarial"] for r in results) / len(results)
        avg_l = sum(r["scores"]["lifecycle"] for r in results) / len(results)
        avg_final = sum(r["scores"]["final"] for r in results) / len(results)

        print("\n" + "=" * 60)
        print("📊 Benchmark Summary [LLM-as-a-Judge Evaluation]")
        print("=" * 60)
        print(f"  Schema Valid    : {passed}/{len(test_files)}")
        print(f"  [35%] Recall    : {avg_r:.1f}")
        print(f"  [25%] EL Precis : {avg_e:.1f}")
        print(f"  [30%] Def/PlanB : {avg_a:.1f}")
        print(f"  [10%] Lifecycle : {avg_l:.1f}")
        print(f"  🏆 Overall Score : {avg_final:.1f}/100")
        print("=" * 60)

    if args.output:
        save_json(args.output, results)

    # ── ORCHESTRATOR: 报告收束 ──
    if args.report:
        from datetime import datetime

        from report_generator import generate_risk_report

        report_path = (
            args.report_output
            or f"results/risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        print("\n📄 ORCHESTRATOR: 正在生成风险报告...")
        generate_risk_report(results, output_path=report_path)
        print(f"✅ 风险报告已输出至: {report_path}")


if __name__ == "__main__":
    main()
