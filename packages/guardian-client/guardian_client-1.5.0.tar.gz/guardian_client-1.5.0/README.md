# Protect AI Guardian Client

A CLI and SDK client for Protect AI's Guardian service. You can find more information about this service here: https://protectai.com/guardian

## Using CLI

The Guardian Scanner's CLI offers a convenient way of submitting a scan, listing scans, and retrieving scan reports, along with an exit code that can be used to block model deployment depending upon the discovered vulnerabilities.

### Installation

``` shell
pip install guardian-client
```

### Setup Environment Variables

These environment variables are required for setting up the authorization with the API. The admin of your account should be able to provide you with these.

``` shell

# Guardian endpoint, can also be passed as a CLI option
export GUARDIAN_API_ENDPOINT=

# Client ID
export GUARDIAN_API_CLIENT_ID=
  
# Client Secret
export GUARDIAN_API_CLIENT_SECRET=
```

### Running Your Scans

That's it! Now you should be all set to start scanning your models.

``` shell
guardian-client scan <model_uri> \
       [--base-url <base-url>] \
       [--block-on-errors] \
       [--report-only] \
       [--log-level <log-level>] \
       [--poll-interval-secs <n_secs>] \
       [--silent] || echo $?
```

### Retrieving Your Scans

``` shell
guardian-client get-scan <scan_id> \
       [--base-url <base-url>] \
       [--block-on-errors] \
       [--report-only] \
       [--log-level <log-level>] \
       [--silent] || echo $?
```

### Listing All Scans

List scans with optional filters.

```shell
guardian-client list-scans \
       [--limit <number>] \
       [--skip <number>] \
       [--count] \
       [--sort-field <field>] \
       [--sort-order <order>] \
       [--severities <severity>] \
       [--outcome <outcome>] \
       [--start-time <start-time>] \
       [--end-time <end-time>] \
       [--report-only] \
       [--silent]
```

### Create Third Party Scan Result

``` shell
guardian-client scan-3p <repo_id> \
       [--revision <revision>] \
       [--block-on-errors] \
       [--report-only] \
       [--log-level <log-level>] \
       [--allowed-patterns <allowed-patterns>] \
       [--ignore-patterns <ignore-patterns>] \
       [--silent] || echo $?

Examples

guardian-client scan-3p meta-llama/Llama-3.1-8B-Instruct --allow-patterns "*.safetensors"
guardian-client scan-3p meta-llama/Llama-3.1-8B-Instruct --ignore-patterns "*.safetensors"
guardian-client scan-3p meta-llama/Llama-3.1-8B-Instruct -ip "*.json" -ap "*.safetensors" # specify multiple patterns of different types
guardian-client scan-3p meta-llama/Llama-3.1-8B-Instruct -ip "*.json" -ip "README.md" -ap "*.safetensors" # specify multiple patterns of same type
```

### Get Third Party Scan Result
``` shell
guardian-client download-from-scan <scan-id> \
        [--local-dir]
```

#### Arguments
- `--base-url` The API URL if not set as environment variable (required)

- `model_uri` The Path where the model is stored e.g. S3 bucket (required)

- `--block-on-errors` A boolean flag indicating the error in scanning should also lead to a block. These errors are only specific to model scanning.

- `--log-level` Can be set to any of the following: error, info, or debug

- `--silent` Disable all logging / reporting

- `--report-only` Print out the scan report and skip evaluating it for blocking.

- `--poll-interval-secs` The interval in seconds to wait before polling the server for scan status. Default is 5.

- `--allowed-patterns` `-ap` Allow files matching given patterns to be part of scan

- `--ignore-patterns` `-ip` Ignore files matching given patterns

- `--revision` The branch-reference name or commit-SHA for the specified 3p-repository.

- `--local-dir` The location on the file-system where files need to be downloaded.

- `--limit` Maximum number of scans to retrieve in `list-scans`.

- `--skip` Number of scans to skip in `list-scans`.

- `--count` Return count of scans in `list-scans`.

- `--sort-field` Field to sort the scans by (`created_at`, `updated_at`).

- `--sort-order` Order of sorting (`asc`, `desc`).

- `--severities` Filter scans by severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

- `--outcome` Filter scans by outcome (`PASS`, `FAIL`, `ERROR`).

- `--start-time` Start time filter (ISO 8601 format).

- `--end-time` End time filter (ISO 8601 format).

#### Exit Codes

The CLI returns following exit codes that can be used by the downstream applications to block a deployment.

- **0** Successful scan without violating any of your organization's policies

- **1** Successful scan with issues violating your organization's policies

- **2** Scan failed for any reason

### Examples

#### To get a block decision for a model in S3

``` shell
guardian-client scan s3://a-bucket/path/ || echo $?
```

#### To only see the report from scanning the model

```shell
guardian-client scan s3://a-bucket/path/ --report-only

```

#### To retrieve a particular historical scan

```shell
guardian-client get-scan c4fb7d8c-fc8c-422e-814c-c4441982e726 --report-only
```

#### To retrieve a list of historical scans

```
guardian-client list-scans \   
                --limit 10 \
                --skip 0 \
                --sort-field created_at \
                --start-time 2025-04-22T01:00:00 \
                --end-time 2025-04-23T01:00:00 \
                --count
```


## Using the Python SDK

In addition to the CLI, you can also integrate the scanner within your python application. The installation and environment setup is same as CLI when using the SDK.

Example for submitting a scan:

``` python
# Import the Guardian API client
from guardian_client import GuardianAPIClient

# Define the location of the Guardian Scanner's API and your model
base_url = "<ADD_YOUR_SERVICE_URL>"
model_uri = "<ADD_YOUR_MODEL_URL>"

# Initiate the client
guardian = GuardianAPIClient(base_url=base_url)

# Scan the model
response = guardian.scan(model_uri=model_uri)


# Retrieve the pass/fail decision from Guardian
assert response.get("http_status_code") == 200
assert response.get("scan_status_json") != None
assert response.get("scan_status_json").get("aggregate_eval_outcome") != "ERROR"
  
if response.get("scan_status_json").get("aggregate_eval_outcome") == "FAIL":
  print(f"Model {model_uri} was blocked because it failed your organization's security policies")
```

Example for retrieving a previous scan's results:

```python
# Import the Guardian API client
from guardian_client import GuardianAPIClient

# Define the location of the Guardian Scanner's API
base_url = "<ADD_YOUR_SERVICE_URL>"

# Initiate the client
guardian = GuardianAPIClient(base_url=base_url)

# Get a historical scan
response = guardian.get_scan(scan_uuid="c4fb7d8c-fc8c-422e-814c-c4441982e726")

print(response.get("scan_status_json"))
```

Example for retrieving a list of previous scans:

```python
# Import the Guardian API client
from guardian_client import GuardianAPIClient

base_url = "<ADD_YOUR_SERVICE_URL>"

# Initialize Guardian client
guardian = GuardianAPIClient(base_url=base_url)

# Define datetime filters
start_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
end_time = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

# Define all filter parameters
filters = {
    "limit": 10,
    "skip": 0,
    "sort_field": "created_at",
    "sort_order": "desc",
    "start_time": start_time,
    "end_time": end_time,
    "count": True,
}

# Call the API with all filters
response = guardian.list_scans(**filters)

# Pretty-print the result
print(response.get('scan_list'))

```

### Reference

#### Class GuardianAPIClient

``` python
def __init__(
    self,
    base_url: str,
    scan_endpoint: str = "scans",
    api_version: str = "v1",
    log_level: str = "INFO",
) -> None:
    """
    Initializes the Guardian API client.

    Args:
        base_url (str): The base URL of the Guardian API.
        scan_endpoint (str, optional): The endpoint for scanning. Defaults to "scans".
        api_version (str, optional): The API version. Defaults to "v1".
        log_level (str, optional): The log level. Defaults to "INFO".

    Raises:
        ValueError: If the log level is not one of "DEBUG", "INFO", "ERROR", or "CRITICAL".

    """
```

##### Methods

##### GuardianAPIClient.scan

``` python
def scan(self, model_uri: str, poll_interval_secs: int = 5) -> Dict[str, Any]:
    """
    Submits a scan request for the given URI and polls for the scan status until it is completed.

    Args:
        uri (str): The URI to be scanned.
        poll_interval_secs (int, optional): The interval in seconds to poll for the scan status.
            If <= 0, the function returns immediately after submitting the scan. Defaults to 5.

    Returns:
        dict: A dictionary containing the HTTP status code and the scan status JSON.
                If an error occurs during the scan submission or polling, the dictionary
                will also contain the error details.
    """
```

##### GuardianAPIClient.get_scan

```python
def get_scan(self, scan_uuid: str) -> Dict[str, Any]:
    """
    Retrieves the scan results for a given past scan.

    Args:
        scan_uuid (str): The ID of the scan to retrieve.

    Returns:
        dict: A dictionary containing the HTTP status code and the scan status JSON.
                If an error occurred during the scan, the dictionary
                will contain the error details instead of the scan status.
    """
```

##### GuardianAPIClient.list_scans

```python
def list_scans(
    self,
    limit: int = 10,
    skip: int = 0,
    count: bool = True,
    sort_field: str = "created_at",
    sort_order: str = "desc",
    severities: Optional[List[str]] = None,
    outcome: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Lists scans with optional filters.

    Args:
        limit (int): Maximum number of scans to retrieve. Defaults to 10.
        skip (int): Number of scans to skip. Defaults to 0.
        count (bool): Whether to return a count of scans. Defaults to True.
        sort_field (str): Field to sort the scans by. Choices are "created_at" or "updated_at". Defaults to "created_at".
        sort_order (str): Order of sorting: "asc" or "desc". Defaults to "desc".
        severities (list[str], optional): Severities to filter by. Choices are "LOW", "MEDIUM", "HIGH", or "CRITICAL".
        outcome (str, optional): Outcome filter for scans. Choices are "PASS", "FAIL", or "ERROR".
        start_time (datetime, optional): Start time filter in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
        end_time (datetime, optional): End time filter in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

    Returns:
        dict: A dictionary containing the HTTP status code and the scan list JSON.
                If an error occurred during the request, the dictionary
                will contain the error details instead of the scan list.
    """
```
