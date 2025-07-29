from mmanager.mmanager import Usecase

secret_key = "Secret-Key"
url = 'URL' #enter url
path =  'api_assets'

data = {
    "name": "test usecase5",
    "author": "sssdsadads",
    "description": "sss",
    "source": "ssssdsdsa",
    "contributor": "sdadssdssddass",
    "image": '%s/project_assets/thumbnail.jpg' % path,
    "banner": '%s/project_assets/banner.jpg' % path,
}

try:
    Usecase(secret_key,url).post_usecase(data)
except ConnectionResetError as e:
    print(str(e))

        