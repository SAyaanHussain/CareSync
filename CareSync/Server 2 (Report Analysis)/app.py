from flask import Flask, render_template, request
import openai
import os
from PyPDF2 import PdfReader
import re

app = Flask(__name__)
openai.api_key = 'sk-key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_report', methods=['POST'])
def submit_report():
    if 'pdfFile' not in request.files:
        return "No file part"
    
    file = request.files['pdfFile']
    
    if file.filename == '':
        return "No selected file"
    
    if file:
        file_path = os.path.join('uploads', 'report.pdf')
        file.save(file_path)
        response = analyze_report(file_path)
        return render_template('index.html', ai_response=response)

    return "Something went wrong"

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def analyze_report(file_path):
    text = extract_text_from_pdf(file_path)
    cleaned_text = re.sub(r'\s+', ' ', text)

    # Limit the input token length
    max_input_tokens = 2048
    truncated_content = cleaned_text[:max_input_tokens]

    # Call OpenAI API to analyze the report
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You will be given a medical report. You need to analyze it and provide a detailed analysis along with the patient's name written on top of the PDF. Elaborate on any abnormalities and potential diseases, and provide improvement suggestions and dietary/fitness plan improvements. If and only if the blood test is for malaria, dengue, typhoid, other major diseases, then you would add at the end that the report says that [those major diseases] are positive/negative (only mention this point if the blood test is especially inclined towards these points, else don't."},
            {"role": "user", "content": truncated_content}
        ],
        max_tokens=500
    )
    
    formatted_response = response.choices[0].message['content']

    # Format the response with HTML tags
    formatted_response = format_response(formatted_response)
    
    return formatted_response

def format_response(response):
    response = response.replace("\n", "<br>")
    response = re.sub(r'(Patient Name: [^\n]+)', r'<strong>\1</strong>', response)
    response = re.sub(r'(Detailed Analysis:)', r'<h4>\1</h4>', response)
    response = re.sub(r'(Improvement Suggestions:)', r'<h4>\1</h4>', response)
    response = re.sub(r'(Potential Diseases:)', r'<h4>\1</h4>', response)
    response = re.sub(r'(Dietary/Fitness Plan Improvements:)', r'<h4>\1</h4>', response)
    response = re.sub(r'(-)', r'<br>-', response)
    return response

if __name__ == '__main__':
    app.run(debug=True)
