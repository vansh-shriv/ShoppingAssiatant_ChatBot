import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import random
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
import re

class ShoppingChatbot:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        
        self.stop_words = set(stopwords.words('english'))
        self.load_intents()
        self.train_model()

    def load_intents(self):
        with open('data/intents.json', 'r') as f:
            self.intents = json.load(f)
        with open('data/products.json', 'r') as f:
            self.products = json.load(f)['products'] # Load products here as well

    def train_model(self):
        self.words = []
        self.classes = []
        self.documents = []
        ignore_words = ['?', '!', '.', ',']

        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                w = word_tokenize(pattern)
                self.words.extend(w)
                self.documents.append((w, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        self.words = [w.lower() for w in self.words if w not in ignore_words]
        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

        training_data = []
        output_empty = [0] * len(self.classes)

        for doc in self.documents:
            bag = []
            pattern_words = doc[0]
            pattern_words = [word.lower() for word in pattern_words]
            for w in self.words:
                bag.append(1) if w in pattern_words else bag.append(0)
            
            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training_data.append((bag, output_row))

        # Prepare data for scikit-learn
        X_train = [data[0] for data in training_data]
        y_train = [data[1] for data in training_data]

        self.vectorizer = CountVectorizer(tokenizer=lambda x: word_tokenize(x.lower()), stop_words=list(self.stop_words))
        X_counts = self.vectorizer.fit_transform([" ".join(doc[0]) for doc in self.documents])
        self.tfidf_transformer = TfidfTransformer()
        X_tfidf = self.tfidf_transformer.fit_transform(X_counts)

        self.classifier = LogisticRegression(random_state=0, solver='liblinear')
        
        # Map one-hot encoded labels to single labels for classification
        y_labels = [self.classes[row.index(1)] for row in y_train]
        self.classifier.fit(X_tfidf, y_labels)

    def preprocess_text(self, text):
        # Tokenize and remove stopwords
        tokens = word_tokenize(text.lower())
        tokens = [t for t in tokens if t not in self.stop_words]
        return " ".join(tokens)

    def predict_intent(self, sentence):
        processed_sentence = self.preprocess_text(sentence)
        if not processed_sentence.strip(): # Handle empty string after preprocessing
            return "default"

        try:
            # Transform the new sentence using the fitted vectorizer and transformer
            sentence_counts = self.vectorizer.transform([processed_sentence])
            sentence_tfidf = self.tfidf_transformer.transform(sentence_counts)
            prediction = self.classifier.predict(sentence_tfidf)[0]
            return prediction
        except Exception as e:
            print(f"Error predicting intent: {e}")
            return "default"

    def get_response(self, user_input):
        print(f"User input: {user_input}") # Debug print
        predicted_tag = self.predict_intent(user_input)
        print(f"Predicted tag: {predicted_tag}") # Debug print
        
        for intent in self.intents['intents']:
            if intent['tag'] == predicted_tag:
                responses = intent['responses']
                
                # Handle product search and category browse more dynamically
                if predicted_tag == "product_search":
                    # First, try to extract a specific product name
                    product_or_category_name = self._extract_entity(user_input, self.products, 'name')
                    print(f"Extracted entity for product_search (key=name): {product_or_category_name}") # Debug print
                    
                    # Check if the extracted entity is actually a category
                    if product_or_category_name and product_or_category_name in [p['category'] for p in self.products]:
                        category_name = product_or_category_name
                        print(f"Identified as category: {category_name}") # Debug print
                        found_products = [p for p in self.products if category_name.lower() in p['category'].lower()]
                        if found_products:
                            response_text = f"Here are some products in the {category_name} category:<br/>"
                            for p in found_products:
                                response_text += f"<div><b>{p['name']}</b><br/>"
                                response_text += f"Price: ${p['price']:.2f}<br/>"
                                response_text += f"Description: {p['description']}<br/>"
                                response_text += f"<img src=\"static/images/{p['image']}\" alt=\"{p['name']}\" width=\"100\"/><br/>"
                                response_text += f"<button class=\"btn btn-success btn-sm add-to-cart-btn\" data-product-id=\"{p['id']}\">Add to Cart</button></div><br/>"
                            return response_text
                        else:
                            return f"Sorry, I couldn't find any products in the '{category_name}' category."

                    elif product_or_category_name: # It's a specific product name
                        print(f"Identified as specific product: {product_or_category_name}") # Debug print
                        found_products = [p for p in self.products if product_or_category_name.lower() in p['name'].lower()]
                        if found_products:
                            response_text = f"Here are some products related to {product_or_category_name}:<br/>"
                            for p in found_products:
                                response_text += f"<div><b>{p['name']}</b> ({p['category']})<br/>"
                                response_text += f"Price: ${p['price']:.2f}<br/>"
                                response_text += f"Description: {p['description']}<br/>"
                                response_text += f"<img src=\"static/images/{p['image']}\" alt=\"{p['name']}\" width=\"100\"/><br/>"
                                response_text += f"<button class=\"btn btn-success btn-sm add-to-cart-btn\" data-product-id=\"{p['id']}\">Add to Cart</button></div><br/>"
                            return response_text
                        else:
                            return f"Sorry, I couldn't find any products related to '{product_or_category_name}'."
                    else:
                        return random.choice(responses) # Fallback to general response if no specific product/category found
                
                elif predicted_tag == "category_browse":
                    category_name = self._extract_entity(user_input, self.products, 'category')
                    print(f"Extracted entity for category_browse (key=category): {category_name}") # Debug print
                    if category_name:
                        found_products = [p for p in self.products if category_name.lower() in p['category'].lower()]
                        if found_products:
                            response_text = f"Here are some products in the {category_name} category:<br/>"
                            for p in found_products:
                                response_text += f"<div><b>{p['name']}</b><br/>"
                                response_text += f"Price: ${p['price']:.2f}<br/>"
                                response_text += f"Description: {p['description']}<br/>"
                                response_text += f"<img src=\"static/images/{p['image']}\" alt=\"{p['name']}\" width=\"100\"/><br/>"
                                response_text += f"<button class=\"btn btn-success btn-sm add-to-cart-btn\" data-product-id=\"{p['id']}\">Add to Cart</button></div><br/>"
                            return response_text
                        else:
                            return f"Sorry, I couldn't find any products in the '{category_name}' category."
                    else:
                        # List all categories if no specific category is mentioned
                        all_categories = sorted(list(set([p['category'] for p in self.products])))
                        return f"We have products in categories like: {', '.join(all_categories)}. Which one are you interested in?"

                elif predicted_tag == "price_inquiry":
                    product_name = self._extract_entity(user_input, self.products, 'name')
                    print(f"Extracted entity for price_inquiry (key=name): {product_name}") # Debug print
                    if product_name:
                        found_product = next((p for p in self.products if product_name.lower() in p['name'].lower()), None)
                        if found_product:
                            return random.choice(responses).format(product=found_product['name'], price=f"${found_product['price']:.2f}")
                        else:
                            return f"Sorry, I couldn't find price information for '{product_name}'."
                    else:
                        return "Which product's price are you interested in?"

                return random.choice(responses)

        return random.choice(self.intents['intents'][len(self.intents['intents'])-1]['responses']) # Fallback to default if no intent matches

    def _extract_entity(self, text, data_list, key):
        text_lower = text.lower()

        # 1. Prioritize finding exact matches from the data_list (product names or categories)
        for item in data_list:
            if key in item:
                item_value = item[key]
                item_value_lower = item_value.lower()
                
                # Check for exact word or phrase match within the text
                if re.search(r'\b' + re.escape(item_value_lower) + r'\b', text_lower):
                    return item_value
                
                # For multi-word items, check if all component words are present
                words_in_item = item_value_lower.split()
                if len(words_in_item) > 1 and all(word in text_lower for word in words_in_item):
                    return item_value

        # 2. Fallback to more generic keyword matching to suggest categories based on product types
        # This section will now return category names for general product type queries
        if "book" in text_lower or "novel" in text_lower:
            return "Books" # Return category for a general book query
        if "headphone" in text_lower:
            return "Electronics" # Return category for a general headphone query
        if "watch" in text_lower:
            return "Electronics" # Return category for a general watch query
        if "shirt" in text_lower or "t-shirt" in text_lower:
            return "Clothing" # Return category for a general shirt query
        if "shoe" in text_lower:
            return "Clothing" # Return category for a general shoe query

        # Explicit category keywords still return their category name directly
        if "electronics" in text_lower:
            return "Electronics"
        if "clothing" in text_lower:
            return "Clothing"
        if "books" in text_lower:
            return "Books"
        
        return None 