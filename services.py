import requests
import yfinance as yf
import logging
import time
import json
from functools import wraps
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    redis_client = redis.Redis(
        host="localhost",  # Change this to your Redis host
        port=6379,
        db=0,
        decode_responses=True,
    )
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Running without cache.")
    redis_client = None

# Rate limiting configuration
RATE_LIMIT_PERIOD = 60  # seconds
MAX_REQUESTS = 50
last_request_time = 0
request_count = 0


def rate_limit_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global last_request_time, request_count

        current_time = time.time()
        if current_time - last_request_time > RATE_LIMIT_PERIOD:
            last_request_time = current_time
            request_count = 0

        if request_count >= MAX_REQUESTS:
            sleep_time = RATE_LIMIT_PERIOD - (current_time - last_request_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_request_time = time.time()
            request_count = 0

        request_count += 1
        return func(*args, **kwargs)

    return wrapper


def get_cached_data(key):
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.error(f"Cache retrieval error: {e}")
        return None


def set_cached_data(key, data, expiry_hours=24):
    if not redis_client:
        return
    try:
        redis_client.setex(key, timedelta(hours=expiry_hours), json.dumps(data))
    except Exception as e:
        logger.error(f"Cache storage error: {e}")


@rate_limit_decorator
def get_ticker_from_name(company_name):
    cache_key = f"ticker:{company_name}"
    cached_result = get_cached_data(cache_key)
    if cached_result:
        return cached_result

    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        ticker = (
            data.get("quotes", [{}])[0].get("symbol") if data.get("quotes") else None
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching ticker for {company_name}: {e}")
        return None

    if ticker:
        set_cached_data(cache_key, ticker)
    return ticker


def get_company_financials(ticker):
    try:
        stock = yf.Ticker(ticker)

        # Implement exponential backoff for API requests
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                info = stock.info

        # ...existing code building company_info...
        company_info = {
            "Company Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Country": info.get("country", "N/A"),
            "Website": info.get("website", "N/A"),
            "Description": info.get("longBusinessSummary", "N/A"),
            "Full Time Employees": info.get("fullTimeEmployees", "N/A"),
        }

        # ...existing code building market_data...
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

        # ...existing code building financial_metrics...
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

        # ...existing code building income_statement...
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

        # ...existing code building balance_sheet...
        balance_sheet = {
            "Total Cash": info.get("totalCash", "N/A"),
            "Total Debt": info.get("totalDebt", "N/A"),
            "Current Ratio": info.get("currentRatio", "N/A"),
            "Quick Ratio": info.get("quickRatio", "N/A"),
            "Total Assets": info.get("totalAssets", "N/A"),
            "Total Liabilities": info.get("totalDebt", "N/A"),
            "Book Value": info.get("bookValue", "N/A"),
        }

        # ...existing code building dividend_info...
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
        # In this simple integration, we assume that if no competitors from ticker,
        # an empty list is returned (or a default message).
        competitors = []
    return competitors or ["No competitors found"]
