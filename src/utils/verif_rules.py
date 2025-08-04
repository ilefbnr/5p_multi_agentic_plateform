VERIFICATION_PROMPT = """
You are a FinTech startup evaluator. Evaluate the following idea for relevance and business viability.

Idea: "{idea}"

Evaluate the idea across the following criteria:
1. Relevance to FinTech (AI in Finance, DeFi, InsurTech, WealthTech, etc.)
2. Market Viability: Demand, target market, growth potential.
3. Competitive Edge: What makes it stand out?
4. Revenue Model: Sustainable monetization approach?
5. Team Capability: Can this team deliver?

Output JSON with this structure:
{
  "relevance_score": int (0-10),
  "market_viability": int,
  "competitive_edge": int,
  "revenue_model": int,
  "team_capability": int,
  "verdict": "pass" | "fail",
  "reason": "short summary",
  "weak_areas": ["Market Viability", "Revenue Model"],
  "suggestions": {
    "Market Viability": ["Add specific target demographics"],
    "Revenue Model": ["Include revenue projections"]
  }
}
"""

ENHANCEMENT_SUGGESTIONS_MAP = {
    "Market Viability": [
        "Add specific target demographics",
        "Mention demand signals (e.g., search trends, user interviews)",
        "Cite real market gaps"
    ],
    "Competitive Edge": [
        "Define unique value proposition",
        "Benchmark against known competitors"
    ],
    "Revenue Model": [
        "Include revenue projections",
        "Describe pricing strategy",
        "Mention key partnerships"
    ],
    "Team Capability": [
        "Outline team background",
        "Describe technical skills or domain expertise"
    ],
    "Relevance to FinTech": [
        "Align with FinTech use cases like lending, payments, or compliance",
        "Mention specific financial technologies used"
    ]
}
def assess_verdict(scores: dict, threshold: int = 6):
    weak_areas = []
    for k, v in scores.items():
        if v < threshold:
            weak_areas.append(k)
    return "fail" if weak_areas or scores["relevance_score"] < threshold else "pass", weak_areas
