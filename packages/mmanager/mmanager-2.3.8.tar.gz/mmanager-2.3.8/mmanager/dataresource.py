"""
Data resource utilities for model and dataset handling in Model Manager.
Provides helpers for serializing options and preparing file objects for API requests.
"""

import json
from typing import Dict, Any


def get_model_data(model_data: dict) -> dict:
    """
    Prepare model data for API requests by serializing registry and fetch options.

    Args:
        model_data (dict): Model metadata and options.
    Returns:
        dict: Updated model data with serialized options if present.
    """
    data = model_data.copy()
    registry_option = data.get('registryOption')
    if registry_option is not None:
        data['registryOption'] = json.dumps(registry_option)
    fetch_option = data.get('fetchOption')
    if fetch_option is not None:
        data['fetchOption'] = json.dumps(fetch_option)
    return data


def file_mod(
    insertionType: str,
    field_name: str,
    mlflow_file_key: str,
    file_path: str
) -> Dict[str, Any]:
    """
    Prepare file object or file path for upload depending on insertion type.

    Args:
        insertionType (str): Type of dataset insertion (e.g., 'MLFlow').
        field_name (str): Key for standard file upload.
        mlflow_file_key (str): Key for MLFlow file upload.
        file_path (str): Path to the file.
    Returns:
        dict: Dictionary with the appropriate key and file object or path.
    """
    if insertionType == "MLFlow":
        return {mlflow_file_key: file_path}
    file = open(file_path, 'rb')
    return {field_name: file}


from contextlib import contextmanager

def get_files(model_data: dict) -> Dict[str, Any]:
    """
    Collect all relevant file objects or paths for model API requests (legacy, not context-managed).
    Args:
        model_data (dict): Model metadata including file paths.
    Returns:
        dict: Mapping of field names to file objects or paths.
    """
    key_pairs = [
        ("training_dataset", "train_file"),
        ("test_dataset", "test_file"),
        ("pred_dataset", "pred_file"),
        ("actual_dataset", "truth_file"),
        ("model_image_path", "model_image_file"),
        ("model_summary_path", "model_summary_file"),
        ("model_file_path", "model_file"),
    ]
    files = {}
    insertion_type = model_data.get("datasetinsertionType")
    for data_key, mlflow_key in key_pairs:
        file_path = model_data.get(data_key)
        if file_path:
            files.update(
                file_mod(
                    insertionType=insertion_type,
                    field_name=data_key,
                    mlflow_file_key=mlflow_key,
                    file_path=file_path
                )
            )
    return files

@contextmanager
def get_files_cm(model_data: dict):
    """
    Context manager to yield open file objects for API requests and ensure they are closed after use.
    Args:
        model_data (dict): Model metadata including file paths.
    Yields:
        dict: Mapping of field names to open file objects or paths.
    """
    key_pairs = [
        ("training_dataset", "train_file"),
        ("test_dataset", "test_file"),
        ("pred_dataset", "pred_file"),
        ("actual_dataset", "truth_file"),
        ("model_image_path", "model_image_file"),
        ("model_summary_path", "model_summary_file"),
        ("model_file_path", "model_file"),
    ]
    files = {}
    handles = []
    insertion_type = model_data.get("datasetinsertionType")
    try:
        for data_key, mlflow_key in key_pairs:
            file_path = model_data.get(data_key)
            if file_path:
                if insertion_type == "MLFlow":
                    files[mlflow_key] = file_path
                else:
                    f = open(file_path, 'rb')
                    files[data_key] = f
                    handles.append(f)
        yield files
    finally:
        for f in handles:
            try:
                f.close()
            except Exception:
                pass
