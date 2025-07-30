import requests
import json
import time
import logging
import pkg_resources
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from requests import Response
from http import HTTPStatus
from huggingface_hub import repo_info, hf_hub_download

GUARDIAN_CLIENT_SDK_VERSION = pkg_resources.get_distribution("guardian-client").version

from guardian_client.python.credentials import GuardianClientCredentialContext


class GuardianAPIClient:
    """
    Client for Guardian API
    """

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
        clean_endpoint = base_url.rstrip("/")
        clean_endpoint = (
            clean_endpoint
            if clean_endpoint.endswith("/guardian")
            else f"{clean_endpoint}/guardian"
        )
        self.endpoint = f"{clean_endpoint}/{api_version}/{scan_endpoint}"
        log_string_to_level = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        log_level_enum = log_string_to_level.get(log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level_enum,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        logging.info(f"Initialized scanning endpoint: {self.endpoint}")

        # client credential context is tied to a client instance.
        # In it's current state, a new client instance is created on each new call
        # to the guardian scanner, so a new context (and consequently a token)
        # is created for each scan request.
        self._access_token_context = GuardianClientCredentialContext(
            guardian_endpoint=base_url, log_level=log_level
        )

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
        if not model_uri:
            logging.error("Model URI is required")
            return {
                "http_status_code": None,
                "error": "Model URI is required",
            }

        logging.info(f"Submitting scan for {model_uri}")

        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }
        response = requests.post(
            self.endpoint,
            json={
                "model_uri": model_uri,
                "scope": "PRIVATE",
            },
            headers=headers,
        )
        if response.status_code != HTTPStatus.ACCEPTED:
            return {
                "http_status_code": response.status_code,
                "error": self._decode_error(response),
            }

        logging.info(
            f"Scan submitted successfully for {model_uri} with status_code: {response.status_code}"
        )

        if poll_interval_secs <= 0:
            return {
                "http_status_code": response.status_code,
                "scan_status_json": response.json(),
            }

        response_json = response.json()
        id = response_json["uuid"]

        # Polling
        scan_status_json = None
        status_response = None

        logging.info(f"Polling for scan outcome for {id} for {model_uri}")
        while True:
            # reload header to check if token is still valid during this processing.
            headers = {
                "Authorization": f"Bearer {self._access_token_context.access_token}",
                "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
            }

            status_response = requests.get(
                url=f"{self.endpoint}/{id}",
                headers=headers,
            )
            if status_response.status_code == HTTPStatus.OK:
                scan_status_json = status_response.json()
                if scan_status_json["aggregate_eval_outcome"] != "PENDING":
                    break
            else:
                return {
                    "http_status_code": status_response.status_code,
                    "error": self._decode_error(status_response),
                }

            logging.debug(
                f"Scan outcome for {id} is {scan_status_json['aggregate_eval_outcome']}. Sleeping for 5 seconds before next check"
            )
            time.sleep(poll_interval_secs)  # Wait for 5 seconds before next check

        logging.info(f"Scan complete for {id} for {model_uri}")

        return {
            "http_status_code": (
                status_response.status_code if status_response else None
            ),
            "scan_status_json": scan_status_json,
        }

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
        if not scan_uuid:
            logging.error("Scan UUID is required")
            return {
                "http_status_code": None,
                "error": "Scan UUID is required",
            }

        logging.info(f"Retrieving scan ID {scan_uuid}")

        # reload header to check if token is still valid during this processing.
        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }

        status_response = requests.get(
            url=f"{self.endpoint}/{scan_uuid}",
            headers=headers,
        )
        if status_response.status_code != HTTPStatus.OK:
            return {
                "http_status_code": status_response.status_code,
                "error": self._decode_error(status_response),
            }

        scan_status_json = status_response.json()
        return {
            "http_status_code": (
                status_response.status_code if status_response else None
            ),
            "scan_status_json": scan_status_json,
        }

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
        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }

        params = {
            "limit": limit,
            "skip": skip,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "count": count,
        }

        # Dynamically add optional params only if they are provided
        if severities:
            params["severities"] = severities

        if outcome:
            params["outcome"] = outcome

        if start_time:
            params["start_time"] = start_time.isoformat()

        if end_time:
            params["end_time"] = end_time.isoformat()

        status_response = requests.get(
            url=self.endpoint,
            headers=headers,
            params=params,
        )

        if status_response.status_code != HTTPStatus.OK:
            return {
                "http_status_code": status_response.status_code,
                "error": self._decode_error(status_response),
            }

        scan_list_json = status_response.json()
        return {
            "http_status_code": status_response.status_code,
            "scan_list": scan_list_json,
        }

    def scan_3p(
        self,
        repo_id: str,
        revision: str = "",
        allow_patterns: list[str] = ["*"],
        ignore_patterns: list[str] = [],
    ) -> Dict[str, Any]:
        logging.info(
            f"Creating scan for {repo_id}/{revision if revision else 'latest'}"
        )

        # if revision is not provided, it will default to the latest revision from Hugging Face
        if not revision:
            logging.debug(
                f"Revision not provided. Fetching latest revision for {repo_id} from Hugging Face"
            )
            latest_revision = repo_info(repo_id)

            if not latest_revision:
                logging.error(
                    f"Error: Could not fetch latest revision for {repo_id} from Hugging Face"
                )
                return {
                    "http_status_code": HTTPStatus.BAD_REQUEST,
                    "error": f"Error: Could not fetch latest revision for {repo_id} from Hugging Face",
                }

            revision = latest_revision.sha
            logging.debug(
                f"Fetched latest revision from Hugging Face: {repo_id}/{revision}"
            )

        if revision and not self._is_git_sha(revision):
            logging.debug(
                f"Given revision {revision} is not a SHA. Fetching a valid sha for revision"
            )

            revision_check = repo_info(repo_id=repo_id, revision=revision)

            if not revision_check:
                logging.error(
                    f"Error: Could not find the revision {revision} for {repo_id} from Hugging Face"
                )
                return {
                    "http_status_code": HTTPStatus.BAD_REQUEST,
                    "error": f"Error: Could not find the revision {revision} for {repo_id} from Hugging Face",
                }

            revision = revision_check.sha

        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }

        response = requests.post(
            self.endpoint,
            json={
                "model_uri": f"https://huggingface.co/{repo_id}",
                "scope": "PUBLIC",
                "revision": revision,
                "allow_patterns": allow_patterns,
                "ignore_patterns": ignore_patterns,
            },
            headers=headers,
        )

        if (
            response.status_code != HTTPStatus.ACCEPTED
            and response.status_code != HTTPStatus.OK
        ):
            return {
                "http_status_code": response.status_code,
                "error": self._decode_error(response),
            }

        return {
            "http_status_code": response.status_code,
            "scan_status_json": response.json(),
        }

    def download_from_scan(self, scan_uuid: str, local_dir: str) -> Dict[str, Any]:
        logging.info(f"Downloading file(s) from scan ID {scan_uuid} to {local_dir}")
        scan_response = self.get_scan(scan_uuid)
        if scan_response["http_status_code"] != HTTPStatus.OK:
            return scan_response

        scan_status_json = scan_response["scan_status_json"]
        aggregate_eval_outcome = scan_status_json["aggregate_eval_outcome"]

        model_uri = scan_status_json["model_uri"].split("/")
        repo_id = f"{model_uri[-2]}/{model_uri[-1]}"
        revision = scan_status_json["revision"]

        file_download_locs = []

        if aggregate_eval_outcome == "ERROR":
            logging.error(
                f"Model is blocked because scan id {scan_uuid} encountered an unexpected error"
            )
            return {
                "http_status_code": HTTPStatus.FORBIDDEN,
                "scan_status_json": scan_status_json,
                "download_locations": [],
            }
        elif aggregate_eval_outcome == "FAIL":
            logging.error(
                f"Model is blocked because scan id {scan_uuid} violated your organization's security policies"
            )
            return {
                "http_status_code": HTTPStatus.FORBIDDEN,
                "scan_status_json": scan_status_json,
                "download_locations": [],
            }

        for file_ in scan_status_json["files_scanned"]:
            download_loc = hf_hub_download(
                repo_id=repo_id,
                revision=revision,
                local_dir=local_dir,
                filename=os.path.basename(file_.get("absolute_path")),
                subfolder=os.path.dirname(file_.get("absolute_path")),
                # Custom-header indicating a completed scan to use during download.
                headers={"guardian-scan-uuid": scan_uuid},
                token=os.environ.get("HF_TOKEN"),
            )
            file_download_locs.append(download_loc)

        return {
            "http_status_code": HTTPStatus.OK,
            "scan_status_json": scan_status_json,
            "download_locations": file_download_locs,
        }

    def _decode_error(self, response: Response) -> str:
        try:
            response_json = response.json()
            if "detail" in response_json and response_json["detail"]:
                if isinstance(response_json["detail"], list):
                    concat_msg = ""
                    for item_ in response_json["detail"]:
                        concat_msg += f"- {item_['msg']}\n"
                    return concat_msg
                elif isinstance(response_json["detail"], str):
                    return response_json["detail"]

            return "Unknown error"
        except json.JSONDecodeError:
            return "Response is not in JSON format"

    def _is_git_sha(self, in_str: str) -> bool:
        # Git SHAs are 40 characters long (full) or 7-8 characters (short)
        # They only contain hexadecimal characters (0-9, a-f)

        # For both full and short SHA
        pattern_with_short = r"^[0-9a-f]{7,40}$"

        return bool(re.match(pattern_with_short, in_str.lower()))
