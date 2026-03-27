"""ORCHESTRATOR: Central coordinator for multi-agent contract review.

Dispatches contract text to 6 independent agents in parallel,
collects results, runs quality audit, and produces unified output.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.base import LLMBackend
from agents.compliance import ComplianceAgent
from agents.dealmaker import DealMakerAgent
from agents.lifecycle import LifecycleAgent
from agents.negotiation import NegotiationAgent
from agents.proofreading import ProofreadingAgent
from agents.risk_quant import RiskQuantAgent

# ── Score extraction helpers ────────────────────────

SCORE_KEY_MAP = {
    "Agent-1 合规审核": "compliance_risk_score",
    "Agent-2 风险量化": "financial_risk_score",
    "Agent-3 谈判策略": "adversarial_risk_score",
    "Agent-4 生命周期": "performance_risk_score",
    "Agent-5 商业撮合": "commercial_risk_score",
}

DIMENSION_WEIGHTS = {
    "compliance_risk": 0.30,
    "financial_risk": 0.25,
    "adversarial_risk": 0.20,
    "performance_risk": 0.15,
    "commercial_risk": 0.10,
}


class Orchestrator:
    """Central orchestrator that dispatches, collects, audits, and reports."""

    def __init__(self, backend: LLMBackend, max_workers: int = 6):
        self.backend = backend
        self.max_workers = max_workers
        self.agents = [
            ComplianceAgent(backend),
            RiskQuantAgent(backend),
            NegotiationAgent(backend),
            LifecycleAgent(backend),
            DealMakerAgent(backend),
            ProofreadingAgent(backend),
        ]

    def run(self, contract_text: str, context: dict | None = None) -> dict:
        """Execute full multi-agent review pipeline.

        1. Dispatch all 6 agents in parallel
        2. Collect raw results
        3. Run quality audit
        4. Compute 5-dimension scores
        5. Generate unified output matching output_schema.json
        """
        print(f"\n{'=' * 60}")
        print("🧠 ORCHESTRATOR: Dispatching 6 agents in parallel...")
        print(f"{'=' * 60}")

        # ── Phase 1: Parallel dispatch ───────────────────
        raw_results = {}
        start = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            future_to_agent = {
                pool.submit(agent.review, contract_text, context): agent
                for agent in self.agents
            }
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    raw_results[agent.name] = result
                    print(f"  ✅ {agent.name} completed")
                except Exception as e:
                    print(f"  ❌ {agent.name} failed: {e}")
                    raw_results[agent.name] = {"error": str(e), "risk_items": []}

        elapsed = time.time() - start
        print(f"\n⏱  All agents finished in {elapsed:.1f}s")

        # ── Phase 2: Quality audit ───────────────────────
        print("\n📋 ORCHESTRATOR: Running quality audit...")
        agent_findings = self._build_agent_findings(raw_results)

        # ── Phase 3: Score computation ───────────────────
        risk_scores = self._compute_risk_scores(raw_results)

        # ── Phase 4: Extract cross-agent fields ──────────
        primary_vulnerability = self._extract_primary_vulnerability(raw_results)
        defense_plan_b = self._extract_plan_b(raw_results)
        el_estimation = self._extract_el(raw_results)
        legal_citations = self._extract_citations(raw_results)
        proofreading = self._extract_proofreading(raw_results)
        modifications = self._build_modification_suggestions(raw_results)

        # ── Phase 5: Determine overall risk level ────────
        composite = risk_scores.get("composite_index", 0)
        risk_level = self._composite_to_level(composite)

        # ── Phase 6: Assemble final output ───────────────
        output = {
            "risk_level": risk_level,
            "identified_vulnerability": primary_vulnerability,
            "clause_location": self._extract_clause_location(raw_results),
            "expected_loss_estimation": el_estimation,
            "legal_citations": legal_citations,
            "citation_verified": False,
            "confidence_degrade": "本次审查未接入 MCP/RAG 联网核验，法条引用基于模型记忆，需人工复核。",
            "defense_plan_b": defense_plan_b,
            "agent_findings": agent_findings,
            "risk_scores": risk_scores,
            "proofreading_findings": proofreading,
            "final_modification_suggestions": modifications,
        }

        print(
            f"\n🏁 ORCHESTRATOR: Review complete. Risk level: {risk_level} (composite: {composite:.1f})"
        )
        return output

    # ── Internal helpers ─────────────────────────────────

    def _build_agent_findings(self, raw: dict) -> list:
        """Build the agent_findings array with quality audit scores."""
        valid_sev = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        findings = []
        for agent in self.agents:
            result = raw.get(agent.name, {})
            risk_items = result.get("risk_items", [])
            # Normalize severity values to match schema enum
            for item in risk_items:
                if item.get("severity") not in valid_sev:
                    item["severity"] = "MEDIUM"

            # Quality audit: score each agent's output
            quality = self._audit_agent_quality(agent.name, result)

            findings.append(
                {
                    "agent_name": agent.name,
                    "agent_role": agent.role,
                    "quality_scores": quality,
                    "risk_items": risk_items,
                }
            )
        return findings

    def _audit_agent_quality(self, agent_name: str, result: dict) -> dict:
        """Score agent output quality across 4 dimensions (0-25 each)."""
        risk_items = result.get("risk_items", [])
        has_error = "error" in result

        if has_error or not risk_items:
            return {
                "citation_accuracy": 0,
                "coverage_completeness": 0,
                "logical_consistency": 0,
                "actionability": 0,
            }

        # Heuristic quality scoring based on output completeness
        has_legal_basis = sum(1 for r in risk_items if r.get("legal_basis"))
        has_recommendation = sum(1 for r in risk_items if r.get("recommendation"))
        has_finding = sum(
            1 for r in risk_items if r.get("finding") and len(r["finding"]) > 20
        )
        total = len(risk_items) or 1

        citation = min(25, int(25 * has_legal_basis / total))
        coverage = min(25, int(8 + len(risk_items) * 3))
        consistency = min(25, int(15 + has_finding / total * 10))
        actionability = min(25, int(25 * has_recommendation / total))

        return {
            "citation_accuracy": citation,
            "coverage_completeness": coverage,
            "logical_consistency": consistency,
            "actionability": actionability,
        }

    def _compute_risk_scores(self, raw: dict) -> dict:
        """Compute 5-dimension risk scores from agent outputs."""
        scores = {}
        score_map = {
            "compliance_risk": ("Agent-1 合规审核", "compliance_risk_score"),
            "financial_risk": ("Agent-2 风险量化", "financial_risk_score"),
            "adversarial_risk": ("Agent-3 谈判策略", "adversarial_risk_score"),
            "performance_risk": ("Agent-4 生命周期", "performance_risk_score"),
            "commercial_risk": ("Agent-5 商业撮合", "commercial_risk_score"),
        }

        for dim, (agent_name, key) in score_map.items():
            result = raw.get(agent_name, {})
            # Try to get the score from agent output; fall back to severity-based estimate
            score = result.get(key)
            if score is None:
                score = self._estimate_score_from_severity(result.get("risk_items", []))
            scores[dim] = min(100, max(0, int(score)))

        composite = sum(scores[d] * w for d, w in DIMENSION_WEIGHTS.items())
        scores["composite_index"] = round(composite, 1)
        return scores

    def _estimate_score_from_severity(self, risk_items: list) -> int:
        """Estimate a 0-100 risk score from severity counts when agent doesn't provide one."""
        if not risk_items:
            return 10  # minimal baseline
        severity_weight = {"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10, "LOW": 5}
        total = sum(
            severity_weight.get(r.get("severity", "LOW"), 5) for r in risk_items
        )
        return min(100, total)

    def _extract_primary_vulnerability(self, raw: dict) -> str:
        """Extract the most critical finding across all agents."""
        severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        worst = None
        for result in raw.values():
            for item in result.get("risk_items", []):
                rank = severity_rank.get(item.get("severity", "LOW"), 3)
                if worst is None or rank < worst[0]:
                    worst = (rank, item.get("finding", ""))
        return worst[1] if worst else "未发现显著漏洞"

    def _extract_plan_b(self, raw: dict) -> str:
        """Get Plan B from Agent-3."""
        a3 = raw.get("Agent-3 谈判策略", {})
        if a3.get("defense_plan_b"):
            return a3["defense_plan_b"]
        items = a3.get("risk_items", [])
        if items:
            return items[0].get("recommendation", "")
        return ""

    def _extract_el(self, raw: dict) -> dict:
        """Get EL estimation from Agent-2."""
        a2 = raw.get("Agent-2 风险量化", {})
        return a2.get(
            "expected_loss_estimation",
            {
                "amount_range": "需人工评估",
                "calculation_logic": "Agent-2 未返回量化数据",
            },
        )

    def _extract_citations(self, raw: dict) -> list:
        """Collect unique legal citations from all agents."""
        seen = set()
        citations = []
        for result in raw.values():
            for item in result.get("risk_items", []):
                basis = item.get("legal_basis", "")
                if basis and basis not in seen:
                    seen.add(basis)
                    citations.append({"law_name": basis, "article_number": ""})
        return citations[:10]  # cap at 10

    def _extract_clause_location(self, raw: dict) -> str:
        """Get the primary clause location from the most critical finding."""
        for result in raw.values():
            for item in result.get("risk_items", []):
                if item.get("severity") == "CRITICAL" and item.get("clause_location"):
                    return item["clause_location"]
        # fallback
        for result in raw.values():
            for item in result.get("risk_items", []):
                if item.get("clause_location"):
                    return item["clause_location"]
        return "N/A"

    _SEVERITY_MAP = {
        "CRITICAL": "FATAL_AMBIGUITY",
        "HIGH": "SERIOUS_DEFECT",
        "MEDIUM": "MINOR_FLAW",
        "LOW": "STYLE_SUGGESTION",
        "SAFE": "STYLE_SUGGESTION",
    }

    _DEFECT_TYPE_MAP = {
        "consistency": "inconsistency",
        "format": "style",
        "spelling": "typo",
        "formatting": "style",
        "reference": "numbering",
    }

    def _extract_proofreading(self, raw: dict) -> list:
        """Get proofreading findings from Agent-6, normalizing enum values."""
        a6 = raw.get("Agent-6 文书质检", {})
        findings = a6.get("proofreading_findings", [])
        valid_sev = {
            "FATAL_AMBIGUITY",
            "SERIOUS_DEFECT",
            "MINOR_FLAW",
            "STYLE_SUGGESTION",
        }
        valid_dt = {
            "typo",
            "grammar",
            "terminology",
            "punctuation",
            "inconsistency",
            "numbering",
            "style",
        }
        for f in findings:
            sev = f.get("severity", "")
            if sev not in valid_sev:
                f["severity"] = self._SEVERITY_MAP.get(sev, "MINOR_FLAW")
            dt = f.get("defect_type", "")
            if dt not in valid_dt:
                f["defect_type"] = self._DEFECT_TYPE_MAP.get(dt, "style")
        return findings

    def _build_modification_suggestions(self, raw: dict) -> list:
        """Build prioritized modification suggestions from all agent recommendations."""
        severity_priority = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        suggestions = []
        seen_locations = set()

        # Collect from all agents, deduplicate by clause_location
        all_items = []
        for result in raw.values():
            for item in result.get("risk_items", []):
                if item.get("recommendation"):
                    all_items.append(item)

        # Sort by severity
        all_items.sort(key=lambda x: severity_priority.get(x.get("severity", "LOW"), 4))

        for i, item in enumerate(all_items[:8], 1):  # cap at 8
            loc = item.get("clause_location", "")
            if loc in seen_locations:
                continue
            seen_locations.add(loc)
            suggestions.append(
                {
                    "priority": i,
                    "clause_ref": loc,
                    "current_text": "",
                    "suggested_text": item.get("recommendation", ""),
                    "rationale": item.get("finding", ""),
                    "legal_basis": item.get("legal_basis", ""),
                }
            )

        return suggestions

    @staticmethod
    def _composite_to_level(score: float) -> str:
        if score <= 20:
            return "SAFE"
        elif score <= 40:
            return "LOW"
        elif score <= 60:
            return "MEDIUM"
        elif score <= 80:
            return "HIGH"
        else:
            return "CRITICAL"
