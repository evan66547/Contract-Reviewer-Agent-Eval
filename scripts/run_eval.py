#!/usr/bin/env python3
"""
Benchmark Evaluation Runner for Contract Reviewer Agent (v2.0)
Usage:
  Mock mode:  python scripts/run_eval.py --input_dir data/test_cases/ --schema schemas/output_schema.json
  Live mode:  python scripts/run_eval.py --live --model gpt-4o --input_dir data/test_cases/ --schema schemas/output_schema.json
"""

import os
import json
import glob
import argparse
import difflib
from jsonschema import validate, ValidationError

# ──────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# LLM Call (Mock + Live)
# ──────────────────────────────────────────────

def mock_llm_call(prompt, schema):
    """
    Returns a hard-coded mock response for offline testing.
    All cases will pass schema validation but receive low semantic scores.
    """
    return {
        "risk_level": "CRITICAL",
        "identified_vulnerability": "Simulated vulnerability analysis matching expected recall...",
        "clause_location": "(mock) N/A",
        "expected_loss_estimation": {
            "amount_range": "100W - 500W RMB",
            "calculation_logic": "Simulated EL logic strictly using 130% judicial limitation."
        },
        "legal_citations": [
            {"law_name": "《中华人民共和国民法典》", "article_number": "第五百八十四条"}
        ],
        "citation_verified": True,
        "confidence_degrade": "",
        "defense_plan_b": "Simulated mandatory Plan B insertion to block the vulnerability."
    }


def live_llm_call(prompt, schema, model="gpt-4o"):
    """
    Call a real LLM (OpenAI-compatible) to generate the contract review output.
    Requires OPENAI_API_KEY environment variable.
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("  ❌ openai package not installed. Run: pip install openai")
        raise

    client = OpenAI()
    system_prompt = (
        "你是一名具备15年经验的中国执业资深商业律师。"
        "请严格按照提供的 JSON Schema 格式输出合同审查结果。"
        "必须包含: risk_level, identified_vulnerability, clause_location, "
        "expected_loss_estimation, legal_citations, citation_verified, defense_plan_b。"
        "输出纯 JSON，不要包含 markdown 代码块标记。"
    )
    user_prompt = (
        f"请审查以下合同条款并按 JSON Schema 输出结构化风险分析：\n\n"
        f"合同条款：\n{prompt}\n\n"
        f"要求的输出 Schema：\n{json.dumps(schema, ensure_ascii=False, indent=2)}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


# ──────────────────────────────────────────────
# Semantic Scoring (Recall + Plan B Quality)
# ──────────────────────────────────────────────

def compute_recall_score(agent_vuln_text, expected_recalls):
    """
    Compute semantic recall score by checking keyword overlap
    between the agent's vulnerability output and expected recall points.
    Returns a score between 0.0 and 1.0.
    """
    if not expected_recalls or not agent_vuln_text:
        return 0.0

    hit_count = 0
    for recall_point in expected_recalls:
        # Extract key terms (4+ char segments) from the expected recall
        key_terms = [t for t in recall_point if len(t) >= 2]
        # Use SequenceMatcher for fuzzy substring matching
        ratio = difflib.SequenceMatcher(None, agent_vuln_text, recall_point).ratio()
        if ratio >= 0.25:  # Threshold: at least 25% overlap
            hit_count += 1

    return hit_count / len(expected_recalls)


def compute_plan_b_score(agent_plan_b, expected_plan_b):
    """
    Compute Plan B quality score using string similarity.
    Returns a score between 0.0 and 1.0.
    """
    if not agent_plan_b or not expected_plan_b:
        return 0.0
    return difflib.SequenceMatcher(None, agent_plan_b, expected_plan_b).ratio()


# ──────────────────────────────────────────────
# Case Evaluator
# ──────────────────────────────────────────────

def evaluate_case(case_data, schema, live=False, model="gpt-4o"):
    case_id = case_data.get('case_id', '?')
    case_name = case_data.get('name', 'Unknown')
    print(f"\n[{case_id}] Evaluating: {case_name}")

    contract_text = case_data.get("contract_snippet", "")

    # 1. Get Agent Output
    if live:
        print("  ⏳ Calling LLM...")
        agent_output = live_llm_call(contract_text, schema, model)
    else:
        agent_output = mock_llm_call(contract_text, schema)

    # 2. Schema Validation
    try:
        validate(instance=agent_output, schema=schema)
        print("  ✓ Schema Validation: PASSED")
        schema_pass = True
    except ValidationError as e:
        print(f"  ✗ Schema Validation: FAILED ({e.message})")
        schema_pass = False

    # 3. Semantic Recall Score
    expected_recalls = case_data.get("expected_vulnerability_recall", [])
    vuln_text = agent_output.get("identified_vulnerability", "")
    recall_score = compute_recall_score(vuln_text, expected_recalls)
    print(f"  📊 Recall Score: {recall_score*100:.0f}%")

    # 4. Plan B Quality Score
    expected_plan_b = case_data.get("expected_plan_b", "")
    agent_plan_b = agent_output.get("defense_plan_b", "")
    plan_b_score = compute_plan_b_score(agent_plan_b, expected_plan_b)
    print(f"  📊 Plan B Score: {plan_b_score*100:.0f}%")

    # 5. Weighted Final Score (aligned with Analysis_Report 4-tier model)
    #    Risk Recall 35% + EL Precision 25% (simplified) + Adversarial 30% + Lifecycle 10%
    final_score = (recall_score * 0.45) + (plan_b_score * 0.45) + (0.1 if schema_pass else 0.0)
    print(f"  🏆 Weighted Score: {final_score*100:.1f}%")

    return {
        "case_id": case_id,
        "name": case_name,
        "schema_pass": schema_pass,
        "recall_score": recall_score,
        "plan_b_score": plan_b_score,
        "final_score": final_score,
        "agent_output": agent_output
    }


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Run Benchmark Evaluation for Contract Reviewer Agent")
    parser.add_argument("--input_dir", default="data/test_cases/", help="Directory containing JSON test cases")
    parser.add_argument("--schema", default="schemas/output_schema.json", help="Path to JSON output schema")
    parser.add_argument("--live", action="store_true", help="Use real LLM API instead of mock responses")
    parser.add_argument("--model", default="gpt-4o", help="LLM model name (default: gpt-4o)")
    parser.add_argument("--output", default=None, help="Save detailed results to JSON file")
    args = parser.parse_args()

    schema = load_json(args.schema)
    test_files = sorted(glob.glob(os.path.join(args.input_dir, "*.json")))
    test_files = [f for f in test_files if not f.endswith("README.md")]

    if not test_files:
        print(f"No test cases found in {args.input_dir}")
        return

    mode_label = "🔴 LIVE" if args.live else "🟢 MOCK"
    print(f"Mode: {mode_label} | Model: {args.model}")
    print(f"Loaded {len(test_files)} test cases. Starting evaluation...\n")
    print("=" * 60)

    results = []
    for file in test_files:
        case_data = load_json(file)
        result = evaluate_case(case_data, schema, live=args.live, model=args.model)
        results.append(result)

    # Summary
    passed = sum(1 for r in results if r["schema_pass"])
    avg_recall = sum(r["recall_score"] for r in results) / len(results) * 100
    avg_plan_b = sum(r["plan_b_score"] for r in results) / len(results) * 100
    avg_final = sum(r["final_score"] for r in results) / len(results) * 100

    print("\n" + "=" * 60)
    print("📊 Benchmark Summary")
    print("=" * 60)
    print(f"  Total Cases     : {len(test_files)}")
    print(f"  Schema Passed   : {passed}/{len(test_files)}")
    print(f"  Avg Recall      : {avg_recall:.1f}%")
    print(f"  Avg Plan B      : {avg_plan_b:.1f}%")
    print(f"  Avg Final Score : {avg_final:.1f}%")
    print("=" * 60)

    # Save results
    if args.output:
        save_json(args.output, {
            "mode": "live" if args.live else "mock",
            "model": args.model,
            "total_cases": len(test_files),
            "avg_recall": round(avg_recall, 1),
            "avg_plan_b": round(avg_plan_b, 1),
            "avg_final_score": round(avg_final, 1),
            "cases": results
        })
        print(f"\n💾 Detailed results saved to: {args.output}")


if __name__ == "__main__":
    main()