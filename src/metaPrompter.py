"""
MetaPromptAgent: Generates strategic, force-specific instructions for DeepCrawlerAgent in AI/Data domains.
Uses Gemini 2.5 Flash via Google Generative AI API. Modular, scalable, and outputs prompt to ./prompts/prompt.txt.
"""
import os
import json
from typing import Dict
import google.generativeai as genai
from google.generativeai import GenerativeModel
from dotenv import load_dotenv

# Load environment and configure Gemini API key ONCE at module level
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment.")
genai.configure(api_key=api_key)

class MetaPromptAgent:
    """
    Generates a meta-prompt for the DeepCrawlerAgent based on an enhanced idea and Porter Force.
    Outputs the prompt to ./prompts/prompt.txt for downstream use.
    """
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-flash")
        self.prompt_template = (
     "You are the DeepCrawler Agent embedded within an agentic system that analyzes the AI and Data industry using Porter's Five Forces framework. "
     "Your task is to autonomously plan and execute a deep market and ecosystem crawl using tools like Tavily, Gemini, and MCP APIs. "
     "The pipeline should adapt based on the strategic context provided.\n\n"
     "Instructions:\n"
     "1. Based on the selected **Porter Force** below, formulate a data acquisition and crawling strategy.\n"
     "2. Use your understanding of the AI and Data industry to customize your queries, APIs, and exploration depth.\n"
     "3. Generate a list of highly targeted, force-specific keyword searches that enable in-depth exploration of the selected force.\n"
     "4. For each force, recommend the most relevant APIs and data sources to maximize insight.\n"
     "5. Return structured results including URLs, summaries, sentiment analysis, and relevance scores.\n\n"
     "Inputs:\n"
     "- **Porter Force**: {{porter_force}}\n"
     "- **Project Idea / Business Context**: {{project_idea}}\n\n"
     "Output Format:\n"
     "- Force-Specific Keyword Search Strategy: List of 10-20 highly targeted keyword searches for {{porter_force}}\n"
     "- Recommended APIs and Data Sources: List of APIs and sources best suited for {{porter_force}}\n"
     "- List of primary data sources used (Tavily, APIs, Gemini responses)\n"
     "- Top 10 relevant entities (e.g., companies, products, technologies, patents)\n"
     "- Link and metadata for each entity (e.g., title, summary, tags, confidence score)\n"
     "- Observations tied back to the force (e.g., how buyer power is increasing due to XYZ)\n"
     "- Confidence score for each observation\n"
     "- Suggestions for next best crawling targets (iterative learning)\n\n"
     "Behavior by Force:\n"
     "- *Buyer Power*: Identify key buyer segments, emerging use cases, price sensitivity, adoption trends. Generate keywords and APIs that reveal buyer leverage, negotiation, and influence.\n"
     "- *Supplier Power*: Scrape vendor ecosystems, toolchains, dependency graphs, and monopolies. Generate keywords and APIs that expose supplier concentration, switching costs, and critical dependencies.\n"
     "- *New Entrants*: Detect startups, product launches, hackathons, funding rounds. Generate keywords and APIs that surface new players, barriers to entry, and disruptive innovations.\n"
     "- *Substitutes*: Explore parallel industries, alternative tooling, competitive innovations. Generate keywords and APIs that highlight alternative solutions, cross-industry trends, and replacement risks.\n"
     "- *Rivalry*: Benchmark players, marketing strategies, talent wars, or acquisition trends. Generate keywords and APIs that reveal direct competition, market share battles, and rivalry intensity.\n\n"
     "Constraints:\n"
     "- You must respect API limits and respond in under 60 seconds.\n"
     "- Filter low-relevance results using cosine similarity or Gemini-generated summary validation.\n"
     "- Prioritize freshness (past 6–12 months) and regionally relevant data.\n\n"
     "Goal:\n"
     "Provide rich, dynamic, and actionable insights that help strategic analysts understand the force-specific landscape surrounding the project idea in the AI/Data space.\n\n"
     "Begin execution based on:\n"
     "- {{porter_force}}\n"
     "- {{project_idea}}"
        )
        self.output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'prompts', 'prompt.txt'))

    def generate_prompt(self, enhanced_idea: str, porter_force: str) -> str:
        """
        Generates the meta-prompt and writes it to ./prompts/prompt.txt.
        Returns the generated prompt string.
        """
        prompt = self.prompt_template.format(
            porter_force=porter_force,
            enhanced_idea=enhanced_idea
        )
        response = self.model.generate_content(prompt)
        # Try to parse as JSON, fallback to string
        try:
            instructions = json.loads(response.text)
            pretty_instructions = json.dumps(instructions, indent=2, ensure_ascii=False)
        except Exception:
            pretty_instructions = response.text.strip()
        # Write to prompt.txt
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(pretty_instructions)
        return pretty_instructions

if __name__ == "__main__":
    idea = input("Enter your enhanced business idea: ").strip()
    if not idea:
        idea = "AI-powered optimization platform for car rental fleet usage and predictive maintenance"
    porter_force = input("Enter Porter Force (e.g., Buyer Power): ").strip()
    if not porter_force:
        porter_force = "Buyer Power"
    agent = MetaPromptAgent()
    result = agent.generate_prompt(idea, porter_force)
    print("\nGenerated DeepCrawler Agent MetaPrompt (written to ./prompts/prompt.txt):\n")
    print(result)
