from io import BytesIO, StringIO
import json
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import requests
from pydantic import ValidationError  # Import for handling Pydantic errors

import uuid
from datetime import datetime
from enum import StrEnum


from pydantic import BaseModel, Field


class ClientFunctionType(StrEnum):
    analytical_function = "analytical_function"
    feature_function = "feature_function"
    forecasting_function = "forecasting_function"


class ClientFeatureFunctionArgument(BaseModel):
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    default_value: Optional[str] = None


class ClientMinimalFeatureFunctionInfo(BaseModel):
    name: str
    function_type: ClientFunctionType
    short_description: Optional[str] = None
    description: Optional[str] = None


class ClientDetailedFeatureFunctionInfo(ClientMinimalFeatureFunctionInfo):
    arguments: List[ClientFeatureFunctionArgument] = []
    returns: Optional[ClientFeatureFunctionArgument] = None
    examples: Optional[str] = None


class ClientUser(BaseModel):
    id: uuid.UUID
    username: str
    first_name: Optional[str] = Field(
        default=None, alias="firstName"
    )  # Handle potential alias from server
    last_name: Optional[str] = Field(default=None, alias="lastName")
    email: Optional[str] = None
    token: Optional[str] = None

    class Config:
        populate_by_name = True  # Allow using alias for population


class ClientUserResponse(BaseModel):
    message: str
    user: ClientUser


class ClientTaskStatus(BaseModel):
    id: uuid.UUID
    status: str
    info: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ClientDatasetHistory(BaseModel):
    origin_datasets: List[str] = []
    origin_feature_function: Optional[str] = None


class ClientVoltusMetadata(
    BaseModel
):  # Represents the 'voltus' key in dataset metadata
    description: Optional[str] = None
    history: List[ClientDatasetHistory] = []


class ClientApiResponse(BaseModel):
    message: Union[str, List[str], Dict[str, Any]]
    task_id: Optional[Union[str, List[str]]] = None


class ClientRecipeInputColumn(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    unique_values: bool = False


class ClientMinimalRecipeInfo(BaseModel):
    name: str
    input_columns: List[ClientRecipeInputColumn] = Field(alias="input columns")

    class Config:
        populate_by_name = True


class ClientDetailedRecipeInfo(ClientMinimalRecipeInfo):
    description: Optional[str] = None
    use_cases: Optional[str] = Field(default=None, alias="use cases")
    tags: List[str] = []
    recipe: Dict[str, Any]

    class Config:
        populate_by_name = True


class ClientFilteredRecipesResponse(BaseModel):
    recipes: List[str]


class ClientTrainedModelInfo(BaseModel):
    name: str


class ClientTrainingProgressInfo(BaseModel):
    epoch: int
    total_epochs: int
    batch: int
    total_batches: int
    timestamp: str  # datetime could also be used if format is consistent


class ClientTrainingInfoMessage(BaseModel):
    message: str


# For generate_synthetic_data if file_format="json"
# The server might return a list of lists of dictionaries, where each inner list represents a DataFrame.
# For simplicity in the client, we will parse this into List[pd.DataFrame] if needed by the user,
# or the raw List[List[Dict[str,Any]]] directly from response.json() as before.
# The return type hint will reflect that the JSON part is List[Any] to indicate it's raw.

PROTOCOL: str = "http"

class VoltusClient:
    """
    A client for interacting with the Voltus feature store API.

    Attributes:
        api_url (str): The base URL of the Voltus API.
        token (str): The authentication token.
    """

    def __init__(self, api_base_url: str, token: str, verify_requests: bool = True):
        """
        Initializes the VoltusClient.

        Args:
            api_base_url: The base URL of the Voltus API.
            token: The authentication token for the user.
            verify_requests: Whether to verify SSL certificates for requests.
        """
        if api_base_url is None:
            raise ValueError(f"'api_base_url' is required. Got '{api_base_url}'")
        elif not isinstance(api_base_url, str):
            raise TypeError(
                f"'api_base_url' must be a string. Got {type(api_base_url)}"
            )

        if token is None:
            raise ValueError(f"'token' is required. Got '{token}'")
        elif not isinstance(token, str):
            raise TypeError(f"'token' must be a string. Got {type(token)}")

        self.url = (
            api_base_url.replace("\\", "/")
            .replace("https://", "")
            .replace("http://", "")
            .strip("/")
            .strip()
        )
        self.token = token
        self.verify_requests = verify_requests
        self.healthcheck()

        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/datasets/examples/list",  # This endpoint does not require auth
            headers={
                # "Authorization": f"Bearer {self.token}", # Not strictly needed but doesn't hurt
                "accept": "application/json",
            },
        )
        response.raise_for_status()
        example_dataset_names = response.json()
        if not isinstance(example_dataset_names, list):
            raise TypeError(
                f"Failed to get example datasets: Response is not a list. response status code: {response.status_code}, text: {response.text}"
            )
        # It's valid for this list to be empty if no examples are configured
        self.example_dataset_names = example_dataset_names
        if not example_dataset_names:
            print("Warning: No example datasets found on the server.")

    def _handle_response(
        self, response: requests.Response, model_class=None, is_list_of_models=False
    ):
        """Helper to handle HTTP responses and Pydantic parsing."""
        try:
            # Always try to get JSON first, as even error responses might contain JSON details
            json_data = None
            try:
                json_data = response.json()
            except json.JSONDecodeError:
                # If JSON decoding fails, it's fine, we'll use response.text later for errors
                pass

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            # If we reached here, status code is 2xx
            if (
                json_data is None
            ):  # Should not happen for 2xx if server sends JSON, but as a fallback
                raise ValueError(
                    f"Successful response but no JSON body: {response.text[:500]}"
                )

            if model_class:
                if is_list_of_models:
                    if isinstance(json_data, list):
                        return [model_class.model_validate(item) for item in json_data]
                    else:
                        raise ValueError(
                            f"Expected a list for {model_class.__name__}, but got {type(json_data)}"
                        )
                else:
                    return model_class.model_validate(json_data)
            return json_data
        except requests.exceptions.HTTPError as http_err:
            status_code = http_err.response.status_code
            detail = f"HTTP Error {status_code}"
            response_text = http_err.response.text

            if json_data and isinstance(json_data, dict) and "detail" in json_data:
                detail = json_data[
                    "detail"
                ]  # Use detail from server's JSON error response if available
            elif response_text:
                detail = f"HTTP Error {status_code}: {response_text[:200]}"  # Fallback to response text

            # Option 1: Re-raise with more context (current approach)
            raise requests.exceptions.HTTPError(
                f"{detail}", response=http_err.response
            ) from http_err

            # Option 2: Using custom exceptions (if defined)
            # if status_code == 401 or status_code == 403:
            #     raise VoltusAuthError(status_code, detail, response_text) from http_err
            # elif status_code == 404:
            #     raise VoltusNotFoundError(status_code, detail, response_text) from http_err
            # else:
            #     raise VoltusApiError(status_code, detail, response_text) from http_err

        except (
            json.JSONDecodeError
        ):  # Should be caught by the initial try for json_data
            raise ValueError(f"Could not decode JSON response: {response.text[:500]}")
        except ValidationError as e:
            # Add more context to Pydantic validation errors
            # error_details = e.errors()
            # data_preview = str(json_data)[:500] if json_data else response.text[:500]
            # raise ValueError(f"Pydantic validation error: {error_details}. Data preview: {data_preview}") from e
            raise e  # Keep it simple for now, Pydantic's error is usually good
        except (
            Exception
        ) as err:  # Catch-all for other unexpected errors during processing
            raise Exception(
                f"An unexpected error occurred while handling response: {err}"
            ) from err

    def healthcheck(self) -> bool:
        try:
            response = requests.get(
                verify=self.verify_requests,
                url=f"{PROTOCOL}://{self.url}/v1/current_authenticated_user",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "accept": "application/json",
                },
            )
            print("Healthcheck response:", response.status_code, response.text, self.url)
            user_response = self._handle_response(
                response, ClientUserResponse
            )  # Validates response structure
            if user_response.user.token.split(".")[0] != self.token.split(".")[0]:
                raise ValueError("Healthcheck failed: token mismatch.")
            return True
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Failed to connect to '{self.url}'.")
        except Exception as e:
            raise Exception(f"Healthcheck failed: {e}")

    def get_task_status(self, task_id: Optional[str] = None) -> List[ClientTaskStatus]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/task_status",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"task_id": task_id} if task_id else {},
        )
        return self._handle_response(response, ClientTaskStatus, is_list_of_models=True)

    def get_current_authenticated_user(self) -> ClientUserResponse:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/current_authenticated_user",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
        )
        return self._handle_response(response, ClientUserResponse)

    def upload_dataset(
        self,
        dataset: pd.DataFrame,
        dataset_name: str = "new dataset",
        description: str = "",
        overwrite: bool = True,
    ) -> ClientApiResponse:
        buffer = BytesIO()
        dataset.to_parquet(buffer, index=False)
        buffer.seek(0)
        response = requests.post(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/datasets/file",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            params={
                "dataset_name": dataset_name,
                "description": description,
                "overwrite": overwrite,
            },
            files={"file": (f"{dataset_name}.parquet", buffer)},
        )
        response.raise_for_status()  # Ensure server responded with 2xx
        return ClientApiResponse(
            message=response.text
        )  # Server returns PlainTextResponse

    def list_datasets(self) -> List[str]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/datasets/list",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"detailed": "false"},
        )
        return self._handle_response(response)  # Returns List[str] directly

    def retrieve_dataset(
        self, dataset_name: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/datasets/{dataset_name}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"file_format": "json"},
        )
        response_json = self._handle_response(response)
        if "metadata" not in response_json:
            raise ValueError("Metadata not found in response.")
        if "data" not in response_json:
            raise ValueError("Data not found in response.")
        data_df = pd.read_json(StringIO(response_json["data"]), orient="records")
        return data_df, response_json["metadata"]

    def delete_datasets(self, dataset_names: List[str]) -> ClientApiResponse:
        response = requests.delete(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/datasets/delete",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"dataset_names": dataset_names},
        )
        # The server response for delete is a dictionary, e.g.,
        # {"message": "...", "deleted datasets": [...], "not found datasets": [...]}
        # We want this entire dictionary to be the 'message' part of our ClientApiResponse
        # or extract specific parts if ClientApiResponse was more structured.
        # Given ClientApiResponse.message = Union[str, List[str], Dict[str, Any]],
        # passing the whole JSON response dict as the message is valid.
        json_data = self._handle_response(response)  # Get the raw dict
        return ClientApiResponse(message=json_data)  # Wrap the dict in message

    def list_example_datasets(self) -> List[str]:
        return self.example_dataset_names

    def retrieve_example_dataset(
        self, dataset_name: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/datasets/example/{dataset_name}",
            headers={
                # "Authorization": f"Bearer {self.token}", # Not needed for example datasets
                "accept": "application/json",
            },
            params={"file_format": "json"},
        )
        response_json = self._handle_response(response)
        if "metadata" not in response_json:
            raise ValueError("Metadata not found in example dataset response.")
        if "data" not in response_json:
            raise ValueError("Data not found in example dataset response.")
        data_df = pd.read_json(StringIO(response_json["data"]), orient="records")
        return data_df, response_json["metadata"]

    def apply_feature_function_to_dataset(
        self,
        feature_function_name: str,
        original_datasets: List[str],
        generated_dataset_name: Optional[str] = None,
        generated_dataset_description: Optional[str] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        process_synchronously: bool = True,
        overwrite: bool = True,
    ) -> ClientApiResponse:
        instruction = {
            "feature_function_name": feature_function_name,
            "original_datasets": original_datasets,
            "generated_dataset_name": generated_dataset_name,
            "generated_dataset_description": generated_dataset_description,
            "feature_function_kwargs": kwargs or {},
        }
        response = requests.post(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/functions/apply_to_dataset",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "process_synchronously": process_synchronously,
                "overwrite": overwrite,
            },
            json=[instruction],
        )
        return self._handle_response(response, ClientApiResponse)

    def apply_feature_function_to_data(
        self,
        data: pd.DataFrame,
        feature_function_name: str,
        generated_dataset_name: Optional[str] = None,
        generated_dataset_description: Optional[str] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        process_synchronously: bool = True,
        overwrite: bool = True,
    ) -> ClientApiResponse:
        buffer = BytesIO()
        data.to_parquet(buffer, index=False)
        buffer.seek(0)
        fake_path = f"{generated_dataset_name or feature_function_name}_origin.parquet"
        response = requests.post(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/functions/apply_to_file",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "feature_function_name": feature_function_name,
                "generated_dataset_name": generated_dataset_name,
                "generated_dataset_description": generated_dataset_description,
                "feature_function_kwargs_str": json.dumps(kwargs or {}),
                "process_synchronously": process_synchronously,
                "overwrite": overwrite,
            },
            files={"file": (fake_path, buffer)},
        )
        return self._handle_response(response, ClientApiResponse)

    def list_feature_functions(
        self,
        detailed: bool = False,
        must_contain_all_tags: bool = False,
        tags: List[str] = [],
        function_type: Optional[
            ClientFunctionType
        ] = None,  # Changed to ClientFunctionType
    ) -> Union[
        List[ClientDetailedFeatureFunctionInfo], List[ClientMinimalFeatureFunctionInfo]
    ]:
        params = {
            "detailed": detailed,
            "must_contain_all_tags": must_contain_all_tags,
            "tags": tags,
        }
        if function_type is not None:
            params["function_type"] = function_type.value  # Pass the enum value

        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/functions/list",
            headers={
                # "Authorization": f"Bearer {self.token}", # Not needed for this endpoint
                "accept": "application/json",
            },
            params=params,
        )
        if detailed:
            return self._handle_response(
                response, ClientDetailedFeatureFunctionInfo, is_list_of_models=True
            )
        else:
            return self._handle_response(
                response, ClientMinimalFeatureFunctionInfo, is_list_of_models=True
            )

    def list_available_feature_functions_tags(self) -> List[str]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/functions/tags",
            headers={
                # "Authorization": f"Bearer {self.token}", # Not needed
                "accept": "application/json",
            },
        )
        json_data = self._handle_response(response)
        if "tags" in json_data and isinstance(json_data["tags"], list):
            return json_data["tags"]
        raise ValueError("Invalid response format for tags")

    def list_available_recipes_tags(self) -> List[str]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/recipes/tags",
            headers={
                # "Authorization": f"Bearer {self.token}", # Not needed
                "accept": "application/json",
            },
        )
        json_data = self._handle_response(response)
        if "tags" in json_data and isinstance(json_data["tags"], list):
            return json_data["tags"]
        raise ValueError("Invalid response format for recipe tags")

    def list_recipes(
        self,
        detailed: bool = False,
        must_contain_all_tags: bool = False,
        tags: List[str] = [],
    ) -> Union[List[ClientDetailedRecipeInfo], List[ClientMinimalRecipeInfo]]:
        params = {
            "detailed": detailed,
            "must_contain_all_tags": must_contain_all_tags,
            "tags": tags,
        }
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/recipes/list",
            headers={
                # "Authorization": f"Bearer {self.token}", # Not needed
                "accept": "application/json",
            },
            params=params,
        )
        if detailed:
            return self._handle_response(
                response, ClientDetailedRecipeInfo, is_list_of_models=True
            )
        else:
            return self._handle_response(
                response, ClientMinimalRecipeInfo, is_list_of_models=True
            )

    def list_recipes_applicable_to_dataset(
        self, dataset_name: str, tags: List[str] = []
    ) -> ClientFilteredRecipesResponse:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/recipes/filtered_list",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "dataset_name": dataset_name,
                "tags": tags,
            },
        )
        return self._handle_response(response, ClientFilteredRecipesResponse)

    def apply_recipe_to_dataset(
        self,
        recipe_name: str,
        original_dataset: str,
        generated_dataset_name: Optional[str] = None,
        generated_dataset_description: Optional[str] = None,
        process_synchronously: bool = True,
        overwrite: bool = True,
    ) -> ClientApiResponse:
        response = requests.post(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/recipes/apply_to_dataset",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "recipe_name": recipe_name,
                "original_dataset": original_dataset,
                "generated_dataset_name": generated_dataset_name,
                "generated_dataset_description": generated_dataset_description,
                "process_synchronously": process_synchronously,
                "overwrite": overwrite,
            },
        )
        return self._handle_response(response, ClientApiResponse)

    def apply_recipe_to_data(
        self,
        recipe_name: str,
        data: pd.DataFrame,
        generated_dataset_name: Optional[str] = None,
        generated_dataset_description: Optional[str] = None,
        process_synchronously: bool = True,
        overwrite: bool = True,
    ) -> ClientApiResponse:
        available_recipes_info = self.list_recipes(detailed=False)
        if not any(r.name == recipe_name for r in available_recipes_info):
            raise ValueError(
                f"Recipe '{recipe_name}' not found. Available recipes: {[r.name for r in available_recipes_info]}"
            )
        buffer = BytesIO()
        data.to_parquet(buffer, index=False)
        buffer.seek(0)
        response = requests.post(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/recipes/apply_to_file",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "recipe_name": recipe_name,
                "generated_dataset_name": generated_dataset_name,
                "generated_dataset_description": generated_dataset_description,
                "process_synchronously": process_synchronously,
                "overwrite": overwrite,
            },
            files={
                "file": (f"{generated_dataset_name or recipe_name}.parquet", buffer)
            },
        )
        return self._handle_response(response, ClientApiResponse)

    def list_trained_models(self) -> List[ClientTrainedModelInfo]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/machinelearning/models",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
        )
        return self._handle_response(
            response, ClientTrainedModelInfo, is_list_of_models=True
        )

    def get_training_info(
        self, model_name: str
    ) -> Union[ClientTrainingProgressInfo, ClientTrainingInfoMessage]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/machinelearning/training_info",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"model_name": model_name},
        )
        json_data = self._handle_response(response)
        if "message" in json_data:  # Server returns a message if no detailed progress
            return ClientTrainingInfoMessage(**json_data)
        return ClientTrainingProgressInfo(**json_data)

    def generate_synthetic_data(
        self,
        model_name: str,
        number_of_examples: int,
        file_format: str = "json",
        single_file: bool = False,
    ) -> Union[List[Any], requests.Response]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"{PROTOCOL}://{self.url}/v1/machinelearning/generate",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json"
                if file_format == "json"
                else "*/*",  # Allow any for file download
            },
            params={
                "model_name": model_name,
                "number_of_examples": number_of_examples,
                "file_format": file_format,
                "single_file": single_file,
            },
        )
        response.raise_for_status()
        if file_format == "json":
            return response.json()
        else:
            return response

    def train_model(
        self,
        dataset_name: str,
        model_name: str = "test_model",
        index_col: str = "timestamp",
        epochs: int = 10,
        batch_size: int = 1000,
        sequence_len: int = 2,
        add_sin_cos: bool = True,
        overwrite: bool = False,
        synchronously: bool = True,
    ) -> ClientApiResponse:
        response = requests.post(
            f"{PROTOCOL}://{self.url}/v1/machinelearning/train",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "model_name": model_name,
                "dataset_name": dataset_name,
                "synchronously": synchronously,
                "batch_size": batch_size,
                "epochs": epochs,
                "index_col": index_col,
                "overwrite": overwrite,
                "sequence_len": sequence_len,
                "add_sin_cos": add_sin_cos,
            },
            verify=self.verify_requests,
        )
        response.raise_for_status()
        try:
            json_data = response.json()
            if isinstance(json_data, dict):
                # Server for async train returns: {"message": "Background task created.", "task_id": "some-uuid-string"}
                msg = json_data.get("message", str(json_data))
                tid = json_data.get("task_id")  # This will be a string or None
                return ClientApiResponse(
                    message=msg, task_id=tid
                )  # Pass string directly
            # Fallback for other JSON structures or plain text
            return ClientApiResponse(message=str(json_data))
        except json.JSONDecodeError:
            return ClientApiResponse(message=response.text)


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv(verbose=True)

    BASE_URL = os.getenv("BASE_URL", None)
    USER_TOKEN = os.getenv("USER_TOKEN", None)

    client = VoltusClient(BASE_URL, USER_TOKEN, verify_requests=False)

    # Example usage:
    print(client.get_current_authenticated_user())
    print(client.list_datasets())
    print(
        client.list_feature_functions(
            detailed=True, function_type=ClientFunctionType.analytical_function
        )
    )
    print(client.list_recipes(detailed=True))
    print(
        client.list_feature_functions(
            detailed=False, function_type=ClientFunctionType.forecasting_function
        )
    )
