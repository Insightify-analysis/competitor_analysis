from typing import Dict, List, Optional, Any


def create_competition_data(
    names: List[str],
    total_market_cap: float,
    market_share: float,
    competitive_landscape: str,
) -> Dict:
    return {
        "names": names,
        "total_market_cap": total_market_cap,
        "market_share": market_share,
        "competitive_landscape": competitive_landscape,
    }


def create_company_analysis(
    company_name: str,
    industry: str,
    strengths: str,
    weaknesses: str,
    opportunities: str,
    threats: str,
) -> Dict:
    return {
        "company_name": company_name,
        "industry": industry,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats,
    }


def create_market_research(
    total_addressable_market: float, emerging_trends: str, remarks: str
) -> Dict:
    return {
        "total_addressable_market": total_addressable_market,
        "emerging_trends": emerging_trends,
        "remarks": remarks,
    }


def create_categorization_result(
    rule_based: Dict[str, List[str]],
    ai_based: Optional[Dict] = None,
    raw_context: Optional[Dict[str, Any]] = None,
    market_analysis: Optional[Dict] = None,
) -> Dict:
    return {
        "rule_based": rule_based,
        "ai_based": ai_based,
        "raw_context": raw_context,
        "market_analysis": market_analysis,
    }
