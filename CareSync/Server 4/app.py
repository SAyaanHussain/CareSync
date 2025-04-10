from flask import Flask, request, jsonify, render_template
import openai
import re
from pymongo import MongoClient
from datetime import datetime
import ssl
import logging

app = Flask(__name__)
openai.api_key = 'sk-KEY'

# Create a custom SSL context that does not verify certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Connect to MongoDB with custom SSL context
try:
    client = MongoClient('DATABASE', tls=True, tlsAllowInvalidCertificates=True)
    db = client['CareSync']
    collection = db['fitness_plans']
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")

@app.route('/fitness-plans')
def index():
    return render_template('index.html')

@app.route('/submit_goal', methods=['POST'])
def submit_goal():
    data = request.get_json()
    age = data.get('age')
    gender = data.get('gender')
    goal = data.get('goal')
    diseases = data.get('diseases')
    days = data.get('days')
    dietary = data.get('dietary')
    prompt = f"Generate a highly accurate and personalized 7-day fitness and dietary plan for the respective person, based on their Age: {age}, Gender: {gender}, Fitness Goal: {goal}, and most importantly, Number of days: {days}, Health Conditions: {diseases or 'None'} and keep in mind if they are vegetarian or non-vegetarian so their diet is, {dietary}. So write the fitness plan first and then write down what the person should eat, no need to give what to eat for breakfast and all but just generalise the diet. Give day wise routine but do not just say 'repeat' and do not club days like day1+day5 do this no..."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fitness expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        ai_response = response['choices'][0]['message']['content'].strip()

        # Format the response using regular expressions
        ai_response = re.sub(r'(\bDay\s\d\b)', r'<h3>\1</h3>', ai_response)
        ai_response = re.sub(r'(Fitness Plan:)', r'<h2>\1</h2>', ai_response)
        ai_response = re.sub(r'(Diet Plan:)', r'<h2>\1</h2>', ai_response)
        ai_response = re.sub(r'\n\n', r'</p><p>', ai_response)
        ai_response = f"<p>{ai_response}</p>"

        # Store the response in MongoDB
        record = {
            "age": age,
            "gender": gender,
            "goal": goal,
            "diseases": diseases,
            "days": days,
            "response": ai_response,
            "timestamp": datetime.utcnow()
        }
        result = collection.insert_one(record)
        logging.info(f"Inserted document id: {result.inserted_id}")

    except Exception as e:
        logging.error(f"An error occurred while generating the response or storing in DB: {str(e)}")
        ai_response = f"An error occurred while generating the response: {str(e)}"

    return jsonify({"response": ai_response})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=4500)
