from mmanager.mmanager import Usecase

secret_key = 'YOUR_SECRET_KEY'
url = 'YOUR_API_URL'

usecase_data = {
    "name": "Fraud Detection",
    "description": "Detect fraud in transactions"
}

response = Usecase(secret_key, url).post_usecase(usecase_data)
print("Usecase created:", response)
