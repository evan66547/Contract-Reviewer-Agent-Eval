"""Base agent class and LLM backend abstraction."""

import json
from dataclasses import dataclass


@dataclass
class LLMBackend:
    """Abstraction over OpenAI / Gemini API calls."""

    model: str = "gpt-4o"
    temperature: float = 0.1

    def call(self, system_prompt: str, user_prompt: str) -> dict:
        """Send a structured JSON request to the LLM and return parsed dict."""
        if "gemini" in self.model.lower():
            return self._call_gemini(system_prompt, user_prompt)
        return self._call_openai(system_prompt, user_prompt)

    # ── OpenAI ──────────────────────────────────────────

    def _call_openai(self, system_prompt: str, user_prompt: str) -> dict:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    # ── Gemini ──────────────────────────────────────────

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> dict:
        import google.generativeai as genai

        m = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=self.temperature,
            ),
        )
        response = m.generate_content(user_prompt)
        return json.loads(response.text)


class BaseAgent:
    """Base class for all review agents.

    Each subclass must define:
        name:          e.g. "Agent-1 合规审核"
        role:          e.g. "Compliance Agent"
        system_prompt: the full system prompt for this agent
        output_schema: a brief JSON schema description embedded in the user prompt
    """

    name: str = ""
    role: str = ""
    system_prompt: str = ""
    output_schema_description: str = ""

    def __init__(self, backend: LLMBackend):
        self.backend = backend

    def review(self, contract_text: str, context: dict | None = None) -> dict:
        """Run this agent's review on the contract text.

        Args:
            contract_text: The raw contract clause / full text.
            context: Optional dict with party_role, jurisdiction, amount, etc.

        Returns:
            Agent-specific structured findings dict.
        """
        ctx_block = ""
        if context:
            parts = []
            if context.get("party_role"):
                parts.append(f"己方立场：{context['party_role']}")
            if context.get("jurisdiction"):
                parts.append(f"适用法域：{context['jurisdiction']}")
            if context.get("amount"):
                parts.append(f"交易金额：{context['amount']}")
            if context.get("industry"):
                parts.append(f"行业：{context['industry']}")
            ctx_block = "\n".join(parts) + "\n\n"

        user_prompt = (
            f"{ctx_block}"
            f"请审查以下合同条款，并严格按照 JSON 格式输出：\n\n"
            f"【合同文本】\n{contract_text}\n\n"
            f"【输出格式要求】\n{self.output_schema_description}"
        )

        return self.backend.call(self.system_prompt, user_prompt)
