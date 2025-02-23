from flask import Flask, request, jsonify
import asyncio
from company_domain_categorizer import DomainCategorizer

app = Flask(__name__)
categorizer = DomainCategorizer()


@app.route("/categorize", methods=["GET"])
def categorize():
    company_name = request.args.get("company_name")
    if not company_name:
        return jsonify({"error": "Missing company_name parameter"}), 400
    try:
        result = asyncio.run(categorizer.categorize_company(company_name))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
