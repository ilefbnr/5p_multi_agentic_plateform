import google.generativeai as genai
from utils.verif_rules import VERIFICATION_PROMPT, ENHANCEMENT_SUGGESTIONS_MAP, assess_verdict
from dotenv import load_dotenv
import os
load_dotenv()

GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")

genai.configure(api_key="GOOGLE_API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")

def evaluate_idea(idea: str):
    prompt = VERIFICATION_PROMPT.format(idea=idea)
    response = model.generate_content(prompt).text

    try:
        import json
        parsed = json.loads(response)
    except:
        return {
            "status": "error",
            "message": "Failed to parse model output",
            "raw": response
        }

    scores = {
        "relevance_score": parsed.get("relevance_score", 0),
        "Market Viability": parsed.get("market_viability", 0),
        "Competitive Edge": parsed.get("competitive_edge", 0),
        "Revenue Model": parsed.get("revenue_model", 0),
        "Team Capability": parsed.get("team_capability", 0)
    }

    verdict, weak_areas = assess_verdict(scores)

    suggestions = {}
    for area in weak_areas:
        suggestions[area] = ENHANCEMENT_SUGGESTIONS_MAP.get(area, [])

    return {
        "verdict": verdict,
        "scores": scores,
        "reason": parsed.get("reason", ""),
        "weak_areas": weak_areas,
        "suggestions": suggestions,
        "next": "continue" if verdict == "pass" else "revise"
    }

def __main__():
    idea = "A decentralized finance platform using AI to optimize lending rates"
    result = evaluate_idea(idea)
    print("Evaluation Result:")
    print(result)