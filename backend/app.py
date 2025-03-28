from flask import Flask, request, jsonify, send_from_directory
from services.simulator import load_stock_data, simulate_sip, simulate_lump_sum, generate_summary_and_facts
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json()

    symbol = data.get("symbol")
    investment_type = data.get("type")  # 'sip' or 'lump_sum'
    amount = float(data.get("amount", 0))
    years = int(data.get("years", 5))

    stock_data = load_stock_data(symbol)

    if not stock_data:
        return jsonify({"error": f"No data found for symbol {symbol}"}), 404

    if investment_type == "sip":
        results = simulate_sip(stock_data, monthly_amount=amount, years=years)
    elif investment_type == "lump_sum":
        results = simulate_lump_sum(stock_data, lump_sum_amount=amount, years=years)
    else:
        return jsonify({"error": "Invalid investment type. Must be 'sip' or 'lump_sum'."}), 400

    summary, fun_facts = generate_summary_and_facts(symbol, results, years)

    return jsonify({
        "results": results,
        "summary": summary,
        "fun_facts": fun_facts
    })

# Serve React static files from /frontend/build
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    build_dir = os.path.join(os.path.dirname(__file__), "../frontend/build")
    if path != "" and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    else:
        return send_from_directory(build_dir, "index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)

