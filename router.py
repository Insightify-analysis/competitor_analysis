from flask import Blueprint, request, jsonify
from wholeCode import get_company_financials, logger

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
