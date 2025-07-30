import json
import sys
import os

from guardian_client.python.api import GuardianAPIClient
import click
import pkg_resources
from typing import Optional, List
from datetime import datetime

client_version = pkg_resources.get_distribution("guardian-client").version


# Prefer new env var GUARDIAN_API_ENDPOINT, but fall back to GUARDIAN_ENDPOINT for backward compatibility
guardian_api_endpoint_env = os.getenv("GUARDIAN_API_ENDPOINT")
guardian_endpoint_env = os.getenv("GUARDIAN_ENDPOINT")
GUARDIAN_ENDPOINT = guardian_api_endpoint_env or guardian_endpoint_env
if guardian_endpoint_env and not guardian_api_endpoint_env:
    click.echo(
        "Warning: GUARDIAN_ENDPOINT is deprecated, please use GUARDIAN_API_ENDPOINT instead.",
    )
LOW, MEDIUM, HIGH, CRITICAL = "low", "medium", "high", "critical"
CRITICAL, ERROR, INFO, DEBUG = "critical", "error", "info", "debug"


@click.group()
@click.version_option(client_version, "-v", "--version")
@click.option(
    "--base-url",
    default=GUARDIAN_ENDPOINT,
    help="Base URL of the Guardian API. Overrides environment variable if set.",
)
@click.option("--silent", is_flag=True, help="Do not print anything to stdout")
@click.option(
    "--log-level",
    default=INFO,
    type=str,
    required=False,
    help="Logging level if not silent (critical, error, info, debug)",
)
@click.pass_context
def cli(
    ctx,
    base_url: str,
    silent: bool = True,
    log_level: str = INFO,
) -> None:
    # Skip client initialization if help or version is requested
    if "--help" in sys.argv or "--version" in sys.argv or "-v" in sys.argv:
        return

    # In all cases other than help mode, base_url is required
    elif not base_url:
        click.echo("Error: Base URL is required", err=True)
        sys.exit(2)

    # Safety check that we are in CLI mode
    ctx.ensure_object(dict)

    # Create guardian client
    guardian = GuardianAPIClient(
        base_url, log_level=log_level if not silent else CRITICAL
    )

    ctx.obj["SILENT"] = silent
    ctx.obj["CLIENT"] = guardian


@cli.command()
@click.pass_context
@click.argument("model-uri", required=True)
@click.option(
    "--poll-interval-secs",
    default=5,
    type=int,
    required=False,
    help="Seconds to poll for scan status. If <= 0, the function returns immediately after submitting the scan",
)
@click.option(
    "--report-only",
    is_flag=True,
    default=False,
    help="Only generate a report without blocking.",
)
@click.option(
    "--block-on-errors",
    is_flag=True,
    default=False,
    help="Block if a scan error occurs.",
)
def scan(
    ctx,
    model_uri: str,
    poll_interval_secs: int = 5,
    report_only: bool = False,
    block_on_errors: bool = False,
) -> None:
    """
    Submits a scan request for a 1-party model at the given URI
    """

    try:
        guardian: GuardianAPIClient = ctx.obj["CLIENT"]
        response = guardian.scan(model_uri, poll_interval_secs=poll_interval_secs)

        http_status_code = response.get("http_status_code")
        if not http_status_code or http_status_code // 100 != 2:
            click.echo(
                f"Error: Scan failed with status code: {http_status_code}, message: {response.get('error')}",
                err=True,
            )
            sys.exit(2)

        if not ctx.obj["SILENT"]:
            click.echo(json.dumps(response["scan_status_json"], indent=4))

        if report_only or poll_interval_secs <= 0:
            sys.exit(0)

        if (
            response["scan_status_json"]["aggregate_eval_outcome"] == "ERROR"
            and block_on_errors
        ):
            click.echo(
                f"Error: Scan failed with code: {response['scan_status_json']['error_code']}, message: {response['scan_status_json']['error_message']}",
                err=True,
            )
            sys.exit(2)

        if response["scan_status_json"]["aggregate_eval_outcome"] == "FAIL":
            click.echo(
                f"Error: Scan failed because it failed your organization's security policies",
                err=True,
            )
            sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: Invalid arguments {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Error: Scan submission failed: {e}", err=True)
        sys.exit(2)

    sys.exit(0)


@cli.command()
@click.pass_context
@click.argument("scan-id", required=True)
@click.option(
    "--report-only",
    is_flag=True,
    default=False,
    help="Only generate a report without blocking.",
)
@click.option(
    "--block-on-errors",
    is_flag=True,
    default=False,
    help="Block if a scan error occurs.",
)
def get_scan(
    ctx,
    scan_id: str,
    report_only: bool = False,
    block_on_errors: bool = False,
):
    """
    Retrieves a scan for the given scan ID
    """
    guardian: GuardianAPIClient = ctx.obj["CLIENT"]
    response = guardian.get_scan(scan_id)

    http_status_code = response.get("http_status_code")
    if (
        not http_status_code
        or http_status_code != 200
        or not response.get("scan_status_json")
    ):
        click.echo(
            f"Error: Scan retrieval failed with status code: {http_status_code}, message: {response.get('error')}",
            err=True,
        )
        sys.exit(2)

    if not ctx.obj["SILENT"]:
        click.echo(json.dumps(response["scan_status_json"], indent=4))

    if report_only:
        sys.exit(0)

    if (
        response["scan_status_json"]["aggregate_eval_outcome"] == "ERROR"
        and block_on_errors
    ):
        click.echo(
            f"Error: Scan failed with code: {response['scan_status_json']['error_code']}, message: {response['scan_status_json']['error_message']}",
            err=True,
        )
        sys.exit(2)

    if response["scan_status_json"]["aggregate_eval_outcome"] == "FAIL":
        click.echo(
            f"Error: Scan failed because it failed your organization's security policies",
            err=True,
        )
        sys.exit(1)

    sys.exit(0)


@cli.command(name="list-scans")
@click.pass_context
@click.option(
    "--limit", default=10, type=int, help="Maximum number of scans to retrieve"
)
@click.option("--skip", default=0, type=int, help="Number of scans to skip")
@click.option(
    "--count",
    is_flag=True,
    default=False,
    help="Whether to return count of scans",
)
@click.option(
    "--sort-field",
    default="created_at",
    type=click.Choice(["created_at", "updated_at"]),
    help="Field to sort the scans by",
)
@click.option(
    "--sort-order",
    default="desc",
    type=click.Choice(["asc", "desc"]),
    help="Order of sorting: 'asc' or 'desc'",
)
@click.option(
    "--severities",
    multiple=True,
    type=click.Choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    help="Severities to filter by",
)
@click.option(
    "--outcome",
    type=click.Choice(["PASS", "FAIL", "ERROR"], case_sensitive=True),
    help="Outcome filter for scans",
)
@click.option(
    "--start-time",
    type=str,
    help="Start time filter (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)",
)
@click.option(
    "--end-time",
    type=str,
    help="End time filter (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)",
)
@click.option(
    "--report-only",
    is_flag=True,
    default=False,
    help="Only generate a report without blocking.",
)
def list_scans(
    ctx: click.Context,
    limit: int,
    skip: int,
    count: bool,
    sort_field: str,
    sort_order: str,
    severities: Optional[List[str]],
    outcome: Optional[str],
    start_time: Optional[str],
    end_time: Optional[str],
    report_only: bool,
):
    """
    Lists scans with optional filters
    """
    guardian: GuardianAPIClient = ctx.obj["CLIENT"]

    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None

    response = guardian.list_scans(
        limit=limit,
        skip=skip,
        count=count,
        sort_field=sort_field,
        sort_order=sort_order,
        severities=list(severities) if severities else None,
        outcome=outcome,
        start_time=start_dt,
        end_time=end_dt,
    )

    http_status_code = response.get("http_status_code")
    if not http_status_code or http_status_code != 200 or not response.get("scan_list"):
        click.echo(
            f"Error: Scan retrieval failed with status code: {http_status_code}, message: {response.get('error')}",
            err=True,
        )
        sys.exit(2)

    if not ctx.obj["SILENT"]:
        click.echo(json.dumps(response["scan_list"], indent=4))

    if report_only:
        sys.exit(0)

    sys.exit(0)


@cli.command()
@click.pass_context
@click.argument("repo-id", required=True)
@click.option(
    "--revision",
    default="main",
    type=str,
    required=False,
    help="Repo id revision to get scan",
)
@click.option(
    "--allow-patterns",
    "-ap",
    default=["*"],
    required=False,
    help="Allow files matching given patterns to be part of scan",
    multiple=True,
)
@click.option(
    "--ignore-patterns",
    "-ip",
    default=[],
    required=False,
    help="Ignore files matching given patterns",
    multiple=True,
)
@click.option(
    "--report-only",
    is_flag=True,
    default=False,
    help="Only generate a report without blocking.",
)
@click.option(
    "--block-on-errors",
    is_flag=True,
    default=False,
    help="Block if a scan error occurs.",
)
def scan_3p(
    ctx,
    repo_id: str,
    revision: str = "",
    allow_patterns: list[str] = ["*"],
    ignore_patterns: list[str] = [],
    report_only: bool = False,
    block_on_errors: bool = False,
):
    """
    Submits a scan request for a given 3rd-party Repository
    """
    try:
        guardian: GuardianAPIClient = ctx.obj["CLIENT"]
        response = guardian.scan_3p(repo_id, revision, allow_patterns, ignore_patterns)

        http_status_code = response.get("http_status_code")
        if (
            not http_status_code
            or http_status_code // 100 != 2
            or not response.get("scan_status_json")
        ):
            click.echo(
                f"Error: Third party scan creation failed for {repo_id}/{revision} with status code: {http_status_code}, message: {response.get('error')}",
                err=True,
            )
            sys.exit(2)

        if not ctx.obj["SILENT"]:
            click.echo(json.dumps(response["scan_status_json"], indent=4))

        if report_only:
            sys.exit(0)

        if (
            response["scan_status_json"].get("aggregate_eval_outcome") == "ERROR"
            and block_on_errors
        ):
            click.echo(
                f"Error: Scan failed with code: {response['scan_status_json']['error_code']}, message: {response['scan_status_json']['error_message']}",
                err=True,
            )
            sys.exit(2)

        if response["scan_status_json"].get("aggregate_eval_outcome") == "FAIL":
            click.echo(
                f"Error: Scan failed because it failed your organization's security policies",
                err=True,
            )
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Scan submission failed: {e}", err=True)
        sys.exit(2)

    sys.exit(0)


@cli.command()
@click.pass_context
@click.argument("scan-id", required=True)
@click.option(
    "--local-dir",
    default=".",
    help="Location on device to which files are downloaded",
)
@click.option(
    "--block-on-errors",
    is_flag=True,
    default=False,
    help="Block if a scan error occurs.",
)
def download_from_scan(
    ctx,
    scan_id: str,
    local_dir: str = ".",
    block_on_errors: bool = False,
):
    """
    Download files that are already scanned in the given scan ID
    """
    try:
        guardian: GuardianAPIClient = ctx.obj["CLIENT"]
        response = guardian.download_from_scan(scan_id, local_dir)

        http_status_code = response.get("http_status_code")

        if not http_status_code or http_status_code != 200:
            click.echo(
                f"Error: Scan download failed with status code: {http_status_code}, message: {response.get('error')}",
                err=True,
            )
            sys.exit(2)

        if not ctx.obj["SILENT"]:
            click.echo(json.dumps(response["scan_status_json"], indent=4))
            click.echo(json.dumps(response["download_locations"]))

        if (
            response["scan_status_json"]["aggregate_eval_outcome"] == "ERROR"
            and block_on_errors
        ):
            click.echo(
                f"Error: Scan failed with code: {response['scan_status_json']['error_code']}, message: {response['scan_status_json']['error_message']}",
                err=True,
            )
            sys.exit(2)

        if response["scan_status_json"]["aggregate_eval_outcome"] == "FAIL":
            click.echo(
                "Error: Scan failed because it failed your organization's security policies",
                err=True,
            )
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Scan download failed: {e}", err=True)
        sys.exit(2)


if __name__ == "__main__":
    cli(obj={})
