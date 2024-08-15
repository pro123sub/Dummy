from flask import Flask, jsonify, request
import cohere
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Fetch Cohere API key from environment variables
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
cohere_client = cohere.Client(COHERE_API_KEY)
# Load hardcoded demand data from the JSON file
def load_demand_data():
    with open('demand.json', 'r') as file:
        return json.load(file)

# Load the demand data
demand_data = load_demand_data()


def generate_cohere_response(prompt):
    response = cohere_client.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=100,  # Adjusted for shorter responses
        temperature=0.7,
        k=0,
        stop_sequences=["."]
    )
    return response.generations[0].text.strip()

@app.route('/api/recommend', methods=['POST'])
def recommend_items():
    data = request.json
    search_history = data.get('search_history', [])

    if not search_history:
        return jsonify({"error": "Search history is required"}), 400

    prompt = f"Based on the search history {', '.join(search_history)}, generate a list of product names in these categories: Gaming Consoles, Beauty Products, and Accessories. Only include the product names and ensure diversity in the suggestions."

    recommendations_text = generate_cohere_response(prompt)
    recommendations_list = recommendations_text.split("\n")

    recommendations = []
    for recommendation in recommendations_list:
        recommendation = recommendation.strip()
        if recommendation:
            match_percentage = round(70 + 30 * (hash(recommendation) % 100 / 100), 2)  # Simulated match percentage
            tag = "Best match" if match_percentage >= 70 else "Good match"
            recommendations.append({
                'product': recommendation,
                'match_percentage': match_percentage,
                'tag': f"{tag} ({match_percentage}%)"
            })

    return jsonify(recommendations)

@app.route('/api/optimize_price', methods=['POST'])
def optimize_price():
    data = request.json
    prices = data.get('prices', [])
    actual_prices = data.get('actual_prices', [])

    if not prices or not actual_prices:
        return jsonify({"error": "Prices and actual prices are required"}), 400

    prompt = f"Given the list of prices {prices} and actual prices {actual_prices}, provide a list of optimized prices that balance revenue maximization without making the product feel too expensive for the user or causing loss to the retailer. Provide only product names and their optimized prices."

    optimized_prices_text = generate_cohere_response(prompt)
    optimized_prices_list = optimized_prices_text.split("\n")

    optimized_prices = [{"product": price.split(":")[0].strip(), "optimized_price": price.split(":")[1].strip()} 
                        for price in optimized_prices_list if ":" in price]

    return jsonify(optimized_prices)

@app.route('/api/demand_forecasting', methods=['POST'])
def demand_forecasting():
    data = request.json
    city = data.get('city', '')
    age = data.get('age', '')
    gender = data.get('gender', '')

    if not city or not age or not gender:
        return jsonify({"error": "City, age, and gender are required"}), 400

    # Use hardcoded data for demand forecasting
    category = 'Electronics'  # You can customize this or make it dynamic based on input
    category_data = demand_data.get(category, {})
    city_data = category_data.get(city, {})
    demand_percentage = city_data.get(age, 0)

    demand_forecast = [
        {
            "category": category,
            "demand_percentage": demand_percentage
        }
    ]

    return jsonify(demand_forecast)

if __name__ == '__main__':
    app.run(debug=True)
