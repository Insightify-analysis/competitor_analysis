import requests
import yfinance as yf
import logging

logger = logging.getLogger(__name__)


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


def get_company_financials(company_name):
    try:
        ticker = get_ticker_from_name(company_name)
        if not ticker:
            logger.error(f"Could not find ticker for company: {company_name}")
            return None

        stock = yf.Ticker(ticker)
        info = stock.info

        company_info = {
            "Company Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Country": info.get("country", "N/A"),
            "Website": info.get("website", "N/A"),
            "Description": info.get("longBusinessSummary", "N/A"),
            "Full Time Employees": info.get("fullTimeEmployees", "N/A"),
        }

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

        balance_sheet = {
            "Total Cash": info.get("totalCash", "N/A"),
            "Total Debt": info.get("totalDebt", "N/A"),
            "Current Ratio": info.get("currentRatio", "N/A"),
            "Quick Ratio": info.get("quickRatio", "N/A"),
            "Total Assets": info.get("totalAssets", "N/A"),
            "Total Liabilities": info.get("totalDebt", "N/A"),
            "Book Value": info.get("bookValue", "N/A"),
        }

        dividend_info = {
            "Dividend Rate": info.get("dividendRate", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "Payout Ratio": info.get("payoutRatio", "N/A"),
            "Ex-Dividend Date": info.get("exDividendDate", "N/A"),
        }

        return {
            "ticker": ticker,
            "company_info": company_info,
            "market_data": market_data,
            "financial_metrics": financial_metrics,
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "dividend_info": dividend_info,
        }
    except Exception as e:
        logger.error(f"Error fetching financial data for company {company_name}: {e}")
        return None


def get_competitors(company_name, wikidata_id=None, ticker=None, industry=None):
    import yfinance as yf  # Needed here for accessing stock info

    competitors = []
    if ticker:
        try:
            stock = yf.Ticker(ticker)
            all_competitors = stock.info.get("competitors", [])
            competitors = [c for c in all_competitors if c != company_name]
        except Exception:
            pass
    if not competitors:
        competitors = []
    return competitors or ["No competitors found"]
