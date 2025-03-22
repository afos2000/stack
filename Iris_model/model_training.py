import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load Iris dataset
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)

# Train a logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

mlflow_url = "http://mlflow-server-service.mlflow:5000"
# mlflow_url = "http://localhost:5000"
mlflow.set_tracking_uri(mlflow_url)
mlflow.set_experiment('iris-model')
# Log the model and parameters in MLflow
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("test_size", 0.2)
    mlflow.log_param("random_state", 42)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)

    # Log model
    mlflow.sklearn.log_model(model, "logistic_regression_model")
