"""
SmartCleaner Agent: Cleans and enriches all JSON files in ./data/raw, saving cleaned results to ./data/clean.
No external config files required. Designed for B2B AI lead intelligence pipelines.
"""
import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import json
import phonenumbers
import spacy

class SmartCleanerAgent:
    """
    Cleans, normalizes, deduplicates, and enriches raw lead data for B2B AI lead intelligence.
    Iterates over all JSON files in ./data/raw and saves cleaned output to ./data/clean.
    """
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            print(f"spaCy model '{spacy_model}' not found. Entity extraction disabled.")
            self.nlp = None
        self.raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
        self.clean_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'clean'))
        os.makedirs(self.clean_dir, exist_ok=True)

    def clean_lead(self, raw_lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        lead = {
            "id": str(uuid.uuid4()),
            "full_name": self._clean_str(raw_lead.get("full_name")),
            "first_name": None,
            "last_name": None,
            "email": self._normalize_email(raw_lead.get("email")),
            "phone": self._normalize_phone(raw_lead.get("phone")),
            "company": self._clean_str(raw_lead.get("company")),
            "job_title": self._clean_str(raw_lead.get("job_title")),
            "address": {
                "street": self._clean_str(raw_lead.get("address", {}).get("street")),
                "city": self._clean_str(raw_lead.get("address", {}).get("city")),
                "postal_code": self._clean_str(raw_lead.get("address", {}).get("postal_code")),
                "country": self._clean_str(raw_lead.get("address", {}).get("country")),
            },
            "linkedin_url": self._normalize_url(raw_lead.get("linkedin_url")),
            "website_url": self._normalize_url(raw_lead.get("website_url")),
            "industry": self._clean_str(raw_lead.get("industry")),
            "company_size": self._clean_str(raw_lead.get("company_size")),
            "last_updated": datetime.now().isoformat() + "Z",
            "source": raw_lead.get("source", "Unknown")
        }
        if lead["full_name"]:
            parts = lead["full_name"].split(maxsplit=1)
            if len(parts) > 0:
                lead["first_name"] = parts[0].title()
            if len(parts) > 1:
                lead["last_name"] = parts[1].title()
        self._enrich_company(lead)
        if lead["job_title"] and self.nlp:
            lead["entities"] = self._extract_entities(lead["job_title"])
        return lead

    def clean_dataset(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.clean_lead(lead) for lead in leads if self.clean_lead(lead)]

    def deduplicate(self, leads: List[Dict[str, Any]], key_fields: List[str] = None) -> List[Dict[str, Any]]:
        if key_fields is None:
            key_fields = ["email"]
        seen = set()
        deduped = []
        for lead in leads:
            key = "_".join(str(lead.get(f, '')).lower() for f in key_fields)
            if key and key not in seen:
                deduped.append(lead)
                seen.add(key)
        return deduped

    def _clean_str(self, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s.,\-@:/]', '', text)
        return text if text else None

    def _normalize_email(self, email: Optional[str]) -> Optional[str]:
        if not email:
            return None
        email = email.lower().strip()
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return email
        return None

    def _normalize_phone(self, phone: Optional[str], country_code: str = "US") -> Optional[str]:
        if not phone:
            return None
        try:
            parsed = phonenumbers.parse(phone, country_code)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            pass
        return None

    def _normalize_url(self, url: Optional[str]) -> Optional[str]:
        if not url:
            return None
        url = url.strip()
        if not re.match(r'^[a-zA-Z]+://', url):
            url = 'http://' + url
        if re.match(r'https?://(?:[-\w.]|(?:%[0-9a-fA-F]{2}))+\S*', url):
            return url
        return None

    def _enrich_company(self, lead: Dict[str, Any]) -> None:
        name = lead.get("company")
        if name:
            if "Tech" in name or "Software" in name:
                lead["industry"] = "IT & Software"
                lead["company_size"] = "51-200 employees"
            elif "Startup" in name:
                lead["industry"] = "Innovation & Technology"
                lead["company_size"] = "11-50 employees"

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {"persons": [], "organizations": [], "locations": [], "misc": []}
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities["persons"].append(ent.text)
                elif ent.label_ == "ORG":
                    entities["organizations"].append(ent.text)
                elif ent.label_ == "GPE":
                    entities["locations"].append(ent.text)
                else:
                    entities["misc"].append({"text": ent.text, "label": ent.label_})
        return entities

    def process_all_json(self):
        """
        Iterate over all JSON files in ./data/raw, clean and deduplicate, and save to ./data/clean with the same filename.
        """
        for filename in os.listdir(self.raw_dir):
            if filename.endswith('.json'):
                raw_path = os.path.join(self.raw_dir, filename)
                clean_path = os.path.join(self.clean_dir, filename)
                print(f"Processing {raw_path} ...")
                with open(raw_path, encoding='utf-8') as f:
                    try:
                        raw_data = json.load(f)
                    except Exception as e:
                        print(f"Failed to load {filename}: {e}")
                        continue
                if isinstance(raw_data, dict):
                    leads = [raw_data]
                else:
                    leads = raw_data
                cleaned = self.clean_dataset(leads)
                deduped = self.deduplicate(cleaned)
                with open(clean_path, 'w', encoding='utf-8') as f:
                    json.dump(deduped, f, ensure_ascii=False, indent=2)
                print(f"Saved cleaned leads to {clean_path}")

if __name__ == "__main__":
    agent = SmartCleanerAgent()
    agent.process_all_json()
