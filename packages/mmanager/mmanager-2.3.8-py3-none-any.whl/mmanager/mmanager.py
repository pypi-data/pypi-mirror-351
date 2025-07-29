import os
import json
import requests
import traceback
import sys
from .dataresource import *
from .serverequest import *
from .log_keeper import *
from colorama import Fore
from IPython.display import HTML, IFrame

class ModelManager:
    """
    Core manager for API requests, authentication, and logging within the Model Manager system.
    Supplies centralized request and error handling for all subclasses.
    """
    def  __init__(self, secret_key, base_url):
        self.base_url = base_url
        self.project_data = {}
        self.secret_key = secret_key

    def _get_headers(self, **kwargs):
        """
        Constructs the HTTP headers required for API requests.

        Returns:
            dict: A dictionary containing the Authorization header with the secret key.
        """
        return {'Authorization': f'secret-key {self.secret_key}'}

    def _send_request(self, method: str, url: str, data=None, files=None, headers=None, **kwargs):
        """
        Sends an HTTP request using the specified method, URL, and parameters.

        Args:
            method (str): The HTTP method to use ('get', 'post', 'patch', 'delete').
            url (str): The endpoint URL for the request.
            data (dict, optional): Data to send in the body of the request (for POST/PATCH).
            files (dict, optional): Files to send in the request (for POST/PATCH).
            headers (dict, optional): Custom headers for the request. If not provided, uses self._get_headers().
            **kwargs: Additional arguments passed to the requests method.

        Returns:
            requests.Response or Exception: The response object from the requests library if successful, otherwise the exception object.
        """
        if headers is None:
            headers = self._get_headers()
        try:
            if method == 'post':
                resp = requests.post(url, data=data, files=files, headers=headers, **kwargs)
            elif method == 'patch':
                resp = requests.patch(url, data=data, files=files, headers=headers, **kwargs)
            elif method == 'delete':
                resp = requests.delete(url, headers=headers, **kwargs)
            elif method == 'get':
                resp = requests.get(url, headers=headers, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            return resp
        except Exception as e:
            self._logger(exception_msg=str(e))
            return e

    def _logger(self, resp=None, task=None, exception_msg=None):
        """
        Logs the status and errors of HTTP requests or exceptions.

        Args:
            resp: The response object returned by the requests library (optional).
            task: A string describing the task being logged (optional).
            exception_msg: An exception message to log as an error (optional).

        Behavior:
            - If exception_msg is provided, logs it as an error.
            - If resp is provided, logs success for status codes 200, 201, 204.
        """
        import requests
        if exception_msg:
            logger.error(f"Error message: {exception_msg}")
            return
        if isinstance(resp, requests.Response):
            if resp.status_code in (200, 201, 204):
                logger.info(f"Success: {task}")
            else:
                logger.error(f"Failed: {task} | Status: {resp.status_code} | Response: {getattr(resp, 'text', '')}")
                try:
                    resp_json = resp.json()
                    error_msg = (
                        resp_json.get("name", [None])[0] if isinstance(resp_json.get("name"), list) and resp_json.get("name")
                        else resp_json.get("detail")
                        or next(iter(resp_json.values()), None)
                    )
                    if error_msg:
                        logger.error(f"{Fore.RED}Error message: {error_msg}")
                except Exception:
                    pass

            
    
class ReleaseTable(ModelManager):
    """
    API interface for creating and updating release table entries related to model deployment.
    """
    def post(self, data):
        """
        Sends a PATCH request to update or create a release table entry.

        Args:
            data (dict): The data to be sent in the PATCH request for the release table.

        Returns:
            requests.Response or Exception: The response object from the requests library if successful, otherwise the exception object.
        """
        url = f"{self.base_url}/api/releaseTable/"
        resp = self._send_request('patch', url, data=data)
        self._logger(resp=resp, task="Post Release Table")
        return resp

class Usecase(ModelManager):
    """
    Manages CRUD operations for usecases, including forecasting fields and file uploads.
    """
    def post_usecase(self, usecase_info: dict, forecasting_fields: dict = None, forecasting_feature_tabs: dict = None) -> requests.Response:
        """
        Creates a new usecase by sending a POST request with the provided information.

        Args:
            usecase_info (dict): Information about the usecase, including optional 'image' and 'banner' file paths.
            forecasting_fields (dict, optional): Additional forecasting fields to include if usecase_type is 'Forecasting'.
            forecasting_feature_tabs (dict, optional): Additional forecasting feature tabs to include if usecase_type is 'Forecasting'.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/projects/"
        files = {}
        data = {k: v for k, v in usecase_info.items() if k not in ['image', 'banner']}
        image_p = usecase_info.get('image')
        banner_p = usecase_info.get('banner')
        try:
            if image_p:
                files['image'] = open(image_p, 'rb')
            if banner_p:
                files['banner'] = open(banner_p, 'rb')
            if usecase_info.get("usecase_type") == "Forecasting":
                if forecasting_fields:
                    data.update(forecasting_fields)
                if forecasting_feature_tabs:
                    data.update(forecasting_feature_tabs)
            response = self._send_request('post', url, data=data, files=files)
            self._logger(resp=response, task="Post usecase")
            return response
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=e)
            return e
        finally:
            for f in files.values():
                try:
                    f.close()
                except Exception as close_exc:
                    logger.warning(f"Failed to close file: {close_exc}")

    def patch_usecase(self, usecase_data: dict, usecase_id: str) -> requests.Response:
        """
        Updates an existing usecase by sending a PATCH request with the provided data.

        Args:
            usecase_data (dict): The updated usecase information, including optional 'image' and 'banner' file paths.
            usecase_id (str): The ID of the usecase to update.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/projects/{usecase_id}/"
        files = {}
        data = {k: v for k, v in usecase_data.items() if k not in ['image', 'banner']}
        image_p = usecase_data.get('image')
        banner_p = usecase_data.get('banner')
        try:
            if image_p:
                files['image'] = open(image_p, 'rb')
            if banner_p:
                files['banner'] = open(banner_p, 'rb')
            response = self._send_request('patch', url, data=data, files=files)
            self._logger(resp=response, task="Update usecase")
            return response
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=e)
            return e
        finally:
            for f in files.values():
                try:
                    f.close()
                except Exception as close_exc:
                    logger.warning(f"Failed to close file: {close_exc}")

    def delete_usecase(self, usecase_id: str) -> requests.Response:
        """
        Deletes a usecase by its ID.

        Args:
            usecase_id (str): The ID of the usecase to delete.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/projects/{usecase_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete usecase")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp

    def get_usecases(self) -> requests.Response:
        """
        Retrieves all usecases from the server.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/projects/get_usecases/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get usecases")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp

    def get_detail(self, usecase_id: str) -> requests.Response:
        """
        Retrieves the details of a specific usecase by ID.

        Args:
            usecase_id (str): The ID of the usecase to retrieve.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/projects/{usecase_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get usecase detail")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp

    def get_models(self, usecase_id: str) -> requests.Response:
        """
        Retrieves all models associated with a specific usecase ID.

        Args:
            usecase_id (str): The ID of the usecase for which to retrieve models.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/projects/getmodels/?usecase_id={usecase_id}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Models")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp

    def load_cache(self, usecase_id: str) -> requests.Response:
        """
        Loads cached data for a specific usecase ID.

        Args:
            usecase_id (str): The ID of the usecase for which to load cached data.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/projects/data_loadcache/?usecase_id={usecase_id}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Load Data Cache")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp

class Applications(ModelManager):
    """
    Handles creation and retrieval of application entities.
    """
    
    def post_application(self, data: dict) -> object:
        """
        Sends a POST request to create a new application.

        Args:
            data (dict): The data to be sent in the POST request for the application.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/applications/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Post Application")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp
    
    def delete_application(self, usecase_id: str) -> object:
        """
        Sends a DELETE request to remove an application by usecase ID.

        Args:
            usecase_id (str): The ID of the usecase/application to delete.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/applications/{usecase_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete Application")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp
    
    def get_applications(self) -> object:
        """
        Retrieves all applications from the server.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/applications/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Applications")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp

class ExternalDatabase(ModelManager):
    """
    Manages linking, retrieval, and deletion of external databases.
    """
    """
    Handles operations related to external databases, such as linking and retrieving related DBs.
    """
    def post_related_db(self, data: dict) -> object:
        """
        Create or update a related external database entry.
        Args:
            data (dict): The data for the related database.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/related_db/"
        response = self._send_request('post', url, data=data)
        self._logger(resp=response, task="Post Related Database")
        return response

    def get_related_db(self, data: dict) -> object:
        """
        Retrieve information about related external databases.
        Args:
            data (dict): Query parameters or data for the request.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/related_db/"
        response = self._send_request('get', url, data=data)
        self._logger(resp=response, task="Get Related Database")
        return response

    def link_externaldb(self, data: dict) -> object:
        """
        Link an external database to the system.
        Args:
            data (dict): The linking data for the external database.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/externaldb_link/"
        response = self._send_request('post', url, data=data)
        self._logger(resp=response, task="Post Database Link")
        return response

    
    def get_externaldb_links(self) -> object:
        """
        Retrieve all external database links registered in the system.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/externaldb_link/"
        response = self._send_request('get', url)
        self._logger(resp=response, task="Get Database Link")
        return response

from IPython.display import display, HTML

class Model(ModelManager):

    def post_model(self, model_data: dict, ml_options: dict = None, data_distribution: bool = True) -> object:
        """
        Creates a new model by sending a POST request with the provided model data and options.

        Args:
            model_data (dict): Information about the model.
            ml_options (dict, optional): Additional machine learning options to include.
            data_distribution (bool, optional): Whether to include data distribution information. Defaults to True.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        from .dataresource import get_files_cm
        if ml_options is None:
            ml_options = {}
        url = f"{self.base_url}/api/models/"
        try:
            if not isinstance(model_data, dict):
                model_data = dict(model_data) if model_data is not None else {}
            model_data.update(ml_options)
            model_data["data_distribution"] = data_distribution
            data = get_model_data(model_data)
            with get_files_cm(model_data) as files:
                resp = self._send_request('post', url, data=data, files=files)
                self._logger(resp=resp, task="Post Model")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            return e
        return resp

    
    def delete_model(self, model_id: str) -> object:
        """
        Deletes a model by its ID.

        Args:
            model_id (str): The ID of the model to delete.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/models/{model_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete Model")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            resp = e
        return resp


    def patch_model(self, model_data: dict, model_id: str, create_sweetviz: bool = True) -> object:
        """
        Updates an existing model by sending a PATCH request with the provided data.

        Args:
            model_data (dict): The updated model information.
            model_id (str): The ID of the model to update.
            create_sweetviz (bool, optional): Whether to create a Sweetviz report. Defaults to True.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/models/{model_id}/"
        try:
            data = dict(model_data)
            data["create_sweetviz"] = create_sweetviz
            files = get_files(model_data)
            resp = self._send_request('patch', url, data=data, files=files)
            self._logger(resp=resp, task="Update Model")
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred", exc_info=True)
            return e
        finally:
            for f in getattr(files, 'values', lambda: [])():
                try:
                    f.close()
                except Exception as close_exc:
                    logger.warning(f"Failed to close file: {close_exc}")
        return resp


    def generate_report(self, model_id: str) -> object:
        """
        Generates a governance report for the specified model.

        Args:
            model_id (str): The ID of the model for which to generate the report.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/govrnreport/{model_id}/generateReport/"
        try:
            resp = self._send_request('post', url)
            self._logger(resp=resp, task="Generate Report")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp


    def get_details(self, model_id: str) -> object:
        """
        Retrieves the details of a specific model by ID.

        Args:
            model_id (str): The ID of the model to retrieve.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/models/{model_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Model Details")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    
    def get_latest_metrics(self, model_id: str, metric_type: str) -> object:
        """
        Retrieves the latest metrics for a specific model and metric type.

        Args:
            model_id (str): The ID of the model.
            metric_type (str): The type of metric to retrieve.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/models/get_latest_metrics/?model_id={model_id}&&metric_type={metric_type}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Latest Model Metrics")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp


    def get_all_reports(self, model_id: str) -> object:
        """
        Retrieves all reports associated with a specific model.

        Args:
            model_id (str): The ID of the model for which to retrieve reports.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/models/get_all_reports/?model_id={model_id}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Model Reports")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    
    def create_insight(self, model_id: str) -> object:
        """
        Creates an insight for a specific model.

        Args:
            model_id (str): The ID of the model for which to create the insight.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/insight/create_insight/?model_id={model_id}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Create Insight")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    
    def create_causalgraph(self, model_id: str, target_col: str, algorithm: str) -> object:
        """
        Creates a causal graph for the given model, target column, and algorithm.

        Args:
            model_id (str): The ID of the model.
            target_col (str): The target column for causal discovery.
            algorithm (str): The algorithm to use for causal discovery.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/CausalGraph/{model_id}/create_causalgraph/?target_col={target_col}&&algorithm={algorithm}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Create Causal Graph")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    
    def get_causal_discovery_graphs(self, model_id: str, graph_type: str) -> object:
        """
        Retrieves causal discovery graphs for a given model and graph type.

        Args:
            model_id (str): The ID of the model.
            graph_type (str): The type of graph to retrieve.

        Returns:
            HTML object with the graph content, or Exception.
        """
        url = f"{self.base_url}/api/PyCausalD3Graph/{model_id}/get_discovery_graphs/?graph_type={graph_type}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Causal Discovery")
            html_content = resp.json().get(graph_type)
            return HTML(html_content)
        except Exception as e:
            self._logger(exception_msg=str(e))
            logger.exception("Exception occurred")
            return e

    
    def get_causal_inference_graphs(self, model_id: str, graph_type: str, treatment: str = None, outcome: str = None) -> object:
        """
        Retrieves causal inference graphs for a given model.

        Args:
            model_id (str): The ID of the model.
            graph_type (str): The type of graph to retrieve.
            treatment (str, optional): Treatment variable.
            outcome (str, optional): Outcome variable.

        Returns:
            HTML object with the graph content, or Exception.
        """
        if treatment and outcome:
            url = f"{self.base_url}/api/PyCausalInference/{model_id}/create_inference_graphs/?treatment={treatment}&&outcome={outcome}"
        else:
            url = f"{self.base_url}/api/PyCausalInference/{model_id}/create_inference_graphs/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Causal Inference")
            html_content = resp.json().get(graph_type)
            return HTML(html_content)
        except Exception as e:
            self._logger(exception_msg=str(e))
            return e

    
    def get_causal_inference_correlation(self, model_id: str, graph_type: str, treatment: str, outcome: str) -> object:
        """
        Retrieves causal inference correlation for a given model.

        Args:
            model_id (str): The ID of the model.
            graph_type (str): The type of graph/correlation to retrieve.
            treatment (str): The treatment variable.
            outcome (str): The outcome variable.

        Returns:
            HTML object with the correlation content, or Exception.
        """
        url = f"{self.base_url}/api/PyCausalInference-Correlation/{model_id}/create_correlation/?treatment={treatment}&&outcome={outcome}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Causal Inference Correlation")
            html_content = resp.json().get(graph_type)
            if graph_type == "causal_correlation_summary":
                html_content = f"<pre>{html_content}</pre>"
            return HTML(html_content)
        except Exception as e:
            self._logger(exception_msg=str(e))
            return e

    def get_causal_discovery_metrics(self, model_id: str, parse_json: bool = True) -> object:
        """
        Retrieve causal discovery metrics for a given model.

        Args:
            model_id (str): The unique identifier of the model.
            parse_json (bool, optional): If True (default), returns the parsed JSON content from the response if successful.
                If False, returns the raw requests.Response object.

        Returns:
            dict or requests.Response or Exception: If parse_json is True and the request is successful, returns a dictionary of metrics.
            If parse_json is False, returns the raw response object. If the request fails, returns the exception.

        Example structure of returned dict (if parse_json=True):
            {
                "metrics": [...],
                ...
            }
        """
        url = f"{self.base_url}/api/PyCausalD3Graph/{model_id}/get_metric_list_score/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Causal Discovery Metrics")
            if parse_json and hasattr(resp, 'json'):
                try:
                    return resp.json()
                except Exception as json_exc:
                    self._logger(exception_msg=f"JSON decode error: {json_exc}")
                    return resp
            return resp
        except Exception as e:
            self._logger(exception_msg=str(e))
            if 'logger' in globals():
                logger.exception("Exception occurred")
            return e

    def get_wit(self, model_id: str) -> object:
        """
        Retrieves the What-If Tool (WIT) visualization for a given model.

        Args:
            model_id (str): The ID of the model.

        Returns:
            IFrame with the WIT visualization, or Exception.
        """
        url = f"{self.base_url}/api/getFeature/{model_id}/get_wit_url/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get What If Analysis")
            wit_url = resp.json().get('wit_url')
            if wit_url:
                full_url = f"{self.base_url}{wit_url}"
                return IFrame(full_url, width=1500, height=800)
            return None
        except Exception as e:
            self._logger(exception_msg=str(e))
            return e

    
    def get_netron(self, model_id: str) -> object:
        """
        Retrieves the Netron visualization for a given model.

        Args:
            model_id (str): The ID of the model.

        Returns:
            IFrame with the Netron visualization, or Exception.
        """
        url = f"{self.base_url}/api/getFeature/{model_id}/get_netron_url/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Netron")
            netron_url = resp.json().get('netron_url')
            if netron_url:
                full_url = f"{self.base_url}{netron_url}"
                return IFrame(full_url, width=1500, height=800)
            return None
        except Exception as e:
            self._logger(exception_msg=str(e))
            return e


    def get_data_distribution(self, model_id: str) -> object:
        """
        Retrieves the data distribution visualization for a given model.

        Args:
            model_id (str): The ID of the model.

        Returns:
            IFrame with the data distribution visualization, or Exception.
        """
        url = f"{self.base_url}/api/getFeature/{model_id}/get_data_distribution_url/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Data Distribution")
            data_distribution_url = resp.json().get('data_distribution_url')
            if data_distribution_url:
                full_url = f"{self.base_url}{data_distribution_url}"
                return IFrame(full_url, width=1500, height=800)
            return None
        except Exception as e:
            self._logger(exception_msg=str(e))
            return e

    def get_causal_insights(self, input_data: dict) -> object:
        """
        Retrieves the causal insights for a given file path.

        Args:
            input_data (dict): The input data for the causal insights.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        treatment = input_data.get("treatment", None)
        outcome = input_data.get("outcome", None)
        file_path = input_data.get("file_path", None)

        print(treatment, outcome, file_path)

        if not file_path:
            return Exception("File path is required")
        
        url = f"{self.base_url}/api/PyCausalInferenceSingleFile/post_inference_graphs/"
        data = {
            "treatment": treatment,
            "outcome": outcome
        }

        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                resp = self._send_request('post', url, files=files, data=data)
            self._logger(resp=resp, task="Get Causal Insights")
            return resp
        except Exception as e:
            self._logger(exception_msg=str(e))
            return e

class TableInfo(ModelManager):
    """
    Handles CRUD operations for table metadata linked to datasets or models.
    """
    def post_table_info(self, data: dict) -> object:
        """
        Sends a POST request to create new table information.

        Args:
            data (dict): The data to be sent in the POST request.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/table_info/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Post Table Info")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def delete_table_info(self, table_id: str) -> object:
        """
        Deletes table information by its ID.

        Args:
            table_id (str): The ID of the table information to delete.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/table_info/{table_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete Table Info")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_table_info(self, table_id: str) -> object:
        """
        Retrieves table information by its ID.

        Args:
            table_id (str): The ID of the table information to retrieve.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/table_info/{table_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Table Info")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    
class FieldInfo(ModelManager):
    """
    Handles CRUD operations for field metadata associated with datasets or models.
    """
    def post_field_info(self, data: dict) -> object:
        """
        Sends a POST request to create new field information.

        Args:
            data (dict): The data to be sent in the POST request.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/field_info/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Post Field Info")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def delete_field_info(self, field_id: str) -> object:
        """
        Deletes field information by its ID.

        Args:
            field_id (str): The ID of the field information to delete.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/field_info/{field_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete Field Info")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_field_info(self, field_id: str) -> object:
        """
        Retrieves field information by its ID.

        Args:
            field_id (str): The ID of the field information to retrieve.

        Returns:
            requests.Response or Exception: The response object if successful, otherwise the exception.
        """
        url = f"{self.base_url}/api/field_info/{field_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Field Info")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    
class LLMCreds(ModelManager):
    def post(self, data: dict) -> object:
        """
        Sends a POST request to create new LLM credentials.
        Args:
            data (dict): The data to be sent in the POST request.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/llmCreds/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Post LLM Creds")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def delete_llm_creds(self, llmCreds_id: str) -> object:
        """
        Deletes LLM credentials by ID.
        Args:
            llmCreds_id (str): The ID of the LLM credentials to delete.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/llmCreds/{llmCreds_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete LLM Credentials")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_llm_creds(self, llmCreds_id: str) -> object:
        """
        Retrieves LLM credentials by ID.
        Args:
            llmCreds_id (str): The ID of the LLM credentials to retrieve.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/llmCreds/{llmCreds_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get LLM Credentials Info")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp


class RelatedDatabase(ModelManager):
    def post_related_db(self, data: dict) -> object:
        """
        Sends a POST request to create a related database entry.
        Args:
            data (dict): The data to be sent in the POST request.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/related_db/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Post Related Database")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def delete_related_db(self, related_db_id: str) -> object:
        """
        Deletes a related database entry by ID.
        Args:
            related_db_id (str): The ID of the related database entry to delete.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/related_db/{related_db_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete Related Database")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_related_db(self, related_db_id: str) -> object:
        """
        Retrieves a related database entry by ID.
        Args:
            related_db_id (str): The ID of the related database entry to retrieve.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/related_db/{related_db_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Related Database")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp


class DatabaseLink(ModelManager):
    def post_db_link(self, data: dict) -> object:
        """
        Sends a POST request to create a new external database link.
        Args:
            data (dict): The data to be sent in the POST request.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/externaldb_link/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Post Database Link")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def delete_db_link(self, db_link_id: str) -> object:
        """
        Deletes an external database link by ID.
        Args:
            db_link_id (str): The ID of the database link to delete.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/externaldb_link/{db_link_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete Database Link")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_externaldb_link(self, db_link_id: str) -> object:
        """
        Retrieves an external database link by ID.
        Args:
            db_link_id (str): The ID of the database link to retrieve.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/externaldb_link/{db_link_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Database Link")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp


class MLFlow(ModelManager):
    """
    Manages MLFlow credentials and dataset/model artifact downloads.
    """
    def post_mlflow_creds(self, data: dict) -> object:
        """
        Sends a POST request to create new MLFlow credentials.
        Args:
            data (dict): The data to be sent in the POST request.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/mlflow_creds/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Post MLFlow Creds")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def delete_mlflow_creds(self, mlflow_creds_id: str) -> object:
        """
        Deletes MLFlow credentials by ID.
        Args:
            mlflow_creds_id (str): The ID of the MLFlow credentials to delete.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/mlflow_creds/{mlflow_creds_id}/"
        try:
            resp = self._send_request('delete', url)
            self._logger(resp=resp, task="Delete MLFlow Creds")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_mlflow_creds(self, mlflow_creds_id: str) -> object:
        """
        Retrieves MLFlow credentials by ID.
        Args:
            mlflow_creds_id (str): The ID of the MLFlow credentials to retrieve.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/mlflow_creds/{mlflow_creds_id}/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get MLFlow Creds")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def download_dataset_model(self, mlflow_cred_id: str, exp_name: str, run_id: str = '', artifact_path: str = '') -> object:
        """
        Downloads datasets and model from MLFlow.
        Args:
            mlflow_cred_id (str): The MLFlow credential ID.
            exp_name (str): The experiment name.
            run_id (str, optional): The run ID.
            artifact_path (str, optional): The artifact path.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/ml_flow/get_tmp_dataset_model_path/?exp_name={exp_name}&&mlflow_id={mlflow_cred_id}&&run_id={run_id}&&artifact_path={artifact_path}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Download MLFlow Dataset/Model")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp


class WhatIf(ModelManager):
    """
    Uploads resources and builds What-If analysis tools for models.
    """
    def post_wit_files(self, data: dict) -> object:
        """
        Sends a POST request to upload WIT resources.
        Args:
            data (dict): The data to be sent in the POST request, including file paths.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/wit_files/"
        files = {}
        file_path = data.get('file', None)
        if file_path:
            files['file'] = open(file_path, 'rb')
        try:
            resp = self._send_request('post', url, data=data, files=files if files else None)
            self._logger(resp=resp, task="WIT Resources Added")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred")
            resp = Exception("Exception occurred")
        finally:
            for f in files.values():
                f.close()
        return resp

    def post_img_cls_wit_files(self, data: dict) -> object:
        """
        Sends a POST request to upload image classification WIT resources.
        Args:
            data (dict): The data to be sent in the POST request, including file paths.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/wit_files/img_cls/"
        files = {}
        files_list = ["input_model", "input_zip", "dicom_zipfile", "dicom_labelfile"]
        for key in files_list:
            file_path = data.get(key)
            if file_path:
                files[key] = open(file_path, 'rb')
        try:
            resp = self._send_request('post', url, data=data, files=files if files else None)
            self._logger(resp=resp, task="WIT Image Classification Resources Added")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred")
            resp = Exception("Exception occurred")
        finally:
            for f in files.values():
                f.close()
        return resp

    def build_wit(self, model_id: str) -> object:
        """
        Builds the What If Analysis Tool for a given model.
        Args:
            model_id (str): The ID of the model.
        Returns:
            Response object or Exception
        """
        url = f"{self.base_url}/api/buildWIT/{model_id}/build_whatif/"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Build What If Analysis Tool")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp


class VersionControl(ModelManager):
    """
    Handles Git/DVC configuration, version tagging, switching, and dataset export.
    """
    def git_config(self, data: dict) -> object:
        """
        Post Git configuration for version control integration.

        Args:
            data (dict): Git configuration parameters.
        Returns:
            Response object or Exception if the request fails.
        """
        url = f"{self.base_url}/api/git-config/"
        try:
            resp = self._send_request('post', url, data=data)
            self._logger(resp=resp, task="Git Config Added")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def dvc_set(self, git_config_id: str) -> object:
        """
        Set up Data Version Control (DVC) for a given Git configuration.

        Args:
            git_config_id (str): Git configuration identifier.
        Returns:
            Response object or Exception if the request fails.
        """
        url = f"{self.base_url}/api/dvc_git_setup/{git_config_id}/set/?is_notebook=True"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Data Version Control Setup Successful")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_version_tags(self, model_id: str, usecase_id: str) -> object:
        """
        Retrieve all version tags for a specific model and usecase.

        Args:
            model_id (str): Model identifier.
            usecase_id (str): Usecase identifier.
        Returns:
            Response object or Exception if the request fails.
        """
        url = f"{self.base_url}/api/dataVersion/versioning_tags/?model_id={model_id}&&usecase_id={usecase_id}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Fetch Data Versions With Tags")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def get_version_details(self, tag_name: str) -> object:
        """
        Retrieve details for a specific data version tag.

        Args:
            tag_name (str): Version tag name.
        Returns:
            Response object or Exception if the request fails.
        """
        url = f"{self.base_url}/api/versioning/get_detail/?tag_name={tag_name}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task="Get Data Version Details")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def switch_data_version(self, model_id: str, usecase_id: str, tag_name: str) -> object:
        """
        Switch data version for a model and usecase to a specified tag.

        Args:
            model_id (str): Model identifier.
            usecase_id (str): Usecase identifier.
            tag_name (str): Version tag name.
        Returns:
            Response object or Exception if the request fails.
        """
        url = f"{self.base_url}/api/dataVersion/data_switch_version/?model_id={model_id}&&usecase_id={usecase_id}&&tag_name={tag_name}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task=f"Switched Data Versions To {tag_name}")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp

    def export_datasets(self, model_id: str, usecase_id: str, tag_name: str) -> object:
        """
        Export datasets for a given model, usecase, and version tag.

        Args:
            model_id (str): Model identifier.
            usecase_id (str): Usecase identifier.
            tag_name (str): Version tag name.
        Returns:
            Response object or Exception if the request fails.
        """
        url = f"{self.base_url}/api/dataVersion/export_datasets/?model_id={model_id}&&usecase_id={usecase_id}&&tag_name={tag_name}"
        try:
            resp = self._send_request('get', url)
            self._logger(resp=resp, task=f"Exported Datasets For {tag_name}")
        except Exception:
            self._logger(exception_msg="Exception occurred")
            logger.exception("Exception occurred", exc_info=True)
            resp = Exception("Exception occurred")
        return resp