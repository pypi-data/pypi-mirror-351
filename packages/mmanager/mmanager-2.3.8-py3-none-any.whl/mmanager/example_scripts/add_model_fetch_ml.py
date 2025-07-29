from mmanager.mmanager import Model
secret_key = '0fc94b1d5b7d916d143c070f29bccc1614977c2d'
url = 'http://localhost:8000'
model_data = {
    "project": 71, #Project ID or Usecase ID
    "transformerType": "Classification", #Options: Classification, Regression, Forcasting
    "training_dataset": "",
    "test_dataset": "",
    "pred_dataset": "",
    "actual_dataset": "",
    "model_file_path": "", 
    "target_column": "label", #Target Column
    "note": "" #Short description of Model
    }

ml_options = {
    "credPath": "config.json", #Path to Azure ML credential files.
    "datasetinsertionType": "AzureML", #Option: AzureML, Manual
    "fetchOption": ["Model", "Dataset"], #To fetch model, add ["Model", "Dataset"] to fetch both model and datasets.
    "modelName": "model_18_2022_05_31_203641", #Fetch model file registered with model name.
    "dataPath": "dataset_18_2022_02_13_223137", #Get datasets registered with dataset name.
    }
Model(secret_key, url).post_model(model_data, ml_options)