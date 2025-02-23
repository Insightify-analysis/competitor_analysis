from flask import Flask, request, jsonify, Response
import asyncio
import os
import json
from app import CompanyCategorizerApp
import threading
from dotenv import load_dotenv  # added import for dotenv

app = Flask(__name__)
instance = CompanyCategorizerApp()

# Create and run a persistent event loop in a background thread
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
    except asyncio.TimeoutError as e:
        app.logger.error(f"Async task timeout: {e}")
        raise
    except Exception as e:
        app.logger.error(f"Async task error: {e}")
        raise


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route("/categorize", methods=["POST"])
def categorize_endpoint():
    company_name = request.args.get("query")
    if not company_name:
        return jsonify({"error": "Missing company_name parameter"}), 400
    # Get "clean" parameter (default False)
    clean_param = request.args.get("clean", "false").lower() == "true"
    try:
        result = run_async_task(
            instance.categorizer.categorize_company(
                company_name, clean_output=clean_param
            )
        )
        # Extract only the "raw_market_data" portion
        raw_data = result.get("raw_market_data", {})
        post_response = post_json_result(raw_data)
        return jsonify({"result": result, "post_response": post_response})
    except Exception as e:
        app.logger.error(f"/categorize error: {e}")
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
        # Extract only the "raw_market_data" portion
        raw_data = result.get("raw_market_data", {}) if isinstance(result, dict) else {}
        post_response = post_json_result(raw_data)
        return jsonify({"result": result, "post_response": post_response})
    except Exception as e:
        app.logger.error(f"/categorize_file error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/post_json", methods=["POST"])
def post_json_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
    post_response = post_json_result(data)
    if post_response is None:
        return jsonify({"error": "Failed to post JSON result"}), 500
    return jsonify({"post_response": post_response}), 200


def generate_json_stream(company_name):
    # Simulate multiple steps of JSON generation
    yield "{\n"
    yield f'  "company": "{company_name}",\n'
    # Simulate first part of analysis results
    yield '  "analysis": {\n'
    yield '    "step1": "processing...",\n'
    yield '    "step2": "processing..."\n'
    yield "  },\n"
    # Simulate delay or additional computations here (omitted)
    yield '  "final_result": "Category X"\n'
    yield "}\n"


@app.route("/stream_categorize", methods=["GET"])
def stream_categorize_endpoint():
    company_name = request.args.get("company_name")
    if not company_name:
        return jsonify({"error": "Missing company_name parameter"}), 400
    # Create a response with streamed JSON data
    return Response(generate_json_stream(company_name), mimetype="application/json")


import os
import requests
import logging

logger = logging.getLogger(__name__)


def post_json_result(data):
    post_url = os.getenv(
        "POST_URL"
    )  # set POST_URL in your environment for target endpoint
    if not post_url:
        logger.info("POST_URL not set, skipping posting JSON result")
        return None
    try:
        response = requests.post(post_url, json=data)
        response.raise_for_status()
        logger.info(f"Successfully posted JSON result to {post_url}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to post JSON result: {e}")
        return None


@app.route("/json", methods=["GET", "POST"])
def json_response():
    if request.method == "POST":
        data = request.get_json()
        if not data or not data.get("company"):
            return jsonify({"error": "Missing company name"}), 400
        company_name = data["company"]
    else:  # GET request
        company_name = request.args.get("company")
        if not company_name:
            return (
                jsonify(
                    {
                        "message": "Provide a company parameter, e.g., /json?company=YourCompany"
                    }
                ),
                200,
            )
    result = {
        "company": company_name,
        "analysis": {"step1": "processing...", "step2": "processing..."},
        "final_result": "Category X",
    }
    return jsonify(result)


if __name__ == "__main__":
    load_dotenv()  # load environment variables from .env file
    # Determine debug mode from environment variable for production readiness
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))  # get port from .env file (default 5000)
    # Bind to 0.0.0.0 to allow external access on Render
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
