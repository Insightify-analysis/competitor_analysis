import requests
import logging

logger = logging.getLogger(__name__)


def get_wikidata_id(company_name):
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={company_name}&language=en&format=json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "search" in data and data["search"]:
            return data["search"][0]["id"]
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching wikidata ID for {company_name}: {e}")
        return None


def fetch_wikidata(query):
    endpoint = "https://query.wikidata.org/sparql"
    params = {"query": query, "format": "json"}
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["results"]["bindings"] if "results" in data else []
    except requests.exceptions.RequestException as e:
        logger.error(f"SPARQL query failed: {e}")
        return []


def get_wikidata_details(wikidata_id):
    query = f"""
    SELECT ?industryLabel ?countryLabel ?hqLabel ?founded ?employees WHERE {{
        OPTIONAL {{ wd:{wikidata_id} wdt:P452 ?industry. }}
        OPTIONAL {{ wd:{wikidata_id} wdt:P17 ?country. }}
        OPTIONAL {{ wd:{wikidata_id} wdt:P159 ?hq. }}
        OPTIONAL {{ wd:{wikidata_id} wdt:P571 ?founded. }}
        OPTIONAL {{ wd:{wikidata_id} wdt:P1128 ?employees. }}
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} LIMIT 1
    """
    results = fetch_wikidata(query)
    if not results:
        return {}
    result = results[0]
    return {
        "Industry": result.get("industryLabel", {}).get("value", "N/A"),
        "Country": result.get("countryLabel", {}).get("value", "N/A"),
        "Headquarters": result.get("hqLabel", {}).get("value", "N/A"),
        "Founded": result.get("founded", {}).get("value", "N/A"),
        "Employees": result.get("employees", {}).get("value", "N/A"),
    }


def get_funding_rounds(wikidata_id):
    query = f"""
    SELECT ?investmentLabel ?amount ?currencyLabel WHERE {{
      ?investment wdt:P3320 wd:{wikidata_id}.
      OPTIONAL {{ ?investment wdt:P4999 ?amount. }}
      OPTIONAL {{ ?investment wdt:P38 ?currency. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    results = fetch_wikidata(query)
    funding_data = []
    for result in results:
        amount = result.get("amount", {}).get("value", "Unknown")
        currency = result.get("currencyLabel", {}).get("value", "Unknown")
        funding_data.append(
            {
                "round": result.get("investmentLabel", {}).get("value", "Unknown"),
                "amount": amount,
                "currency": currency,
            }
        )
    return funding_data if funding_data else []


def get_industry_id(wikidata_id):
    query = f"""
    SELECT ?industry WHERE {{
        wd:{wikidata_id} wdt:P452 ?industry.
    }}
    """
    results = fetch_wikidata(query)
    return results[0]["industry"]["value"].split("/")[-1] if results else None


def search_industry_id(industry_name):
    query = f"""
    SELECT ?industry WHERE {{
        ?industry rdfs:label "{industry_name}"@en;
                  wdt:P31/wdt:P279* wd:Q8148.
    }}
    LIMIT 1
    """
    results = fetch_wikidata(query)
    return results[0]["industry"]["value"].split("/")[-1] if results else None


def get_industry_competitors(company_id=None, industry_id=None, industry_name=None):
    if not industry_id:
        if company_id:
            industry_id = get_industry_id(company_id)
        elif industry_name:
            industry_id = search_industry_id(industry_name)
    if not industry_id:
        return []
    query = f"""
    SELECT DISTINCT ?company ?companyLabel WHERE {{
        ?company wdt:P452 wd:{industry_id}.
        {f"FILTER (?company != wd:{company_id})" if company_id else ""}
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    ORDER BY DESC(?company)
    """
    results = fetch_wikidata(query)
    return [result["companyLabel"]["value"] for result in results]


def get_direct_competitors(wikidata_id):
    query = f"""
    SELECT ?competitorLabel WHERE {{
        wd:{wikidata_id} wdt:P4886 ?competitor.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    results = fetch_wikidata(query)
    return [result["competitorLabel"]["value"] for result in results]
