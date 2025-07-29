from mmanager.mmanager import Usecase

secret_key = 'YOUR_SECRET_KEY'
url = 'YOUR_API_URL'
usecase_id = 7

response = Usecase(secret_key, url).load_cache(usecase_id=usecase_id)
print("Cache loaded:", response)
