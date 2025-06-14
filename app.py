from flask import Flask, render_template, request, jsonify
import json
import random
from models.chatbot import ShoppingChatbot
import logging
from markupsafe import Markup

app = Flask(__name__)

# In-memory cart for demonstration
cart = []

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

chatbot = ShoppingChatbot()

# Load sample products
with open('data/products.json', 'r') as f:
    products = json.load(f)['products']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    logging.info(f"Received message: {user_message}")
    try:
        response = chatbot.get_response(user_message)
        return jsonify({'response': Markup(response)})
    except Exception as e:
        logging.error(f"Error processing chat message: {e}", exc_info=True)
        return jsonify({'response': 'Sorry, I encountered an internal error. Please try again later.'}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category', None)
    if category:
        filtered_products = [p for p in products if p['category'].lower() == category.lower()]
        return jsonify(filtered_products)
    return jsonify(products)

@app.route('/api/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart.append(product)
        logging.info(f"Added {product['name']} to cart. Current cart: {cart}")
        return jsonify({'message': f'{product['name']} added to cart!', 'cart_count': len(cart)})
    return jsonify({'message': 'Product not found.'}), 404

@app.route('/api/view_cart', methods=['GET'])
def view_cart():
    return jsonify({'cart': cart, 'total_items': len(cart), 'total_price': sum(item['price'] for item in cart)})

if __name__ == '__main__':
    app.run(debug=True) 