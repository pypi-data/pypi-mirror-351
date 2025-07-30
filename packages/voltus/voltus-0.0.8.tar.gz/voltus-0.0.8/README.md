# Voltus Python Client

This is a Python client for interacting with the Voltus feature store API. It provides a convenient way to programmatically access Voltus functionalities, such as adding datasets, applying feature functions (including analytical and forecasting functions), managing recipes, and generating synthetic data.

## Installation

You can install the client using pip:

```bash
pip install voltus
```

## Usage

### Initialization

First, you need to initialize the client with your Voltus API base URL and a user authentication token. It's recommended to store these in a `.env` file.

Create a `.env` file in your project root with:
```env
BASE_URL="your_voltus_api_base_url" # e.g., "voltus.inesctec.pt" or "localhost"
USER_TOKEN="your_authentication_token"
VERIFY_REQUESTS="true" # or "false" for local development with self-signed certs
```

Then, in your Python script:
```python
import os
import pandas as pd
from dotenv import load_dotenv
from voltus.client import VoltusClient, ClientFunctionType # Import ClientFunctionType

load_dotenv(verbose=True)

BASE_URL = os.getenv("BASE_URL")
USER_TOKEN = os.getenv("USER_TOKEN")
verify_requests_str = os.getenv("VERIFY_REQUESTS", "true") # Default to true
VERIFY_REQUESTS = True if verify_requests_str.lower().strip() == "true" else False

if not BASE_URL or not USER_TOKEN:
    raise ValueError("BASE_URL and USER_TOKEN must be set in your environment or .env file.")

# Initialize the client
client = VoltusClient(api_base_url=BASE_URL, token=USER_TOKEN, verify_requests=VERIFY_REQUESTS)
print(f"Client initialized. Server healthy: {client.healthcheck()}")
```

### Basic Operations

Here's how to perform common operations with the client:

#### Healthcheck

Check if the server is healthy:
```python
if client.healthcheck():
    print("Server is healthy")
else:
    print("Server is not healthy")
```

#### Current Authenticated User

Retrieve information about the currently authenticated user. The method returns a `ClientUserResponse` Pydantic model.
```python
user_response = client.get_current_authenticated_user()
print(f"Current User: {user_response.user.username}")
# print(user_response.model_dump_json(indent=2)) # For full details
```

#### Get Task Status

Retrieve the status of background tasks. Returns a list of `ClientTaskStatus` models.
```python
# Get task status for a specific task ID (if you have one)
# task_id_example = "some-uuid-string"
# specific_task_status = client.get_task_status(task_id=task_id_example)
# if specific_task_status:
#     print(f"Status of task {task_id_example}: {specific_task_status[0].status}")

# Get status of all tasks for the user
all_tasks_status = client.get_task_status()
if all_tasks_status:
    print(f"Status of the first task found: {all_tasks_status[0].id} - {all_tasks_status[0].status}")
# for task in all_tasks_status:
#     print(f"Task ID: {task.id}, Status: {task.status}, Info: {task.info}")
```

#### Uploading a Dataset
Upload a Pandas DataFrame as a dataset to the server. This returns a `ClientApiResponse`.
```python
# Create a sample pandas DataFrame
data_for_upload = {
    "timestamp": pd.to_datetime(
        ["2023-01-01 00:00:00", "2023-01-01 01:00:00", "2023-01-01 02:00:00"], utc=True
    ),
    "power": [10, 12, 15],
    "unit": ["MW", "MW", "MW"],
}
df_to_upload = pd.DataFrame(data_for_upload)

dataset_name_uploaded = "my_client_dataset"
upload_response = client.upload_dataset(
    dataset=df_to_upload,
    dataset_name=dataset_name_uploaded,
    description="Dataset uploaded via Python client.",
    overwrite=True # Set to False to prevent overwriting existing datasets
)
print(f"Upload response: {upload_response.message}")
```
#### Listing Uploaded Datasets
List all dataset names in the user's account.
```python
uploaded_datasets = client.list_datasets() # Returns List[str]
print(f"Currently uploaded datasets by user: {uploaded_datasets}")
```

#### Retrieving an Uploaded Dataset
Retrieve a dataset. The client returns a tuple: `(DataFrame, metadata_dict)`.
```python
if dataset_name_uploaded in uploaded_datasets:
    retrieved_df, retrieved_metadata = client.retrieve_dataset(dataset_name_uploaded)
    print(f"Retrieved dataset '{dataset_name_uploaded}' (first 2 rows):\n{retrieved_df.head(2)}")
    # print(f"Metadata: {retrieved_metadata}")
```

#### Deleting Datasets
Delete one or more datasets using a list of dataset names. This returns a `ClientApiResponse`.
```python
# Example: Delete the dataset we just uploaded
if dataset_name_uploaded in client.list_datasets(): # Check if it exists
    delete_response = client.delete_datasets(dataset_names=[dataset_name_uploaded])
    print(f"Deletion response: {delete_response.message}") # Message is a dict here
    if dataset_name_uploaded in delete_response.message.get("deleted datasets", []):
        print(f"'{dataset_name_uploaded}' successfully deleted.")
```

#### Listing Available Example Datasets
Lists all available example datasets provided by the server.
```python
example_dataset_names = client.list_example_datasets() # Returns List[str]
print(f"Available example datasets (first 5): {example_dataset_names[:5]}...")
```
#### Retrieving an Example Dataset
Retrieve the contents of a specific example dataset. Returns `(DataFrame, metadata_dict)`.
```python
if example_dataset_names:
    example_df, example_metadata = client.retrieve_example_dataset(example_dataset_names[0])
    print(f"Retrieved example dataset: '{example_dataset_names[0]}' (first 2 rows):\n{example_df.head(2)}")
    # print(f"Example metadata: {example_metadata}")
```

### Feature, Analytical, and Forecasting Functions

#### Listing Available Functions
Lists available feature, analytical, or forecasting functions. Returns a list of `ClientMinimalFeatureFunctionInfo` or `ClientDetailedFeatureFunctionInfo`.
```python
# List all available functions (minimal detail)
all_functions = client.list_feature_functions()
print(f"Found {len(all_functions)} total functions. Example: {all_functions[0].name} ({all_functions[0].function_type.value})")

# List only forecasting functions (detailed)
forecasting_functions = client.list_feature_functions(
    detailed=True,
    function_type=ClientFunctionType.forecasting_function # Use the enum
)
print(f"Found {len(forecasting_functions)} forecasting functions.")
if forecasting_functions:
    print(f"  Details of first forecasting function ({forecasting_functions[0].name}):")
    print(f"    Description: {forecasting_functions[0].short_description}")
    # print(f"    Arguments: {[(arg.name, arg.type, arg.default_value) for arg in forecasting_functions[0].arguments]}")
```
#### Listing Available Function Tags
```python
available_tags = client.list_available_feature_functions_tags() # Returns List[str]
print(f"Available function tags: {available_tags}")
```

#### Applying a Function to a Dataset
Apply a function to a dataset that already exists on the server, creating a new dataset. This returns a `ClientApiResponse`.
```python
# First, ensure an input dataset exists (e.g., upload an example)
input_dataset_name_for_ff = "power_usage_for_ff"
if "Power Usage" in client.list_example_datasets():
    power_df, _ = client.retrieve_example_dataset("Power Usage")
    client.upload_dataset(power_df, input_dataset_name_for_ff, overwrite=True)

    generated_ff_name = "datetime_features_output"
    ff_kwargs = {"season": ["hour", "month"]}

    ff_apply_response = client.apply_feature_function_to_dataset(
        feature_function_name="DatetimeFeatures",
        original_datasets=[input_dataset_name_for_ff],
        generated_dataset_name=generated_ff_name,
        kwargs=ff_kwargs,
        process_synchronously=True, # For demonstration, process synchronously
        overwrite=True
    )
    print(f"Apply 'DatetimeFeatures' response: {ff_apply_response.message}")

    if "created" in str(ff_apply_response.message) or "overwritten" in str(ff_apply_response.message):
        ff_result_df, _ = client.retrieve_dataset(generated_ff_name)
        # print(f"Result from 'DatetimeFeatures' (first 3 rows of '{generated_ff_name}'):\n{ff_result_df.head(3)}")
        client.delete_datasets([input_dataset_name_for_ff, generated_ff_name]) # Cleanup
```

#### Applying a Function to a Local DataFrame
Apply a function directly to a local Pandas DataFrame, uploading the result as a new dataset.
```python
# Create a sample DataFrame
df_local = pd.DataFrame({
    "timestamp": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"], utc=True),
    "value": [10, 12, 15]
})

df_local_output_name = "squared_values_from_local_df"
apply_to_data_response = client.apply_feature_function_to_data(
    data=df_local,
    feature_function_name="SquaredValue",
    generated_dataset_name=df_local_output_name,
    kwargs={"target_columns_names": ["value"]},
    overwrite=True
)
print(f"Apply 'SquaredValue' to local data response: {apply_to_data_response.message}")
if "created" in str(apply_to_data_response.message) or "overwritten" in str(apply_to_data_response.message):
    # client.delete_datasets([df_local_output_name]) # Cleanup
    pass
```

### Recipes

#### Listing Recipes
```python
# List available recipes (minimal detail)
recipes_minimal = client.list_recipes(detailed=False)
if recipes_minimal:
    print(f"Found {len(recipes_minimal)} recipes. Example: {recipes_minimal[0].name}")

# List available recipes (detailed)
recipes_detailed = client.list_recipes(detailed=True)
if recipes_detailed:
    # print(f"Details of first recipe ({recipes_detailed[0].name}):")
    # print(recipes_detailed[0].model_dump_json(indent=2))
    pass
```

#### Applying a Recipe to a Dataset
```python
if "Power Usage" in client.list_example_datasets() and recipes_minimal: # Ensure dataset and recipes exist
    recipe_input_ds = "power_usage_for_recipe"
    power_df_recipe, _ = client.retrieve_example_dataset("Power Usage")
    client.upload_dataset(power_df_recipe, recipe_input_ds, overwrite=True)

    chosen_recipe_name = "example recipe" # Assuming this recipe exists
    if any(r.name == chosen_recipe_name for r in recipes_minimal):
        generated_recipe_output_name = f"output_from_{chosen_recipe_name.replace(' ', '_')}"
        recipe_apply_response = client.apply_recipe_to_dataset(
            recipe_name=chosen_recipe_name,
            original_dataset=recipe_input_ds,
            generated_dataset_name=generated_recipe_output_name,
            overwrite=True
        )
        print(f"Apply recipe '{chosen_recipe_name}' response: {recipe_apply_response.message}")
        # if "created" in str(recipe_apply_response.message) or "overwritten" in str(recipe_apply_response.message):
            # client.delete_datasets([recipe_input_ds, generated_recipe_output_name]) # Cleanup
    else:
        print(f"Recipe '{chosen_recipe_name}' not found. Skipping recipe application example.")
```

### Synthetic Data Generation (Gretel)

#### Training a Model
```python
# Ensure 'Power Usage' example dataset is uploaded for training
ml_train_ds_name = "power_usage_for_ml_train"
if "Power Usage" in client.list_example_datasets():
    power_usage_df_ml, _ = client.retrieve_example_dataset("Power Usage")
    client.upload_dataset(power_usage_df_ml, dataset_name=ml_train_ds_name, overwrite=True)

    my_ml_model_name = f"pytest_client_gretel_model_{pd.Timestamp.now().strftime('%H%M%S')}"
    train_response = client.train_model(
        model_name=my_ml_model_name,
        dataset_name=ml_train_ds_name,
        epochs=2, # Very few epochs for quick demo
        synchronously=True,
        overwrite=True
    )
    print(f"Train model '{my_ml_model_name}' response: {train_response.message}")

    # List trained models
    trained_models = client.list_trained_models()
    print(f"Trained models: {[m.name for m in trained_models]}")

    # Generate synthetic data (JSON format)
    if any(m.name == my_ml_model_name for m in trained_models):
        synthetic_data_json = client.generate_synthetic_data(
            model_name=my_ml_model_name,
            number_of_examples=1, # Generate 1 example sequence
            file_format="json"
        )
        # print("Generated synthetic data (JSON, first sequence, first 2 records):")
        # if synthetic_data_json and isinstance(synthetic_data_json, list) and synthetic_data_json[0]:
        #      print(json.dumps(synthetic_data_json[0][:2], indent=2))
    client.delete_datasets([ml_train_ds_name]) # Cleanup
else:
    print("'Power Usage' example dataset not found, skipping ML training example.")

```

## Error Handling

The client raises exceptions derived from `requests.exceptions.RequestException` for HTTP errors or connection issues. It may also raise `ValueError` or `TypeError` for client-side input validation issues, or `pydantic.ValidationError` if server responses do not match expected Pydantic models.

## Examples

For more complete examples, see the `tests/test_client.py` file and the `example_usage.ipynb` Jupyter Notebook in the project repository.

## Contributing

Feel free to submit pull requests to the repository to improve this library.
