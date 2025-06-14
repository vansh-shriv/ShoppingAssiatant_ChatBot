# Shopping Chatbot

A smart shopping assistant chatbot that helps users find products, get recommendations, and make purchases.

## Features

- Natural language processing for understanding user queries
- Product search and recommendations
- Shopping cart management
- User-friendly interface
- Real-time responses

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

- `app.py`: Main Flask application
- `static/`: Static files (CSS, JavaScript, images)
- `templates/`: HTML templates
- `models/`: Chatbot model and utilities
- `data/`: Sample product data

## Technologies Used

- Python
- Flask
- NLTK
- scikit-learn
- HTML/CSS
- JavaScript 