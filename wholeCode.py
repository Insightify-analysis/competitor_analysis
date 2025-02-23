import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import yfinance as yf
from datetime import datetime

# Import wikidata functions from the new module
from wikidata import (
    get_wikidata_id,
    get_wikidata_details,
    get_funding_rounds,
    get_industry_id,
    search_industry_id,
    get_industry_competitors,
    get_direct_competitors,
)

from router import router_bp  # Import the router blueprint

app = Flask(__name__)
CORS(app)

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app.register_blueprint(router_bp)  # Register the blueprint


def get_ticker_from_name(company_name):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("quotes", [{}])[0].get("symbol") if data.get("quotes") else None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching ticker for {company_name}: {e}")
        return None


def get_company_financials(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Basic company information
        company_info = {
            "Company Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Country": info.get("country", "N/A"),
            "Website": info.get("website", "N/A"),
            "Description": info.get("longBusinessSummary", "N/A"),
            "Full Time Employees": info.get("fullTimeEmployees", "N/A"),
        }

        # Market data
        market_data = {
            "Market Cap": info.get("marketCap", "N/A"),
            "Current Price": info.get("currentPrice", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "50 Day Average": info.get("fiftyDayAverage", "N/A"),
            "200 Day Average": info.get("twoHundredDayAverage", "N/A"),
            "Volume": info.get("volume", "N/A"),
            "Average Volume": info.get("averageVolume", "N/A"),
        }

        # Financial metrics
        financial_metrics = {
            "PE Ratio": info.get("trailingPE", "N/A"),
            "Forward PE": info.get("forwardPE", "N/A"),
            "EPS": info.get("trailingEps", "N/A"),
            "Forward EPS": info.get("forwardEps", "N/A"),
            "PEG Ratio": info.get("pegRatio", "N/A"),
            "Price to Book": info.get("priceToBook", "N/A"),
            "Price to Sales": info.get("priceToSalesTrailing12Months", "N/A"),
            "Beta": info.get("beta", "N/A"),
        }

        # Income statement metrics
        income_statement = {
            "Revenue": info.get("totalRevenue", "N/A"),
            "Revenue Growth": info.get("revenueGrowth", "N/A"),
            "Gross Profits": info.get("grossProfits", "N/A"),
            "EBITDA": info.get("ebitda", "N/A"),
            "Net Income": info.get("netIncomeToCommon", "N/A"),
            "Profit Margin": info.get("profitMargins", "N/A"),
            "Operating Margin": info.get("operatingMargins", "N/A"),
            "Gross Margin": info.get("grossMargins", "N/A"),
        }

        # Balance sheet metrics
        balance_sheet = {
            "Total Cash": info.get("totalCash", "N/A"),
            "Total Debt": info.get("totalDebt", "N/A"),
            "Current Ratio": info.get("currentRatio", "N/A"),
            "Quick Ratio": info.get("quickRatio", "N/A"),
            "Total Assets": info.get("totalAssets", "N/A"),
            "Total Liabilities": info.get("totalDebt", "N/A"),
            "Book Value": info.get("bookValue", "N/A"),
        }

        # Dividend information
        dividend_info = {
            "Dividend Rate": info.get("dividendRate", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "Payout Ratio": info.get("payoutRatio", "N/A"),
            "Ex-Dividend Date": info.get("exDividendDate", "N/A"),
        }

        return {
            "company_info": company_info,
            "market_data": market_data,
            "financial_metrics": financial_metrics,
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "dividend_info": dividend_info,
        }
    except Exception as e:
        logger.error(f"Error fetching financial data for ticker {ticker}: {e}")
        return None


def get_competitors(company_name, wikidata_id=None, ticker=None, industry=None):
    competitors = []

    # Method 1: Yahoo Finance (no country filter now)
    if ticker:
        try:
            stock = yf.Ticker(ticker)
            all_competitors = stock.info.get("competitors", [])
            competitors = [c for c in all_competitors if c != company_name]
        except Exception:
            pass

    if not competitors:
        industry_id = None
        if industry:
            industry_id = search_industry_id(industry)
        competitors = get_industry_competitors(
            company_id=wikidata_id, industry_id=industry_id, industry_name=industry
        )

    if not competitors and wikidata_id:
        competitors = get_direct_competitors(wikidata_id)

    return competitors or ["No competitors found"]


@app.route("/api/company_analysis", methods=["POST"])
def company_analysis():
    try:
        data = request.get_json()

        if not data or "company_name" not in data:
            return jsonify({"error": "Missing company_name in request body"}), 400

        company_name = data["company_name"].strip()

        # Get Wikidata information
        wikidata_id = get_wikidata_id(company_name)
        response_data = {
            "company_name": company_name,
            "wikidata_id": wikidata_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Get company details from Wikidata
        if wikidata_id:
            response_data["wikidata_details"] = get_wikidata_details(wikidata_id)
            response_data["funding_rounds"] = get_funding_rounds(wikidata_id)

        # Get Yahoo Finance information
        ticker = get_ticker_from_name(company_name)
        response_data["ticker"] = ticker

        if ticker:
            response_data["financial_data"] = get_company_financials(ticker)

        # Get competitors (all companies; no country filtering)
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
