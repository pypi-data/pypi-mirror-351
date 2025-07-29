from mmanager.mmanager import Model

secret_key = 'YOUR_SECRET_KEY'
url = 'YOUR_API_URL'
usecase_id = '<usecase-id>'

model_data = {
    "project": usecase_id,
    "transformerType": "Classification",  # or Regression, Forecasting
    "training_dataset": "/path/train.csv",
    "test_dataset": "/path/test.csv",
    "target_column": "Class"
}

response = Model(secret_key, url).post_model(model_data)
print("Model created:", response)
