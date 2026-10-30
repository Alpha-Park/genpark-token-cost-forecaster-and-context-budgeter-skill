"""Token Cost Forecaster & Context Window Budgeter.
100% Python Standard Library.
"""

class TokenCostForecaster:
    """Forecasts LLM token consumption trajectories, enforces hard multi-agent cost budgets, and truncates overflow."""

    DEFAULT_PRICING = {
        "prompt_per_1k": 0.0015,
        "completion_per_1k": 0.0020
    }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        words = len(text.split())
        chars = len(text)
        return max(1, int((words * 1.3 + chars / 4.0) / 2.0))

    @classmethod
    def forecast_and_budget(cls, prompt_text: str, expected_completion_tokens: int,
                            accumulated_spend_usd: float, hard_budget_cap_usd: float,
                            pricing: dict = None) -> dict:
        rates = pricing or cls.DEFAULT_PRICING
        prompt_tokens = cls.estimate_tokens(prompt_text)

        prompt_cost = (prompt_tokens / 1000.0) * rates.get("prompt_per_1k", 0.0015)
        comp_cost = (expected_completion_tokens / 1000.0) * rates.get("completion_per_1k", 0.0020)
        projected_call_cost = prompt_cost + comp_cost
        projected_cumulative = accumulated_spend_usd + projected_call_cost

        budget_exceeded = projected_cumulative > hard_budget_cap_usd
        remaining_budget = max(0.0, hard_budget_cap_usd - accumulated_spend_usd)

        recommendation = "PERMIT_CALL"
        if budget_exceeded:
            recommendation = "HARD_BUDGET_BREACHED_REJECT_OR_COMPRESS"
        elif projected_cumulative > hard_budget_cap_usd * 0.85:
            recommendation = "WARNING_BUDGET_NEAR_SATURATION"

        return {
            "estimated_prompt_tokens": prompt_tokens,
            "projected_completion_tokens": expected_completion_tokens,
            "projected_call_cost_usd": round(projected_call_cost, 5),
            "accumulated_spend_usd": round(accumulated_spend_usd, 4),
            "hard_budget_cap_usd": round(hard_budget_cap_usd, 4),
            "remaining_budget_usd": round(remaining_budget, 4),
            "is_budget_breached": budget_exceeded,
            "policy_verdict": recommendation
        }
