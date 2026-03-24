#!/usr/bin/env python3
"""
Benchmark Evaluation Runner for Contract Reviewer Agent (v2.0)
【LLM-as-a-Judge Enhanced Edition】
Usage:
  Mock mode (Pipeline Check): python scripts/run_eval.py --input_dir data/test_cases/
  Live mode (Real Score):     python scripts/run_eval.py --live --model gpt-4o --output results/report.json
"""

import os
import json
import glob
import argparse
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
            "calculation_logic": "Mock Logic"
        },
        "legal_citations": [{"law_name": "民法典", "article_number": "未知"}],
        "citation_verified": True,
        "confidence_degrade": "",
        "defense_plan_b": "Mock Plan B"
    }

def live_llm_call(prompt, schema, model="gpt-4o"):
    """Call the Generation LLM to review the contract."""
    from openai import OpenAI
    client = OpenAI()
    system_prompt = (
        "你是一名具备15年经验的中国执业资深商业律师。请严格按照JSON Schema审查合同。"
        "必须包含: risk_level, identified_vulnerability, clause_location, expected_loss_estimation, legal_citations, citation_verified, defense_plan_b。"
    )
    user_prompt = f"合同条款：\n{prompt}\n\n要求的输出 Schema：\n{json.dumps(schema, ensure_ascii=False)}"
    
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

def llm_as_a_judge(agent_output, case_data, model="gpt-4o"):
    """
    Use an LLM to blindly judge the semantic quality of the agent's output against the Ground Truth.
    This replaces the flawed difflib string-matching approach and truly evaluates "Plan B" effectiveness.
    """
    from openai import OpenAI
    client = OpenAI()
    
    judge_prompt = f"""
    你是独立客观的第三方『法律基准测试裁判』。请评估受测 Agent 出具的风控报告是否真正解决了基准库(Ground Truth)中的问题。
    请你从 0 到 100 分独立给出四个维度的打分，并严格返回 JSON 格式：
    {{"recall_score": int, "el_precision_score": int, "adversarial_score": int, "lifecycle_score": int}}

    【基准答案 (Ground Truth)】
    期待发现的漏洞: {case_data.get('expected_vulnerability_recall', [])}
    期待的 Plan B 防御方向: {case_data.get('expected_plan_b', '')}

    【受测 Agent 输出】
    识别到的漏洞: {agent_output.get('identified_vulnerability', '')}
    预期损失估算逻辑: {json.dumps(agent_output.get('expected_loss_estimation', dict()), ensure_ascii=False)}
    给出的 Plan B: {agent_output.get('defense_plan_b', '')}

    【打分规则】
    1. recall_score (漏洞召回): Agent 是否准确识别了基准答案预期的业务/法律致命漏洞？(哪怕表述不同，语义相符即可满分)
    2. el_precision_score (损失估算精度): Agent 的损失估算逻辑是否客观？是否有天价违约金调减意识？
    3. adversarial_score (抗对抗防御/Plan B): Agent 写的条款是否比基准答案规定的方向更强、更滴水不漏？不要受限于文字相似度，写得越狠越完美分数越高。
    4. lifecycle_score (生命周期): 是否指出了隐藏的期限黑洞？如无涉及但总体优秀也可酌情给高分。
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# ──────────────────────────────────────────────
# Case Evaluator
# ──────────────────────────────────────────────

def evaluate_case(case_data, schema, live=False, model="gpt-4o"):
    case_id = case_data.get('case_id', '?')
    case_name = case_data.get('name', 'Unknown')
    print(f"\n[{case_id}] Evaluating: {case_name}")

    contract_text = case_data.get("contract_snippet", "")

    # 1. Output Generation
    if live:
        print("  ⏳ Calling Generation LLM...")
        agent_output = live_llm_call(contract_text, schema, model)
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
        judge_scores = llm_as_a_judge(agent_output, case_data, model="gpt-4o") # Always use strong model as judge
        r_score = judge_scores.get("recall_score", 0)
        e_score = judge_scores.get("el_precision_score", 0)
        a_score = judge_scores.get("adversarial_score", 0)
        l_score = judge_scores.get("lifecycle_score", 0)
        
        # Exact Weighting from the Documentation
        final_score = (r_score * 0.35) + (e_score * 0.25) + (a_score * 0.30) + (l_score * 0.10)
        
        print(f"  📊 Recall (35%):  {r_score}/100")
        print(f"  📊 EL Prec (25%): {e_score}/100")
        print(f"  📊 Plan B (30%):  {a_score}/100")
        print(f"  📊 Lifecyc (10%): {l_score}/100")
        print(f"  🏆 Weighted Final: {final_score:.1f}/100")
    else:
        print("  ⚠️ MOCK MODE: Bypass semantic scoring. (Requires --live for real benchmarking)")
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
            "final": final_score
        },
        "agent_output": agent_output
    }

# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data/test_cases/")
    parser.add_argument("--schema", default="schemas/output_schema.json")
    parser.add_argument("--live", action="store_true", help="Use real API to generate & LLM-as-a-Judge to score")
    parser.add_argument("--model", default="gpt-4o")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    schema = load_json(args.schema)
    test_files = sorted(glob.glob(os.path.join(args.input_dir, "*.json")))
    test_files = [f for f in test_files if not f.endswith("README.md")]

    if not args.live:
        print("\n" + "!"*60)
        print("🚨 ATTENTION: Running in MOCK Mode 🚨")
        print("Mock mode ONLY validates the execution pipeline and JSON schema.")
        print("SCORES WILL BE 0. To evaluate AI performance, you MUST use the --live flag.")
        print("!"*60 + "\n")

    results = []
    for file in test_files:
        case_data = load_json(file)
        result = evaluate_case(case_data, schema, live=args.live, model=args.model)
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

if __name__ == "__main__":
    main()