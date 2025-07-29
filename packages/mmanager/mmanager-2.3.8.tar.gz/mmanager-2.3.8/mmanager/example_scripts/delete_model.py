from mmanager.mmanager import Model

secret_key = "Secret-Key"

url = 'URL' #enter url
model_id = 'Model_id' #use model id

try:
    Model(secret_key,url).delete_model(model_id)
except ConnectionResetError as e:
    print(str(e))

