from mmanager.mmanager import Model
secret_key = '0fc94b1d5b7d916d143c070f29bccc1614977c2d'
url = 'http://localhost:8000'
path = 'assets' #path to csv file
model_data = {
    "project": 71, #Project ID or Usecase ID
    "transformerType": "Classification", #Options: Classification, Regression, Forcasting
    "training_dataset": "/home/mizal/Projects/mmanager/mmanager/assets/model_assets/train.csv",
    "test_dataset": "/home/mizal/Projects/mmanager/mmanager/assets/model_assets/test.csv",
    "pred_dataset": "/home/mizal/Projects/mmanager/mmanager/assets/model_assets/pred.csv",
    "actual_dataset": "/home/mizal/Projects/mmanager/mmanager/assets/model_assets/truth.csv",
    "model_file_path": "/home/mizal/Projects/mmanager/mmanager/assets/model_assets/model.h5",
    "target_column": "label", #Target Column
    "note": "This is using Onprem.", #Short description of Model
    "model_area": "Area API test."
    }

ml_options = {
    "credPath": "config.json", #Path to Azure ML credential files.
    "datasetinsertionType": "Manual", #Option: AzureML, Manual
    "registryOption": ["Model","Dataset"], #To register model, add ["Model", "Dataset"] to register both model and datasets.
    "datasetUploadPath": "api_test_upload_june8", #To registere dataset on path.
    }
Model(secret_key, url).post_model(model_data, ml_options)