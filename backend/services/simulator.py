import json
import os
from datetime import datetime

def load_stock_data(symbol):
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "..", "data", f"{symbol.upper()}.json")

    try:
        with open(data_path, "r") as f:
            data = json.load(f)

        for row in data:
            if "time" in row:
                row["date"] = datetime.strptime(row["time"], "%Y-%m-%dT%H:%M:%SZ")
            else:
                raise ValueError("Missing 'time' field in data")

        data.sort(key=lambda x: x["date"])
        return data

    except FileNotFoundError:
        print(f"❌ Data file for {symbol} not found.")
        return []
    except Exception as e:
        print(f"❌ Error loading stock data: {e}")
        return []

def simulate_sip(data, monthly_amount, years):
    results = []
    months_required = years * 12

    for i in range(len(data) - months_required):
        window = data[i:i + months_required]
        total_units = 0
        total_invested = 0

        for month_data in window:
            close_price = month_data["close"]
            if close_price > 0:
                units = monthly_amount / close_price
                total_units += units
                total_invested += monthly_amount

        final_price = window[-1]["close"]
        final_value = total_units * final_price
        cagr = ((final_value / total_invested) ** (1 / years) - 1) * 100 if total_invested > 0 else 0

        results.append({
            "start": window[0]["date"].strftime("%Y-%m-%d"),
            "end": window[-1]["date"].strftime("%Y-%m-%d"),
            "final_value": round(final_value, 2),
            "invested": round(total_invested, 2),
            "cagr_percent": round(cagr, 2),
            "initial_price": round(window[0]["close"], 2),
            "final_price": round(window[-1]["close"], 2)
        })

    return results

def simulate_lump_sum(data, lump_sum_amount, years):
    results = []
    months_required = years * 12

    for i in range(len(data) - months_required):
        window = data[i:i + months_required]
        start_price = window[0]["close"]
        end_price = window[-1]["close"]

        if start_price > 0 and end_price > 0:
            units = lump_sum_amount / start_price
            final_value = units * end_price
            cagr = ((final_value / lump_sum_amount) ** (1 / years) - 1) * 100

            results.append({
                "start": window[0]["date"].strftime("%Y-%m-%d"),
                "end": window[-1]["date"].strftime("%Y-%m-%d"),
                "final_value": round(final_value, 2),
                "invested": round(lump_sum_amount, 2),
                "cagr_percent": round(cagr, 2),
                "initial_price": round(start_price, 2),
                "final_price": round(end_price, 2)
            })

    return results

def generate_summary_and_facts(symbol, results, years):
    if not results:
        return {}, []

    sorted_results = sorted(results, key=lambda r: r["cagr_percent"])
    total_cagr = sum(r["cagr_percent"] for r in results)
    avg_cagr = total_cagr / len(results)
    prob_above_avg = len([r for r in results if r["cagr_percent"] > avg_cagr]) / len(results) * 100

    best = sorted_results[-1]
    worst = sorted_results[0]
    avg_final_value = sum(r["final_value"] for r in results) / len(results)

    best_month = datetime.strptime(best["end"], "%Y-%m-%d").strftime("%b")
    worst_month = datetime.strptime(worst["end"], "%Y-%m-%d").strftime("%b")
    best_year = best["start"][:4]

    min_cagr = sorted_results[0]["cagr_percent"]
    max_cagr = sorted_results[-1]["cagr_percent"]

    summary = {
        "avg_cagr": round(avg_cagr, 2),
        "avg_final": round(avg_final_value, 2),
        "prob_above_avg": round(prob_above_avg, 2),
        "min_cagr": min_cagr,
        "max_cagr": max_cagr,
        "best_final": best["final_value"],
        "best_start": best["start"],
        "best_end": best["end"],
        "best_initial_price": best["initial_price"],
        "best_final_price": best["final_price"],
        "worst_final": worst["final_value"],
        "worst_start": worst["start"],
        "worst_end": worst["end"],
        "worst_initial_price": worst["initial_price"],
        "worst_final_price": worst["final_price"]
    }
    best_end_year = best["end"][:4]

    fun_facts = [
        f"📈 Do you know {symbol} gave its highest return over a full {years}-year period ending in {best_end_year}?",
        f"📊 Do you know {symbol} gave above average returns in {summary['prob_above_avg']}% of simulations?",
        f"📅 Do you know {symbol} performed best in the month of {best_month}?",
        f"📉 Do you know {symbol} gave the lowest return in {worst_month}?",
        f"📐 Do you know the CAGR of {symbol} ranged from {min_cagr}% to {max_cagr}% over different {years}-year periods?"
    ]

    # 🆕 Add this data-driven insight based on return probability
    if prob_above_avg > 50:
        fun_facts.append(
            f"📈 Do you know {symbol} had more chances of beating the average than missing it in {years}-year periods?"
        )
    else:
        fun_facts.append(
            f"📉 Do you know {symbol} had more chances of missing the average than beating it in {years}-year periods?"
        )
    return summary, fun_facts