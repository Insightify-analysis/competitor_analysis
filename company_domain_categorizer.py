import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging
import asyncio
from dotenv import load_dotenv
import os
import nest_asyncio

# Add this import at the top:
from file_manager import FileManager

from gemini_model import GeminiModel
from context_loader import ContextLoader
from models.company_models import create_categorization_result
from config import get_config

nest_asyncio.apply()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent.parent / ".env")


class DomainCategorizer:
    def __init__(self, config: Dict = None, categories_file: str = None):
        self.config = config or get_config()
        self.categories_file = categories_file or self.config["categories_file"]
        self.file_manager = FileManager()
        try:
            self.categories = self._load_categories()
        except Exception as e:
            logger.warning(f"Error loading categories: {e}, using empty default.")
            self.categories = {"byType": {}}

        if self.config.get("use_ai"):
            try:
                self.model = GeminiModel()
            except Exception as e:
                logger.warning(f"Failed to initialize AI model: {e}")
                self.model = None
        else:
            self.model = None

    # Add new helper method to remove keys with None or empty string values.
    def _clean_dict(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: self._clean_dict(v)
                for k, v in data.items()
                if v is not None and (not isinstance(v, str) or v.strip() != "")
            }
        elif isinstance(data, list):
            return [self._clean_dict(item) for item in data]
        else:
            return data

    def _load_categories(self) -> Dict:
        try:
            return self.file_manager.load_json(self.categories_file)
        except (ValueError, OSError) as e:
            logger.warning(f"Error loading categories file: {e}")
            logger.info("Creating default categories file")
            return self.file_manager.create_default_categories(self.categories_file)

    def _extract_patterns(self, category_data: Dict) -> List[str]:
        patterns = []
        if isinstance(category_data, dict):
            if "lists" in category_data:
                for item in category_data["lists"]:
                    if isinstance(item, str):
                        patterns.append(
                            item.lower()
                            .replace("list of ", "")
                            .replace("lists of ", "")
                        )
                    elif isinstance(item, dict):
                        for subcat in item.values():
                            if isinstance(subcat, list):
                                patterns.extend(
                                    [p.lower().replace("list of ", "") for p in subcat]
                                )
            if "mainArticle" in category_data:
                patterns.append(
                    category_data["mainArticle"].lower().replace("lists of ", "")
                )
        return patterns

    def _get_subcategories(self, category_data: Dict) -> List[str]:
        subcategories = []
        if isinstance(category_data, dict):
            if "lists" in category_data:
                for item in category_data["lists"]:
                    if isinstance(item, str):
                        subcategories.append(item)
                    elif isinstance(item, dict):
                        for sublist in item.values():
                            if isinstance(sublist, list):
                                subcategories.extend(sublist)
        return subcategories

    def _prepare_category_prompt(self, company_name: str) -> str:
        # Updated prompt with the new JSON format instructions.
        return f"""## Company Categorization and Market Analysis

### Task Overview
You are an **AI specializing in company categorization and market analysis**. Your task is to **categorize a company** based on its name and provide additional insights if the company is relevant or has direct competitors.

### Instructions

1. **Categorization**
   - Analyze the company name: **"{company_name}"**.
   - Assign the company to **one of the available categories** exactly as provided.
   - If uncertain, select the **most appropriate** category and assign a **confidence score** between **0.0** and **1.0**.

2. **Justification**
   - Provide a **concise yet clear explanation** of why the chosen category fits best.

3. **Market Analysis for Relevant Companies**
   - If the company is relevant (related or competitive), gather and return the following:
     - **Names** of related companies
     - **Total market capitalization**
     - **Total addressable market**
     - **Competitive landscape overview**
     - **Market share distribution**
     - **Any other relevant remarks or insights**

4. **Structured Output Format**
   - Ensure the response follows this exact JSON format:

```json
{{
    "category": "category_name",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this category was chosen",
    "related_companies": {{
        "names": "value",
        "total_market_cap": "value",
        "total_addressable_market": "value",
        "competitive_landscape": "value",
        "market_share": "value",
        "remarks": "value"
    }}
}}
```

Do not include any markdown or additional text.
"""

    async def categorize_company_ai(self, company_name: str) -> Optional[Dict]:
        """Enhanced categorization using AI with better error handling"""
        if not self.model:
            logger.warning("AI categorization skipped - model not available")
            return None

        try:
            response = await self.model.generate(
                self._prepare_category_prompt(company_name),
                temperature=0.1,
            )

            if not response.text:
                raise ValueError("Empty response from API")

            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text[
                    response_text.find("{") : response_text.rfind("}") + 1
                ]

            return self._parse_ai_response(response_text, company_name)

        except Exception as e:
            logger.error(f"AI categorization failed for {company_name}: {e}")
            return None

    def _parse_ai_response(self, response_text: str, company_name: str) -> Dict:
        """Parse AI response. If JSON parsing fails, return plain text.
        Enhanced extraction using regex to capture JSON content.
        """
        import re  # ensure regex module is imported

        # Attempt to extract JSON substring using regex
        json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
            try:
                market_data = json.loads(json_text)
                return self._convert_to_ai_result(market_data, company_name)
            except json.JSONDecodeError:
                logger.error("JSON decoding failed for extracted content.")
        # Fallback to returning plaintext if extraction or parsing fails
        return {"plaintext": response_text}

    def _convert_to_ai_result(self, market_data: Dict, company_name: str) -> Dict:
        """Convert market data to AI analysis result without Pydantic"""
        market_metrics = market_data.get("market_analysis", {}).get(
            "market_metrics", {}
        )
        competitors = market_data.get("market_analysis", {}).get("competitors", [])
        # New: extract full market_analysis section, or fallback to an empty dict.
        market_analysis_full = market_data.get("market_analysis", {})

        return {
            "company_analysis": {
                "company_name": company_name,
                "industry": market_metrics.get("market_maturity", ""),
                "strengths": [],
                "weaknesses": [],
                "opportunities": market_metrics.get("key_trends", []),
                "threats": market_data.get("market_analysis", {}).get(
                    "barriers_to_entry", []
                ),
            },
            "competition_analysis": {
                "competitors": {
                    "names": [comp.get("name", "") for comp in competitors],
                    "total_market_cap": sum(
                        comp.get("market_cap", 0) for comp in competitors
                    ),
                    "market_share": sum(
                        comp.get("market_share", 0) for comp in competitors
                    ),
                    "competitive_landscape": "Detailed analysis available in raw_market_data",
                },
                "market_research": {
                    "total_addressable_market": market_metrics.get(
                        "total_market_size", 0
                    ),
                    "emerging_trends": market_data.get("market_analysis", {}).get(
                        "technology_drivers", []
                    ),
                    "remarks": "Analysis includes detailed competitor and market metrics",
                },
            },
            "raw_market_data": market_data,
            "market_analysis": market_analysis_full,  # New key to populate market_analysis section
        }

    def categorize_company_rules(self, company_name: str) -> Dict[str, List]:
        """Rule-based categorization using plain dictionaries."""
        company_name = company_name.lower()
        matches: Dict[str, List] = {}
        for category, category_data in self.categories.get("byType", {}).items():
            patterns = self._extract_patterns(category_data)
            patterns.append(category.lower())
            if any(pattern in company_name for pattern in patterns):
                subcats = self._get_subcategories(category_data)
                # Use plain dictionary instead of RuleBasedCategory
                matches[category] = [{"category": category, "subcategories": subcats}]
        return matches

    async def categorize_company(
        self, company_name: str, clean_output: bool = False
    ) -> Dict:
        """Complete categorization with both rule-based and AI analysis.
        Uses context loaded from self.config['context_folder'].
        """
        rule_based = self.categorize_company_rules(company_name)
        context = ContextLoader.load_all_context(
            Path(self.config.get("context_folder"))
        )

        ai_based = None
        if self.config["use_ai"] and self.model:
            try:
                ai_based = await self.categorize_company_ai(company_name)
            except Exception as e:
                logger.error(f"AI categorization failed: {str(e)}")

        result = create_categorization_result(
            rule_based=rule_based,
            ai_based=ai_based,
            raw_context=context,
            market_analysis=(
                ai_based.get("market_analysis")
                if (ai_based and isinstance(ai_based, dict))
                else None
            ),
        )

        if clean_output:
            result = self._clean_dict(result)
        return result
