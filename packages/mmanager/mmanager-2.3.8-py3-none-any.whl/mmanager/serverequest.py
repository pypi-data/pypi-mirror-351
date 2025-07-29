"""
Server-side request utilities for credential loading, AzureML/MLFlow integration, and model API requests.
Handles credential management, data preparation, and robust error logging for model operations.
"""

import os
import json
import requests
from .log_keeper import *

def _load_credentials(ml_options: dict) -> dict:
    """
    Load credentials from a file path specified in ml_options.

    Args:
        ml_options (dict): Dictionary containing 'credPath'.
    Returns:
        dict: Loaded credentials.
    Raises:
        FileNotFoundError: If the credential file path is invalid.
    """
    cred_path = ml_options.get("credPath")
    if cred_path and os.path.exists(cred_path):
        with open(cred_path) as f:
            creds = json.load(f)
        logger.info(f"Loaded credentials from {cred_path}")
        return creds
    logger.error("Credential file path invalid.")
    raise FileNotFoundError("Credential file path invalid.")

def reg_ml(data: dict, ml_options: dict) -> dict:
    """
    Register model data with AzureML credentials and upload path.

    Args:
        data (dict): Model data to update.
        ml_options (dict): Options including credentials and upload path.
    Returns:
        dict: Updated model data with credentials and upload path.
    """
    dataset_upload_path = ml_options.get("datasetUploadPath")
    try:
        creds = _load_credentials(ml_options)
        data.update({"amlCred": json.dumps(creds), "datasetUploadPath": dataset_upload_path})
    except Exception:
        logger.exception("Exception occurred")
    return data

def fetch_ml(data: dict, ml_options: dict) -> dict:
    """
    Update model data with AzureML credentials and data path for fetching.

    Args:
        data (dict): Model data to update.
        ml_options (dict): Options including credentials and data path.
    Returns:
        dict: Updated model data with credentials and data path.
    """
    data_path = ml_options.get("dataPath")
    try:
        creds = _load_credentials(ml_options)
        data.update({"amlCred": json.dumps(creds), "dataPath": data_path})
    except Exception:
        logger.exception("Exception occurred")
    return data

def model_request(
    url: str,
    kwargs: dict,
    data: dict,
    ml_options: dict,
    files: dict
) -> requests.Response:
    """
    Send a model-related API request, handling different dataset insertion types.

    Args:
        url (str): Endpoint URL.
        kwargs (dict): Additional arguments, e.g., headers.
        data (dict): Model data.
        ml_options (dict): Options for credentials and upload/fetch.
        files (dict): File objects or paths for upload.
    Returns:
        requests.Response: The response object from the API call, or None on error.
    """
    insertion_type = data.get("datasetinsertionType")
    model = None
    try:
        if insertion_type == "Manual":
            if ml_options:
                data = reg_ml(data, ml_options)
            model = requests.post(url, data=data, files=files, headers=kwargs['headers'])
        elif insertion_type == "AzureML":
            data = fetch_ml(data, ml_options)
            data.update(files)
            model = requests.post(url, data=data, headers=kwargs['headers'])
        elif insertion_type == "MLFlow":
            for key in ['training_dataset', 'test_dataset', 'pred_dataset', 'actual_dataset', 'model_file_path']:
                data.pop(key, None)
            data.update(files)
            model = requests.post(url, data=data, headers=kwargs['headers'])
        else:
            data.update({"datasetinsertionType": "Manual"})
            model = requests.post(url, data=data, files=files, headers=kwargs['headers'])
    except Exception:
        logger.exception("Exception occurred")
    return model