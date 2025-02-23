from flask import Flask, request, jsonify, Response
import asyncio
import threading
import os
import requests
import logging
from dotenv import load_dotenv
from app import CompanyCategorizerApp
from flask_cors import CORS, cross_origin
from flask_cors import CORS
from datetime import datetime  # added from router.py
from services import (
    get_ticker_from_name,
    get_company_financials,
    get_competitors,
)  # added from router.py
from wikidata import (
    get_wikidata_id,
    get_wikidata_details,
    get_funding_rounds,
)  # added from router.py

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type"],
        }
    },
)

app = Flask(__name__)
instance = CompanyCategorizerApp()
logger = app.logger

# Start an asynchronous event loop in a background thread
loop = asyncio.new_event_loop()


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


threading.Thread(target=start_loop, args=(loop,), daemon=True).start()


def run_async_task(coro, timeout=10):
    try:
        future = asyncio.run_coroutine_threadsafe(
            asyncio.wait_for(coro, timeout=timeout), loop
        )
        return future.result(timeout=timeout + 1)
    except Exception as e:
        logger.error(f"Async task error: {e}")
        raise


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/categorize", methods=["POST"])
def categorize_endpoint():
    company_name = request.args.get("query")
    if not company_name:
        return jsonify({"error": "Missing company_name parameter"}), 400
    clean_param = request.args.get("clean", "false").lower() == "true"
    try:
        result = run_async_task(
            instance.categorizer.categorize_company(
                company_name, clean_output=clean_param
            )
        )
        raw_data = result.get("raw_market_data", {})
        post_response = post_json_result(raw_data)
        return jsonify({"result": result, "post_response": post_response})
    except Exception as e:
        logger.error(f"/categorize error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/categorize_file", methods=["GET"])
def categorize_file_endpoint():
    file_path = request.args.get("file_path")
    if not file_path:
        return jsonify({"error": "Missing file_path parameter"}), 400
    clean_param = request.args.get("clean", "false").lower() == "true"
    try:
        result = run_async_task(
            instance.handle_file_input(file_path, clean_output=clean_param)
        )
        raw_data = result.get("raw_market_data", {}) if isinstance(result, dict) else {}
        post_response = post_json_result(raw_data)
        return jsonify({"result": result, "post_response": post_response})
    except Exception as e:
        logger.error(f"/categorize_file error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/post_json", methods=["POST"])
def post_json_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
    post_response = post_json_result(data)
    if post_response is None:
        return jsonify({"error": "Failed to post JSON result"}), 500
    return jsonify({"post_response": post_response})


def generate_json_stream(company_name):
    yield "{\n"
    yield f'  "company": "{company_name}",\n'
    yield '  "analysis": {\n'
    yield '    "step1": "processing...",\n'
    yield '    "step2": "processing..."\n'
    yield "  },\n"
    yield '  "final_result": "Category X"\n'
    yield "}\n"


@app.route("/stream_categorize", methods=["GET"])
def stream_categorize_endpoint():
    company_name = request.args.get("company_name")
    if not company_name:
        return jsonify({"error": "Missing company_name parameter"}), 400
    return Response(generate_json_stream(company_name), mimetype="application/json")


@app.route("/json", methods=["GET", "POST"])
def json_response():
    company_name = None
    if request.method == "POST":
        data = request.get_json()
        if data and "company" in data:
            company_name = data["company"]
    else:
        company_name = request.args.get("company")
    if not company_name:
        return jsonify(
            {"message": "Provide a company parameter, e.g., /json?company=YourCompany"}
        )
    result = {
        "company": company_name,
        "analysis": {"step1": "processing...", "step2": "processing..."},
        "final_result": "Category X",
    }
    return jsonify(result)


@app.route("/company/<company_name>", methods=["POST"])
def company_post():
    # Get optional clean flag from query parameters.
    clean_param = request.args.get("clean", "false").lower() == "true"
    try:
        result = run_async_task(
            instance.categorizer.categorize_company(
                company_name, clean_output=clean_param
            )
        )
        return jsonify({"result": result})
    except Exception as e:
        logger.error(f"/company/{company_name} error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/company_json", methods=["POST"])
@cross_origin()
def company_json_post():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'company' in JSON payload"}), 400
        company_name = data["query"]
        clean_param = data.get("clean", False)
        try:
            result = run_async_task(
                instance.categorizer.categorize_company(
                    company_name, clean_output=clean_param
                )
            )
            return jsonify({"result": result})
        except Exception as e:
            logger.error(f"/company_json error: {e}")
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"/company_json error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/yfinance", methods=["POST"])
@cross_origin()
def yfinance_data():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    try:
        data = request.get_json()
        if not data or "company_name" not in data:
            return jsonify({"error": "Missing company_name in request body"}), 400

        company_name = data["company_name"].strip()
        financial_data = get_company_financials(company_name)
        if not financial_data:
            return jsonify({"error": "Could not fetch financial data"}), 500

        return jsonify({"company_name": company_name, "financial_data": financial_data})
    except Exception as e:
        app.logger.exception("Unhandled exception in /api/yfinance")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/api/company_analysis", methods=["POST"])
@cross_origin()
def company_analysis():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
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
        app.logger.exception("Unhandled exception in /api/company_analysis")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


def post_json_result(data):
    post_url = os.getenv("POST_URL")
    if not post_url:
        logger.info("POST_URL not set, skipping posting JSON result")
        return None
    try:
        response = requests.post(post_url, json=data)
        response.raise_for_status()
        logger.info(f"Posted JSON result to {post_url}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to post JSON result: {e}")
        return None


if __name__ == "__main__":
    load_dotenv()
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
