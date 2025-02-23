from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

# Import helper functions from the new services module
from services import get_ticker_from_name, get_company_financials, get_competitors

# Import wikidata functions
from wikidata import get_wikidata_id, get_wikidata_details, get_funding_rounds

logger = logging.getLogger(__name__)

router_bp = Blueprint("router_bp", __name__)


@router_bp.route("/api/yfinance", methods=["POST"])
def yfinance_data():
    try:
        data = request.get_json()
        if not data or "ticker" not in data:
            return jsonify({"error": "Missing ticker in request body"}), 400

        ticker = data["ticker"].strip()
        financial_data = get_company_financials(ticker)
        if not financial_data:
            return jsonify({"error": "Could not fetch financial data"}), 500

        return jsonify({"ticker": ticker, "financial_data": financial_data})
    except Exception as e:
        logger.exception("Unhandled exception in /api/yfinance")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@router_bp.route("/api/company_analysis", methods=["POST"])
def company_analysis():
    try:
        data = request.get_json()
        if not data or "company_name" not in data:
            return jsonify({"error": "Missing company_name in request body"}), 400

        company_name = data["company_name"].strip()
        wikidata_id = get_wikidata_id(company_name)
        response_data = {
            "company_name": company_name,
            "wikidata_id": wikidata_id,
            "timestamp": datetime.now().isoformat(),
        }

        if wikidata_id:
            response_data["wikidata_details"] = get_wikidata_details(wikidata_id)
            response_data["funding_rounds"] = get_funding_rounds(wikidata_id)

        ticker = get_ticker_from_name(company_name)
        response_data["ticker"] = ticker

        if ticker:
            response_data["financial_data"] = get_company_financials(ticker)

        response_data["competitors"] = get_competitors(
            company_name=company_name,
            wikidata_id=wikidata_id,
            ticker=ticker,
            industry=response_data.get("wikidata_details", {}).get("Industry"),
        )

        return jsonify(response_data)

    except Exception as e:
        logger.exception("Unhandled exception in /api/company_analysis")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
