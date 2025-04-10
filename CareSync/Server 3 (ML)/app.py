# 6846
from flask import Flask, request, render_template
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

app = Flask(__name__)

# Load the data from the CSV file
file_path = 'heart.csv'
data = pd.read_csv(file_path)

# we will get all columns except for output
X = data.drop(columns='output')
y = data['output']

# we use 80% of the data for training and testing for 20%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# instance of the algo
model = LogisticRegression(max_iter=1000)

# we use the training data
model.fit(X_train, y_train)

# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define the route for the prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get form data
    age = request.form['age']
    sex = request.form['gender']
    cp = request.form['cp']
    trtbps = request.form['trtbps']
    chol = request.form['chol']
    fbs = request.form['fbs']
    restecg = request.form['restecg']
    thalachh = request.form['thalachh']
    exng = request.form['exng']
    oldpeak = request.form['oldpeak']
    slp = request.form['slp']
    caa = request.form['caa']
    thall = request.form['thall']
    
    
    # Create a DataFrame with the input values
    new_data = pd.DataFrame({
        'age': [age],
        'sex': [sex],
        'cp': [cp],
        'trtbps': [trtbps],
        'chol': [chol],
        'fbs': [fbs],
        'restecg': [restecg],
        'thalachh': [thalachh],
        'exng': [exng],
        'oldpeak': [oldpeak],
        'slp': [slp],
        'caa': [caa],
        'thall': [thall]
    })

    # Make prediction for the new data
    new_pred = model.predict(new_data)
    
    # Determine the prediction message
    if new_pred[0] == 1:
        prediction_text = "There is some chance that your heart might have some disease."
        print(prediction_text)
    elif new_pred[0]==0:
        prediction_text = "Your heart seems to be healthy."
        print(prediction_text)
    return render_template('index.html', prediction=prediction_text)

if __name__ == '__main__':
    app.run(debug=True, port=6846)
