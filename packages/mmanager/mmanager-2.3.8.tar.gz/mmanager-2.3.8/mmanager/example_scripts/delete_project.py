from mmanager.mmanager import Usecase

secret_key = "Secret-Key" 

url = 'URL' #enter url
project_id ='Project_id'

try:
    Usecase(secret_key,url).delete_usecase(project_id)
except ConnectionResetError as e:
    print(str(e))
