"""
Module for extracting and cleaning HTML/text content from URLs.
"""

import requests
from bs4 import BeautifulSoup

def extract_content(url: str) -> str:
    """
    Fetch and clean the main textual content from a URL.
    Returns cleaned text.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        # Extract visible text
        text = ' '.join(soup.stripped_strings)
        # Optionally truncate to avoid LLM context overflow
        return text[:8000]
    except Exception as e:
        return f"Failed to extract content: {e}"