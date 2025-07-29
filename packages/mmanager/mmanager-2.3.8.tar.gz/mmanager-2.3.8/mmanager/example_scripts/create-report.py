from mmanager.mmanager import Model
secret_key = 'secret-key'
url = 'URL'

model_id = "<model-id>" #use model_id number to delete
Model(secret_key,url).generate_report(model_id)