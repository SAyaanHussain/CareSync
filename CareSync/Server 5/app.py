from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = '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'

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form.get('prompt')
    print(user_input)
    if not user_input:
        return jsonify({'response': 'Please provide a query.'})

    try:
        # Use your fine-tuned model
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI Model which diagnoses people. At the END of every message include that this is all based on training data and they should verify with their doctor."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150
        )

        ai_response = response.choices[0].message['content'].strip()
        return jsonify({'response': ai_response})

    except Exception as e:
        return jsonify({'response': 'An error occurred: ' + str(e)})




if __name__ == '__main__':
    app.run(debug=True, port=3555)
