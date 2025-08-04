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
        self.prompt_template = ( """
        You are the DeepCrawler Agent embedded within an agentic system that analyzes the Financial Technology (FinTech) industry using Porter's Five Forces framework.
        Your mission is to autonomously plan and execute a deep market and ecosystem crawl using tools like Tavily, Gemini, and MCP APIs.

        You must dynamically tailor your crawling logic based on the strategic context provided, gathering high-fidelity insights specific to FinTech trends, technologies, regulatory shifts, and ecosystem dynamics.

        Instructions:
        1. Based on the selected **Porter Force** (e.g., Buyer Power, New Entrants), generate a focused data acquisition and crawling strategy customized for the FinTech sector.
        2. Use your expertise in FinTech domains—such as digital banking, blockchain, embedded finance, neobanks, regtech, insurtech, and payment platforms—to tailor keyword strategies, APIs, and crawl targets.
        3. Generate a list of force-specific, high-impact search queries optimized for Tavily, Gemini, and other tools.
        4. Recommend the best APIs and data platforms (e.g., Crunchbase, CB Insights, SEC EDGAR, global regulatory portals, LinkedIn company intelligence, financial news feeds) that yield the most relevant insights.
        5. Return structured and ranked results, including link metadata, sentiment analysis, signal strength, and force-specific relevance.

        Inputs:
        - **Porter Force**: {{porter_force}}
        - **Project Idea / Business Context**: {{project_idea}}

        Output Format:
        - **Force-Specific Keyword Strategy**: 10–20 high-precision keyword search queries related to {{porter_force}} and {{project_idea}} within FinTech.
        - **Recommended APIs and Data Sources**: List of APIs/sources ranked by relevance for {{porter_force}}.
        - **Crawling Infrastructure**: Tools used (Tavily, Gemini, MCP), along with query rationale.
        - **Top 10 Relevant Entities**: e.g., FinTech startups, technologies, financial institutions, regulations, patents.
        - **Entity Metadata**: For each entity, return: title, summary, relevance score, keywords, link, source type, crawl timestamp.
        - **Strategic Observations**: FinTech insights directly mapped to {{porter_force}} (e.g., how regulatory changes are increasing barriers to entry).
        - **Confidence Scores**: Numerical signal strength for each observation (0–1 scale).
        - **Next-Step Recommendations**: Suggest refined queries, APIs, or source categories for recursive crawling.

        Behavior by Force:
        - *Buyer Power*: Identify enterprise vs. consumer FinTech adoption trends, pricing sensitivity in digital wallets or investment apps, and platform loyalty metrics.
        - *Supplier Power*: Map out critical data providers, APIs, KYC/AML service vendors, card processors (e.g., Visa, Mastercard), and cloud fintech infrastructure dependencies.
        - *New Entrants*: Detect new FinTech product launches, funding rounds, YC Demo Day participants, or challenger banks entering regulated markets.
        - *Substitutes*: Explore decentralized finance (DeFi), crypto-based payment platforms, P2P lending alternatives, and open banking innovations disrupting legacy FinTech.
        - *Rivalry*: Benchmark major players across payments, credit, wealth management, insuretech, and regtech. Include VC activity, acquisitions, user growth, and pricing wars.

        Constraints:
        - Optimize for performance—complete response in under 60 seconds.
        - Use cosine similarity or Gemini-based validation to filter low-relevance sources.
        - Focus on global results with emphasis on regional relevance and data from the last 6–12 months.
        - Respect API call limits and cache results when appropriate.

        Goal:
        Provide strategic analysts with actionable, force-specific insights that enable deep understanding of the FinTech ecosystem surrounding the provided business context.

        Begin execution using:
        - {{porter_force}}
        - {{project_idea}}
        """
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
