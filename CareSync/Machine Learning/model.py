import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load the data from the CSV file
file_path = 'heart.csv'
data = pd.read_csv(file_path)

# Split the data into features (X) and target (y)
X = data.drop(columns='output')
y = data['output']

# Perform the train-test split (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create an instance of the Logistic Regression model
model = LogisticRegression(max_iter=1000)

# Train the model using the training data
model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = model.predict(X_test)

# Calculate the accuracy of the model
accuracy = accuracy_score(y_test, y_pred)

# Display the accuracy
print("Model Accuracy:", accuracy*100)

# Given values for prediction
new_data = pd.DataFrame({
    'age': [53],
    'sex': [1],
    'cp': [0],
    'trtbps': [123],
    'chol': [282],
    'fbs': [0],
    'restecg': [1],
    'thalachh': [95],
    'exng': [1],
    'oldpeak': [2],
    'slp': [1],
    'caa': [2],
    'thall': [3]
})

# Make prediction for the new data
new_pred = model.predict(new_data)

# Display the prediction
print("Prediction for the given values:", new_pred[0])
